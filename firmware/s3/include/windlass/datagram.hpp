#ifndef WINDLASS_DATAGRAM_HPP
#define WINDLASS_DATAGRAM_HPP

#include "windlass/controller.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace windlass {

// WLC2 is the protocol this image speaks. The prototype WLC1 bytes were not
// recovered. The Pi bridge adopts this layout; that bridge is not edited here.
//
// Multi-byte integers are big-endian. The HMAC-SHA256 covers every byte
// before the tag and uses the raw COMMAND_KEY bytes.

constexpr uint8_t kDatagramMagic[4] = {'W', 'L', 'C', '2'};
constexpr uint8_t kDatagramVersion = 1;
constexpr uint8_t kTypeCommand = 1;
constexpr uint8_t kTypeAck = 2;
constexpr uint8_t kTypeTelemetry = 3;
constexpr uint8_t kOpStop = 0;
constexpr uint8_t kOpUp = 1;
constexpr uint8_t kOpDown = 2;
constexpr uint8_t kOpBoth = 3;
constexpr uint16_t kCommandPort = 4212;
constexpr uint16_t kTelemetryPort = 4210;
constexpr std::size_t kCommandBytes = 61;
constexpr std::size_t kAckBytes = 59;
constexpr std::size_t kTelemetryBytes = 66;
constexpr std::size_t kMacBytes = 32;

constexpr uint8_t kFlagRunning = 1u << 0;
constexpr uint8_t kFlagFault = 1u << 1;
constexpr uint8_t kFlagLocked = 1u << 2;
constexpr uint8_t kFlagUp = 1u << 3;
constexpr uint8_t kFlagDown = 1u << 4;
constexpr uint8_t kFlagHeartbeat = 1u << 5;

struct OpenedCommand {
  bool authentic = false;
  Command command;
};

bool session_to_bytes(const std::string& hex, uint8_t out[16]);
std::string session_to_hex(const uint8_t raw[16]);

OpenedCommand open_command(const uint8_t* data, std::size_t length, const uint8_t* key, std::size_t key_length);
std::vector<uint8_t> seal_command(const std::string& session_hex, uint32_t sequence, uint8_t op, uint16_t ttl_ms,
                                  const uint8_t* key, std::size_t key_length);
std::vector<uint8_t> seal_ack(const std::string& session_hex, uint32_t sequence, bool accepted, const uint8_t* key,
                              std::size_t key_length);

struct TelemetryView {
  std::string session_hex;
  int32_t pulses = 0;
  int32_t millimetres = 0;
  uint16_t mm_per_pulse = 0;
  uint8_t flags = 0;
  uint8_t direction = 0;
  bool authentic = false;
};

std::vector<uint8_t> seal_telemetry(const Controller& controller, const uint8_t* key, std::size_t key_length);
TelemetryView open_telemetry(const uint8_t* data, std::size_t length, const uint8_t* key, std::size_t key_length);

}  // namespace windlass
#endif  // WINDLASS_DATAGRAM_HPP
