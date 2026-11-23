#include "windlass/controller.hpp"

namespace windlass {

uint32_t clamp_ttl(uint32_t ttl_ms) {
  if (ttl_ms < kTtlMinMs) return kTtlMinMs;
  if (ttl_ms > kTtlMaxMs) return kTtlMaxMs;
  return ttl_ms;
}

Controller::Controller(Store& store) : store_(store) {
  drive_ = Drive{};
}

void Controller::begin(uint32_t now_ms, const Sense& sense) {
  ChainState loaded;
  if (store_.load(loaded) && loaded.mm_per_pulse > 0) {
    chain_ = loaded;
  } else {
    chain_ = ChainState{};
    store_.save(chain_);
  }
  sense_ = sense;
  // The level present at start is not an edge.
  reed_debounced_ = sense.reed_high;
  reed_candidate_ = sense.reed_high;
  reed_change_ms_ = now_ms;
  running_ = false;
  want_up_ = false;
  want_down_ = false;
  fault_ = false;
  start_locked_ = false;
  have_rise_ = false;
  last_seq_ = 0;
  drive_ = Drive{};
  update_leds();
  begun_ = true;
}

Direction Controller::direction() const {
  const bool up = sense_.up_sense_low;
  const bool down = sense_.down_sense_low;
  if (up && down) return Direction::Conflict;
  if (up) return Direction::Up;
  if (down) return Direction::Down;
  return Direction::Stopped;
}

bool Controller::set_calibration(int32_t mm_per_pulse) {
  if (mm_per_pulse < 1 || mm_per_pulse > 10000) return false;
  chain_.mm_per_pulse = mm_per_pulse;
  store_.save(chain_);
  return true;
}

void Controller::set_pulses(int32_t pulses) {
  chain_.pulses = pulses;
  store_.save(chain_);
}

void Controller::halt(bool as_fault) {
  running_ = false;
  want_up_ = false;
  want_down_ = false;
  fault_ = as_fault;
  start_locked_ = true;
  ++generation_;
  session_ = "s" + std::to_string(generation_);
  last_seq_ = 0;
  have_rise_ = false;
  drive_.up_req = false;
  drive_.down_req = false;
  drive_.heartbeat = false;
  drive_.heartbeat_rising = false;
  update_leds();
}

void Controller::update_leds() {
  if (fault_) {
    drive_.led_red = true;
    drive_.led_green = false;
    return;
  }
  if (!sense_.coil_rail_high) {
    // Both LEDs together are the amber indication. There is no blue LED.
    drive_.led_red = true;
    drive_.led_green = true;
    return;
  }
  drive_.led_red = false;
  drive_.led_green = sense_.link_up;
}

void Controller::update_heartbeat(uint32_t now_ms, bool motion) {
  drive_.heartbeat_rising = false;
  if (!motion) {
    drive_.heartbeat = false;
    have_rise_ = false;
    return;
  }
  if (!have_rise_ || static_cast<uint32_t>(now_ms - last_rise_ms_) >= kHeartbeatPeriodMs) {
    drive_.heartbeat = true;
    drive_.heartbeat_rising = true;
    last_rise_ms_ = now_ms;
    have_rise_ = true;
    return;
  }
  if (static_cast<uint32_t>(now_ms - last_rise_ms_) >= kHeartbeatHighMs) {
    drive_.heartbeat = false;
  } else {
    drive_.heartbeat = true;
  }
}

void Controller::refresh_motion(uint32_t now_ms) {
  const bool motion = running_ && sense_.coil_rail_high && (want_up_ != want_down_);
  drive_.up_req = motion && want_up_;
  drive_.down_req = motion && want_down_;
  update_heartbeat(now_ms, motion);
  update_leds();
}

void Controller::sample_reed(uint32_t now_ms) {
  if (sense_.reed_high != reed_candidate_) {
    reed_candidate_ = sense_.reed_high;
    reed_change_ms_ = now_ms;
  }
  if (static_cast<uint32_t>(now_ms - reed_change_ms_) < kDebounceMs) return;
  if (reed_debounced_ == reed_candidate_) return;
  const bool rising = reed_candidate_ && !reed_debounced_;
  reed_debounced_ = reed_candidate_;
  if (!rising) return;
  const Direction dir = direction();
  if (dir == Direction::Up) {
    chain_.pulses -= 1;
    store_.save(chain_);
  } else if (dir == Direction::Down) {
    chain_.pulses += 1;
    store_.save(chain_);
  }
}

void Controller::service_watchdog(uint32_t now_ms) {
  if (!running_) return;
  if (now_ms >= deadline_ms_) halt(true);
}

bool Controller::command(uint32_t now_ms, const Command& cmd) {
  if (!begun_) return false;
  if (cmd.session != session_) return false;
  if (cmd.sequence == 0 || cmd.sequence <= last_seq_) return false;

  if (cmd.kind == CmdKind::Stop) {
    if (!running_) {
      // Release on the current session. This is what clears the lock left
      // by STOP, the TTL, a conflict, or rail loss. It does not start a coil.
      last_seq_ = cmd.sequence;
      if (start_locked_) {
        start_locked_ = false;
        fault_ = false;
        update_leds();
      }
      drive_.up_req = false;
      drive_.down_req = false;
      drive_.heartbeat = false;
      drive_.heartbeat_rising = false;
      return true;
    }
    halt(false);
    return true;
  }
  if (cmd.kind == CmdKind::Both || (want_up_ && cmd.kind == CmdKind::Down) ||
      (want_down_ && cmd.kind == CmdKind::Up)) {
    halt(true);
    return false;
  }
  if (start_locked_) {
    // A RUN after STOP, expiry, conflict, or rail loss is stale until the
    // operator releases on this session. Consuming the sequence keeps the
    // same packet from starting later.
    last_seq_ = cmd.sequence;
    refresh_motion(now_ms);
    return false;
  }
  if (!sense_.coil_rail_high) {
    last_seq_ = cmd.sequence;
    refresh_motion(now_ms);
    return false;
  }

  last_seq_ = cmd.sequence;
  ttl_ms_ = clamp_ttl(cmd.ttl_ms);
  deadline_ms_ = now_ms + ttl_ms_;
  want_up_ = cmd.kind == CmdKind::Up;
  want_down_ = cmd.kind == CmdKind::Down;
  running_ = true;
  fault_ = false;
  refresh_motion(now_ms);
  return true;
}

void Controller::tick(uint32_t now_ms, const Sense& sense) {
  if (!begun_) {
    drive_ = Drive{};
    return;
  }
  const bool rail_was_holding = running_ && sense_.coil_rail_high;
  sense_ = sense;
  sample_reed(now_ms);
  if (running_ && rail_was_holding && !sense_.coil_rail_high) {
    halt(true);
    return;
  }
  service_watchdog(now_ms);
  if (running_) refresh_motion(now_ms);
  else {
    drive_.up_req = false;
    drive_.down_req = false;
    drive_.heartbeat = false;
    drive_.heartbeat_rising = false;
    update_leds();
  }
}

}  // namespace windlass
