/**
 * Face Liveness Detection - Web App
 * Mobile-first UX with coherent feedback & usability heuristics
 */

// ============================================
// STATE MANAGEMENT
// ============================================

const state = {
  model: "v2",
  threshold: 0.5,
  currentImage: null,
  isAnalyzing: false,
  cameraActive: false,
  videoStream: null,
  currentResult: null,
};

// ============================================
// DOM ELEMENTS
// ============================================

const elements = {
  // Tabs
  tabBtns: document.querySelectorAll(".tab-btn"),
  tabPanels: document.querySelectorAll(".tab-panel"),

  // Upload
  uploadArea: document.getElementById("upload-area"),
  fileInput: document.getElementById("file-input"),
  uploadPreview: document.getElementById("upload-preview"),
  previewImg: document.getElementById("preview-img"),
  clearUploadBtn: document.getElementById("clear-upload"),

  // Camera
  cameraVideo: document.getElementById("camera-video"),
  toggleCameraBtn: document.getElementById("toggle-camera"),
  captureBtn: document.getElementById("capture-btn"),
  cameraOverlay: document.querySelector(".camera-overlay"),
  cameraPreview: document.getElementById("camera-preview"),
  cameraPreviewImg: document.getElementById("camera-preview-img"),
  retakePhotoBtn: document.getElementById("retake-photo"),

  // Config
  modelSelect: document.getElementById("model-select"),
  thresholdSlider: document.getElementById("threshold-slider"),
  thresholdValue: document.getElementById("threshold-value"),

  // Result
  resultSection: document.getElementById("result-section"),
  resultContainer: document.getElementById("result-container"),
  analyzeAnotherBtn: document.getElementById("analyze-another"),

  // Status
  statusMessage: document.getElementById("status-message"),
  loadingSpinner: document.getElementById("loading-spinner"),
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Show status message with auto-dismiss
 */
function showStatus(message, type = "success", duration = 3000) {
  const status = elements.statusMessage;
  status.textContent = message;
  status.className = `status-message ${type}`;

  if (duration > 0) {
    setTimeout(() => {
      status.classList.add("hidden");
    }, duration);
  }
}

/**
 * Show loading spinner
 */
function showLoading() {
  elements.loadingSpinner.classList.remove("hidden");
  state.isAnalyzing = true;
}

/**
 * Hide loading spinner
 */
function hideLoading() {
  elements.loadingSpinner.classList.add("hidden");
  state.isAnalyzing = false;
}

/**
 * Switch to a tab
 */
function switchTab(tabName) {
  // Hide all panels
  elements.tabPanels.forEach((panel) => panel.classList.remove("active"));

  // Deactivate all buttons
  elements.tabBtns.forEach((btn) => btn.classList.remove("active"));

  // Show target panel
  const targetPanel = document.getElementById(`${tabName}-panel`);
  if (targetPanel) targetPanel.classList.add("active");

  // Activate target button
  const targetBtn = Array.from(elements.tabBtns).find(
    (btn) => btn.dataset.tab === tabName,
  );
  if (targetBtn) targetBtn.classList.add("active");
}

/**
 * Clear form state
 */
function clearForm() {
  state.currentImage = null;
  state.currentResult = null;
  elements.uploadPreview.classList.add("hidden");
  elements.resultSection.classList.add("hidden");
  elements.previewImg.src = "";
}

/**
 * Disable buttons during analysis
 */
function setButtonsDisabled(disabled) {
  elements.tabBtns.forEach((btn) => (btn.disabled = disabled));
  elements.analyzeAnotherBtn.disabled = disabled;
}

// ============================================
// TAB NAVIGATION
// ============================================

elements.tabBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const tabName = btn.dataset.tab;
    switchTab(tabName);

    // Heuristic: Feedback on tab change
    if (tabName === "camera" && !state.cameraActive) {
      showStatus('Camera ready. Tap "Start Camera" to begin.', "success", 2000);
    }
  });
});

// ============================================
// UPLOAD FUNCTIONALITY
// ============================================

// Click to upload
elements.uploadArea.addEventListener("click", () => {
  elements.fileInput.click();
});

// File selected
elements.fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) {
    handleFileUpload(file);
  }
});

// Drag and drop
elements.uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  e.stopPropagation();
  elements.uploadArea.classList.add("drag-active");
});

elements.uploadArea.addEventListener("dragleave", () => {
  elements.uploadArea.classList.remove("drag-active");
});

elements.uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  e.stopPropagation();
  elements.uploadArea.classList.remove("drag-active");

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    if (file.type.startsWith("image/")) {
      handleFileUpload(file);
    } else {
      showStatus("❌ Please upload an image file", "error", 3000);
    }
  }
});

// Heuristic: User control & system feedback
function handleFileUpload(file) {
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    showStatus("❌ File too large (max 10MB)", "error", 3000);
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    state.currentImage = e.target.result;
    elements.previewImg.src = state.currentImage;
    elements.uploadPreview.classList.remove("hidden");
    showStatus("✅ Image ready for analysis", "success", 2000);
    analyzeImage();
  };
  reader.onerror = () => {
    showStatus("❌ Error reading file", "error", 3000);
  };
  reader.readAsDataURL(file);
}

elements.clearUploadBtn.addEventListener("click", () => {
  clearForm();
  elements.fileInput.value = "";
  showStatus("Image cleared", "success", 1500);
});

// ============================================
// CAMERA FUNCTIONALITY
// ============================================

elements.toggleCameraBtn.addEventListener("click", async () => {
  if (!state.cameraActive) {
    await startCamera();
  } else {
    stopCamera();
  }
});

async function startCamera() {
  try {
    state.videoStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user" },
    });

    elements.cameraVideo.srcObject = state.videoStream;
    elements.cameraVideo.classList.add("active");
    elements.cameraOverlay.classList.add("active");
    elements.captureBtn.classList.add("active");

    elements.toggleCameraBtn.textContent = "🛑 Stop Camera";
    state.cameraActive = true;

    showStatus(
      "✅ Camera started. Frame your face in the circle.",
      "success",
      3000,
    );
  } catch (error) {
    showStatus("❌ Camera access denied. Check permissions.", "error", 3000);
    console.error("Camera error:", error);
  }
}

function stopCamera() {
  if (state.videoStream) {
    state.videoStream.getTracks().forEach((track) => track.stop());
    state.videoStream = null;
  }

  elements.cameraVideo.classList.remove("active");
  elements.cameraOverlay.classList.remove("active");
  elements.captureBtn.classList.remove("active");
  elements.toggleCameraBtn.textContent = "📷 Start Camera";
  state.cameraActive = false;

  showStatus("Camera stopped", "success", 1500);
}

// Capture photo
elements.captureBtn.addEventListener("click", () => {
  if (!state.cameraActive) return;

  const canvas = document.createElement("canvas");
  canvas.width = elements.cameraVideo.videoWidth;
  canvas.height = elements.cameraVideo.videoHeight;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(elements.cameraVideo, 0, 0);

  state.currentImage = canvas.toDataURL("image/jpeg", 0.9);
  elements.cameraPreviewImg.src = state.currentImage;
  elements.cameraPreview.classList.remove("hidden");

  stopCamera();
  showStatus("✅ Photo captured. Analyzing...", "success", 2000);
  analyzeImage();
});

elements.retakePhotoBtn.addEventListener("click", async () => {
  elements.cameraPreview.classList.add("hidden");
  elements.cameraPreviewImg.src = "";
  state.currentImage = null;
  await startCamera();
});

// ============================================
// CONFIGURATION
// ============================================

elements.modelSelect.addEventListener("change", (e) => {
  state.model = e.target.value;
  showStatus(`Model switched to ${state.model}`, "success", 2000);
});

elements.thresholdSlider.addEventListener("input", (e) => {
  state.threshold = parseFloat(e.target.value);
  elements.thresholdValue.textContent = state.threshold.toFixed(2);
});

// ============================================
// ANALYSIS & RESULTS
// ============================================

async function analyzeImage() {
  if (!state.currentImage || state.isAnalyzing) return;

  showLoading();
  setButtonsDisabled(true);

  try {
    // Simulate API call (replace with real backend)
    await simulateAnalysis();

    // Display results
    displayResult(state.currentResult);
    showStatus("✅ Analysis complete", "success", 2000);
  } catch (error) {
    showStatus(`❌ Analysis failed: ${error.message}`, "error", 3000);
    console.error("Analysis error:", error);
  } finally {
    hideLoading();
    setButtonsDisabled(false);
  }
}

/**
 * Call backend API for analysis
 */
async function simulateAnalysis() {
  const API_URL = "/api/analyze";

  const payload = {
    image: state.currentImage,
    model: state.model,
    threshold: state.threshold,
  };

  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Analysis failed");
  }

  const result = await response.json();

  state.currentResult = {
    label: result.label,
    confidence: result.confidence,
    detectionTime: result.detectionTime,
    classificationTime: result.classificationTime,
    totalTime: result.totalTime,
    annotatedImage: result.annotatedImage,
    facesDetected: result.facesDetected,
    faces: result.faces,
  };
}

/**
 * Display result with clear feedback
 * Heuristic: Match system status with user expectations
 */
function displayResult(result) {
  const isReal = result.label === "Real";
  const confidence = result.confidence;

  let html = `
        <div class="result-verdict ${isReal ? "success" : "danger"}">
            <div class="result-icon">${isReal ? "✅" : "⚠️"}</div>
            <div class="result-label ${isReal ? "success" : "danger"}">
                ${isReal ? "Authentic Face" : "Presentation Attack"}
            </div>
            <div class="result-confidence">
                Confidence: ${(confidence * 100).toFixed(1)}%
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${confidence * 100}%"></div>
            </div>
        </div>

        <div class="result-details">
            <div class="result-item">
                <span class="result-item-label">Detection Time</span>
                <span class="result-item-value">${result.detectionTime.toFixed(0)} ms</span>
            </div>
            <div class="result-item">
                <span class="result-item-label">Classification Time</span>
                <span class="result-item-value">${result.classificationTime.toFixed(0)} ms</span>
            </div>
            <div class="result-item">
                <span class="result-item-label">Total Time</span>
                <span class="result-item-value">${(result.detectionTime + result.classificationTime).toFixed(0)} ms</span>
            </div>
            <div class="result-item">
                <span class="result-item-label">Model</span>
                <span class="result-item-value">${state.model.toUpperCase()}</span>
            </div>
            <div class="result-item">
                <span class="result-item-label">Threshold</span>
                <span class="result-item-value">${state.threshold.toFixed(2)}</span>
            </div>
        </div>

        <img src="${result.annotatedImage}" alt="Annotated result" class="result-image">
    `;

  elements.resultContainer.innerHTML = html;
  elements.resultSection.classList.remove("hidden");
}

elements.analyzeAnotherBtn.addEventListener("click", () => {
  clearForm();
  switchTab("upload");
  showStatus("Ready for another analysis", "success", 2000);
});

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener("DOMContentLoaded", () => {
  showStatus(
    "👋 Welcome! Upload an image or use camera to get started.",
    "success",
    3000,
  );
});

// Heuristic: Prevent accidental loss of work
window.addEventListener("beforeunload", (e) => {
  if (state.isAnalyzing) {
    e.preventDefault();
    e.returnValue = "";
  }
});
