import cv2
import io
import os
import tempfile
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
 
 
# ── Colour palette ────────────────────────────────────────────────────────────
BLACK      = colors.HexColor("#0a0a0a")
DARK_GREY  = colors.HexColor("#1a1a1a")
MID_GREY   = colors.HexColor("#333333")
LIGHT_GREY = colors.HexColor("#cccccc")
WHITE      = colors.white
GOLD       = colors.HexColor("#FFD700")
RED        = colors.HexColor("#CC0000")
GREEN      = colors.HexColor("#00AA44")
CYAN       = colors.HexColor("#00CCCC")
BORDER     = colors.HexColor("#444444")
 
 
# ── Style helpers ─────────────────────────────────────────────────────────────
def _styles():
    base = {"fontName": "Courier", "textColor": colors.HexColor("#e0e0e0")}
 
    return {
        "cover_title": ParagraphStyle("cover_title",
            fontName="Courier-Bold", fontSize=22, textColor=GOLD,
            alignment=TA_CENTER, spaceAfter=6, leading=28),
 
        "cover_sub": ParagraphStyle("cover_sub",
            fontName="Courier", fontSize=10, textColor=LIGHT_GREY,
            alignment=TA_CENTER, spaceAfter=4, leading=14),
 
        "section_header": ParagraphStyle("section_header",
            fontName="Courier-Bold", fontSize=13, textColor=GOLD,
            spaceAfter=6, spaceBefore=14, leading=16,
            borderPad=4, leftIndent=0),
 
        "field_label": ParagraphStyle("field_label",
            fontName="Courier-Bold", fontSize=9, textColor=GOLD,
            spaceAfter=1, leading=12),
 
        "field_value": ParagraphStyle("field_value",
            fontName="Courier", fontSize=9, textColor=colors.HexColor("#e0e0e0"),
            spaceAfter=6, leading=12),
 
        "finding_item": ParagraphStyle("finding_item",
            fontName="Courier", fontSize=9, textColor=colors.HexColor("#00FF99"),
            spaceAfter=3, leading=13, leftIndent=12),
 
        "narrative": ParagraphStyle("narrative",
            fontName="Courier", fontSize=9, textColor=LIGHT_GREY,
            spaceAfter=8, leading=14, alignment=TA_JUSTIFY),
 
        "caption": ParagraphStyle("caption",
            fontName="Courier", fontSize=8, textColor=colors.HexColor("#888888"),
            alignment=TA_CENTER, spaceAfter=4),
 
        "warning": ParagraphStyle("warning",
            fontName="Courier-Bold", fontSize=9, textColor=RED,
            spaceAfter=4, leading=12),
 
        "table_header": ParagraphStyle("table_header",
            fontName="Courier-Bold", fontSize=8, textColor=GOLD,
            alignment=TA_CENTER),
 
        "table_cell": ParagraphStyle("table_cell",
            fontName="Courier", fontSize=8, textColor=LIGHT_GREY,
            alignment=TA_LEFT, leading=11),
    }
 
 
def _gold_rule():
    return HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=8, spaceBefore=4)
 
def _dim_rule():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6, spaceBefore=4)
 
 
def _cv_to_rl_image(cv_img, max_width_mm=170, max_height_mm=110):
    """Convert OpenCV BGR image to a ReportLab Image flowable."""
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB) if len(cv_img.shape) == 3 else cv_img
    from PIL import Image as PILImage
    pil = PILImage.fromarray(rgb)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    buf.seek(0)
 
    ih, iw = cv_img.shape[:2]
    max_w = max_width_mm * mm
    max_h = max_height_mm * mm
    scale = min(max_w / iw, max_h / ih, 1.0)
    return RLImage(buf, width=iw * scale, height=ih * scale)
 
 
def _dark_table(data, col_widths, has_header=True):
    """Build a dark-themed ReportLab table."""
    t = Table(data, colWidths=col_widths)
    style = [
        ("BACKGROUND",  (0, 0), (-1, 0 if has_header else -1), DARK_GREY),
        ("TEXTCOLOR",   (0, 0), (-1, -1), LIGHT_GREY),
        ("FONTNAME",    (0, 0), (-1, -1), "Courier"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("GRID",        (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1 if has_header else 0), (-1, -1),
            [colors.HexColor("#111111"), colors.HexColor("#181818")]),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0),(-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]
    if has_header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), MID_GREY),
            ("TEXTCOLOR",  (0, 0), (-1, 0), GOLD),
            ("FONTNAME",   (0, 0), (-1, 0), "Courier-Bold"),
            ("LINEBELOW",  (0, 0), (-1, 0), 1, GOLD),
        ]
    t.setStyle(TableStyle(style))
    return t
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────
 
def generate_pdf_report(
    original_cv,
    processed_cv,
    findings: list,
    filename: str = "unknown",
    face_details: list = None,
    stain_coverage: float = None,
    stain_count: int = None,
    contour_count: int = None,
    contour_areas: list = None,
    techniques_applied: list = None,
    mask_cv=None,
) -> bytes:
    """
    Build a full forensic PDF report and return it as bytes
    (for st.download_button).
    """
    buf = io.BytesIO()
    W, H = A4
    margin = 18 * mm
 
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin,
        title="TraceLens Forensic Report",
        author="TraceLens DIP System",
    )
 
    S = _styles()
    story = []
    ts = datetime.now()
    case_id = f"TL-{ts.strftime('%Y%m%d-%H%M%S')}"
 
    # ══════════════════════════════════════════════════════════════════════
    # PAGE 1 — COVER
    # ══════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 20 * mm))
    story.append(_gold_rule())
    story.append(Paragraph("🔍  TRACELENS", S["cover_title"]))
    story.append(Paragraph("FORENSIC DIGITAL IMAGE ANALYSIS REPORT", S["cover_title"]))
    story.append(_gold_rule())
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("DIGITAL IMAGE PROCESSING SYSTEM — CLASSIFIED", S["cover_sub"]))
    story.append(Paragraph("FOR LAW ENFORCEMENT USE ONLY", S["cover_sub"]))
    story.append(Spacer(1, 10 * mm))
 
    # Case metadata table
    meta_data = [
        ["CASE ID",       case_id,                   "CLASSIFICATION",  "RESTRICTED"],
        ["EVIDENCE FILE", filename.upper(),           "REPORT DATE",     ts.strftime("%Y-%m-%d")],
        ["ANALYSIS TIME", ts.strftime("%H:%M:%S"),    "SYSTEM VERSION",  "TraceLens v2.0"],
        ["STATUS",        "ANALYSIS COMPLETE",        "PAGE COUNT",      "AUTO-GENERATED"],
    ]
    meta_table_data = []
    for row in meta_data:
        meta_table_data.append([
            Paragraph(row[0], S["field_label"]),
            Paragraph(row[1], S["field_value"]),
            Paragraph(row[2], S["field_label"]),
            Paragraph(row[3], S["field_value"]),
        ])
 
    meta_t = Table(meta_table_data, colWidths=[38*mm, 55*mm, 42*mm, 40*mm])
    meta_t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), DARK_GREY),
        ("GRID",         (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1),
             [colors.HexColor("#111111"), colors.HexColor("#181818")]),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 8 * mm))
 
    # Executive summary box
    findings_count = len([f for f in findings if f])
    techniques_count = len(techniques_applied) if techniques_applied else 0
    face_count = len(face_details) if face_details else 0
 
    exec_lines = [
        f"This report documents the automated forensic image analysis performed by TraceLens",
        f"on evidence file '{filename}'. A total of {techniques_count} image processing",
        f"technique(s) were applied and {findings_count} finding(s) were recorded.",
    ]
    if face_count:
        exec_lines.append(f"{face_count} human face(s) were detected in the evidence image.")
    if stain_coverage is not None and stain_coverage > 0:
        exec_lines.append(
            f"Colour-based stain analysis identified {stain_count} region(s) covering "
            f"{stain_coverage:.2f}% of the image area."
        )
    if contour_count:
        exec_lines.append(
            f"Object boundary analysis detected {contour_count} significant contour(s)."
        )
 
    exec_box = Table(
        [[Paragraph("EXECUTIVE SUMMARY", S["field_label"])],
         [Paragraph(" ".join(exec_lines), S["narrative"])]],
        colWidths=[W - 2 * margin]
    )
    exec_box.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#0f0f0f")),
        ("BOX",         (0, 0), (-1, -1), 1, GOLD),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0,0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",(0, 0), (-1, -1), 10),
    ]))
    story.append(exec_box)
    story.append(PageBreak())
 
    # ══════════════════════════════════════════════════════════════════════
    # PAGE 2 — ORIGINAL vs PROCESSED IMAGES
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 1 — EVIDENCE IMAGERY", S["section_header"]))
    story.append(_gold_rule())
 
    orig_rl  = _cv_to_rl_image(original_cv,  max_width_mm=83, max_height_mm=90)
    proc_rl  = _cv_to_rl_image(processed_cv, max_width_mm=83, max_height_mm=90)
 
    img_table = Table(
        [[orig_rl, proc_rl],
         [Paragraph("FIG 1 — ORIGINAL EVIDENCE", S["caption"]),
          Paragraph("FIG 2 — PROCESSED OUTPUT",  S["caption"])]],
        colWidths=[(W - 2 * margin) / 2 - 3 * mm,
                   (W - 2 * margin) / 2 - 3 * mm],
        hAlign="CENTER"
    )
    img_table.setStyle(TableStyle([
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("GRID",         (0, 0), (-1, 0),  0.5, BORDER),
        ("BACKGROUND",   (0, 0), (-1, 0),  colors.HexColor("#0d0d0d")),
    ]))
    story.append(img_table)
 
    if mask_cv is not None:
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph("STAIN DETECTION MASK", S["field_label"]))
        story.append(_cv_to_rl_image(mask_cv, max_width_mm=100, max_height_mm=70))
        story.append(Paragraph("FIG 3 — HSV STAIN SEGMENTATION MASK", S["caption"]))
 
    story.append(_dim_rule())
 
    # Image technical metadata
    oh, ow = original_cv.shape[:2]
    ph, pw = processed_cv.shape[:2]
    total_pixels = oh * ow
 
    img_meta = [
        ["PROPERTY", "ORIGINAL", "PROCESSED"],
        ["Dimensions",    f"{ow} x {oh} px",    f"{pw} x {ph} px"],
        ["Total Pixels",  f"{total_pixels:,}",   f"{pw*ph:,}"],
        ["Colour Mode",   "BGR (colour)",
            "BGR / Grayscale" if len(processed_cv.shape) == 2 else "BGR (colour)"],
        ["File",          filename,               "In-memory (processed)"],
    ]
    story.append(_dark_table(img_meta, [55*mm, 60*mm, 60*mm]))
    story.append(PageBreak())
 
    # ══════════════════════════════════════════════════════════════════════
    # PAGE 3 — TECHNIQUES APPLIED + FINDINGS
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 2 — PROCESSING PIPELINE", S["section_header"]))
    story.append(_gold_rule())
 
    story.append(Paragraph(
        "The following image processing operations were applied to the evidence "
        "in the order listed. Each technique modifies the working copy of the image "
        "or extracts analytical data for the findings log.",
        S["narrative"]
    ))
 
    if techniques_applied:
        tech_data = [["#", "TECHNIQUE", "PARAMETERS / NOTES"]]
        for i, tech in enumerate(techniques_applied, 1):
            tech_data.append([str(i), tech.get("name", "—"), tech.get("params", "—")])
        story.append(_dark_table(tech_data, [10*mm, 65*mm, 95*mm]))
    else:
        story.append(Paragraph("No processing techniques were recorded.", S["narrative"]))
 
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("SECTION 3 — ANALYTICAL FINDINGS", S["section_header"]))
    story.append(_gold_rule())
 
    if findings:
        for f in findings:
            story.append(Paragraph(f"▶  {f}", S["finding_item"]))
    else:
        story.append(Paragraph("No findings were recorded.", S["narrative"]))
 
    story.append(Spacer(1, 8 * mm))
 
    # ── Face detection detail ─────────────────────────────────────────────
    if face_details:
        story.append(KeepTogether([
            Paragraph("SECTION 4 — FACE DETECTION DETAIL", S["section_header"]),
            _gold_rule(),
            Paragraph(
                f"{len(face_details)} face(s) were detected using a multi-method cascade "
                "(DNN ResNet-SSD + Haar cascades). Each detected region is listed below "
                "with bounding-box coordinates, detection confidence, and image position.",
                S["narrative"]
            ),
        ]))
 
        face_table_data = [["ID", "METHOD", "CONFIDENCE", "BBOX (x,y,w,h)", "POSITION"]]
        for fd in face_details:
            x, y, fw, fh = fd["bbox"]
            conf = f"{fd['confidence']:.1%}" if fd["confidence"] else "N/A"
            face_table_data.append([
                f"#{fd['id']}",
                fd["method"],
                conf,
                f"({x}, {y}, {fw}, {fh})",
                fd.get("position", "—"),
            ])
        story.append(_dark_table(face_table_data, [12*mm, 28*mm, 24*mm, 52*mm, 34*mm]))
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(
            "NOTE: DNN detections include a confidence score (0–100%). "
            "Haar-based detections are threshold-based and do not produce a "
            "probability score. Detections below 45% confidence were suppressed.",
            S["narrative"]
        ))
 
    # ── Stain detection detail ────────────────────────────────────────────
    if stain_coverage is not None:
        section_num = 5 if face_details else 4
        story.append(KeepTogether([
            Paragraph(f"SECTION {section_num} — STAIN / COLOUR SEGMENTATION DETAIL",
                      S["section_header"]),
            _gold_rule(),
        ]))
        stain_rows = [
            ["METRIC", "VALUE", "INTERPRETATION"],
            ["Regions detected",
             str(stain_count) if stain_count is not None else "—",
             "Distinct contiguous colour-matched areas"],
            ["Coverage",
             f"{stain_coverage:.4f}%",
             "Percentage of total image pixels matching target HSV range"],
            ["Pixel count",
             f"{int(stain_coverage / 100 * oh * ow):,}" if stain_coverage else "—",
             "Approximate number of matching pixels"],
            ["Severity estimate",
             _stain_severity(stain_coverage),
             "Based on coverage percentage thresholds"],
        ]
        story.append(_dark_table(stain_rows, [45*mm, 35*mm, 90*mm]))
 
    # ── Contour detail ────────────────────────────────────────────────────
    if contour_count is not None:
        section_num = (6 if face_details else 5) if stain_coverage is not None else (5 if face_details else 4)
        story.append(KeepTogether([
            Paragraph(f"SECTION {section_num} — OBJECT / CONTOUR ANALYSIS", S["section_header"]),
            _gold_rule(),
        ]))
        story.append(Paragraph(
            f"{contour_count} significant object contour(s) were identified after "
            "applying Canny edge detection internally. Contours below the minimum "
            "area threshold were discarded as noise.",
            S["narrative"]
        ))
        if contour_areas:
            contour_rows = [["CONTOUR #", "AREA (px)", "RELATIVE SIZE"]]
            max_a = max(contour_areas)
            for i, area in enumerate(sorted(contour_areas, reverse=True), 1):
                rel = "Large" if area > 0.5 * max_a else ("Medium" if area > 0.15 * max_a else "Small")
                contour_rows.append([f"#{i}", f"{int(area):,}", rel])
            story.append(_dark_table(contour_rows, [25*mm, 40*mm, 40*mm]))
 
    story.append(PageBreak())
 
    # ══════════════════════════════════════════════════════════════════════
    # PAGE 4 — DISCLAIMER + SIGNATURE BLOCK
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION — NOTES & DISCLAIMERS", S["section_header"]))
    story.append(_gold_rule())
 
    disclaimers = [
        "This report was generated automatically by the TraceLens Digital Image Processing System.",
        "All analysis is performed using classical computer vision algorithms (OpenCV). Results "
        "should be treated as investigative aids and not as conclusive forensic evidence without "
        "independent verification by a qualified forensic examiner.",
        "Face detection employs DNN-based (ResNet-SSD) and Haar-cascade methods. Detection "
        "accuracy is dependent on image quality, resolution, and subject orientation.",
        "Colour-based stain segmentation is tuned for dark-red/brownish-red regions (dried "
        "blood approximation). Environmental lighting, image compression, and surface texture "
        "may affect accuracy. Results should be confirmed with chemical testing.",
        "This document is classified RESTRICTED. Unauthorised distribution is prohibited.",
    ]
    for d in disclaimers:
        story.append(Paragraph(d, S["narrative"]))
 
    story.append(Spacer(1, 10 * mm))
    story.append(_gold_rule())
    story.append(Paragraph("AUTHORISATION & CHAIN OF CUSTODY", S["section_header"]))
 
    sig_data = [
        ["ROLE", "NAME / ID", "SIGNATURE", "DATE"],
        ["Analyst",         "_______________________", "____________________", ts.strftime("%Y-%m-%d")],
        ["Supervising Officer", "___________________", "____________________", "____________"],
        ["Evidence Custodian",  "___________________", "____________________", "____________"],
    ]
    story.append(_dark_table(sig_data, [40*mm, 55*mm, 50*mm, 30*mm]))
 
    story.append(Spacer(1, 8 * mm))
    story.append(_gold_rule())
    story.append(Paragraph(
        f"END OF REPORT  ·  CASE {case_id}  ·  GENERATED {ts.strftime('%Y-%m-%d %H:%M:%S')}",
        S["cover_sub"]
    ))
    story.append(_gold_rule())
 
    # ── Build with dark page background ──────────────────────────────────
    def _dark_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#0a0a0a"))
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        # Page number
        canvas.setFont("Courier", 7)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawCentredString(A4[0] / 2, 12 * mm,
            f"TRACELENS FORENSIC REPORT  |  {case_id}  |  PAGE {doc.page}")
        canvas.restoreState()
 
    doc.build(story, onFirstPage=_dark_bg, onLaterPages=_dark_bg)
    return buf.getvalue()
 
 
def _stain_severity(coverage: float) -> str:
    if coverage < 0.5:   return "Trace / Minimal"
    if coverage < 3.0:   return "Minor"
    if coverage < 10.0:  return "Moderate"
    if coverage < 25.0:  return "Significant"
    return "Extensive"