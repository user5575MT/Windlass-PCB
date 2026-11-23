#ifndef WINDLASS_REMOTE_GAP_HPP
#define WINDLASS_REMOTE_GAP_HPP

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace windlass {

// What the interface document records from the prototype, and no more.
// The byte layout, the password, and the Pi bridge were not in the source
// available to this image. consider_remote() therefore accepts nothing.

struct RemoteDecision {
  bool accepted = false;
  const char* reason =
      "The prototype datagram layout is not available, so this packet is not a command.";
};

inline RemoteDecision consider_remote(const uint8_t*, std::size_t) { return {}; }

struct ContractFact {
  const char* item;
  const char* state;
};

// Each row is either a value copied from the interface document or an
// explicit gap. Nothing here is a substitute packet format.
inline std::vector<ContractFact> remote_contract() {
  return {
      {"SoftAP SSID", "WindlassCounter, from the interface document"},
      {"SoftAP password", "missing: a secret in WindlassController main.cpp, not copied"},
      {"Telemetry port", "UDP 4210 broadcast, from the interface document"},
      {"Telemetry layout", "missing: magic name WLC1 only; field order and encoding were not copied"},
      {"Command port", "UDP 4212, from the interface document"},
      {"Command layout", "missing: magic names WLC1CMD and WLC1ACK only; bytes were not copied"},
      {"Command TTL", "300 ms default, clamped to 150–1000 ms, from the interface document"},
      {"Session", "a new RFC4122 UUID after boot, stop, or fault; the field that carries it was not copied"},
      {"Authentication", "missing: algorithm, token, and key. SoftAP presence is not authentication"},
      {"Link loss", "the command path drops the coils and does not resume the old hold"},
      {"Prototype relay compile flag", "ENABLE_RELAY_CONTROL defaults off in the prototype; that tree is not edited"},
      {"Pi windlass bridge",
       "missing: no source, port, or message definition in this repository, in user5575MT GitHub, or in Origin"},
  };
}

inline bool contract_marks_missing(const std::vector<ContractFact>& facts, const char* item) {
  for (const auto& fact : facts) {
    if (fact.item == std::string(item) && std::string(fact.state).find("missing:") == 0) return true;
  }
  return false;
}

}  // namespace windlass
#endif  // WINDLASS_REMOTE_GAP_HPP
