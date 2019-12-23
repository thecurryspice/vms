#!/usr/bin/python3

import sys
import os
import shelve
import telnetlib
import getpass
from datetime import datetime
import paho.mqtt.publish as publish
from cryptography.fernet import Fernet
import base64
from helper import *

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
    if(serverChoice == 2):
        print("MQTT Username: "+ mqttUsername)

def encryptMessage(msg):
    global fernetObject
    if(not fernetObject):
        return msg
    else:
        return fernetObject.encrypt(msg.encode('utf-8'))

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
        elif(serverChoice == 2):
            mqttBrokerIP = input("MQTT Broker IP: ")
            mqttPort = input("MQTT Port: ")
            mqttTopic = input("MQTT Topic: ")
            mqttUsername = input("MQTT Username: ")
            print("MQTT ", end='')
            sys.stdout.flush()
            mqttPassword = getpass.getpass()
        else:
            sys.exit()
    else:
        print("Loaded Configuration:")
        printConfig()

# command was executed with arguments
elif(n == 6):
    mqttBrokerIP = args[1]
    mqttPort = args[2]
    mqttTopic = args[3]
    mqttUsername = args[4]
    mqttPassword = args[5]

# wrong number of arguments
else:
    print("Wrong number of arguments!")
    print("Usage:\npython3 vlcMQTTSync.py\nor\npython3 vlcMQTTSync.py <brokerIP> <port> <topic> <username> <password>")
    print("Exiting...")
    sys.exit()

# change this to your liking
chatID = getpass.getuser()
# Ask every time for a key.
chatKey = getpass.getpass("Enter chat key (32 characters maximum):")
# if(chatKey != 'x' or chatKey != 'X'):
# pad chatKey
for i in range(32-len(chatKey)):
    chatKey = chatKey + ''.join('0')
# will have to check for a URL safe key here. Probably look at what exception is thrown
# and ask the user to create a key again
fernetObject = Fernet(base64.b64encode(chatKey.encode('utf-8')))
print(YELLOW+"Chats are now encrypted! Anyone with the key can interpret conversations."+NC)


print("\033[0;38;2;0;192;0mReady\033[0m\nEnter 'h' for a list of available functions, or 'x' to exit")
while True:
    x = input("Message: ")
    if(x == 'h'):
        print("| add XYZ  . . . . . . . . . . . . . . . . . . . . add XYZ to playlist")
        print("| enqueue XYZ  . . . . . . . . . . . . . . . . . queue XYZ to playlist")
        print("| delete [X] . . . . . . . . . . . . . . . . delete item X in playlist")
        print("| move [X][Y]  . . . . . . . . . . . . move item X in playlist after Y")
        print("| sort key . . . . . . . . . . . . . . . . . . . . . sort the playlist")
        print("| sd [sd]  . . . . . . . . . . . . . show services discovery or toggle")
        print("| play . . . . . . . . . . . . . . . . . . . . . . . . . . play stream")
        print("| stop . . . . . . . . . . . . . . . . . . . . . . . . . . stop stream")
        print("| next . . . . . . . . . . . . . . . . . . . . . .  next playlist item")
        print("| prev . . . . . . . . . . . . . . . . . . . .  previous playlist item")
        print("| goto, gotoitem . . . . . . . . . . . . . . . . .  goto item at index")
        print("| repeat [on|off]  . . . . . . . . . . . . . .  toggle playlist repeat")
        print("| loop [on|off]  . . . . . . . . . . . . . . . .  toggle playlist loop")
        print("| random [on|off]  . . . . . . . . . . . . . .  toggle playlist random")
        print("| clear  . . . . . . . . . . . . . . . . . . . . .  clear the playlist")
        print("| title [X]  . . . . . . . . . . . . . . set/get title in current item")
        print("| chapter [X]  . . . . . . . . . . . . set/get chapter in current item")
        print("| ")
        print("| seek X . . . . . . . . . . . seek in seconds, for instance `seek 12'")
        print("| pause  . . . . . . . . . . . . . . . . . . . . . . . .  toggle pause")
        print("| fastforward  . . . . . . . . . . . . . . . . . . set to maximum rate")
        print("| rewind . . . . . . . . . . . . . . . . . . . . . set to minimum rate")
        print("| faster . . . . . . . . . . . . . . . . . .  faster playing of stream")
        print("| slower . . . . . . . . . . . . . . . . . .  slower playing of stream")
        print("| normal . . . . . . . . . . . . . . . . . .  normal playing of stream")
        print("| rate [playback rate] . . . . . . . . . .  set playback rate to value")
        print("| frame  . . . . . . . . . . . . . . . . . . . . . play frame by frame")
        print("| fullscreen, f, F [on|off]  . . . . . . . . . . . . toggle fullscreen")
        print("| ")
        print("| volume [X] . . . . . . . . . . . . . . . . . .  set/get audio volume")
        print("| volup [X]  . . . . . . . . . . . . . . .  raise audio volume X steps")
        print("| voldown [X]  . . . . . . . . . . . . . .  lower audio volume X steps")
        print("| achan [X]  . . . . . . . . . . . .  set/get stereo audio output mode")
        print("| atrack [X] . . . . . . . . . . . . . . . . . . . set/get audio track")
        print("| vtrack [X] . . . . . . . . . . . . . . . . . . . set/get video track")
        print("| vratio [X] . . . . . . . . . . . . . . .  set/get video aspect ratio")
        print("| vcrop, crop [X]  . . . . . . . . . . . . . . . .  set/get video crop")
        print("| vzoom, zoom [X]  . . . . . . . . . . . . . . . .  set/get video zoom")
        print("| vdeinterlace [X] . . . . . . . . . . . . . set/get video deinterlace")
        print("| vdeinterlace_mode [X]  . . . . . . .  set/get video deinterlace mode")
        print("| snapshot . . . . . . . . . . . . . . . . . . . . take video snapshot")
        print("| strack [X] . . . . . . . . . . . . . . . . .  set/get subtitle track")
        print("| ")
        print("| vlm  . . . . . . . . . . . . . . . . . . . . . . . . .  load the VLM")
        print("| logout . . . . . . . . . . . . . .  exit (if in a socket connection)")
        print("| quit . . . . . . . .  quit VLC (or logout if in a socket connection)")
        print("| shutdown . . . . . . . . . . . . . . . . . . . . . . .  shutdown VLC")
        print()
    elif(x == 'x'):
        print("Exiting")
        sys.exit()
    else:
        if(serverChoice == 1):
            try:
                # Don't worry about conflicting timezones, print local time with messages
                tt = datetime.today().timetuple()
                # x = "("+str(tt.tm_hour)+":"+str(tt.tm_min) +":"+str(tt.tm_sec)+")- " + chatID + "/: " + x
                x = chatID + "/: " + x
                enc = encryptMessage(x)
                publish.single(mqttTopic, enc, hostname=mqttBrokerIP, port=int(mqttPort))
            except Exception as e:
                print("\033[1;38;2;227;32;32mError while sending message\033[0m")   
                print(str(e)+"\n")

        else:
            authen = {'username':mqttUsername, 'password':mqttPassword}
            try:
                publish.single(mqttTopic, x, hostname=mqttBrokerIP, auth=authen, port=int(mqttPort))
            except Exception as e:
                print("\033[1;38;2;227;32;32mError while sending message\033[0m")   
                print(str(e)+"\n")
