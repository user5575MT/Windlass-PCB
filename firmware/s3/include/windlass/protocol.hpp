#pragma once

#include "windlass/controller.hpp"

#include <string>

namespace windlass {

// On-wire text used by this image. The prototype datagram layout was not in
// this repository, so this text is the contract for the integrated board.
// SoftAP presence is not authentication: a command must name the current
// session and a new sequence.

bool parse_command(const std::string& line, Command& out);
std::string format_ack(const std::string& session, uint32_t sequence, bool ok);
std::string format_telemetry(const Controller& controller);

}  // namespace windlass
