import streamlit as st
from theme import inject_theme, tape_divider


def render():
    inject_theme("Guide")

    st.markdown("""
    <style>
    .guide-hero {
        padding: 60px 40px 20px;
        border-bottom: 1px solid #1a1a1a;
    }
    .step-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1px;
        background: #1a1a1a;
        margin: 32px 0;
    }
    .step-card {
        background: var(--bg2);
        padding: 32px 28px;
        position: relative;
        transition: background 0.3s;
    }
    .step-card:hover { background: rgba(139,0,0,0.05); }
    .step-number {
        font-family: var(--font-horror);
        font-size: 64px;
        color: rgba(139,0,0,0.15);
        position: absolute;
        top: 12px; right: 20px;
        line-height: 1;
    }
    .step-tag {
        font-family: var(--font-mono);
        font-size: 9px;
        letter-spacing: 3px;
        color: var(--blood-bright);
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .step-title {
        font-family: var(--font-head);
        font-size: 16px;
        letter-spacing: 2px;
        color: var(--gold);
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .step-desc {
        font-family: var(--font-mono);
        font-size: 12px;
        color: var(--text);
        line-height: 1.8;
    }
    .step-desc li {
        margin-bottom: 6px;
        padding-left: 8px;
        border-left: 2px solid #2a2a2a;
        list-style: none;
    }
    .tip-box {
        background: rgba(255,215,0,0.03);
        border: 1px solid rgba(255,215,0,0.15);
        border-left: 3px solid var(--gold);
        padding: 16px 20px;
        margin: 12px 0;
        font-family: var(--font-mono);
        font-size: 12px;
        color: var(--text-dim);
        line-height: 1.7;
    }
    .tip-box strong { color: var(--gold); }
    .warn-box {
        background: rgba(139,0,0,0.05);
        border: 1px solid rgba(139,0,0,0.3);
        border-left: 3px solid var(--blood-bright);
        padding: 16px 20px;
        margin: 12px 0;
        font-family: var(--font-mono);
        font-size: 12px;
        color: var(--text-dim);
        line-height: 1.7;
    }
    </style>

    <div class="guide-hero">
        <p style="font-family:var(--font-mono);font-size:10px;letter-spacing:4px;color:var(--blood-bright);margin-bottom:12px;">
            [ FIELD MANUAL // INVESTIGATOR GUIDE ]
        </p>
        <h1 style="font-family:var(--font-horror);font-size:52px;color:#fff;margin-bottom:12px;text-shadow:0 0 20px rgba(204,0,0,0.3);">
            How To Use TraceLens
        </h1>
        <p style="font-family:var(--font-type);font-size:15px;color:var(--text-dim);max-width:680px;line-height:1.8;letter-spacing:1px;">
            Follow this operational guide to extract maximum intelligence from your crime scene evidence.
            Each module builds on the previous — run them in order for best results.
        </p>
    </div>

    """, unsafe_allow_html=True)

    tape_divider()

    st.markdown("""
        <div style="padding: 0 40px;">
        <div class="step-grid">
            <div class="step-card">
                <div class="step-number">01</div>
                <div class="step-tag">Step One</div>
                <div class="step-title">📁 Upload Evidence</div>
                <div class="step-desc"><ul>
                    <li>Navigate to the <strong style="color:var(--gold)">Analyze</strong> page from the navbar</li>
                    <li>Click the upload area and select a JPG or PNG image</li>
                    <li>Supported formats: JPG, JPEG, PNG — up to 200MB</li>
                    <li>Higher resolution images yield more accurate results</li>
                </ul></div>
            </div>
            <div class="step-card">
                <div class="step-number">02</div>
                <div class="step-tag">Step Two</div>
                <div class="step-title">🗂 Fill Case Details</div>
                <div class="step-desc"><ul>
                    <li>After upload, a case information form will appear</li>
                    <li>Enter victim/suspect name and case location</li>
                    <li>Write a brief description of the crime scene context</li>
                    <li>This information is embedded in the final PDF report</li>
                </ul></div>
            </div>
            <div class="step-card">
                <div class="step-number">03</div>
                <div class="step-tag">Step Three</div>
                <div class="step-title">⚙ Enhancement First</div>
                <div class="step-desc"><ul>
                    <li>Use <strong style="color:var(--gold)">Histogram Equalisation</strong> on dark images</li>
                    <li>Increase <strong style="color:var(--gold)">Contrast</strong> if the scene appears washed out</li>
                    <li>Apply <strong style="color:var(--gold)">Sharpen</strong> if details appear blurry</li>
                    <li>Always enhance before running detection modules</li>
                </ul></div>
            </div>
        </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="padding: 0 40px;">
        <div class="step-grid">
            <div class="step-card">
                <div class="step-number">04</div>
                <div class="step-tag">Step Four</div>
                <div class="step-title">🌫 Noise Reduction</div>
                <div class="step-desc"><ul>
                    <li>Use <strong style="color:var(--gold)">Gaussian Blur</strong> for general graininess</li>
                    <li>Use <strong style="color:var(--gold)">Median Filter</strong> for scanned photos with speckle noise</li>
                    <li>Keep kernel size small (3–7) — large kernels destroy edge detail</li>
                    <li>Edge detection always runs on the original, not the blurred version</li>
                </ul></div>
            </div>
            <div class="step-card">
                <div class="step-number">05</div>
                <div class="step-tag">Step Five</div>
                <div class="step-title">🩸 Blood Stain Detection</div>
                <div class="step-desc"><ul>
                    <li>Check <strong style="color:var(--gold)">Enable Color Detection</strong></li>
                    <li>Click <strong style="color:var(--blood-bright)">🩸 FRESH</strong> for bright red, <strong style="color:var(--blood-bright)">🩸 DRIED</strong> for dark brownish stains</li>
                    <li>Fine-tune HSV sliders if the preset misses stains</li>
                    <li>Coverage % and severity rating are auto-calculated</li>
                </ul></div>
            </div>
            <div class="step-card">
                <div class="step-number">06</div>
                <div class="step-tag">Step Six</div>
                <div class="step-title">👤 Face & Object Detection</div>
                <div class="step-desc"><ul>
                    <li>Check <strong style="color:var(--gold)">Detect Faces</strong> for human presence detection</li>
                    <li>Works on frontal faces, side profiles, and angled views</li>
                    <li>Use <strong style="color:var(--gold)">Contours</strong> to detect objects and impact points</li>
                    <li>Circular contours (circularity > 0.65) are flagged as ⚠ IMPACT</li>
                </ul></div>
            </div>
        </div>
        </div>
    """, unsafe_allow_html=True)
    
    tape_divider()

    st.markdown("""
        <div style="padding: 0 40px;">
        <div style="margin:32px 0;">
            <p style="font-family:var(--font-head);font-size:14px;letter-spacing:3px;color:var(--gold);text-transform:uppercase;margin-bottom:16px;">
                ⚡ Pro Tips
            </p>
            <div class="tip-box">
                <strong>Enhancement + Detection combo:</strong> Apply Histogram Equalisation and Sharpen before enabling blood detection — this significantly improves stain visibility on dark or low-contrast scenes.
            </div>
            <div class="tip-box">
                <strong>Chaining techniques:</strong> You can enable multiple modules simultaneously. Blood detection and face detection can run together — stain outlines are composited on top of the face detection output.
            </div>
            <div class="tip-box">
                <strong>Impact point detection:</strong> Set Min Contour Area to 100-300 for small bullet holes. Larger values filter out small circular features.
            </div>
            <div class="warn-box">
                ⚠ <strong>Limitation:</strong> Blood detection accuracy depends on lighting conditions. Images with strong orange/warm lighting may produce false positives. Use the HSV sliders to manually narrow the detection range if needed.
            </div>
            <div class="warn-box">
                ⚠ <strong>Limitation:</strong> Face detection works best on images where the face is at least 60×60 pixels. Faces turned completely away from camera cannot be detected by any classical method.
            </div>
        </div>

        <div style="text-align:center;padding:40px 0;">
            <a href="?page=Analyze" style="font-family:var(--font-head);font-size:13px;letter-spacing:3px;text-transform:uppercase;padding:14px 48px;background:var(--blood);color:#fff;border:1px solid var(--blood-bright);text-decoration:none;box-shadow:0 0 30px rgba(139,0,0,0.4);">
                START ANALYZING →
            </a>
        </div>            
    """, unsafe_allow_html=True)