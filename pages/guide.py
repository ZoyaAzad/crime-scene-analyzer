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
        color: rgba(139,0,0,0.6);
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
        color: color:#c8c8c8;
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
        color:#c8c8c8;
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
        <p style="font-family:var(--font-type);font-size:15px;color:#c8c8c8;max-width:680px;line-height:1.8;letter-spacing:1px;">
            Follow this operational guide to extract maximum intelligence from your crime scene evidence.
            Each module builds on the previous — run them in order for best results.
        </p>
    </div>

    """, unsafe_allow_html=True)

    tape_divider()

    st.markdown("<div style='padding:0 40px;'>", unsafe_allow_html=True)
    st.markdown("<div class='step-grid'>", unsafe_allow_html=True)

    st.markdown("""
    <div class="step-card">
        <div class="step-number">01</div>
        <div class="step-tag">Step One</div>
        <div class="step-title">📁 Upload Evidence</div>
        <div class="step-desc"><ul>
            <li>Navigate to <strong style="color:var(--gold)">Analyze</strong> from the navbar</li>
            <li>Click the upload area and select a JPG or PNG image</li>
            <li>Supported: JPG, JPEG, PNG — up to 200MB</li>
            <li>Higher resolution yields more accurate results</li>
        </ul></div>
    </div>
    <div class="step-card">
        <div class="step-number">02</div>
        <div class="step-tag">Step Two</div>
        <div class="step-title">🗂 Fill Case Details</div>
        <div class="step-desc"><ul>
            <li>After upload, a case information form appears</li>
            <li>Enter victim/suspect name and scene location</li>
            <li>Write a brief crime scene context description</li>
            <li>All details are embedded in the final PDF report</li>
        </ul></div>
    </div>
    <div class="step-card">
        <div class="step-number">03</div>
        <div class="step-tag">Step Three</div>
        <div class="step-title">⚙ Enhancement First</div>
        <div class="step-desc"><ul>
            <li>Use <strong style="color:var(--gold)">Histogram Equalisation</strong> on dark images</li>
            <li>Increase <strong style="color:var(--gold)">Contrast</strong> for washed-out scenes</li>
            <li>Apply <strong style="color:var(--gold)">Sharpen</strong> for blurry detail</li>
            <li>Always enhance before running detection modules</li>
        </ul></div>
    </div>
    <div class="step-card">
        <div class="step-number">04</div>
        <div class="step-tag">Step Four</div>
        <div class="step-title">🌫 Noise Reduction</div>
        <div class="step-desc"><ul>
            <li><strong style="color:var(--gold)">Gaussian Blur</strong> for general graininess</li>
            <li><strong style="color:var(--gold)">Median Filter</strong> for scanned speckle noise</li>
            <li>Keep kernel small (3-7) to preserve edge detail</li>
            <li>Edge detection always runs on the clean original</li>
        </ul></div>
    </div>
    <div class="step-card">
        <div class="step-number">05</div>
        <div class="step-tag">Step Five</div>
        <div class="step-title">🩸 Blood Stain Detection</div>
        <div class="step-desc"><ul>
            <li>Check <strong style="color:var(--gold)">Enable Color Detection</strong></li>
            <li>FRESH = bright red | DRIED = dark brownish stains</li>
            <li>Fine-tune HSV sliders if presets miss stains</li>
            <li>Coverage and severity rating auto-calculated</li>
        </ul></div>
    </div>
    <div class="step-card">
        <div class="step-number">06</div>
        <div class="step-tag">Step Six</div>
        <div class="step-title">👤 Face and Object Detection</div>
        <div class="step-desc"><ul>
            <li>Check <strong style="color:var(--gold)">Detect Faces</strong> for human presence</li>
            <li>Works on frontal faces, profiles, and angled views</li>
            <li>Use <strong style="color:var(--gold)">Contours</strong> to detect objects and wounds</li>
            <li>Circular contours flagged as IMPACT POINT</li>
        </ul></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
    tape_divider()

    st.markdown("""
    <div style="padding:0 40px;">
        <div style="margin:32px 0;">
            <p style="font-family:var(--font-head);font-size:14px;letter-spacing:3px;color:var(--gold);text-transform:uppercase;margin-bottom:16px;">
                ⚡ Pro Tips
            </p>
            <div class="tip-box">
                <strong>Enhancement + Detection combo:</strong> Apply Histogram Equalisation and Sharpen before enabling blood detection — this significantly improves stain visibility on dark or low-contrast scenes.
            </div>
            <div class="tip-box">
                <strong>Chaining techniques:</strong> Multiple modules can run simultaneously. Blood detection and face detection can both be active — stain outlines are composited on top of face detection output automatically.
            </div>
            <div class="tip-box">
                <strong>Impact point detection:</strong> Set Min Contour Area to 100-300 for small bullet holes. Larger values filter out small circular features.
            </div>
            <div class="warn-box">
                <strong>Limitation:</strong> Blood detection accuracy depends on lighting. Images with strong orange/warm lighting may produce false positives. Use HSV sliders to narrow the range manually.
            </div>
            <div class="warn-box">
                <strong>Limitation:</strong> Face detection works best when the face is at least 60x60 pixels. Faces turned completely away cannot be detected by any classical method.
            </div>
        </div>
        <div style="text-align:center;padding:40px 0;">
            <a onclick="navigateTo('Analyze')" href="javascript:void(0)"
               style="font-family:var(--font-head);font-size:13px;letter-spacing:3px;
                      text-transform:uppercase;padding:14px 48px;background:var(--blood);
                      color:#fff;border:1px solid var(--blood-bright);text-decoration:none;
                      box-shadow:0 0 30px rgba(139,0,0,0.4);cursor:pointer;">
                START ANALYZING →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)