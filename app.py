import cv2
import numpy as np
import streamlit as st
from PIL import Image
from pathlib import Path

from src.pipeline import LivenessPipeline

st.set_page_config(
    page_title="Face Liveness Detection",
    page_icon="🔍",
    layout="wide",
)

st.markdown(
    """
    <style>
        body {
            background-color: #0f172a;
            color: #e2e8f0;
        }
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1a202c 100%);
        }
        .stProgress > div > div > div { 
            background: linear-gradient(90deg, #0ea5e9, #10b981) !important; 
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(16, 185, 129, 0.08));
            border: 2px solid rgba(6, 182, 212, 0.3);
            border-radius: 20px;
            padding: 2rem 2.2rem;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        .hero-card h1 { 
            font-size: 2.6rem;
            font-weight: 800;
            color: #38bdf8;
            margin-bottom: 0.5rem;
        }
        .hero-card p {
            font-size: 1.1rem;
            color: #cbd5e1;
        }
        .info-card {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(139, 92, 246, 0.04));
            border: 1.5px solid rgba(6, 182, 212, 0.25);
            border-radius: 16px;
            padding: 1.3rem;
            min-height: 130px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .info-card h4 {
            color: #10b981;
            font-weight: 700;
            font-size: 1.3rem;
            margin-bottom: 0.4rem;
        }
        .info-card p {
            color: #94a3b8;
            font-size: 0.95rem;
        }
        .panel-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(20, 30, 48, 0.4));
            border: 1.5px solid rgba(6, 182, 212, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
        }
        .status-pill {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.1));
            border: 1.5px solid rgba(16, 185, 129, 0.4);
            border-radius: 12px;
            color: #10b981;
            font-weight: 700;
            padding: 0.6rem 1.2rem;
            margin: 0.8rem 0;
            display: inline-block;
            font-size: 1rem;
        }
        .result-card {
            background: rgba(6, 182, 212, 0.08);
            border-left: 5px solid #0ea5e9;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }
        .result-card h4 {
            color: #10b981;
            font-weight: 700;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.8rem;
            border-bottom: 2px solid rgba(6, 182, 212, 0.2);
        }
        .stTabs [data-baseweb="tab"] {
            height: 48px;
            border-radius: 12px;
            padding: 0 1.5rem;
            background: rgba(30, 41, 59, 0.4);
            color: #94a3b8;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0ea5e9, #06b6d4);
            color: white;
        }
        [data-testid="stMetric"] {
            background: rgba(6, 182, 212, 0.08);
            border: 1px solid rgba(6, 182, 212, 0.2);
            border-radius: 12px;
            padding: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_pipeline(weights_path, threshold):
    return LivenessPipeline(weights_path=weights_path, threshold=threshold)


def convert_to_bgr(uploaded_file):
    pil_img = Image.open(uploaded_file).convert("RGB")
    np_img = np.array(pil_img)
    bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
    return pil_img, bgr_img


def display_result(output):
    results = output["results"]
    latency = output["latency"]
    annotated = output["annotated_frame"]
    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    st.subheader("Analysis Result")
    st.image(annotated_rgb, caption="Annotated image with prediction", use_container_width=True)

    if not results:
        st.warning("⚠️ No face detected in the image. Try a clearer image with a better visible face.")
        return

    summary_label = "REAL" if all(res["label"] == "Real" for res in results) else "SPOOF"

    if summary_label == "REAL":
        st.markdown("<div class='status-pill'>✅ Overall verdict: authentic face detected</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-pill'>⚠️ Overall verdict: presentation attack detected</div>", unsafe_allow_html=True)

    for i, res in enumerate(results, start=1):
        label = res["label"]
        confidence = float(res["confidence"])
        with st.container():
            st.markdown(f"<div class='result-card'><h4 style='margin:0 0 0.25rem 0;'>Face {i}</h4></div>", unsafe_allow_html=True)
            if label == "Real":
                st.success(f"Authentic — confidence {confidence:.1%}")
            else:
                st.error(f"Spoof — confidence {confidence:.1%}")
            st.progress(confidence)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Detection", f"{latency.get('detection_ms', 0):.0f} ms")
    with col2:
        st.metric("Classification", f"{latency.get('classification_ms', 0):.0f} ms")
    with col3:
        st.metric("Total", f"{latency.get('total_ms', 0):.0f} ms")


with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    model_choice = st.radio(
        "Model to use",
        ["v1 — NUAA only", "v2 — NUAA + LCC FASD (merged)"],
        help="v1: trained only on NUAA. v2: trained on merged data with better cross-domain generalization.",
    )

    weights_map = {
        "v1 — NUAA only": "models/best_checkpoint.pth",
        "v2 — NUAA + LCC FASD (merged)": "models/best_checkpoint_v2.pth",
    }
    weights_path = weights_map[model_choice]

    threshold = st.slider(
        "Decision threshold",
        min_value=0.3,
        max_value=0.9,
        value=0.5,
        step=0.05,
        help="Above this threshold → Real. Below it → Spoof.",
    )

    st.markdown("---")
    st.markdown("### 📊 Known performance")
    if "v1" in model_choice:
        st.markdown(
            """
            **In-domain (NUAA)**
            - F1: 0.9957
            - HTER: 0.0044

            **Cross-domain (LCC FASD)**
            - F1: 0.3003
            - HTER: 0.4151 ⚠️
            """
        )
    else:
        st.markdown(
            """
            **In-domain (NUAA)**
            - F1: 0.9979
            - HTER: 0.0023

            **Cross-domain (LCC FASD)**
            - F1: 0.8721
            - HTER: 0.0057 ✅
            """
        )

    st.markdown("---")
    st.markdown("### About")
    st.markdown(
        """
        **Face Liveness Detection System**

        Anti-spoofing pipeline:
        - Detection: MTCNN
        - Classification: MobileNetV2

        *M1 Cybersecurity — University of Buea*
        """
    )


st.markdown(
    """
    <div class="hero-card">
        <h1 style="margin-bottom:0.25rem;">🔍 Face Liveness Detection</h1>
        <p style="margin:0; font-size:1.05rem;">Analyze an image or webcam capture to detect whether a face is authentic or spoofed.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='info-card'><h4 style='margin:0 0 0.25rem 0;'>📸 Input modes</h4><p style='margin:0;'>Upload an image or use your webcam instantly.</p></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='info-card'><h4 style='margin:0 0 0.25rem 0;'>⚡ Fast analysis</h4><p style='margin:0;'>Get a decision, confidence score, and latency metrics.</p></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='info-card'><h4 style='margin:0 0 0.25rem 0;'>🛡️ Secure detection</h4><p style='margin:0;'>Designed for presentation attack and spoof detection.</p></div>", unsafe_allow_html=True)

checkpoint = Path(weights_path)
if not checkpoint.exists():
    st.error(f"❌ Checkpoint not found: {weights_path}")
    st.info("Download the corresponding checkpoint and place it in the models folder.")
    st.stop()

pipeline = load_pipeline(weights_path, threshold)
st.success(f"✅ Model loaded: {model_choice}")

upload_tab, camera_tab, help_tab = st.tabs(["📁 Upload image", "📷 Webcam", "ℹ️ Guide"])

with upload_tab:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.subheader("Upload an image")
    st.caption("Supported formats: JPG, JPEG, and PNG")
    uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded is not None:
        try:
            pil_img, bgr_img = convert_to_bgr(uploaded)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original image**")
                st.image(pil_img, use_container_width=True)
            with col2:
                st.markdown("**Analysis**")
                with st.spinner("Analyzing..."):
                    output = pipeline.run(bgr_img)
                display_result(output)
        except Exception as exc:
            st.error(f"Could not process the image: {exc}")

with camera_tab:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.subheader("Capture from webcam")
    st.caption("Take a photo with your webcam and analyze it instantly.")
    img_data = st.camera_input("Capture an image")
    st.markdown("</div>", unsafe_allow_html=True)

    if img_data is not None:
        try:
            pil_img = Image.open(img_data).convert("RGB")
            np_img = np.array(pil_img)
            bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
            with st.spinner("Analyzing..."):
                output = pipeline.run(bgr_img)
            display_result(output)
        except Exception as exc:
            st.error(f"Could not process the capture: {exc}")

with help_tab:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.subheader("How to use the tool")
    st.markdown(
        """
        1. Choose a model in the sidebar.
        2. Adjust the threshold if needed.
        3. Upload an image or use the webcam.
        4. Review the verdict, confidence, and latency metrics.
        """
    )
    st.info("For better results, use well-lit images with the face fully visible.")
    st.markdown("</div>", unsafe_allow_html=True)
