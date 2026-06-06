import cv2
import numpy as np


def analyze_body_pose(image, face_details, mask=None):
    """
    Body Pose & Scene Consistency Analysis.
    Uses face bounding box position/orientation + stain distribution
    to infer body posture and flag scene inconsistencies.

    Returns: (annotated_image, results_dict)
    """
    if not face_details:
        return image.copy(), None

    h, w   = image.shape[:2]
    result = image.copy()

    largest_face = max(face_details, key=lambda f: f["bbox"][2] * f["bbox"][3])
    fx, fy, fw, fh = largest_face["bbox"]
    face_cx = fx + fw // 2
    face_cy = fy + fh // 2

    # ── Step 1: Classify posture from face position ───────────────────────
    face_y_ratio = face_cy / h  # normalized vertical position of face center

    if face_y_ratio < 0.35:
        posture = "UPRIGHT / STANDING"
        posture_confidence = 0.72
        posture_note = "Face detected in upper portion of frame — consistent with a standing or seated upright subject."
    elif face_y_ratio < 0.60:
        posture = "SEATED / SLUMPED"
        posture_confidence = 0.65
        posture_note = "Face position in mid-frame suggests a seated or slumped subject."
    else:
        posture = "SUPINE / PRONE (LYING DOWN)"
        posture_confidence = 0.78
        posture_note = "Face detected in lower portion of frame — strongly consistent with a supine (face-up) or prone (face-down) lying position."

    # ── Step 2: Face orientation (tilt) ──────────────────────────────────
    # Approximate from aspect ratio of the face bounding box
    face_aspect = fw / fh if fh > 0 else 1.0
    if face_aspect > 1.3:
        orientation = "TILTED / SIDEWAYS"
        orientation_note = "Bounding box wider than tall — face may be rotated, consistent with lying on side."
    elif face_aspect < 0.75:
        orientation = "VERTICAL / UPRIGHT FACE"
        orientation_note = "Bounding box taller than wide — face is in standard upright orientation."
    else:
        orientation = "NEUTRAL"
        orientation_note = "Face bounding box aspect ratio within normal range."

    # ── Step 3: Stain-posture consistency check ───────────────────────────
    stain_consistency = "UNDETERMINED"
    stain_consistency_confidence = 0.0
    stain_note = "No stain mask provided for consistency analysis."

    if mask is not None and cv2.countNonZero(mask) > 0:
        stain_pixels = cv2.findNonZero(mask)
        if stain_pixels is not None and len(stain_pixels) > 50:
            stain_ys = stain_pixels[:, 0, 1]
            stain_cx_vals = stain_pixels[:, 0, 0]
            stain_y_mean = np.mean(stain_ys) / h
            stain_cx_mean = np.mean(stain_cx_vals)

            # Blood should pool downward relative to wound site
            blood_below_face = stain_y_mean > face_y_ratio

            if posture in ("SUPINE / PRONE (LYING DOWN)",) and blood_below_face:
                stain_consistency = "CONSISTENT"
                stain_consistency_confidence = 0.76
                stain_note = "Blood distribution is below the detected face/wound region — consistent with gravity-driven pooling in a lying position."
            elif posture == "UPRIGHT / STANDING" and not blood_below_face:
                stain_consistency = "INCONSISTENT"
                stain_consistency_confidence = 0.68
                stain_note = "Blood detected above face level in a standing posture — may indicate impact from above or scene manipulation."
            elif posture == "UPRIGHT / STANDING" and blood_below_face:
                stain_consistency = "CONSISTENT"
                stain_consistency_confidence = 0.71
                stain_note = "Blood distribution is below face level — consistent with downward flow from a standing position."
            else:
                stain_consistency = "PARTIALLY CONSISTENT"
                stain_consistency_confidence = 0.55
                stain_note = "Stain distribution is partially consistent with detected posture but inconclusive."

    # ── Step 4: Scene staging indicators ─────────────────────────────────
    staging_flags = []
    staging_score = 0.0

    # Flag 1: Face in unexpected position relative to scene
    if posture == "SUPINE / PRONE (LYING DOWN)" and stain_consistency == "INCONSISTENT":
        staging_flags.append("Blood distribution does not match lying posture — possible repositioning of body.")
        staging_score += 0.25

    # Flag 2: Multiple faces — check relative positions
    if len(face_details) > 1:
        staging_flags.append(f"{len(face_details)} subjects detected — multi-person scene requires individual analysis.")
        staging_score += 0.10

    # Flag 3: Face near edge of frame (partial body visible)
    if fx < w * 0.05 or fx + fw > w * 0.95:
        staging_flags.append("Subject partially out of frame — full body posture cannot be determined.")
        staging_score += 0.10

    # Overall staging probability (capped at 0.85)
    staging_probability = min(staging_score, 0.85)

    # ── Scene consistency score ───────────────────────────────────────────
    # Weighted combination of individual confidence scores
    weights = [
        (posture_confidence, 0.35),
        (stain_consistency_confidence, 0.40),
        ((1.0 - staging_probability), 0.25),
    ]
    scene_consistency = sum(c * w_ for c, w_ in weights)

    # ── Annotate image ────────────────────────────────────────────────────
    # Draw posture label above face
    label_y = max(fy - 30, 20)
    cv2.rectangle(result, (fx, label_y - 20), (fx + fw, label_y), (80, 0, 200), -1)
    cv2.putText(result, posture.split("/")[0].strip(),
                (fx + 4, label_y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)

    # Draw estimated spine line
    spine_top    = (face_cx, fy + fh)
    spine_bottom = (face_cx, min(h - 1, fy + fh + int(fh * 4.5)))
    cv2.line(result, spine_top, spine_bottom, (180, 0, 255), 1)
    cv2.putText(result, "SPINE EST",
                (spine_bottom[0] + 5, spine_bottom[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 0, 255), 1)

    return result, {
        "posture":                      posture,
        "posture_confidence":           round(posture_confidence, 2),
        "posture_note":                 posture_note,
        "orientation":                  orientation,
        "orientation_note":             orientation_note,
        "stain_posture_consistency":    stain_consistency,
        "stain_consistency_confidence": round(stain_consistency_confidence, 2),
        "stain_note":                   stain_note,
        "staging_flags":                staging_flags,
        "staging_probability":          round(staging_probability, 2),
        "scene_consistency_score":      round(scene_consistency * 100, 1),
        "annotated_image":              result,
    }