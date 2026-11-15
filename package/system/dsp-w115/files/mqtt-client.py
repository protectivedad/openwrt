#!/usr/bin/micropython

import sys
sys.path.insert(0, '/usr/lib/micropython/unix')

import ssl
import time
import signal
import os
import pyb

from umqtt.simple import MQTTClient

PID = "/run/mqtt-client.pid"
STATUS = "/tmp/uhttpd.status"

section = sys.argv[1]

def read_config():
	path = f"/etc/config/mqtt-client"
	result = {}
	current = None
	anon_count = {}

	with open(path) as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			if line.startswith("config "):
				parts = line.split()
				stype = parts[1]
				if len(parts) >= 3:
					sname = parts[2].strip("'\"")
					current = f"{stype}/{sname}"
				else:
					n = anon_count.get(stype, 0)
					anon_count[stype] = n + 1
					current = f"{stype}[{n}]"
				result[current] = {}
			elif line.startswith("option ") and current:
				parts = line.split(None, 2)
				if len(parts) == 3:
					result[current][parts[1]] = parts[2].strip("'\"")

	return result["mqtt-client/" + section]

def publish_relay():
	with open("/sys/class/gpio/power_relay/value", "r+b") as f:
		if f.read(1) == b"1":
			c.publish(POWER_STAT, "ON")
		else:
			c.publish(POWER_STAT, "OFF")

def publish_led_enable():
        try:
                with open("/tmp/led-enable", "r+b") as f:
                        if f.read(1) == b"1":
                                c.publish(LEDEN_STAT, "CLOSED")
                        else:
                                c.publish(LEDEN_STAT, "OPEN")
        except:
                c.publish(LEDEN_STAT, "OPEN")

def indicate_https():
	e = os.system("service uhttpd status >" + STATUS)
	with open(STATUS, "r") as f:
		r = f.read().strip()
	os.remove(STATUS)

	if r == "running":
		https_signal.on()
	else:
		https_signal.off()

def publish_https():
	e = os.system("service uhttpd status >" + STATUS)
	with open(STATUS, "r") as f:
		r = f.read().strip()
	os.remove(STATUS)

	if r == "running":
		c.publish(HTTPS_STAT, "ON")
		https_signal.on()
	elif r == "inactive":
		c.publish(HTTPS_STAT, "OFF")
		https_signal.off()
	else:
		c.publish(HTTPS_STAT, "UNKNOWN")
		https_signal.off()

def control_https(value):
	if value == "on":
		e = os.system("service uhttpd start")
		c.publish(HTTPS_STAT, "ON")
		https_signal.on()
	elif value == "off":
		e = os.system("service uhttpd stop")
		c.publish(HTTPS_STAT, "OFF")
		https_signal.off()
	else:
		print("Unknown command for https")
		print((topic, msg))

	publish_https()

def sub_cb(topic, msg):
	if topic.decode() == POWER_CMND:
		if msg.decode().lower() == "on":
			e = os.system("relay_control.sh 1")
		elif msg.decode().lower() == "off":
			e = os.system("relay_control.sh 0")
		elif msg.decode().lower() == "toggle":
			e = os.system("relay_control.sh")
		else:
			print("Unknown msg for topic")
			print((topic, msg))

	elif topic.decode() == LEDEN_CMND:
		if msg.decode().lower() == "open":
			e = os.system("brightness_control.sh 1")
		elif msg.decode().lower() == "closed":
			e = os.system("brightness_control.sh 0")
		elif msg.decode().lower() == "toggle":
			e = os.system("brightness_control.sh")
		else:
			print("Unknown msg for topic")
			print((topic, msg))

	elif topic.decode() == HTTPS_CMND:
		control_https(msg.decode().lower())

	else:
		print("Unknown topic")
		print((topic, msg))


def publish(signum):
	publish_https()
	publish_relay()
	publish_led_enable()

def connect():
	mqtts_signal.on()
	while 1:
		try:
			if not c.connect(False):
				c.subscribe(POWER_CMND)
				c.subscribe(HTTPS_CMND)

			c.publish(LWT_TOPIC, "ON", retain=True, qos=1)
			break
		except Exception:
			time.sleep(1)
	mqtts_signal.off()


def disconnect(signum):
	mqtts_signal.on()
	control_https("on")
	c.disconnect()
	os.remove(PID)
	sys.exit(0)


try:
	with open(PID, 'r') as f:
		oldpid = int(f.read())
	print("Killing old mqtt-client.py")
except:
	print("No old mqtt-client.py")
else:
	try:
		r = os.kill(oldpid, signal.SIGTERM)
	except:
		os.remove(PID)

with open(PID, 'w', encoding='utf-8') as f:
	f.write(str(os.getpid()))

https_signal = pyb.LED("green:status")
indicate_https()
mqtts_signal = pyb.LED("red:status")
mqtts_signal.on()

# SIGUSR1 - publish
signal.signal(16, publish)

secrets = read_config()

LWT_TOPIC = "tele/"+secrets["client"]+"/LWT"
POWER_CMND = "cmnd/"+secrets["client"]+"/POWER"
POWER_STAT = "stat/"+secrets["client"]+"/POWER"
LEDEN_CMND = "cmnd/"+secrets["client"]+"/LEDENABLE"
LEDEN_STAT = "stat/"+secrets["client"]+"/LEDENABLE"
HTTPS_CMND = "cmnd/"+secrets["client"]+"/HTTPS"
HTTPS_STAT = "stat/"+secrets["client"]+"/HTTPS"

with open(secrets["ca"], 'rb') as f:
	ca_data = f.read()

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.load_verify_locations(cadata=ca_data)
ctx.check_hostname = True

c = MQTTClient(
	client_id=secrets["client"].encode(),
	server=secrets["host"],
	port=6883,
	user=secrets["client"].encode(),
	password=secrets["password"].encode(),
	keepalive=60,
	ssl=ctx)

signal.signal(signal.SIGTERM, disconnect)

c.set_callback(sub_cb)
c.set_last_will(LWT_TOPIC, "OFF", retain=False, qos=2)

connect()
publish_relay()
publish_led_enable()
control_https("off")

while 1:
	try:
		c.check_msg()
	except KeyboardInterrupt:
		break;
	except Exception:
		connect()
		c.check_msg()
	try:
		time.sleep(0.5)
	except KeyboardInterrupt:
		break

disconnect(signal.SIGTERM)
