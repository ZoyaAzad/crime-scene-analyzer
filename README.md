# TraceLens 🔍
### Forensic Digital Crime Scene Analyzer

An advanced **Digital Image Processing (DIP)** application designed to automate forensic analysis of crime scene imagery. TraceLens leverages classical computer vision techniques to enhance low-quality captures and extract critical forensic markers such as biological stains, facial data, blood spatter patterns, injury regions, and weapon placement.

---

## 📸 Features

- 🔬 **Image Enhancement** — improve low-light and blurry evidence images
- 🧹 **Noise Reduction** — clean degraded images before analysis
- 🔴 **Blood Stain Detection** — HSV-based color segmentation to isolate stains
- 🩸 **Blood Spatter Analysis** — classify pattern type and estimate origin direction
- 🎯 **Injury Localization** — map stains to named body regions with severity ratings
- 🔫 **Weapon Proximity** — detect objects and measure distance from subject's hands
- 🧍 **Body Pose Inference** — infer posture and flag scene staging inconsistencies
- 🕵️ **Face Detection** — Haar Cascade classifiers for facial region identification
- 📄 **PDF Report Generation** — export a complete forensic report automatically

---

## ⚙️ Tech Stack

- **Language** — Python 3.8+
- **UI Framework** — Streamlit
- **Computer Vision** — OpenCV, NumPy
- **Report Generation** — ReportLab
- **Image Processing** — Pillow (PIL)

---

## 🚀 Installation & Setup

### Prerequisites
Make sure you have the following installed:
- Python 3.8 or higher
- pip

### Step 1 — Clone the repository
```bash
git clone 
cd TraceLens
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run the app
```bash
streamlit run app.py
```

### Step 4 — Open in browser
Streamlit will automatically open it in your browser

---

**TraceLens — Forensic Digital Crime Scene Analyzer** | DIP University Project
