import sys
import os
import time
import winreg
import ctypes
import webbrowser
import threading
import traceback
from pathlib import Path
from PIL import Image
import pystray
import pystray._win32
from pystray import MenuItem as item, Menu

# Import our Flask app and WebRTC manager
from web_server import app, HOST, PORT
from webrtc_manager import go2rtc_mgr, BUNDLE_DIR, APP_DIR

LOG_FILE = APP_DIR / "app.log"

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

# Safe redirection
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "CCTVLocalWeb"
URL_DASHBOARD = f"http://{HOST}:{PORT}"

_mutex = None
def ensure_single_instance():
    global _mutex
    ERROR_ALREADY_EXISTS = 183
    # Use Local\ namespace so no admin rights are required
    _mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\CCTVLocalWebSingleInstance")
    last_error = ctypes.windll.kernel32.GetLastError()
    if last_error == ERROR_ALREADY_EXISTS:
        log("Duplicate instance detected. Opening browser and exiting.")
        webbrowser.open(URL_DASHBOARD)
        sys.exit(0)
    log("Single instance mutex acquired successfully.")

def is_autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_REG_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def toggle_autostart(icon, item):
    current = is_autostart_enabled()
    target = not current
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if target:
                if getattr(sys, "frozen", False):
                    cmd_str = f'"{sys.executable}"'
                else:
                    cmd_str = f'"{sys.executable}" "{Path(__file__).resolve()}"'
                winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, cmd_str)
                log("Autostart enabled in registry.")
            else:
                try:
                    winreg.DeleteValue(key, APP_REG_NAME)
                    log("Autostart disabled in registry.")
                except FileNotFoundError:
                    pass
        icon.update_menu()
    except Exception as e:
        log(f"Autostart toggle error: {e}")

def open_dashboard(icon=None, item=None):
    log("Opening dashboard in browser.")
    webbrowser.open(URL_DASHBOARD)

def restart_streams(icon=None, item=None):
    log("Restarting go2rtc streams.")
    go2rtc_mgr.restart()

def open_folder(icon=None, item=None):
    log(f"Opening app folder: {APP_DIR}")
    try:
        os.startfile(str(APP_DIR))
    except Exception as e:
        log(f"Open folder error: {e}")

def exit_app(icon, item):
    log("Exiting application from system tray.")
    try:
        go2rtc_mgr.stop()
    except Exception:
        pass
    icon.stop()
    os._exit(0)

def get_app_icon():
    for loc in [
        BUNDLE_DIR / "cctv_icon.png",
        BUNDLE_DIR / "cctv_icon.ico",
        APP_DIR / "cctv_icon.png",
        APP_DIR / "cctv_icon.ico",
    ]:
        if loc.exists():
            try:
                return Image.open(str(loc))
            except Exception as e:
                log(f"Failed to open icon {loc}: {e}")
    return Image.new("RGBA", (64, 64), (14, 165, 233, 255))

def main():
    try:
        log("=== CCTV Local Web Starting ===")
        ensure_single_instance()

        log("Starting go2rtc engine...")
        go2rtc_mgr.start()

        log("Starting Flask server...")
        def run_flask():
            try:
                app.run(host=HOST, port=PORT, threaded=True, debug=False, use_reloader=False)
            except Exception as e:
                log(f"Flask runtime error: {e}\n{traceback.format_exc()}")

        server_thread = threading.Thread(target=run_flask, daemon=True)
        server_thread.start()

        def auto_open():
            time.sleep(1.2)
            open_dashboard()

        threading.Thread(target=auto_open, daemon=True).start()

        menu = Menu(
            item("📹 เปิดดูกล้อง (Open Dashboard)", open_dashboard, default=True),
            item("🔄 เชื่อมต่อสัญญาณใหม่ (Restart Streams)", restart_streams),
            item("📁 เปิดโฟลเดอร์โปรแกรม (Open App Folder)", open_folder),
            item("🚀 เริ่มทำงานพร้อมเปิด Windows", toggle_autostart, checked=lambda it: is_autostart_enabled()),
            Menu.SEPARATOR,
            item("❌ ออกจากโปรแกรม (Exit)", exit_app)
        )

        icon_image = get_app_icon()
        tray_icon = pystray.Icon(
            name="CCTV-Local-Web",
            icon=icon_image,
            title="CCTV Local Web (ทำงานอยู่ในพื้นหลัง)",
            menu=menu
        )

        log("System tray initialized. Entering event loop...")
        tray_icon.run()

    except Exception as e:
        log(f"Fatal error in main: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
