"""
theme.py — shared styles, navbar, and visual effects for TraceLens.
Import and call inject_theme() at the top of every page.
"""
import streamlit as st


GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Creepster&family=Special+Elite&family=Share+Tech+Mono&family=Oswald:wght@400;700&display=swap');

/* ── Root variables ──────────────────────────────────────── */
:root {
    --blood:      #8B0000;
    --blood-bright: #CC0000;
    --gold:       #FFD700;
    --gold-dim:   #B8960C;
    --bg:         #050505;
    --bg2:        #0d0d0d;
    --bg3:        #111111;
    --text:       #c8c8c8;
    --text-dim:   #666666;
    --green:      #00FF99;
    --font-horror: 'Creepster', cursive;
    --font-type:   'Special Elite', cursive;
    --font-mono:   'Share Tech Mono', monospace;
    --font-head:   'Oswald', sans-serif;
}

/* ── Base ────────────────────────────────────────────────── */
* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background-image: url('https://mir-s3-cdn-cf.behance.net/project_modules/fs/2b328023174489.5631e6a61b06a.jpg');
    background-attachment: fixed;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    cursor: crosshair !important;
}

/* Crime scene atmospheric overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background: 
        radial-gradient(ellipse 600px 400px at 10% 20%, rgba(139,0,0,0.1) 0%, transparent 60%),
        radial-gradient(ellipse 500px 300px at 90% 80%, rgba(139,0,0,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 400px 500px at 50% 50%, rgba(0,0,0,0.3) 0%, transparent 70%);
    pointer-events: none;
    z-index: -1;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* Remove default padding */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}
section.main > div { padding-top: 0 !important; }

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: var(--blood); border-radius: 0; }

/* ── Navbar ──────────────────────────────────────────────── */
.navbar-container {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: rgba(5,5,5,0.97);
    border-bottom: 2px solid var(--blood);
    padding: 0 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 30px rgba(139,0,0,0.4);
}
.navbar-logo {
    font-family: var(--font-horror);
    font-size: 28px;
    color: var(--blood-bright);
    letter-spacing: 3px;
    text-shadow: 0 0 20px rgba(204,0,0,0.8), 0 0 40px rgba(204,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 10px;
}
.navbar-logo span { color: var(--gold); }

/* ── Navbar buttons ──────────────────────────────────────── */
.navbar-nav-button {
    font-family: var(--font-head);
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-dim);
    padding: 8px 18px;
    background: none;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.3s;
    position: relative;
}
.navbar-nav-button::after {
    content: '';
    position: absolute;
    bottom: 0; left: 50%;
    width: 0; height: 2px;
    background: var(--blood-bright);
    transition: all 0.3s;
    transform: translateX(-50%);
}
.navbar-nav-button:hover {
    color: var(--blood-bright);
}
.navbar-nav-button:hover::after {
    width: 100%;
}
.navbar-nav-button.active {
    color: var(--gold);
    border-color: var(--gold-dim);
    background: rgba(255,215,0,0.05);
}
.navbar-nav-button.active::after {
    width: 100%;
    background: var(--gold);
}

/* ── Flickering bulb ─────────────────────────────────────── */
@keyframes flicker {
    0%,19%,21%,23%,25%,54%,56%,100% { opacity:1; text-shadow: 0 0 8px #ffee88, 0 0 20px #ffcc00, 0 0 40px #ff9900; }
    20%,24%,55% { opacity:0.3; text-shadow: none; }
}
.bulb-widget {
    position: fixed;
    top: 72px;
    right: 18px;
    z-index: 8888;
    font-size: 28px;
    animation: flicker 4s infinite;
    transform: rotate(15deg);
    pointer-events: none;
    filter: drop-shadow(0 0 6px #ffcc00);
}

/* ── Blood drip SVG animation ────────────────────────────── */
@keyframes drip {
    0%   { transform: scaleY(0) translateY(0); opacity:1; }
    70%  { transform: scaleY(1) translateY(0); opacity:1; }
    85%  { transform: scaleY(1) translateY(8px); opacity:1; }
    100% { transform: scaleY(1) translateY(20px); opacity:0; }
}
@keyframes drip-drop {
    0%,80%  { transform: scale(0); opacity:0; }
    85%     { transform: scale(1); opacity:0.8; }
    100%    { transform: scale(1.4); opacity:0; }
}
.blood-bar {
    position: fixed;
    top: 64px;
    left: 0; right: 0;
    height: 28px;
    pointer-events: none;
    z-index: 9990;
    overflow: visible;
}
.drip {
    position: absolute;
    top: 0;
    width: 10px;
    background: var(--blood);
    border-radius: 0 0 6px 6px;
    transform-origin: top center;
    animation: drip linear infinite;
}
.drip::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 14px; height: 14px;
    background: var(--blood);
    border-radius: 50%;
    animation: drip-drop linear infinite;
    animation-duration: inherit;
    animation-delay: inherit;
}

/* ── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg3) !important;
    border-right: 2px solid var(--blood) !important;
}
section[data-testid="stSidebar"] * {
    font-family: var(--font-mono) !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    background: #0d0d0d !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold-dim) !important;
    border-radius: 0 !important;
    font-family: var(--font-head) !important;
    font-size: 12px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: var(--gold) !important;
    color: #000 !important;
    box-shadow: 0 0 20px rgba(255,215,0,0.4) !important;
}

/* ── Inputs, selects, sliders ────────────────────────────── */
.stSlider label, .stCheckbox label,
.stSelectbox label, .stFileUploader label,
.stTextArea label, .stTextInput label {
    color: var(--gold) !important;
    font-family: var(--font-mono) !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
.stTextArea textarea, .stTextInput input {
    background: #0d0d0d !important;
    color: var(--text) !important;
    border: 1px solid #333 !important;
    border-radius: 0 !important;
    font-family: var(--font-mono) !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--blood) !important;
    box-shadow: 0 0 10px rgba(139,0,0,0.3) !important;
}
div[data-testid="stFileUploader"] {
    border:  none !important;
    background: rgba(139,0,0,0.05) !important;
    border-radius: 0 !important;
}
.stSelectbox > div > div {
    background: #0d0d0d !important;
    border: 1px solid #333 !important;
    border-radius: 0 !important;
    color: var(--text) !important;
}

/* ── Download button ─────────────────────────────────────── */
div[data-testid="stDownloadButton"] > button {
    background: rgba(0,255,153,0.05) !important;
    color: var(--green) !important;
    border: 1px solid var(--green) !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: var(--green) !important;
    color: #000 !important;
}

/* ── Section headers ─────────────────────────────────────── */
h1,h2,h3,h4,h5,h6 {
    font-family: var(--font-head) !important;
    color: var(--gold) !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
}

/* ── Evidence card ───────────────────────────────────────── */
.evidence-card {
    background: #0d0d0d;
    border: 1px solid #222;
    border-left: 3px solid var(--blood);
    padding: 16px 20px;
    margin-bottom: 12px;
    font-family: var(--font-mono);
    font-size: 13px;
}
.evidence-card .label {
    color: var(--gold);
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 4px;
}

/* ── Findings log ────────────────────────────────────────── */
.findings-box {
    background: #080808;
    border: 1px solid #1a1a1a;
    border-left: 3px solid var(--green);
    padding: 16px;
    font-family: var(--font-mono);
    font-size: 12px;
    line-height: 1.8;
}

/* ── Image frames ────────────────────────────────────────── */
.img-frame {
    border: 2px solid #222;
    position: relative;
    overflow: hidden;
}
.img-frame::before {
    content: '';
    position: absolute;
    inset: 0;
    border: 1px solid rgba(139,0,0,0.3);
    pointer-events: none;
    z-index: 1;
}
.img-label {
    background: var(--blood);
    color: #fff;
    font-family: var(--font-head);
    font-size: 11px;
    letter-spacing: 3px;
    padding: 4px 12px;
    text-transform: uppercase;
    display: inline-block;
    margin-bottom: 6px;
}

/* ── Divider ─────────────────────────────────────────────── */
.tape-divider {
    height: 24px;
    background: repeating-linear-gradient(
        90deg,
        #FFD700 0px, #FFD700 30px,
        #111 30px, #111 60px
    );
    opacity: 0.6;
    margin: 24px 0;
    position: relative;
}
.tape-divider::before {
    content: '◆ DO NOT CROSS ◆ CRIME SCENE ◆ DO NOT CROSS ◆ CRIME SCENE ◆ DO NOT CROSS ◆ CRIME SCENE ◆ DO NOT CROSS ◆';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-family: var(--font-head);
    font-size: 9px;
    font-weight: 700;
    color: #111;
    white-space: nowrap;
    letter-spacing: 2px;
}

/* ── Scanline overlay ────────────────────────────────────── */
.scanlines {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 7000;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
    );
}

/* ── Glitch text ─────────────────────────────────────────── */
@keyframes glitch1 {
    0%,100% { clip-path: inset(0 0 95% 0); transform: translate(-3px,0); }
    25%     { clip-path: inset(40% 0 50% 0); transform: translate(3px,0); }
    50%     { clip-path: inset(20% 0 70% 0); transform: translate(-2px,0); }
    75%     { clip-path: inset(60% 0 30% 0); transform: translate(2px,0); }
}
@keyframes glitch2 {
    0%,100% { clip-path: inset(50% 0 40% 0); transform: translate(3px,0); color: #00ccff; }
    33%     { clip-path: inset(10% 0 80% 0); transform: translate(-3px,0); color: var(--blood-bright); }
    66%     { clip-path: inset(80% 0 10% 0); transform: translate(2px,0); }
}
.glitch {
    position: relative;
    display: inline-block;
}
.glitch::before, .glitch::after {
    content: attr(data-text);
    position: absolute;
    inset: 0;
    font-family: inherit;
    font-size: inherit;
    font-weight: inherit;
}
.glitch::before { animation: glitch1 3s infinite; color: var(--blood-bright); }
.glitch::after  { animation: glitch2 3s infinite 0.1s; }
"""


DRIP_HTML = """
<div class="blood-bar" id="bloodBar"></div>
<div class="scanlines"></div>
<div class="bulb-widget">💡</div>
<script>
(function(){
    const bar = document.getElementById('bloodBar');
    if (!bar) return;
    const positions = [3,7,11,16,21,27,33,38,43,49,54,59,64,69,74,79,84,89,93,97];
    const heights   = [18,32,14,44,22,36,12,28,40,16,24,38,20,34,10,42,26,30,46,8];
    const durations = [2.1,3.4,1.8,4.2,2.7,3.1,1.5,3.8,2.3,4.5,2.0,3.6,1.9,4.0,2.5,3.2,1.7,3.9,2.8,4.3];
    const delays    = [0,0.8,1.6,0.3,1.1,2.0,0.5,1.4,2.3,0.7,1.9,0.2,1.3,2.5,0.6,1.7,0.4,2.1,1.0,2.8];
    positions.forEach((p,i)=>{
        const d = document.createElement('div');
        d.className = 'drip';
        d.style.cssText = `left:${p}%;height:${heights[i]}px;animation-duration:${durations[i]}s;animation-delay:${delays[i]}s;width:${6+Math.random()*8}px;opacity:${0.7+Math.random()*0.3}`;
        bar.appendChild(d);
    });
})();
</script>
"""


def navbar(active: str, navigate_func):
    """Render navbar with Streamlit buttons"""
    st.markdown(f"<style>{GLOBAL_CSS}</style>", unsafe_allow_html=True)
    
    # Navbar container
    col_logo, col_nav = st.columns([1, 4])
    
    with col_logo:
        st.markdown(
            """
            <div style="
                font-family: var(--font-horror);
                font-size: 24px;
                color: var(--blood-bright);
                letter-spacing: 3px;
                text-shadow: 0 0 20px rgba(204,0,0,0.8);
            ">
                🔍 TRACE<span style="color: var(--gold);">LENS</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col_nav:
        nav_cols = st.columns(5)
        pages = [
            (" Home", "Home"),
            (" About", "About"),
            (" Guide", "Guide"),
            (" Analyze", "Analyze"),
            (" Report", "Report"),
        ]
        
        for i, (label, page_name) in enumerate(pages):
            with nav_cols[i]:
                is_active = page_name == active
                btn_style = "color: var(--gold); border: 1px solid var(--gold-dim); background: rgba(255,215,0,0.05);" if is_active else ""
                
                if st.button(label, key=f"nav_{page_name}", use_container_width=True):
                    navigate_func(page_name)


def inject_theme(active_page: str = "Home"):
    """Call at the top of every page file."""
    # NOTE: Sidebar visibility is handled entirely in app.py
    # Do NOT add any sidebar show/hide CSS here — it conflicts
    
    navigate_func = st.session_state.get("navigate", lambda x: None)
    navbar(active_page, navigate_func)
    st.markdown(DRIP_HTML, unsafe_allow_html=True)

def tape_divider():
    st.markdown("<div class='tape-divider'></div>", unsafe_allow_html=True)

def section_header(icon: str, title: str, subtitle: str = ""):
    sub = (
        f"<p style='font-family:var(--font-mono);font-size:12px;color:var(--text-dim);"
        f"letter-spacing:2px;margin-top:4px;text-transform:uppercase;'>{subtitle}</p>"
        if subtitle else ""
    )
    html = (
        f"<div style='margin:28px 0 16px 0;'>"
        f"<div style='display:flex;align-items:center;gap:12px;'>"
        f"<span style='font-size:22px'>{icon}</span>"
        f"<h3 style='margin:0;font-size:18px;'>{title}</h3>"
        f"</div>"
        f"{sub}"
        f"<div style='height:2px;background:linear-gradient(90deg,var(--blood),transparent);margin-top:8px;'></div>"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)