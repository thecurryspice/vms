# vlcMQTTSync

A Python utility to keep multiple devices playing the same video file in sync, using MQTT.

(Originally made for easing out movie-watching for nerdy long-distance-relationships)

The module can be run on a device connected locally to the device hosting the VLC session.  
For example, it is possible to have a Raspberry Pi (with internet access), connected locally to a system (with or without internet access) running a VLC session, control the system's playback.


## Configuration and Requirements

On your host machine, go to  
VLC > Tools > Preferences > All Settings > Interface > Main Interfaces > Lua  
and edit these options for Lua Telnet:

```
Host 		: <Find the local IP of the host and insert here>
Port 		: <port>
Password 	: <password>
```

The utility runs on Python 3. All packages and libraries have been used keeping in mind backward compatibilty, and the script can be easily translated to Python 2.7

The packages `getpass`, `paho-mqtt` must be installed to run the script.

Use `pip3 install <package-name>` to install the above packages.  


## Usage

1. Make sure all instances of VLC are closed.
2. Run the script.
3. Wait for all connections to establish.
4. Open same files on different systems connected to the internet.
5. Use the `master.py` script to keep all viewers in sync.


## Examples

### Public Server

For a quick test, a config file for Mosquitto's public server is already provided with the configuration:

```
MQTT Broker IP/Server: test.mosquitto.org
MQTT Port: 1883
MQTT Topic: vlcMQTTSyncPublic
VLC Host IP: localhost
Host Port: 4212
Host Password: test
```


The configurations can be done manually as well.

Run `python3 vlcMQTTSync.py`, choose option 1, and follow-up with:

```
MQTT Broker IP/Server: test.mosquitto.org
MQTT Port: 1883
MQTT Topic: randomTopic
VLC Host IP: localhost
Host Port: 4212
Host Password: ****
```

A list of publicly available MQTT servers can be found [here](https://github.com/mqtt/mqtt.github.io/wiki/public_brokers).

Some public servers allow traffic only on certain ports. The server `test.mosquitto.org` for example, listens on the following ports:
* 1883 : MQTT, unencrypted
* 8883 : MQTT, encrypted
* 8884 : MQTT, encrypted, client certificate required
* 8080 : MQTT over WebSockets, unencrypted
* 8081 : MQTT over WebSockets, encrypted


### Private Servers

Run `python3 vlcMQTTSync.py`, choose option 2, and follow-up with:

```
MQTT Broker IP/Server: <server-ip>
MQTT Port: 1883
MQTT Topic: customTopic
MQTT Username: <username>
MQTT Password: *******
VLC Host IP: localhost
Host Port: 1437
Host Password: *******
```

### Using a separate interface

The only change that needs to be made when vlcMQTTSync and VLC sessions are running on different devices is giving the correct VLC Host IP and port and making sure the VLC host is configured to listen to it.

```
MQTT Broker IP/Server: test.mosquitto.org
MQTT Port: 1883
MQTT Topic: randomTopic
VLC Host IP: 192.168.1.5
Host Port: 4212
Host Password: *******
```

## The Master

`master.py` can send various commands (most of the ones provided in the VideoLAN interface) to control behaviour on all screens.  
Send `h` for a list of available commands, or `x` to exit.

Due to the VLC Interface responding only to specific commands, the `master.py` interface doubles up as a group chat, where each message is sent to all live users!  
The messages can be sent from the `master` shell and can be received on the `vlcMQTTSync` shell.


## Saved configurations

All configurations are saved in the `config` folder and are accessible by `vlcMQTTSync.py` as well as `master.py`
