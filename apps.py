# app.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

from src.pipeline import LivenessPipeline

# ── Configuration de la page ──────────────────────────────────────
st.set_page_config(
    page_title="Face Liveness Detection",
    page_icon="🔍",
    layout="wide"
)

# ── Chargement du modèle (mis en cache par chemin + version) ──────
@st.cache_resource
def load_pipeline(weights_path, threshold, model_version):
    return LivenessPipeline(
        weights_path=weights_path,
        threshold=threshold,
        model_version=model_version
    )

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    model_choice = st.radio(
        "Select Model",
        ["V1 — NUAA only", "V2 — Better generalization"],
        help="V1: trained on NUAA only. V2: trained on fused NUAA + LCC FASD."
    )

    weights_map = {
        "V1 — NUAA only":            ("models/best_checkpoint.pth",    1),
        "V2 — Better generalization": ("models/best_checkpoint_v2.pth", 2),
    }
    weights_path, model_version = weights_map[model_choice]

    threshold = st.slider(
        "Confidence Threshold",
        min_value=0.3,
        max_value=0.9,
        value=0.5,
        step=0.05,
        help="Above this threshold → Real. Below → Spoof."
    )

    st.markdown("---")
    st.markdown("### 📊 Model Performance")

    if model_version == 1:
        st.markdown("""
        **In-domain (NUAA)**
        - F1 : 0.9957
        - HTER : 0.0044

        **Cross-domain (LCC FASD)**
        - F1 : 0.3003
        - HTER : 0.4151 ⚠️
        """)
    else:
        st.markdown("""
        **In-domain (NUAA)**
        - F1 : 0.9979
        - HTER : 0.0023

        **Cross-domain (LCC FASD)**
        - F1 : 0.8721
        - HTER : 0.0057 ✅
        """)

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **Face Liveness Detection System**

    Pipeline:
    - Detection: MTCNN
    - Classification: MobileNetV2

    *M1 Cybersecurity — University of Buea*
    """)

# ── Titre principal ───────────────────────────────────────────────
st.title("🔍 Face Liveness Detection")
st.markdown("Anti-spoofing system detecting print and replay presentation attacks.")
st.markdown("---")

# ── Chargement du pipeline ────────────────────────────────────────
checkpoint = Path(weights_path)
if not checkpoint.exists():
    st.error(f"❌ Checkpoint not found: `{weights_path}`")
    st.info("Place `best_checkpoint.pth` and `best_checkpoint_v2.pth` in `models/`.")
    st.stop()

pipeline = load_pipeline(weights_path, threshold, model_version)
st.success(f"✅ Model loaded: {model_choice}")

# ── Sélection du mode ─────────────────────────────────────────────
mode = st.radio(
    "Input Mode",
    ["📁 Upload Image", "📷 Webcam"],
    horizontal=True
)
st.markdown("---")


# ── Fonction d'affichage du résultat ─────────────────────────────
def display_result(output):
    results   = output["results"]
    latency   = output["latency"]
    annotated = output["annotated_frame"]

    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
    st.image(annotated_rgb, caption="Annotated Result",
             use_container_width=True)

    if not results:
        st.warning("No face detected in the image.")
        return

    for i, res in enumerate(results):
        label      = res["label"]
        confidence = res["confidence"]

        st.markdown(f"#### Face {i+1}")

        if label == "Real":
            st.success(f"REAL — Genuine live face detected")
        else:
            st.error(f"SPOOF DETECTED — Presentation attack")

        st.markdown(f"**Confidence: {confidence:.1%}**")
        st.progress(confidence)

    st.markdown("---")
    st.markdown("#### Latency")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Detection",
                  f"{latency.get('detection_ms', 0):.0f} ms")
    with col2:
        st.metric("Classification",
                  f"{latency.get('classification_ms', 0):.0f} ms")
    with col3:
        st.metric("Total",
                  f"{latency.get('total_ms', 0):.0f} ms")


# ── MODE UPLOAD ───────────────────────────────────────────────────
if "Upload" in mode:
    st.subheader("📁 Upload an Image")
    st.markdown("Supports JPG, PNG, JPEG formats.")

    uploaded = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded:
        pil_img = Image.open(uploaded).convert("RGB")
        np_img  = np.array(pil_img)
        bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Original Image**")
            st.image(pil_img, use_container_width=True)

        with col2:
            st.markdown(f"**Analysis ({model_choice})**")
            with st.spinner("Analysing..."):
                output = pipeline.run(bgr_img)
            display_result(output)

        # Comparaison rapide
        st.markdown("---")
        if st.button("🔄 Compare with other model"):
            other_choice = (
                "V1 — NUAA only"
                if model_version == 2
                else "V2 — Better generalization"
            )
            other_path, other_version = weights_map[other_choice]

            if not Path(other_path).exists():
                st.error(f"Checkpoint not found: `{other_path}`")
            else:
                other_pipeline = load_pipeline(
                    other_path, threshold, other_version
                )
                st.markdown(f"### Result with {other_choice}")
                with st.spinner("Analysing..."):
                    other_output = other_pipeline.run(bgr_img)
                display_result(other_output)


# ── MODE WEBCAM ───────────────────────────────────────────────────
elif "Webcam" in mode:
    st.subheader("📷 Webcam Capture")
    st.markdown("Take a photo with your webcam for liveness analysis.")

    img_data = st.camera_input("Capture Image")

    if img_data:
        pil_img = Image.open(img_data).convert("RGB")
        np_img  = np.array(pil_img)
        bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

        with st.spinner("Analysing..."):
            output = pipeline.run(bgr_img)

        display_result(output)