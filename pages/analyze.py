import streamlit as st
import cv2
import numpy as np
from PIL import Image
from datetime import datetime

from modules.noise_reduction import gaussian_blur, median_filter
from modules.color_segment   import segment_color
from modules.edge_detection  import canny_edges, sobel_edges, detect_contours, threshold_image
from modules.enhancement     import histogram_equalization, adjust_contrast_brightness, sharpen_image
from modules.face_detect     import detect_faces


def render():
    # Import theme helpers — but force sidebar open first
    from theme import inject_theme, tape_divider, section_header
    inject_theme("Analyze")

    # ── Force sidebar open + style it ─────────────────────────────────────────
    st.markdown("""
    <style>
    /* Force sidebar visible on analyze page */
    section[data-testid="stSidebar"] {
        display: flex !important;
        width: 320px !important;
        min-width: 320px !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 320px !important;
    }
    /* Sidebar toggle button — keep visible */
    button[data-testid="stSidebarNav"] { display: flex !important; }
    button[data-testid="collapsedControl"] { display: flex !important; }

    /* Sidebar internals */
    section[data-testid="stSidebar"] .stMarkdown h4 {
        font-family: var(--font-mono, 'Courier New') !important;
        font-size: 10px !important;
        letter-spacing: 3px !important;
        color: #CC0000 !important;
        text-transform: uppercase !important;
        margin: 16px 0 8px !important;
    }
    section[data-testid="stSidebar"] label {
        font-family: var(--font-mono, 'Courier New') !important;
        font-size: 11px !important;
        color: #FFD700 !important;
        letter-spacing: 1px !important;
    }
    section[data-testid="stSidebar"] .stSlider > div > div {
        background: #CC0000 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: #0d0d0d !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        font-family: var(--font-mono, 'Courier New') !important;
        font-size: 10px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-radius: 0 !important;
        padding: 6px 8px !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #FFD700 !important;
        color: #000 !important;
    }
    section[data-testid="stSidebar"] .stCheckbox label {
        color: #e0e0e0 !important;
        font-size: 12px !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #FFD700 !important;
    }
    .analyze-header {
        padding: 40px 40px 20px;
        border-bottom: 1px solid #1a1a1a;
    }
    .case-form {
        background: #080808;
        border: 1px solid #1a1a1a;
        border-top: 2px solid #CC0000;
        padding: 28px;
        margin: 20px 0;
    }
    .case-form-title {
        font-family: 'Courier New', monospace;
        font-size: 9px;
        letter-spacing: 4px;
        color: #CC0000;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    .findings-entry {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        line-height: 2;
        padding: 2px 0;
        border-bottom: 1px solid #111;
    }
    .findings-entry.main { color: #00FF99; }
    .findings-entry.sub  { color: #666; padding-left: 20px; }
    .img-section-label {
        font-family: 'Courier New', monospace;
        font-size: 11px;
        letter-spacing: 3px;
        color: #FFD700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="analyze-header">
        <p style="font-family:'Courier New',monospace;font-size:10px;letter-spacing:4px;color:#CC0000;margin-bottom:8px;">
            [ FORENSIC ANALYSIS TERMINAL ]
        </p>
        <h1 style="font-family:'Special Elite',serif;font-size:48px;color:#fff;
                   text-shadow:0 0 20px rgba(204,0,0,0.3);margin:0;">
            Evidence Analyzer
        </h1>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="padding:20px 0 12px;">
            <p style="font-family:'Courier New',monospace;font-size:9px;letter-spacing:3px;
                      color:#CC0000;text-transform:uppercase;margin:0;">
                ▌ TRACELENS // CONTROL PANEL
            </p>
            <div style="height:1px;background:linear-gradient(90deg,#CC0000,transparent);margin-top:8px;"></div>
        </div>
        """, unsafe_allow_html=True)

        # ── UPLOAD ────────────────────────────────────────────────────────────
        st.markdown("#### 📁 EVIDENCE UPLOAD")
        uploaded_file = st.file_uploader(
            "Upload crime scene image",
            type=["jpg", "jpeg", "png"],
            key="analyze_uploader"
        )

        # ── ENHANCEMENT ───────────────────────────────────────────────────────
        st.markdown("<hr style='border:1px solid #1a1a1a;margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("#### ⚙ ENHANCEMENT")
        contrast      = st.slider("Contrast",   0.5, 3.0, 1.0)
        brightness    = st.slider("Brightness", -100, 100, 0)
        apply_hist    = st.checkbox("Histogram Equalization")
        apply_sharpen = st.checkbox("Sharpen Image")

        # ── NOISE REDUCTION ───────────────────────────────────────────────────
        st.markdown("<hr style='border:1px solid #1a1a1a;margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("#### 🌫 NOISE REDUCTION")
        kernel_size    = st.slider("Kernel Size", 3, 31, 5, step=2)
        apply_gaussian = st.checkbox("Gaussian Blur")
        apply_median   = st.checkbox("Median Filter")

        # ── EDGE DETECTION ────────────────────────────────────────────────────
        st.markdown("<hr style='border:1px solid #1a1a1a;margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("#### 🔎 EDGE DETECTION")
        edge_mode = st.selectbox(
            "Detection Method",
            ["None", "Canny Edges", "Sobel Edges", "Contours", "Thresholding"]
        )
        t1            = st.slider("Canny Threshold 1", 0, 255, 50)
        t2            = st.slider("Canny Threshold 2", 0, 255, 130)
        min_area      = st.slider("Min Contour Area",  50, 5000, 500)
        threshold_val = st.slider("Threshold Value",   0, 255, 127)

        # ── STAIN DETECTION ───────────────────────────────────────────────────
        st.markdown("<hr style='border:1px solid #1a1a1a;margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("#### 🩸 STAIN DETECTION")
        enable_color = st.checkbox("Enable Color Detection")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🩸 FRESH"):
                st.session_state["h_min"]=0;  st.session_state["h_max"]=10
                st.session_state["s_min"]=150; st.session_state["s_max"]=255
                st.session_state["v_min"]=80;  st.session_state["v_max"]=200
        with col_b:
            if st.button("🩸 DRIED"):
                st.session_state["h_min"]=0;  st.session_state["h_max"]=15
                st.session_state["s_min"]=60; st.session_state["s_max"]=180
                st.session_state["v_min"]=20; st.session_state["v_max"]=100
        with col_c:
            if st.button("↺ HSV"):
                for k in ["h_min","h_max","s_min","s_max","v_min","v_max"]:
                    st.session_state.pop(k, None)

        h_min = st.slider("Hue Min",        0, 179, st.session_state.get("h_min", 0),   key="h_min")
        h_max = st.slider("Hue Max",        0, 179, st.session_state.get("h_max", 15),  key="h_max")
        s_min = st.slider("Saturation Min", 0, 255, st.session_state.get("s_min", 60),  key="s_min")
        s_max = st.slider("Saturation Max", 0, 255, st.session_state.get("s_max", 180), key="s_max")
        v_min = st.slider("Value Min",      0, 255, st.session_state.get("v_min", 20),  key="v_min")
        v_max = st.slider("Value Max",      0, 255, st.session_state.get("v_max", 100), key="v_max")

        # ── FACE DETECTION ────────────────────────────────────────────────────
        st.markdown("<hr style='border:1px solid #1a1a1a;margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("#### 👤 FACE DETECTION")
        apply_face = st.checkbox("Detect Faces / Persons")

        # ── RESET ─────────────────────────────────────────────────────────────
        st.markdown("<hr style='border:1px solid #1a1a1a;margin:16px 0;'>", unsafe_allow_html=True)
        if st.button("🔄 RESET ALL"):
            st.session_state.clear()
            st.rerun()

    # ═════════════════════════════════════════════════════════════════════════
    # MAIN CONTENT
    # ═════════════════════════════════════════════════════════════════════════
    if uploaded_file is None:
        st.markdown("""
        <div style='text-align:center;margin-top:80px;padding:60px;'>
            <div style='font-size:64px;margin-bottom:20px;
                        filter:drop-shadow(0 0 20px rgba(139,0,0,0.5));'>🗂</div>
            <p style='font-family:"Courier New",monospace;font-size:14px;letter-spacing:4px;
                      color:#CC0000;text-transform:uppercase;'>
                AWAITING EVIDENCE UPLOAD
            </p>
            <p style='font-family:"Courier New",monospace;font-size:12px;color:#444;margin-top:8px;'>
                Upload a crime scene image from the sidebar panel to begin analysis
            </p>
            <div style='border:1px dashed rgba(139,0,0,0.3);padding:20px 40px;
                        display:inline-block;margin-top:24px;
                        font-family:"Courier New",monospace;font-size:11px;color:#333;'>
                ACCEPTED FORMATS: JPG &nbsp;•&nbsp; JPEG &nbsp;•&nbsp; PNG
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Load image ────────────────────────────────────────────────────────────
    image           = Image.open(uploaded_file).convert("RGB")
    image_np        = np.array(image)
    image_cv        = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    original_cv     = image_cv.copy()
    clean_for_edges = image_cv.copy()
    processed       = image_cv.copy()

    findings           = []
    techniques_applied = []
    face_details_list  = []
    stain_coverage_val = None
    stain_count_val    = None
    contour_count_val  = None
    contour_areas_val  = []
    mask_cv            = None

    # Evidence header bar
    st.markdown(f"""
    <div style='background:#0d0d0d;border:1px solid #222;border-left:4px solid #CC0000;
                padding:12px 24px;margin:16px 0;'>
        <p style='font-family:"Courier New",monospace;font-size:11px;letter-spacing:3px;
                  color:#FFD700;margin:0;'>
            📋 EVIDENCE FILE: {uploaded_file.name.upper()}
        </p>
        <p style='font-family:"Courier New",monospace;font-size:10px;color:#555;margin:4px 0 0;'>
            {image_np.shape[1]}×{image_np.shape[0]} px
            &nbsp;|&nbsp; {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            &nbsp;|&nbsp; STATUS: ACTIVE
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Case details form ─────────────────────────────────────────────────────
    st.markdown("""
    <p style='font-family:"Courier New",monospace;font-size:9px;letter-spacing:4px;
              color:#CC0000;text-transform:uppercase;margin:24px 0 4px;'>
        ▌ CASE INFORMATION
    </p>
    <p style='font-family:"Courier New",monospace;font-size:11px;color:#555;margin-bottom:16px;'>
        Fill in case details to include in the forensic report — all fields optional
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<div class='case-form'>", unsafe_allow_html=True)
    st.markdown("<div class='case-form-title'>// CASE METADATA</div>", unsafe_allow_html=True)

    cf1, cf2 = st.columns(2)
    with cf1:
        case_number  = st.text_input("Case Number / ID",        placeholder="e.g. TL-2024-0042")
        victim_name  = st.text_input("Victim / Subject Name",   placeholder="Full name or UNKNOWN")
        suspect_name = st.text_input("Suspect Name (if known)", placeholder="Full name or UNKNOWN")
    with cf2:
        location      = st.text_input("Crime Scene Location",    placeholder="e.g. 14 Elm Street, Basement")
        investigator  = st.text_input("Investigating Officer",   placeholder="Your name")
        incident_date = st.text_input("Incident Date",           placeholder="e.g. 2024-11-15")

    scene_description = st.text_area(
        "Crime Scene Description",
        placeholder="Describe what is visible in the scene, known sequence of events, relevant context...",
        height=100
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state["case_info"] = {
        "case_number":       case_number,
        "victim_name":       victim_name,
        "suspect_name":      suspect_name,
        "location":          location,
        "investigator":      investigator,
        "incident_date":     incident_date,
        "scene_description": scene_description,
        "filename":          uploaded_file.name,
        "dimensions":        f"{image_np.shape[1]}×{image_np.shape[0]}",
    }

    st.markdown("<hr style='border:1px solid #1a1a1a;margin:32px 0;'>", unsafe_allow_html=True)

    # ── MODULE 1: Enhancement ─────────────────────────────────────────────────
    if contrast != 1.0 or brightness != 0:
        processed = adjust_contrast_brightness(processed, contrast, brightness)
        techniques_applied.append({"name": "Contrast / Brightness",
                                    "params": f"alpha={contrast:.2f}, beta={brightness}"})
    if apply_hist:
        processed = histogram_equalization(processed)
        findings.append("Histogram equalisation applied — tonal range expanded")
        techniques_applied.append({"name": "Histogram Equalisation", "params": "YCrCb channel 0"})
    if apply_sharpen:
        processed = sharpen_image(processed)
        findings.append("Sharpening filter applied — edge definition enhanced")
        techniques_applied.append({"name": "Sharpening",
                                    "params": "Laplacian kernel [0,-1,0,-1,5,-1,0,-1,0]"})

    # ── MODULE 2: Noise reduction ─────────────────────────────────────────────
    if apply_gaussian:
        processed = gaussian_blur(processed, kernel_size)
        findings.append(f"Gaussian blur — noise suppressed (kernel {kernel_size}×{kernel_size})")
        techniques_applied.append({"name": "Gaussian Blur", "params": f"kernel={kernel_size}x{kernel_size}"})
    if apply_median:
        processed = median_filter(processed, kernel_size)
        findings.append(f"Median filter — salt-and-pepper noise removed (kernel {kernel_size})")
        techniques_applied.append({"name": "Median Filter", "params": f"kernel={kernel_size}"})

    # ── MODULE 3: Edge detection ──────────────────────────────────────────────
    if edge_mode == "Canny Edges":
        processed = canny_edges(clean_for_edges, t1, t2)
        findings.append(f"Canny edge detection — thresholds T1={t1}, T2={t2}")
        techniques_applied.append({"name": "Canny Edge Detection",
                                    "params": f"threshold1={t1}, threshold2={t2}"})

    elif edge_mode == "Sobel Edges":
        processed, _, _, _ = sobel_edges(clean_for_edges)
        findings.append("Sobel edge detection — directional gradients computed")
        findings.append("  Red=vertical edges (X gradient) | Blue=horizontal (Y gradient)")
        techniques_applied.append({"name": "Sobel Edge Detection",
                                    "params": "ksize=3, colour-coded XY gradients"})

    elif edge_mode == "Contours":
        processed, obj_count, areas, impact_count = detect_contours(clean_for_edges, min_area)
        contour_count_val = obj_count
        contour_areas_val = areas
        findings.append(f"Contour detection: {obj_count} object(s) found (min area={min_area}px)")
        if impact_count > 0:
            findings.append(f"  ⚠ POTENTIAL IMPACT POINTS: {impact_count} circular region(s) detected")
            findings.append("  Circularity ratio threshold > 0.65 (perfect circle = 1.0)")
        if areas:
            findings.append(
                f"  Largest: {max(areas):.0f}px | Smallest: {min(areas):.0f}px | "
                f"Avg: {sum(areas)/len(areas):.0f}px"
            )
        techniques_applied.append({"name": "Contour + Impact Detection",
                                    "params": f"min_area={min_area}px, circularity=0.65"})

    elif edge_mode == "Thresholding":
        processed = threshold_image(processed, threshold_val)
        findings.append(f"Binary thresholding — value={threshold_val}")
        techniques_applied.append({"name": "Binary Thresholding",
                                    "params": f"threshold={threshold_val}, THRESH_BINARY"})

    # ── MODULE 4: Colour segmentation ────────────────────────────────────────
    if enable_color:
        lower     = np.array([h_min, s_min, v_min])
        upper     = np.array([h_max, s_max, v_max])
        processed, mask_cv, stain_count, coverage = segment_color(
            clean_for_edges.copy(), lower, upper
        )
        stain_coverage_val = coverage
        stain_count_val    = stain_count
        findings.append(f"Blood stain detection: {stain_count} region(s) identified")
        findings.append(f"  Coverage: {coverage:.4f}% of image area")
        pixel_count = int(coverage / 100 * image_np.shape[0] * image_np.shape[1])
        findings.append(
            f"  Matching pixels: {pixel_count:,} | "
            f"HSV H({h_min}-{h_max}) S({s_min}-{s_max}) V({v_min}-{v_max})"
        )
        sev = ("TRACE" if coverage < 0.5 else "MINOR" if coverage < 3
               else "MODERATE" if coverage < 10 else "SIGNIFICANT" if coverage < 25
               else "EXTENSIVE")
        findings.append(f"  Severity estimate: {sev}")
        techniques_applied.append({"name": "HSV Multi-Range Segmentation",
                                    "params": f"4 blood ranges + user H({h_min}-{h_max})"})

    # ── MODULE 5: Face detection ──────────────────────────────────────────────
    face_count = 0
    if apply_face:
        face_input = clean_for_edges.copy()
        if len(face_input.shape) == 2:
            face_input = cv2.cvtColor(face_input, cv2.COLOR_GRAY2BGR)
        processed, face_count, face_details_list = detect_faces(face_input)
        findings.append(f"Face detection: {face_count} face(s) identified")
        for fd in face_details_list:
            x, y, fw, fh = fd["bbox"]
            conf = f"{fd['confidence']:.1%}" if fd["confidence"] else fd["method"]
            findings.append(
                f"  Face #{fd['id']}: {fd['method']} | "
                f"confidence={conf} | position={fd['position']}"
            )
        techniques_applied.append({"name": "Face Detection (YuNet + Haar)",
                                    "params": "DNN confidence>75%, Haar minNeighbors=8"})

    # Composite: stain borders on top of face output
    if enable_color and apply_face and mask_cv is not None and face_details_list:
        stain_c, _ = cv2.findContours(mask_cv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(processed, stain_c, -1, (0, 0, 255), 2)

    # Save to session for report page
    st.session_state["last_findings"]       = findings
    st.session_state["last_techniques"]     = techniques_applied
    st.session_state["last_face_details"]   = face_details_list
    st.session_state["last_stain_coverage"] = stain_coverage_val
    st.session_state["last_stain_count"]    = stain_count_val
    st.session_state["last_contour_count"]  = contour_count_val
    st.session_state["last_contour_areas"]  = contour_areas_val

    # ── Display results ───────────────────────────────────────────────────────
    st.markdown("""
    <p style='font-family:"Courier New",monospace;font-size:9px;letter-spacing:4px;
              color:#CC0000;text-transform:uppercase;margin:24px 0 4px;'>
        ▌ ANALYSIS OUTPUT
    </p>
    """, unsafe_allow_html=True)

    processed_display = (
        cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        if len(processed.shape) == 3 else processed
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='img-section-label'>🖼 ORIGINAL EVIDENCE</div>",
                    unsafe_allow_html=True)
        st.image(image_np, use_container_width=True)
    with col2:
        st.markdown("<div class='img-section-label'>🔬 ANALYZED OUTPUT</div>",
                    unsafe_allow_html=True)
        st.image(processed_display, use_container_width=True)

    if enable_color and mask_cv is not None:
        st.markdown("<hr style='border:1px solid #1a1a1a;margin:24px 0;'>",
                    unsafe_allow_html=True)
        st.markdown("<div class='img-section-label'>🩸 STAIN DETECTION MASK</div>",
                    unsafe_allow_html=True)
        st.image(mask_cv, use_container_width=True, clamp=True)

    # ── Findings log ──────────────────────────────────────────────────────────
    st.markdown("<hr style='border:1px solid #1a1a1a;margin:32px 0;'>",
                unsafe_allow_html=True)
    st.markdown("""
    <p style='font-family:"Courier New",monospace;font-size:9px;letter-spacing:4px;
              color:#CC0000;text-transform:uppercase;margin-bottom:12px;'>
        ▌ FINDINGS LOG
    </p>
    """, unsafe_allow_html=True)

    if findings:
        findings_html = ""
        for f in findings:
            cls    = "sub"  if f.startswith("  ") else "main"
            prefix = "└─"   if f.startswith("  ") else "▶"
            findings_html += (
                f"<div class='findings-entry {cls}'>"
                f"{prefix} {f.strip()}</div>"
            )
        st.markdown(f"<div class='case-form'>{findings_html}</div>",
                    unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='case-form'>
            <p style='font-family:"Courier New",monospace;font-size:12px;color:#333;'>
                No techniques applied yet — enable modules from the sidebar.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── Report generation ─────────────────────────────────────────────────────
    st.markdown("<hr style='border:1px solid #1a1a1a;margin:32px 0;'>",
                unsafe_allow_html=True)

    from modules.reports import generate_pdf_report
    if st.button("📄 GENERATE FORENSIC REPORT", key="gen_report_btn"):
        with st.spinner("Compiling classified report..."):
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
                case_info          = st.session_state.get("case_info", {}),
            )
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_name = f"TraceLens_CaseReport_{ts}.pdf"
        st.download_button(
            label     = "⬇ DOWNLOAD CLASSIFIED REPORT (PDF)",
            data      = pdf_bytes,
            file_name = pdf_name,
            mime      = "application/pdf",
            key       = "download_report_btn",
        )
        st.success(f"Report compiled — {pdf_name}")