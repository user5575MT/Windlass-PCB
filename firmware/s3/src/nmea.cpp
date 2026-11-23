#include "windlass/nmea.hpp"

#include <cstring>

namespace windlass {
namespace {

struct Decoded {
  uint8_t priority = 0;
  uint32_t pgn = 0;
  uint8_t source = 0;
  uint8_t dest = 255;
};

Decoded decode(uint32_t id) {
  Decoded out;
  out.source = static_cast<uint8_t>(id);
  const uint8_t ps = static_cast<uint8_t>(id >> 8);
  const uint8_t pf = static_cast<uint8_t>(id >> 16);
  const uint8_t dp = static_cast<uint8_t>((id >> 24) & 1u);
  out.priority = static_cast<uint8_t>((id >> 26) & 7u);
  out.pgn = (static_cast<uint32_t>(dp) << 16) | (static_cast<uint32_t>(pf) << 8);
  if (pf < 240) {
    out.dest = ps;
  } else {
    out.pgn |= ps;
  }
  return out;
}

class BitWriter {
 public:
  explicit BitWriter(uint8_t* data) : data_(data) {}
  void put(uint32_t value, int bits) {
    for (int i = 0; i < bits; ++i) {
      if ((value >> i) & 1u) data_[bit_ / 8] |= static_cast<uint8_t>(1u << (bit_ % 8));
      ++bit_;
    }
  }

 private:
  uint8_t* data_;
  int bit_ = 0;
};

void put_fixed_string(uint8_t* dest, std::size_t width, const char* text) {
  std::memset(dest, 0xff, width);
  if (text == nullptr) return;
  const std::size_t length = std::strlen(text);
  const std::size_t copy = length < width ? length : width;
  std::memcpy(dest, text, copy);
  if (copy < width) dest[copy] = 0;
}

std::vector<CanFrame> fast_frames(uint32_t pgn, uint8_t source, uint8_t& sequence, const uint8_t* payload,
                                  std::size_t length) {
  std::vector<CanFrame> frames;
  const uint8_t seq = static_cast<uint8_t>(sequence & 7u);
  sequence = static_cast<uint8_t>((sequence + 1) & 7u);
  std::size_t offset = 0;
  int index = 0;
  while (offset < length) {
    CanFrame frame;
    frame.id = can_id(pgn, source, 255, 6);
    frame.data[0] = static_cast<uint8_t>((seq << 5) | (index & 0x1f));
    int used = 1;
    if (index == 0) {
      frame.data[1] = static_cast<uint8_t>(length);
      used = 2;
    }
    while (used < 8 && offset < length) {
      frame.data[used++] = payload[offset++];
    }
    frame.dlc = static_cast<uint8_t>(used);
    frames.push_back(frame);
    ++index;
  }
  return frames;
}

uint16_t rode_decimetres(int32_t rode_mm) {
  if (rode_mm < 0) return 0xffffu;
  const int32_t dm = rode_mm / 100;
  if (dm > 65532) return 65532;
  return static_cast<uint16_t>(dm);
}

}  // namespace

uint32_t can_id(uint32_t pgn, uint8_t source, uint8_t dest, uint8_t priority) {
  const uint8_t pf = static_cast<uint8_t>(pgn >> 8);
  const uint8_t dp = static_cast<uint8_t>((pgn >> 16) & 1u);
  const uint8_t ps = pf < 240 ? dest : static_cast<uint8_t>(pgn);
  return (static_cast<uint32_t>(priority & 7u) << 26) | (static_cast<uint32_t>(dp) << 24) |
         (static_cast<uint32_t>(pf) << 16) | (static_cast<uint32_t>(ps) << 8) | source;
}

void pack_name(const NameFields& name, uint8_t out[8]) {
  std::memset(out, 0, 8);
  BitWriter bits(out);
  bits.put(name.unique_number & 0x1fffffu, 21);
  bits.put(name.manufacturer & 0x7ffu, 11);
  bits.put(name.ecu_instance & 0x7u, 3);
  bits.put(name.function_instance & 0x1fu, 5);
  bits.put(name.function, 8);
  bits.put(0, 1);
  bits.put(name.device_class & 0x7fu, 7);
  bits.put(name.system_instance & 0xfu, 4);
  bits.put(name.industry & 0x7u, 3);
  bits.put(name.arbitrary_address ? 1u : 0u, 1);
}

uint64_t name_value(const uint8_t name[8]) {
  uint64_t value = 0;
  for (int i = 0; i < 8; ++i) value |= static_cast<uint64_t>(name[i]) << (8 * i);
  return value;
}

NameFields name_from_mac(uint64_t mac) {
  NameFields name;
  name.unique_number = static_cast<uint32_t>(mac & 0x1fffffu);
  if (name.unique_number == 0) name.unique_number = 1;
  return name;
}

NmeaNode::NmeaNode(NameFields name, uint8_t preferred_address)
    : name_(name), preferred_(preferred_address), source_(preferred_address) {
  pack_name(name_, name_bytes_);
}

void NmeaNode::set_publish(bool enabled) { publish_ = enabled; }

void NmeaNode::set_report(const WindlassReport& report) { report_ = report; }

CanFrame NmeaNode::claim_frame() const {
  CanFrame frame;
  frame.id = can_id(kPgnAddressClaim, source_, 255, 6);
  std::memcpy(frame.data, name_bytes_, 8);
  frame.dlc = 8;
  return frame;
}

void NmeaNode::append_status(std::vector<CanFrame>& out, bool operating, bool monitoring) {
  const uint8_t direction = report_.running_up ? 2u : (report_.running_down ? 1u : 0u);
  const uint8_t motion = direction;
  const uint16_t rode = rode_decimetres(report_.rode_mm);
  if (operating) {
    uint8_t bytes[8] = {};
    BitWriter op(bytes);
    op.put(sid_, 8);
    op.put(0, 8);  // single windlass
    op.put(direction, 2);
    op.put(motion, 2);
    op.put(0, 2);  // chain
    op.put(0x3u, 2);
    op.put(rode, 16);
    op.put(0xffffu, 16);  // line speed is not measured
    op.put(0x3u, 2);       // no docking sensor; 0 would mean "not docked"
    op.put(report_.fault ? 1u : 0u, 6);
    CanFrame frame;
    frame.id = can_id(kPgnOperating, source_, 255, 6);
    std::memcpy(frame.data, bytes, 8);
    out.push_back(frame);
  }
  if (monitoring) {
    uint8_t bytes[8] = {};
    BitWriter mon(bytes);
    mon.put(sid_, 8);
    mon.put(0, 8);
    mon.put(0, 8);
    mon.put(0xffu, 8);
    mon.put(0xffu, 8);
    mon.put(0xffffu, 16);
    mon.put(0xffu, 8);
    CanFrame frame;
    frame.id = can_id(kPgnMonitoring, source_, 255, 6);
    std::memcpy(frame.data, bytes, 8);
    out.push_back(frame);
  }
  if (operating || monitoring) sid_ = static_cast<uint8_t>(sid_ + 1);
}

CanFrame NmeaNode::nmea_heartbeat_frame() const {
  CanFrame frame;
  frame.id = can_id(kPgnHeartbeat, source_, 255, 7);
  BitWriter bits(frame.data);
  bits.put(60000u, 16);
  bits.put(heartbeat_seq_, 8);
  bits.put(0, 2);    // error active
  bits.put(0x3u, 2);  // no second controller
  bits.put(report_.fault ? 1u : 0u, 2);
  bits.put(0x3fffffffu, 30);
  bits.put(0xfu, 4);
  frame.dlc = 8;
  return frame;
}

std::vector<CanFrame> NmeaNode::product_info_frames() const {
  // 132 bytes stops before the certification-level field. Level 0 in the
  // public lookup is "Level A", which this board does not hold.
  uint8_t payload[132] = {};
  payload[0] = static_cast<uint8_t>(2100);
  payload[1] = static_cast<uint8_t>(2100 >> 8);
  payload[2] = 1;
  payload[3] = 0;
  put_fixed_string(payload + 4, 32, "Windlass-PCB");
  put_fixed_string(payload + 36, 32, "s3");
  put_fixed_string(payload + 68, 32, "install-v2");
  put_fixed_string(payload + 100, 32, "unassigned");
  uint8_t seq = fast_seq_;
  auto frames = fast_frames(kPgnProductInfo, source_, seq, payload, sizeof(payload));
  return frames;
}

void NmeaNode::begin_claim(uint32_t now_ms, std::vector<CanFrame>& out) {
  state_ = State::Claiming;
  mark_ms_ = now_ms;
  out.push_back(claim_frame());
}

void NmeaNode::handle_claim_contest(uint32_t now_ms, const uint8_t their_name[8], std::vector<CanFrame>& out) {
  const uint64_t theirs = name_value(their_name);
  const uint64_t ours = name_value(name_bytes_);
  if (theirs == ours) return;
  if (ours < theirs) {
    state_ = State::Claiming;
    mark_ms_ = now_ms;
    out.push_back(claim_frame());
    return;
  }
  if (source_ >= 251) {
    source_ = kNullAddress;
    state_ = State::Failed;
    out.push_back(claim_frame());
    return;
  }
  ++source_;
  begin_claim(now_ms, out);
}

std::vector<CanFrame> NmeaNode::tick(uint32_t now_ms) {
  std::vector<CanFrame> out;
  if (!publish_) {
    state_ = State::Idle;
    return out;
  }
  if (state_ == State::Idle) {
    state_ = State::Wait;
    mark_ms_ = now_ms;
    source_ = preferred_;
  }
  if (state_ == State::Wait && static_cast<uint32_t>(now_ms - mark_ms_) >= claim_delay_ms_) {
    begin_claim(now_ms, out);
  }
  if (state_ == State::Claiming && static_cast<uint32_t>(now_ms - mark_ms_) >= kClaimQuietMs) {
    state_ = State::Claimed;
    last_status_ms_ = now_ms;
    last_heartbeat_ms_ = now_ms;
    append_status(out, true, true);
  }
  if (state_ == State::Claimed && static_cast<uint32_t>(now_ms - last_status_ms_) >= kStatusPeriodMs) {
    last_status_ms_ = now_ms;
    append_status(out, true, true);
  }
  if (state_ == State::Claimed && static_cast<uint32_t>(now_ms - last_heartbeat_ms_) >= kNmeaHeartbeatMs) {
    last_heartbeat_ms_ = now_ms;
    out.push_back(nmea_heartbeat_frame());
    heartbeat_seq_ = static_cast<uint8_t>(heartbeat_seq_ + 1);
  }
  return out;
}

std::vector<CanFrame> NmeaNode::on_frame(uint32_t now_ms, const CanFrame& frame) {
  std::vector<CanFrame> out;
  if (!publish_ || state_ == State::Idle) return out;
  const Decoded id = decode(frame.id);
  if (id.pgn == kPgnMotorCommand) {
    ++ignored_motor_;
    return out;
  }
  if (id.pgn == kPgnAddressClaim && id.source == source_ && frame.dlc >= 8 && state_ != State::Failed) {
    handle_claim_contest(now_ms, frame.data, out);
    return out;
  }
  if (id.pgn == kPgnIsoRequest && frame.dlc >= 3 && (id.dest == 255 || id.dest == source_)) {
    const uint32_t requested = static_cast<uint32_t>(frame.data[0]) | (static_cast<uint32_t>(frame.data[1]) << 8) |
                               (static_cast<uint32_t>(frame.data[2]) << 16);
    if (requested == kPgnAddressClaim && state_ != State::Wait) out.push_back(claim_frame());
    if (state_ == State::Claimed && requested == kPgnProductInfo) {
      auto info = product_info_frames();
      fast_seq_ = static_cast<uint8_t>((fast_seq_ + 1) & 7u);
      out.insert(out.end(), info.begin(), info.end());
    }
    if (state_ == State::Claimed && requested == kPgnOperating) append_status(out, true, false);
    if (state_ == State::Claimed && requested == kPgnMonitoring) append_status(out, false, true);
  }
  return out;
}

}  // namespace windlass
