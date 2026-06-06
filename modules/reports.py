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
ORANGE     = colors.HexColor("#FF8C00")


# ── Style helpers ─────────────────────────────────────────────────────────────
def _styles():
    return {
        "cover_title": ParagraphStyle("cover_title",
            fontName="Courier-Bold", fontSize=22, textColor=GOLD,
            alignment=TA_CENTER, spaceAfter=6, leading=28),
        "cover_sub": ParagraphStyle("cover_sub",
            fontName="Courier", fontSize=10, textColor=LIGHT_GREY,
            alignment=TA_CENTER, spaceAfter=4, leading=14),
        "section_header": ParagraphStyle("section_header",
            fontName="Courier-Bold", fontSize=13, textColor=GOLD,
            spaceAfter=6, spaceBefore=14, leading=16),
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
        "conclusion_title": ParagraphStyle("conclusion_title",
            fontName="Courier-Bold", fontSize=11, textColor=GOLD,
            spaceAfter=4, leading=14),
        "conclusion_item": ParagraphStyle("conclusion_item",
            fontName="Courier", fontSize=9, textColor=colors.HexColor("#e0e0e0"),
            spaceAfter=5, leading=13, leftIndent=16),
        "score_label": ParagraphStyle("score_label",
            fontName="Courier-Bold", fontSize=10, textColor=CYAN,
            spaceAfter=2, leading=13, alignment=TA_CENTER),
    }


def _gold_rule():
    return HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=8, spaceBefore=4)

def _dim_rule():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6, spaceBefore=4)


def _cv_to_rl_image(cv_img, max_width_mm=170, max_height_mm=110):
    if cv_img is None:
        return None
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


def _confidence_bar_text(confidence):
    """Return a simple ASCII confidence bar."""
    filled = int(confidence * 20)
    bar = "█" * filled + "░" * (20 - filled)
    return f"[{bar}] {confidence:.0%}"


def _stain_severity(coverage: float) -> str:
    if coverage < 0.5:  return "Trace / Minimal"
    if coverage < 3.0:  return "Minor"
    if coverage < 10.0: return "Moderate"
    if coverage < 25.0: return "Significant"
    return "Extensive"


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
    case_info: dict = None,
    # ── New forensic module results ───────────────────────────────────────
    spatter_results: dict = None,
    weapon_results: dict = None,
    injury_results: dict = None,
    pose_results: dict = None,
    spatter_cv=None,
    weapon_cv=None,
    injury_cv=None,
    pose_cv=None,
) -> bytes:

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

    S  = _styles()
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

    findings_count    = len([f for f in findings if f])
    techniques_count  = len(techniques_applied) if techniques_applied else 0
    face_count        = len(face_details) if face_details else 0
    forensic_modules  = sum([
        spatter_results is not None,
        weapon_results  is not None,
        injury_results  is not None,
        pose_results    is not None,
    ])

    exec_lines = [
        f"This report documents automated forensic image analysis performed by TraceLens "
        f"on evidence file '{filename}'. {techniques_count} processing technique(s) applied, "
        f"{findings_count} finding(s) recorded, {forensic_modules} advanced forensic module(s) run.",
    ]
    if face_count:
        exec_lines.append(f"{face_count} human subject(s) detected.")
    if stain_coverage is not None and stain_coverage > 0:
        exec_lines.append(
            f"Stain analysis: {stain_count} region(s), {stain_coverage:.2f}% coverage.")
    if spatter_results:
        exec_lines.append(f"Blood spatter: {spatter_results.get('pattern_type','—')}.")
    if injury_results:
        exec_lines.append(f"Injury localization: {injury_results.get('overall_severity','—')} severity.")
    if pose_results:
        exec_lines.append(f"Body posture: {pose_results.get('posture','—')}.")

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

    if case_info and any(case_info.values()):
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph("CASE INFORMATION", S["field_label"]))
        ci = case_info
        ci_data = [
            ["CASE NUMBER",    ci.get("case_number",  "—") or "—",
             "INCIDENT DATE",  ci.get("incident_date","—") or "—"],
            ["VICTIM / SUBJECT", ci.get("victim_name","—") or "—",
             "SUSPECT",        ci.get("suspect_name", "—") or "—"],
            ["LOCATION",       ci.get("location",     "—") or "—",
             "INVESTIGATOR",   ci.get("investigator",  "—") or "—"],
        ]
        ci_rows = []
        for row in ci_data:
            ci_rows.append([
                Paragraph(row[0], S["field_label"]),
                Paragraph(row[1], S["field_value"]),
                Paragraph(row[2], S["field_label"]),
                Paragraph(row[3], S["field_value"]),
            ])
        ci_table = Table(ci_rows, colWidths=[38*mm, 55*mm, 38*mm, 44*mm])
        ci_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#0f0f0f")),
            ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        story.append(ci_table)
        desc = ci.get("scene_description", "")
        if desc:
            story.append(Spacer(1, 4 * mm))
            story.append(Paragraph("SCENE DESCRIPTION", S["field_label"]))
            story.append(Paragraph(desc, S["narrative"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # PAGE 2 — EVIDENCE IMAGERY
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 1 — EVIDENCE IMAGERY", S["section_header"]))
    story.append(_gold_rule())

    orig_rl = _cv_to_rl_image(original_cv,  max_width_mm=83, max_height_mm=90)
    proc_rl = _cv_to_rl_image(processed_cv, max_width_mm=83, max_height_mm=90)

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
    oh, ow = original_cv.shape[:2]
    ph, pw = processed_cv.shape[:2]
    img_meta = [
        ["PROPERTY", "ORIGINAL", "PROCESSED"],
        ["Dimensions",   f"{ow} x {oh} px",  f"{pw} x {ph} px"],
        ["Total Pixels", f"{oh*ow:,}",        f"{ph*pw:,}"],
        ["Colour Mode",  "BGR (colour)",
            "BGR / Grayscale" if len(processed_cv.shape) == 2 else "BGR (colour)"],
        ["File",         filename,             "In-memory (processed)"],
    ]
    story.append(_dark_table(img_meta, [55*mm, 60*mm, 60*mm]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # PAGE 3 — PROCESSING PIPELINE + BASE FINDINGS
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 2 — PROCESSING PIPELINE", S["section_header"]))
    story.append(_gold_rule())
    story.append(Paragraph(
        "The following image processing operations were applied in order.",
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
    story.append(Paragraph("SECTION 3 — BASE ANALYTICAL FINDINGS", S["section_header"]))
    story.append(_gold_rule())
    if findings:
        for f in findings:
            story.append(Paragraph(f"▶  {f}", S["finding_item"]))
    else:
        story.append(Paragraph("No findings were recorded.", S["narrative"]))

    if face_details:
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph("FACE / SUBJECT DETECTION DETAIL", S["field_label"]))
        face_table_data = [["ID", "METHOD", "CONFIDENCE", "BBOX (x,y,w,h)", "POSITION"]]
        for fd in face_details:
            x, y, fw, fh = fd["bbox"]
            conf = f"{fd['confidence']:.1%}" if fd["confidence"] else "N/A"
            face_table_data.append([
                f"#{fd['id']}", fd["method"], conf,
                f"({x}, {y}, {fw}, {fh})", fd.get("position", "—"),
            ])
        story.append(_dark_table(face_table_data, [12*mm, 28*mm, 24*mm, 52*mm, 34*mm]))

    if stain_coverage is not None:
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph("STAIN DETECTION DETAIL", S["field_label"]))
        stain_rows = [
            ["METRIC", "VALUE", "INTERPRETATION"],
            ["Regions detected",  str(stain_count) if stain_count is not None else "—",
             "Distinct colour-matched areas"],
            ["Coverage",          f"{stain_coverage:.4f}%",
             "Percentage of total image pixels"],
            ["Severity estimate", _stain_severity(stain_coverage), "Threshold-based classification"],
        ]
        story.append(_dark_table(stain_rows, [45*mm, 35*mm, 90*mm]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # FORENSIC ANALYSIS SECTIONS (4–7)
    # ══════════════════════════════════════════════════════════════════════
    sec = 4

    # ── Section 4: Blood Spatter Analysis ────────────────────────────────
    if spatter_results:
        story.append(Paragraph(f"SECTION {sec} — BLOOD SPATTER PATTERN ANALYSIS", S["section_header"]))
        story.append(_gold_rule())
        sec += 1

        if spatter_cv is not None:
            img = _cv_to_rl_image(spatter_cv, max_width_mm=140, max_height_mm=80)
            if img:
                story.append(img)
                story.append(Paragraph("FIG — BLOOD SPATTER ANNOTATED OUTPUT", S["caption"]))
                story.append(Spacer(1, 4 * mm))

        sp = spatter_results
        spatter_data = [
            ["METRIC", "VALUE"],
            ["Pattern Type",         sp.get("pattern_type", "—")],
            ["Confidence",           _confidence_bar_text(sp.get("pattern_confidence", 0))],
            ["Velocity Class",       sp.get("velocity", "—")],
            ["Stain Count",          str(sp.get("stain_count", "—"))],
            ["Avg Stain Area",       f"{sp.get('avg_area_px', '—')} px"],
            ["Avg Circularity",      str(sp.get("avg_circularity", "—"))],
            ["Avg Aspect Ratio",     str(sp.get("avg_aspect_ratio", "—"))],
            ["Edge Serration Index", str(sp.get("edge_serration_index", "—"))],
            ["Origin Direction",     sp.get("origin_direction", "—")],
            ["Direction Confidence", _confidence_bar_text(sp.get("origin_confidence", 0))],
        ]
        story.append(_dark_table(spatter_data, [70*mm, 100*mm]))
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("FORENSIC INTERPRETATION:", S["field_label"]))
        story.append(Paragraph(sp.get("pattern_detail", "—"), S["narrative"]))
        story.append(PageBreak())

    # ── Section 5: Injury Localization ───────────────────────────────────
    if injury_results:
        story.append(Paragraph(f"SECTION {sec} — INJURY LOCALIZATION & SEVERITY MAPPING", S["section_header"]))
        story.append(_gold_rule())
        sec += 1

        if injury_cv is not None:
            img = _cv_to_rl_image(injury_cv, max_width_mm=140, max_height_mm=80)
            if img:
                story.append(img)
                story.append(Paragraph("FIG — INJURY LOCALIZATION MAP", S["caption"]))
                story.append(Spacer(1, 4 * mm))

        ir = injury_results
        story.append(Paragraph(
            f"Overall Severity: {ir.get('overall_severity','—')}  |  "
            f"Confidence: {ir.get('overall_confidence', 0):.0%}  |  "
            f"Regions with evidence: {ir.get('active_region_count', 0)}",
            S["field_label"]
        ))
        story.append(Spacer(1, 3 * mm))

        if ir.get("injury_summary"):
            inj_data = [["BODY REGION", "SEVERITY", "CONFIDENCE", "STAIN COUNT", "AREA %"]]
            for inj in ir["injury_summary"]:
                inj_data.append([
                    inj["region"],
                    inj["severity"],
                    f"{inj['confidence']:.0%}",
                    str(inj["stain_count"]),
                    f"{inj['area_pct']:.3f}%",
                ])
            t = _dark_table(inj_data, [55*mm, 28*mm, 26*mm, 26*mm, 25*mm])
            # Color critical rows red
            for i, inj in enumerate(ir["injury_summary"], 1):
                if inj["severity"] == "CRITICAL":
                    t.setStyle(TableStyle([("TEXTCOLOR", (1, i), (1, i), RED)]))
            story.append(t)

        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("FORENSIC INTERPRETATION:", S["field_label"]))
        story.append(Paragraph(ir.get("conclusion", "—"), S["narrative"]))
        story.append(PageBreak())

    # ── Section 6: Weapon Proximity ───────────────────────────────────────
    if weapon_results:
        story.append(Paragraph(f"SECTION {sec} — WEAPON-HAND PROXIMITY ANALYSIS", S["section_header"]))
        story.append(_gold_rule())
        sec += 1

        if weapon_cv is not None:
            img = _cv_to_rl_image(weapon_cv, max_width_mm=140, max_height_mm=80)
            if img:
                story.append(img)
                story.append(Paragraph("FIG — WEAPON PROXIMITY ANNOTATED OUTPUT", S["caption"]))
                story.append(Spacer(1, 4 * mm))

        wr = weapon_results
        story.append(Paragraph(
            f"Weapon-like objects detected: {wr.get('weapon_count', 0)}  |  "
            f"Overall confidence: {wr.get('confidence', 0):.0%}",
            S["field_label"]
        ))
        story.append(Spacer(1, 3 * mm))

        if wr.get("items"):
            wp_data = [["OBJ #", "DISTANCE (px)", "PROXIMITY CLASS", "CONFIDENCE", "NEAREST SUBJECT"]]
            for item in wr["items"]:
                wp_data.append([
                    f"#{item['weapon_id']}",
                    str(int(item["distance_px"])),
                    item["proximity_class"],
                    f"{item['confidence']:.0%}",
                    f"Face #{item['nearest_face_id']}" if item["nearest_face_id"] else "—",
                ])
            story.append(_dark_table(wp_data, [18*mm, 30*mm, 40*mm, 28*mm, 34*mm]))
            story.append(Spacer(1, 4 * mm))
            for item in wr["items"]:
                story.append(Paragraph(
                    f"Object #{item['weapon_id']}: {item['note']}", S["narrative"]
                ))

        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("FORENSIC INTERPRETATION:", S["field_label"]))
        story.append(Paragraph(wr.get("conclusion", "—"), S["narrative"]))
        story.append(PageBreak())

    # ── Section 7: Body Pose ──────────────────────────────────────────────
    if pose_results:
        story.append(Paragraph(f"SECTION {sec} — BODY POSE & SCENE CONSISTENCY ANALYSIS", S["section_header"]))
        story.append(_gold_rule())
        sec += 1

        if pose_cv is not None:
            img = _cv_to_rl_image(pose_cv, max_width_mm=140, max_height_mm=80)
            if img:
                story.append(img)
                story.append(Paragraph("FIG — BODY POSE ANNOTATED OUTPUT", S["caption"]))
                story.append(Spacer(1, 4 * mm))

        pr = pose_results
        pose_data = [
            ["METRIC", "VALUE"],
            ["Posture Classification",     pr.get("posture", "—")],
            ["Posture Confidence",         _confidence_bar_text(pr.get("posture_confidence", 0))],
            ["Face Orientation",           pr.get("orientation", "—")],
            ["Stain-Posture Consistency",  pr.get("stain_posture_consistency", "—")],
            ["Consistency Confidence",     _confidence_bar_text(pr.get("stain_consistency_confidence", 0))],
            ["Staging Probability",        f"{pr.get('staging_probability', 0):.0%}"],
            ["Scene Consistency Score",    f"{pr.get('scene_consistency_score', 0):.1f} / 100"],
        ]
        story.append(_dark_table(pose_data, [70*mm, 100*mm]))

        flags = pr.get("staging_flags", [])
        if flags:
            story.append(Spacer(1, 4 * mm))
            story.append(Paragraph("STAGING FLAGS DETECTED:", S["warning"]))
            for flag in flags:
                story.append(Paragraph(f"⚠  {flag}", S["warning"]))

        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("POSTURE NOTE:", S["field_label"]))
        story.append(Paragraph(pr.get("posture_note", "—"), S["narrative"]))
        story.append(Paragraph("STAIN CONSISTENCY NOTE:", S["field_label"]))
        story.append(Paragraph(pr.get("stain_note", "—"), S["narrative"]))
        story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # FINAL PAGE — FORENSIC CONCLUSION
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("FORENSIC CONCLUSION", S["section_header"]))
    story.append(_gold_rule())
    story.append(Paragraph(
        "The following conclusions are generated automatically from all active "
        "analysis modules. Each finding is accompanied by a confidence score. "
        "These results are investigative aids and must be verified by a qualified forensic examiner.",
        S["narrative"]
    ))
    story.append(Spacer(1, 4 * mm))

    conclusion_lines = []

    # Face
    if face_count > 0:
        conclusion_lines.append(f"• {face_count} human subject(s) detected in the scene.")

    # Blood
    if stain_coverage is not None and stain_coverage > 0:
        sev = _stain_severity(stain_coverage)
        conclusion_lines.append(
            f"• Blood/stain evidence detected: {stain_count} region(s), "
            f"{stain_coverage:.2f}% coverage — classified as {sev.upper()}."
        )

    # Spatter
    if spatter_results:
        conclusion_lines.append(
            f"• Blood spatter pattern: {spatter_results.get('pattern_type','—')} "
            f"(confidence: {spatter_results.get('pattern_confidence',0):.0%}). "
            f"Origin direction: {spatter_results.get('origin_direction','—')}."
        )

    # Injury
    if injury_results:
        crit = injury_results.get("critical_regions", [])
        if crit:
            conclusion_lines.append(
                f"• Major injury evidence in: {', '.join(crit)}. "
                f"Severity: {injury_results.get('overall_severity','—')} "
                f"(confidence: {injury_results.get('overall_confidence',0):.0%})."
            )
        else:
            conclusion_lines.append(
                f"• Injury localization: {injury_results.get('conclusion','—')}"
            )

    # Weapon
    if weapon_results and weapon_results.get("weapon_count", 0) > 0:
        items = weapon_results.get("items", [])
        if items:
            closest = min(items, key=lambda x: x["distance_px"])
            conclusion_lines.append(
                f"• Weapon-like object located {int(closest['distance_px'])}px "
                f"from nearest subject — classified as {closest['proximity_class']}."
            )
        conclusion_lines.append(f"• {weapon_results.get('conclusion','—')}")

    # Pose
    if pose_results:
        conclusion_lines.append(
            f"• Body posture classified as: {pose_results.get('posture','—')} "
            f"(confidence: {pose_results.get('posture_confidence',0):.0%})."
        )
        flags = pose_results.get("staging_flags", [])
        if flags:
            conclusion_lines.append(
                f"• STAGING INDICATOR: {flags[0]}"
            )

    # Scene consistency score
    scene_score = None
    if pose_results:
        scene_score = pose_results.get("scene_consistency_score", None)

    for line in conclusion_lines:
        story.append(Paragraph(line, S["conclusion_item"]))

    story.append(Spacer(1, 8 * mm))

    # Scene consistency score box
    if scene_score is not None:
        score_color = GREEN if scene_score >= 70 else (ORANGE if scene_score >= 45 else RED)
        score_box = Table(
            [[Paragraph("OVERALL SCENE CONSISTENCY SCORE", S["field_label"])],
             [Paragraph(f"{scene_score:.1f} / 100", S["score_label"])],
             [Paragraph(
                "Score reflects agreement between detected posture, stain distribution, "
                "subject presence, and object placement. Higher = more internally consistent scene.",
                S["narrative"]
             )]],
            colWidths=[W - 2 * margin]
        )
        score_box.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#0f0f0f")),
            ("BOX",         (0, 0), (-1, -1), 2, score_color),
            ("TOPPADDING",  (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0,0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",(0, 0), (-1, -1), 12),
        ]))
        story.append(score_box)

    story.append(Spacer(1, 8 * mm))
    story.append(_gold_rule())
    story.append(Paragraph("NOTES & DISCLAIMERS", S["section_header"]))
    disclaimers = [
        "This report was generated automatically by TraceLens. Results are investigative aids only.",
        "All analysis uses classical computer vision (OpenCV). Independent expert verification required.",
        "Blood stain detection is tuned for red/brownish-red regions. Lighting and compression affect accuracy.",
        "Weapon proximity uses shape heuristics — elongated high-contrast objects. Not weapon-type specific.",
        "Injury localization uses a body region grid relative to detected face position. Accuracy depends on face detection.",
        "This document is classified RESTRICTED. Unauthorised distribution is prohibited.",
    ]
    for d in disclaimers:
        story.append(Paragraph(d, S["narrative"]))

    story.append(Spacer(1, 6 * mm))
    story.append(_gold_rule())
    story.append(Paragraph("AUTHORISATION & CHAIN OF CUSTODY", S["section_header"]))
    sig_data = [
        ["ROLE", "NAME / ID", "SIGNATURE", "DATE"],
        ["Analyst",             "_______________________", "____________________", ts.strftime("%Y-%m-%d")],
        ["Supervising Officer", "___________________",     "____________________", "____________"],
        ["Evidence Custodian",  "___________________",     "____________________", "____________"],
    ]
    story.append(_dark_table(sig_data, [40*mm, 55*mm, 50*mm, 30*mm]))
    story.append(Spacer(1, 8 * mm))
    story.append(_gold_rule())
    story.append(Paragraph(
        f"END OF REPORT  ·  CASE {case_id}  ·  GENERATED {ts.strftime('%Y-%m-%d %H:%M:%S')}",
        S["cover_sub"]
    ))
    story.append(_gold_rule())

    def _dark_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#0a0a0a"))
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.setFont("Courier", 7)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawCentredString(A4[0] / 2, 12 * mm,
            f"TRACELENS FORENSIC REPORT  |  {case_id}  |  PAGE {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_dark_bg, onLaterPages=_dark_bg)
    return buf.getvalue()