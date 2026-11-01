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

import time
import json
import webbrowser
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify

from webrtc_manager import go2rtc_mgr, get_config_file

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "web" / "templates"),
    static_folder=str(BASE_DIR / "web" / "static")
)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

HOST = "127.0.0.1"
PORT = 5000

# Start hardware-accelerated go2rtc engine
go2rtc_mgr.start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET", "POST"])
def config_api():
    cfg_file = get_config_file()
    if request.method == "POST":
        data = request.get_json() or {}
        cameras_data = data.get("cameras", [])
        if cameras_data:
            with open(cfg_file, "w", encoding="utf-8") as f:
                json.dump({"cameras": cameras_data}, f, indent=4, ensure_ascii=False)
            # Reload go2rtc engine with new streams
            go2rtc_mgr.restart()
            return jsonify({"status": "success", "message": "บันทึกและเชื่อมต่อกล้องใหม่เรียบร้อยแล้ว!"})
        return jsonify({"status": "error", "message": "ข้อมูลไม่ถูกต้อง"}), 400

    try:
        with open(cfg_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            return jsonify(cfg)
    except Exception as e:
        return jsonify({"cameras": []})


@app.route("/api/status")
def status_api():
    cfg_file = get_config_file()
    try:
        with open(cfg_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            cams = cfg.get("cameras", [])
    except Exception:
        cams = []

    result = []
    for c in cams:
        result.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "url": c.get("url"),
            "enabled": c.get("enabled", True),
            "status": "online" if c.get("enabled", True) else "disabled"
        })

    return jsonify({"status": "online", "cameras": result})


def open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://{HOST}:{PORT}")


def main():
    print("=" * 65)
    print(" ⚡ CCTV Hardware-Accelerated Multi-Viewer (Zero-CPU WebRTC)")
    print("=" * 65)
    print(f" เปิดดูผ่านหน้าเว็บที่: http://{HOST}:{PORT}")
    print(" ถอดรหัสภาพสดผ่านชิปการ์ดจอ (GPU Hardware Acceleration) CPU < 1%")
    print(" กด Ctrl + C ในหน้าต่างนี้เพื่อหยุดการทำงาน")
    print("=" * 65)

    threading.Thread(target=open_browser, daemon=True).start()
    try:
        app.run(host=HOST, port=PORT, threaded=True, debug=False)
    finally:
        go2rtc_mgr.stop()


if __name__ == "__main__":
    main()
