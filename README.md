# Bambu Labs X1C Python Monitor and Pushover Notifier
This script will monitor the Bambu X1C and send pushover notifications on gcode_state changes.

Why create this script? The iPhone Bambu Handy app notifications are not insistent enough... I keep missing the notifications.

**This is a work in progress**.

## Requirements

- Windows. May work with linux platforms with some tweaks..
- Git
- Python
- mqtt-explorer - Optional
- Basic knowledge of git, windows scheduled tasks, task scheduler, starting an administrative powershell session, etc.
- A pushover account [https://pushover.net](https://pushover.net) is required and a pushover application created [https://pushover.net/apps/build](https://pushover.net/apps/build).

## Setup

Start Powershell as admin (Windows 10). Assuming you're on the C:\ drive, follow the instructions below:

Install Git and Python via Chocolatey (or download and install via other means)

```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

choco install git -y
choco install python -y
```

Python packages to install
```
py -m pip install -U pip
py -m pip install -U paho-mqtt
py -m pip install -U chump
py -m pip install -U python-dateutil
py -m pip install -U datetime
py -m pip install -U tzlocal
```

Optional: Install mqtt-explorer, this can be used to obtain the device ID (serial number) from the printer. You'll need to know your X1C access code, which can be obtained from the X1C screen by navigating to the cog wheel and clicking the network tab.
```
choco install mqtt-explorer --pre
```

After connecting to the printer expand "Device". The Alphanumberic ID listed is your printer ID required for [vardata.py](vardata.py) settings.

<img src="./MQTT_Explorer_Settings.png?raw=true" width="250">

The Device ID (serial number) can also be found in Bambu Studio. Navigate to the Device Tab on top, then Update on left.

<img src="./Bambu_Studio_Device_ID.png?raw=true" width="250">

Clone this repo
```
cd\
git clone https://github.com/ChadDevOps/bambu-lab-pushover-notify.git
```

Update [vardata.py](vardata.py) with your settings.

```
# Pushover info
my_pushover_user = "your_pushover_user_key" # pushover user key
my_pushover_app = "the_application_token" # pushover app key
notify_at_percent = 50 # additional percent you wish to be notified, e.g. 50% would be 50.
pause_error_secs = 10 # seconds
repeat_errors = 2 # number of times

# Bambu login information
host = '127.0.0.7' # bambu x1c ipv4 address
port = 8883 # default port
user = 'bblp' # default user
password = 'alphanumeric_code' # access code from bambu x1c screen under cog wheel / network tab
device_id = '0SOMETHING' # use mqtt-explorer to obtain or Bambu Studio, see details above
```

To start monitoring on Windows startup, open task scheduler and import bambu_monitor.xml. Modify paths in xml if you did not clone to the C: drive. This will launch run.bat on windows startup as SYSTEM.

Click run under the task to launch, or just execute `run.bat`.

## References

* https://vile.thoughtcrime.dk/post/sending-notifications-with-mqtt-and-pushover-net/
* https://forums.homeseer.com/forum/lighting-primary-technology-plug-ins/lighting-primary-technology-discussion/mcsmqtt-michael-mcsharry/1601281-how-to-integrate-bambu-lab-3d-printer-via-mqtt
* https://community.home-assistant.io/t/bambu-lab-x1-x1c-mqtt/489510
