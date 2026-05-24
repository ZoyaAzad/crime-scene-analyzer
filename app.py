import streamlit as st
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
 
from modules.noise_reduction   import gaussian_blur, median_filter
from modules.color_segment     import segment_color
from modules.edge_detection    import canny_edges, detect_contours, threshold_image
from modules.enhancement       import histogram_equalization, adjust_contrast_brightness, sharpen_image
from modules.face_detect       import detect_faces
from modules.reports           import generate_pdf_report
 
# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="TraceLens", layout="wide", page_icon="🔍")
 
st.markdown("""
<style>
  .stApp { background-color: #0a0a0a; color: #e0e0e0; font-family: 'Courier New', monospace; }
  section[data-testid="stSidebar"] {
      background-color: #111111;
      border-right: 2px solid #FFD700;
  }
  .stButton>button {
      background: #1a1a1a; color: #FFD700;
      border: 1px solid #FFD700; border-radius: 0px;
      letter-spacing: 2px; text-transform: uppercase;
      font-family: 'Courier New', monospace; width: 100%;
  }
  .stButton>button:hover { background: #FFD700; color: #000000; }
  h1, h2, h3, h4 { color: #FFD700 !important; letter-spacing: 3px; font-family: 'Courier New', monospace; }
  .stSelectbox label, .stSlider label, .stCheckbox label, .stFileUploader label {
      color: #FFD700 !important; font-family: 'Courier New', monospace; letter-spacing: 1px;
  }
  .stAlert { background-color: #1a1a1a; border: 1px solid #FFD700; color: #e0e0e0; }
  div[data-testid="stFileUploader"] {
      border: 1px dashed #FFD700; padding: 8px; background: #111;
  }
  /* Download button — green accent */
  div[data-testid="stDownloadButton"] > button {
      background: #0a1a0a !important; color: #00FF99 !important;
      border: 1px solid #00FF99 !important;
  }
  div[data-testid="stDownloadButton"] > button:hover {
      background: #00FF99 !important; color: #000 !important;
  }
</style>
""", unsafe_allow_html=True)
 
# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 10px 0;'>
  <h1>🔍 TRACELENS — FORENSIC EVIDENCE ANALYZER</h1>
  <p style='color:#888; font-family:Courier New; letter-spacing:2px;'>DIGITAL IMAGE PROCESSING SYSTEM — CLASSIFIED</p>
</div>
""", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #FFD700;'>", unsafe_allow_html=True)
 
# ── Sidebar ──────────────────────────────────────────────────────────────────────
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
    kernel_size    = st.slider("Kernel Size", 3, 31, 5, step=2)
    apply_gaussian = st.checkbox("Gaussian Blur")
    apply_median   = st.checkbox("Median Filter")
 
    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("### 🔎 EDGE DETECTION")
    edge_mode     = st.selectbox("Detection Method", ["None", "Canny Edges", "Contours", "Thresholding"])
    t1            = st.slider("Canny Threshold 1", 0, 255, 50)
    t2            = st.slider("Canny Threshold 2", 0, 255, 130)
    min_area      = st.slider("Min Contour Area",  50, 5000, 500)
    threshold_val = st.slider("Threshold Value",   0, 255, 127)
 
    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("### 🩸 STAIN DETECTION (HSV)")
    enable_color = st.checkbox("Enable Color Detection")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🩸 FRESH BLOOD"):
            st.session_state["h_min"]=0;  st.session_state["h_max"]=10
            st.session_state["s_min"]=150; st.session_state["s_max"]=255
            st.session_state["v_min"]=80; st.session_state["v_max"]=200

        if st.button("🩸 DRIED BLOOD"):
            st.session_state["h_min"]=0;  st.session_state["h_max"]=15
            st.session_state["s_min"]=40; st.session_state["s_max"]=160
            st.session_state["v_min"]=20; st.session_state["v_max"]=110
            with col_b:
                if st.button("🔵 RESET HSV"):
                    for k in ["h_min","h_max","s_min","s_max","v_min","v_max"]:
                        st.session_state.pop(k, None)
 
    h_min = st.slider("Hue Min",        0, 179, st.session_state.get("h_min", 0))
    h_max = st.slider("Hue Max",        0, 179, st.session_state.get("h_max", 15))
    s_min = st.slider("Saturation Min", 0, 255, st.session_state.get("s_min", 40))
    s_max = st.slider("Saturation Max", 0, 255, st.session_state.get("s_max", 160))
    v_min = st.slider("Value Min",      0, 255, st.session_state.get("v_min", 20))
    v_max = st.slider("Value Max",      0, 255, st.session_state.get("v_max", 110))
 
    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("### 👤 FACE DETECTION")
    apply_face = st.checkbox("Detect Faces")
 
    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    if st.button("🔄 RESET ALL"):
        st.session_state.clear()
        st.rerun()
 
# ── Main panel ───────────────────────────────────────────────────────────────────
if uploaded_file is None:
    st.markdown("""
    <div style='text-align:center; margin-top:80px; color:#555;'>
        <p style='font-size:48px;'>🗂</p>
        <p style='font-family:Courier New; letter-spacing:2px;'>AWAITING EVIDENCE UPLOAD...</p>
        <p style='font-family:Courier New; color:#444;'>Upload an image from the sidebar to begin analysis</p>
    </div>
    """, unsafe_allow_html=True)
 
else:
    image     = Image.open(uploaded_file).convert("RGB")
    image_np  = np.array(image)
    image_cv  = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
 
    # Keep pristine originals — edge detection always works from clean copy
    original_cv     = image_cv.copy()
    clean_for_edges = image_cv.copy()
    processed       = image_cv.copy()
 
    findings           = []
    techniques_applied = []
 
    # ── Data to collect for report ──────────────────────────────────────────
    face_details_list  = []
    stain_coverage_val = None
    stain_count_val    = None
    contour_count_val  = None
    contour_areas_val  = []
    mask_cv            = None
 
    # Evidence file header
    st.markdown(f"""
    <div style='background:#111; border:1px solid #FFD700; padding:10px 20px; margin-bottom:16px;'>
        <span style='color:#FFD700; font-family:Courier New; letter-spacing:2px;'>
        📋 EVIDENCE FILE: {uploaded_file.name.upper()}
        &nbsp;&nbsp;|&nbsp;&nbsp;
        {image_np.shape[1]}×{image_np.shape[0]} px
        &nbsp;&nbsp;|&nbsp;&nbsp;
        {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </span>
    </div>
    """, unsafe_allow_html=True)
 
    # ── MODULE 1: Enhancement ────────────────────────────────────────────────
    if contrast != 1.0 or brightness != 0:
        processed = adjust_contrast_brightness(processed, contrast, brightness)
        techniques_applied.append({
            "name": "Contrast / Brightness Adjustment",
            "params": f"alpha={contrast:.2f}, beta={brightness}"
        })
    if apply_hist:
        processed = histogram_equalization(processed)
        findings.append("Histogram equalisation applied — tonal range expanded")
        techniques_applied.append({"name": "Histogram Equalisation", "params": "YCrCb channel 0"})
    if apply_sharpen:
        processed = sharpen_image(processed)
        findings.append("Sharpening filter applied — edge definition enhanced")
        techniques_applied.append({"name": "Sharpening (Laplacian kernel)", "params": "kernel=[0,-1,0,-1,5,-1,0,-1,0]"})
 
    # ── MODULE 2: Noise Reduction ────────────────────────────────────────────
    if apply_gaussian:
        processed = gaussian_blur(processed, kernel_size)
        findings.append(f"Gaussian blur applied — random noise suppressed (kernel {kernel_size}×{kernel_size})")
        techniques_applied.append({"name": "Gaussian Blur", "params": f"kernel={kernel_size}x{kernel_size}"})
    if apply_median:
        processed = median_filter(processed, kernel_size)
        findings.append(f"Median filter applied — salt-and-pepper noise removed (kernel {kernel_size})")
        techniques_applied.append({"name": "Median Filter", "params": f"kernel={kernel_size}"})
 
    # ── MODULE 3: Edge Detection  ─────────────────────────────────────────────
    # IMPORTANT: always run edge detection on the clean original, never blurred
    if edge_mode == "Canny Edges":
        processed = canny_edges(clean_for_edges, t1, t2)
        findings.append(f"Canny edge detection completed — thresholds T1={t1}, T2={t2}")
        techniques_applied.append({
            "name": "Canny Edge Detection",
            "params": f"threshold1={t1}, threshold2={t2}"
        })
 
    elif edge_mode == "Contours":
        processed, obj_count, areas = detect_contours(clean_for_edges, min_area)
        contour_count_val = obj_count
        contour_areas_val = areas
        findings.append(f"Contour detection: {obj_count} significant object(s) found (min area={min_area}px)")
        if areas:
            findings.append(f"  Largest contour: {max(areas):.0f} px  |  Smallest: {min(areas):.0f} px")
            avg = sum(areas) / len(areas)
            findings.append(f"  Average contour size: {avg:.0f} px  |  Total objects: {obj_count}")
        techniques_applied.append({
            "name": "Contour Detection",
            "params": f"min_area={min_area}px, internal Canny T1=50 T2=150"
        })
 
    elif edge_mode == "Thresholding":
        processed = threshold_image(processed, threshold_val)
        findings.append(f"Binary thresholding applied — value={threshold_val} (pixels above=white, below=black)")
        techniques_applied.append({
            "name": "Binary Thresholding",
            "params": f"threshold={threshold_val}, type=THRESH_BINARY"
        })
 
    # ── MODULE 4: Colour Segmentation ────────────────────────────────────────
    if enable_color:
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        # Run on original so stains are not washed out by prior blur
        seg_input = clean_for_edges.copy()
        processed, mask_cv, stain_count, coverage = segment_color(seg_input, lower, upper)
        stain_coverage_val = coverage
        stain_count_val    = stain_count
 
        findings.append(f"Colour stain detection: {stain_count} region(s) identified")
        findings.append(f"  Stain coverage: {coverage:.4f}% of image area")
        pixel_count = int(coverage / 100 * image_np.shape[0] * image_np.shape[1])
        findings.append(f"  Matching pixels: {pixel_count:,}  |  HSV range H({h_min}-{h_max}) S({s_min}-{s_max}) V({v_min}-{v_max})")
        # Severity label
        if coverage < 0.5:   sev = "TRACE"
        elif coverage < 3:   sev = "MINOR"
        elif coverage < 10:  sev = "MODERATE"
        elif coverage < 25:  sev = "SIGNIFICANT"
        else:                sev = "EXTENSIVE"
        findings.append(f"  Stain severity estimate: {sev}")
        techniques_applied.append({
            "name": "HSV Colour Segmentation",
            "params": f"H({h_min}-{h_max}), S({s_min}-{s_max}), V({v_min}-{v_max}) + morphological cleanup"
        })
 
    # ── MODULE 5: Face Detection ─────────────────────────────────────────────
    face_count = 0
    if apply_face:
        face_input = clean_for_edges.copy()
        if len(face_input.shape) == 2:
            face_input = cv2.cvtColor(face_input, cv2.COLOR_GRAY2BGR)
        processed, face_count, face_details_list = detect_faces(face_input)
 
        findings.append(f"Face detection: {face_count} face(s) identified")
        for fd in face_details_list:
            x, y, fw, fh = fd["bbox"]
            conf = f"{fd['confidence']:.1%}" if fd["confidence"] else "Haar"
            findings.append(
                f"  Face #{fd['id']}: method={fd['method']}, confidence={conf}, "
                f"position={fd['position']}, bbox=({x},{y},{fw}×{fh})"
            )
        techniques_applied.append({
            "name": "Face Detection (DNN + Haar)",
            "params": "DNN confidence>45%, Haar scaleFactor=[1.05,1.1,1.2], minNeighbors=4"
        })
 
    # ── Display ───────────────────────────────────────────────────────────────
    processed_display = (
        processed if len(processed.shape) == 2
        else cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
    )
 
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🖼 ORIGINAL EVIDENCE")
        st.image(image_np, use_container_width=True)
    with col2:
        st.markdown("#### 🔬 ANALYZED OUTPUT")
        st.image(processed_display, use_container_width=True)
 
    if enable_color and mask_cv is not None:
        st.markdown("#### 🩸 STAIN DETECTION MASK")
        st.image(mask_cv, use_container_width=True, clamp=True)
 
    # ── Findings Log ──────────────────────────────────────────────────────────
    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
    st.markdown("#### 📋 FINDINGS LOG")
    if findings:
        for f in findings:
            indent = f.startswith("  ")
            colour = "#aaaaaa" if indent else "#00FF99"
            prefix = "  └─" if indent else "▶"
            st.markdown(
                f"<p style='font-family:Courier New; color:{colour}; margin:1px 0;'>"
                f"{prefix} {f.strip()}</p>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            "<p style='font-family:Courier New; color:#555;'>No techniques applied yet.</p>",
            unsafe_allow_html=True
        )
 
    # ── Report generation ─────────────────────────────────────────────────────
    st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)
 
    if st.button("📄 GENERATE EVIDENCE REPORT"):
        with st.spinner("Compiling forensic report..."):
            pdf_bytes = generate_pdf_report(
                original_cv        = original_cv,
                processed_cv       = processed,
                findings           = findings,
                filename           = uploaded_file.name,
                face_details       = face_details_list if face_details_list else None,
                stain_coverage     = stain_coverage_val,
                stain_count        = stain_count_val,
                contour_count      = contour_count_val,
                contour_areas      = contour_areas_val if contour_areas_val else None,
                techniques_applied = techniques_applied,
                mask_cv            = mask_cv,
            )
 
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_name = f"TraceLens_Report_{ts}.pdf"
 
        st.download_button(
            label    = "⬇ DOWNLOAD FORENSIC REPORT (PDF)",
            data     = pdf_bytes,
            file_name= pdf_name,
            mime     = "application/pdf",
        )
        st.success(f"Report ready — click above to download  ·  {pdf_name}")