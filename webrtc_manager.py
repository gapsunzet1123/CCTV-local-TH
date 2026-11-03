import sys
import os

# Ensure safe console handling on Windows (handles None when run without console)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
else:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")
else:
    if sys.stdin and sys.stdin.encoding and sys.stdin.encoding.lower() != 'utf-8':
        try:
            sys.stdin.reconfigure(encoding='utf-8')
        except Exception:
            pass

import json
import time
import subprocess
import atexit
import shutil
from pathlib import Path

# Path resolutions (support PyInstaller bundled mode and normal script mode)
if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS).resolve()
    APP_DIR = Path(sys.executable).resolve().parent
else:
    BUNDLE_DIR = Path(__file__).resolve().parent
    APP_DIR = Path(__file__).resolve().parent

def get_config_file():
    """Finds or creates cameras config file in persistent APP_DIR"""
    # 1. Local private credentials
    local_cfg = APP_DIR / "cameras.local.json"
    if local_cfg.exists():
        return local_cfg
    if (APP_DIR.parent / "cameras.local.json").exists():
        return APP_DIR.parent / "cameras.local.json"

    # 2. General config
    default_cfg = APP_DIR / "cameras.json"
    if default_cfg.exists():
        return default_cfg
    if (APP_DIR.parent / "cameras.json").exists():
        return APP_DIR.parent / "cameras.json"

    # 3. Copy bundled template if neither exists
    bundled_cfg = BUNDLE_DIR / "cameras.json"
    if bundled_cfg.exists():
        try:
            shutil.copyfile(bundled_cfg, default_cfg)
            return default_cfg
        except Exception:
            return bundled_cfg

    return default_cfg

def get_go2rtc_exe():
    """Finds go2rtc executable in bundled assets or beside executable"""
    # Check bundled bin folder
    b1 = BUNDLE_DIR / "bin" / "go2rtc.exe"
    if b1.exists():
        return b1
    # Check APP_DIR bin folder
    b2 = APP_DIR / "bin" / "go2rtc.exe"
    if b2.exists():
        return b2
    # Check parent bin folder (e.g. running from dist/)
    b3 = APP_DIR.parent / "bin" / "go2rtc.exe"
    if b3.exists():
        return b3
    # Check directly beside exe
    b4 = APP_DIR / "go2rtc.exe"
    if b4.exists():
        return b4
    return b1

YAML_FILE = APP_DIR / "go2rtc.yaml"

class Go2RTCManager:
    def __init__(self):
        self.process = None

    def sync_config(self):
        """Reads camera config and generates go2rtc.yaml"""
        cfg_file = get_config_file()
        if not cfg_file or not cfg_file.exists():
            return

        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[Error] Failed to load {cfg_file.name}: {e}")
            return

        lines = ["streams:"]
        for cam in data.get("cameras", []):
            if cam.get("enabled", True) and cam.get("url"):
                cid = f"cam{cam.get('id')}"
                url = cam.get("url").strip()
                lines.append(f'  {cid}: "{url}"')

        lines.extend([
            "",
            "api:",
            '  listen: ":1984"',
            "",
            "webrtc:",
            '  listen: ":8555"'
        ])

        with open(YAML_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def start(self):
        if self.process and self.process.poll() is None:
            return

        exe_path = get_go2rtc_exe()
        if not exe_path.exists():
            print(f"[Error] go2rtc.exe not found at: {exe_path}")
            return

        self.sync_config()
        cmd = [str(exe_path), "-config", str(YAML_FILE)]

        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags
        )
        print("⚡ [WebRTC Engine] go2rtc started with Zero-CPU Hardware Acceleration.")

    def restart(self):
        self.stop()
        time.sleep(0.5)
        self.start()

    def stop(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None

go2rtc_mgr = Go2RTCManager()
atexit.register(go2rtc_mgr.stop)
