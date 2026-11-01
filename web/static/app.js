let currentLayout = localStorage.getItem("cctv_layout") || "balanced";
let focusedCamId = null;
let activeInputIdForPreset = 1;
let currentCameras = [];
let draggedCamId = null;

// DOM Elements
const body = document.body;
const liveClock = document.getElementById("live-clock");
const videoStage = document.getElementById("video-stage");
const layoutButtons = document.querySelectorAll(".layout-btn");
const btnFullscreen = document.getElementById("btn-fullscreen");
const btnOpenSettings = document.getElementById("btn-open-settings");
const btnCloseSettings = document.getElementById("btn-close-settings");
const btnCancelSettings = document.getElementById("btn-cancel-settings");
const btnSaveSettings = document.getElementById("btn-save-settings");
const btnAddCamera = document.getElementById("btn-add-camera");
const settingsDrawer = document.getElementById("settings-drawer");
const drawerBackdrop = document.getElementById("drawer-backdrop");
const cameraSettingsList = document.getElementById("camera-settings-list");
const toastContainer = document.getElementById("toast-container");

// Real-time Clock
function updateClock() {
  const now = new Date();
  liveClock.textContent = now.toTimeString().split(" ")[0];
}
setInterval(updateClock, 1000);
updateClock();

// Layout Switcher
function setLayout(layoutName) {
  currentLayout = layoutName;
  localStorage.setItem("cctv_layout", layoutName);

  body.classList.remove("layout-balanced", "layout-columns", "layout-focus");
  body.classList.add(`layout-${layoutName}`);

  layoutButtons.forEach(btn => {
    if (btn.dataset.layout === layoutName) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  if (focusedCamId !== null) {
    exitFocusMode();
  }
  applyGridLayoutClass();
}

layoutButtons.forEach(btn => {
  btn.addEventListener("click", () => setLayout(btn.dataset.layout));
});

function applyGridLayoutClass() {
  const activeCount = document.querySelectorAll(".camera-tile").length;
  body.classList.remove("cams-1", "cams-2", "cams-3", "cams-4", "cams-5", "cams-6", "cams-many");

  if (activeCount === 1) body.classList.add("cams-1");
  else if (activeCount === 2) body.classList.add("cams-2");
  else if (activeCount === 3) body.classList.add("cams-3");
  else if (activeCount === 4) body.classList.add("cams-4");
  else if (activeCount <= 6) body.classList.add("cams-6");
  else body.classList.add("cams-many");
}

// ----------------------------------------------------
// Order Persistence (for Drag & Drop)
// ----------------------------------------------------
function getSavedOrder() {
  try {
    const saved = localStorage.getItem("cctv_order");
    return saved ? JSON.parse(saved) : null;
  } catch (e) {
    return null;
  }
}

function saveOrder(ids) {
  try {
    localStorage.setItem("cctv_order", JSON.stringify(ids));
  } catch (e) {}
}

// ----------------------------------------------------
// Render Video Tiles (Hardware Accelerated via go2rtc)
// ----------------------------------------------------
function renderVideoTiles(cameras) {
  const activeCameras = cameras.filter(c => c.enabled !== false);
  const savedOrder = getSavedOrder();

  if (savedOrder && Array.isArray(savedOrder)) {
    activeCameras.sort((a, b) => {
      const idxA = savedOrder.indexOf(a.id);
      const idxB = savedOrder.indexOf(b.id);
      if (idxA === -1) return 1;
      if (idxB === -1) return -1;
      return idxA - idxB;
    });
  }

  const existingTileIds = new Set(Array.from(document.querySelectorAll(".camera-tile")).map(t => parseInt(t.dataset.id)));
  const newTileIds = new Set(activeCameras.map(c => c.id));
  const isIdentical = existingTileIds.size === newTileIds.size && [...existingTileIds].every(id => newTileIds.has(id));

  if (!isIdentical) {
    videoStage.innerHTML = "";
    if (activeCameras.length === 0) {
      videoStage.innerHTML = `
        <div style="grid-column: 1/-1; display:flex; flex-direction:column; align-items:center; justify-content:center; color:var(--text-muted); gap:12px;">
          <span style="font-size:36px;">📷</span>
          <p>ยังไม่มีกล้องที่เปิดใช้งาน</p>
          <button class="btn btn-primary" onclick="openSettings()">กดที่นี่เพื่อเพิ่มหรือเปิดใช้งานกล้อง</button>
        </div>`;
      return;
    }

    activeCameras.forEach(cam => {
      const tile = document.createElement("div");
      tile.className = "camera-tile";
      tile.id = `tile-cam-${cam.id}`;
      tile.dataset.id = cam.id;
      tile.draggable = true;

      // Reliable hardware-accelerated WebRTC stream
      tile.innerHTML = `
        <div class="tile-bar">
          <div class="tile-title-group">
            <span class="drag-grip" title="คลิกค้างแล้วลากเพื่อสลับตำแหน่งจอ">⠿</span>
            <span class="cam-dot"></span>
            <strong class="cam-name" id="name-${cam.id}">${escapeHtml(cam.name || 'กล้อง ' + cam.id)}</strong>
            <span class="cam-hw-badge">GPU HW</span>
          </div>
          <div class="tile-actions">
            <button class="btn-tile-action" title="รีเฟรชกล้องนี้" onclick="reloadFeed(${cam.id})">🔄</button>
            <button class="btn-tile-action btn-expand" title="ขยายเฉพาะกล้องนี้" onclick="toggleFocus(${cam.id})">⛶</button>
          </div>
        </div>
        <div class="video-container">
          <iframe 
            src="http://127.0.0.1:1984/webrtc.html?src=cam${cam.id}&media=video" 
            class="video-feed-frame" 
            id="feed-frame-${cam.id}"
            frameborder="0" 
            scrolling="no"
            allow="autoplay; fullscreen">
          </iframe>
        </div>
      `;

      attachDragEvents(tile);
      videoStage.appendChild(tile);
    });
  } else {
    activeCameras.forEach(cam => {
      const nameEl = document.getElementById(`name-${cam.id}`);
      if (nameEl) nameEl.textContent = cam.name || `กล้อง ${cam.id}`;
    });
  }

  applyGridLayoutClass();
}

// ----------------------------------------------------
// HTML5 Drag and Drop Swapping Logic
// ----------------------------------------------------
function attachDragEvents(tile) {
  tile.addEventListener("dragstart", (e) => {
    draggedCamId = parseInt(tile.dataset.id);
    tile.classList.add("dragging");
    // Disable iframe pointer events during drag so drop is smooth
    body.classList.add("is-dragging");
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", draggedCamId);
  });

  tile.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    if (!tile.classList.contains("dragging")) {
      tile.classList.add("drag-over");
    }
  });

  tile.addEventListener("dragleave", () => {
    tile.classList.remove("drag-over");
  });

  tile.addEventListener("drop", (e) => {
    e.preventDefault();
    tile.classList.remove("drag-over");
    body.classList.remove("is-dragging");
    const targetCamId = parseInt(tile.dataset.id);

    if (draggedCamId && draggedCamId !== targetCamId) {
      swapCameraTiles(draggedCamId, targetCamId);
    }
  });

  tile.addEventListener("dragend", () => {
    body.classList.remove("is-dragging");
    document.querySelectorAll(".camera-tile").forEach(t => {
      t.classList.remove("dragging", "drag-over");
    });
    draggedCamId = null;
  });
}

function swapCameraTiles(camIdA, camIdB) {
  const tileA = document.getElementById(`tile-cam-${camIdA}`);
  const tileB = document.getElementById(`tile-cam-${camIdB}`);

  if (!tileA || !tileB) return;

  const parent = tileA.parentNode;
  const nextSiblingA = tileA.nextSibling === tileB ? tileA : tileA.nextSibling;

  // Swap DOM positions seamlessly without restarting WebRTC stream
  parent.insertBefore(tileA, tileB);
  parent.insertBefore(tileB, nextSiblingA);

  const newOrder = Array.from(document.querySelectorAll(".camera-tile")).map(t => parseInt(t.dataset.id));
  saveOrder(newOrder);

  const nameA = tileA.querySelector(".cam-name")?.textContent || `กล้อง ${camIdA}`;
  const nameB = tileB.querySelector(".cam-name")?.textContent || `กล้อง ${camIdB}`;
  showToast(`🔀 สลับตำแหน่ง: ${nameA} ⇄ ${nameB} เรียบร้อย!`, "success");
}

// Reload single feed
window.reloadFeed = function(camId) {
  const frame = document.getElementById(`feed-frame-${camId}`);
  if (frame) {
    frame.src = `http://127.0.0.1:1984/webrtc.html?src=cam${camId}&media=video&t=${Date.now()}`;
    showToast(`รีเฟรชสัญญาณกล้องที่ ${camId} เรียบร้อย`, "info");
  }
};

// Focus Mode (Maximize Single Camera on click)
window.toggleFocus = function(camId) {
  if (focusedCamId === camId) {
    exitFocusMode();
  } else {
    enterFocusMode(camId);
  }
};

function enterFocusMode(camId) {
  focusedCamId = camId;
  body.classList.add("focus-mode-active");

  document.querySelectorAll(".camera-tile").forEach(tile => {
    tile.classList.remove("focused");
  });

  const targetTile = document.getElementById(`tile-cam-${camId}`);
  if (targetTile) {
    targetTile.classList.add("focused");
  }

  showToast(`ขยายกล้องที่ ${camId} จอใหญ่ (คลิก ⛶ อีกครั้งเพื่อกลับสู่ตารางรวม)`, "info");
}

function exitFocusMode() {
  focusedCamId = null;
  body.classList.remove("focus-mode-active");
  document.querySelectorAll(".camera-tile").forEach(tile => {
    tile.classList.remove("focused");
  });
}

// Fullscreen Browser
btnFullscreen.addEventListener("click", () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {});
  } else {
    document.exitFullscreen().catch(() => {});
  }
});

// Load Cameras from API
async function loadCameras() {
  try {
    const res = await fetch("/api/status");
    if (!res.ok) return;
    const data = await res.json();
    if (data.cameras) {
      currentCameras = data.cameras;
      renderVideoTiles(data.cameras);
    }
  } catch (err) {}
}

// Settings Drawer Management
async function openSettings() {
  try {
    const res = await fetch("/api/config");
    const data = await res.json();
    currentCameras = data.cameras || [];
    renderSettingsList();
  } catch (err) {
    showToast("ไม่สามารถโหลดการตั้งค่าได้", "error");
  }
  settingsDrawer.classList.add("open");
  drawerBackdrop.classList.add("open");
}

function closeSettings() {
  settingsDrawer.classList.remove("open");
  drawerBackdrop.classList.remove("open");
}

btnOpenSettings.addEventListener("click", openSettings);
btnCloseSettings.addEventListener("click", closeSettings);
btnCancelSettings.addEventListener("click", closeSettings);
drawerBackdrop.addEventListener("click", closeSettings);

function renderSettingsList() {
  cameraSettingsList.innerHTML = "";
  if (currentCameras.length === 0) {
    cameraSettingsList.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-muted);">ไม่มีกล้องในระบบ กดปุ่มด้านบนเพื่อเพิ่มกล้อง</div>`;
    return;
  }

  currentCameras.forEach(cam => {
    const card = document.createElement("div");
    card.className = "cam-setting-card";
    card.id = `setting-card-${cam.id}`;

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <strong style="color:var(--accent-cyan); font-size:13px;">กล้องที่ ${cam.id}</strong>
        <div style="display:flex; align-items:center; gap:12px;">
          <label style="font-size:12px; color:var(--text-muted); cursor:pointer;">
            <input type="checkbox" class="setting-cam-enabled" data-id="${cam.id}" ${cam.enabled !== false ? 'checked' : ''}> เปิดใช้งาน
          </label>
          <button class="btn-card-del" title="ลบกล้องนี้" onclick="deleteCameraFromSettings(${cam.id})">🗑️</button>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">ชื่อกล้อง:</label>
        <input type="text" class="form-input setting-cam-name" data-id="${cam.id}" value="${escapeHtml(cam.name || '')}" placeholder="เช่น หน้าบ้าน, หน้าห้อง">
      </div>

      <div class="form-group">
        <label class="form-label">RTSP Stream URL:</label>
        <input type="text" class="form-input font-mono setting-cam-url" data-id="${cam.id}" value="${escapeHtml(cam.url || '')}" onfocus="activeInputIdForPreset = ${cam.id}" placeholder="rtsp://admin:pass@192.168.1.x:554/stream2">
      </div>
    `;
    cameraSettingsList.appendChild(card);
  });
}

// Add New Camera
btnAddCamera.addEventListener("click", () => {
  const nextId = currentCameras.length > 0 ? Math.max(...currentCameras.map(c => c.id)) + 1 : 1;
  currentCameras.push({
    id: nextId,
    name: `กล้อง ${nextId}`,
    url: "rtsp://admin:admin123@192.168.1.100:554/stream1",
    enabled: true
  });
  renderSettingsList();
  showToast(`เพิ่มกล้องที่ ${nextId} เรียบร้อย กรุณาใส่ RTSP URL แล้วกดบันทึก`, "info");
});

// Delete Camera
window.deleteCameraFromSettings = function(camId) {
  if (confirm(`คุณแน่ใจหรือไม่ว่าต้องการลบกล้องที่ ${camId}?`)) {
    currentCameras = currentCameras.filter(c => c.id !== camId);
    renderSettingsList();
    showToast(`ลบกล้องที่ ${camId} ออกแล้ว อย่าลืมกดบันทึกการตั้งค่า`, "info");
  }
};

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

window.fillPresetTemplate = function(template) {
  const input = document.querySelector(`.setting-cam-url[data-id="${activeInputIdForPreset}"]`);
  if (input) {
    input.value = template;
    showToast(`ใส่ตัวอย่าง URL ในกล้องที่ ${activeInputIdForPreset} เรียบร้อย`, "info");
  }
};

btnSaveSettings.addEventListener("click", async () => {
  const updatedCameras = [];
  currentCameras.forEach(cam => {
    const nameInput = document.querySelector(`.setting-cam-name[data-id="${cam.id}"]`);
    const urlInput = document.querySelector(`.setting-cam-url[data-id="${cam.id}"]`);
    const enabledInput = document.querySelector(`.setting-cam-enabled[data-id="${cam.id}"]`);

    updatedCameras.push({
      id: cam.id,
      name: nameInput ? nameInput.value.trim() : cam.name,
      url: urlInput ? urlInput.value.trim() : cam.url,
      enabled: enabledInput ? enabledInput.checked : true
    });
  });

  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cameras: updatedCameras })
    });
    const data = await res.json();
    if (res.ok) {
      showToast("บันทึกและเชื่อมต่อสัญญาณใหม่สำเร็จ!", "success");
      closeSettings();
      setTimeout(loadCameras, 800);
    } else {
      showToast(data.message || "เกิดข้อผิดพลาดในการบันทึก", "error");
    }
  } catch (err) {
    showToast("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้", "error");
  }
});

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = "toast";
  if (type === "success") toast.style.borderColor = "var(--accent-green)";
  if (type === "error") toast.style.borderColor = "var(--accent-red)";
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Initial Run
setLayout(currentLayout);
loadCameras();
