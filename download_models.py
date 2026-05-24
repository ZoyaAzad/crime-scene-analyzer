import urllib.request
import os
 
os.makedirs("assets", exist_ok=True)
 
files = {
    # DNN model — handles angled/profile faces (the important one)
    "assets/opencv_face_detector_uint8.pb": (
        "https://raw.githubusercontent.com/spmallick/learnopencv/"
        "master/FaceDetectionComparison/models/opencv_face_detector_uint8.pb"
    ),
    "assets/opencv_face_detector.pbtxt": (
        "https://raw.githubusercontent.com/spmallick/learnopencv/"
        "master/FaceDetectionComparison/models/opencv_face_detector.pbtxt"
    ),
 
    # Haar cascades — frontal + profile fallbacks
    "assets/haarcascade_frontalface_default.xml": (
        "https://raw.githubusercontent.com/opencv/opencv/"
        "master/data/haarcascades/haarcascade_frontalface_default.xml"
    ),
    "assets/haarcascade_profileface.xml": (
        "https://raw.githubusercontent.com/opencv/opencv/"
        "master/data/haarcascades/haarcascade_profileface.xml"
    ),
    "assets/haarcascade_frontalface_alt2.xml": (
        "https://raw.githubusercontent.com/opencv/opencv/"
        "master/data/haarcascades/haarcascade_frontalface_alt2.xml"
    ),
}
 
for dest, url in files.items():
    if os.path.exists(dest):
        print(f"  already exists, skipping:  {dest}")
        continue
    print(f"  downloading → {dest} ...")
    try:
        urllib.request.urlretrieve(url, dest)
        size_kb = os.path.getsize(dest) / 1024
        print(f"  ✓  {dest}  ({size_kb:.0f} KB)")
    except Exception as e:
        print(f"  ✗  FAILED: {dest}\n     {e}")
 
print("\nDone. Your assets/ folder now contains all required model files.")