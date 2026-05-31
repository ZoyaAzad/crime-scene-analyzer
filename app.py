import streamlit as st
 
st.set_page_config(
    page_title="TraceLens — Forensic Evidence Analyzer",
    layout="wide",
    page_icon="🔍",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* Hide Streamlit's auto-generated pages navigation */
[data-testid="stSidebarNav"] { display: none !important; }
            
[data-testid="stSidebarCollapsedControl"],
button[data-testid="collapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
}
span[data-testid="stIconMaterial"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

def navigate_to(page_name):
    st.session_state.current_page = page_name
    # Expand sidebar automatically when going to Analyze
    if page_name == "Analyze":
        st.session_state["sidebar_expanded"] = True
    else:
        st.session_state["sidebar_expanded"] = False
    st.rerun()

st.session_state.navigate = navigate_to

from pages import home, about, guide, analyze, report

page = st.session_state.current_page

# Sidebar visibility — handle BEFORE rendering any page
if page == "Analyze":
    st.markdown("""
    <style>
    /* Hide the built-in pages nav */
    [data-testid="stSidebarNav"] { display: none !important; }

    /* Let Streamlit handle sidebar width naturally — just force it visible */
    section[data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        transform: translateX(0) !important;
    }

    /* Remove the conflicting manual margin — Streamlit adds this automatically */
    section.main {
        margin-left: unset !important;
    }

    /* Hide collapse arrow */
    button[data-testid="collapsedControl"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    button[data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
if page == "Home":     home.render()
elif page == "About":  about.render()
elif page == "Guide":  guide.render()
elif page == "Analyze": analyze.render()
elif page == "Report": report.render()
else:                  home.render()