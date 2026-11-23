#pragma once

#include "windlass/gpio_map.hpp"

#include <cstdint>
#include <string>

namespace windlass {

enum class CmdKind { Up, Down, Stop, Both };

struct Command {
  std::string session;
  uint32_t sequence = 0;
  CmdKind kind = CmdKind::Stop;
  uint32_t ttl_ms = kTtlDefaultMs;
};

struct Sense {
  bool reed_high = false;
  bool up_sense_low = false;     // opto, low means that direction is live
  bool down_sense_low = false;
  bool coil_rail_high = false;   // GPIO14 high means the coil rail is present
  bool publish_high = false;
  bool link_up = false;
};

struct Drive {
  bool up_req = false;
  bool down_req = false;
  bool heartbeat = false;
  bool heartbeat_rising = false;
  bool led_red = false;
  bool led_green = false;
};

struct ChainState {
  int32_t pulses = 0;
  int32_t mm_per_pulse = kDefaultMmPerPulse;
  int64_t millimetres() const {
    return static_cast<int64_t>(pulses) * static_cast<int64_t>(mm_per_pulse);
  }
};

// UP hauls chain in (pulses decrease). DOWN pays chain out (pulses increase).
enum class Direction { Stopped, Up, Down, Conflict };

class Store {
 public:
  virtual ~Store() = default;
  virtual bool load(ChainState& out) = 0;
  virtual void save(const ChainState& in) = 0;
};

class MemoryStore : public Store {
 public:
  bool load(ChainState& out) override {
    if (!have_) return false;
    out = saved_;
    return true;
  }
  void save(const ChainState& in) override {
    saved_ = in;
    have_ = true;
  }
  bool have() const { return have_; }

 private:
  ChainState saved_{};
  bool have_ = false;
};

// Decision core for the integrated board. Outputs start off and stay off
// until a new RUN is accepted. A RUN that has already expired, or that
// belongs to a session retired by STOP, TTL, conflict, or rail loss, does
// not start the windlass. Heartbeat edges are produced only while one
// direction request is on.
class Controller {
 public:
  explicit Controller(Store& store);

  void begin(uint32_t now_ms, const Sense& sense);
  // Applies immediately. STOP clears the requests and the heartbeat in this
  // call. Returns false when the packet must not change the outputs.
  bool command(uint32_t now_ms, const Command& cmd);
  void tick(uint32_t now_ms, const Sense& sense);

  const Drive& drive() const { return drive_; }
  const ChainState& chain() const { return chain_; }
  const std::string& session() const { return session_; }
  bool running() const { return running_; }
  bool fault() const { return fault_; }
  bool start_locked() const { return start_locked_; }
  Direction direction() const;
  uint32_t ttl_ms() const { return ttl_ms_; }

  // Configuration only. Neither call asserts a coil request.
  bool set_calibration(int32_t mm_per_pulse);
  void set_pulses(int32_t pulses);

 private:
  void halt(bool as_fault);
  void refresh_motion(uint32_t now_ms);
  void sample_reed(uint32_t now_ms);
  void service_watchdog(uint32_t now_ms);
  void update_heartbeat(uint32_t now_ms, bool motion);
  void update_leds();

  Store& store_;
  ChainState chain_{};
  Sense sense_{};
  Drive drive_{};
  std::string session_ = "s1";
  uint32_t generation_ = 1;
  uint32_t last_seq_ = 0;
  uint32_t ttl_ms_ = kTtlDefaultMs;
  uint32_t deadline_ms_ = 0;
  uint32_t reed_change_ms_ = 0;
  uint32_t last_rise_ms_ = 0;
  bool begun_ = false;
  bool running_ = false;
  bool want_up_ = false;
  bool want_down_ = false;
  bool fault_ = false;
  bool start_locked_ = false;
  bool reed_debounced_ = false;
  bool reed_candidate_ = false;
  bool have_rise_ = false;
};

uint32_t clamp_ttl(uint32_t ttl_ms);

}  // namespace windlass
