#!/usr/bin/python3

import sys
import telnetlib
import paho.mqtt.subscribe as subscribe
import time
import os
import getpass
import subprocess
from datetime import datetime
from cryptography.fernet import Fernet
import helper

YELLOW = helper.YELLOW
GREEN = helper.GREEN
RED = helper.RED
NC = helper.NC

# callback for MQTT subscriber
def on_message_print(client, userdata, message):
    decryptedMessage = helper.fernetObject.decrypt(message.payload)
    decryptedMessage = str(decryptedMessage)[2:-1]
    
    #extract user and command fields
    user = decryptedMessage[:decryptedMessage.find('/: ')]
    command = decryptedMessage[decryptedMessage.find('/: ')+3:]

    # prevent abuse
    if(command == "shutdown" or command == "quit" or command == "logout"):
        pass

    # display everyone's timestamps
    elif(command == "sync"):
        # force a pause
        # sendCommand("play")
        # sendCommand("pause")
        sendCommand("get_time")

        # assuming a timeout of 3 seconds
        x = -1
        start = time.time()
        while (x == -1 and time.time()-start < 3):
            recBuff = tnh.read_eager().decode().split("\r\n")
            for element in recBuff:
                try:
                    x = int(element)
                    break
                except:
                    pass
        try:
            if(x == -1):
                helper.publishMQTTMsg("Couldn't fetch timestamp!")
            else:
                helper.publishMQTTMsg("is at " + str(helper.secsToHours(x)) + " ("+str(x)+")")
        except Exception as error:
            print(RED+"Failed to respond to sync request:"+NC)
            print(error)

    # throw on console and send as command
    else:
        # Don't worry about coflicting timezones, print local time with messages
        # This will be later compared with the sender's timestamp to check network latency
        tt = datetime.today().timetuple()
        timeX = ""
        timeX = str(tt.tm_hour) if (len(str(tt.tm_hour)) > 1) else "0"+str(tt.tm_hour)
        timeX += ":"
        timeX += str(tt.tm_min) if (len(str(tt.tm_min)) > 1) else "0"+str(tt.tm_min)
        timeX += ":"
        timeX += str(tt.tm_sec) if (len(str(tt.tm_sec)) > 1) else "0"+str(tt.tm_sec)
        timeX = "("+timeX+")- "
        print(timeX + decryptedMessage)
        helper.cmdLineSuppressed("notify-send \""+str(user)+"\" \""+str(command)+"\"")
        sendCommand(str(command))

# for sending commands to VLC telnet host
def sendCommand(message):
    global tnh
    tnh.write(message.encode('ascii') + b"\n")
    recBuff = tnh.read_very_eager().decode().split("\r\n")
    # print(recBuff)

def startHostServer():
    try:
        cmd = "vlc --extraintf telnet --telnet-password=" + str(helper.hostPassword) + " --telnet-host="+ str(helper.hostIP) + " --telnet-port=" + str(helper.hostPort)
        # cmdLineSuppressed(cmd)
        process = subprocess.Popen(args = cmd, stderr=subprocess.DEVNULL, universal_newlines = True, shell = True)
        #print(process[0])
    except:
        print(RED+"Fatal error! Please check host telnet configuration."+NC)
        # Exit the program. There's no point continuing. Recursion can reach maximum recursion depths and/or create core dumps.
        sys.exit()

def connectToHost():
    global tnh
    try:
        print("Attempting Host Telnet Connection...")
        tnh = telnetlib.Telnet(helper.hostIP, int(helper.hostPort))
        # give some time before trying to read
        time.sleep(0.5)
        try:
            tnh.read_until(b"Password: ")
            tnh.write(helper.hostPassword.encode('ascii') + b"\n")
            tnh.read_until(b"> ")
            print(GREEN+"Connected To Host"+NC)
        except:
            print("Wrong Password!")
            helper.hostPassword = getpass.getpass()
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

helper.prepConfig()

# detect and kill all VLC instances to assume control of the telnet interface
# otherwise the playback keeps running under GUI control (mostly qvlc)
def killAllVLC():
    if(helper.cmdLine("pidof vlc").stdout == ''):
        return
    x = input(YELLOW+"Live VLC instances detected. Terminate now to proceed?<y/n>"+NC)
    if(x == 'y' or x == 'Y'):
        wasKilled = helper.cmdLine("kill -9 $(pidof vlc)")
        if(wasKilled == "Killed"):
            # sanity check
            killAllVLC()
        else:
            return
    else:
        # create a lock until the user tries to kill all instances of VLC
        x = input(YELLOW+"Please make sure no instances of VLC are running. Press any key to continue"+NC)
    # sanity check
    killAllVLC()     

helper.getChatKey()
killAllVLC()
startHostServer()
time.sleep(1)
connectToHost()

if(helper.serverChoice == 1):
    try:
        subscribe.callback(on_message_print, helper.mqttTopic, hostname=helper.mqttBrokerIP, port=int(helper.mqttPort))
    except KeyboardInterrupt:
        tnh.read_all()  # might be helpful later
        tnh.close()
        killAllVLC()
        print("\nExiting")
        sys.exit()
    except:
        print("Network Error!")
        sys.exit()
else:
    authen = {'username':helper.mqttUsername, 'password':helper.mqttPassword}
    try:
        subscribe.callback(on_message_print, helper.mqttTopic, hostname=helper.mqttBrokerIP, auth=authen, port=int(helper.mqttPort))
    except KeyboardInterrupt:
        tnh.read_all()  # might be helpful later
        tnh.close()
        killAllVLC()
        print("\nExiting")
        sys.exit()
    except:
        print("Network Error!")
        sys.exit()