#pragma once

#include <cstdint>

// GPIO numbers from kicad11/esp32.kicad_sch nets, as listed in
// docs/pin_allocation.md for the integrated board. Classic ESP32
// GPIO25/26/27/32/33 are not pins on ESP32-S3-WROOM-1-N16.

namespace windlass {

struct Gpio {
  static constexpr int heartbeat = 1;    // WDI_FUTURE, rising edge
  static constexpr int twai_tx = 4;      // TWAI_TX
  static constexpr int twai_rx = 5;      // TWAI_RX
  static constexpr int reed = 6;         // REED_GPIO, after the blanker
  static constexpr int up_sense = 7;     // UP_SENSE, low = 12 V present
  static constexpr int down_sense = 8;   // DN_SENSE, low = 12 V present
  static constexpr int up_req = 9;       // UP_REQ, high asks, pulldown = off
  static constexpr int down_req = 10;    // DN_REQ, high asks, pulldown = off
  static constexpr int coil_rail = 14;   // COIL_RAIL_OK, high = rail present
  static constexpr int led_red = 15;     // LED_R
  static constexpr int led_green = 16;   // LED_G
  static constexpr int publish = 18;     // PUBLISH_EN, jumper readback
  static constexpr int uart_tx = 43;
  static constexpr int uart_rx = 44;
};

// Not outputs, and not driven by this image.
static constexpr int kGpioUsbDn = 19;
static constexpr int kGpioUsbDp = 20;
static constexpr int kOpenLedPin = 17;  // no blue LED on the integrated board

constexpr uint32_t kTtlDefaultMs = 300;
constexpr uint32_t kTtlMinMs = 150;
constexpr uint32_t kTtlMaxMs = 1000;
constexpr uint32_t kDebounceMs = 30;
// 74LVC1G123 on U11: A held low, CLR held high, rising edge on B (GPIO1).
// Nexperia tW = K × R52(kΩ) × C50(pF) ns, K about 1 above 10 nF.
// R52 is 100 kΩ and C50 is 3.3 µF, so the typical pulse is 330 ms.
// The short case used for the edge rule is K = 1 and capacitance −20%: 264 ms.
// The long case is K = 1.2 and capacitance +20%: 475 ms.
constexpr uint32_t kMonostableTypicalMs = 330;
constexpr uint32_t kMonostableShortMs = 264;
constexpr uint32_t kMonostableLongMs = 475;
constexpr uint32_t kHeartbeatPeriodMs = 80;
constexpr uint32_t kHeartbeatHighMs = 40;
static_assert(kHeartbeatPeriodMs <= 100, "edge period must stay inside the heartbeat contract");
static_assert(kHeartbeatPeriodMs * 2 < kMonostableShortMs,
              "the short monostable pulse must cover two edges");
constexpr int32_t kDefaultMmPerPulse = 360;

}  // namespace windlass
