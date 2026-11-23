CXX ?= g++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -Werror -Iinclude
SRC := src/controller.cpp src/nmea.cpp src/web.cpp
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
	! grep -E -q "controller\\.command|parse_command|WLC1CMD|WiFiUDP" platform/esp32s3_main.cpp
	# The first executable call in setup() is the pin clear.
	awk '/void setup\(\)/,/WiFi.mode/' platform/esp32s3_main.cpp | grep -q "drivePinsLow();"

clean:
	rm -rf build
