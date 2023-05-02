#!/usr/bin/python3
from vardata import *
import paho.mqtt.client as paho
import http.client, urllib
import argparse
import logging
import json
import sys
import ssl
import time
from chump import Application
from dateutil.parser import parse
from datetime import datetime, timedelta
import tzlocal

dash = '\n-------------------------------------------\n'
gcode_state_prev = ''
first_run = True
percent_notify = False
po_app = Application(my_pushover_app)
po_user = po_app.get_user(my_pushover_user)

def parse_message(self, message):
	dataDict = json.loads(message)
	return dataDict

def on_connect(client, userdata, flags, rc):
	client.subscribe("device/"+device_id+"/report",0)

def on_message(client, userdata, msg):
	global dash, gcode_state_prev, app, user, my_pushover_app, my_pushover_user, first_run, percent_notify
	#logging.info("received message with topic"+msg.topic)
	msgData = msg.payload.decode('utf-8')
	dataDict = json.loads(msgData)
	if('print' in dataDict):
		if('gcode_state' in dataDict['print']):
			gcode_state = dataDict['print']['gcode_state']
			percent_done = dataDict['print']['mc_percent']
			if(gcode_state_prev != gcode_state or (gcode_state_prev != gcode_state and not percent_notify and percent_done >= notify_at_percent)):
				if(notify_at_percent >= percent_done):
					percent_notify = True

				# init
				priority = 0
				logging.info("gcode_state has chnaged to "+gcode_state)
				json_formatted_str = json.dumps(dataDict, indent=2)
				logging.info(dash+json_formatted_str+dash)
				gcode_state_prev = gcode_state

				# Get start time
				unix_timestamp = float(dataDict['print']['gcode_start_time'])
				if(gcode_state == "PREPARE" and unix_timestamp == 0):
						unix_timestamp = float(time.time())
				if(unix_timestamp != 0):
					local_timezone = tzlocal.get_localzone() # get pytz timezone
					local_time = datetime.fromtimestamp(unix_timestamp, local_timezone)
					my_datetime = local_time.strftime("%Y-%m-%d %I:%M %p (%Z)")
				else:
					my_datetime = ""

				# Get finish time (aprox)
				my_finish_datetime = ""
				remaining_time = ""
				time_left_seconds = int(dataDict['print']['mc_remaining_time']) * 60
				if(time_left_seconds != 0):
					aprox_finish_time = time.time() + time_left_seconds
					unix_timestamp = float(aprox_finish_time)
					local_timezone = tzlocal.get_localzone() # get pytz timezone
					local_time = datetime.fromtimestamp(unix_timestamp, local_timezone)
					my_finish_datetime = local_time.strftime("%Y-%m-%d %I:%M %p (%Z)")
					remaining_time = str(timedelta(minutes=dataDict['print']['mc_remaining_time']))
				else:
					if(gcode_state == "FINISH" and time_left_seconds == 0):
						my_finish_datetime = "Done!"

				# text
				msg_text = "<ul>"
				msg_text = msg_text + "<li>State: "+ gcode_state + "</li>"
				msg_text = msg_text + f"<li>Percent: {percent_done}</li>"
				msg_text = msg_text + "<li>Name: "+ dataDict['print']['subtask_name'] + "</li>"
				msg_text = msg_text + f"<li>Remaining time: {remaining_time}</li>"
				msg_text = msg_text + "<li>Started: "+ my_datetime + "</li>"
				msg_text = msg_text + "<li>Aprox End: "+ my_finish_datetime + "</li>"

				# failed
				fail_reason = ""
				if(len(dataDict['print']['fail_reason']) > 1 or dataDict['print']['print_error'] != 0 or gcode_state == "FAILED" ):
					msg_text = msg_text + f"<li>print_error: {dataDict['print']['print_error']}</li>"
					msg_text = msg_text + f"<li>mc_print_error_code: {dataDict['print']['mc_print_error_code']}</li>"
					error_code = int(dataDict['print']['mc_print_error_code'])
					if(error_code == 32778):
						fail_reason = "Arrr! Swab the poop deck!"
					elif(error_code == 32771):
						fail_reason = "Spaghetti and meatballs!"
					elif(error_code == 32774):
						fail_reason = "Build plate mismatch!"
					else:
						fail_reason = dataDict['print']['fail_reason']
					msg_text = msg_text + "<li>fail_reason: "+ fail_reason + "</li>"
					priority = 1

				# pushover notify
				if(not first_run):
					msg_text = msg_text + "</ul>"
					message = po_user.create_message(
						title="Bambu State Changed!",
						message=msg_text,
						html=True,
						sound='mechanical',
						priority=priority
					)
					message.send()
				else:
					first_run = False


def main(argv):
	global host, port, user, password
	loglevel = logging.INFO
	logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=loglevel)
	logging.info("Starting")

	client = paho.Client()
	client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
	client.tls_insecure_set(True)
	client.username_pw_set(user, password)
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect(host, port, 60)
	client.loop_forever()


if __name__ == "__main__":
	main(sys.argv[1:])
