import time
import platform
import psutil
import re 
import pathlib
from pathlib import Path
import requests
from packaging.version import Version
import sys
import subprocess
import keyboard 
from scapy.all import sniff, IP


VERSION = "1.0.2"
GITHUB_API = "https://api.github.com/repos/Spendichan/Spendi-Agent/releases/latest"

def check_update():
    try:
        response = requests.get(GITHUB_API, timeout=10)
        response.raise_for_status()

        release = response.json()
        latest_version = release["tag_name"].lstrip("v")

        print("Installierte Version:", VERSION)
        print("Neueste Version:", latest_version)

        if Version(latest_version) <= Version(VERSION):
            print("Du hast bereits die neueste Version.")
            return None

        print("Ein Update ist verfügbar!")

        for asset in release["assets"]:
            if asset["name"] == "SpendyAgent.exe":
                return asset["browser_download_url"]

        print("Keine passende EXE im Release gefunden.")

    except (requests.RequestException, KeyError, ValueError) as error:
        print(f"Update-Prüfung fehlgeschlagen: {error}")

    return None


def download_update(url):
    # Funktioniert so für die kompilierte Windows-EXE
    if not getattr(sys, "frozen", False):
        print("Der automatische EXE-Updater funktioniert nur in der EXE.")
        return

    app_path = Path(sys.executable).resolve()
    app_folder = app_path.parent
    new_exe = app_folder / "SpendyAgent_new.exe"
    updater_exe = app_folder / "Updater.exe"

    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(new_exe, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

        if not updater_exe.is_file():
            print("Updater.exe wurde nicht gefunden.")
            new_exe.unlink(missing_ok=True)
            return

        subprocess.Popen([
            str(updater_exe),
            str(app_path),
            str(new_exe)
        ])

        sys.exit()

    except requests.RequestException as error:
        print(f"Download fehlgeschlagen: {error}")
        new_exe.unlink(missing_ok=True)


update_url = check_update()

if update_url:
    download_update(update_url)

def packet_handler(packet):
    if IP in packet:
        print(packet[IP].src)

def networkscan(check=0):
    print("\nstarting network-scan...")
    print("\nstop the script by pressing and holding down esc")
    if check ==1:
        while True:

            packets = sniff(prn=packet_handler, timeout=1)
            packets.summary()

            if keyboard.is_pressed("esc"):
                break

    elif check ==0:
        while True:
            packets = sniff(timeout=1)
            packets.summary()

            if keyboard.is_pressed("esc"):
                break

def delete_file(path):
    path = Path(path)
    if path.exists():
        path.unlink()
        print(f"\n{path} was deletet")

    else:
        print(f"\nError {path} doesn't exist")

def get_time():
    current_time = time.ctime()
    return current_time

def help():
    print("""
    commands:
        info            -shows information about Spendi Agent
        help            -list all available commands
        exit            -exit the spendi agent (add a number at the end like exit 5 for delay in sec)
        device-info     -get user information
        nano            -create a file (cant create folders)
        rm              -delete a file (cant delete folders)
        network-scan    -scan through your local wifi for connections and other devices (arg: -t |arg2: ip; soon...)
    """)

def exit_application(delay=0):
    time.sleep(delay)

def nano(file_name):
    project_folder = Path(__file__).resolve().parent
    pathing = project_folder / file_name

    if pathing.exists():
        print(f"{file_name} located in {pathing}")

        file_data = pathing.read_text()

        print("\nold file content:")
        print(file_data)

        new_content = input("\nNew content: ")
        pathing.write_text(new_content)

    else:
        new_content = input("New content: ")
        pathing.write_text(new_content)

        print(f"\n{file_name} created in {pathing}")

def info():
    print("""\n
    The Spendi Agent is build to do serveral functions that a normal terminal cant do.
    This isn't a substitute for a normal terminal. 

    Have fun!

    """)

def device_info():
    mem = psutil.virtual_memory()
    
    print(f"""\n
    device info: 
        OS:             {platform.system()}
        architecture:   {platform.machine()}
        processor:      {platform.processor()}
        hostname:       {platform.node()}
    
    cpu:
        cpu count:      {psutil.cpu_count()}
        cpu frequence:  {psutil.cpu_freq()}
        
    ram:
        ram used:       {mem.used / 1000000000:.1f} GB
        ram available:  {mem.available / 1000000000:.1f} GB
        ram free:       {mem.free / 1000000000:.1f} GB
    
    """)

def command_prozessing(command):

    match command:

        case "help":
            help()

        case command if command.startswith("exit"):
            try:
                split = command.split()
                if split[1] == "-h":
                    try: 
                        delay = int(split[2])
                        print(f"\nexit Spendi Agent with a delay of {delay} sec...")
                        exit_application(delay)
                        return 0
                    except:
                        print("\nError: there must be given a number after -h")
                else:
                    print(f"\nError: unknown argument {split[1]}")
            except:
                print("exit Spendi Agent...")
                exit_application()
                return 0
            

        case "device-info":
            device_info()

        case "info":
            info()

        case command if command.startswith("nano"):
            try:
                args = command.split()
                name = args[1]
                
                try:
                    if args[2]:
                        print("\nError: please connect the name with characters for example - _")
                        return
                except:
                    if command.endswith((".txt",".py")):
                        nano(name)
                    else:
                        print("Error: only .txt or .py files are allowed ")

            except:
                print("\nError: dont forget to add the name of the file after nano")

        case command if command.startswith("rm"):
            try:
                args = command.split()
                path = args[1]

                delete_file(path)
            except:
                print("\nError: dont forget the path after rm")

        case command if command.startswith("network-scan"):
            try:
                args = command.split()
                if args[1]:
                    if args[1] =="-t":
                        if args[2]:
                            if args[2] =="ip":
                                networkscan(1)
                            else:
                                print(f"\nError: unknown target {args[2]}")
                        else:
                            print("\nError: dont forget to add a target after -t")
                    else:
                        print(f"\nError: unknown argument {args[1]}")
                

            except:
                networkscan()

        case _:
            print(f"\nunknown command: {command}\
                  \n-type help to list every command available-")

GREEN   = "\033[1;32m"   # Grün (fett)
RESET   = "\033[0m"      # Zurücksetzen

BANNER = GREEN + r"""
 ___ ___ ___ _  _ ___ ___     _    ___ ___ _  _ _____
/ __| _ \ __| \| |   \_ _|   /_\  / __| __| \| |_   _|
\__ \  _/ _|| .` | |) | |   / _ \| (_ | _|| .` | | |
|___/_| |___|_|\_|___/___| /_/ \_\\___|___|_|\_| |_|
""" + RESET

print(BANNER)


while True:
    command = input(f"\n{time.ctime()} : > ")
    loop = command_prozessing(command)
    if loop == 0:
        break
