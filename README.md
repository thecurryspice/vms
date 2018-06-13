# vlcMQTTSync

A Python utility to keep multiple devices playing the same video file in sync, using MQTT.

(Originally made for easing out movie-watching for nerdy long-distance-relationships)


## Requirements

The utility runs on Python 3. All packages and libraries have been used keeping in mind backward compatibilty, and the script can be easily translated to ~Python 2.7

The following packages must be installed to run the script: `telnetlib`, `getpass`, `paho-mqtt`

Use `pip3 install <package-name>` to install the above packages.  
No sudo permissions are required


## Usage

1. Make sure all instances of VLC are closed.
2. Run the script.
3. Wait for all connections to establish.
4. Open same files on different systems connected to the internet.
5. Use the `master.py` script to keep all viewers in sync.