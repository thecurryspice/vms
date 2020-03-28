import subprocess
import os
import getpass
import shelve
import sys
from cryptography.fernet import Fernet
import base64

BLUE =  '\033[1;38;2;32;64;227m'
RED =   '\033[1;38;2;227;32;32m'
GREEN = '\033[0;38;2;0;192;0m'
YELLOW ='\033[0;38;2;192;192;0m'
NC =    '\033[0m'

[serverChoice, mqttBrokerIP, mqttPort, mqttTopic, mqttUsername, mqttPassword, hostIP, hostPort, hostPassword] = ['','','','','','','','','']

# for executing shell commands
def cmdLine(cmd):
    process = subprocess.run(args = cmd, capture_output=True, universal_newlines = True, shell = True)
    return process

def cmdLineSuppressed(cmd):
    process = subprocess.run(args = cmd, capture_output=False, universal_newlines = True, shell = True)
    return process

def cmdLineWaitUntilExecution(cmd):
    process = subprocess.Popen(args = cmd, universal_newlines = True, shell = True)
    if(wait):
        while(process.poll() == None):
            continue

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

def printConfig():
    print("MQTT Broker IP/Server: "+ mqttBrokerIP)
    print("MQTT Port: "+ mqttPort)
    print("MQTT Topic: "+ mqttTopic)
    if(serverChoice == 2):
        print("MQTT Username: "+ mqttUsername)
    print("VLC Host IP: "+ hostIP)
    print("Host Port: "+ hostPort)

def prepConfig():
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

# encrypts message using the global fernetObject from helper
def encryptMessage(msg):
    if(not fernetObject):
        return msg
    else:
        return fernetObject.encrypt(msg.encode('utf-8'))

# prepare chatKey
def getChatKey():
	global fernetObject
	chatKey = getpass.getpass("Enter chat key (32 characters maximum):")
	# if(chatKey != 'x' or chatKey != 'X'):
	# pad chatKey
	for i in range(32-len(chatKey)):
	    chatKey = chatKey + ''.join('0')
	# will have to check for a URL safe key here. Probably look at what exception is thrown
	# and ask the user to create a key again
	fernetObject = Fernet(base64.b64encode(chatKey.encode('utf-8')))