import cv2
import numpy as np


def analyze_blood_spatter(image, mask):
    """
    Forensic blood spatter pattern analysis.
    Takes the original BGR image and the clean binary mask from color_segment.py.
    Returns: (annotated_image, results_dict)
    """
    if mask is None or cv2.countNonZero(mask) == 0:
        return image.copy(), None

    h, w = image.shape[:2]
    result = image.copy()

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.contourArea(c) > 80]

    if not contours:
        return result, None

    stain_data = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 80:
            continue
        perimeter = cv2.arcLength(c, True)
        x, y, bw, bh = cv2.boundingRect(c)

        # Aspect ratio
        aspect = bw / bh if bh > 0 else 1.0

        # Circularity
        circularity = (4 * np.pi * area / (perimeter ** 2)) if perimeter > 0 else 0

        # Edge serration: compare actual perimeter to convex hull perimeter
        hull = cv2.convexHull(c)
        hull_perim = cv2.arcLength(hull, True)
        serration = (perimeter / hull_perim) if hull_perim > 0 else 1.0

        # Satellite detection: small stains within 2x bounding box of this stain
        expanded = (x - bw, y - bh, x + 2*bw, y + 2*bh)

        # Ellipse fitting for directionality (needs >=5 points)
        angle = None
        if len(c) >= 5:
            try:
                ellipse = cv2.fitEllipse(c)
                angle = ellipse[2]  # rotation angle in degrees
            except:
                angle = None

        stain_data.append({
            "area": area,
            "aspect": aspect,
            "circularity": circularity,
            "serration": serration,
            "angle": angle,
            "bbox": (x, y, bw, bh),
            "contour": c,
        })

    if not stain_data:
        return result, None

    # ── Pattern Classification ────────────────────────────────────────────
    avg_circularity = np.mean([s["circularity"] for s in stain_data])
    avg_aspect      = np.mean([s["aspect"]      for s in stain_data])
    avg_serration   = np.mean([s["serration"]   for s in stain_data])
    count           = len(stain_data)
    areas           = [s["area"] for s in stain_data]
    avg_area        = np.mean(areas)

    # Classify pattern type
    if avg_circularity > 0.80 and avg_serration < 1.15:
        pattern_type = "Passive Drip / Low Velocity"
        pattern_confidence = 0.82
        pattern_detail = "Circular stains with smooth edges indicate blood dripping under gravity from a stationary or slow-moving source."
        velocity = "Low"
    elif avg_serration > 1.45 or (count > 15 and avg_area < 800):
        pattern_type = "High Velocity Impact Spatter"
        pattern_confidence = 0.74
        pattern_detail = "Fine mist-like stains with jagged, serrated edges are consistent with high-energy events such as gunshot or high-speed impact."
        velocity = "High"
    elif avg_circularity < 0.55 and avg_aspect > 1.6:
        pattern_type = "Cast-Off / Directional Spatter"
        pattern_confidence = 0.71
        pattern_detail = "Elongated, directional stains suggest blood was flung from a moving object or swinging motion."
        velocity = "Medium-High"
    elif count > 8 and avg_serration > 1.2:
        pattern_type = "Medium Velocity Impact Spatter"
        pattern_confidence = 0.76
        pattern_detail = "Multiple stains with moderate edge irregularity are consistent with blunt force or medium-energy impact events."
        velocity = "Medium"
    else:
        pattern_type = "Transfer / Contact Pattern"
        pattern_confidence = 0.62
        pattern_detail = "Pattern characteristics suggest direct surface contact rather than projected spatter."
        velocity = "Undetermined"

    # ── Origin Direction Estimation ───────────────────────────────────────
    angles = [s["angle"] for s in stain_data if s["angle"] is not None]
    origin_direction = "Undetermined"
    origin_confidence = 0.0
    if len(angles) >= 3:
        mean_angle = np.mean(angles)
        std_angle  = np.std(angles)
        if std_angle < 30:
            # Consistent directionality
            if   mean_angle < 30 or mean_angle > 150:
                origin_direction = "Horizontal (left-right)"
            elif 60 < mean_angle < 120:
                origin_direction = "Vertical (top-down)"
            else:
                origin_direction = f"Diagonal (~{mean_angle:.0f}°)"
            origin_confidence = max(0.4, min(0.85, 1.0 - std_angle / 90))
        else:
            origin_direction = "Multiple / Scattered origins"
            origin_confidence = 0.35

    # ── Annotate image ────────────────────────────────────────────────────
    for s in stain_data:
        x, y, bw, bh = s["bbox"]
        if s["circularity"] > 0.75:
            color = (0, 255, 200)   # teal = circular/drip
        elif s["aspect"] > 1.6:
            color = (0, 100, 255)   # orange = directional
        else:
            color = (80, 80, 255)   # red = impact

        cv2.drawContours(result, [s["contour"]], -1, color, 2)

    # Draw origin arrow if directional
    if "Horizontal" in origin_direction or "Vertical" in origin_direction or "Diagonal" in origin_direction:
        cx, cy = w // 2, h // 2
        angle_rad = np.radians(float(origin_direction.split("~")[-1].replace("°)", "").strip()) if "~" in origin_direction else 0)
        ex = int(cx + 80 * np.cos(angle_rad))
        ey = int(cy + 80 * np.sin(angle_rad))
        cv2.arrowedLine(result, (cx, cy), (ex, ey), (0, 255, 255), 2, tipLength=0.3)
        cv2.putText(result, "ORIGIN DIR", (cx - 40, cy - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    results = {
        "pattern_type":        pattern_type,
        "pattern_confidence":  pattern_confidence,
        "pattern_detail":      pattern_detail,
        "velocity":            velocity,
        "stain_count":         count,
        "avg_area_px":         round(avg_area, 1),
        "avg_circularity":     round(avg_circularity, 3),
        "avg_aspect_ratio":    round(avg_aspect, 2),
        "edge_serration_index":round(avg_serration, 3),
        "origin_direction":    origin_direction,
        "origin_confidence":   round(origin_confidence, 2),
        "annotated_image":     result,
    }
    return result, results