#include "windlass/web.hpp"

#include <cstdlib>
#include <sstream>

namespace windlass {
namespace {

std::string field(const std::string& body, const std::string& key) {
  const std::string token = key + "=";
  std::size_t at = 0;
  while (at < body.size()) {
    if (body.compare(at, token.size(), token) == 0) {
      const std::size_t start = at + token.size();
      const std::size_t end = body.find('&', start);
      return body.substr(start, end == std::string::npos ? std::string::npos : end - start);
    }
    const std::size_t next = body.find('&', at);
    if (next == std::string::npos) break;
    at = next + 1;
  }
  return {};
}

bool parse_i32(const std::string& text, int32_t& out) {
  if (text.empty()) return false;
  char* end = nullptr;
  const long value = std::strtol(text.c_str(), &end, 10);
  if (end == text.c_str() || *end != '\0') return false;
  out = static_cast<int32_t>(value);
  return true;
}

}  // namespace

std::string config_page(const Controller& controller) {
  const ChainState& chain = controller.chain();
  std::ostringstream page;
  page << "<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width\">"
       << "<title>Windlass chain</title></head><body>"
       << "<h1>Chain position</h1>"
       << "<p>Pulses " << chain.pulses << ", " << chain.millimetres()
       << " mm, " << chain.mm_per_pulse << " mm per pulse.</p>"
       << "<form method=\"POST\" action=\"/config\">"
       << "<label>Millimetres per pulse <input name=\"mm_per\" value=\"" << chain.mm_per_pulse
       << "\"></label><br>"
       << "<label>Pulse count <input name=\"pulses\" value=\"" << chain.pulses << "\"></label><br>"
       << "<button type=\"submit\">Save</button></form>"
       << "<p>UP and DOWN are not on this page. Hold-to-run stays on UDP port 4212.</p>"
       << "</body></html>";
  return page.str();
}

std::string status_json(const Controller& controller) {
  const ChainState& chain = controller.chain();
  std::ostringstream out;
  out << "{\"session\":\"" << controller.session() << "\",\"pulses\":" << chain.pulses
      << ",\"mm\":" << chain.millimetres() << ",\"mm_per\":" << chain.mm_per_pulse
      << ",\"running\":" << (controller.running() ? "true" : "false")
      << ",\"fault\":" << (controller.fault() ? "true" : "false") << "}";
  return out.str();
}

bool apply_config(Controller& controller, const std::string& body) {
  bool applied = false;
  const std::string mm = field(body, "mm_per");
  if (!mm.empty()) {
    int32_t value = 0;
    if (!parse_i32(mm, value) || !controller.set_calibration(value)) return false;
    applied = true;
  }
  const std::string pulses = field(body, "pulses");
  if (!pulses.empty()) {
    int32_t value = 0;
    if (!parse_i32(pulses, value)) return false;
    controller.set_pulses(value);
    applied = true;
  }
  return applied;
}

}  // namespace windlass
