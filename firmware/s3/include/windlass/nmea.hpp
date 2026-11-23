#ifndef WINDLASS_NMEA_HPP
#define WINDLASS_NMEA_HPP

#include <cstddef>
#include <cstdint>
#include <vector>

namespace windlass {

// NMEA 2000 / ISO 11783-5 on the TWAI pins. Publishing stays off until the
// caller enables it. The hardware strap is that enable: open means no frames.
// PGN 128776 is a windlass command and is never transmitted. A received
// 128776 does not become a relay request.

constexpr uint32_t kPgnAddressClaim = 60928;
constexpr uint32_t kPgnIsoRequest = 59904;
constexpr uint32_t kPgnProductInfo = 126996;
constexpr uint32_t kPgnHeartbeat = 126993;
constexpr uint32_t kPgnOperating = 128777;
constexpr uint32_t kPgnMonitoring = 128778;
constexpr uint32_t kPgnMotorCommand = 128776;

constexpr uint32_t kClaimQuietMs = 250;
constexpr uint32_t kStatusPeriodMs = 1000;
constexpr uint32_t kNmeaHeartbeatMs = 60000;
constexpr uint8_t kNullAddress = 254;

struct CanFrame {
  uint32_t id = 0;
  uint8_t data[8] = {};
  uint8_t dlc = 8;
};

struct NameFields {
  uint32_t unique_number = 1;  // 21 bits. 0 is not a useful identity.
  uint16_t manufacturer = 0;   // 11 bits. 0: no NMEA manufacturer code is assigned here.
  uint8_t ecu_instance = 0;    // 3 bits
  uint8_t function_instance = 0;
  uint8_t function = 0;        // no windlass function is in the public class-100 list
  uint8_t device_class = 100;  // deck, cargo, and fishing equipment
  uint8_t system_instance = 0;
  uint8_t industry = 4;        // marine
  bool arbitrary_address = true;
};

struct WindlassReport {
  bool running_up = false;
  bool running_down = false;
  int32_t rode_mm = 0;
  bool fault = false;
};

uint32_t can_id(uint32_t pgn, uint8_t source, uint8_t dest, uint8_t priority);
void pack_name(const NameFields& name, uint8_t out[8]);
uint64_t name_value(const uint8_t name[8]);

// Fills the low 21 bits from a 48-bit MAC so two boards do not share a NAME.
NameFields name_from_mac(uint64_t mac);

class NmeaNode {
 public:
  explicit NmeaNode(NameFields name, uint8_t preferred_address = 128);

  void set_publish(bool enabled);
  void set_report(const WindlassReport& report);
  void set_claim_delay_ms(uint32_t delay_ms) { claim_delay_ms_ = delay_ms; }

  std::vector<CanFrame> tick(uint32_t now_ms);
  std::vector<CanFrame> on_frame(uint32_t now_ms, const CanFrame& frame);

  bool publish_enabled() const { return publish_; }
  bool claimed() const { return state_ == State::Claimed; }
  uint8_t source() const { return source_; }
  uint32_t ignored_motor_commands() const { return ignored_motor_; }

 private:
  enum class State { Idle, Wait, Claiming, Claimed, Failed };

  CanFrame claim_frame() const;
  void append_status(std::vector<CanFrame>& out, bool operating, bool monitoring);
  CanFrame nmea_heartbeat_frame() const;
  std::vector<CanFrame> product_info_frames() const;
  void begin_claim(uint32_t now_ms, std::vector<CanFrame>& out);
  void handle_claim_contest(uint32_t now_ms, const uint8_t their_name[8], std::vector<CanFrame>& out);

  NameFields name_;
  uint8_t name_bytes_[8] = {};
  uint8_t preferred_ = 128;
  uint8_t source_ = 128;
  uint8_t sid_ = 0;
  uint8_t heartbeat_seq_ = 0;
  uint8_t fast_seq_ = 0;
  uint32_t claim_delay_ms_ = 0;
  uint32_t mark_ms_ = 0;
  uint32_t last_status_ms_ = 0;
  uint32_t last_heartbeat_ms_ = 0;
  bool publish_ = false;
  State state_ = State::Idle;
  WindlassReport report_{};
  uint32_t ignored_motor_ = 0;
};

}  // namespace windlass
#endif  // WINDLASS_NMEA_HPP
