#!/usr/bin/python3

import re
import json
import os
import sys
import shutil
import subprocess
import ipaddress 

src_path, _ = os.path.split(os.path.abspath(__file__))

def checkIP(ip, hasPrefix=False):
    if hasPrefix:
        if len(ip.split("/")) != 2:
            print("Error: WrongPrefix")
            exit(1)
        try:
            ipaddress.ip_network(ip)
        except ValueError:
            print("Error: NoValidIP/Prefix")
            exit(1)
    else:
        if len(ip.split("/"))!=1:
            print("Error: NoPrefixAllowed")
            exit(1)
        try:
            ipaddress.ip_network(ip)
        except:
            print("Error: NoValidIP")
            exit(1)

def getIP(message, hasPrefix=False , stand = False):
    ip_prefix = input(message)
    
    if stand and len(ip_prefix) == 0:
      return False
    
    while True:

        if hasPrefix:
            if len(ip_prefix.split("/")) != 2:
                print("Error: WrongPrefix")
            else:
                try:
                    ipaddress.ip_network(ip_prefix)
                    return ip_prefix
                except ValueError:
                    print("Error: NoValidIP/Prefix")
        else:
            if len(ip_prefix.split("/"))!=1:
                print("Error: NoPrefixAllowed")
            else:
                try:
                    ipaddress.ip_network(ip_prefix)
                    return ip_prefix
                except:
                    print("Error: NoValidIP")

        if input("Enter again(y/n): ").strip().lower() != 'y':
            print("Nothing created")
            return None

        ip_prefix = input(message)
        
        if stand and len(ip_prefix) == 0:
          return False


def checkInterface(iface):
    if re.search("^\w{1,16}$", iface) == None:
        print("Error: InvalidInterface")
        exit(1)


def getInterface(message, stand = False):
    interface = input(message)
    
    if stand and len(interface) == 0:
      return False
    
    while re.search("^\w{1,16}$", interface) == None:
        print("Error: InvalidInterface")
        if input("Enter again(y/n): ").lower() != 'y':
            print("Nothing created")
            return None
        interface = input(message) 
        
        if stand and len(interface) == 0:
          return False
        
    return interface


def checkPort(port):
    if (not port.isdigit() or (49152 > int(port) or 65535 < int(port))):
        print("Error: InvalidPort")
        exit(1)


def getPort(message, stand = False):
    port = input(message)
    
    if len(port) == 0:
        return False

    while not port.isdigit() or 49152 > int(port) or 65535 < int(port):
        print("Erro: InvalidPort")

        if input("Enter again(y/n): ").lower() != 'y':
            print("Nothing created")
            return None
        port = input(message) 

        if len(port) == 0:
            return False
    
    return port

def writeFile(path, data):
    with open(f"{src_path}/{path}", "w") as f:
        json.dump(data, f)

def readFile(path):
    with open(f"{src_path}/{path}", "r") as f:
        data = json.load(f)
    return data


def createConfig(address = True):
    #get Server
    server = readFile(".server/config.json")

    ret = "[Interface]\n"
    ret += f"ListenPort = {server['port']}\n"
    if address:
    	ret += f"Address = {server['privateIP']}\n"
    ret += f"PrivateKey = {server['privatekey']}\n\n"

    if os.path.isdir(src_path+"/.users/"):
        users = os.listdir(src_path+"/.users/")
        for f in users:
            user = readFile(f"/.users/{f}")
            ret += f"#{user['name']}\n"
            ret += "[Peer]\n"
            ret += f"PublicKey = {user['publickey']}\n"
            ret += f"AllowedIPs = {user['route']}\n\n"
    return ret


def initialize(ip="", pip="", port="", iface="", cmd=False):
    if not cmd:
        if input("Are you sure (y/n): ").strip().lower() != 'y':
            return
    elif port.strip() == "-auto":
        port = "51820"

    if not os.path.isfile(f"{src_path}/.server/config.json"):
        if not os.path.isdir(f"{src_path}/.server"):
            os.mkdir(f"{src_path}/.server")
        
        if not cmd:
            # get ip, port, private key, public key 
            if input("Enter DNS name for server public IP? (y/n)").strip().lower() == 'y':
                ip = input("Enter server dns name: ") 
            else:
                ip = getIP("Enter server public IP: ")
                if ip == None:
                    return

            pip = getIP("Enter server private IP: ")
            if pip == None:
                return

        
            port = getPort("Enter server port [51820]: ")
            if port == False:
                port = "51820"
            elif port == None:
                return
        
            iface = getInterface("Enter Interface: ")
            if iface == None:
                return
        else:
            checkIP(ip)
            checkIP(pip)
            checkPort(port)
            checkInterface(iface)

        prikey = subprocess.getoutput(f"wg genkey 2> /dev/null")
        pubkey = subprocess.getoutput(f"echo {prikey}|wg pubkey  2>/dev/null")
        
        data = dict()
        data.update({'publicIP': ip,'privateIP' : pip,'interface' : iface,'port': port, 'privatekey': prikey, 'publickey': pubkey})
        
        # write into /.server/config.json
        writeFile(".server/config.json",data)
        
        # Create config
        with open(f"/etc/wireguard/{iface}.conf","w") as f:
        	f.write(createConfig())
        
        # Start wg        
        suc = subprocess.Popen(["systemctl", "start", f"wg-quick@{iface}"],stdout = subprocess.PIPE,stderr = subprocess.PIPE)
        suc.wait()
        if suc.returncode != 0:
        	print("Error:CouldNotStartService")
        	print("Make sure that address and port are free")
        	shutil.rmtree(src_path+"/.server")
        	return
       
        # Status ausgeben
        print("-"*30)
        os.system(f"systemctl status wg-quick@{iface}")
        print("-"*30)
        
        print(".server created and started")
    if not os.path.isdir(src_path+"/.users"):
        os.mkdir(src_path+"/.users")
        print(".users created")
    if not os.path.isdir(src_path+"/.trash"):
        os.mkdir(src_path+"/.trash")
        print(".trash created")
        



def cleanUp(cmd=False):
    if not cmd:
        if input("Are you sure (y/n): ").strip().lower() != "y":
            return
    if os.path.isdir(src_path+"/.trash"):
        shutil.rmtree(src_path+"/.trash")
        print(".trash is removed")
    if os.path.isdir(src_path+"/.users"):
        shutil.rmtree(src_path+"/.users")
        print(".users is removed")
    if os.path.isdir(src_path+"/.server"):
        shutil.rmtree(src_path+"/.server")
        print(".server is removed")




def listUsers():
    if os.path.isdir(src_path+"/.users/"):
        users = os.listdir(src_path+"/.users/")
        for f in users:
            user = readFile(f".users/{f}")
            print(user["name"] + " :: " + user["publickey"] + " :: " +user["privateIP"])           
    else:
        print("Error: No users found")



def createUser(name="", ip="", cmd=False):
    if not cmd:
         # Geneate Username
        num = 1
        while os.path.isfile(f"{src_path}/.users/user{num}.json"):
            num += 1
        sugg = f"user{num}"


        name = getInterface(f"Enter name of user [{sugg}]: ", True)
        if name == False:
            name = sugg
        elif name == None:
            return

        while os.path.isfile(f"{src_path}/.users/{name}.json"):
            if input("Error: UserNotFound\nEnter again (y/n): ").lower() != "y":
                return
            # Enter Username
            name = getInterface("Enter name of user: ")
            if name == None:
                return
    else:
        if name.strip() == "-auto":
            num = 1
            while os.path.isfile(f"{src_path}/.users/user{num}.json"):
                num += 1
            name = f"user{num}"
        else:
            if os.path.isfile(f"{src_path}/.users/{name}.json"):
                print("Error: UserAlreadyInUse")
                exit(1)
            checkInterface(name)

    #create private and public key
    prikey = subprocess.getoutput(f"wg genkey 2> /dev/null")
    pubkey = subprocess.getoutput(f"echo {prikey}|wg pubkey  2>/dev/null")

    # search biggest IP
    ad = ipaddress.IPv4Address(readFile(".server/config.json")["privateIP"])
    users = os.listdir(src_path+"/.users/")
    for f in users:
        user = readFile(f"/.users/{f}")
        if ad < ipaddress.IPv4Address(user["privateIP"]):
            ad = ipaddress.IPv4Address(user["privateIP"])
    ad += 1

    if not cmd:
        #read public and local ip
        ip = getIP(f"Enter local IP for Client [{ad}]: ", False , True)
        if ip == False:
            ip = str(ad)
        elif ip == None:
            return
    else:
        if ip.strip() == "-auto":
            ip = str(ad)
        checkIP(ip)

    #write user
    data = dict()
    data.update({'route': f"{ip}/32",'name': name, 'privateIP': ip, 'privatekey': prikey, 'publickey': pubkey})

    writeFile(f".users/{name}.json",data)


def deleteUser(name="",cmd=False):
    if not cmd:
        # Enter Username
        name = getInterface("Enter name of user: ")
        if name == None:
            return
    	
        while not os.path.isfile(f"{src_path}/.users/{name}.json"):
            if input("Error: UserNotFound\nEnter again (y/n): ").lower() != "y":
                return
            # Enter Username
            name = getInterface("Enter name of user: ")
            if name == None:
                return
    elif not os.path.isfile(f"{src_path}/.users/{name}.json"):
        print("Error: UserNotFound")
        exit(1)


    if os.path.isfile(f"{src_path}/.trash/{name}.json"):
        os.remove(f"{src_path}/.trash/{name}.json")
    shutil.move(f"{src_path}/.users/{name}.json",f"{src_path}/.trash/")

    if os.path.isfile(f"{src_path}/export/{name}.conf"):
        if input("Delete user-export? (y/n): ").lower() == "y":
            if os.path.isfile(f"{src_path}/.trash/{name}.conf"):
                os.remove(f"{src_path}/.trash/{name}.conf")
            shutil.move(f"{src_path}/export/{name}.conf",f"{src_path}/.trash/")


def showConfig():
    if not os.path.isfile(f"{src_path}/.server/config.json"):
        print("Error: ConfigNotFound")
    else:
        print(createConfig(),end='')


def applyConfig():
    if os.path.isfile(f"{src_path}/.server/config.json"):
        server = readFile(".server/config.json")
        # Create config
        with open(f"/etc/wireguard/{server['interface']}.conf","w") as f:
            f.write(createConfig())
        
        # Create config for changes
        with open(f"{src_path}/.server/{server['interface']}.conf","w") as f:
            f.write(createConfig(False))
        # Insert Changes
        os.system(f"wg syncconf {server['interface']} {src_path}/.server/{server['interface']}.conf")
            
        # Print
        print("Config written") 

    else:
        print("Error: ConfigNotFound")



def showRoute(name="", cmd=False):
    if not cmd:
        # Enter Username
        name = getInterface("Enter name of user: ")
        if name == None:
            return
        while not os.path.isfile(f"{src_path}/.users/{name}.json"):
            if input("Error: UserNotFound\nEnter again (y/n): ").lower() != "y":
                return
            # Enter Username
            name = getInterface("Enter name of user: ")
            if name == None:
                return
    elif not os.path.isfile(f"{src_path}/.users/{name}.json"):
        print("Error: UserNotFound")
        exit(1)

    # get user route
    data = readFile(f".users/{name}.json")
    if len(data["route"]) != 0:
        for d in data["route"].split(", "):
            print(f"-> {d}")
    else:
        print("No Route Defined")

def addRoute(name="", route="", cmd=False):
    if not cmd:
        # Enter Username
        name = getInterface("Enter name of user: ")
        if name == None:
            return

        while not os.path.isfile(f"{src_path}/.users/{name}.json"):
            if input("Error: UserNotFound\nEnter again (y/n): ") != "y":
                return
            # Enter Username
            name = getInterface("Enter name of user: ")
            if name == None:
                return


        route = getIP("Enter new Route: ", True)
        if route == None:
            return
    else:
        if not os.path.isfile(f"{src_path}/.users/{name}.json"):
            print("Error: UserNotFound")
            exit(1)
        checkInterface(name)
        checkIP(route, hasPrefix=True)

    # add route to user.json
    data = readFile(f".users/{name}.json")
    # Check if route already added
    if route in data["route"]:
        print("Error: RouteAlreadyActive")
        return
    if len(data["route"]) == 0:
        data["route"] += route
    else:
        data["route"] += ", " + route
    writeFile(f".users/{name}.json",data)

def deleteRoute(name="", in_route="", cmd=False):
    if not cmd:
        # Enter Username
        name = getInterface("Enter name of user: ")
        if name == None:
            return

        while not os.path.isfile(f"{src_path}/.users/{name}.json"):
            if input("Error: UserNotFound\nEnter again (y/n): ") != "y":
                return
            # Enter Username
            name = getInterface("Enter name of user: ")
            if name == None:
                return


        in_route = getIP("Enter route: ", True)
        if in_route == None:
            return
    else:
        if not os.path.isfile(f"{src_path}/.users/{name}.json"):
            print("Error: UserNotFound")
            exit(1)
        checkInterface(name)
        checkIP(in_route, hasPrefix=True)


    # delete route in user.json
    data = readFile(f".users/{name}.json")
    # Split to diffrent routes
    prev = data["route"]
    routes = prev.split(",")
    ret = ""

    for route in routes:
        if not in_route in route:
            if not len(ret) == 0:
                ret += ","
            ret += route

    data["route"] = ret

    if ret is prev:
        print("Route was not found")

    writeFile(f".users/{name}.json",data)


def deleteAllRoutes(name="", cmd=False):
    if not cmd:
        # Enter Username
        name = getInterface("Enter name of user: ")
        if name == None:
            return

        while not os.path.isfile(f"{src_path}/.users/{name}.json"):
            if input("Error: UserNotFound\nEnter again (y/n): ") != "y":
                return
            # Enter Username
            name = getInterface("Enter name of user: ")
            if name == None:
                return
    elif not os.path.isfile(f"{src_path}/.users/{name}.json"):
        print("Error: UserNotFound")
        exit(1)


    # delete route in user.json
    data = readFile(f".users/{name}.json")
    data["route"] = ""
    writeFile(f".users/{name}.json",data)


def exportClient(name = "", cmd = False):
    if not os.path.isdir(f"{src_path}/export"):
        os.mkdir(f"{src_path}/export")
    if not cmd:
        name = input("Enter client name: ")
        if os.path.isdir(f"{src_path}/.users"):
            while not os.path.isfile(f"{src_path}/.users/{name}.json"):
                if input("Error: UserNotFound\nEnter again (y/n): ") != "y":
                    return
                client = input("Enter client name: ")

    elif not os.path.isfile(f"{src_path}/.users/{name}.json"):
        print("Error: UserNotFound")
        exit(1)


    server = readFile(".server/config.json")
    user = readFile(f".users/{name}.json")
        
    with open(f"{src_path}/export/{user['name']}.conf", "w") as f:

        serv = "[Interface]\n"
        serv += f"ListenPort = {server['port']}\n"
        serv += f"Address = {user['privateIP']}\n"
        serv += f"PrivateKey = {user['privatekey']}\n\n"
        
        serv += "[Peer]\n"
        serv += f"PublicKey = {server['publickey']}\n"
        serv += f"AllowedIPs = {server['privateIP']}/32\n"
        serv += f"Endpoint = {server['publicIP']}:{server['port']}\n"

        print(serv)
        f.write(serv)
        print(f'{user["name"]} exported')


def exportAllClients():
    if not os.path.isdir(src_path+"/export"):
        os.mkdir(src_path+"/export")
        print("Export created")
    if os.path.isdir(src_path+"/.users/"):
        users = os.listdir(src_path+"/.users/")
        server = readFile(".server/config.json")

        serv = "[Peer]\n"
        serv += f"PublicKey = {server['publickey']}\n"
        serv += f"AllowedIPs = {server['privateIP']}/32\n"
        serv += f"Endpoint = {server['publicIP']}:{server['port']}\n"


        for u in users:
            user = readFile(f".users/{u}")
            with open(f"{src_path}/export/{user['name']}.conf","w") as f:
                ret = "[Interface]\n"
                ret += f"ListenPort = {server['port']}\n"
                ret += f"Address = {user['privateIP']}\n"
                ret += f"PrivateKey = {user['privatekey']}\n\n"
                ret += serv
                f.write(ret)
            print(f"{user['name']} exported")
    else:
        print("Error: No users found")

def printCmdHelp():
    print("Usage: wg <cmd> {<args>}\n")
    print("Available subcommands:")
    print("    --initialize [-i] {publicIP, privateIP, port[-auto], interface}:")
    print("      creates internal folder structure (.server, .users, .trash)")
    print("    --clean [-c] {}: ")
    print("      deletes internal folder structure (.server, .users, .trash) and data within")
    print("    --listUsers [-ul] {}: ")
    print("      prints all users with their public key and private ip line by line")
    print("    --createUser [-uc] {name[-auto], ip[-auto]}: ")
    print("      generates a user with name and ip")
    print("    --deleteUser [-ud] {name}: ")
    print("      removes the user with the specified name")
    print("    --showRoute [-rs] {name}: ")
    print("      lists al routes that the specified user has")
    print("    --addRoute [-ra] {name, route}: ")
    print("      adds a route to the specified user with the name")
    print("    --deleteRoute [-rd] {name, route}: ")
    print("      deletes the specified route for the given user")
    print("    --deleteAllRoutes [-rda] {name}: ")
    print("      deletes all routes for the given user")
    print("    --showConfig [-cs] {}: ")
    print("      prints the configuration for the server")
    print("    --applyConfig [-ca] {}: ")
    print("      applies the configuration for the server and copies it to /etc/wireguard")
    print("    --exportClient [-ec] {name}: ")
    print("      exports the specified client to the export/ folder")
    print("    --exportAllClients [-ea] {}: ")
    print("      exports all clients to the export/ folder")
    print("    --help [-h]: shows this")

def printMenu():
    print("")
    print("1) Initialize           8)  Delete Route")
    print("2) Clean up             9)  Delete All Routes")
    print("3) List Users           10) Show Config")
    print("4) Create User          11) Apply Config")
    print("5) Delete User          12) Export Client")
    print("6) Show Route           13) Export All Clients")
    print("7) Add Route            14) Quit")
    print("")

def checkRequirements():
    try:
        subprocess.Popen(["wg"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: WireguardNotInstalled.\nPlease install package first")
        exit(1)
    try:
        subprocess.Popen(["wg-quick"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: Wg-QuickNotInstalled.\nPlease install package first")
        exit(1)
    try:
        subprocess.Popen(["systemctl"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: SystemCtlNotInstalled.\nPlease install package first")
        exit(1)

def processArguments():
    arg1 = sys.argv[1].strip()
    if (arg1 == "--initialize" or arg1 == "-i") and len(sys.argv) == 6:
        initialize(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], cmd=True)
    elif (arg1 == "--clean" or arg1 == "-c") and len(sys.argv)==2:
        cleanUp(cmd=True)
    elif (arg1 == "--createUser" or arg1 == "-uc") and len(sys.argv)==4:
        createUser(sys.argv[2], sys.argv[3], cmd=True)
    elif (arg1 == "--deleteUser" or arg1 == "-ud") and len(sys.argv)==3:
        deleteUser(sys.argv[2], cmd=True)
    elif (arg1 == "--listUsers" or arg1 == "-ul") and len(sys.argv)==2:
        listUsers()
    elif (arg1 == "--showConfig" or arg1 == "-cs") and len(sys.argv)==2:
        showConfig()
    elif (arg1 == "--applyConfig" or arg1 == "-ca") and len(sys.argv)==2:
        applyConfig()
    elif (arg1 == "--exportClient" or arg1 == "-ec") and len(sys.argv)==3:
        exportClient(sys.argv[2], cmd=True)
    elif (arg1 == "--exportAllClients" or arg1 == "-ea") and len(sys.argv)==2:
        exportAllClients()
    elif (arg1 == "--showRoute" or arg1 == "-rs") and len(sys.argv)==3:
        showRoute(sys.argv[2], cmd=True)
    elif (arg1 == "--addRoute" or arg1 == "-ra") and len(sys.argv)==4:
        addRoute(sys.argv[2], sys.argv[3], cmd=True)
    elif (arg1 == "--deleteRoute" or arg1 == "-rd") and len(sys.argv)==4:
        deleteRoute(sys.argv[2], sys.argv[3], cmd=True)
    elif (arg1 == "--deleteAllRoutes" or arg1 == "-rda") and len(sys.argv)==3:
        deleteAllRoutes(sys.argv[2], cmd=True)
    elif (arg1 == "--help" or arg1 == "-h") and len(sys.argv)==2:
        printCmdHelp()
    else:
        print("Error: Invalid command (-h or --help for help)")
    exit(0)

def main():
    #check if user is root
    if os.geteuid() != 0:
        print("User should be root. Some commands may need root privileges!!!")
        print("This may cause unknown bugs to the developer and the user")
    
    # if has arguments, process and then stop
    if len(sys.argv)>1:
        processArguments()
    
    print("")
    print("        _ _ _ _                           _ ")
    print("       | | | |_|___ ___ ___ _ _ ___ ___ _| |")
    print("       | | | | |  _| -_| . | | | .'|  _| . |")
    print("       |_____|_|_| |___|_  |___|__,|_| |___|")
    print("                       |___|         Manager")

    checkRequirements()

    running = True
    while running:
        printMenu()
        try:
            opt = input("Enter option: ").strip()
        except KeyboardInterrupt:
            print()
            break

        print("-"*30)

        if opt != "1" and opt != "14" and opt!="2" and not os.path.isdir(f"{src_path}/.server"):
            print("You should initialize first!")

        try:
            if opt == "1":
                initialize()
            elif opt == "2":
                cleanUp()
            elif opt == "3":
                listUsers()
            elif opt == "4":
                createUser()
            elif opt == "5":
                deleteUser()
            elif opt == "6":
                showRoute()
            elif opt == "7":
                addRoute()
            elif opt == "8":
                deleteRoute()
            elif opt == "9":
                deleteAllRoutes()
            elif opt == "10":
                showConfig()
            elif opt == "11":
                applyConfig()
            elif opt == "12":
                exportClient()
            elif opt == "13":
                exportAllClients()
            elif opt == "14":
                running = False
            else:
                print("Error: Invalid Option")
        except KeyboardInterrupt:
            print()
            break

        if running:
            print("-"*30)


if __name__ == "__main__":
    main()
