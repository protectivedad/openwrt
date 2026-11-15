#!/bin/sh

FILE=/tmp/led-enable

# if command given do oppposite so toggle can run
if [ -n "$1" ]; then
	echo $1 >"${FILE}"
else
	echo $(($(cat "${FILE}") ^ 1)) >"${FILE}"
fi

exit 0

