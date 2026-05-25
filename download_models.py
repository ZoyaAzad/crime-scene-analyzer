"""
Run once:  python download_models.py
Downloads all model files into assets/
"""
import urllib.request, os

os.makedirs("assets", exist_ok=True)

files = {
    # ── DNN SSD face detector (handles angled/partial faces) ──────────────
    "assets/opencv_face_detector_uint8.pb": (
        "https://raw.githubusercontent.com/spmallick/learnopencv/"
        "master/FaceDetectionComparison/models/opencv_face_detector_uint8.pb"
    ),
    "assets/opencv_face_detector.pbtxt": (
        "https://raw.githubusercontent.com/spmallick/learnopencv/"
        "master/FaceDetectionComparison/models/opencv_face_detector.pbtxt"
    ),

    # ── Haar cascades: frontal + profile ──────────────────────────────────
    "assets/haarcascade_frontalface_default.xml": (
        "https://raw.githubusercontent.com/opencv/opencv/"
        "master/data/haarcascades/haarcascade_frontalface_default.xml"
    ),
    "assets/haarcascade_frontalface_alt2.xml": (
        "https://raw.githubusercontent.com/opencv/opencv/"
        "master/data/haarcascades/haarcascade_frontalface_alt2.xml"
    ),
    "assets/haarcascade_profileface.xml": (
        "https://raw.githubusercontent.com/opencv/opencv/"
        "master/data/haarcascades/haarcascade_profileface.xml"
    ),

    # ── Haar body cascades ────────────────────────────────────────────────
    "assets/haarcascade_fullbody.xml": (
        "https://raw.githubusercontent.com/opencv/opencv/"
        "master/data/haarcascades/haarcascade_fullbody.xml"
    ),
    "assets/haarcascade_upperbody.xml": (
        "https://raw.githubusercontent.com/opencv/opencv/"
        "master/data/haarcascades/haarcascade_upperbody.xml"
    ),

    # ── YuNet — lightweight DNN, best for rotated / side faces ───────────
    # handles in-plane rotation natively up to ±90°
    "assets/face_detection_yunet_2023mar.onnx": (
        "https://github.com/opencv/opencv_zoo/raw/main/"
        "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
    ),
}

def _progress(count, block, total):
    if total > 0:
        pct = min(count * block * 100 // total, 100)
        print(f"\r  {pct:3d}%", end="", flush=True)

for dest, url in files.items():
    if os.path.exists(dest):
        print(f"  ✓  already exists: {dest}")
        continue
    print(f"  ↓  {dest} ...")
    try:
        urllib.request.urlretrieve(url, dest, reporthook=_progress)
        size_kb = os.path.getsize(dest) / 1024
        print(f"\r  ✓  {dest}  ({size_kb:.0f} KB)")
    except Exception as e:
        print(f"\r  ✗  FAILED: {dest}\n     {e}")

print("\nAll models ready.  Your assets/ folder is complete.")
