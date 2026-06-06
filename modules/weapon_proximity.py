import cv2
import numpy as np


def analyze_weapon_proximity(image, face_details, mask=None):
    """
    Weapon-Hand Proximity Analysis.
    Detects potential weapon-like objects (elongated, dark, high-contrast contours)
    and measures their distance to the nearest detected body/face region.

    Returns: (annotated_image, results_dict)
    """
    if not face_details:
        return image.copy(), None

    result = image.copy()
    h, w   = image.shape[:2]

    # ── Step 1: Detect weapon-like contours ──────────────────────────────
    gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges   = cv2.Canny(blurred, 40, 120)
    dilated = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    weapon_candidates = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 400:
            continue

        x, y, bw, bh = cv2.boundingRect(c)
        aspect = max(bw, bh) / (min(bw, bh) + 1)
        extent = area / (bw * bh) if bw * bh > 0 else 0

        # Weapon heuristic: elongated (aspect > 3), moderate fill
        if aspect > 3.0 and 0.2 < extent < 0.85:
            # Check it doesn't overlap any face bounding box
            overlaps_face = False
            for fd in face_details:
                fx, fy, fw, fh = fd["bbox"]
                # Simple overlap check
                if (x < fx + fw and x + bw > fx and y < fy + fh and y + bh > fy):
                    overlaps_face = True
                    break
            if not overlaps_face:
                weapon_candidates.append({
                    "contour": c,
                    "bbox": (x, y, bw, bh),
                    "area": area,
                    "aspect": round(aspect, 2),
                    "centroid": (x + bw // 2, y + bh // 2),
                })

    # ── Step 2: Compute body centroids from face bboxes ──────────────────
    body_centroids = []
    for fd in face_details:
        fx, fy, fw, fh = fd["bbox"]
        # Estimate hand position: below the face bounding box
        hand_x = fx + fw // 2
        hand_y = fy + fh + int(fh * 1.2)   # ~1.2 face-heights below face
        hand_y = min(hand_y, h - 1)
        body_centroids.append({
            "face_id":   fd["id"],
            "face_bbox": fd["bbox"],
            "hand_est":  (hand_x, hand_y),
        })

    # ── Step 3: Match weapons to nearest hand estimate ────────────────────
    proximity_results = []
    for wc in weapon_candidates:
        wx, wy = wc["centroid"]
        min_dist = float("inf")
        nearest_face_id = None
        nearest_hand = None

        for bc in body_centroids:
            hx, hy = bc["hand_est"]
            dist = np.sqrt((wx - hx) ** 2 + (wy - hy) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest_face_id = bc["face_id"]
                nearest_hand = bc["hand_est"]

        # Classify proximity
        if min_dist < 80:
            proximity_class = "WITHIN REACH"
            prox_confidence = 0.78
            prox_note = "Object is within typical arm's reach of subject. Consistent with self-inflicted scenario."
        elif min_dist < 200:
            proximity_class = "NEARBY"
            prox_confidence = 0.60
            prox_note = "Object is in the general vicinity of the subject but not immediately adjacent."
        else:
            proximity_class = "DISTANT"
            prox_confidence = 0.72
            prox_note = f"Object is {int(min_dist)}px from nearest subject. Inconsistent with typical self-inflicted distance — may indicate staging or third-party placement."

        proximity_results.append({
            "weapon_id":       len(proximity_results) + 1,
            "weapon_centroid": wc["centroid"],
            "weapon_bbox":     wc["bbox"],
            "aspect_ratio":    wc["aspect"],
            "nearest_face_id": nearest_face_id,
            "distance_px":     round(min_dist, 1),
            "proximity_class": proximity_class,
            "confidence":      prox_confidence,
            "note":            prox_note,
            "hand_est":        nearest_hand,
        })

        # Annotate
        x, y, bw, bh = wc["bbox"]
        color = (0, 255, 0) if proximity_class == "WITHIN REACH" else (0, 80, 255)
        cv2.rectangle(result, (x, y), (x + bw, y + bh), color, 2)
        cv2.putText(result, f"OBJ#{len(proximity_results)} {proximity_class}",
                    (x, max(y - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        if nearest_hand:
            cv2.line(result, wc["centroid"], nearest_hand, (0, 255, 255), 1)
            cv2.putText(result, f"{int(min_dist)}px",
                        ((wc["centroid"][0] + nearest_hand[0]) // 2,
                         (wc["centroid"][1] + nearest_hand[1]) // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 255), 1)

    # Mark estimated hand positions
    for bc in body_centroids:
        hx, hy = bc["hand_est"]
        cv2.circle(result, (hx, hy), 8, (255, 200, 0), 2)
        cv2.putText(result, f"HAND EST F#{bc['face_id']}",
                    (hx + 10, hy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 200, 0), 1)

    if not proximity_results:
        return result, {
            "weapon_count": 0,
            "conclusion": "No weapon-like objects detected.",
            "confidence": 0.0,
            "items": [],
        }

    # ── Overall conclusion ────────────────────────────────────────────────
    distant_count = sum(1 for p in proximity_results if p["proximity_class"] == "DISTANT")
    if distant_count > 0:
        conclusion = f"{distant_count} object(s) located at atypical distance from subject — possible scene staging indicator."
        overall_confidence = 0.65
    else:
        conclusion = "All detected objects are within normal proximity of subject. No staging indicators from object placement."
        overall_confidence = 0.70

    return result, {
        "weapon_count":       len(weapon_candidates),
        "conclusion":         conclusion,
        "confidence":         overall_confidence,
        "items":              proximity_results,
        "annotated_image":    result,
    }