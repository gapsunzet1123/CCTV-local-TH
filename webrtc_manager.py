import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stdin.encoding and sys.stdin.encoding.lower() != 'utf-8':
    try:
        sys.stdin.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os
import json
import time
import subprocess
import atexit
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOCAL_CONFIG = BASE_DIR / "cameras.local.json"
DEFAULT_CONFIG = BASE_DIR / "cameras.json"
YAML_FILE = BASE_DIR / "go2rtc.yaml"
GO2RTC_EXE = BASE_DIR / "bin" / "go2rtc.exe"

def get_config_file():
    return LOCAL_CONFIG if LOCAL_CONFIG.exists() else DEFAULT_CONFIG

class Go2RTCManager:
    def __init__(self):
        self.process = None
        self.sync_config()

    def sync_config(self):
        """Reads camera config and generates go2rtc.yaml"""
        cfg_file = get_config_file()
        if not cfg_file.exists():
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

        if not GO2RTC_EXE.exists():
            print("[Error] go2rtc.exe not found in bin directory.")
            return

        self.sync_config()
        cmd = [str(GO2RTC_EXE), "-config", str(YAML_FILE)]
        self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
