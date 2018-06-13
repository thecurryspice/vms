#!/usr/bin/python3

import sys
import telnetlib
import time
import os
import subprocess
import getpass
import paho.mqtt.subscribe as subscribe

# callback for MQTT subscriber
def on_message_print(client, userdata, message):
    message.payload = str(message.payload)[2:-1]
    
    # will be updated in future
    if(message.payload[2:-1] == "sync"):
    	sendCommand("pause")
    	time.sleep(0.5)
    	sendCommand("get_time")
    	x = 0
    	while x == 0:
    		recBuff = tnh.read_very_eager().decode().split("\r\n")
    		for element in recBuff:
    			try:
    				x = int(element)
    				break
    			except:
    				pass
    else:
    	sendCommand(str(message.payload))

# for sending commands to VLC telnet host
def sendCommand(message):
	global tnh
	print("Sending: " + message)
	tnh.write(message.encode('ascii') + b"\n")
	recBuff = tnh.read_very_eager().decode().split("\r\n")
	#print(recBuff)

def startHostServer():
	try:
		cmd = "vlc -I telnet --telnet-password=" + str(hostPassword) + " --telnet-host="+ str(hostIP) + " --telnet-port=" + str(hostPort)
		process = subprocess.Popen(args = cmd, stdout = subprocess.PIPE, universal_newlines = True, shell = True)
		#print(process[0])
	except:
		print("Error occured in starting server! Please make sure no instances of VLC are running")
		# Exit the program. There's no point continuing. Recursion can reach maximum recursion depths and/or create core dumps.
		sys.exit()

def connectToHost():
	global tnh, hostPassword
	try:
		print("Attempting Host Telnet Connection...")
		tnh = telnetlib.Telnet(hostIP, int(hostPort))
		# give some time before trying to read
		time.sleep(0.5)
		try:
			tnh.read_until(b"Password: ")
			tnh.write(hostPassword.encode('ascii') + b"\n")
			tnh.read_until(b"> ")
			print("\033[0;32mConnected To Host\033[0m")
		except:
			print("Wrong Password!")
			hostPassword = getpass.getpass()
			connectToHost()
	except:
		t = 3
		while(t > 0):
			print("Host server is not yet ready! Retrying in " + str(t) + " seconds...")
			time.sleep(1)
			t -= 1
			print("\033[F\033[K", end = '')
		print("\033[F\033[K", end = '')
		connectToHost()

# if arguments have been passed, prepare list
args = []
for arg in sys.argv:
    args.append(arg)
n = len(args)

# command was directly executed
if(n == 1):
	mqttBrokerIP = input("MQTT Broker IP: ")
	mqttPort = input("MQTT Port: ")
	mqttTopic = input("MQTT Topic: ")
	mqttUsername = input("MQTT Username: ")
	print("MQTT ", end='')
	sys.stdout.flush()
	mqttPassword = getpass.getpass()
	hostIP = input("VLC Host IP: ")
	hostPort = input("Host Port: ")
	print("Host ", end='')
	sys.stdout.flush()
	hostPassword = getpass.getpass()

# command was executed with arguments
elif(n == 9):
	mqttBrokerIP = args[1]
	mqttPort = args[2]
	mqttTopic = args[3]
	mqttUsername = args[4]
	mqttPassword = args[5]
	hostIP = args[6]
	hostPort = args[7]
	hostPassword = args[8]

# wrong number of arguments
else:
	print("Wrong number of arguments!")
	print("Usage:\npython3 vlcMQTTSync.py\nor\npython3 vlcMQTTSync.py <mqttBrokerIP> <mqttPort> <mqttTopic> <mqttUsername> <mqttPassword> <hostIP> <hostPassword> <hostPort>")
	print("Exiting...")
	sys.exit()

# create a lock until the user kills all instances of VLC
x = input("Please make sure no instances of VLC are running. Press Enter key to continue")

startHostServer()
connectToHost()

print("You may now start a VLC session")

auther = {'username':mqttUsername, 'password':mqttPassword}
subscribe.callback(on_message_print, mqttTopic, hostname=mqttBrokerIP, auth=auther, port=int(mqttPort))