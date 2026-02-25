import streamlit as st
import json
import numpy as np
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

def healpix_pix2ang_ring(nside, ipix):
    """Convert HEALPix RING pixel index to (theta, phi) in radians.

    Uses the analytic formula for RING ordering scheme.
    theta = colatitude [0, pi], phi = longitude [0, 2*pi].
    """
    npix = 12 * nside * nside
    # Normalized pixel index
    p = ipix + 0.5

    if ipix < 2 * nside * (nside - 1):
        # North polar cap
        p_h = ipix + 1
        # Find ring index
        i_ring = int(np.floor(np.sqrt(p_h / 2 - np.sqrt(np.floor(p_h / 2)))) + 1)
        # Correct ring index
        while 2 * i_ring * (i_ring - 1) < p_h:
            if 2 * i_ring * (i_ring + 1) >= p_h:
                break
            i_ring += 1
        i_ring = int(np.floor((-1 + np.sqrt(1 + 8 * p_h)) / 4) + 1)
        # Recompute more carefully
        i_ring = 0
        s = 0
        while s + 4 * (i_ring + 1) < ipix + 1:
            s += 4 * (i_ring + 1)
            i_ring += 1
        i_ring += 1  # 1-indexed
        j = ipix + 1 - 2 * i_ring * (i_ring - 1)

        theta = np.arccos(1 - i_ring * i_ring / (3.0 * nside * nside))
        phi = (j - 0.5) * np.pi / (2 * i_ring)

    elif ipix < npix - 2 * nside * (nside - 1):
        # Equatorial belt
        ip = ipix - 2 * nside * (nside - 1)
        i_ring = ip // (4 * nside) + nside  # ring index (0-based from north pole)
        j = ip % (4 * nside) + 1

        s = (i_ring - nside + 1) % 2  # shift for odd rings
        theta = np.arccos((2.0 * nside - i_ring) / (1.5 * nside))
        phi = (j - (1 + s) / 2.0) * np.pi / (2 * nside)

    else:
        # South polar cap (mirror of north)
        ip = npix - ipix  # count from south pole
        i_ring_s = 0
        s = 0
        while s + 4 * (i_ring_s + 1) < ip:
            s += 4 * (i_ring_s + 1)
            i_ring_s += 1
        i_ring_s += 1  # 1-indexed ring from south pole
        j = ip - 2 * i_ring_s * (i_ring_s - 1)

        theta = np.arccos(-1 + i_ring_s * i_ring_s / (3.0 * nside * nside))
        phi = (j - 0.5) * np.pi / (2 * i_ring_s)

    return float(theta), float(phi)


def load_healpix_map(filepath):
    """Load a HEALPix .npy file, return JSON-friendly dict with nside and nonzero pixels."""
    data = np.load(filepath)
    npix = len(data)
    nside = int(np.sqrt(npix / 12))
    assert 12 * nside * nside == npix, f"Invalid HEALPix map: {npix} pixels"

    pixels = []
    for ipix in range(npix):
        prob = data[ipix]
        if prob > 0:
            theta, phi = healpix_pix2ang_ring(nside, ipix)
            # Convert to RA/Dec (degrees)
            dec = 90.0 - np.degrees(theta)
            ra = np.degrees(phi)
            pixels.append({
                'ipix': int(ipix),
                'ra': round(float(ra), 4),
                'dec': round(float(dec), 4),
                'prob': float(prob)
            })

    return {
        'nside': int(nside),
        'npix': int(npix),
        'pixels': pixels
    }


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

# Scan data/ for all .npy HEALPix skymap files and pre-load them
HEALPIX_FILES = {}
data_dir = os.path.join(BASE_DIR, 'data')
try:
    for fname in sorted(os.listdir(data_dir)):
        if fname.endswith('.npy'):
            try:
                fpath = os.path.join(data_dir, fname)
                HEALPIX_FILES[fname] = load_healpix_map(fpath)
            except Exception as e:
                st.warning(f"Skipping {fname}: {e}")
except Exception as e:
    st.error(f"Error scanning data/ for HEALPix maps: {e}")

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
    html_code = html_code.replace('{{ HEALPIX_FILES_JSON }}', json.dumps(HEALPIX_FILES))

    # --- RENDER COMPONENT ---
    components.html(html_code, height=850, scrolling=False)
except Exception as e:
    st.error(f"Error loading frontend resources: {e}")