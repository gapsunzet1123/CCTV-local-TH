import sys
import os

# Console safety for Windows
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

import time
import winreg
import ctypes
import webbrowser
import threading
from pathlib import Path
from PIL import Image
import pystray
import pystray._win32
from pystray import MenuItem as item, Menu
import webview

# Import our Flask app and WebRTC manager
from web_server import app, HOST, PORT
from webrtc_manager import go2rtc_mgr, BUNDLE_DIR, APP_DIR

REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "CCTVLocalWeb"
APP_TITLE = "CCTV Multi-Viewer"
URL_DASHBOARD = f"http://{HOST}:{PORT}"

_main_window = None
_should_really_exit = False
_mutex = None

# Single-Instance Check via Windows Named Mutex
def ensure_single_instance():
    global _mutex
    ERROR_ALREADY_EXISTS = 183
    _mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\CCTVLocalWebSingleInstance")
    last_error = ctypes.windll.kernel32.GetLastError()
    if last_error == ERROR_ALREADY_EXISTS:
        # Already running! Bring existing native window to front
        hwnd = ctypes.windll.user32.FindWindowW(None, APP_TITLE)
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        else:
            webbrowser.open(URL_DASHBOARD)
        sys.exit(0)

# Windows Autostart Registry Management
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
            else:
                try:
                    winreg.DeleteValue(key, APP_REG_NAME)
                except FileNotFoundError:
                    pass
        icon.update_menu()
    except Exception:
        pass

# Tray and Window Actions
def show_window(icon=None, item=None):
    global _main_window
    if _main_window:
        try:
            _main_window.show()
            _main_window.restore()
        except Exception:
            pass

def open_in_browser(icon=None, item=None):
    webbrowser.open(URL_DASHBOARD)

def restart_streams(icon=None, item=None):
    go2rtc_mgr.restart()

def open_folder(icon=None, item=None):
    try:
        os.startfile(str(APP_DIR))
    except Exception:
        pass

def exit_app(icon=None, item=None):
    global _should_really_exit, _main_window
    _should_really_exit = True
    try:
        go2rtc_mgr.stop()
    except Exception:
        pass
    if icon:
        try:
            icon.stop()
        except Exception:
            pass
    if _main_window:
        try:
            _main_window.destroy()
        except Exception:
            pass
    os._exit(0)

def on_window_closing():
    global _should_really_exit, _main_window
    if not _should_really_exit:
        if _main_window:
            try:
                _main_window.hide()
            except Exception:
                pass
        return False
    return True

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
            except Exception:
                pass
    return Image.new("RGBA", (64, 64), (14, 165, 233, 255))

def main():
    global _main_window
    ensure_single_instance()

    # 1. Start go2rtc hardware-accelerated WebRTC streaming engine
    go2rtc_mgr.start()

    # 2. Start Flask Web Server in background thread
    def run_flask():
        app.run(host=HOST, port=PORT, threaded=True, debug=False, use_reloader=False)

    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()

    # 3. Setup System Tray Menu
    menu = Menu(
        item("🖥️ เปิดหน้าต่างแอป (Show App)", show_window, default=True),
        item("🌐 เปิดดูผ่านเบราว์เซอร์ (Open in Browser)", open_in_browser),
        item("🔄 เชื่อมต่อสัญญาณใหม่ (Restart Streams)", restart_streams),
        item("📁 เปิดโฟลเดอร์โปรแกรม (Open App Folder)", open_folder),
        item("🚀 เริ่มทำงานพร้อมเปิด Windows", toggle_autostart, checked=lambda it: is_autostart_enabled()),
        Menu.SEPARATOR,
        item("❌ ออกจากโปรแกรม (Exit)", exit_app)
    )

    icon_image = get_app_icon()
    tray_icon = pystray.Icon(
        name="CCTV-Local-App",
        icon=icon_image,
        title="CCTV Multi-Viewer (ทำงานอยู่ในพื้นหลัง)",
        menu=menu
    )

    # Run tray in daemon thread
    threading.Thread(target=tray_icon.run, daemon=True).start()

    # 4. Create and start native desktop window (Edge WebView2)
    _main_window = webview.create_window(
        title=APP_TITLE,
        url=URL_DASHBOARD,
        width=1380,
        height=820,
        min_size=(900, 550),
        background_color="#0b1120"
    )
    _main_window.events.closing += on_window_closing

    # Start native window event loop on main thread
    webview.start()

    # Clean exit when window is closed
    exit_app(tray_icon)

if __name__ == "__main__":
    main()
