#!/bin/sh
# Build the ESP32-S3 image. Does not flash.
#   ./build_image.sh
#   ./build_image.sh 'softap-password' 'command-key-at-least-16'
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
WIFI_PASS=${1:-CHANGE_ME}
COMMAND_KEY=${2:-CHANGE_ME}
PATH="$HOME/.local/bin:$PATH"
export PATH
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
SK="$STAGE/windlass_s3"
mkdir -p "$SK/windlass"
cp "$ROOT/src/"*.cpp "$SK/"
cp "$ROOT/include/windlass/"*.hpp "$SK/windlass/"
cp "$ROOT/platform/esp32s3_main.cpp" "$SK/windlass_s3.ino"
python3 - "$WIFI_PASS" "$COMMAND_KEY" "$SK/secrets.h" << 'PY'
import sys
from pathlib import Path
wifi, key, dest = sys.argv[1:]
def esc(value):
    return value.replace("\\", "\\\\").replace('"', '\\"')
Path(dest).write_text('#pragma once\n#define WIFI_PASS "%s"\n#define COMMAND_KEY "%s"\n' % (esc(wifi), esc(key)))
PY
OUT="$ROOT/build/arduino"
mkdir -p "$OUT"
FQBN="esp32:esp32:esp32s3:FlashSize=16M,PartitionScheme=app3M_fat9M_16MB,CDCOnBoot=cdc,PSRAM=disabled"
arduino-cli compile -b "$FQBN" --build-path "$OUT" "$SK"
mkdir -p "$ROOT/release"
cp "$OUT/windlass_s3.ino.bin" "$ROOT/release/windlass_s3.bin"
echo "image: $ROOT/release/windlass_s3.bin"
