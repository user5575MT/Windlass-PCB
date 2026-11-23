// Integrated-board image for ESP32-S3-WROOM-1-N16.
// The prototype WindlassController tree is not in this repository and is not
// built here. This file compiles with the Arduino-ESP32 core. The host tests
// do not include it.
//
// Coil outputs are driven only from Controller::drive(). There is no timer
// interrupt on GPIO1. If loop() stops, the edges stop and the monostable
// releases the series switch.
//
// No command socket is opened. The prototype datagram bytes, the password,
// and the Pi bridge are not in this repository, so nothing in this file
// calls Controller::command().

#if defined(ARDUINO)

#include "windlass/controller.hpp"
#include "windlass/nmea.hpp"
#include "windlass/web.hpp"

#include <Arduino.h>
#include <Preferences.h>
#include <WebServer.h>
#include <WiFi.h>
#include <driver/twai.h>
#include <esp_random.h>

#include <cstring>
#include <vector>

namespace {

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
windlass::NmeaNode* bus = nullptr;
bool twai_up = false;
bool radio_up = false;

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
  // Station presence is not a command link. This image accepts no datagram.
  sense.link_up = false;
  return sense;
}

void transmit(const std::vector<windlass::CanFrame>& frames) {
  if (!twai_up) return;
  for (const auto& frame : frames) {
    twai_message_t message = {};
    message.identifier = frame.id;
    message.extd = 1;
    message.data_length_code = frame.dlc;
    for (int i = 0; i < frame.dlc && i < 8; ++i) message.data[i] = frame.data[i];
    twai_transmit(&message, 0);
  }
}

windlass::WindlassReport reportFromController() {
  windlass::WindlassReport report;
  report.running_up = controller.drive().up_req;
  report.running_down = controller.drive().down_req;
  report.rode_mm = static_cast<int32_t>(controller.chain().millimetres());
  report.fault = controller.fault();
  return report;
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

  bus = new windlass::NmeaNode(windlass::name_from_mac(ESP.getEfuseMac()));
  bus->set_claim_delay_ms(esp_random() % 256u);
  bus->set_publish(false);

  const bool password_set = std::strcmp(WIFI_PASS, "CHANGE_ME") != 0 && WIFI_PASS[0] != '\0';
  if (password_set) {
    WiFi.mode(WIFI_AP);
    WiFi.softAP("WindlassCounter", WIFI_PASS);
    server.on("/", HTTP_GET, handleRoot);
    server.on("/status", HTTP_GET, handleStatus);
    server.on("/config", HTTP_POST, handleConfig);
    server.begin();
    radio_up = true;
  }

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
  controller.tick(now, readSense());
  applyDrive();
  if (radio_up) server.handleClient();
  if (bus != nullptr) {
    bus->set_publish(digitalRead(windlass::Gpio::publish) == HIGH);
    bus->set_report(reportFromController());
    transmit(bus->tick(now));
    if (twai_up) {
      twai_message_t received;
      while (twai_receive(&received, 0) == ESP_OK) {
        if (!received.extd || received.data_length_code > 8) continue;
        windlass::CanFrame frame;
        frame.id = received.identifier;
        frame.dlc = received.data_length_code;
        for (int i = 0; i < frame.dlc; ++i) frame.data[i] = received.data[i];
        transmit(bus->on_frame(now, frame));
      }
    }
  }
  delay(10);
}

#endif
