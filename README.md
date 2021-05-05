# OBSAutoQLRefresher

This script is intended to solve the **frozen game capture screen** problem in OBS which you face in Quake Live streaming.

It tackles this problem by monitoring the game server where you are playing in combination of checking steam profile page and querying a game server.

## Requirements
- Open Broadcaster Software
- Python 3.6
  - Make sure you are using 3.6 since **OBS doesn't support the versions other than 3.6**
- libraries written in requirements.txt

## Installation
1. Install Python 3.6
- Don't forget to check the "Add Python 3.6 to PATH" when installing it.

2. Download and load the script in *Scripts* window on OBS.
- Go to *Tools* in menu bar > *Scripts* and add the script via "+" button on the bottom left courner.

3. Install necessary libraries for the script using pip via Command prompt or bash or something.
- Move to the directory where requirements.txt sits and execute `pip install -r requirements.txt`
  - if your system has multiple python versions, `py -3.6 -m pip install -r requirements.txt` may help.

4. Set *Python Install Path* in Scripts window on OBS to your python 3.6's path.
- The option is **not** in *Settings* window, but in *Python Settings* tab of *Scripts* window.
5. Set *Steam Community URL* option to yours.
- If you want to get the url on Steam client, right click on your profile page and click *Copy Page URL*.
- You can open your Steam Community Profile page via *steam://url/SteamIDMyProfile*

6. Set *Target Source* to the screen which captures Quake Live and volia.

## Settings
- Enable this script [checkbox]
  - why OBS doesnt have this option as default.

- Steam Community URL [string]
  - this is used to check your game status and get the ip address of a game server where you are playing in.

- Target Source [select]
  - the target source which will be refreshed when you join/leave a server or server's map change happens.

- Check Interval (ms) [value]
  - how often the script checks a game server where you are playing.
  - the lower the value is, the more often it checks. But not recommended since setting it to lower results in more load on a game server.
  
- Blink Speed (ms) [value]
  - how fast the targeted screen turns off and on when refreshing.
  - If you set it to extremely lower value, the screen may remain frozen even if it refreshes.
  
- Disable the script when Quake Live is not running [checkbox]
  - to stop monitoring works when you are not playing Quake Live.
  
- Enable debug logging [checkbox]
  - may be useful when you fix the problems related to this script.
  
  
## Known Issues
- Failed to refresh frozen screen *when you are playing in local game server.*
  - we cannot tell apart the status of the lobby from the local server, so unfortunately, that shouldn't be helped.
- Failed to refresh frozen screen *when you reconnect to a server.*
  - you reconnect to a server so fast that the script couldn't catch the status change. thats why refreshing doesnt occur.
