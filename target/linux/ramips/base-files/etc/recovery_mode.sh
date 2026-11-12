#!/bin/sh

GPIO_BASE=/sys/class/gpio
STATUS=$GPIO_BASE/gpio14
POWER=$GPIO_BASE/gpio18

[ ! -d $STATUS ] && echo 14 >$GPIO_BASE/export
[ ! -d $POWER ] && echo 18 >$GPIO_BASE/export

echo out >$STATUS/direction
echo 0 >$STATUS/value
echo out >$POWER/direction
echo 1 >$POWER/value

while true; do
	sleep 1
	echo $((1-$(cat $STATUS/value))) >$STATUS/value
	echo $((1-$(cat $POWER/value))) >$POWER/value
done

exit 0
