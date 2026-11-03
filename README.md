# 📹 CCTV Multi-Viewer (Native Desktop & WebRTC)

[![GitHub Release](https://img.shields.io/github/v/release/gapsunzet1123/CCTV-local-web-TH?label=Latest%20Release&color=0ea5e9)](https://github.com/gapsunzet1123/CCTV-local-web-TH/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue)](https://github.com/gapsunzet1123/CCTV-local-web-TH/releases)
[![License](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)

ศูนย์รวมดูกล้องวงจรปิดความเร็วสูง **Zero-CPU Hardware Acceleration (WebRTC)** ถอดรหัสภาพผ่านชิปการ์ดจอ (GPU) โดยตรง กิน CPU ต่ำกว่า 1% เปิดขึ้นมาเป็น **หน้าต่างโปรแกรม Desktop ของตัวเองโดยตรง (Standalone Native App)** พร้อมระบบ System Tray ทำงานเบื้องหลังเงียบๆ และรองรับคลิกลากสลับตำแหน่งจอ (Drag & Drop) ได้อย่างอิสระ

A high-performance, ultra-low latency, zero-CPU native desktop viewer for multiple CCTV cameras (RTSP/WebRTC) with GPU hardware acceleration, Windows System Tray background app, and interactive drag-and-drop tile management.

---

## 📥 ดาวน์โหลดเวอร์ชันพร้อมใช้งาน (Download Ready-to-Run)

สำหรับผู้ใช้งานทั่วไปที่ต้องการเปิดใช้งานทันทีโดยไม่ต้องติดตั้งโปรแกรมหรือเขียนโค้ด:

👉 **[ดาวน์โหลดโปรแกรมเวอร์ชันล่าสุด (.ZIP) ที่หน้า Releases](https://github.com/gapsunzet1123/CCTV-local-web-TH/releases/latest)**

1. ดาวน์โหลดไฟล์ `CCTV-Viewer-v2.0.0-Windows.zip`
2. แตกไฟล์ (Extract All)
3. ดับเบิ้ลคลิก `CCTV-Viewer.exe` ใช้งานได้ทันที!

---

## ✨ คุณสมบัติเด่น (Features)

* 🖥️ **Native Desktop Window (จบในตัวมันเอง):** 
  * เปิดขึ้นมาเป็นหน้าต่างโปรแกรมของตัวเองโดยตรง (ไม่เปิด Google Chrome อีกต่อไป ไม่มีแถบ URL ไม่มีแท็บกวนใจ)
  * ใช้เอนจิน Microsoft Edge WebView2 ที่มีอยู่ใน Windows 10/11 ทันสมัย ลื่นไหล และปลอดภัย
* ⚡ **กิน CPU ต่ำกว่า 1% (Zero-CPU Hardware Acceleration):** สตรีมภาพสดผ่าน WebRTC Passthrough ให้การ์ดจอ (GPU) ถอดรหัสโดยตรง ไม่ใช้ CPU แปลงภาพซ้ำซ้อน
* 🔲 **System Tray & Minimize-to-Tray:** 
  * เมื่อกดปุ่มกากบาท `X` หน้าต่างจะซ่อนตัวลงข้างนาฬิกาเงียบๆ โดยไม่ตัดสัญญาณกล้อง
  * ดับเบิ้ลคลิกไอคอนกล้องที่ Tray เพื่อเรียกหน้าต่างแอปกลับขึ้นมาได้ทันทีแบบ Zero-Latency
  * เมนูคลิกขวา: เปิดหน้าต่างแอป, เปิดดูผ่านเบราว์เซอร์, สั่งเชื่อมต่อสัญญาณใหม่, และเริ่มทำงานพร้อมเปิด Windows (Autostart)
* 🔀 **คลิกลากจอสลับตำแหน่งได้อิสระ (Drag & Drop):** คลิกค้างที่แถบชื่อหัวกล้อง (มีสัญลักษณ์ `⠿`) แล้วลากไปปล่อยทับกล้องตัวอื่นเพื่อสลับตำแหน่งกันได้ทันที โดยวิดีโอไม่ดับและไม่กระตุก
* 🔲 **เลย์เอาต์หน้าจอสมดุล (Balanced Multi-View):**
  * **3 จอเท่ากัน:** สัดส่วนกว้าง x สูงเท่ากันเป๊ะ 100% สมดุลสบายตา
  * **3 จอแนวนอน:** เรียงเป็น 3 คอลัมน์ด้านข้าง
  * **1 จอหลัก + 2 จอข้าง:** จอซ้ายใหญ่สำหรับจุดสำคัญ + สามารถลากกล้องตัวไหนมาใส่เป็นจอใหญ่ก็ได้
* ➕ **เพิ่ม/ลดกล้องได้ไม่จำกัดผ่านหน้าต่างตั้งค่า:** มีหน้าต่างตั้งค่า (Settings Drawer) ให้เพิ่มกล้องตัวที่ 4, 5, 6... หรือลบออกได้ทันที ไม่ต้องแก้โค้ด
* 🛡️ **ความปลอดภัยสูงสุด (100% Local Privacy):** สัญญาณภาพวิ่งตรงจากกล้องในบ้าน (Local LAN) เข้าสู่โปรแกรมของคุณโดยตรง ไม่มีการส่งข้อมูลใดๆ ออกสู่อินเทอร์เน็ตภายนอก

---

## ⚙️ การตั้งค่ากล้องวงจรปิด (Configuration)

คุณสามารถตั้งค่าได้ 2 วิธี:
1. **ผ่านหน้าต่างแอปโดยตรง (แนะนำ):** กดปุ่ม **"⚙️ จัดการกล้อง & เพิ่มจอ"** ที่มุมขวาบน กรอกชื่อกล้องและ RTSP URL แล้วกดบันทึก
2. **ผ่านไฟล์ `cameras.json` หรือ `cameras.local.json`:** ใส่ URL กล้องลงในไฟล์การตั้งค่าในโฟลเดอร์โปรแกรม

### ตัวอย่างรูปแบบ RTSP URL ตามยี่ห้อกล้องยอดนิยม:

| ยี่ห้อกล้อง | รูปแบบ RTSP URL |
| :--- | :--- |
| **TP-Link Tapo** | `rtsp://[USER]:[PASS]@[IP]:554/stream1` (HD) หรือ `/stream2` (Substream ลื่นสุด) |
| **Hikvision / Ezviz** | `rtsp://[USER]:[PASS]@[IP]:554/Streaming/Channels/101` หรือ `102` |
| **Dahua / IMOU** | `rtsp://[USER]:[PASS]@[IP]:554/cam/realmonitor?channel=1&subtype=0` หรือ `subtype=1` |
| **V380 / ทั่วไป** | `rtsp://[USER]:[PASS]@[IP]:554/live/ch0` |

---

## 🛠️ สำหรับนักพัฒนา (Developer Guide & Build)

### การรันจาก Source Code:
```bash
pip install -r requirements.txt
python main.py
```

### การคอมไพล์เป็น Portable Application Folder:
```bash
pip install pyinstaller pystray pillow pywebview pythonnet backports.tarfile
pyinstaller --noconsole --onedir --clean --name "CCTV-Viewer" --icon "cctv_icon.ico" --add-data "web;web" --add-data "bin/go2rtc.exe;bin" --add-data "cctv_icon.ico;." --add-data "cctv_icon.png;." --add-data "cameras.json;." --hidden-import "pystray._win32" --collect-all "webview" --collect-all "clr_loader" --collect-all "pythonnet" main.py
```

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```
cctv-local-web/
├── bin/
│   └── go2rtc.exe            # WebRTC streaming engine (Hardware Accelerated)
├── web/
│   ├── static/
│   │   ├── app.js           # Frontend WebRTC & Drag & Drop controller
│   │   └── style.css        # Responsive dark theme CCTV styling
│   └── templates/
│       └── index.html       # Clean CCTV Dashboard template
├── cameras.json             # Camera configurations template
├── cctv_icon.ico            # Windows application icon
├── cctv_icon.png            # System Tray icon image
├── main.py                  # Standalone Native App & Tray entrypoint
├── start_cctv_web.bat       # 1-Click batch launcher script for Windows
├── web_server.py            # Local Flask web server & REST API
├── webrtc_manager.py        # WebRTC stream engine manager
└── README.md                # Project documentation
```

---

## 📄 ใบอนุญาต (License)
MIT License - สามารถนำไปใช้งาน พัฒนาต่อ หรือแจกจ่ายได้อย่างอิสระ
