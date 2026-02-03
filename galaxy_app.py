import streamlit as st
import json
import streamlit.components.v1 as components
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Galaxy Catalog Viewscreen",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FULLSCREEN CSS ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    iframe {
        height: 100vh;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA AND FRONTEND ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_file(rel_path):
    with open(os.path.join(BASE_DIR, rel_path), 'r', encoding='utf-8') as f:
        return f.read()

# Load Pulsar Data
try:
    with open(os.path.join(BASE_DIR, 'data/pulsars.json'), 'r') as f:
        PULSARS = json.load(f)
except Exception as e:
    st.error(f"Error loading pulsar data: {e}")
    PULSARS = []

# Don't load galaxy catalog by default - use mock data for faster startup
# Users can upload their own catalog via the UI
GALAXIES = []

# Load Frontend Files
try:
    index_html = load_file('frontend/index.html')
    style_css = load_file('frontend/style.css')
    script_js = load_file('frontend/script.js')

    # Inject CSS, JS, and Data into the HTML template
    html_code = index_html.replace('{{ STYLE_CSS }}', style_css)
    html_code = html_code.replace('{{ SCRIPT_JS }}', script_js)
    html_code = html_code.replace('{{ PULSARS_JSON }}', json.dumps(PULSARS))
    html_code = html_code.replace('{{ GALAXIES_JSON }}', json.dumps(GALAXIES))

    # --- RENDER COMPONENT ---
    components.html(html_code, height=850, scrolling=False)
except Exception as e:
    st.error(f"Error loading frontend resources: {e}")