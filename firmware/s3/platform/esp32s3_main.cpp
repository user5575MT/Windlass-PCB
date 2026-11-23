// Integrated-board image for ESP32-S3-WROOM-1-N16.
// The prototype WindlassController tree is not in this repository and is not
// built here. This file compiles with the Arduino-ESP32 core. The host tests
// do not include it.
//
// Coil outputs are driven only from Controller::drive(). There is no timer
// interrupt on GPIO1. If loop() stops, the edges stop and the monostable
// releases the series switch.

#if defined(ARDUINO)

#include "windlass/controller.hpp"
#include "windlass/nmea.hpp"
#include "windlass/protocol.hpp"
#include "windlass/web.hpp"

#include <Arduino.h>
#include <Preferences.h>
#include <WebServer.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <driver/twai.h>

namespace {

constexpr uint16_t kTelemetryPort = 4210;
constexpr uint16_t kCommandPort = 4212;
constexpr uint8_t kNodeAddress = 0x22;

#ifndef WIFI_PASS
#define WIFI_PASS "CHANGE_ME"
#endif

class NvsStore : public windlass::Store {
 public:
  bool load(windlass::ChainState& out) override {
    prefs_.begin("chain", true);
    const bool have = prefs_.isKey("pulses");
    if (have) {
      out.pulses = prefs_.getInt("pulses", 0);
      out.mm_per_pulse = prefs_.getInt("mm", windlass::kDefaultMmPerPulse);
    }
    prefs_.end();
    return have && out.mm_per_pulse > 0;
  }
  void save(const windlass::ChainState& in) override {
    prefs_.begin("chain", false);
    prefs_.putInt("pulses", in.pulses);
    prefs_.putInt("mm", in.mm_per_pulse);
    prefs_.end();
  }

 private:
  Preferences prefs_;
};

NvsStore store;
windlass::Controller controller(store);
WebServer server(80);
WiFiUDP commands;
bool twai_up = false;

// Called before radio, NVS, or any other peripheral init.
void drivePinsLow() {
  pinMode(windlass::Gpio::heartbeat, OUTPUT);
  pinMode(windlass::Gpio::up_req, OUTPUT);
  pinMode(windlass::Gpio::down_req, OUTPUT);
  pinMode(windlass::Gpio::led_red, OUTPUT);
  pinMode(windlass::Gpio::led_green, OUTPUT);
  digitalWrite(windlass::Gpio::heartbeat, LOW);
  digitalWrite(windlass::Gpio::up_req, LOW);
  digitalWrite(windlass::Gpio::down_req, LOW);
  digitalWrite(windlass::Gpio::led_red, LOW);
  digitalWrite(windlass::Gpio::led_green, LOW);
}

void applyDrive() {
  const windlass::Drive& drive = controller.drive();
  digitalWrite(windlass::Gpio::up_req, drive.up_req ? HIGH : LOW);
  digitalWrite(windlass::Gpio::down_req, drive.down_req ? HIGH : LOW);
  digitalWrite(windlass::Gpio::heartbeat, drive.heartbeat ? HIGH : LOW);
  digitalWrite(windlass::Gpio::led_red, drive.led_red ? HIGH : LOW);
  digitalWrite(windlass::Gpio::led_green, drive.led_green ? HIGH : LOW);
}

windlass::Sense readSense() {
  windlass::Sense sense;
  sense.reed_high = digitalRead(windlass::Gpio::reed) == HIGH;
  sense.up_sense_low = digitalRead(windlass::Gpio::up_sense) == LOW;
  sense.down_sense_low = digitalRead(windlass::Gpio::down_sense) == LOW;
  sense.coil_rail_high = digitalRead(windlass::Gpio::coil_rail) == HIGH;
  sense.publish_high = digitalRead(windlass::Gpio::publish) == HIGH;
  sense.link_up = WiFi.softAPgetStationNum() > 0;
  return sense;
}

void sendStatus() {
  if (!twai_up || digitalRead(windlass::Gpio::publish) != HIGH) return;
  const auto frames = windlass::status_frames(controller, true, kNodeAddress);
  for (const auto& frame : frames) {
    twai_message_t message = {};
    message.identifier = frame.id;
    message.extd = 1;
    message.data_length_code = frame.dlc;
    for (int i = 0; i < 8; ++i) message.data[i] = frame.data[i];
    twai_transmit(&message, 0);
  }
}

void handleRoot() { server.send(200, "text/html", windlass::config_page(controller)); }

void handleStatus() { server.send(200, "application/json", windlass::status_json(controller)); }

void handleConfig() {
  std::string body;
  if (server.hasArg("mm_per")) body += "mm_per=" + std::string(server.arg("mm_per").c_str());
  if (server.hasArg("pulses")) {
    if (!body.empty()) body += "&";
    body += "pulses=" + std::string(server.arg("pulses").c_str());
  }
  if (body.empty() && server.hasArg("plain")) body = server.arg("plain").c_str();
  const bool ok = windlass::apply_config(controller, body);
  applyDrive();
  if (!ok) {
    server.send(400, "text/plain", "rejected");
    return;
  }
  server.sendHeader("Location", "/");
  server.send(303, "text/plain", "saved");
}

}  // namespace

void setup() {
  drivePinsLow();
  pinMode(windlass::Gpio::reed, INPUT);
  pinMode(windlass::Gpio::up_sense, INPUT_PULLUP);
  pinMode(windlass::Gpio::down_sense, INPUT_PULLUP);
  pinMode(windlass::Gpio::coil_rail, INPUT_PULLUP);
  pinMode(windlass::Gpio::publish, INPUT_PULLDOWN);
  Serial.begin(115200);
  controller.begin(millis(), readSense());
  applyDrive();

  WiFi.mode(WIFI_AP);
  WiFi.softAP("WindlassCounter", WIFI_PASS);
  commands.begin(kCommandPort);
  server.on("/", HTTP_GET, handleRoot);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/config", HTTP_POST, handleConfig);
  server.begin();

  twai_general_config_t general =
      TWAI_GENERAL_CONFIG_DEFAULT(static_cast<gpio_num_t>(windlass::Gpio::twai_tx),
                                  static_cast<gpio_num_t>(windlass::Gpio::twai_rx), TWAI_MODE_NORMAL);
  twai_timing_config_t timing = TWAI_TIMING_CONFIG_250KBITS();
  twai_filter_config_t filter = TWAI_FILTER_CONFIG_ACCEPT_ALL();
  if (twai_driver_install(&general, &timing, &filter) == ESP_OK && twai_start() == ESP_OK) {
    twai_up = true;
  }
  applyDrive();
}

void loop() {
  const uint32_t now = millis();
  int packet = commands.parsePacket();
  while (packet > 0) {
    char buffer[128];
    const int length = commands.read(buffer, sizeof(buffer) - 1);
    if (length > 0) {
      buffer[length] = '\0';
      windlass::Command command;
      if (windlass::parse_command(buffer, command)) {
        const bool ok = controller.command(now, command);
        applyDrive();
        const std::string ack = windlass::format_ack(controller.session(), command.sequence, ok);
        commands.beginPacket(commands.remoteIP(), kCommandPort);
        commands.write(reinterpret_cast<const uint8_t*>(ack.data()), ack.size());
        commands.endPacket();
      }
    }
    packet = commands.parsePacket();
  }
  controller.tick(now, readSense());
  applyDrive();
  server.handleClient();
  static uint32_t last_status = 0;
  if (static_cast<uint32_t>(now - last_status) >= 200) {
    last_status = now;
    WiFiUDP telemetry;
    telemetry.beginPacket("255.255.255.255", kTelemetryPort);
    const std::string line = windlass::format_telemetry(controller);
    telemetry.write(reinterpret_cast<const uint8_t*>(line.data()), line.size());
    telemetry.endPacket();
    sendStatus();
  }
  delay(10);
}

#endif
