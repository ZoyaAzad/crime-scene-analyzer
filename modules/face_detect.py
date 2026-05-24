import cv2
import numpy as np
import os


def detect_faces(image):
    """
    Human detection with two layers:
    1. Face detection (DNN + Haar) — for visible faces
    2. Full-body / upper-body detection (HOG + Haar) — for lying/turned persons
    Returns: (annotated_image, face_count, face_details_list)
    """
    result = image.copy()
    face_details = []
    detected_boxes = []

    h_img, w_img = image.shape[:2]

    # ── Layer 1: DNN face detector ────────────────────────────────────────
    pb_path    = "assets/opencv_face_detector_uint8.pb"
    pbtxt_path = "assets/opencv_face_detector.pbtxt"

    if os.path.exists(pb_path) and os.path.exists(pbtxt_path):
        try:
            net  = cv2.dnn.readNetFromTensorflow(pb_path, pbtxt_path)
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)), 1.0,
                (300, 300), [104, 117, 123], swapRB=False
            )
            net.setInput(blob)
            detections = net.forward()

            for i in range(detections.shape[2]):
                confidence = float(detections[0, 0, i, 2])
                if confidence > 0.75:
                    x1 = max(0, int(detections[0, 0, i, 3] * w_img))
                    y1 = max(0, int(detections[0, 0, i, 4] * h_img))
                    x2 = min(w_img, int(detections[0, 0, i, 5] * w_img))
                    y2 = min(h_img, int(detections[0, 0, i, 6] * h_img))
                    if not _overlaps(detected_boxes, x1, y1, x2, y2):
                        detected_boxes.append((x1, y1, x2, y2))
                        face_details.append({
                            "id":         len(face_details) + 1,
                            "type":       "FACE",
                            "method":     "DNN",
                            "confidence": confidence,
                            "bbox":       (x1, y1, x2 - x1, y2 - y1),
                            "position":   _position_label(x1, y1, w_img, h_img),
                        })
        except Exception as e:
            print(f"[DNN] {e}")

    # ── Layer 2: Haar frontal face (strict) ───────────────────────────────
    haar_face_cascades = [
        ("assets/haarcascade_frontalface_default.xml", "Frontal"),
        ("assets/haarcascade_frontalface_alt2.xml",    "Frontal-Alt"),
        ("assets/haarcascade_profileface.xml",         "Profile"),
    ]
    gray = cv2.equalizeHist(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))

    for path, label in haar_face_cascades:
        if not os.path.exists(path):
            continue
        cc = cv2.CascadeClassifier(path)
        if cc.empty():
            continue
        for scale in [1.1, 1.2]:
            faces = cc.detectMultiScale(
                gray, scaleFactor=scale,
                minNeighbors=8, minSize=(60, 60),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            for (x, y, fw, fh) in (faces if len(faces) else []):
                x2, y2 = x + fw, y + fh
                if not _overlaps(detected_boxes, x, y, x2, y2):
                    detected_boxes.append((x, y, x2, y2))
                    face_details.append({
                        "id":         len(face_details) + 1,
                        "type":       "FACE",
                        "method":     f"Haar-{label}",
                        "confidence": None,
                        "bbox":       (x, y, fw, fh),
                        "position":   _position_label(x, y, w_img, h_img),
                    })

    # ── Layer 3: HOG person detector (handles lying/turned bodies) ────────
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # Try multiple scales so lying-down bodies are caught
    for win_stride, padding, scale in [
        ((8, 8),  (4, 4), 1.05),
        ((8, 8),  (8, 8), 1.10),
        ((16, 16),(8, 8), 1.05),
    ]:
        rects, weights = hog.detectMultiScale(
            image, winStride=win_stride, padding=padding,
            scale=scale
        )
        for i, (x, y, bw, bh) in enumerate(rects if len(rects) else []):
            conf = float(weights[i]) if len(weights) > i else 0.0
            if conf < 0.3:           # ignore very weak body hits
                continue
            x2, y2 = x + bw, y + bh
            if not _overlaps(detected_boxes, x, y, x2, y2, iou_thresh=0.4):
                detected_boxes.append((x, y, x2, y2))
                face_details.append({
                    "id":         len(face_details) + 1,
                    "type":       "PERSON",
                    "method":     "HOG",
                    "confidence": conf,
                    "bbox":       (x, y, bw, bh),
                    "position":   _position_label(x, y, w_img, h_img),
                })

    # ── Haar full-body fallback ───────────────────────────────────────────
    fullbody_path = "assets/haarcascade_fullbody.xml"
    upperbody_path = "assets/haarcascade_upperbody.xml"

    for path, label in [(fullbody_path, "Full-Body"), (upperbody_path, "Upper-Body")]:
        if not os.path.exists(path):
            continue
        cc = cv2.CascadeClassifier(path)
        if cc.empty():
            continue
        detections_haar = cc.detectMultiScale(
            gray, scaleFactor=1.1,
            minNeighbors=3, minSize=(40, 80)
        )
        for (x, y, bw, bh) in (detections_haar if len(detections_haar) else []):
            x2, y2 = x + bw, y + bh
            if not _overlaps(detected_boxes, x, y, x2, y2, iou_thresh=0.4):
                detected_boxes.append((x, y, x2, y2))
                face_details.append({
                    "id":         len(face_details) + 1,
                    "type":       "PERSON",
                    "method":     f"Haar-{label}",
                    "confidence": None,
                    "bbox":       (x, y, bw, bh),
                    "position":   _position_label(x, y, w_img, h_img),
                })

    # ── Draw all detections ───────────────────────────────────────────────
    for det in face_details:
        x, y, bw, bh = det["bbox"]
        is_face   = det["type"] == "FACE"
        box_color = (0, 255, 255) if is_face else (0, 165, 255)  # yellow / orange
        conf_text = f"{det['confidence']:.0%}" if det["confidence"] else det["method"]
        label_txt = f"{det['type']} #{det['id']}  {conf_text}"

        cv2.rectangle(result, (x, y), (x + bw, y + bh), box_color, 2)
        cv2.rectangle(result, (x, y - 22), (x + bw, y), box_color, -1)
        cv2.putText(result, label_txt, (x + 4, y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    return result, len(face_details), face_details


def _overlaps(boxes, x1, y1, x2, y2, iou_thresh=0.3):
    for (bx1, by1, bx2, by2) in boxes:
        ix1, iy1 = max(x1, bx1), max(y1, by1)
        ix2, iy2 = min(x2, bx2), min(y2, by2)
        iw, ih   = max(0, ix2 - ix1), max(0, iy2 - iy1)
        inter    = iw * ih
        union    = (x2-x1)*(y2-y1) + (bx2-bx1)*(by2-by1) - inter
        if union > 0 and inter / union > iou_thresh:
            return True
    return False


def _position_label(x, y, img_w, img_h):
    cx = x + img_w // 6
    cy = y + img_h // 6
    v  = "upper" if cy < img_h // 2 else "lower"
    h  = "left"  if cx < img_w // 3 else ("center" if cx < 2 * img_w // 3 else "right")
    return f"{v}-{h}"