# 📹 CCTV Local Web (Multi-View Monitoring)

ระบบศูนย์รวมดูกล้องวงจรปิดผ่านเว็บเบราว์เซอร์ความเร็วสูง **Zero-CPU Hardware Acceleration (WebRTC)** ถอดรหัสภาพผ่านชิปการ์ดจอ (GPU) โดยตรง กิน CPU ต่ำกว่า 1% พร้อมระบบคลิกลากสลับตำแหน่งจอ (Drag & Drop) และปรับแต่งเลย์เอาต์หน้าจอได้อิสระ

A high-performance, ultra-low latency, zero-CPU local web viewer for multiple CCTV cameras (RTSP/WebRTC) with GPU hardware acceleration and interactive drag-and-drop tile management.

---

## ✨ คุณสมบัติเด่น (Features)

* ⚡ **กิน CPU ต่ำกว่า 1% (Zero-CPU Hardware Acceleration):** สตรีมภาพผ่าน WebRTC Direct Passthrough ให้การ์ดจอ (GPU) ของเครื่องถอดรหัสโดยตรง ไม่ใช้ CPU แปลงภาพซ้ำซ้อน
* 🔀 **คลิกลากจอสลับตำแหน่งได้อิสระ (Drag & Drop):** คลิกค้างที่แถบชื่อหัวกล้อง (มีสัญลักษณ์ `⠿`) แล้วลากไปปล่อยทับกล้องตัวอื่นเพื่อสลับตำแหน่งกันได้ทันที โดยวิดีโอไม่ดับและไม่กระตุก
* 🔲 **เลย์เอาต์หน้าจอสมดุล (Balanced Multi-View):**
  * **3 จอเท่ากัน:** สัดส่วนกว้าง x สูงเท่ากันเป๊ะ 100% สมดุลสบายตา
  * **3 จอแนวนอน:** เรียงเป็น 3 คอลัมน์ด้านข้าง
  * **1 จอหลัก + 2 จอข้าง:** จอซ้ายใหญ่สำหรับจุดสำคัญ + สามารถลากกล้องตัวไหนมาใส่เป็นจอใหญ่ก็ได้
* 📐 **ปรับสเกลภาพ (Fit / Fill):** สลับระหว่างโหมดเต็มกรอบไร้ขอบดำ (Cover) หรือโหมดพอดีมุมกล้องเดิม (Contain)
* ➕ **เพิ่ม/ลดกล้องได้ไม่จำกัดผ่านหน้าเว็บ:** มีหน้าต่างตั้งค่า (Settings Drawer) ให้เพิ่มกล้องตัวที่ 4, 5, 6... หรือลบออกได้ทันที ไม่ต้องแก้โค้ด
* 🛡️ **ความปลอดภัยสูงสุด (100% Local Privacy):** สัญญาณภาพวิ่งตรงจากกล้องในบ้าน (Local LAN) เข้าสู่เบราว์เซอร์ของคุณโดยตรง ไม่มีการส่งข้อมูลใดๆ ออกสู่อินเทอร์เน็ตภายนอก

---

## 🚀 วิธีเริ่มต้นใช้งาน (Quick Start)

### สำหรับ Windows:
ดับเบิ้ลคลิกไฟล์:
> **`start_cctv_web.bat`**

ระบบจะเริ่มทำงานและเปิดหน้าเว็บขึ้นมาที่ `http://localhost:5000` โดยอัตโนมัติ

---

## ⚙️ การตั้งค่ากล้องวงจรปิด (Configuration)

คุณสามารถตั้งค่าได้ 2 วิธี:
1. **ผ่านหน้าเว็บโดยตรง (แนะนำ):** กดปุ่ม **"⚙️ จัดการกล้อง & เพิ่มจอ"** ที่มุมขวาบนของหน้าเว็บ กรอกชื่อกล้องและ RTSP URL แล้วกดบันทึก
2. **ผ่านไฟล์ `cameras.json`:** แก้ไขไฟล์ `cameras.json` ในโฟลเดอร์โครงการ

### ตัวอย่างรูปแบบ RTSP URL ตามยี่ห้อกล้องยอดนิยม:

| ยี่ห้อกล้อง | รูปแบบ RTSP URL |
| :--- | :--- |
| **TP-Link Tapo** | `rtsp://[USER]:[PASS]@[IP]:554/stream1` (HD) หรือ `/stream2` (Substream ลื่นสุด) |
| **Hikvision / Ezviz** | `rtsp://[USER]:[PASS]@[IP]:554/Streaming/Channels/101` หรือ `102` |
| **Dahua / IMOU** | `rtsp://[USER]:[PASS]@[IP]:554/cam/realmonitor?channel=1&subtype=0` หรือ `subtype=1` |
| **V380 / ทั่วไป** | `rtsp://[USER]:[PASS]@[IP]:554/live/ch0` |

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
│       └── index.html       # Web dashboard
├── cameras.json             # Camera configurations template
├── start_cctv_web.bat       # 1-Click launcher script for Windows
├── web_server.py            # Local Flask web server
├── webrtc_manager.py        # Stream synchronization manager
└── README.md                # Project documentation
```

---

## 📄 ใบอนุญาต (License)

โปรเจกต์นี้เผยแพร่ภายใต้ใบอนุญาต [MIT License](LICENSE) สามารถนำไปใช้งาน ปรับแต่ง หรือต่อยอดได้อย่างอิสระ
