#include "windlass/controller.hpp"
#include "windlass/datagram.hpp"
#include "windlass/nmea.hpp"
#include "windlass/remote_gap.hpp"
#include "windlass/sha256.hpp"
#include "windlass/web.hpp"

#include <cstdint>
#include <cstring>
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

void test_link_loss() {
  windlass::MemoryStore store;
  windlass::Controller controller(store);
  auto sense = rail_on();
  sense.link_up = false;
  controller.begin(0, sense);
  expect(!controller.command(0, cmd(controller.session(), 1, windlass::CmdKind::Up)),
         "RUN without a command link does not start");
  expect(!controller.drive().up_req && !controller.drive().heartbeat, "no link leaves the outputs off");

  windlass::Controller live(store);
  auto linked = rail_on();
  live.begin(0, linked);
  const std::string session = live.session();
  expect(live.command(0, cmd(session, 1, windlass::CmdKind::Down, 1000)), "linked hold starts");
  linked.link_up = false;
  live.tick(20, linked);
  expect(!live.running() && !live.drive().down_req && !live.drive().up_req && !live.drive().heartbeat &&
             !live.drive().heartbeat_rising,
         "link loss clears the requests and the heartbeat");
  expect(live.fault() && live.start_locked(), "link loss locks a restart");
  linked.link_up = true;
  live.tick(40, linked);
  expect(!live.drive().down_req && !live.drive().heartbeat, "the link returning does not restart");
  expect(!live.command(50, cmd(session, 2, windlass::CmdKind::Down, 1000)), "the old session stays retired");
}

bool is_motor(uint32_t id) {
  const uint8_t pf = static_cast<uint8_t>(id >> 16);
  const uint8_t ps = static_cast<uint8_t>(id >> 8);
  const uint8_t dp = static_cast<uint8_t>((id >> 24) & 1u);
  uint32_t pgn = (static_cast<uint32_t>(dp) << 16) | (static_cast<uint32_t>(pf) << 8);
  if (pf >= 240) pgn |= ps;
  return pgn == windlass::kPgnMotorCommand;
}

void test_remote_gap_web_nmea_and_pins() {
  const char* invented = "WLC1CMD sess 7 UP 300";
  const auto text = windlass::consider_remote(reinterpret_cast<const uint8_t*>(invented), std::strlen(invented));
  expect(!text.accepted, "the invented text line is not a command");
  const uint8_t binary[8] = {0x57, 0x4c, 0x43, 0x31, 0x00, 0x01, 0x02, 0x03};
  expect(!windlass::consider_remote(binary, sizeof(binary)).accepted, "a binary datagram is not a command");
  expect(!windlass::consider_remote(nullptr, 0).accepted, "an empty datagram is not a command");
  const auto facts = windlass::remote_contract();
  expect(windlass::contract_marks_missing(facts, "SoftAP password"), "password is recorded as missing");
  expect(windlass::contract_marks_missing(facts, "Telemetry layout"), "telemetry bytes are recorded as missing");
  expect(windlass::contract_marks_missing(facts, "Command layout"), "command bytes are recorded as missing");
  expect(windlass::contract_marks_missing(facts, "Authentication"), "authentication is recorded as missing");
  expect(windlass::contract_marks_missing(facts, "Pi windlass bridge"), "the Pi bridge is recorded as missing");

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
  expect(windlass::config_page(controller).find("UDP port") == std::string::npos, "page does not name a command port");
  expect(windlass::status_json(controller).find("\"running\":false") != std::string::npos, "status idle");

  windlass::NameFields sample;
  sample.unique_number = 1083224;
  sample.manufacturer = 381;
  sample.function = 130;
  sample.device_class = 85;
  sample.industry = 4;
  sample.arbitrary_address = true;
  uint8_t packed[8] = {};
  windlass::pack_name(sample, packed);
  const uint8_t expected_name[8] = {0x58, 0x87, 0xb0, 0x2f, 0x00, 0x82, 0xaa, 0xc0};
  expect(std::memcmp(packed, expected_name, 8) == 0, "address-claim NAME matches the published sample");

  const auto ours = windlass::name_from_mac(0);
  expect(ours.unique_number == 1 && ours.manufacturer == 0 && ours.function == 0 && ours.device_class == 100 &&
             ours.industry == 4 && ours.arbitrary_address,
         "this board does not borrow a windlass function or a manufacturer code");
  expect(windlass::name_from_mac(0x123456).unique_number == 0x123456u, "the MAC fills the unique number");

  windlass::NmeaNode silent(windlass::NameFields{});
  expect(!silent.publish_enabled(), "publishing starts disabled");
  expect(silent.tick(0).empty() && silent.tick(10000).empty(), "a closed strap transmits nothing");

  windlass::NmeaNode node(windlass::NameFields{}, 128);
  node.set_publish(true);
  node.set_claim_delay_ms(0);
  windlass::WindlassReport report;
  report.running_up = true;
  report.rode_mm = 3600;
  node.set_report(report);
  auto claim = node.tick(0);
  expect(claim.size() == 1 && !node.claimed(), "the strap starts an address claim and nothing else");
  expect(claim[0].id == windlass::can_id(windlass::kPgnAddressClaim, 128, 255, 6), "claim id");
  expect(claim[0].id == 0x18eeff80u, "claim id carries the data page and the global destination");
  expect(node.tick(249).empty(), "status waits out the 250 ms claim");
  auto status = node.tick(250);
  expect(node.claimed() && status.size() == 2, "status follows a quiet claim");
  expect(status[0].id == 0x19f70980u, "operating id");
  expect(status[0].data[0] == 0 && status[0].data[1] == 0 && status[0].data[2] == 0xca, "UP retrieval encoding");
  expect(status[0].data[3] == 36 && status[0].data[4] == 0, "rode is 36.0 m as decimetres");
  expect(status[0].data[5] == 0xff && status[0].data[6] == 0xff, "line speed is not measured");
  expect(status[0].data[7] == 0x03, "docking is unavailable");
  expect(status[1].id == windlass::can_id(windlass::kPgnMonitoring, 128, 255, 6), "monitoring id");
  expect(status[1].data[0] == 0 && status[1].data[2] == 0 && status[1].data[3] == 0xff && status[1].data[7] == 0xff,
         "monitoring voltages stay unavailable");
  for (const auto& frame : status) expect(!is_motor(frame.id), "status is not a motor command");

  windlass::CanFrame motor;
  motor.id = windlass::can_id(windlass::kPgnMotorCommand, 20, 255, 6);
  motor.data[0] = 2;
  windlass::CanFrame ask_operating = motor;
  ask_operating.id = windlass::can_id(windlass::kPgnIsoRequest, 9, 128, 6);
  ask_operating.dlc = 3;
  ask_operating.data[0] = static_cast<uint8_t>(windlass::kPgnOperating);
  ask_operating.data[1] = static_cast<uint8_t>(windlass::kPgnOperating >> 8);
  ask_operating.data[2] = static_cast<uint8_t>(windlass::kPgnOperating >> 16);
  auto only_operating = node.on_frame(280, ask_operating);
  expect(only_operating.size() == 1 && only_operating[0].id == status[0].id, "an operating-status request returns that PGN");
  expect(node.on_frame(300, motor).empty(), "a received motor command produces no frame");
  expect(node.ignored_motor_commands() == 1, "the motor command is counted and dropped");
  report.running_up = false;
  node.set_report(report);
  auto stopped = node.tick(1250);
  expect(!stopped.empty() && stopped[0].data[2] == 0xc0, "the motor command did not select UP");

  windlass::NmeaNode negative(windlass::NameFields{}, 128);
  negative.set_publish(true);
  windlass::WindlassReport below;
  below.rode_mm = -100;
  negative.set_report(below);
  negative.tick(0);
  auto unavailable = negative.tick(250);
  expect(unavailable.size() == 2 && unavailable[0].data[3] == 0xff && unavailable[0].data[4] == 0xff,
         "a negative rode is unavailable rather than wrapped");

  windlass::CanFrame request;
  request.id = windlass::can_id(windlass::kPgnIsoRequest, 9, 255, 6);
  request.dlc = 3;
  request.data[0] = static_cast<uint8_t>(windlass::kPgnProductInfo);
  request.data[1] = static_cast<uint8_t>(windlass::kPgnProductInfo >> 8);
  request.data[2] = static_cast<uint8_t>(windlass::kPgnProductInfo >> 16);
  windlass::NmeaNode claiming(windlass::NameFields{}, 128);
  claiming.set_publish(true);
  claiming.tick(0);
  expect(claiming.on_frame(10, request).empty(), "product information waits until the address is claimed");
  auto info = node.on_frame(1300, request);
  expect(info.size() == 19, "132-byte product information is 19 fast-packet frames");
  expect(info[0].data[1] == 132 && info[0].data[2] == 0x34 && info[0].data[3] == 0x08, "version is 2.100");
  expect((info[1].data[0] & 0x1f) == 1, "the second frame is the continuation");
  for (const auto& frame : info) expect(!is_motor(frame.id), "product information is not a motor command");

  auto before_heartbeat = node.tick(250 + windlass::kNmeaHeartbeatMs - 1);
  bool early = false;
  for (const auto& frame : before_heartbeat) {
    if (frame.id == windlass::can_id(windlass::kPgnHeartbeat, node.source(), 255, 7)) early = true;
  }
  expect(!early, "the NMEA heartbeat waits 60 s");
  auto heartbeat_frames = node.tick(250 + windlass::kNmeaHeartbeatMs);
  const uint8_t expected_heartbeat[8] = {0x60, 0xea, 0x00, 0xcc, 0xff, 0xff, 0xff, 0xff};
  bool heartbeat_ok = false;
  for (const auto& frame : heartbeat_frames) {
    if (frame.id == 0x1df01180u && std::memcmp(frame.data, expected_heartbeat, 8) == 0) heartbeat_ok = true;
    expect(!is_motor(frame.id), "the NMEA heartbeat is not a motor command");
  }
  expect(heartbeat_ok, "NMEA heartbeat encoding");

  windlass::NameFields winner;
  winner.unique_number = 1;
  windlass::NmeaNode defender(winner, 128);
  defender.set_publish(true);
  defender.tick(0);
  windlass::NameFields loser = winner;
  loser.unique_number = 2;
  windlass::CanFrame contest;
  contest.id = windlass::can_id(windlass::kPgnAddressClaim, 128, 255, 6);
  windlass::pack_name(loser, contest.data);
  expect(defender.on_frame(10, contest).size() == 1, "a higher NAME is answered with our claim");
  expect(defender.source() == 128 && !defender.claimed(), "a successful defence keeps the address");
  expect(defender.tick(250).empty(), "a defence restarts the 250 ms quiet time");
  expect(defender.tick(260).size() == 2 && defender.claimed(), "status follows the restarted quiet time");

  windlass::NameFields weaker;
  weaker.unique_number = 5;
  windlass::NmeaNode yielded(weaker, 128);
  yielded.set_publish(true);
  yielded.tick(0);
  windlass::CanFrame stronger = contest;
  windlass::pack_name(winner, stronger.data);
  auto moved = yielded.on_frame(0, stronger);
  expect(yielded.source() == 129 && !yielded.claimed() && moved.size() == 1, "a lower NAME takes the next address");

  windlass::NmeaNode last(weaker, 251);
  last.set_publish(true);
  last.tick(0);
  windlass::CanFrame at_last = stronger;
  at_last.id = windlass::can_id(windlass::kPgnAddressClaim, 251, 255, 6);
  expect(!last.on_frame(0, at_last).empty(), "the last address answers the contest");
  expect(last.source() == windlass::kNullAddress && !last.claimed(), "losing the last address goes to the null address");
  expect(last.tick(1000).empty(), "the null address publishes no windlass status");

  node.set_publish(false);
  expect(node.tick(70000).empty() && !node.claimed(), "opening the strap stops transmission");

  expect(windlass::Gpio::heartbeat == 1, "GPIO1 heartbeat");
  expect(windlass::kHeartbeatPeriodMs == 80, "heartbeat edge period");
  expect(windlass::kHeartbeatPeriodMs <= 100, "edge period inside the contract");
  expect(windlass::kHeartbeatPeriodMs * 2 < windlass::kMonostableShortMs, "two edges fit the short pulse");
  expect(windlass::kMonostableTypicalMs == 330 && windlass::kMonostableShortMs == 264 &&
             windlass::kMonostableLongMs == 475,
         "monostable bounds");
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

bool bytes_eq(const uint8_t* got, const char* hex) {
  for (int i = 0; hex[i] != '\0'; i += 2) {
    const int hi = hex[i] >= 'a' ? hex[i] - 'a' + 10 : hex[i] - '0';
    const int lo = hex[i + 1] >= 'a' ? hex[i + 1] - 'a' + 10 : hex[i + 1] - '0';
    if (got[i / 2] != static_cast<uint8_t>((hi << 4) | lo)) return false;
  }
  return true;
}

void test_authenticated_udp() {
  uint8_t digest[32];
  const uint8_t abc[] = {'a', 'b', 'c'};
  windlass::sha256(abc, 3, digest);
  expect(bytes_eq(digest, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"), "sha256 abc");
  windlass::sha256(nullptr, 0, digest);
  expect(bytes_eq(digest, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"), "sha256 empty");
  uint8_t hmac_key[20];
  std::memset(hmac_key, 0x0b, sizeof(hmac_key));
  const uint8_t hi_there[] = {'H', 'i', ' ', 'T', 'h', 'e', 'r', 'e'};
  windlass::hmac_sha256(hmac_key, sizeof(hmac_key), hi_there, sizeof(hi_there), digest);
  expect(bytes_eq(digest, "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"), "hmac rfc4231 case 1");

  const char* key = "0123456789abcdef0123456789abcdef";
  const auto key_len = std::strlen(key);
  windlass::MemoryStore store;
  windlass::Controller controller(store);
  controller.set_identity(0x11223344u, 0x55667788u);
  auto sense = rail_on();
  controller.begin(0, sense);
  const std::string session = controller.session();
  expect(session.size() == 32 && session[12] == '4' && session[16] == '8' &&
             session.substr(24) == "00000001",
         "boot session is a 16-byte id");
  const char* invented = "WLC1CMD sess 7 UP 300";
  expect(!windlass::open_command(reinterpret_cast<const uint8_t*>(invented), std::strlen(invented),
                                 reinterpret_cast<const uint8_t*>(key), key_len)
              .authentic,
         "the old text line is not WLC2");

  auto packet = windlass::seal_command(session, 1, windlass::kOpUp, 300, reinterpret_cast<const uint8_t*>(key), key_len);
  expect(packet.size() == windlass::kCommandBytes, "command datagram size");
  const char* published =
      "574c43320101112233445566478880000000000000010000000101012c977945be88d1a5a1b6888ac900bdf8de2aa7f71c9563e4c6f0c5e5d45eac785e";
  bool vector_ok = true;
  for (int i = 0; published[i] != '\0'; i += 2) {
    const int hi = published[i] >= 'a' ? published[i] - 'a' + 10 : published[i] - '0';
    const int lo = published[i + 1] >= 'a' ? published[i + 1] - 'a' + 10 : published[i + 1] - '0';
    if (packet[static_cast<std::size_t>(i / 2)] != static_cast<uint8_t>((hi << 4) | lo)) vector_ok = false;
  }
  expect(vector_ok, "published WLC2 command vector");
  auto opened = windlass::open_command(packet.data(), packet.size(), reinterpret_cast<const uint8_t*>(key), key_len);
  expect(opened.authentic && opened.command.kind == windlass::CmdKind::Up && opened.command.sequence == 1,
         "a signed UP opens");
  expect(controller.command(0, opened.command) && controller.drive().up_req && controller.drive().heartbeat,
         "a signed UP starts the hold and the heartbeat");
  packet[40] ^= 0x01;
  expect(!windlass::open_command(packet.data(), packet.size(), reinterpret_cast<const uint8_t*>(key), key_len).authentic,
         "a bad tag is not a command");
  expect(controller.drive().up_req, "a bad tag leaves the hold untouched");

  auto replay = windlass::seal_command(session, 1, windlass::kOpUp, 300, reinterpret_cast<const uint8_t*>(key), key_len);
  auto replayed = windlass::open_command(replay.data(), replay.size(), reinterpret_cast<const uint8_t*>(key), key_len);
  expect(replayed.authentic && !controller.command(20, replayed.command), "a repeated sequence does not refresh");

  auto stop = windlass::seal_command(session, 2, windlass::kOpStop, 300, reinterpret_cast<const uint8_t*>(key), key_len);
  auto stopped = windlass::open_command(stop.data(), stop.size(), reinterpret_cast<const uint8_t*>(key), key_len);
  expect(controller.command(30, stopped.command), "signed STOP is accepted");
  expect(!controller.drive().up_req && !controller.drive().down_req && !controller.drive().heartbeat &&
             !controller.drive().heartbeat_rising,
         "STOP clears the requests and the heartbeat");
  const std::string retired = controller.session();
  expect(retired != session && retired.substr(24) == "00000002", "STOP advances the session generation");
  auto ack = windlass::seal_ack(retired, 2, true, reinterpret_cast<const uint8_t*>(key), key_len);
  expect(ack.size() == windlass::kAckBytes && ack[26] == 1, "the ack carries the session after STOP");
  auto stale = windlass::seal_command(session, 3, windlass::kOpUp, 300, reinterpret_cast<const uint8_t*>(key), key_len);
  auto stale_open = windlass::open_command(stale.data(), stale.size(), reinterpret_cast<const uint8_t*>(key), key_len);
  expect(stale_open.authentic && !controller.command(40, stale_open.command) && !controller.drive().up_req,
         "a retired session cannot start the windlass");

  auto release = windlass::seal_command(retired, 1, windlass::kOpStop, 300, reinterpret_cast<const uint8_t*>(key), key_len);
  auto released = windlass::open_command(release.data(), release.size(), reinterpret_cast<const uint8_t*>(key), key_len);
  expect(controller.command(50, released.command) && !controller.start_locked() && !controller.drive().up_req,
         "STOP on the new session unlocks without moving");
  auto again = windlass::seal_command(retired, 2, windlass::kOpDown, 300, reinterpret_cast<const uint8_t*>(key), key_len);
  auto down = windlass::open_command(again.data(), again.size(), reinterpret_cast<const uint8_t*>(key), key_len);
  expect(controller.command(60, down.command) && controller.drive().down_req && !controller.drive().up_req,
         "a new press after the release runs DOWN");

  auto tel = windlass::seal_telemetry(controller, reinterpret_cast<const uint8_t*>(key), key_len);
  auto view = windlass::open_telemetry(tel.data(), tel.size(), reinterpret_cast<const uint8_t*>(key), key_len);
  expect(view.authentic && view.session_hex == controller.session() && (view.flags & windlass::kFlagRunning) != 0 &&
             (view.flags & windlass::kFlagDown) != 0,
         "signed telemetry reports the hold");
  tel[40] ^= 0x01;
  expect(!windlass::open_telemetry(tel.data(), tel.size(), reinterpret_cast<const uint8_t*>(key), key_len).authentic,
         "telemetry with a bad tag is ignored");
}

int main() {
  test_boot_outputs_off();
  test_stop_priority_and_stale_run();
  test_watchdog();
  test_conflict_and_heartbeat_window();
  test_rail_loss_and_chain();
  test_link_loss();
  test_remote_gap_web_nmea_and_pins();
  test_authenticated_udp();
  if (failures != 0) {
    std::cerr << failures << " failed\n";
    return 1;
  }
  std::cout << "all tests passed\n";
  return 0;
}
