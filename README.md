# GPIO input output hooks
This repo contains two hooks called event2io and io2key: <br/>
- event2io listens a message from another process through a pipe and triggers a gpio related function given a config file. <br/>
- io2key waits for a gpio pin to be triggered and simulates a keystroke afterwards given a config file. <br/>

## Files description
### io2key files:
- **io2key.py** binds GPIO pins to simulate keystrokes given a config file.
- **input_key.yaml** config file which maps pins to a keystroke.
- **io2key_launcher.sh** runs io2key.py after activating a python env.
### event2io files:
- **event2io.py** listens an event through named pipe and accordingly controls GPIO pins given a config file
- **output_key.yaml** config file which maps pins to different variables that are aimed to trigger different kinds of gpio related functions.
- **event2io_launcher.sh** runs event2io.py after activating a python env.
- **exemple.py** shows how to use named pipe in the main code to communicate with event2io.
### logger:
- **logger.py** logging singleton script that is used in even2io and io2key. The logs is stored in `/var/log/cel-apus/`


## Setup
### Environment
Both _launcher.sh activate a specific python env called cel-apus. If you already have another env, do the dedicated path changes and package installations <br/>
### event2io service systemd
Starts event2io_launcher that runs its associated hook after activating the env. <br/>
To create the service copy the content of `services/event2io.service` to `/etc/systemd/system/event2io.service` and set the correct permission:
```
sudo chmod 644 /etc/systemd/system/event2io.service
```
event2io.service should be owned by root so do the dedicated changes in case with the following:
```
sudo chown root:root /etc/systemd/system/event2io.service
```

### io2key service systemd
Starts io2key_launcher that runs its associated hook after activating the env. <br/>
To create the service copy the content of `services/io2key.service` to `/etc/systemd/system/io2key.service` and set the correct permission:
```
sudo chmod 644 /etc/systemd/system/io2key.service
```
io2key.service should be owned by root so do the dedicated changes in case with the following:
```
sudo chown root:root /etc/systemd/system/io2key.service
```

### Logfile service
tmpfile is a systemd service used to create temporary files on boot. In this case, it is used to create log files for both hooks and set them to the correct file permission when the instance starts. <br/>
Write the following in `/etc/tmpfiles.d/cel-apus.conf`
```
d /var/log/cel-apus 0755 cellari cellari -
```
### Systemd enable
Enable both services:
```
sudo systemctl enable io2key --now
sudo systemctl enable even2io --now
```
## Debugging
### Systemd logs
To check the log of a specific service:
```
journalctl -u <service_name>
```
### Hooks's logfiles
To check the log of a specific hook:
```
watch -n 1 cat /var/log/cel-apus/logs-<hook_name>.log
```

## Notes
### Launcher's permissions
In case of permission error related to the launchers, check if they are owned by the user and have the correct permissions (744)
### X-server issue
io2key works with a library called xdotool that able users to send a kestroke <br/>
Xdotool works with x-server thus exporting DISPLAY=0 is needed in the io2key_launcher.sh <br/>
If there is still an issue related to the x-server display when trying to enable the service try :
```
xhost si:localuser:root
```

## Dependencies:
```
sudo apt-get install -y xdotool
pip install Jetson.GPIO
pip install pyyaml
pip install python-dotenv
```
