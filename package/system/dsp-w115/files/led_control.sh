#!/bin/sh

FILE=/tmp/led-enable
RELAY=/sys/class/gpio/power_relay/value
LED=/sys/class/leds/green:power/brightness
PIDFILE=/var/run/mqtt-client.pid

echo $(($(cat "${FILE}") & $(cat "${RELAY}"))) > "${LED}"

[ -f "${PIDFILE}" ] && kill -USR1 $(cat "${PIDFILE}")

exit 0

