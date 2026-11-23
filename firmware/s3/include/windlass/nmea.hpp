#pragma once

#include "windlass/controller.hpp"

#include <cstdint>
#include <vector>

namespace windlass {

// Status frames only. PGN 128776 is a motor command and is not produced.
constexpr uint32_t kPgnOperating = 128777;
constexpr uint32_t kPgnMonitoring = 128778;
constexpr uint32_t kPgnMotorCommand = 128776;

struct CanFrame {
  uint32_t id = 0;
  uint8_t data[8] = {};
  uint8_t dlc = 8;
};

// 29-bit identifier, PDU2 (PF >= 240). Source address is the 8-bit node id.
uint32_t nmea_id(uint32_t pgn, uint8_t source, uint8_t priority);

// Empty when the publish strap is low. The hardware strap also holds the
// transceiver off; this image still withholds the frames.
std::vector<CanFrame> status_frames(const Controller& controller, bool publish_strap, uint8_t source);

}  // namespace windlass
