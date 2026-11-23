#include "windlass/nmea.hpp"

namespace windlass {
namespace {

void put_i32(uint8_t* dest, int32_t value) {
  dest[0] = static_cast<uint8_t>(value);
  dest[1] = static_cast<uint8_t>(value >> 8);
  dest[2] = static_cast<uint8_t>(value >> 16);
  dest[3] = static_cast<uint8_t>(value >> 24);
}

uint8_t motion_code(const Controller& controller) {
  if (!controller.running()) return 0;
  if (controller.drive().up_req) return 1;
  if (controller.drive().down_req) return 2;
  return 0;
}

uint8_t sense_code(Direction direction) {
  switch (direction) {
    case Direction::Up:
      return 1;
    case Direction::Down:
      return 2;
    case Direction::Conflict:
      return 3;
    case Direction::Stopped:
      return 0;
  }
  return 0;
}

}  // namespace

uint32_t nmea_id(uint32_t pgn, uint8_t source, uint8_t priority) {
  const uint32_t pf = (pgn >> 8) & 0xffu;
  const uint32_t ps = pgn & 0xffu;
  return ((static_cast<uint32_t>(priority) & 7u) << 26) | (pf << 16) | (ps << 8) | source;
}

std::vector<CanFrame> status_frames(const Controller& controller, bool publish_strap, uint8_t source) {
  std::vector<CanFrame> frames;
  if (!publish_strap) return frames;
  const int32_t mm = static_cast<int32_t>(controller.chain().millimetres());

  CanFrame operating;
  operating.id = nmea_id(kPgnOperating, source, 6);
  operating.data[0] = motion_code(controller);
  operating.data[1] = controller.fault() ? 1 : 0;
  put_i32(&operating.data[2], mm);
  operating.data[6] = static_cast<uint8_t>(controller.chain().mm_per_pulse);
  operating.data[7] = static_cast<uint8_t>(controller.chain().mm_per_pulse >> 8);
  frames.push_back(operating);

  CanFrame monitoring;
  monitoring.id = nmea_id(kPgnMonitoring, source, 6);
  monitoring.data[0] = sense_code(controller.direction());
  put_i32(&monitoring.data[1], controller.chain().pulses);
  monitoring.data[5] = static_cast<uint8_t>(controller.chain().mm_per_pulse);
  monitoring.data[6] = static_cast<uint8_t>(controller.chain().mm_per_pulse >> 8);
  monitoring.data[7] = 0;
  frames.push_back(monitoring);
  return frames;
}

}  // namespace windlass
