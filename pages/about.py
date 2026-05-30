import streamlit as st
from theme import inject_theme, tape_divider, section_header


def render():
    inject_theme("About")

    st.markdown("""
    <style>
    .about-hero {
        padding: 60px 40px 40px;
        text-align: center;
        border-bottom: 1px solid #1a1a1a;
    }
    .member-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1px;
        background: #1a1a1a;
        margin: 40px 0;
    }
    .member-card {
        background: var(--bg2);
        padding: 40px 28px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: background 0.3s;
    }
    .member-card:hover { background: rgba(139,0,0,0.06); }
    .member-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--blood), transparent);
    }
    .member-avatar {
        width: 80px; height: 80px;
        border-radius: 0;
        border: 2px solid var(--blood);
        background: #1a1a1a;
        margin: 0 auto 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        position: relative;
    }
    .member-avatar::before {
        content: '';
        position: absolute;
        inset: -4px;
        border: 1px solid rgba(139,0,0,0.3);
    }
    .member-id {
        font-family: var(--font-mono);
        font-size: 9px;
        letter-spacing: 3px;
        color: var(--blood-bright);
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .member-name {
        font-family: var(--font-head);
        font-size: 18px;
        color: var(--gold);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .member-role {
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--text-dim);
        letter-spacing: 1px;
        margin-bottom: 16px;
    }
    .member-desc {
        font-family: var(--font-mono);
        font-size: 12px;
        color: var(--text);
        line-height: 1.7;
    }
    .mission-block {
        background: #080808;
        border: 1px solid #1a1a1a;
        border-left: 4px solid var(--blood);
        padding: 40px;
        margin: 40px 0;
        position: relative;
    }
    .mission-block::before {
        content: '// MISSION STATEMENT';
        position: absolute;
        top: -10px;
        left: 20px;
        background: #080808;
        padding: 0 10px;
        font-family: var(--font-mono);
        font-size: 10px;
        color: var(--blood-bright);
        letter-spacing: 2px;
    }
    .tech-tag {
        display: inline-block;
        border: 1px solid #333;
        padding: 4px 12px;
        font-family: var(--font-mono);
        font-size: 10px;
        color: var(--text-dim);
        letter-spacing: 1px;
        margin: 4px;
        background: #0d0d0d;
    }
    .tech-tag:hover { border-color: var(--blood); color: var(--blood-bright); }
    </style>

    <!-- Hero -->
    <div class="about-hero">
        <p style="font-family:var(--font-mono);font-size:10px;letter-spacing:4px;color:var(--blood-bright);margin-bottom:12px;">
            [ CASE FILE // TEAM DOSSIER ]
        </p>
        <h1 style="font-family:var(--font-horror);font-size:56px;color:#fff;margin-bottom:12px;text-shadow:0 0 30px rgba(204,0,0,0.4);">
            The Investigators
        </h1>
        <p style="font-family:var(--font-type);font-size:15px;color:var(--text-dim);letter-spacing:2px;max-width:600px;margin:0 auto;">
            A team of three forensic imaging specialists dedicated to building tools that help uncover the truth hidden in digital evidence.
        </p>
    </div>

    <div style="padding: 0 40px;">
    """, unsafe_allow_html=True)

    tape_divider()

    st.markdown("""
        <!-- Team -->
        <div class="member-grid">
            <div class="member-card">
                <div class="member-avatar">🔍</div>
                <div class="member-id">AGENT // 001</div>
                <div class="member-name">Zoya Azad</div>
                <div class="member-role">Lead Developer & Systems Architect</div>
                <div class="member-desc">
                    Spearheaded the TraceLens architecture, built the core analysis pipeline, and integrated multi-method face detection and blood stain segmentation modules.
                </div>
            </div>
            <div class="member-card">
                <div class="member-avatar">🧬</div>
                <div class="member-id">AGENT // 002</div>
                <div class="member-name">Hafsa Choudary</div>
                <div class="member-role">Image Processing Specialist</div>
                <div class="member-desc">
                    Led the implementation of enhancement, noise reduction, and edge detection modules. Researched forensic HSV colour spaces for accurate stain classification.
                </div>
            </div>
            <div class="member-card">
                <div class="member-avatar">⚙</div>
                <div class="member-id">AGENT // 003</div>
                <div class="member-name">Aly Ansar</div>
                <div class="member-role">Detection Systems & Reporting</div>
                <div class="member-desc">
                    Developed the YuNet face detection integration, PDF report generation engine, and the multi-range blood detection algorithm refinements.
                </div>
            </div>
        </div>

        <!-- Mission -->
        <div class="mission-block">
            <p style="font-family:var(--font-type);font-size:16px;color:var(--text);line-height:1.9;">
                TraceLens was built at the intersection of <span style="color:var(--gold)">Digital Image Processing</span>
                and forensic science. Crime scene photography contains information invisible to the naked eye —
                blood patterns obscured by darkness, faces hidden in low-resolution footage, impact points lost
                in image compression. Our goal was to build a system that applies classical DIP algorithms
                — histogram equalisation, HSV segmentation, Canny and Sobel edge detection, morphological
                processing — in a way that mimics the pipeline a real forensic imaging analyst would use,
                making evidence analysis accessible, reproducible, and documented.
            </p>
            <p style="font-family:var(--font-type);font-size:16px;color:var(--text);line-height:1.9;margin-top:20px;">
                Every analysis generates a <span style="color:var(--gold)">classified forensic PDF report</span>
                with chain-of-custody tracking, case metadata, and quantified findings — not just processed images,
                but actionable investigative intelligence.
            </p>
        </div>
    """, unsafe_allow_html=True)

    tape_divider()

    st.markdown("""
        <!-- Tech stack -->
        <div style="text-align:center;padding:40px 0;">
            <p style="font-family:var(--font-mono);font-size:10px;letter-spacing:4px;color:var(--blood-bright);margin-bottom:20px;">
                [ TECHNOLOGY STACK ]
            </p>
            <div>
                <span class="tech-tag">Python 3.11</span>
                <span class="tech-tag">OpenCV 4.x</span>
                <span class="tech-tag">Streamlit</span>
                <span class="tech-tag">NumPy</span>
                <span class="tech-tag">Pillow</span>
                <span class="tech-tag">ReportLab</span>
                <span class="tech-tag">YuNet DNN</span>
                <span class="tech-tag">HOG Descriptor</span>
                <span class="tech-tag">HSV Colour Space</span>
                <span class="tech-tag">Haar Cascades</span>
                <span class="tech-tag">Morphological Ops</span>
                <span class="tech-tag">Canny / Sobel</span>
            </div>
        </div>
    """, unsafe_allow_html=True)