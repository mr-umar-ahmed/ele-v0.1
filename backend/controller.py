import subprocess
import os

def launch_app(app_name: str):
    """
    Simulates ELE's hands. It looks for common apps and opens them.
    """
    apps = {
        "code": "code",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "browser": "start msedge" # or "start chrome"
    }
    
    try:
        if app_name in apps:
            print(f"[ELE] Launching {app_name}...")
            subprocess.Popen(apps[app_name], shell=True)
            return True
        else:
            print(f"[ELE] I don't know how to open {app_name} yet.")
            return False
    except Exception as e:
        print(f"[ELE] Error launching app: {e}")
        return False