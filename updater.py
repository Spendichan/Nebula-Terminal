import sys
import time
import os
import subprocess
from pathlib import Path

def install_update():
    if len(sys.argv) != 3:
        print("Ungültige Argumente")
        return

    app_path = Path(sys.argv[1]).resolve()
    new_exe = Path(sys.argv[2]).resolve()

    if not app_path.is_file() or not new_exe.is_file():
        print("EXE nicht gefunden")
        return

    for _ in range(30):
        try:
            os.replace(new_exe, app_path)
            break
        except PermissionError:
            time.sleep(1)
        except OSError as e:
            print(f"Fehler beim Ersetzen: {e}")
            return
    else:
        print("Update konnte nicht installiert werden.")
        return

    subprocess.Popen([str(app_path)], cwd=str(app_path.parent))

if __name__ == "__main__":
    install_update()
