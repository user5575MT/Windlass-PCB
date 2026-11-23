#include "windlass/controller.hpp"
#include "windlass/nmea.hpp"
#include "windlass/protocol.hpp"
#include "windlass/web.hpp"

#include <cstdlib>
#include <iostream>
#include <string>

namespace {

int failures = 0;

void expect(bool cond, const char* name) {
  if (cond) return;
  std::cerr << "FAIL " << name << '\n';
  ++failures;
}

windlass::Sense rail_on() {
  windlass::Sense sense;
  sense.coil_rail_high = true;
  sense.link_up = true;
  return sense;
}

windlass::Command cmd(const std::string& session, uint32_t seq, windlass::CmdKind kind, uint32_t ttl = 300) {
  windlass::Command out;
  out.session = session;
  out.sequence = seq;
  out.kind = kind;
  out.ttl_ms = ttl;
  return out;
}

int rising_edges(windlass::Controller& controller, uint32_t from, uint32_t to, const windlass::Sense& sense) {
  int edges = 0;
  for (uint32_t t = from; t <= to; t += 10) {
    controller.tick(t, sense);
    if (controller.drive().heartbeat_rising) ++edges;
  }
  return edges;
}

void test_boot_outputs_off() {
  windlass::MemoryStore store;
  windlass::Controller controller(store);
  controller.tick(0, rail_on());
  expect(!controller.drive().up_req && !controller.drive().down_req && !controller.drive().heartbeat,
         "tick before begin stays off");
  controller.begin(0, rail_on());
  expect(!controller.drive().up_req && !controller.drive().down_req && !controller.drive().heartbeat,
         "begin leaves the coils off");
  expect(rising_edges(controller, 10, 2000, rail_on()) == 0, "no heartbeat without a command");
}

void test_stop_priority_and_stale_run() {
  windlass::MemoryStore store;
  windlass::Controller controller(store);
  auto sense = rail_on();
  controller.begin(0, sense);
  const std::string first = controller.session();
  expect(controller.command(0, cmd(first, 1, windlass::CmdKind::Up)), "UP accepted");
  expect(controller.drive().up_req && controller.drive().heartbeat_rising, "UP raises the request and an edge");
  expect(!controller.drive().down_req, "DOWN stays low during UP");
  expect(controller.command(20, cmd(first, 2, windlass::CmdKind::Stop)), "STOP accepted");
  expect(!controller.drive().up_req && !controller.drive().down_req && !controller.drive().heartbeat &&
             !controller.drive().heartbeat_rising,
         "STOP clears requests and heartbeat immediately");
  expect(!controller.fault(), "STOP is not a fault");
  expect(controller.start_locked(), "STOP locks a restart");
  const std::string retired = controller.session();
  expect(retired != first, "STOP retires the session");
  expect(!controller.command(30, cmd(first, 3, windlass::CmdKind::Up)), "old session cannot restart");
  expect(!controller.drive().up_req && !controller.drive().heartbeat, "old RUN leaves outputs off");
  expect(!controller.command(40, cmd(retired, 1, windlass::CmdKind::Up)), "RUN on the new session is stale");
  expect(!controller.drive().up_req, "stale RUN does not start");
  expect(controller.command(50, cmd(retired, 2, windlass::CmdKind::Stop)), "release on the new session");
  expect(!controller.drive().up_req && !controller.drive().heartbeat, "release stays off");
  expect(controller.command(60, cmd(retired, 3, windlass::CmdKind::Up)), "a new press after release starts");
  expect(controller.drive().up_req && controller.drive().heartbeat, "new press drives UP");
}

void test_watchdog() {
  windlass::MemoryStore store;
  windlass::Controller controller(store);
  auto sense = rail_on();
  controller.begin(0, sense);
  const std::string session = controller.session();
  expect(controller.command(0, cmd(session, 1, windlass::CmdKind::Down, 50)), "short TTL is clamped");
  controller.tick(149, sense);
  expect(controller.running() && controller.drive().down_req, "still running at 149 ms");
  controller.tick(150, sense);
  expect(!controller.running() && !controller.drive().down_req && !controller.drive().heartbeat,
         "150 ms clamp expires the hold");
  expect(controller.fault() && controller.start_locked(), "expiry latches a fault");
  const std::string expired = controller.session();
  expect(!controller.command(160, cmd(session, 2, windlass::CmdKind::Down)), "expired session cannot restart");
  expect(!controller.drive().down_req && !controller.drive().heartbeat, "replay stays off");
  expect(!controller.command(170, cmd(expired, 1, windlass::CmdKind::Down)), "new session still locked");
  expect(!controller.drive().down_req, "locked session stays off");

  windlass::Controller longer(store);
  longer.begin(0, sense);
  const std::string live = longer.session();
  expect(longer.command(0, cmd(live, 1, windlass::CmdKind::Up, 300)), "default TTL");
  expect(!longer.command(200, cmd(live, 1, windlass::CmdKind::Up, 300)), "repeated sequence is not a refresh");
  longer.tick(299, sense);
  expect(longer.running(), "hold is still live at 299 ms");
  longer.tick(300, sense);
  expect(!longer.running() && !longer.drive().up_req && !longer.drive().heartbeat, "300 ms expiry");
  expect(!longer.command(400, cmd(live, 2, windlass::CmdKind::Up, 5000)), "old session after 300 ms");

  windlass::Controller refreshed(store);
  refreshed.begin(0, sense);
  const std::string held = refreshed.session();
  expect(refreshed.command(0, cmd(held, 1, windlass::CmdKind::Down, 300)), "hold starts");
  expect(refreshed.command(200, cmd(held, 2, windlass::CmdKind::Down, 300)), "a new sequence refreshes");
  refreshed.tick(499, sense);
  expect(refreshed.running() && refreshed.drive().down_req, "refresh keeps the hold to 499 ms");
  refreshed.tick(500, sense);
  expect(!refreshed.running() && !refreshed.drive().heartbeat, "refreshed hold expires at 500 ms");
  expect(!longer.drive().up_req, "a late RUN does not restart");
}

void test_conflict_and_heartbeat_window() {
  windlass::MemoryStore store;
  windlass::Controller controller(store);
  auto sense = rail_on();
  controller.begin(0, sense);
  const std::string session = controller.session();
  expect(controller.command(0, cmd(session, 1, windlass::CmdKind::Up)), "conflict setup");
  expect(!controller.command(10, cmd(session, 2, windlass::CmdKind::Down)), "opposite command fails off");
  expect(!controller.drive().up_req && !controller.drive().down_req && !controller.drive().heartbeat,
         "conflict clears both requests and the heartbeat");
  expect(controller.fault(), "conflict is a fault");

  windlass::Controller both(store);
  both.begin(0, sense);
  const std::string both_session = both.session();
  expect(!both.command(0, cmd(both_session, 1, windlass::CmdKind::Both)), "BOTH rejected");
  expect(!both.drive().up_req && !both.drive().down_req && !both.drive().heartbeat_rising,
         "BOTH produces no request and no edge");

  windlass::Controller run(store);
  run.begin(1000, sense);
  const std::string run_session = run.session();
  expect(run.command(1000, cmd(run_session, 1, windlass::CmdKind::Up, 1000)), "heartbeat run");
  int edges = run.drive().heartbeat_rising ? 1 : 0;
  bool edge_while_idle = false;
  for (uint32_t t = 1010; t <= 1800; t += 10) {
    run.tick(t, sense);
    if (run.drive().heartbeat_rising) ++edges;
    if (run.drive().heartbeat_rising && !run.running()) edge_while_idle = true;
  }
  expect(edges >= 9 && edges <= 12, "edges continue through a legal hold");
  expect(!edge_while_idle, "edges only while the hold is legal");
  expect(run.command(1810, cmd(run_session, 2, windlass::CmdKind::Stop)), "stop the heartbeat run");
  int after = 0;
  auto stopped = rail_on();
  for (uint32_t t = 1820; t <= 3000; t += 10) {
    run.tick(t, stopped);
    if (run.drive().heartbeat || run.drive().heartbeat_rising || run.drive().up_req) ++after;
  }
  expect(after == 0, "no heartbeat and no request after STOP");
}

void test_rail_loss_and_chain() {
  windlass::MemoryStore store;
  windlass::Controller controller(store);
  auto sense = rail_on();
  sense.up_sense_low = true;
  sense.reed_high = false;
  controller.begin(0, sense);
  const std::string session = controller.session();
  expect(controller.command(0, cmd(session, 1, windlass::CmdKind::Up)), "run before rail loss");
  sense.coil_rail_high = false;
  controller.tick(20, sense);
  expect(!controller.running() && !controller.drive().up_req && !controller.drive().heartbeat,
         "rail loss stops the request and the heartbeat");
  sense.coil_rail_high = true;
  controller.tick(40, sense);
  expect(!controller.drive().up_req && !controller.drive().heartbeat, "rail returning does not restart");
  expect(!controller.command(50, cmd(session, 2, windlass::CmdKind::Up)), "session retired by the rail");

  windlass::MemoryStore chain_store;
  windlass::Controller chain(chain_store);
  auto idle = rail_on();
  idle.reed_high = true;
  idle.up_sense_low = true;
  chain.begin(0, idle);
  expect(chain.chain().pulses == 0, "the level at start is not a pulse");
  idle.reed_high = false;
  chain.tick(0, idle);
  chain.tick(30, idle);
  expect(chain.chain().pulses == 0, "a falling edge is not a pulse");
  idle.reed_high = true;
  chain.tick(30, idle);
  chain.tick(60, idle);
  expect(chain.chain().pulses == -1, "UP counts the rising edge as chain in");
  idle.up_sense_low = false;
  idle.down_sense_low = true;
  idle.reed_high = false;
  chain.tick(60, idle);
  chain.tick(90, idle);
  idle.reed_high = true;
  chain.tick(90, idle);
  chain.tick(120, idle);
  expect(chain.chain().pulses == 0, "DOWN counts the next rising edge as chain out");
  idle.up_sense_low = true;
  idle.reed_high = false;
  chain.tick(120, idle);
  chain.tick(150, idle);
  idle.reed_high = true;
  chain.tick(150, idle);
  chain.tick(180, idle);
  expect(chain.chain().pulses == 0, "both senses active ignore the edge");

  expect(chain.set_calibration(500), "calibration accepted");
  expect(!chain.set_calibration(0), "zero calibration rejected");
  chain.set_pulses(12);
  expect(!chain.drive().up_req && !chain.drive().down_req && !chain.drive().heartbeat,
         "saving the chain does not drive a coil");

  windlass::Controller restored(chain_store);
  auto quiet = rail_on();
  restored.begin(0, quiet);
  expect(restored.chain().pulses == 12, "saved pulses come back");
  expect(restored.chain().mm_per_pulse == 500, "saved calibration comes back");
  expect(!restored.drive().up_req && !restored.drive().heartbeat, "restored position stays off");
}

void test_protocol_web_nmea_and_pins() {
  windlass::Command parsed;
  expect(windlass::parse_command("WLC1CMD sess 7 UP 300", parsed), "command parses");
  expect(parsed.kind == windlass::CmdKind::Up && parsed.sequence == 7 && parsed.ttl_ms == 300, "fields");
  expect(!windlass::parse_command("WLC1 sess 7 UP 300", parsed), "telemetry is not a command");
  expect(!windlass::parse_command("WLC1CMD sess 0 UP 300", parsed), "sequence 0 rejected");
  expect(windlass::format_ack("s2", 4, false).find("REJECT") != std::string::npos, "reject ack");

  windlass::MemoryStore store;
  windlass::Controller controller(store);
  auto sense = rail_on();
  controller.begin(0, sense);
  const auto before = controller.drive();
  expect(windlass::apply_config(controller, "mm_per=360&pulses=8"), "web config applies");
  expect(controller.chain().pulses == 8 && controller.chain().mm_per_pulse == 360, "web values stored");
  expect(controller.drive().up_req == before.up_req && controller.drive().down_req == before.down_req &&
             controller.drive().heartbeat == before.heartbeat,
         "web config does not move an output");
  expect(windlass::config_page(controller).find("mm_per") != std::string::npos, "page has calibration");
  expect(windlass::config_page(controller).find("WLC1CMD") == std::string::npos, "page has no command");
  expect(windlass::status_json(controller).find("\"running\":false") != std::string::npos, "status idle");

  auto frames = windlass::status_frames(controller, false, 0x22);
  expect(frames.empty(), "strap open sends nothing");
  controller.command(0, cmd(controller.session(), 1, windlass::CmdKind::Up));
  frames = windlass::status_frames(controller, true, 0x22);
  expect(frames.size() == 2, "two status frames");
  expect(frames[0].id == windlass::nmea_id(windlass::kPgnOperating, 0x22, 6), "operating id");
  expect(frames[1].id == windlass::nmea_id(windlass::kPgnMonitoring, 0x22, 6), "monitoring id");
  expect(frames[0].data[0] == 1, "operating says UP");
  for (const auto& frame : frames) {
    const uint32_t pgn = ((frame.id >> 8) & 0xffffu);
    expect(pgn != windlass::kPgnMotorCommand, "no motor-command PGN");
  }

  expect(windlass::Gpio::heartbeat == 1, "GPIO1 heartbeat");
  expect(windlass::Gpio::twai_tx == 4 && windlass::Gpio::twai_rx == 5, "TWAI pins");
  expect(windlass::Gpio::reed == 6, "reed");
  expect(windlass::Gpio::up_sense == 7 && windlass::Gpio::down_sense == 8, "sense");
  expect(windlass::Gpio::up_req == 9 && windlass::Gpio::down_req == 10, "requests");
  expect(windlass::Gpio::coil_rail == 14, "rail");
  expect(windlass::Gpio::led_red == 15 && windlass::Gpio::led_green == 16, "leds");
  expect(windlass::Gpio::publish == 18, "publish strap");
  expect(windlass::kTtlDefaultMs == 300, "300 ms watchdog");
}

}  // namespace

int main() {
  test_boot_outputs_off();
  test_stop_priority_and_stale_run();
  test_watchdog();
  test_conflict_and_heartbeat_window();
  test_rail_loss_and_chain();
  test_protocol_web_nmea_and_pins();
  if (failures != 0) {
    std::cerr << failures << " failed\n";
    return 1;
  }
  std::cout << "all tests passed\n";
  return 0;
}
