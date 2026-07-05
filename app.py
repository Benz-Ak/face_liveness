import cv2
import numpy as np
import streamlit as st
from PIL import Image
from pathlib import Path
import time

from src.pipeline import LivenessPipeline

# Mobile-first configuration
st.set_page_config(
    page_title="Face Liveness Detection",
    page_icon="🔍",
    layout="centered",  # Mobile-first: single column
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        /* Mobile-first responsive design */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body, .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1a202c 100%);
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        /* Header: Simple and clear */
        .header-container {
            text-align: center;
            padding: 1.5rem 1rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(6, 182, 212, 0.2);
        }

        .header-title {
            font-size: 1.75rem;
            font-weight: 800;
            color: #38bdf8;
            margin: 0.5rem 0;
        }

        .header-subtitle {
            font-size: 0.95rem;
            color: #94a3b8;
            margin: 0.25rem 0;
        }

        /* Cards: Consistent styling */
        .card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(20, 30, 48, 0.4));
            border: 1px solid rgba(6, 182, 212, 0.2);
            border-radius: 1rem;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #cbd5e1;
            margin-bottom: 0.75rem;
        }

        /* Verdict styling: Clear color feedback */
        .verdict-success {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.1));
            border-left: 5px solid #10b981;
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin: 1rem 0;
            text-align: center;
        }

        .verdict-danger {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(249, 115, 115, 0.1));
            border-left: 5px solid #ef4444;
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin: 1rem 0;
            text-align: center;
        }

        .verdict-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        .verdict-label {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .verdict-success .verdict-label { color: #10b981; }
        .verdict-danger .verdict-label { color: #ef4444; }

        /* Progress bar styling */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #0ea5e9, #10b981) !important;
            height: 8px !important;
            border-radius: 4px !important;
        }

        /* Metrics: Simple and readable */
        [data-testid="stMetric"] {
            background: rgba(6, 182, 212, 0.08);
            border: 1px solid rgba(6, 182, 212, 0.2);
            border-radius: 0.75rem;
            padding: 1rem;
            text-align: center;
        }

        /* Tabs: Mobile-friendly */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            border-bottom: 2px solid rgba(6, 182, 212, 0.2);
            background: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px;
            border-radius: 0.5rem;
            padding: 0 1rem;
            background: rgba(30, 41, 59, 0.4);
            color: #94a3b8;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0ea5e9, #06b6d4);
            color: white;
        }

        /* Buttons: Touch-friendly sizing */
        .stButton > button {
            width: 100%;
            height: 48px;
            border-radius: 0.5rem;
            font-weight: 600;
            font-size: 1rem;
        }

        /* Status messages styling */
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 0.75rem;
            padding: 1rem;
            margin: 0.75rem 0;
        }

        /* File uploader: Mobile-friendly */
        [data-testid="stFileUploadDropzone"] {
            border-radius: 1rem;
            border: 2px dashed rgba(14, 165, 233, 0.5);
            background: rgba(6, 182, 212, 0.05);
            padding: 2rem 1rem;
            text-align: center;
        }

        /* Sidebar: Config section */
        .sidebar-config {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(6, 182, 212, 0.2);
            border-radius: 0.75rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        /* Result card styling */
        .result-face-card {
            background: rgba(6, 182, 212, 0.08);
            border-left: 4px solid #0ea5e9;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }

        /* Caption: Help text */
        .caption {
            font-size: 0.85rem;
            color: #94a3b8;
            margin: 0.5rem 0;
        }

        /* Responsive: Mobile optimization */
        @media (max-width: 640px) {
            .header-title { font-size: 1.5rem; }
            .stTabs [data-baseweb="tab"] { font-size: 0.8rem; padding: 0 0.75rem; }
            [data-testid="stMetric"] { min-width: 100%; margin-bottom: 0.75rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_pipeline(weights_path, threshold):
    """Load and cache the liveness detection pipeline"""
    return LivenessPipeline(weights_path=weights_path, threshold=threshold)


def convert_to_bgr(uploaded_file):
    """Convert uploaded image to BGR format for processing"""
    pil_img = Image.open(uploaded_file).convert("RGB")
    np_img = np.array(pil_img)
    bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
    print("=" * 50)
    print("Original image shape :", bgr_img.shape)
    print("Image dtype :", bgr_img.dtype)
    print("=" * 50)
    return pil_img, bgr_img


def display_result(output):
    """Display analysis result with coherent feedback"""
    results = output["results"]
    latency = output["latency"]
    annotated = output["annotated_frame"]
    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    # Show annotated image
    st.image(annotated_rgb, caption="Detected faces (annotated)", use_container_width=True)

    # Check if faces detected (Nielsen: System visibility - always inform user)
    if not results:
        st.warning("⚠️ No faces detected. Try a clearer image with visible face.")
        return

    # Determine overall verdict
    overall_verdict = "AUTHENTIC" if all(res["label"] == "Real" for res in results) else "SPOOF"
    is_real = overall_verdict == "AUTHENTIC"

    # Display verdict with clear, color-coded feedback
    if is_real:
        with st.container():
            st.markdown(
                """
                <div class="verdict-success">
                    <div class="verdict-icon">✅</div>
                    <div class="verdict-label">Authentic Face</div>
                    <div style="font-size: 0.95rem; color: #94a3b8;">Face is genuine</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        with st.container():
            st.markdown(
                """
                <div class="verdict-danger">
                    <div class="verdict-icon">⚠️</div>
                    <div class="verdict-label">Presentation Attack Detected</div>
                    <div style="font-size: 0.95rem; color: #94a3b8;">Spoof or non-genuine face</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Display individual face results
    st.subheader("Face Results")
    for i, res in enumerate(results, start=1):
        label = res["label"]
        confidence = float(res["confidence"])
        
        st.markdown(
            f"""
            <div class="result-face-card">
                <strong>Face {i}:</strong> {label} (Confidence: {confidence:.1%})
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(confidence, text=f"{confidence:.0%} confident")

    # Display latency metrics
    st.divider()
    st.subheader("⏱️ Performance")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Detection", f"{latency.get('detection_ms', 0):.0f} ms")
    with col2:
        st.metric("Classification", f"{latency.get('classification_ms', 0):.0f} ms")
    with col3:
        st.metric("Total", f"{latency.get('total_ms', 0):.0f} ms")


# ============================================
# SIDEBAR CONFIGURATION
# ============================================

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.divider()

    model_choice = st.radio(
        "Select Model",
        [
            ("V1 – NUAA only", "v1"),
            ("V2 – Better generalization", "v2"),
        ],
        format_func=lambda x: x[0],
        help="V2 performs better on unseen data",
    )
    model_value = model_choice[1] if isinstance(model_choice, tuple) else model_choice

    weights_map = {
        "v1": "models/best_checkpoint.pth",
        "v2": "models/best_checkpoint_v2.pth",
    }
    weights_path = weights_map[model_value]

    threshold = st.slider(
        "Confidence Threshold",
        min_value=0.3,
        max_value=0.9,
        value=0.5,
        step=0.05,
        help="Higher threshold = stricter (requires higher confidence for 'Real')",
    )

    st.divider()
    st.markdown("### 📊 Model Performance")
    if "v1" in model_value:
        st.metric("NUAA F1 Score", "0.9957")
        st.metric("NUAA HTER", "0.0044")
        st.caption("⚠️ Lower cross-domain performance")
    else:
        st.metric("NUAA F1 Score", "0.9979")
        st.metric("NUAA HTER", "0.0023")
        st.metric("LCC F1 Score", "0.8721")
        st.caption("✅ Best overall performance")

    st.divider()
    st.markdown("### ℹ️ About")
    st.caption(
        "**Face Liveness Detection**  \n"
        "Anti-spoofing system using MTCNN + MobileNetV2  \n"
        "M1 Cybersecurity — University of Buea"
    )


# ============================================
# MAIN CONTENT
# ============================================

# Header (Simple and clear)
st.markdown(
    """
    <div class="header-container">
        <div class="header-title">🔍 Face Liveness</div>
        <div class="header-subtitle">Detect authentic faces</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Check if model exists
checkpoint = Path(weights_path)
if not checkpoint.exists():
    st.error(f"❌ Model not found: {weights_path}")
    st.info("Place the checkpoint file in the `models/` folder to continue.")
    st.stop()

# Load pipeline
pipeline = load_pipeline(weights_path, threshold)
st.success(f"✅ Model loaded: {model_choice[0]}")

# Input tabs
upload_tab, camera_tab, guide_tab = st.tabs(["📁 Upload", "📷 Camera", "ℹ️ Guide"])

# ============================================
# TAB 1: UPLOAD IMAGE
# ============================================

with upload_tab:
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Upload Image</div>
            <div class="caption">JPG, PNG • Max 10MB</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        # Show preview
        try:
            pil_img, bgr_img = convert_to_bgr(uploaded_file)
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(pil_img, caption="Original", use_container_width=True)
            with col2:
                st.markdown("**Analysis running...**")
                with st.spinner("Processing image..."):
                    output = pipeline.run(bgr_img)
                st.caption("✅ Analysis complete")

            st.divider()
            display_result(output)

            # Action buttons (Nielsen: User control)
            if st.button("📁 Upload Another", key="upload_another", use_container_width=True):
                st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.caption("Try a different image or check file format.")


# ============================================
# TAB 2: WEBCAM CAPTURE
# ============================================

with camera_tab:
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Capture from Camera</div>
            <div class="caption">Analyze in real-time</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    img_data = st.camera_input("Take a photo")

    if img_data is not None:
        try:
            pil_img = Image.open(img_data).convert("RGB")
            np_img = np.array(pil_img)
            bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

            st.markdown("**Analysis running...**")
            with st.spinner("Processing capture..."):
                output = pipeline.run(bgr_img)
            st.caption("✅ Analysis complete")

            st.divider()
            display_result(output)

            # Action buttons
            if st.button("📷 Take Another Photo", key="camera_another", use_container_width=True):
                st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.caption("Try capturing again.")


# ============================================
# TAB 3: GUIDE
# ============================================

with guide_tab:
    st.markdown(
        """
        <div class="card">
            <div class="card-title">How to Use</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📸 Upload Image", expanded=True):
        st.markdown(
            """
            1. Click "Upload Image" tab
            2. Select a JPG or PNG file
            3. Wait for analysis
            4. Review verdict and confidence
            """
        )

    with st.expander("📷 Camera"):
        st.markdown(
            """
            1. Click "Camera" tab
            2. Click camera icon to capture
            3. Frame face clearly
            4. Click capture button
            5. Wait for analysis
            """
        )

    with st.expander("⚙️ Configuration"):
        st.markdown(
            """
            - **Model**: V1 (faster) or V2 (more accurate)
            - **Threshold**: Higher = stricter detection
            - Adjust in the sidebar
            """
        )

    st.divider()

    with st.expander("💡 Best Practices"):
        st.markdown(
            """
            ✅ **Good conditions:**
            - Good lighting, no harsh shadows
            - Face clearly visible and centered
            - Camera at eye level or slightly above
            - Natural expression
            
            ❌ **Avoid:**
            - Dark, backlit images
            - Partial face crop
            - Extreme angles
            - Blurred or low-res images
            """
        )

    with st.expander("📊 Model Info"):
        st.markdown(
            """
            **V1 - NUAA Dataset:**
            - Fast inference
            - Best for same dataset
            
            **V2 - NUAA + LCC FASD:**
            - Slower but more accurate
            - Better on unknown data
            - Recommended for production
            """
        )
