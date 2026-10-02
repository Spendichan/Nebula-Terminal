import time
import platform
import psutil
import re 
import pathlib
from pathlib import Path

file_types = [".txt",".py"]

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
        ram active:     {mem.active / 1000000000:.1f} GB
    
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
