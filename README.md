# WireGuardManager
The WireGuardManager is a tool to manage wireguard config files. <br>
You can create user/server configurations, add routes and more.

## Requirements
The only requirements needed are python3, wg, wg-quick and systemctl.

## Installation
To install the WireGuardManager we clone with git
```
git clone https://github.com/MarkusTelser/wireguard-vpn-tool 
```

## Usage
First you need to go into the cloned folder.
Then we can use WireGuardManager as a script with:
```
chmod +x main.py
./main.py
```
or execute as a program with python3:
```
python3 main.py
```
---
**NOTE**

You need root permissions, otherwise some functionalities won't work.

---

## CrashCourse
*   First we need to **Initialize** (option=1), so the internal folder structures are created.<br>
    If you have already created the internal folder structures with Initialize, then you can use **Clean up** (option=2).<br>
    This deletes the folder structures and all data. Use Clean up with caution. <br>
*   Next step is to **Create User** (option=4) and enter all data.<br>
    Then we check with **List Users** (option=3), if everything was inserted the right way.<br>
    If there are any mistakes, we can use **Delete User** (option=5) and repeat the two previous steps.<br>
    
    ---
    
    **NOTE:**  If you deleted a user by accident, then you can find it in the folder .trash/
    
    ---
    
*   Next step is to **Add Route** (option=7) and enter all data.<br>
    Then we check with **List Route** (option=6), if everything was inserted the right way.<br>
    If not, we can use **Delete Route** (option=8) or **Delete All Routes** (option=9) and repeat the two previous steps.
*   Then we check with **Show Config** (option=10), if the config was created the right way.<br>
    Then we need **Apply Config** (option=11) to apply the config with wg-quick and systemctl to the interface.
    
    ---
    
    **NOTE:**  Current configuration for the interface will be overwritten and not recoverable after ApplyConfig.
    
    ---
*   As a bonus step, we can use **Export Client** (option=12) or **Export All Clients** (option=13).<br>
    This exports the configuration of a specified/all user/s into the folder export/.<br>
    So you can send this file to the client/s and he can just apply the configuration.
*   Last step is to **Quit** the program with:
    * option = 14
    * control-c (no option to clean up folder structures) 
    
## Internal Folder Structure
This are the folders created by "Initialize" and deleted by "Clean up".<br>
They are used to store client and server data local, so it can be used during Runtime.
*   .users/ folder contains the user.json data for every user
*   .server/ folder contains the server.json data
*   .trash/ folder contains deletes user.json data
