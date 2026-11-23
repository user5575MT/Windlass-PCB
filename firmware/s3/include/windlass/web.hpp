#ifndef WINDLASS_WEB_HPP
#define WINDLASS_WEB_HPP

#include "windlass/controller.hpp"

#include <string>

namespace windlass {

// Configuration page. It sets chain position and millimetres per pulse.
// It has no UP, DOWN, or STOP control.

std::string config_page(const Controller& controller);
std::string status_json(const Controller& controller);
// body is application/x-www-form-urlencoded. Returns false if nothing valid
// was applied. Does not call the command path.
bool apply_config(Controller& controller, const std::string& body);

}  // namespace windlass
#endif  // WINDLASS_WEB_HPP
