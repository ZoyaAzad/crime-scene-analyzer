import streamlit as st
from theme import inject_theme, tape_divider


def render():
    inject_theme("Home")

    st.markdown("""
    <style>
    /* ── Hero ────────────────────────────────────────── */
    .hero {
        min-height: 88vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
        padding: 60px 20px;
    }

    /* Cracked mirror / blood splatter background */
    .hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background:
            radial-gradient(ellipse 200px 300px at 15% 20%, rgba(139,0,0,0.18) 0%, transparent 70%),
            radial-gradient(ellipse 150px 200px at 80% 15%, rgba(139,0,0,0.12) 0%, transparent 70%),
            radial-gradient(ellipse 100px 150px at 60% 75%, rgba(139,0,0,0.15) 0%, transparent 70%),
            radial-gradient(ellipse 80px 120px at 30% 85%, rgba(139,0,0,0.10) 0%, transparent 70%),
            radial-gradient(ellipse 300px 400px at 50% 50%, rgba(20,0,0,0.6) 0%, transparent 80%),
            url("data:image/svg+xml,%3Csvg width='800' height='600' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 0;
    }

    /* Crack lines SVG overlay */
    .crack-overlay {
        position: absolute;
        inset: 0;
        pointer-events: none;
        z-index: 1;
        opacity: 0.25;
    }

    /* Blood splatter spots */
    .splatter {
        position: absolute;
        border-radius: 50%;
        background: radial-gradient(circle, #8B0000 0%, #4a0000 60%, transparent 100%);
        pointer-events: none;
        z-index: 1;
    }

    .hero-content {
        position: relative;
        z-index: 2;
        text-align: center;
        max-width: 900px;
    }

    .hero-eyebrow {
        font-family: var(--font-mono);
        font-size: 11px;
        letter-spacing: 5px;
        color: var(--blood-bright);
        text-transform: uppercase;
        margin-bottom: 20px;
        opacity: 0;
        animation: fadeUp 0.8s 0.3s forwards;
    }

    @keyframes fadeUp {
        from { opacity:0; transform: translateY(20px); }
        to   { opacity:1; transform: translateY(0); }
    }

    .hero-title {
        font-family: var(--font-horror);
        font-size: clamp(60px, 10vw, 120px);
        color: #fff;
        line-height: 1;
        margin-bottom: 8px;
        text-shadow:
            0 0 30px rgba(204,0,0,0.6),
            0 0 80px rgba(139,0,0,0.3),
            4px 4px 0px #4a0000;
        opacity: 0;
        animation: fadeUp 1s 0.5s forwards;
    }
    .hero-title .blood-word {
        color: var(--blood-bright);
        text-shadow:
            0 0 20px rgba(204,0,0,0.9),
            0 0 60px rgba(204,0,0,0.5),
            3px 3px 0 #2a0000;
    }

    .hero-subtitle {
        font-family: var(--font-type);
        font-size: clamp(14px, 2vw, 20px);
        color: var(--text-dim);
        letter-spacing: 4px;
        text-transform: uppercase;
        margin: 16px 0 40px;
        opacity: 0;
        animation: fadeUp 1s 0.8s forwards;
    }

    .hero-classified {
        display: inline-block;
        border: 2px solid var(--blood-bright);
        color: var(--blood-bright);
        font-family: var(--font-head);
        font-size: 11px;
        letter-spacing: 5px;
        padding: 6px 20px;
        text-transform: uppercase;
        margin-bottom: 48px;
        opacity: 0;
        animation: fadeUp 1s 1s forwards;
        box-shadow: 0 0 20px rgba(204,0,0,0.3), inset 0 0 20px rgba(204,0,0,0.05);
    }

    .hero-cta {
        display: flex;
        gap: 16px;
        justify-content: center;
        flex-wrap: wrap;
        opacity: 0;
        animation: fadeUp 1s 1.2s forwards;
    }

    .cta-btn {
        font-family: var(--font-head);
        font-size: 13px;
        letter-spacing: 3px;
        text-transform: uppercase;
        padding: 14px 36px;
        cursor: pointer;
        text-decoration: none !important;
        transition: all 0.3s;
        border: none;
        display: inline-block;
        color: inherit !important;
    }
    .cta-primary {
        background: var(--blood);
        color: #FFD700 !important;
        border: 1px solid var(--blood-bright);
        box-shadow: 0 0 20px rgba(139,0,0,0.5);
    }
    .cta-primary:hover {
        background: var(--blood-bright);
        box-shadow: 0 0 40px rgba(204,0,0,0.7);
        transform: translateY(-2px);
    }
    .cta-secondary {
        background: transparent;
        color: var(--gold);
        border: 1px solid var(--gold-dim);
    }
    .cta-secondary:hover {
        background: rgba(255,215,0,0.1);
        box-shadow: 0 0 20px rgba(255,215,0,0.2);
        transform: translateY(-2px);
    }

    /* ── Stats row ───────────────────────────────────── */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1px;
        background: var(--blood);
        margin: 60px 0;
        border: 1px solid var(--blood);
    }
    .stat-box {
        background: var(--bg2);
        padding: 32px 20px;
        text-align: center;
        transition: background 0.3s;
    }
    .stat-box:hover { background: rgba(139,0,0,0.1); }
    .stat-num {
        font-family: var(--font-horror);
        font-size: 48px;
        color: var(--blood-bright);
        line-height: 1;
        text-shadow: 0 0 20px rgba(204,0,0,0.5);
    }
    .stat-label {
        font-family: var(--font-mono);
        font-size: 10px;
        letter-spacing: 2px;
        color: var(--text-dim);
        text-transform: uppercase;
        margin-top: 8px;
    }

    /* ── Feature cards ───────────────────────────────── */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1px;
        background: #1a1a1a;
        margin: 40px 0;
    }
    .feature-card {
        background: var(--bg2);
        padding: 32px 24px;
        border-top: 2px solid transparent;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: var(--blood);
        transform: scaleX(0);
        transition: transform 0.3s;
    }
    .feature-card:hover::before { transform: scaleX(1); }
    .feature-card:hover { background: rgba(139,0,0,0.06); }
    .feature-icon {
        font-size: 32px;
        margin-bottom: 16px;
        display: block;
    }
    .feature-title {
        font-family: var(--font-head);
        font-size: 14px;
        letter-spacing: 2px;
        color: var(--gold);
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .feature-desc {
        font-family: var(--font-mono);
        font-size: 12px;
        color: var(--text-dim);
        line-height: 1.7;
    }

    /* ── Ticker ──────────────────────────────────────── */
    @keyframes ticker {
        from { transform: translateX(100vw); }
        to   { transform: translateX(-100%); }
    }
    .ticker-wrap {
        background: var(--blood);
        padding: 8px 0;
        overflow: hidden;
        white-space: nowrap;
        margin: 40px 0;
    }
    .ticker-text {
        display: inline-block;
        animation: ticker 25s linear infinite;
        font-family: var(--font-head);
        font-size: 12px;
        letter-spacing: 3px;
        color: #fff;
        text-transform: uppercase;
    }
    </style>

    <!-- Blood splatter spots -->
    <div class="splatter" style="width:120px;height:80px;top:18%;left:8%;opacity:0.4;transform:rotate(-20deg)"></div>
    <div class="splatter" style="width:60px;height:45px;top:12%;right:12%;opacity:0.3;transform:rotate(15deg)"></div>
    <div class="splatter" style="width:90px;height:60px;bottom:25%;right:6%;opacity:0.35;transform:rotate(-10deg)"></div>
    <div class="splatter" style="width:40px;height:30px;bottom:30%;left:5%;opacity:0.25"></div>

    <!-- SVG crack overlay -->
    <svg class="crack-overlay" viewBox="0 0 1400 900" preserveAspectRatio="xMidYMid slice">
        <path d="M200,0 L180,80 L220,160 L170,250 L210,380" stroke="#8B0000" stroke-width="1.5" fill="none"/>
        <path d="M180,80 L140,120 L160,170" stroke="#8B0000" stroke-width="0.8" fill="none"/>
        <path d="M1200,0 L1220,60 L1180,140 L1210,220 L1190,320" stroke="#8B0000" stroke-width="1.5" fill="none"/>
        <path d="M700,900 L680,820 L720,740 L690,660" stroke="#8B0000" stroke-width="1" fill="none"/>
    </svg>

    <!-- Hero section -->
    <div class="hero">
        <div class="hero-content">
            <p class="hero-eyebrow">[ CLASSIFIED SYSTEM — AUTHORIZED ACCESS ONLY ]</p>
            <h1 class="hero-title glitch" data-text="CRIME MYSTERY">
                CRIME <span class="blood-word">MYSTERY</span>
            </h1>
            <p class="hero-subtitle">TraceLens — Forensic Digital Evidence Analyzer</p>
            <div class="hero-classified">TOP SECRET // FORENSIC DIVISION // CASE ACTIVE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero CTA buttons using Streamlit navigation
    col1, col2, col3, col4, col5 = st.columns([1, 1.2, 0.3, 1.2, 1])
    with col2:
        if st.button("⚡ BEGIN ANALYSIS", key="hero_analyze", use_container_width=True):
            st.session_state.current_page = "Analyze"
            st.session_state["sidebar_expanded"] = True
            st.rerun()
    with col4:
        if st.button("📖 HOW IT WORKS", key="hero_guide", use_container_width=True):
            st.session_state.current_page = "Guide"
            st.session_state["sidebar_expanded"] = False
            st.rerun()

    st.markdown("""
    <!-- Ticker -->
    <div class="ticker-wrap">
        <span class="ticker-text">
            ⚠ CRIME SCENE — DO NOT CROSS &nbsp;•&nbsp; EVIDENCE ANALYSIS IN PROGRESS &nbsp;•&nbsp;
            AUTHORIZED PERSONNEL ONLY &nbsp;•&nbsp; FORENSIC IMAGING SYSTEM ACTIVE &nbsp;•&nbsp;
            CLASSIFIED DATA — RESTRICTED ACCESS &nbsp;•&nbsp; TRACELENS v2.0 ONLINE &nbsp;•&nbsp;
            ⚠ CRIME SCENE — DO NOT CROSS &nbsp;•&nbsp; EVIDENCE ANALYSIS IN PROGRESS &nbsp;•&nbsp;
        </span>
    </div>

    <!-- Stats -->
    <div style="padding: 0 40px;">
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-num">6</div>
                <div class="stat-label">Analysis Modules</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">4</div>
                <div class="stat-label">Blood Detection Ranges</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">3</div>
                <div class="stat-label">Face Detection Methods</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">PDF</div>
                <div class="stat-label">Forensic Report Output</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tape_divider()

    # Feature cards
    st.markdown("""
    <div style="padding: 0 40px;">
        <div style="text-align:center;margin-bottom:32px;">
            <p style="font-family:var(--font-mono);font-size:10px;letter-spacing:4px;color:var(--blood-bright);text-transform:uppercase;">
                SYSTEM CAPABILITIES
            </p>
            <h2 style="font-family:var(--font-horror);font-size:36px;color:#fff;letter-spacing:2px;">
                What We Detect
            </h2>
        </div>
        <div class="features-grid">
            <div class="feature-card">
                <span class="feature-icon">🩸</span>
                <div class="feature-title">Blood Stain Analysis</div>
                <div class="feature-desc">Multi-range HSV segmentation detects fresh, dried, and dark-surface blood. Calculates coverage percentage and severity rating.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">👤</span>
                <div class="feature-title">Face & Body Detection</div>
                <div class="feature-desc">YuNet DNN + Haar cascade ensemble. Detects frontal faces, side profiles, and lying-down persons with confidence scoring.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🔎</span>
                <div class="feature-title">Edge & Object Detection</div>
                <div class="feature-desc">Canny, Sobel, and contour-based analysis. Flags circular objects as potential impact or bullet entry points using circularity ratios.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">⚡</span>
                <div class="feature-title">Image Enhancement</div>
                <div class="feature-desc">Histogram equalisation, contrast adjustment, Laplacian sharpening, Gaussian and median noise reduction for degraded evidence.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">📋</span>
                <div class="feature-title">Forensic PDF Report</div>
                <div class="feature-desc">Auto-generated classified report with case metadata, evidence imagery, technique pipeline, findings table, and chain-of-custody block.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🗂</span>
                <div class="feature-title">Case File System</div>
                <div class="feature-desc">Attach case number, victim/suspect info, scene description, and investigator notes. All data flows directly into the final report.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tape_divider()

    st.markdown("""
    <div style="text-align:center;padding:60px 40px;">
        <p style="font-family:var(--font-type);font-size:16px;color:#c8c8c8;letter-spacing:2px;font-style:italic;">
            "Every pixel tells a story. Every shadow hides the truth."
        </p>
        <div style="margin-top:32px;" id="case-file-btn-placeholder"></div>
    </div>
    """, unsafe_allow_html=True)

    # Bottom CTA button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("OPEN THE CASE FILE →", key="bottom_analyze", use_container_width=True):
            st.session_state.current_page = "Analyze"
            st.session_state["sidebar_expanded"] = True
            st.rerun()