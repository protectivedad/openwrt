#!/bin/sh

RELAY=/sys/class/gpio/power_relay/value

if [ -n "$1" ]; then
	echo $1 >${RELAY}
else
	echo $(($(cat ${RELAY}) ^ 1)) >${RELAY}
fi

exit 0

