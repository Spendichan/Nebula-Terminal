import time
import platform
import psutil
from pathlib import Path
import requests
from packaging.version import Version
import socket
from tqdm import tqdm
import random
from cryptography.fernet import Fernet

VERSION = "1.0.3"


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
        info            -please enter this command first, it shows the important information about Nebula
        help            -list all available commands
        exit            -exit the Nebula (add a number at the end like exit 5 for delay in sec)
        device-info     -get user information
        nano            -create a file (cant create folders)
        rm              -delete a file (cant delete folders)
        weather         -get the current weather stats

    exp. commands:
        encrypt         -encrypt data (folders and files)
	decrypt		-decrypt data (folders and files)

	WARNING: If you encrypt data and lose the key (generated in nebula folder or your own)
		 it wont be possible to decrypt your data! So be careful with this tool and
		 only use it if you know what you are doing!
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

        if new_content == "":
            return

        pathing.write_text(new_content)

    else:
        new_content = input("New content: ")
        pathing.write_text(new_content)

        print(f"\n{file_name} created in {pathing}")


def info():
    print("""
    The Nebula Terminal is build to do serveral functions that a normal terminal cant do.
    This isn't a substitute for a normal terminal. Use the powerful uses of Nebula only 
    if you know what you are doing!

    Have fun!

    """)


def encrypt_folder(folder_path, cipher):
    folder_path = Path(folder_path)

    if not folder_path.is_dir():
        print("\nfolder doesnt exists")
        return

    for file_path in folder_path.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.name.endswith((".key")):
            continue

        try:
            file_data = file_path.read_bytes()
            encrypted = cipher.encrypt(file_data)

            with open(file_path, "wb") as file:
                file.write(encrypted)
                print(f"encrypted: {file_path}")

        except OSError as error:
            print(f"error with {file_path}: {error}")


def decrypt_folder(folder_path, cipher):
    folder_path = Path(folder_path)

    if not folder_path.is_dir():
        print("\nfolder doesnt exists")
        return

    for file_path in folder_path.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.name.endswith(".key"):
            continue

        try:
            file_data = file_path.read_bytes()
            decrypted = cipher.decrypt(file_data)

            with open(file_path, "wb") as file:
                file.write(decrypted)
                print(f"decrypted: {file_path}")

        except (OSError, Exception) as error:
            print(f"error with {file_path}: {error}")


def encrypt():
    try:
        with open("key.txt.key", "rb") as file:
            key = file.read()

    except:
        key_path = Path(input("\nkey path: "))

        if not key_path.is_file():
            print("\nkey doesnt exists")

            if input("\ngenerate a new key? [y/n]").lower() == "y":
                key = Fernet.generate_key()

                with open("key.txt.key", "wb") as file:
                    file.write(key)
            else:
                print("\nencryption canceled")
                return

        else:
            with open(key_path, "rb") as key_file:
                key = key_file.read()

    cipher = Fernet(key)

    if input("\nfolder or file [d/f]").lower() == "d":
        folder_path = input("folder path: ")

        if input("\nAre u sure? [y/n]: ").lower() == "y":
            encrypt_folder(folder_path, cipher)

        return

    file_path = Path(input("file path: ").strip())

    if not file_path.is_file():
        print("\nfile doesnt exists")
        return

    if input("\nAre you sure? [y/n]").lower() != "y":
        print("\nencryption was canceled")
        return

    try:
        file_data = file_path.read_bytes()
        encrypted = cipher.encrypt(file_data)

        with open("key.txt.key", "wb") as file:
            file.write(key)

        with open(file_path, "wb") as file:
            file.write(encrypted)

        print("\nfile encrypted succesfully")

    except OSError as error:
        print(f"\nfile error: {error}")


def decrypt():
    try:
        with open("key.txt.key", "rb") as file:
            key = file.read()

    except:
        key_path = Path(input("\nkey path: "))

        if not key_path.is_file():
            print("\nkey doesnt exists")
            return

        else:
            with open(key_path, "rb") as key_file:
                key = key_file.read()

    cipher = Fernet(key)

    if input("folder or file? [d/f]: ").lower() == "d":
        folder_path = input("folder path: ")

        if input("Are you sure? [y/n]: ").lower() == "y":
            decrypt_folder(folder_path, cipher)

        return

    file_path = Path(input("file path: ").strip())

    if not file_path.is_file():
        print("\nfile doesnt exists")
        return

    if input("\nAre you sure? [y/n]").lower() != "y":
        print("\ndecryption was canceled")
        return

    try:
        file_data = file_path.read_bytes()
        decrypted = cipher.decrypt(file_data)

        with open(file_path, "wb") as file:
            file.write(decrypted)

        print("\nfile decrypted succesfully")

    except OSError as error:
        print(f"\nfile error: {error}")


def check_internet():
    try:
        socket.create_connection(("1.1.1.1", 443), timeout=3)
        return True

    except OSError:
        return False


def device_info():
    mem = psutil.virtual_memory()

    print(f"""
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


def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=53.6&longitude=11.4&current=temperature_2m"
        response = requests.get(url)
        data = response.json()

        print(f"\n{data}")

    except OSError:
        print("\nError: no internet connection")


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
                        print(
                            f"\nexit Nebula Terminal with a delay of {delay} sec..."
                        )
                        exit_application(delay)
                        return 0

                    except:
                        print("\nError: there must be given a number after -h")

                else:
                    print(f"\nError: unknown argument {split[1]}")

            except:
                print("exit Nebula Terminal...")
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
                        print(
                            "\nError: please connect the name with characters for example - _"
                        )
                        return

                except:
                    if command.endswith((".txt", ".py")):
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

        case "weather":
            get_weather()

        case "encrypt":
            encrypt()

        case "decrypt":
            decrypt()

        case _:
            print(
                f"\nunknown command: {command}"
                f"\n-type help to list every command available-"
            )


print("starting setup...")
print("")

for i in tqdm(range(100), desc="Loading modules       "):
    time.sleep(0.05)

print("")

for i in tqdm(range(100), desc="Loading configuration "):
    time.sleep(0.1)
    i = 1

    if i == random.randint(1, 10):
        time.sleep(0.4)

print("\nchecking internet connection...")

if check_internet():
    pass
else:
    print("\nNo internet connection or connection is refused by the device")

time.sleep(2)

print("""
\033[38;5;219m            ✦\033[0m
\033[38;5;213m         ▄▄████▄▄\033[0m            \033[38;5;51m✧\033[0m
\033[38;5;177m       ▄██████████▄\033[0m
\033[38;5;141m  ✧    ▀██████████▀\033[0m
\033[38;5;105m         ▀▀████▀▀\033[0m       \033[38;5;219m✦\033[0m
\033[38;5;69m            ✦\033[0m

\033[38;5;51m███╗   ██╗███████╗██████╗ ██╗   ██╗██╗      █████╗ \033[0m
\033[38;5;45m████╗  ██║██╔════╝██╔══██╗██║   ██║██║     ██╔══██╗\033[0m
\033[38;5;39m██╔██╗ ██║█████╗  ██████╔╝██║   ██║██║     ███████║\033[0m
\033[38;5;33m██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║██║     ██╔══██║\033[0m
\033[38;5;99m██║ ╚████║███████╗██████╔╝╚██████╔╝███████╗██║  ██║\033[0m
\033[38;5;135m╚═╝  ╚═══╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝\033[0m

""")

time.sleep(2)

print("\n-----------------------------")
print("\nType help to see the commands")
print("\n-----------------------------")

while True:
    command = input(f"\n{time.ctime()} : > ")
    loop = command_prozessing(command)

    if loop == 0:
        break
