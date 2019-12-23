#!/usr/bin/python3

import sys
import telnetlib
import paho.mqtt.subscribe as subscribe
import time
import os
import subprocess
import getpass
import shelve
from datetime import datetime
from cryptography.fernet import Fernet
import base64
from helper import *

[serverChoice, mqttBrokerIP, mqttPort, mqttTopic, mqttUsername, mqttPassword, hostIP, hostPort, hostPassword] = ['','','','','','','','','']

# callback for MQTT subscriber
def on_message_print(client, userdata, message):
    global fernetObject
    decryptedMessage = fernetObject.decrypt(message.payload)
    decryptedMessage = str(decryptedMessage)[2:-1]
    
    # will be updated in future
    if(decryptedMessage[2:-1] == "sync"):
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
        sendCommand(str(decryptedMessage[str(decryptedMessage).find('/: ')+3:]))

# for sending commands to VLC telnet host
def sendCommand(message):
    global tnh
    tnh.write(message.encode('ascii') + b"\n")
    recBuff = tnh.read_very_eager().decode().split("\r\n")
    #print(recBuff)

def startHostServer():
    try:
        cmd = "vlc -I telnet --telnet-password=" + str(hostPassword) + " --telnet-host="+ str(hostIP) + " --telnet-port=" + str(hostPort)
        process = subprocess.Popen(args = cmd, stdout = subprocess.PIPE, universal_newlines = True, shell = True)
        #print(process[0])
    except:
        print(RED+"Fatal error! Please check host telnet configuration."+NC)
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
            print(GREEN+"Connected To Host"+NC)
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

def storeConfigFile(name):
    shelfFile = shelve.open(os.path.join('config',name+'.config'))
    if(serverChoice == 1):
        shelfFile['data'] = [serverChoice, mqttBrokerIP, mqttPort, mqttTopic, hostIP, hostPort, hostPassword]
    else:
        shelfFile['data'] = [serverChoice, mqttBrokerIP, mqttPort, mqttTopic, mqttUsername, mqttPassword, hostIP, hostPort, hostPassword]

def promptSaveConfig():
    x = input("Do you want to save the current configuration?(y/n) : ")
    if(x == 'y'):
        name = input("Give a name to the configuration : ")
        storeConfigFile(name)

def getConfigFiles():
    global configFiles
    configFiles = []
    files = os.listdir(os.path.join(os.getcwd(),'config'))
    for file in files:
        if file.endswith('.config'):
            configFiles.append(file)
            print(str(len(configFiles)) + ". " + configFiles[len(configFiles) - 1])

def loadFromConfig():
    global configFiles, serverChoice, mqttBrokerIP, mqttPort, mqttTopic, mqttUsername, mqttPassword, hostIP, hostPort, hostPassword
    if(len(configFiles) > 0):
        x = input("Do you want to load any previous configurations?<y/n> : ")
        if(x == 'y'):
            fileNumber = int(input("Enter corresponding number of file : "))
            if((fileNumber) <= len(configFiles)):
                shelfFile = shelve.open(os.path.join('config', configFiles[fileNumber - 1]))
                if(list(shelfFile['data'])[0] == 1):
                    # public server
                    [serverChoice, mqttBrokerIP, mqttPort, mqttTopic, hostIP, hostPort, hostPassword] = list(shelfFile['data'])
                    return True
                else:
                    # private server
                    [serverChoice, mqttBrokerIP, mqttPort, mqttTopic, mqttUsername, mqttPassword, hostIP, hostPort, hostPassword] = list(shelfFile['data'])
                    return True
            else:
                return False
        else:
            return False

def printConfig():
    print("MQTT Broker IP/Server: "+ mqttBrokerIP)
    print("MQTT Port: "+ mqttPort)
    print("MQTT Topic: "+ mqttTopic)
    print("MQTT Username: "+ mqttUsername)
    print("MQTT Password: "+ mqttPassword)
    print("VLC Host IP: "+ hostIP)
    print("Host Port: "+ hostPort)
    print("Host Password: "+ hostPassword)


# if arguments have been passed, prepare list
args = []
for arg in sys.argv:
    args.append(arg)
n = len(args)

# command was directly executed
if(n == 1):
    getConfigFiles()
    if(not loadFromConfig()):
        print("1. Public Server \nor\n2. Private Server\nPublic Servers don't use a username and password.")
        serverChoice = int(input("Choose (1 or 2): "))
        if(serverChoice == 1):
            mqttBrokerIP = input("MQTT Broker IP/Server: ")
            mqttPort = input("MQTT Port: ")
            mqttTopic = input("MQTT Topic: ")
            hostIP = input("VLC Host IP: ")
            hostPort = input("Host Port: ")
            print("Host ", end='')
            sys.stdout.flush()
            hostPassword = getpass.getpass()
            promptSaveConfig()
        elif(serverChoice == 2):
            mqttBrokerIP = input("MQTT Broker IP/Server: ")
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
            promptSaveConfig()
        else:
            sys.exit()
    else:
        print("Loaded Configuration:")
        printConfig()

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
    promptSaveConfig()

# wrong number of arguments
else:
    print("Wrong number of arguments!")
    print("Usage:\npython3 vlcMQTTSync.py\nor\npython3 vlcMQTTSync.py <mqttBrokerIP> <mqttPort> <mqttTopic> <mqttUsername> <mqttPassword> <hostIP> <hostPassword> <hostPort>")
    print("Exiting...")
    sys.exit()

# detect and kill all VLC instances to assume control of the telnet interface
# otherwise the playback keeps running under GUI control (mostly qvlc)
def killAllVLC():
    if(cmdLine("pidof vlc") == ''):
        return
    x = input(YELLOW+"Live VLC instances detected. Terminate now to proceed?<y/n>"+NC)
    if(x == 'y' or x == 'Y'):
        wasKilled = cmdLine("kill -9 $(pidof vlc)")
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

killAllVLC()
startHostServer()
connectToHost()

chatKey = getpass.getpass("Enter chat key (32 characters maximum):")
# pad chatKey
for i in range(32-len(chatKey)):
    chatKey = chatKey + ''.join('0')
fernetObject = Fernet(base64.b64encode(chatKey.encode('utf-8')))

print("You may now start a VLC session")

if(serverChoice == 1):
    try:
        subscribe.callback(on_message_print, mqttTopic, hostname=mqttBrokerIP, port=int(mqttPort))
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
    authen = {'username':mqttUsername, 'password':mqttPassword}
    try:
        subscribe.callback(on_message_print, mqttTopic, hostname=mqttBrokerIP, auth=authen, port=int(mqttPort))
    except KeyboardInterrupt:
        tnh.read_all()  # might be helpful later
        tnh.close()
        killAllVLC()
        print("\nExiting")
        sys.exit()
    except:
        print("Network Error!")
        sys.exit()