#include "windlass/datagram.hpp"

#include "windlass/sha256.hpp"

#include <cstring>

namespace windlass {
namespace {

void put_be16(uint8_t* p, uint16_t value) {
  p[0] = static_cast<uint8_t>(value >> 8);
  p[1] = static_cast<uint8_t>(value);
}

void put_be32(uint8_t* p, uint32_t value) {
  p[0] = static_cast<uint8_t>(value >> 24);
  p[1] = static_cast<uint8_t>(value >> 16);
  p[2] = static_cast<uint8_t>(value >> 8);
  p[3] = static_cast<uint8_t>(value);
}

uint16_t get_be16(const uint8_t* p) { return static_cast<uint16_t>((p[0] << 8) | p[1]); }

uint32_t get_be32(const uint8_t* p) {
  return (static_cast<uint32_t>(p[0]) << 24) | (static_cast<uint32_t>(p[1]) << 16) |
         (static_cast<uint32_t>(p[2]) << 8) | static_cast<uint32_t>(p[3]);
}

int hex_nibble(char c) {
  if (c >= '0' && c <= '9') return c - '0';
  if (c >= 'a' && c <= 'f') return c - 'a' + 10;
  if (c >= 'A' && c <= 'F') return c - 'A' + 10;
  return -1;
}

bool header_ok(const uint8_t* data, uint8_t type) {
  return std::memcmp(data, kDatagramMagic, 4) == 0 && data[4] == kDatagramVersion && data[5] == type;
}

void tag(std::vector<uint8_t>& packet, const uint8_t* key, std::size_t key_length) {
  uint8_t mac[kMacBytes];
  hmac_sha256(key, key_length, packet.data(), packet.size(), mac);
  packet.insert(packet.end(), mac, mac + kMacBytes);
}

bool tag_ok(const uint8_t* data, std::size_t covered, const uint8_t* key, std::size_t key_length) {
  uint8_t mac[kMacBytes];
  hmac_sha256(key, key_length, data, covered, mac);
  return mac_equal(mac, data + covered, kMacBytes);
}

uint8_t direction_code(Direction direction) {
  if (direction == Direction::Up) return 1;
  if (direction == Direction::Down) return 2;
  if (direction == Direction::Conflict) return 3;
  return 0;
}

CmdKind kind_from_op(uint8_t op, bool& known) {
  known = true;
  if (op == kOpStop) return CmdKind::Stop;
  if (op == kOpUp) return CmdKind::Up;
  if (op == kOpDown) return CmdKind::Down;
  if (op == kOpBoth) return CmdKind::Both;
  known = false;
  return CmdKind::Stop;
}

}  // namespace

bool session_to_bytes(const std::string& hex, uint8_t out[16]) {
  if (hex.size() != 32) return false;
  for (int i = 0; i < 16; ++i) {
    const int hi = hex_nibble(hex[2 * i]);
    const int lo = hex_nibble(hex[2 * i + 1]);
    if (hi < 0 || lo < 0) return false;
    out[i] = static_cast<uint8_t>((hi << 4) | lo);
  }
  return true;
}

std::string session_to_hex(const uint8_t raw[16]) {
  static const char* digits = "0123456789abcdef";
  std::string hex(32, '0');
  for (int i = 0; i < 16; ++i) {
    hex[2 * i] = digits[raw[i] >> 4];
    hex[2 * i + 1] = digits[raw[i] & 0x0f];
  }
  return hex;
}

OpenedCommand open_command(const uint8_t* data, std::size_t length, const uint8_t* key, std::size_t key_length) {
  OpenedCommand opened;
  if (data == nullptr || key == nullptr || key_length == 0 || length != kCommandBytes) return opened;
  if (!header_ok(data, kTypeCommand)) return opened;
  if (!tag_ok(data, kCommandBytes - kMacBytes, key, key_length)) return opened;
  bool known = false;
  const CmdKind kind = kind_from_op(data[26], known);
  if (!known) return opened;
  uint8_t raw[16];
  std::memcpy(raw, data + 6, 16);
  opened.authentic = true;
  opened.command.session = session_to_hex(raw);
  opened.command.sequence = get_be32(data + 22);
  opened.command.kind = kind;
  opened.command.ttl_ms = get_be16(data + 27);
  return opened;
}

std::vector<uint8_t> seal_command(const std::string& session_hex, uint32_t sequence, uint8_t op, uint16_t ttl_ms,
                                  const uint8_t* key, std::size_t key_length) {
  uint8_t raw[16];
  if (key == nullptr || key_length == 0 || !session_to_bytes(session_hex, raw)) return {};
  if (op > kOpBoth) return {};
  std::vector<uint8_t> packet(kCommandBytes - kMacBytes, 0);
  std::memcpy(packet.data(), kDatagramMagic, 4);
  packet[4] = kDatagramVersion;
  packet[5] = kTypeCommand;
  std::memcpy(packet.data() + 6, raw, 16);
  put_be32(packet.data() + 22, sequence);
  packet[26] = op;
  put_be16(packet.data() + 27, ttl_ms);
  tag(packet, key, key_length);
  return packet;
}

std::vector<uint8_t> seal_ack(const std::string& session_hex, uint32_t sequence, bool accepted, const uint8_t* key,
                              std::size_t key_length) {
  uint8_t raw[16];
  if (key == nullptr || key_length == 0 || !session_to_bytes(session_hex, raw)) return {};
  std::vector<uint8_t> packet(kAckBytes - kMacBytes, 0);
  std::memcpy(packet.data(), kDatagramMagic, 4);
  packet[4] = kDatagramVersion;
  packet[5] = kTypeAck;
  std::memcpy(packet.data() + 6, raw, 16);
  put_be32(packet.data() + 22, sequence);
  packet[26] = accepted ? 1 : 0;
  tag(packet, key, key_length);
  return packet;
}

std::vector<uint8_t> seal_telemetry(const Controller& controller, const uint8_t* key, std::size_t key_length) {
  uint8_t raw[16];
  if (key == nullptr || key_length == 0 || !session_to_bytes(controller.session(), raw)) return {};
  std::vector<uint8_t> packet(kTelemetryBytes - kMacBytes, 0);
  std::memcpy(packet.data(), kDatagramMagic, 4);
  packet[4] = kDatagramVersion;
  packet[5] = kTypeTelemetry;
  std::memcpy(packet.data() + 6, raw, 16);
  const int64_t mm = controller.chain().millimetres();
  const int32_t mm32 = mm > 2147483647ll ? 2147483647 : (mm < -2147483647ll ? -2147483647 : static_cast<int32_t>(mm));
  put_be32(packet.data() + 22, static_cast<uint32_t>(controller.chain().pulses));
  put_be32(packet.data() + 26, static_cast<uint32_t>(mm32));
  const int32_t per = controller.chain().mm_per_pulse;
  put_be16(packet.data() + 30, static_cast<uint16_t>(per < 0 ? 0 : (per > 65535 ? 65535 : per)));
  uint8_t flags = 0;
  if (controller.running()) flags |= kFlagRunning;
  if (controller.fault()) flags |= kFlagFault;
  if (controller.start_locked()) flags |= kFlagLocked;
  if (controller.drive().up_req) flags |= kFlagUp;
  if (controller.drive().down_req) flags |= kFlagDown;
  if (controller.drive().heartbeat) flags |= kFlagHeartbeat;
  packet[32] = flags;
  packet[33] = direction_code(controller.direction());
  tag(packet, key, key_length);
  return packet;
}

TelemetryView open_telemetry(const uint8_t* data, std::size_t length, const uint8_t* key, std::size_t key_length) {
  TelemetryView view;
  if (data == nullptr || key == nullptr || key_length == 0 || length != kTelemetryBytes) return view;
  if (!header_ok(data, kTypeTelemetry)) return view;
  if (!tag_ok(data, kTelemetryBytes - kMacBytes, key, key_length)) return view;
  uint8_t raw[16];
  std::memcpy(raw, data + 6, 16);
  view.authentic = true;
  view.session_hex = session_to_hex(raw);
  view.pulses = static_cast<int32_t>(get_be32(data + 22));
  view.millimetres = static_cast<int32_t>(get_be32(data + 26));
  view.mm_per_pulse = get_be16(data + 30);
  view.flags = data[32];
  view.direction = data[33];
  return view;
}

}  // namespace windlass
