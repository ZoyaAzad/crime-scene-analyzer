import cv2
import numpy as np
import os


def detect_faces(image):
    """
    Crime-scene human detection.

    Layers (in priority order):
      1. YuNet ONNX — if model file present (best for all angles, handles ±90°)
      2. DNN SSD    — frontal + partial faces; also run at 270° rotation
      3. Profile Haar — left + right profiles
      4. HOG @0°/90°/180°/270° — person/body detection at all orientations
      5. Haar body — upright full/upper-body fallback

    Returns: (annotated_image, count, face_details_list)
    """
    orig_h, orig_w = image.shape[:2]
    detected_boxes = []
    face_details   = []

    yunet_ran = _run_yunet(image, orig_h, orig_w, detected_boxes, face_details)

    if not yunet_ran:
        _run_dnn(image, orig_h, orig_w, detected_boxes, face_details)
        _run_profile_haar(image, orig_h, orig_w, detected_boxes, face_details)

    # Body/person detection always runs (YuNet is face-only)
    _run_hog_all_angles(image, orig_h, orig_w, detected_boxes, face_details)
    _run_body_haar(image, orig_h, orig_w, detected_boxes, face_details)

    # Draw
    result = image.copy()
    for det in face_details:
        x, y, bw, bh = det["bbox"]
        is_face = det["type"] == "FACE"
        color   = (0, 255, 255) if is_face else (0, 165, 255)
        conf_t  = f"{det['confidence']:.0%}" if det["confidence"] is not None else det["method"]
        label   = f"{det['type']} #{det['id']}  {conf_t}"
        cv2.rectangle(result, (x, y), (x + bw, y + bh), color, 2)
        cv2.rectangle(result, (x, y - 22), (x + bw, y), color, -1)
        cv2.putText(result, label, (x + 4, y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    return result, len(face_details), face_details


# ── Layer 1: YuNet ────────────────────────────────────────────────────────────

def _run_yunet(image, orig_h, orig_w, detected_boxes, face_details):
    model_path = "assets/face_detection_yunet_2023mar.onnx"
    if not os.path.exists(model_path):
        return False
    try:
        detector = cv2.FaceDetectorYN.create(
            model_path, "", (orig_w, orig_h),
            score_threshold=0.45,   # sensitive but not spammy
            nms_threshold=0.3,
            top_k=50
        )
        detector.setInputSize((orig_w, orig_h))
        _, faces = detector.detect(image)
        if faces is not None:
            for face in faces:
                x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])
                conf = float(face[14])
                x1, y1 = max(0, x), max(0, y)
                x2, y2 = min(orig_w, x + w), min(orig_h, y + h)
                if not _overlaps(detected_boxes, x1, y1, x2, y2):
                    _add(detected_boxes, face_details, x1, y1, x2, y2,
                         "FACE", "YuNet", conf, orig_w, orig_h)
        return True
    except Exception as e:
        print(f"[YuNet] {e}")
        return False


# ── Layer 2: DNN SSD ──────────────────────────────────────────────────────────

def _run_dnn(image, orig_h, orig_w, detected_boxes, face_details):
    pb    = "assets/opencv_face_detector_uint8.pb"
    pbtxt = "assets/opencv_face_detector.pbtxt"
    if not (os.path.exists(pb) and os.path.exists(pbtxt)):
        return
    try:
        net = cv2.dnn.readNetFromTensorflow(pb, pbtxt)

        # Run at 0° and 270° (catches the right-side face in Image 1)
        for angle, img_r in [(0, image),
                             (270, cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE))]:
            rh, rw = img_r.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(img_r, (300, 300)), 1.0,
                (300, 300), [104, 117, 123], swapRB=False)
            net.setInput(blob)
            dets = net.forward()
            for i in range(dets.shape[2]):
                conf = float(dets[0, 0, i, 2])
                if conf < 0.40:   # lower threshold to catch side-lying faces
                    continue
                x1 = max(0, int(dets[0, 0, i, 3] * rw))
                y1 = max(0, int(dets[0, 0, i, 4] * rh))
                x2 = min(rw, int(dets[0, 0, i, 5] * rw))
                y2 = min(rh, int(dets[0, 0, i, 6] * rh))
                ox1, oy1, ox2, oy2 = _rotate_box_back(x1, y1, x2, y2, angle, orig_h, orig_w)
                ox1, oy1 = max(0, ox1), max(0, oy1)
                ox2, oy2 = min(orig_w, ox2), min(orig_h, oy2)
                if ox2 <= ox1 or oy2 <= oy1:
                    continue
                if not _overlaps(detected_boxes, ox1, oy1, ox2, oy2):
                    label = "DNN" if angle == 0 else f"DNN@{angle}°"
                    _add(detected_boxes, face_details, ox1, oy1, ox2, oy2,
                         "FACE", label, conf, orig_w, orig_h)
    except Exception as e:
        print(f"[DNN] {e}")


# ── Layer 3: Profile Haar ─────────────────────────────────────────────────────

def _run_profile_haar(image, orig_h, orig_w, detected_boxes, face_details):
    path = "assets/haarcascade_profileface.xml"
    if not os.path.exists(path):
        return
    cc = cv2.CascadeClassifier(path)
    if cc.empty():
        return
    gray = cv2.equalizeHist(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    for flipped, g in [(False, gray), (True, cv2.flip(gray, 1))]:
        faces = cc.detectMultiScale(g, scaleFactor=1.1, minNeighbors=6, minSize=(60, 60))
        for (x, y, fw, fh) in (faces if len(faces) else []):
            x1 = orig_w - x - fw if flipped else x
            x2 = x1 + fw; y1 = y; y2 = y + fh
            x1, x2 = max(0, x1), min(orig_w, x2)
            y1, y2 = max(0, y1), min(orig_h, y2)
            if not _overlaps(detected_boxes, x1, y1, x2, y2):
                _add(detected_boxes, face_details, x1, y1, x2, y2,
                     "FACE", "Haar-Profile-R" if flipped else "Haar-Profile-L",
                     None, orig_w, orig_h)


# ── Layer 4: HOG all 4 angles ─────────────────────────────────────────────────

def _run_hog_all_angles(image, orig_h, orig_w, detected_boxes, face_details):
    """
    Run HOG at all 4 rotations.
    0°/180° catch upright/upside-down standing people.
    90°/270° catch people lying on their side.
    Threshold 0.5 keeps it tight.
    """
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    rotation_map = {
        0:   image,
        90:  cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE),
        180: cv2.rotate(image, cv2.ROTATE_180),
        270: cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE),
    }

    for angle, rot_img in rotation_map.items():
        rects, weights = hog.detectMultiScale(
            rot_img, winStride=(8, 8), padding=(8, 8), scale=1.05)
        for i, (x, y, bw, bh) in enumerate(rects if len(rects) else []):
            conf = float(weights[i]) if i < len(weights) else 0.0
            if conf < 0.5:
                continue
            x1r, y1r, x2r, y2r = _rotate_box_back(
                x, y, x + bw, y + bh, angle, orig_h, orig_w)
            x1r = max(0, x1r); y1r = max(0, y1r)
            x2r = min(orig_w, x2r); y2r = min(orig_h, y2r)
            if x2r <= x1r or y2r <= y1r:
                continue
            if not _overlaps(detected_boxes, x1r, y1r, x2r, y2r, iou_thresh=0.4):
                label = "HOG" if angle == 0 else f"HOG@{angle}°"
                _add(detected_boxes, face_details, x1r, y1r, x2r, y2r,
                     "PERSON", label, conf, orig_w, orig_h)


# ── Layer 5: Haar body ────────────────────────────────────────────────────────

def _run_body_haar(image, orig_h, orig_w, detected_boxes, face_details):
    for path, label in [
        ("assets/haarcascade_fullbody.xml",  "Full-Body"),
        ("assets/haarcascade_upperbody.xml", "Upper-Body"),
    ]:
        if not os.path.exists(path):
            continue
        cc = cv2.CascadeClassifier(path)
        if cc.empty():
            continue
        gray = cv2.equalizeHist(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        dets = cc.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 100))
        for (x, y, bw, bh) in (dets if len(dets) else []):
            x2, y2 = x + bw, y + bh
            if not _overlaps(detected_boxes, x, y, x2, y2, iou_thresh=0.4):
                _add(detected_boxes, face_details, x, y, x2, y2,
                     "PERSON", f"Haar-{label}", None, orig_w, orig_h)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _rotate_box_back(x1, y1, x2, y2, angle, orig_h, orig_w):
    if angle == 0:
        return x1, y1, x2, y2
    if angle == 90:    # was rotated CCW
        return y1, orig_w - x2, y2, orig_w - x1
    if angle == 180:
        return orig_w - x2, orig_h - y2, orig_w - x1, orig_h - y1
    if angle == 270:   # was rotated CW
        return orig_h - y2, x1, orig_h - y1, x2
    return x1, y1, x2, y2


def _add(detected_boxes, face_details, x1, y1, x2, y2,
         det_type, method, conf, img_w, img_h):
    detected_boxes.append((x1, y1, x2, y2))
    face_details.append({
        "id":         len(face_details) + 1,
        "type":       det_type,
        "method":     method,
        "confidence": conf,
        "bbox":       (x1, y1, x2 - x1, y2 - y1),
        "position":   _position_label(x1, y1, img_w, img_h),
    })


def _overlaps(boxes, x1, y1, x2, y2, iou_thresh=0.3):
    for (bx1, by1, bx2, by2) in boxes:
        ix1 = max(x1, bx1); iy1 = max(y1, by1)
        ix2 = min(x2, bx2); iy2 = min(y2, by2)
        inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
        union = (x2-x1)*(y2-y1) + (bx2-bx1)*(by2-by1) - inter
        if union > 0 and inter / union > iou_thresh:
            return True
    return False


def _position_label(x, y, img_w, img_h):
    cx = x + img_w // 6
    cy = y + img_h // 6
    v  = "upper" if cy < img_h // 2 else "lower"
    h  = "left"  if cx < img_w // 3 else ("center" if cx < 2 * img_w // 3 else "right")
    return f"{v}-{h}"
