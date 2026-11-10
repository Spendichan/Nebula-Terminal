import platform
import shutil
import socket
import time
import urllib.request
import zipfile
from pathlib import Path
import os
import psutil
import requests
import speedtest
from cryptography.fernet import Fernet

VERSION = "1.0.3"

def hostname():
    hostname = socket.gethostname()
    return hostname

def speed_test():
    print("Starting speedtest...")

    try:
        st = speedtest.Speedtest()

        st.get_best_server()

        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000

        ping = st.results.ping

        print(f"Download: {download:.2f} Mbps")
        print(f"Upload:   {upload:.2f} Mbps")
        print(f"Ping:     {ping:.2f} ms")

    except Exception as e:
        print(f"Speedtest failed: {e}")

def ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("1.1.1.1", 53))
            local_ip = s.getsockname()[0]

        print(f"Local IP: {local_ip}")
        string = f"ipv4: {local_ip}"
    except OSError:
        print("local ip: unavailable")

    try:
        with urllib.request.urlopen(
            "https://api.ipify.org", timeout=5
        ) as response:
            public_ip = response.read().decode()

        print(f"Public IP: {public_ip}")
        string = f"ipv6: {public_ip}"
    except Exception:
        print("Public IP: unavailable")

def disk():
    total, used, free = shutil.disk_usage("/")
    gb = 1024 ** 3
    string = (f"""
    total: {total / gb:.2f} GiB
    used: {used / gb:.2f} GiB
    free: {free / gb:.2f} GiB
    """)
    print(string)

def create_zip():
    folder_path = Path(input("\npath: "))

    if not folder_path.is_dir():
        if not folder_path.is_file():
            print("\ndirection doesnt exists")
            return

    if input("\nAre you sure? [y/n]").lower() != "y":
        print("\nzip creation canceled")
        return

    try:
        name = input("\nname of new zip: ")
        if not name.endswith(".zip"):
            print("\nplease name your zip file with .zip at the end")
            print("\nfor example: example.zip")
            return
        with zipfile.ZipFile(
            name,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as zips:
            if not folder_path.is_file():
                for file in folder_path.rglob("*"):
                    if file.is_file():
                        zips.write(
                            file,
                            file.relative_to(folder_path.parent)
                        )
                        print(f"packing: {file}")
            else:
                zips.write(folder_path)

    except OSError as error:
        print(error)


def delete_file(path):
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path)
        print(f"\nremoved {path} and content in it")
    
    elif path.is_file():
        path.unlink()
        print(f"\nremoved {path}")

    else:
        print(f"\n{path} doesnt exists")

def get_time():
    current_time = time.ctime()
    return current_time

def mkdir():
    path = Path(input("path: "))
    if path.is_dir():
        print("\npath already exists")
        return
    try:
        os.makedirs(path)
        print(f"\n{path} was created")
    except PermissionError:
        print(f"\nyou dont have the permission to create {path}")

def help():
    print("""
    commands:
        info            -please enter this command first, it shows the important information about Nebula
        help            -list all available commands
        exit            -exit the Nebula Terminal (add a number at the end like exit 5 for delay in sec)
        sysinfo         -show user information
        nano            -create a file
        rm              -delete a file or dir
        ls              -list everything inside a folder
        zip             -create a zip-file containing a folder or file
        weather         -get the current weather stats
        disk            -show the disk usage
        hostname        -show your hostname
        ip              -show your ipv4 and ipv6 address
        speedtest       -test your internet speed
        mkdir           -create a folder

    exp. commands:
        encrypt         -encrypt data (folders and files)
        decrypt         -decrypt data (folders and files)
        zip-b           -create a zip bomb (can be really big -> be carefull)

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

        if file_path.name.endswith(".key"):
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
    if input("load existing key? [y/n]").lower() == "y":
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
    else:
        if input("\ngenerate a new key? [y/n]").lower() == "y":
            key = Fernet.generate_key()

            with open("key.txt.key", "wb") as file:
                file.write(key)
        else:
            print("\nencryption canceled")
            return
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

    if input("\nAre u sure? [y/n]").lower() != "y":
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


def sysinfo():
    mem = psutil.virtual_memory()

    string = (f"""
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
    print(string)

def get_weather():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            "latitude=53.6&longitude=11.4&current=temperature_2m"
        )
        response = requests.get(url)
        data = response.json()

        print(f"\n{data.get('current_weather', {}).get('temperature', 'N/A')}°C")

    except OSError:
        print("\nError: no internet connection")


def ls():
    folder_path = Path(input("\nfolder path: "))

    if not folder_path.is_dir():
        print("\nfolder doesnt exists")

    for file_path in folder_path.rglob("*"):
        print(file_path)


def zips_b():
    path = "data_for_zipb.txt"

    try:
        loop = int(input("loop for the 8.7GB to be inside the zip: "))
        print(f"\nzip size: {loop * 8.7}GB")

    except:  # noqa: E722
        print("\nerror: loop needs to be an integer")
        return

    data = "000000000000000"

    if not Path(path).is_file():
        print("\ndata for the zip doesnt exists")
        time.sleep(2)
        print("\ncreating data for the zip bomb...")

        with open(path, "w") as file:
            file.writelines(data for i in range(625000000))

    print("\ncreating the zip bomb layer 1")

    with zipfile.ZipFile(
        "zip_bomb_data.zip",
        "w",
        compression=zipfile.ZIP_LZMA,
        compresslevel=9
    ) as zipb:
        for i in range(loop):
            zipb.write(path, f"data_{i}.txt")

    print("\ncreating the zip bomb layer 2")
    
    with zipfile.ZipFile(
        "zip_03.zip",
        "w",
        compression=zipfile.ZIP_LZMA,
        compresslevel=9
    ) as zipb:
        for i in range(loop):
            zipb.write("zip_bomb_data.zip", f"data_{i}.zip")

    print("\nlayer 3")
    n=int(input("loop: "))
    with zipfile.ZipFile(
        "zip.zip",
        "w",
        compression=zipfile.ZIP_LZMA,
        compresslevel=9
    ) as zipb:
        for n in range(loop):
            zipb.write("zip_03.zip", f"data_{i}.zip")

    print("\nlayer 4")
    n=int(input("loop: "))
    with zipfile.ZipFile(
        "zip02.zip",
        "w",
        compression=zipfile.ZIP_LZMA,
        compresslevel=9
    ) as zipb:
        for n in range(loop):
            zipb.write("zip.zip", f"data_{i}.zip")

    print("\nlayer 5")
    n=int(input("loop: "))
    with zipfile.ZipFile(
        "zip_bomb.zip",
        "w",
        compression=zipfile.ZIP_LZMA,
        compresslevel=9
    ) as zipb:
        for n in range(loop):
            zipb.write("zip02.zip", f"data_{i}.zip")

    if Path("zip_bomb_data.zip"):
        os.remove("zip_bomb_data.zip")
    if Path("zip_03.zip"):
        os.remove("zip_03.zip")
    if Path("zip.zip"):
        os.remove("zip.zip")
    if Path("zip02.zip"):
        os.remove("zip02.zip")
    
    print("\nzip-bomb was created")

def command_prozessing(command):
    match command:
        case command if command.replace(" ","") =="zip-b":
            zips_b()

        case command if command.replace(" ","")=="mkdir":
            mkdir()

        case command if command.replace(" ","") =="help":
            help()

        case command if command.replace(" ","") =="zip":
            create_zip()

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

        case command if command.replace(" ","") =="sysinfo":
            sysinfo()

        case command if command.replace(" ","") =="info":
            info()

        case command if command.replace(" ","") =="disk":
            disk()

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

        case command if command.replace(" ","") =="weather":
            get_weather()

        case command if command.replace(" ","") =="encrypt":
            encrypt()

        case command if command.replace(" ","") =="decrypt":
            decrypt()

        case command if command.replace(" ","") =="ls":
            ls()

        case command if command.replace(" ","") =="speedtest":
            speed_test()

        case command if command.replace(" ","") =="ip":
            ip()

        case command if command.replace(" ","") == "hostname":
            name = hostname()
            print(f"\n{name}")

        case _:
            print(
                f"\nunknown command: {command}"
                f"\n-type help to list every command available-"
            )

print("starting setup...")
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
