import streamlit as st
from theme import inject_theme, tape_divider, section_header
from datetime import datetime


def render():
    inject_theme("Report")

    st.markdown("""
    <style>
    .report-meta-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1px;
        background: #1a1a1a;
        margin: 20px 0;
    }
    .meta-cell {
        background: #0d0d0d;
        padding: 16px 20px;
    }
    .meta-label {
        font-family: var(--font-mono);
        font-size: 9px;
        letter-spacing: 3px;
        color: var(--blood-bright);
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .meta-value {
        font-family: var(--font-type);
        font-size: 14px;
        color: var(--text);
    }
    .findings-summary {
        background: #080808;
        border: 1px solid #1a1a1a;
        border-left: 3px solid var(--green);
        padding: 20px;
        margin: 16px 0;
    }
    </style>

    <div style="padding:40px 40px 20px;">
        <p style="font-family:var(--font-mono);font-size:10px;letter-spacing:4px;color:var(--blood-bright);margin-bottom:8px;">
            [ CASE REPORT // CLASSIFIED OUTPUT ]
        </p>
        <h1 style="font-family:var(--font-horror);font-size:48px;color:#fff;text-shadow:0 0 20px rgba(204,0,0,0.3);">
            Forensic Report
        </h1>
    </div>
    """, unsafe_allow_html=True)

    tape_divider()

    # Check if analysis has been run
    if "last_findings" not in st.session_state:
        st.markdown("""
        <div style='text-align:center;padding:60px;'>
            <p style='font-family:var(--font-head);font-size:14px;letter-spacing:4px;color:white;text-transform:uppercase;'>
                No analysis data found
            </p>
            <p style='font-family:var(--font-mono);font-size:12px;color:white;margin-top:8px;'>
                Run an analysis on the Analyze page first, then return here to generate the report.
            </p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("GO TO ANALYZE →", key="report_goto_analyze", use_container_width=True):
                st.session_state.current_page = "Analyze"
                st.session_state["sidebar_expanded"] = True
                st.rerun()
        return

    case_info   = st.session_state.get("case_info", {})
    findings    = st.session_state.get("last_findings", [])
    techniques  = st.session_state.get("last_techniques", [])
    coverage    = st.session_state.get("last_stain_coverage")
    stain_count = st.session_state.get("last_stain_count")
    face_details = st.session_state.get("last_face_details", [])

    # Case metadata
    section_header("🗂", "Case Metadata")
    st.markdown(f"""
    <div class="report-meta-grid">
        <div class="meta-cell">
            <div class="meta-label">Case Number</div>
            <div class="meta-value">{case_info.get('case_number','—') or '—'}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-label">Evidence File</div>
            <div class="meta-value">{case_info.get('filename','—')}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-label">Victim / Subject</div>
            <div class="meta-value">{case_info.get('victim_name','—') or '—'}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-label">Suspect</div>
            <div class="meta-value">{case_info.get('suspect_name','—') or '—'}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-label">Location</div>
            <div class="meta-value">{case_info.get('location','—') or '—'}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-label">Investigating Officer</div>
            <div class="meta-value">{case_info.get('investigator','—') or '—'}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-label">Incident Date</div>
            <div class="meta-value">{case_info.get('incident_date','—') or '—'}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-label">Analysis Timestamp</div>
            <div class="meta-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if case_info.get("scene_description"):
        st.markdown(f"""
        <div class="findings-summary">
            <div style="font-family:var(--font-mono);font-size:9px;letter-spacing:3px;color:var(--gold);margin-bottom:10px;">SCENE DESCRIPTION</div>
            <p style="font-family:var(--font-type);font-size:14px;color:var(--text);line-height:1.8;">{case_info['scene_description']}</p>
        </div>
        """, unsafe_allow_html=True)

    tape_divider()

    # Findings summary
    section_header("📋", "Analysis Findings")
    if findings:
        findings_html = ""
        for f in findings:
            cls = "sub" if f.startswith("  ") else "main"
            prefix = "└─" if f.startswith("  ") else "▶"
            color = "#00FF99" if cls == "main" else "#555"
            padding = "0" if cls == "main" else "20px"
            findings_html += f"<div style='font-family:var(--font-mono);font-size:12px;line-height:1.9;color:{color};padding-left:{padding};'>{prefix} {f.strip()}</div>"
        st.markdown(f"<div class='findings-summary'>{findings_html}</div>", unsafe_allow_html=True)
    tape_divider()

    # Generate PDF
    section_header("📄", "Download Report", "Full classified forensic PDF")

    import base64, io as _io
    import cv2
    import numpy as np
    from PIL import Image as PILImage
    from modules.reports import generate_pdf_report

    def _decode(b64str):
        if not b64str: return None
        data = base64.b64decode(b64str)
        img  = PILImage.open(_io.BytesIO(data)).convert("RGB")
        arr  = np.array(img)
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    orig_cv = _decode(st.session_state.get("last_original_b64"))
    proc_cv = _decode(st.session_state.get("last_processed_b64"))
    mask_cv_b64 = st.session_state.get("last_mask_b64")
    mask_decoded = None
    if mask_cv_b64:
        data = base64.b64decode(mask_cv_b64)
        mask_pil = PILImage.open(_io.BytesIO(data)).convert("L")
        mask_decoded = np.array(mask_pil)

    pdf_bytes = st.session_state.get("generated_pdf_bytes")
    pdf_name  = st.session_state.get("generated_pdf_name", "TraceLens_Report.pdf")

    if pdf_bytes:
        st.download_button(
            label     = "⬇ DOWNLOAD CLASSIFIED REPORT (PDF)",
            data      = pdf_bytes,
            file_name = pdf_name,
            mime      = "application/pdf",
        )
        st.success("Report ready for download.")
    else:
        st.markdown("""
        <div style='text-align:center;padding:40px;'>
            <p style='font-family:var(--font-mono);font-size:12px;color:#555;'>
                No report generated yet. Go to Analyze page and click Generate Report.
            </p>
        </div>
        """, unsafe_allow_html=True)