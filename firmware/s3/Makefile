CXX ?= g++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -Werror -Iinclude
SRC := src/controller.cpp src/sha256.cpp src/datagram.cpp src/nmea.cpp src/web.cpp
OUT := build/s3_test

.PHONY: test clean platform-guard

test: platform-guard $(OUT)
	./$(OUT)

$(OUT): $(SRC) test/test_main.cpp include/windlass/*.hpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) $(SRC) test/test_main.cpp -o $(OUT)

platform-guard:
	grep -q "drivePinsLow();" platform/esp32s3_main.cpp
	grep -q "digitalWrite(windlass::Gpio::heartbeat, LOW)" platform/esp32s3_main.cpp
	grep -q "digitalWrite(windlass::Gpio::up_req, drive.up_req" platform/esp32s3_main.cpp
	! grep -E -q "hw_timer|timerAlarm|attachInterrupt" platform/esp32s3_main.cpp
	! grep -E -q "parse_command|WLC1CMD" platform/esp32s3_main.cpp
	python3 -c "import pathlib; t=pathlib.Path('platform/esp32s3_main.cpp').read_text(); a=t.find('open_command('); b=t.find('controller.command('); assert a!=-1 and b!=-1 and a<b"
	# The first executable call in setup() is the pin clear.
	awk '/void setup\(\)/,/WiFi.mode/' platform/esp32s3_main.cpp | grep -q "drivePinsLow();"

clean:
	rm -rf build
