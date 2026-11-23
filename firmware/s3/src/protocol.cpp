#include "windlass/protocol.hpp"

#include <cctype>
#include <cstdlib>
#include <sstream>

namespace windlass {
namespace {

std::string trim(const std::string& in) {
  std::size_t begin = 0;
  while (begin < in.size() && std::isspace(static_cast<unsigned char>(in[begin]))) ++begin;
  std::size_t end = in.size();
  while (end > begin && std::isspace(static_cast<unsigned char>(in[end - 1]))) --end;
  return in.substr(begin, end - begin);
}

bool parse_u32(const std::string& text, uint32_t& out) {
  if (text.empty()) return false;
  char* end = nullptr;
  const unsigned long value = std::strtoul(text.c_str(), &end, 10);
  if (end == text.c_str() || *end != '\0') return false;
  out = static_cast<uint32_t>(value);
  return true;
}

const char* direction_token(Direction direction) {
  switch (direction) {
    case Direction::Up:
      return "U";
    case Direction::Down:
      return "D";
    case Direction::Conflict:
      return "X";
    case Direction::Stopped:
      return "S";
  }
  return "S";
}

}  // namespace

bool parse_command(const std::string& line, Command& out) {
  std::istringstream in(trim(line));
  std::string magic;
  std::string kind;
  std::string session;
  std::string seq_text;
  std::string ttl_text;
  if (!(in >> magic >> session >> seq_text >> kind >> ttl_text)) return false;
  std::string extra;
  if (in >> extra) return false;
  if (magic != "WLC1CMD") return false;
  Command cmd;
  cmd.session = session;
  if (!parse_u32(seq_text, cmd.sequence) || cmd.sequence == 0) return false;
  if (!parse_u32(ttl_text, cmd.ttl_ms)) return false;
  if (kind == "UP") cmd.kind = CmdKind::Up;
  else if (kind == "DOWN") cmd.kind = CmdKind::Down;
  else if (kind == "STOP") cmd.kind = CmdKind::Stop;
  else if (kind == "BOTH") cmd.kind = CmdKind::Both;
  else return false;
  out = cmd;
  return true;
}

std::string format_ack(const std::string& session, uint32_t sequence, bool ok) {
  return "WLC1ACK " + session + " " + std::to_string(sequence) + (ok ? " OK" : " REJECT");
}

std::string format_telemetry(const Controller& controller) {
  const ChainState& chain = controller.chain();
  std::ostringstream out;
  out << "WLC1 " << controller.session() << ' ' << chain.pulses << ' ' << chain.millimetres()
      << ' ' << chain.mm_per_pulse << ' ' << direction_token(controller.direction()) << ' '
      << (controller.running() ? 1 : 0) << ' ' << (controller.fault() ? 1 : 0) << ' '
      << (controller.start_locked() ? 1 : 0);
  return out.str();
}

}  // namespace windlass
