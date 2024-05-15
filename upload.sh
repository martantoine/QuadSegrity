#!/bin/sh
cd Embedded/
arduino-cli compile --fqbn arduino:avr:mega
arduino-cli upload --fqbn arduino:avr:mega -p /dev/ttyACM0