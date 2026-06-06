import cv2
import numpy as np


# Body region grid: divide image into named zones
BODY_REGIONS = [
    {"name": "Head / Skull",    "row": (0.00, 0.18), "col": (0.25, 0.75)},
    {"name": "Neck / Throat",   "row": (0.18, 0.26), "col": (0.30, 0.70)},
    {"name": "Chest (Left)",    "row": (0.26, 0.50), "col": (0.00, 0.45)},
    {"name": "Chest (Right)",   "row": (0.26, 0.50), "col": (0.45, 1.00)},
    {"name": "Abdomen",         "row": (0.50, 0.65), "col": (0.20, 0.80)},
    {"name": "Left Arm",        "row": (0.26, 0.65), "col": (0.00, 0.20)},
    {"name": "Right Arm",       "row": (0.26, 0.65), "col": (0.80, 1.00)},
    {"name": "Pelvis / Groin",  "row": (0.65, 0.75), "col": (0.20, 0.80)},
    {"name": "Left Leg",        "row": (0.75, 1.00), "col": (0.00, 0.50)},
    {"name": "Right Leg",       "row": (0.75, 1.00), "col": (0.50, 1.00)},
]

SEVERITY_CRITICAL = ["Head / Skull", "Neck / Throat", "Chest (Left)", "Chest (Right)"]
SEVERITY_MODERATE = ["Abdomen", "Pelvis / Groin"]
SEVERITY_MINOR    = ["Left Arm", "Right Arm", "Left Leg", "Right Leg"]


def localize_injuries(image, mask, face_details=None):
    """
    Maps detected blood/stain regions onto named body zones.
    Uses the stain mask from color_segment.py.
    Returns: (annotated_image, results_dict)
    """
    if mask is None or cv2.countNonZero(mask) == 0:
        return image.copy(), None

    h, w   = image.shape[:2]
    result = image.copy()

    # ── Find stain contours ───────────────────────────────────────────────
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.contourArea(c) > 150]

    if not contours:
        return result, None

    # ── If face detected, anchor the body grid to it ──────────────────────
    # Without a face, use the full image as the body canvas
    grid_x, grid_y, grid_w, grid_h = 0, 0, w, h
    if face_details:
        # Use the first (largest) detected face to anchor
        largest = max(face_details, key=lambda f: f["bbox"][2] * f["bbox"][3])
        fx, fy, fw, fh = largest["bbox"]
        # Estimate full body: face is roughly top 15% of standing body
        body_top    = fy
        body_height = int(fh / 0.15)
        body_height = min(body_height, h - body_top)
        face_cx     = fx + fw // 2
        body_width  = int(fw * 3.5)
        body_left   = max(0, face_cx - body_width // 2)
        body_width  = min(body_width, w - body_left)
        grid_x, grid_y = body_left, body_top
        grid_w, grid_h = body_width, body_height

    # Draw body grid (faint)
    cv2.rectangle(result, (grid_x, grid_y),
                  (grid_x + grid_w, grid_y + grid_h),
                  (80, 80, 80), 1)

    # ── Map each stain centroid to a body region ──────────────────────────
    region_hits = {r["name"]: {"count": 0, "total_area": 0, "centroids": []} for r in BODY_REGIONS}

    for c in contours:
        M    = cv2.moments(c)
        area = cv2.contourArea(c)
        if M["m00"] == 0:
            continue
        cx_abs = int(M["m10"] / M["m00"])
        cy_abs = int(M["m01"] / M["m00"])

        # Normalize to grid
        nx = (cx_abs - grid_x) / grid_w if grid_w > 0 else 0.5
        ny = (cy_abs - grid_y) / grid_h if grid_h > 0 else 0.5

        nx = max(0.0, min(1.0, nx))
        ny = max(0.0, min(1.0, ny))

        matched_region = "Unknown Region"
        for reg in BODY_REGIONS:
            r0, r1 = reg["row"]
            c0, c1 = reg["col"]
            if r0 <= ny < r1 and c0 <= nx < c1:
                matched_region = reg["name"]
                break

        if matched_region in region_hits:
            region_hits[matched_region]["count"]      += 1
            region_hits[matched_region]["total_area"] += area
            region_hits[matched_region]["centroids"].append((cx_abs, cy_abs))

        # Label stain on image
        x_b, y_b, bw, bh = cv2.boundingRect(c)
        cv2.drawContours(result, [c], -1, (0, 80, 255), 2)
        cv2.putText(result, matched_region.split(" ")[0],
                    (x_b, max(y_b - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 200, 255), 1)

    # ── Build injury summary ──────────────────────────────────────────────
    active_regions = {k: v for k, v in region_hits.items() if v["count"] > 0}

    injury_summary = []
    critical_regions = []
    total_stain_area  = sum(v["total_area"] for v in active_regions.values())

    for region_name, data in sorted(active_regions.items(),
                                     key=lambda x: x[1]["total_area"], reverse=True):
        area_pct = (data["total_area"] / (h * w) * 100) if h * w > 0 else 0

        if region_name in SEVERITY_CRITICAL:
            severity = "CRITICAL"
            sev_conf = 0.82
        elif region_name in SEVERITY_MODERATE:
            severity = "MODERATE"
            sev_conf = 0.74
        else:
            severity = "MINOR"
            sev_conf = 0.68

        if severity == "CRITICAL":
            critical_regions.append(region_name)

        injury_summary.append({
            "region":      region_name,
            "severity":    severity,
            "confidence":  sev_conf,
            "stain_count": data["count"],
            "area_pct":    round(area_pct, 3),
        })

    # ── Overall conclusion ────────────────────────────────────────────────
    if critical_regions:
        primary_region = critical_regions[0]
        conclusion = f"Major injury evidence in {primary_region} region."
        if "Head" in primary_region or "Skull" in primary_region:
            conclusion += " Cranial trauma or gunshot wound cannot be excluded."
        elif "Chest" in primary_region:
            conclusion += " Thoracic injury — potentially life-threatening."
        elif "Neck" in primary_region:
            conclusion += " Cervical trauma — consistent with strangulation or cutting."
        overall_severity = "CRITICAL"
        overall_confidence = 0.80
    elif active_regions:
        primary_region = injury_summary[0]["region"] if injury_summary else "Unknown"
        conclusion = f"Injury evidence localized to {primary_region}. No critical regions flagged."
        overall_severity = "MODERATE"
        overall_confidence = 0.68
    else:
        conclusion = "No injury regions localized from available stain data."
        overall_severity = "NONE"
        overall_confidence = 0.0

    return result, {
        "overall_severity":    overall_severity,
        "overall_confidence":  overall_confidence,
        "conclusion":          conclusion,
        "critical_regions":    critical_regions,
        "injury_summary":      injury_summary,
        "active_region_count": len(active_regions),
        "annotated_image":     result,
    }