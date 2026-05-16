import streamlit as st
import cv2
import numpy as np
from PIL import Image

from modules.noise_reduction import gaussian_blur, median_filter
from modules.color_segment import segment_color
from modules.edge_detection import canny_edges, detect_contours, threshold_image
from modules.enhancement import histogram_equalization, adjust_contrast_brightness, sharpen_image
from modules.face_detect import detect_faces
from modules.reports import save_report

# ── Page config ────────────────────────────────────────
st.set_page_config(page_title="TraceLens", layout="wide", page_icon="🔍")

st.markdown("""
<style>
  .stApp { background-color: #0a0a0a; color: #e0e0e0; font-family: 'Courier New', monospace; }

  section[data-testid="stSidebar"] {
      background-color: #111111;
      border-right: 2px solid #FFD700;
  }

  .stButton>button {
      background: #1a1a1a;
      color: #FFD700;
      border: 1px solid #FFD700;
      border-radius: 0px;
      letter-spacing: 2px;
      text-transform: uppercase;
      font-family: 'Courier New', monospace;
      width: 100%;
  }
  .stButton>button:hover { background: #FFD700; color: #000000; }

  h1, h2, h3, h4 { color: #FFD700 !important; letter-spacing: 3px; font-family: 'Courier New', monospace; }

  .stSelectbox label, .stSlider label, .stCheckbox label, .stFileUploader label {
      color: #FFD700 !important;
      font-family: 'Courier New', monospace;
      letter-spacing: 1px;
  }

  .stAlert { background-color: #1a1a1a; border: 1px solid #FFD700; color: #e0e0e0; }

  div[data-testid="stFileUploader"] {
      border: 1px dashed #FFD700;
      padding: 8px;
      background: #111;
  }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 10px 0;'>
  <h1>🔍 TRACELENS — FORENSIC EVIDENCE ANALYZER</h1>
  <p style='color:#888; font-family:Courier New; letter-spacing:2px;'>DIGITAL IMAGE PROCESSING SYSTEM — CLASSIFIED</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border: 1px solid #FFD700;'>", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📁 EVIDENCE UPLOAD")
    uploaded_file = st.file_uploader("Upload crime scene image", type=["jpg", "jpeg", "png"])

    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("### ⚙ ENHANCEMENT")
    contrast   = st.slider("Contrast",   0.5, 3.0, 1.0)
    brightness = st.slider("Brightness", -100, 100, 0)
    apply_hist    = st.checkbox("Histogram Equalization")
    apply_sharpen = st.checkbox("Sharpen Image")

    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("### 🌫 NOISE REDUCTION")
    kernel_size    = st.slider("Kernel Size", 3, 31, 9, step=2)
    apply_gaussian = st.checkbox("Gaussian Blur")
    apply_median   = st.checkbox("Median Filter")

    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("### 🔎 EDGE DETECTION")
    edge_mode = st.selectbox("Detection Method", ["None", "Canny Edges", "Contours", "Thresholding"])
    t1            = st.slider("Canny Threshold 1", 0, 255, 50)
    t2            = st.slider("Canny Threshold 2", 0, 255, 150)
    min_area      = st.slider("Min Contour Area",  50, 5000, 500)
    threshold_val = st.slider("Threshold Value",   0, 255, 127)

    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("### 🩸 STAIN DETECTION (HSV)")
    enable_color = st.checkbox("Enable Color Detection")
    h_min = st.slider("Hue Min",        0, 179,  0)
    h_max = st.slider("Hue Max",        0, 179, 20)
    s_min = st.slider("Saturation Min", 0, 255, 100)
    s_max = st.slider("Saturation Max", 0, 255, 255)
    v_min = st.slider("Value Min",      0, 255, 50)
    v_max = st.slider("Value Max",      0, 255, 255)

    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("### 👤 FACE DETECTION")
    apply_face = st.checkbox("Detect Faces")

    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    if st.button("🔄 RESET"):
        st.session_state.clear()
        st.rerun()

# ── Main panel ───────────────────────────────────────────
if uploaded_file is None:
    st.markdown("""
    <div style='text-align:center; margin-top:80px; color:#555;'>
        <p style='font-size:48px;'>🗂</p>
        <p style='font-family:Courier New; letter-spacing:2px;'>AWAITING EVIDENCE UPLOAD...</p>
        <p style='font-family:Courier New; color:#444;'>Upload an image from the sidebar to begin analysis</p>
    </div>
    """, unsafe_allow_html=True)

else:
    image        = Image.open(uploaded_file)
    image_np     = np.array(image)
    image_cv     = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    processed    = image_cv.copy()
    findings     = []

    # Evidence file header
    st.markdown(f"""
    <div style='background:#111; border:1px solid #FFD700; padding:10px 20px; margin-bottom:16px;'>
        <span style='color:#FFD700; font-family:Courier New; letter-spacing:2px;'>
        📋 EVIDENCE FILE: {uploaded_file.name.upper()}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Module 1: Enhancement
    processed = adjust_contrast_brightness(processed, contrast, brightness)
    if apply_hist:
        processed = histogram_equalization(processed)
        findings.append("Histogram equalization applied")
    if apply_sharpen:
        processed = sharpen_image(processed)
        findings.append("Sharpening filter applied")

    # Module 2: Noise reduction
    if apply_gaussian:
        processed = gaussian_blur(processed, kernel_size)
        findings.append(f"Gaussian blur applied (kernel={kernel_size})")
    if apply_median:
        processed = median_filter(processed, kernel_size)
        findings.append(f"Median filter applied (kernel={kernel_size})")

    # Module 3: Edge detection
    if edge_mode == "Canny Edges":
        processed = canny_edges(processed, t1, t2)
        findings.append(f"Canny edge detection (t1={t1}, t2={t2})")
    elif edge_mode == "Contours":
        processed = detect_contours(processed, min_area)
        findings.append(f"Contour detection (min area={min_area})")
    elif edge_mode == "Thresholding":
        processed = threshold_image(processed, threshold_val)
        findings.append(f"Thresholding applied (value={threshold_val})")

    # Module 4: Color segmentation
    mask = None
    if enable_color:
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        processed, mask = segment_color(processed, lower, upper)
        findings.append(f"Color stain detection — HSV range H({h_min}-{h_max})")

    # Module 5: Face detection
    face_count = 0
    if apply_face:
        if len(processed.shape) == 2:
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
        processed, face_count = detect_faces(processed)
        findings.append(f"Face detection: {face_count} face(s) found")

    # Display conversion
    if len(processed.shape) == 2:
        processed_display = processed
    else:
        processed_display = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)

    # Side by side display
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🖼 ORIGINAL EVIDENCE")
        st.image(image_np, use_container_width=True)
    with col2:
        st.markdown("#### 🔬 ANALYZED OUTPUT")
        st.image(processed_display, use_container_width=True)

    if enable_color and mask is not None:
        st.markdown("#### 🩸 STAIN DETECTION MASK")
        st.image(mask, use_container_width=True, clamp=True)

    # Findings log
    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("#### 📋 FINDINGS LOG")
    if findings:
        for f in findings:
            st.markdown(f"<p style='font-family:Courier New; color:#00FF99;'>▶ {f}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-family:Courier New; color:#555;'>No techniques applied yet.</p>", unsafe_allow_html=True)

    # Report generation
    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    if st.button("📄 GENERATE EVIDENCE REPORT"):
        img_path, log_path = save_report(image_cv, processed, findings)
        st.success(f"Report saved — {log_path}")
        st.info(f"Image saved — {img_path}")