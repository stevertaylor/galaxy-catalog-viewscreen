import streamlit as st
import json
import streamlit.components.v1 as components

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

# --- PULSAR DATA (NANOGrav 15yr) ---
PULSARS = [
  {"id": "J0023+0923", "ra": 5.8, "dec": 9.4, "type": "Pulsar", "p0": 3.05},
  {"id": "J0030+0451", "ra": 7.6, "dec": 4.8, "type": "Pulsar", "p0": 4.87},
  {"id": "J0340+4130", "ra": 55.0, "dec": 41.5, "type": "Pulsar", "p0": 3.30},
  {"id": "J0406+3039", "ra": 61.5, "dec": 30.6, "type": "Pulsar", "p0": 4.20},
  {"id": "J0437-4715", "ra": 69.3, "dec": -47.2, "type": "Pulsar", "p0": 5.76},
  {"id": "J0509+0856", "ra": 77.3, "dec": 8.9, "type": "Pulsar", "p0": 4.06},
  {"id": "J0557+1551", "ra": 89.3, "dec": 15.8, "type": "Pulsar", "p0": 2.55},
  {"id": "J0605+3757", "ra": 91.3, "dec": 37.9, "type": "Pulsar", "p0": 2.73},
  {"id": "J0610-2100", "ra": 92.5, "dec": -21.0, "type": "Pulsar", "p0": 3.86},
  {"id": "J0613-0200", "ra": 93.4, "dec": -2.0, "type": "Pulsar", "p0": 3.06},
  {"id": "J0636+5128", "ra": 99.0, "dec": 51.5, "type": "Pulsar", "p0": 2.87},
  {"id": "J0645+5158", "ra": 101.3, "dec": 51.9, "type": "Pulsar", "p0": 8.85},
  {"id": "J0709+0458", "ra": 107.3, "dec": 4.9, "type": "Pulsar", "p0": 4.49},
  {"id": "J0740+6620", "ra": 115.0, "dec": 66.3, "type": "Pulsar", "p0": 2.89},
  {"id": "J0931-1902", "ra": 142.8, "dec": -19.0, "type": "Pulsar", "p0": 4.64},
  {"id": "J1012+5307", "ra": 153.1, "dec": 53.1, "type": "Pulsar", "p0": 5.26},
  {"id": "J1022+1001", "ra": 155.5, "dec": 10.0, "type": "Pulsar", "p0": 16.45},
  {"id": "J1024-0719", "ra": 156.1, "dec": -7.3, "type": "Pulsar", "p0": 5.16},
  {"id": "J1125+7819", "ra": 171.3, "dec": 78.3, "type": "Pulsar", "p0": 4.20},
  {"id": "J1327+3423", "ra": 201.8, "dec": 34.4, "type": "Pulsar", "p0": 3.90},
  {"id": "J1453+1902", "ra": 223.3, "dec": 19.0, "type": "Pulsar", "p0": 5.79},
  {"id": "J1455-3330", "ra": 223.9, "dec": -33.5, "type": "Pulsar", "p0": 7.99},
  {"id": "J1600-3053", "ra": 240.1, "dec": -30.9, "type": "Pulsar", "p0": 3.60},
  {"id": "J1614-2230", "ra": 243.6, "dec": -22.5, "type": "Pulsar", "p0": 3.15},
  {"id": "J1630+3734", "ra": 247.6, "dec": 37.6, "type": "Pulsar", "p0": 4.30},
  {"id": "J1640+2224", "ra": 250.1, "dec": 22.4, "type": "Pulsar", "p0": 3.16},
  {"id": "J1643-1224", "ra": 250.9, "dec": -12.4, "type": "Pulsar", "p0": 4.62},
  {"id": "J1705-1903", "ra": 256.3, "dec": -19.1, "type": "Pulsar", "p0": 3.50},
  {"id": "J1713+0747", "ra": 258.4, "dec": 7.8, "type": "Pulsar", "p0": 4.57},
  {"id": "J1719-1438", "ra": 259.8, "dec": -14.6, "type": "Pulsar", "p0": 5.00},
  {"id": "J1730-2304", "ra": 262.6, "dec": -23.1, "type": "Pulsar", "p0": 8.12},
  {"id": "J1738+0333", "ra": 264.5, "dec": 3.5, "type": "Pulsar", "p0": 5.85},
  {"id": "J1741+1351", "ra": 265.3, "dec": 13.8, "type": "Pulsar", "p0": 3.75},
  {"id": "J1744-1134", "ra": 266.1, "dec": -11.6, "type": "Pulsar", "p0": 4.07},
  {"id": "J1745+1017", "ra": 266.3, "dec": 10.3, "type": "Pulsar", "p0": 2.65},
  {"id": "J1747-4036", "ra": 266.9, "dec": -40.6, "type": "Pulsar", "p0": 1.65},
  {"id": "J1751-2857", "ra": 267.8, "dec": -28.9, "type": "Pulsar", "p0": 3.91},
  {"id": "J1802-2124", "ra": 270.6, "dec": -21.4, "type": "Pulsar", "p0": 12.65},
  {"id": "J1811-2405", "ra": 272.8, "dec": -24.1, "type": "Pulsar", "p0": 2.66},
  {"id": "J1832-0836", "ra": 278.1, "dec": -8.6, "type": "Pulsar", "p0": 2.72},
  {"id": "J1843-1113", "ra": 280.8, "dec": -11.2, "type": "Pulsar", "p0": 1.85},
  {"id": "J1853+1303", "ra": 283.3, "dec": 13.0, "type": "Pulsar", "p0": 4.09},
  {"id": "B1855+09", "ra": 284.4, "dec": 9.7, "type": "Pulsar", "p0": 5.36},
  {"id": "J1903+0327", "ra": 285.8, "dec": 3.4, "type": "Pulsar", "p0": 2.15},
  {"id": "J1909-3744", "ra": 287.4, "dec": -37.7, "type": "Pulsar", "p0": 2.95},
  {"id": "J1910+1256", "ra": 287.6, "dec": 12.9, "type": "Pulsar", "p0": 4.98},
  {"id": "J1911+1347", "ra": 287.8, "dec": 13.8, "type": "Pulsar", "p0": 4.63},
  {"id": "J1918-0642", "ra": 289.6, "dec": -6.7, "type": "Pulsar", "p0": 7.65},
  {"id": "J1923+2515", "ra": 290.8, "dec": 25.2, "type": "Pulsar", "p0": 3.79},
  {"id": "B1937+21", "ra": 294.8, "dec": 21.6, "type": "Pulsar", "p0": 1.56},
  {"id": "J1944+0907", "ra": 296.0, "dec": 9.1, "type": "Pulsar", "p0": 5.19},
  {"id": "J1946+3417", "ra": 296.6, "dec": 34.3, "type": "Pulsar", "p0": 3.17},
  {"id": "B1953+29", "ra": 298.3, "dec": 29.1, "type": "Pulsar", "p0": 6.13},
  {"id": "J2010-1323", "ra": 302.5, "dec": -13.4, "type": "Pulsar", "p0": 5.22},
  {"id": "J2017+0603", "ra": 304.3, "dec": 6.0, "type": "Pulsar", "p0": 2.90},
  {"id": "J2033+1734", "ra": 308.3, "dec": 17.6, "type": "Pulsar", "p0": 5.95},
  {"id": "J2043+1711", "ra": 310.8, "dec": 17.2, "type": "Pulsar", "p0": 2.38},
  {"id": "J2124-3358", "ra": 321.1, "dec": -33.9, "type": "Pulsar", "p0": 4.93},
  {"id": "J2145-0750", "ra": 326.4, "dec": -7.8, "type": "Pulsar", "p0": 16.05},
  {"id": "J2214+3000", "ra": 333.6, "dec": 30.0, "type": "Pulsar", "p0": 3.12},
  {"id": "J2229+2643", "ra": 337.3, "dec": 26.7, "type": "Pulsar", "p0": 2.98},
  {"id": "J2234+0611", "ra": 338.6, "dec": 6.2, "type": "Pulsar", "p0": 3.58},
  {"id": "J2234+0944", "ra": 338.6, "dec": 9.7, "type": "Pulsar", "p0": 3.63},
  {"id": "J2302+4442", "ra": 345.6, "dec": 44.7, "type": "Pulsar", "p0": 5.19},
  {"id": "J2317+1439", "ra": 349.4, "dec": 14.6, "type": "Pulsar", "p0": 3.45},
  {"id": "J2322+2057", "ra": 350.6, "dec": 20.9, "type": "Pulsar", "p0": 4.81},
  {"id": "J1231-1411", "ra": 187.9, "dec": -14.2, "type": "Pulsar", "p0": 3.68}
]

# --- FRONTEND CODE ---

html_code_template = """
<!DOCTYPE html>
<html>
<head>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; }
  
  body { 
    margin: 0; 
    background: linear-gradient(135deg, #0c1222 0%, #0f172a 50%, #1a1f35 100%);
    color: #e2e8f0; 
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
    overflow: hidden; 
  }
  
  .container { display: flex; height: 100vh; }
  
  .controls { 
    width: 320px; 
    background: rgba(30, 41, 59, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 20px; 
    border-right: 1px solid rgba(71, 85, 105, 0.5); 
    display: flex; 
    flex-direction: column;
    overflow-y: auto;
  }
  
  .viewscreen { 
    flex: 1; 
    position: relative; 
    background: radial-gradient(ellipse at center, #0a0e1a 0%, #050810 70%, #000000 100%);
    display: flex; 
    align-items: center; 
    justify-content: center;
    overflow: hidden;
  }
  
  /* Milky Way Background */
  .milkyway-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/ESO_-_Milky_Way.jpg/1280px-ESO_-_Milky_Way.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    opacity: 0.18;
    filter: saturate(0.6) brightness(0.8);
    pointer-events: none;
    z-index: 0;
  }
  
  .milkyway-bg.hidden {
    display: none;
  }
  
  /* Starfield layers */
  .starfield {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 0;
  }
  
  .starfield.hidden {
    display: none;
  }
  
  .stars-layer {
    position: absolute;
    top: 0;
    left: 0;
    width: 200%;
    height: 200%;
    background-image: 
      radial-gradient(1.5px 1.5px at 20px 30px, rgba(255,255,255,0.7), transparent),
      radial-gradient(1.5px 1.5px at 40px 70px, rgba(255,255,255,0.6), transparent),
      radial-gradient(1.5px 1.5px at 50px 160px, rgba(255,255,255,0.8), transparent),
      radial-gradient(1.5px 1.5px at 90px 40px, rgba(255,255,255,0.5), transparent),
      radial-gradient(1.5px 1.5px at 130px 80px, rgba(255,255,255,0.65), transparent),
      radial-gradient(2px 2px at 160px 120px, rgba(255,255,255,0.75), transparent),
      radial-gradient(1.5px 1.5px at 200px 50px, rgba(255,255,255,0.55), transparent),
      radial-gradient(1.5px 1.5px at 220px 140px, rgba(255,255,255,0.7), transparent),
      radial-gradient(1.5px 1.5px at 250px 90px, rgba(255,255,255,0.45), transparent),
      radial-gradient(2px 2px at 280px 160px, rgba(255,255,255,0.8), transparent),
      radial-gradient(1.5px 1.5px at 70px 110px, rgba(255,255,255,0.6), transparent),
      radial-gradient(1.5px 1.5px at 180px 180px, rgba(255,255,255,0.55), transparent);
    background-size: 300px 200px;
    animation: drift 120s linear infinite;
  }
  
  .stars-layer.layer-2 {
    background-image: 
      radial-gradient(1.5px 1.5px at 10px 10px, rgba(200,220,255,0.6), transparent),
      radial-gradient(1.5px 1.5px at 60px 90px, rgba(255,230,200,0.55), transparent),
      radial-gradient(1.5px 1.5px at 100px 50px, rgba(200,255,255,0.7), transparent),
      radial-gradient(1.5px 1.5px at 140px 130px, rgba(255,255,230,0.5), transparent),
      radial-gradient(2px 2px at 180px 20px, rgba(255,200,200,0.6), transparent),
      radial-gradient(1.5px 1.5px at 210px 110px, rgba(230,230,255,0.55), transparent),
      radial-gradient(1.5px 1.5px at 260px 60px, rgba(255,255,200,0.65), transparent),
      radial-gradient(1.5px 1.5px at 35px 150px, rgba(220,240,255,0.5), transparent),
      radial-gradient(1.5px 1.5px at 120px 170px, rgba(255,240,220,0.55), transparent);
    background-size: 280px 180px;
    animation: drift 180s linear infinite reverse;
    opacity: 0.85;
  }
  
  .stars-layer.layer-3 {
    background-image: 
      radial-gradient(2.5px 2.5px at 30px 50px, rgba(255,255,255,0.85), transparent),
      radial-gradient(2.5px 2.5px at 150px 100px, rgba(200,220,255,0.75), transparent),
      radial-gradient(2px 2px at 240px 30px, rgba(255,230,200,0.7), transparent),
      radial-gradient(2.5px 2.5px at 80px 140px, rgba(255,255,255,0.8), transparent),
      radial-gradient(2px 2px at 200px 170px, rgba(220,240,255,0.65), transparent);
    background-size: 320px 220px;
    animation: twinkle 3s ease-in-out infinite, drift 200s linear infinite;
    opacity: 0.75;
  }
  
  @keyframes drift {
    from { transform: translate(0, 0); }
    to { transform: translate(-150px, -100px); }
  }
  
  @keyframes twinkle {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1.0; }
  }
  
  canvas { display: block; }
  
  /* Section Headers */
  .section-header {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(71, 85, 105, 0.3);
  }
  
  /* Button Styles */
  .btn-group { display: flex; gap: 6px; margin-bottom: 20px; }
  
  button { 
    flex: 1; 
    background: rgba(51, 65, 85, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(71, 85, 105, 0.5); 
    color: #94a3b8; 
    padding: 10px 8px; 
    border-radius: 8px; 
    cursor: pointer; 
    font-size: 11px;
    font-weight: 500;
    font-family: inherit;
    transition: all 0.2s ease;
  }
  
  button:hover:not(:disabled) { 
    background: rgba(71, 85, 105, 0.8);
    border-color: rgba(100, 116, 139, 0.8);
    color: #e2e8f0;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  
  button.active { 
    background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
    border-color: #22d3ee;
    color: white; 
    box-shadow: 0 0 20px rgba(8, 145, 178, 0.4);
  }
  
  button:disabled { opacity: 0.4; cursor: not-allowed; }
  
  /* Stats Box */
  .stats-box { 
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(71, 85, 105, 0.4); 
    border-radius: 12px; 
    padding: 16px; 
    margin-bottom: 20px; 
  }
  
  .stat-row { 
    display: flex; 
    justify-content: space-between; 
    align-items: center;
    font-size: 12px; 
    margin-bottom: 8px; 
  }
  
  .stat-row:last-child { margin-bottom: 0; }
  
  .stat-label { color: #94a3b8; font-weight: 500; }
  
  .stat-val { 
    font-family: 'JetBrains Mono', monospace; 
    font-size: 14px;
    font-weight: 600;
    color: #22d3ee;
    text-shadow: 0 0 10px rgba(34, 211, 238, 0.3);
  }
  
  /* Legend */
  .legend { 
    margin-top: auto; 
    padding: 14px; 
    background: rgba(234, 179, 8, 0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(234, 179, 8, 0.25); 
    border-radius: 10px; 
    font-size: 12px; 
    font-weight: 500;
    color: #fef08a; 
    display: flex; 
    align-items: center; 
    gap: 10px; 
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .legend:hover {
    background: rgba(234, 179, 8, 0.15);
    border-color: rgba(234, 179, 8, 0.4);
  }
  
  /* Inspector Panel */
  .inspector { 
    position: absolute; 
    bottom: 15px; 
    right: 15px; 
    width: 280px; 
    background: rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(71, 85, 105, 0.5); 
    border-radius: 12px; 
    max-height: 220px; 
    overflow-y: auto; 
    font-size: 11px; 
    display: none;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  }
  
  .inspector table { width: 100%; border-collapse: collapse; }
  .inspector th, .inspector td { 
    padding: 10px 12px; 
    text-align: right; 
    border-bottom: 1px solid rgba(71, 85, 105, 0.3); 
    color: #94a3b8; 
  }
  .inspector th:first-child, .inspector td:first-child { text-align: left; }
  .inspector th { 
    font-weight: 600; 
    color: #64748b;
    text-transform: uppercase;
    font-size: 9px;
    letter-spacing: 0.05em;
  }
  
  /* Trash Button */
  .trash-btn { 
    background: rgba(239, 68, 68, 0.15) !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important; 
    color: #fca5a5 !important;
    flex: 0.5 !important;
  }
  .trash-btn:hover:not(:disabled) { 
    background: rgba(239, 68, 68, 0.3) !important;
    border-color: rgba(239, 68, 68, 0.5) !important;
  }
  
  /* File Inputs */
  .file-input-group { margin-bottom: 12px; }
  .file-input-label { 
    font-size: 11px; 
    font-weight: 500;
    color: #94a3b8; 
    display: block; 
    margin-bottom: 6px; 
  }
  
  input[type="file"] { 
    font-size: 11px; 
    font-family: inherit;
    color: #94a3b8; 
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(71, 85, 105, 0.4); 
    border-radius: 8px; 
    width: 100%; 
    padding: 8px;
    margin-bottom: 4px;
    transition: all 0.2s ease;
  }
  
  input[type="file"]:hover {
    border-color: rgba(100, 116, 139, 0.6);
    background: rgba(15, 23, 42, 0.8);
  }
  
  .status-text { 
    font-size: 11px; 
    font-weight: 500;
    color: #10b981; 
    margin-bottom: 8px; 
  }
  
  /* Loading Progress Bar */
  .progress-container {
    width: 100%;
    height: 4px;
    background: rgba(51, 65, 85, 0.6);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 8px;
    display: none;
  }
  
  .progress-container.active {
    display: block;
  }
  
  .progress-bar {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #06b6d4, #22d3ee, #a855f7);
    background-size: 200% 100%;
    animation: progressShimmer 1.5s ease infinite;
    border-radius: 2px;
    transition: width 0.1s ease-out;
  }
  
  @keyframes progressShimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
  
  .status-text.loading {
    color: #22d3ee;
  }
  
  /* Range Sliders */
  input[type="range"] {
    -webkit-appearance: none;
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: rgba(51, 65, 85, 0.6);
    outline: none;
  }
  
  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: linear-gradient(135deg, #22d3ee 0%, #0891b2 100%);
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(34, 211, 238, 0.4);
    transition: transform 0.2s ease;
  }
  
  input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.15);
  }
  
  /* Custom Scrollbar */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.4); border-radius: 3px; }
  ::-webkit-scrollbar-thumb { background: rgba(71, 85, 105, 0.6); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(100, 116, 139, 0.8); }
  
  /* Histogram Labels */
  .hist-label {
    font-size: 11px;
    font-weight: 500;
    color: #64748b;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  
  .hist-label::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 2px;
  }
  
  .hist-label.distance::before { background: #d946ef; }
  .hist-label.mass::before { background: #22d3ee; }
  
  /* Slider Control */
  .slider-control {
    margin-top: 16px;
    padding: 12px;
    background: rgba(15, 23, 42, 0.4);
    border-radius: 10px;
    border: 1px solid rgba(71, 85, 105, 0.3);
  }
  
  .slider-header {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    color: #94a3b8;
  }
  
  .slider-value {
    font-family: 'JetBrains Mono', monospace;
    color: #22d3ee;
  }
  
  /* Hover Tooltip */
  .tooltip {
    position: absolute;
    pointer-events: none;
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 12px 14px;
    font-size: 11px;
    color: #e2e8f0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 20px rgba(34, 211, 238, 0.05);
    z-index: 1000;
    opacity: 0;
    transform: translateY(5px) scale(0.98);
    transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1), transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    max-width: 220px;
  }
  
  .tooltip.visible {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  
  .tooltip-id {
    font-weight: 600;
    color: #22d3ee;
    margin-bottom: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
  }
  
  .tooltip-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 3px;
  }
  
  .tooltip-label {
    color: #94a3b8;
  }
  
  .tooltip-value {
    font-family: 'JetBrains Mono', monospace;
    color: #f8fafc;
  }
  
  .tooltip-type {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 6px;
  }
  
  .tooltip-type.galaxy {
    background: rgba(34, 211, 238, 0.2);
    color: #22d3ee;
  }
  
  .tooltip-type.pulsar {
    background: rgba(234, 179, 8, 0.2);
    color: #eab308;
  }
</style>
</head>
<body>

<div class="container">
  <div class="controls">
    <div style="font-size: 18px; font-weight: 700; color: #22d3ee; letter-spacing: -0.02em; text-shadow: 0 0 20px rgba(34, 211, 238, 0.3);">GALAXY VIEWSCREEN</div>
    <div style="font-size: 9px; color: #94a3b8; margin-bottom: 20px;">2MRS Catalog & NANOGrav Pulsars</div>

    <div style="font-size: 11px; font-weight: bold; margin-bottom: 15px; color: #f8fafc;">DATA SOURCES</div>
    
    <div class="file-input-group">
      <label class="file-input-label">Galaxy Catalog (.txt)</label>
      <input type="file" id="upload-galaxies" accept=".txt,.dat">
      <div class="progress-container" id="progress-galaxies"><div class="progress-bar" id="progress-bar-galaxies"></div></div>
      <div id="status-galaxies" class="status-text">Using synthetic data</div>
    </div>
    
    <div class="file-input-group">
      <label class="file-input-label">MCMC Chain (.txt)</label>
      <input type="file" id="upload-chain" accept=".txt,.dat">
      <div class="progress-container" id="progress-chain"><div class="progress-bar" id="progress-bar-chain"></div></div>
      <div id="status-chain" class="status-text"></div>
    </div>

    <!-- Selection Tools -->
    <div class="section-header">Selection Tools</div>
    
    <div class="btn-group">
      <button id="btn-lasso" class="active">Lasso</button>
      <button id="btn-poly">Polygon</button>
      <button id="btn-magnify">Magnify</button>
      <button id="btn-posterior" disabled>Posterior</button>
      <button id="trash-btn" class="trash-btn" title="Clear Selection">🗑️</button>
    </div>

    <!-- Statistics -->
    <div class="stats-box">
      <div class="stat-row"><span class="stat-label">TOTAL SOURCES</span> <span class="stat-val" id="count-total">0</span></div>
      <div class="stat-row"><span class="stat-label">SELECTED</span> <span class="stat-val" id="count-sel">0</span></div>
    </div>
    
    <!-- Distributions -->
    <div class="section-header">Distributions</div>
    
    <div class="hist-label distance">Distance (Mpc)</div>
    <canvas id="hist-dist" width="280" height="85" style="margin-bottom: 16px; border-radius: 6px;"></canvas>
    
    <div class="hist-label mass">log₁₀(M_SMBH / M_☉)</div>
    <canvas id="hist-mass" width="280" height="85" style="border-radius: 6px;"></canvas>

    <!-- Pulsar Legend -->
    <div class="legend" id="pulsar-toggle">
       <span>★ NANOGrav 15-yr Dataset Pulsars</span>
    </div>
    
    <!-- Twinkle Slider -->
    <div class="slider-control">
       <div class="slider-header">
         <span>PULSE DILATION</span> <span class="slider-value" id="twinkle-val">400×</span>
       </div>
       <input type="range" id="twinkle-slider" min="10" max="500" step="10" value="400">
    </div>
    
    <!-- Posterior Control -->
    <div id="posterior-control" class="slider-control" style="display: none;">
       <div class="slider-header">
         <span>CREDIBLE REGION</span> <span class="slider-value" id="cred-val">95%</span>
       </div>
       <input type="range" id="cred-slider" min="0.1" max="0.99" step="0.01" value="0.95">
    </div>
    
    <!-- Background Toggles -->
    <div class="slider-control" style="margin-top: 8px;">
       <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; font-size: 11px; font-weight: 500; color: #94a3b8; margin-bottom: 8px;">
         <input type="checkbox" id="grid-toggle" checked style="width: 16px; height: 16px; accent-color: #94a3b8;">
          <span>Coordinate Grid Overlay</span>
       </label>
       <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; font-size: 11px; font-weight: 500; color: #94a3b8; margin-bottom: 8px;">
         <input type="checkbox" id="milkyway-toggle" checked style="width: 16px; height: 16px; accent-color: #a855f7;">
         <span>Milky Way Background</span>
       </label>
       <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; font-size: 11px; font-weight: 500; color: #94a3b8; margin-bottom: 8px;">
         <input type="checkbox" id="starfield-toggle" checked style="width: 16px; height: 16px; accent-color: #22d3ee;">
          <span>Starfield Animation</span>
       </label>
       <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; font-size: 11px; font-weight: 500; color: #94a3b8;">
         <input type="checkbox" id="tooltip-toggle" checked style="width: 16px; height: 16px; accent-color: #10b981;">
          <span>Hover Tooltips</span>
       </label>
    </div>
     
    <!-- Credits -->
    <div style="margin-top: auto; padding-top: 16px; border-top: 1px solid rgba(71, 85, 105, 0.3); font-size: 9px; color: #64748b; line-height: 1.5;">
      <div style="font-weight: 600; margin-bottom: 4px; color: #94a3b8;">DEVELOPED BY</div>
      <div>Polina Petrov, Celine Mang, Stephen Taylor</div>
      <div style="margin-top: 6px;">Participants of the 2024 VIPER Summer School</div>
      <div style="margin-top: 8px; font-size: 8px; color: #475569;">Supported by NSF Award #2307719</div>
    </div>
  </div>

  <div class="viewscreen" id="map-container">
     <!-- Milky Way Background -->
     <div class="milkyway-bg" id="milkyway"></div>
     <!-- Starfield Animation -->
     <div class="starfield" id="starfield" style="z-index: 1;">
       <div class="stars-layer"></div>
       <div class="stars-layer layer-2"></div>
       <div class="stars-layer layer-3"></div>
     </div>
     <canvas id="main-canvas" style="position: relative; z-index: 1;"></canvas>
     <div class="inspector" id="inspector">
       <table>
         <thead><tr><th>ID</th><th>Data</th><th>Pos</th></tr></thead>
         <tbody id="inspector-body"></tbody>
       </table>
     </div>
     <!-- Hover Tooltip -->
     <div class="tooltip" id="tooltip">
       <div class="tooltip-id" id="tooltip-id"></div>
       <div class="tooltip-row"><span class="tooltip-label">RA</span><span class="tooltip-value" id="tooltip-ra"></span></div>
       <div class="tooltip-row"><span class="tooltip-label">Dec</span><span class="tooltip-value" id="tooltip-dec"></span></div>
       <div class="tooltip-row" id="tooltip-dist-row"><span class="tooltip-label">Dist</span><span class="tooltip-value" id="tooltip-dist"></span></div>
       <div class="tooltip-row" id="tooltip-mass-row"><span class="tooltip-label">Mass</span><span class="tooltip-value" id="tooltip-mass"></span></div>
       <div class="tooltip-type" id="tooltip-type"></div>
     </div>
  </div>
</div>

<script>
// --- DATA INJECTION ---
const initialPulsars = @@@PULSARS_JSON@@@;
let galaxyData = [];
let rawData = [];
let posteriorSamples = [];

// --- UTILS ---
function setupHighDPI(canv, w, h) {
  const dpr = window.devicePixelRatio || 1;
  canv.width = w * dpr;
  canv.height = h * dpr;
  canv.style.width = w + 'px';
  canv.style.height = h + 'px';
  const c = canv.getContext('2d');
  c.scale(dpr, dpr);
  return c;
}

function parseCoordinate(str) {
  const pattern = /^(\d{2})(\d{2})(\d{2})(\d{2})([+-])(\d{2})(\d{2})(\d{2})(\d)$/;
  const match = str.trim().match(pattern);
  if (!match) return null;
  const [_, hh, mmRa, ssRa, csRa, signStr, dd, dm, dsDec, tsDec] = match;
  const raSeconds = parseFloat(ssRa) + parseFloat(csRa) / 100.0;
  const raVal = (parseFloat(hh) + parseFloat(mmRa)/60 + raSeconds/3600) * 15.0;
  const decArcsec = parseFloat(dsDec) + parseFloat(tsDec) / 10.0;
  const sign = signStr === '-' ? -1 : 1;
  return [raVal, sign * (parseFloat(dd) + parseFloat(dm)/60 + decArcsec/3600)];
}

function generateMockData() {
  const data = [];
  for (let i = 0; i < 2000; i++) {
    const ra = Math.random() * 360;
    const dec = Math.asin(Math.random() * 2 - 1) * (180 / Math.PI);
    data.push({ id: `mock-${i}`, ra, dec, dist: Math.random() * 495 + 5, mass: Math.random() * 4.5 + 6, type: "Galaxy" });
  }
  return data;
}

async function handleGalaxyUpload(e) {
  const file = e.target.files[0];
  if(!file) return;
  
  const progressContainer = document.getElementById('progress-galaxies');
  const progressBar = document.getElementById('progress-bar-galaxies');
  const statusText = document.getElementById('status-galaxies');
  
  // Show loading state
  progressContainer.classList.add('active');
  progressBar.style.width = '0%';
  statusText.innerText = 'Reading file...';
  statusText.classList.add('loading');
  
  // Small delay to let UI update
  await new Promise(r => setTimeout(r, 10));
  
  const text = await file.text();
  progressBar.style.width = '20%';
  statusText.innerText = 'Parsing data...';
  
  await new Promise(r => setTimeout(r, 10));
  
  const lines = text.split(/\\r?\\n/);
  const totalLines = lines.length;
  const newData = [];
  
  // Process in chunks to allow UI updates
  const chunkSize = 5000;
  for (let i = 0; i < totalLines; i += chunkSize) {
    const chunk = lines.slice(i, Math.min(i + chunkSize, totalLines));
    chunk.forEach(line => {
      line = line.trim();
      if(!line || !/^\\d/.test(line)) return;
      const parts = line.split(/\\s+/);
      if(parts.length < 3) return;
      const coords = parseCoordinate(parts[0]);
      if(coords) newData.push({ id: parts[0], ra: coords[0], dec: coords[1], dist: parseFloat(parts[1]), mass: parseFloat(parts[2]), type: "Galaxy" });
    });
    
    // Update progress (20% to 80% for parsing)
    const progress = 20 + (Math.min(i + chunkSize, totalLines) / totalLines) * 60;
    progressBar.style.width = progress + '%';
    await new Promise(r => setTimeout(r, 0));
  }
  
  if(newData.length > 0) {
    progressBar.style.width = '90%';
    statusText.innerText = 'Rendering map...';
    await new Promise(r => setTimeout(r, 10));
    
    galaxyData = newData;
    refreshData();
    
    progressBar.style.width = '100%';
    statusText.classList.remove('loading');
    statusText.innerText = `Loaded ${newData.length} galaxies`;
    
    // Hide progress bar after a short delay
    setTimeout(() => progressContainer.classList.remove('active'), 500);
  } else {
    progressContainer.classList.remove('active');
    statusText.classList.remove('loading');
    statusText.innerText = 'No valid data found';
    statusText.style.color = '#f87171';
  }
}

async function handleChainUpload(e) {
  const file = e.target.files[0];
  if(!file) return;
  
  const progressContainer = document.getElementById('progress-chain');
  const progressBar = document.getElementById('progress-bar-chain');
  const statusText = document.getElementById('status-chain');
  
  // Show loading state
  progressContainer.classList.add('active');
  progressBar.style.width = '0%';
  statusText.innerText = 'Reading file...';
  statusText.classList.add('loading');
  
  await new Promise(r => setTimeout(r, 10));
  
  const text = await file.text();
  progressBar.style.width = '20%';
  statusText.innerText = 'Parsing samples...';
  
  await new Promise(r => setTimeout(r, 10));
  
  const lines = text.split(/\\r?\\n/);
  const totalLines = lines.length;
  const newSamples = [];
  
  const chunkSize = 5000;
  for (let i = 0; i < totalLines; i += chunkSize) {
    const chunk = lines.slice(i, Math.min(i + chunkSize, totalLines));
    chunk.forEach(line => {
      line = line.trim();
      if(!line || !(/^[\\d-]/.test(line))) return;
      const parts = line.split(/[ ,\\s]+/);
      if(parts.length >= 2) {
         const ra = parseFloat(parts[0]);
         const dec = parseFloat(parts[1]);
         if(!isNaN(ra) && !isNaN(dec)) newSamples.push({ ra, dec });
      }
    });
    
    const progress = 20 + (Math.min(i + chunkSize, totalLines) / totalLines) * 50;
    progressBar.style.width = progress + '%';
    await new Promise(r => setTimeout(r, 0));
  }
  
  if(newSamples.length > 0) {
    progressBar.style.width = '80%';
    statusText.innerText = 'Computing posterior...';
    await new Promise(r => setTimeout(r, 10));
    
    posteriorSamples = newSamples;
    computePosteriorMap();
    
    progressBar.style.width = '100%';
    btnPosterior.disabled = false;
    statusText.classList.remove('loading');
    statusText.innerText = `Loaded ${newSamples.length} MCMC samples`;
    draw();
    
    setTimeout(() => progressContainer.classList.remove('active'), 500);
  } else {
    progressContainer.classList.remove('active');
    statusText.classList.remove('loading');
    statusText.innerText = 'No valid samples found';
    statusText.style.color = '#f87171';
  }
}

function refreshData() {
  rawData = [...galaxyData, ...initialPulsars.map(p => ({...p, dist: 0, mass: 0, type: "Pulsar"}))];
  projectedData = rawData.map(d => {
    const p = projectMollweide(d.ra, d.dec);
    return { ...d, px: p.x, py: p.y };
  });
  pulsarPoints = projectedData.filter(d => d.type === 'Pulsar');
  buildSpatialGrid();
  document.getElementById('count-total').innerText = rawData.length;
  draw();
  drawHistograms();
}

// --- CONFIG ---
let WIDTH = 800;
let HEIGHT = 400;
const PADDING = 20;
let SCALE = (HEIGHT - PADDING * 2) / (2 * Math.sqrt(2));
const PI = Math.PI;

function updateCanvasSize() {
  const container = document.getElementById('map-container');
  if (!container) return;
  
  // Get container dimensions, leaving some margin
  const containerWidth = container.clientWidth - 40;
  const containerHeight = container.clientHeight - 40;
  
  // Maintain Mollweide aspect ratio (2:1)
  const aspectRatio = 2;
  let newWidth = containerWidth;
  let newHeight = containerWidth / aspectRatio;
  
  // If height is too tall, constrain by height
  if (newHeight > containerHeight) {
    newHeight = containerHeight;
    newWidth = containerHeight * aspectRatio;
  }
  
  // Set minimum size
  WIDTH = Math.max(400, Math.floor(newWidth));
  HEIGHT = Math.max(200, Math.floor(newHeight));
  SCALE = (HEIGHT - PADDING * 2) / (2 * Math.sqrt(2));
  
  // Resize canvas
  if (ctx) {
    ctx = setupHighDPI(canvas, WIDTH, HEIGHT);
    
    // Setup offscreen grid canvas
    const dpr = window.devicePixelRatio || 1;
    gridCanvas.width = WIDTH * dpr;
    gridCanvas.height = HEIGHT * dpr;
    gridCtx.scale(dpr, dpr);
    drawCoordinateGrid(gridCtx);

    // Ensure canvas is centered in its container
    canvas.style.position = 'absolute';
    canvas.style.left = '50%';
    canvas.style.top = '50%';
    canvas.style.transform = 'translate(-50%, -50%)';

    // Reproject data with new dimensions
    projectedData = rawData.map(d => {
      const p = projectMollweide(d.ra, d.dec);
      return { ...d, px: p.x, py: p.y };
    });
    pulsarPoints = projectedData.filter(d => d.type === 'Pulsar');
    buildSpatialGrid();
    draw();
  }
}

// --- STATE ---
let projectedData = [];
let pulsarPoints = [];
let mode = 'lasso';
let selectedIds = new Set();
let lassoPoints = [];
let isDrawing = false;
let showPulsars = true;
let mousePos = {x:0, y:0};
let spatialGrid = {};
let posteriorMap = null;
let credibleLevel = 0.95;
let animationTime = 0;
let periodScale = 400; 
let clickedId = null;
let hoveredPoint = null;
let tooltipsEnabled = true;
let showGrid = true;

// --- DOM ELEMENTS ---
const canvas = document.getElementById('main-canvas');
let ctx, distCtx, massCtx;
let gridCanvas = document.createElement('canvas');
let gridCtx = gridCanvas.getContext('2d');
const inspector = document.getElementById('inspector');
const btnPosterior = document.getElementById('btn-posterior');
const posteriorControl = document.getElementById('posterior-control');
const tooltip = document.getElementById('tooltip');

// --- INITIALIZATION ---
function init() {
  ctx = setupHighDPI(canvas, WIDTH, HEIGHT);
  distCtx = setupHighDPI(document.getElementById('hist-dist'), 270, 85);
  massCtx = setupHighDPI(document.getElementById('hist-mass'), 270, 85);
  
  galaxyData = generateMockData();
  refreshData();

  document.getElementById('upload-galaxies').addEventListener('change', handleGalaxyUpload);
  document.getElementById('upload-chain').addEventListener('change', handleChainUpload);
  
  canvas.addEventListener('mousedown', handleStart);
  canvas.addEventListener('mousemove', handleMove);
  window.addEventListener('mouseup', handleEnd);
  
  document.getElementById('btn-lasso').onclick = () => setMode('lasso');
  document.getElementById('btn-poly').onclick = () => setMode('polygon');
  document.getElementById('btn-magnify').onclick = () => setMode('magnify');
  btnPosterior.onclick = () => setMode('posterior');
  
  document.getElementById('pulsar-toggle').onclick = () => {
    showPulsars = !showPulsars;
    draw();
  };

  document.getElementById('cred-slider').oninput = (e) => {
    credibleLevel = parseFloat(e.target.value);
    document.getElementById('cred-val').innerText = Math.round(credibleLevel*100) + '%';
    if(mode === 'posterior') updateSelectionPosterior();
  };
  
  document.getElementById('twinkle-slider').oninput = (e) => {
    periodScale = parseFloat(e.target.value);
    document.getElementById('twinkle-val').innerText = periodScale + 'x';
  };
  
  document.getElementById('trash-btn').onclick = () => {
    selectedIds.clear();
    clickedId = null;
    lassoPoints = [];
    inspector.style.display = 'none';
    drawHistograms();
    updateStats();
  };
  
  document.getElementById('milkyway-toggle').onchange = (e) => {
    const milkyway = document.getElementById('milkyway');
    if (e.target.checked) {
      milkyway.classList.remove('hidden');
    } else {
      milkyway.classList.add('hidden');
    }
  };
  
  document.getElementById('starfield-toggle').onchange = (e) => {
    const starfield = document.getElementById('starfield');
    if (e.target.checked) {
      starfield.classList.remove('hidden');
    } else {
      starfield.classList.add('hidden');
    }
  };
  
  document.getElementById('tooltip-toggle').onchange = (e) => {
    tooltipsEnabled = e.target.checked;
    if (!tooltipsEnabled) {
      hoveredPoint = null;
      tooltip.classList.remove('visible');
    }
  };

  document.getElementById('grid-toggle').onchange = (e) => {
    showGrid = e.target.checked;
    draw();
  };

  draw();
  drawHistograms();
  
  // Handle window resize
  window.addEventListener('resize', () => {
    updateCanvasSize();
  });
  
  // Initial size update
  updateCanvasSize();
  
  function animate(timestamp) {
      animationTime = timestamp;
      draw();
      requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);
}

// --- MATH ---
function projectMollweide(ra, dec) {
  let lambda = (ra - 180) * (PI / 180);
  lambda = -lambda; 
  let phi = dec * (PI / 180);
  
  let theta = phi;
  for(let i=0; i<10; i++) {
     let f = 2*theta + Math.sin(2*theta) - PI*Math.sin(phi);
     let fprime = 2 + 2*Math.cos(2*theta) + 1e-12;
     theta -= f / fprime;
  }
  
  let x = (2 * Math.sqrt(2) / PI) * lambda * Math.cos(theta);
  let y = Math.sqrt(2) * Math.sin(theta);
  
  return {
    x: (x * SCALE) + (WIDTH/2),
    y: -(y * SCALE) + (HEIGHT/2)
  };
}

function buildSpatialGrid() {
  const cellSize = 20;
  const cols = Math.ceil(WIDTH/cellSize);
  const rows = Math.ceil(HEIGHT/cellSize);
  spatialGrid = { cellSize, cols, rows, bins: new Array(cols*rows).fill(null).map(()=>[]) };
  
  projectedData.forEach(d => {
     let c = Math.floor(d.px / cellSize);
     let r = Math.floor(d.py / cellSize);
     if (c >= 0 && c < cols && r >= 0 && r < rows) {
        spatialGrid.bins[r*cols + c].push(d);
     }
  });
}

function queryGrid(x, y, radius) {
  const { cellSize, cols, rows, bins } = spatialGrid;
  const results = [];
  
  // Calculate which cells to check based on radius
  const cellRadius = Math.ceil(radius / cellSize);
  const centerCol = Math.floor(x / cellSize);
  const centerRow = Math.floor(y / cellSize);
  
  // Check nearby cells
  for (let dr = -cellRadius; dr <= cellRadius; dr++) {
    for (let dc = -cellRadius; dc <= cellRadius; dc++) {
      const c = centerCol + dc;
      const r = centerRow + dr;
      
      if (c >= 0 && c < cols && r >= 0 && r < rows) {
        const cellPoints = bins[r * cols + c];
        if (cellPoints) {
          results.push(...cellPoints);
        }
      }
    }
  }
  
  return results;
}


function computePosteriorMap() {
  const res = 10;
  const cols = Math.ceil(WIDTH/res);
  const rows = Math.ceil(HEIGHT/res);
  const bins = new Float32Array(cols*rows).fill(0);
  
  posteriorSamples.forEach(s => {
     const p = projectMollweide(s.ra, s.dec);
     const c = Math.floor(p.x / res);
     const r = Math.floor(p.y / res);
     if (c>=0 && c<cols && r>=0 && r<rows) bins[r*cols+c]++;
  });
  
  const total = posteriorSamples.length;
  const probs = Array.from(bins).map(v => v/total);
  const sorted = [...probs].sort((a,b) => b-a);
  posteriorMap = { probs, sorted, cols, rows, res };
}

// --- DRAWING ---
function draw() {
  ctx.clearRect(0, 0, WIDTH, HEIGHT);
  
  if (mode === 'posterior' && posteriorMap) {
     drawPosterior();
  }

  // Draw cached coordinate grid
  if (showGrid) {
    ctx.drawImage(gridCanvas, 0, 0, WIDTH, HEIGHT);
  }

  // Draw map boundary ellipse
  ctx.strokeStyle = '#334155';
  ctx.lineWidth = 2;
  ctx.beginPath();
  const rx = (HEIGHT/2 - PADDING) * 2;
  const ry = HEIGHT/2 - PADDING;
  ctx.ellipse(WIDTH/2, HEIGHT/2, rx, ry, 0, 0, 2*PI);
  ctx.stroke();
  
  const allVisible = getVisiblePoints();
  const unselectedGalaxies = [];
  const selectedGalaxies = [];
  
  allVisible.forEach(d => {
    if (d.type === 'Pulsar') return;
    if (d === hoveredPoint) return;
    if (selectedIds.has(d.id)) {
      selectedGalaxies.push(d);
    } else {
      unselectedGalaxies.push(d);
    }
  });
  
  // Unselected galaxies - optimized core+aura passes
  ctx.save();
  ctx.fillStyle = '#94a3b8';
  ctx.globalAlpha = 0.35; // Soft aura
  ctx.beginPath();
  unselectedGalaxies.forEach(d => {
       ctx.moveTo(d.px, d.py);
       ctx.arc(d.px, d.py, 2.0, 0, 2*PI);
  });
  ctx.fill();
  
  ctx.globalAlpha = 0.8; // Sharp core
  ctx.beginPath();
  unselectedGalaxies.forEach(d => {
       ctx.moveTo(d.px, d.py);
       ctx.arc(d.px, d.py, 0.8, 0, 2*PI);
  });
  ctx.fill();
  ctx.restore();
  
  // Selected galaxies with streamlined triple-layer glow
  if (selectedGalaxies.length > 0) {
    ctx.save();
    
    // Level 1: Outer cyan bloom (Low alpha, large radius)
    ctx.shadowColor = 'rgba(34, 211, 238, 0.6)';
    ctx.shadowBlur = 12;
    ctx.fillStyle = 'rgba(34, 211, 238, 0.3)';
    ctx.beginPath();
    selectedGalaxies.forEach(d => {
        ctx.moveTo(d.px, d.py);
        ctx.arc(d.px, d.py, 5, 0, 2*PI);
    });
    ctx.fill();

    // Level 2 & 3: Consolidated Mid-glow and core
    // We can do this in one path with shadow for the mid-glow
    ctx.shadowColor = 'rgba(34, 211, 238, 0.9)';
    ctx.shadowBlur = 6;
    ctx.fillStyle = '#ffffff'; // White core with blue shadow makes it look like cyan glowing point
    ctx.beginPath();
    selectedGalaxies.forEach(d => {
        ctx.moveTo(d.px, d.py);
        ctx.arc(d.px, d.py, 2.0, 0, 2*PI);
    });
    ctx.fill();
    
    ctx.restore();
  }
  
  // Highlight hovered point
  if (hoveredPoint && hoveredPoint.type !== 'Pulsar') {
    ctx.save();
    ctx.shadowColor = 'rgba(244, 114, 182, 0.9)';
    ctx.shadowBlur = 15;
    ctx.fillStyle = '#f472b6';
    ctx.beginPath();
    ctx.arc(hoveredPoint.px, hoveredPoint.py, 4.5, 0, 2*PI);
    ctx.fill();
    
    // Pulsing ring around hovered point
    const pulse = 0.5 + 0.5 * Math.sin(animationTime * 0.005);
    ctx.strokeStyle = 'rgba(244, 114, 182, ' + (0.4 + pulse * 0.4) + ')';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(hoveredPoint.px, hoveredPoint.py, 8 + pulse * 4, 0, 2*PI);
    ctx.stroke();
    ctx.restore();
  }
  
  if (clickedId) {
      const d = projectedData.find(x => x.id === clickedId);
      if (d) {
          ctx.save();
          const pulse = 0.5 + 0.5 * Math.sin(animationTime * 0.01);
          ctx.strokeStyle = '#f472b6'; 
          ctx.lineWidth = 2;
          ctx.shadowColor = '#f472b6';
          ctx.shadowBlur = 10;
          ctx.beginPath();
          ctx.arc(d.px, d.py, 6 + pulse * 2, 0, 2*PI);
          ctx.stroke();
          
          ctx.globalAlpha = 0.4;
          ctx.setLineDash([4, 4]);
          ctx.beginPath();
          ctx.arc(d.px, d.py, 12 + pulse * 4, 0, 2*PI);
          ctx.stroke();
          ctx.restore();
      }
  }
  
  // Pulsars with high-intensity layered glow
  if (showPulsars) {
      pulsarPoints.forEach(p => {
         const period = p.p0 * periodScale; 
         const phase = (animationTime % period) / period; 
         const brightness = 0.4 + 0.6 * (0.5 + 0.5 * Math.sin(phase * 2 * PI)); 
         
         ctx.save();
         // Level 1: Outer soft glow
         ctx.shadowColor = 'rgba(234, 179, 8, ' + (brightness * 0.4) + ')';
         ctx.shadowBlur = 15 * brightness;
         ctx.globalAlpha = brightness;
         ctx.fillStyle = '#eab308';
         const sz = selectedIds.has(p.id) ? 6 : 4;
         
         if (p.id === clickedId) {
           ctx.shadowColor = 'rgba(244, 114, 182, 0.9)';
           ctx.shadowBlur = 20;
           ctx.fillStyle = '#f472b6';
         } else if (p === hoveredPoint) {
           ctx.shadowColor = 'rgba(244, 114, 182, 0.7)';
           ctx.shadowBlur = 15;
           ctx.fillStyle = '#f472b6';
         }
         
         drawStar(ctx, p.px, p.py, 5, sz, sz/2);
         
         // Level 2: Inner tight core glow
         ctx.shadowColor = (p.id === clickedId || p === hoveredPoint) ? 'white' : 'rgba(255, 255, 255, ' + (brightness * 0.8) + ')';
         ctx.shadowBlur = 4 * brightness;
         drawStar(ctx, p.px, p.py, 5, sz, sz/2);
         
         ctx.restore();
      });
      ctx.globalAlpha = 1.0;
  }

  if (lassoPoints.length > 0) {
      ctx.save();
      ctx.shadowColor = 'rgba(34, 211, 238, 0.5)';
      ctx.shadowBlur = 6;
      ctx.strokeStyle = '#22d3ee';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(lassoPoints[0].x, lassoPoints[0].y);
      for(let i=1; i<lassoPoints.length; i++) ctx.lineTo(lassoPoints[i].x, lassoPoints[i].y);
      if (mode === 'polygon' && isDrawing && mousePos) {
         ctx.lineTo(mousePos.x, mousePos.y);
      }
      ctx.stroke();
      if (mode === 'lasso' || !isDrawing) {
         ctx.fillStyle = 'rgba(34, 211, 238, 0.1)';
         ctx.fill();
      }
      ctx.restore();
  }
  
  if (mode === 'magnify') {
      drawLens(mousePos.x, mousePos.y);
  }
}

// Draw coordinate grid lines to a specific context (usually offscreen)
function drawCoordinateGrid(g) {
  g.clearRect(0, 0, WIDTH, HEIGHT);
  g.save();
  g.strokeStyle = 'rgba(71, 85, 105, 0.25)';
  g.lineWidth = 0.5;
  g.setLineDash([2, 4]);
  
  // RA lines (every 30 degrees = 2 hours)
  for (let ra = 0; ra < 360; ra += 30) {
    g.beginPath();
    let started = false;
    for (let dec = -90; dec <= 90; dec += 2) {
      const p = projectMollweide(ra, dec);
      if (!started) {
        g.moveTo(p.x, p.y);
        started = true;
      } else {
        g.lineTo(p.x, p.y);
      }
    }
    g.stroke();
  }
  
  // Dec lines (every 30 degrees)
  for (let dec = -60; dec <= 60; dec += 30) {
    if (dec === 0) continue; 
    g.beginPath();
    let started = false;
    for (let ra = 0; ra <= 360; ra += 2) {
      const p = projectMollweide(ra, dec);
      if (!started) {
        g.moveTo(p.x, p.y);
        started = true;
      } else {
        g.lineTo(p.x, p.y);
      }
    }
    g.stroke();
  }
  
  // Equator
  g.strokeStyle = 'rgba(71, 85, 105, 0.4)';
  g.setLineDash([]);
  g.beginPath();
  for (let ra = 0; ra <= 360; ra += 2) {
    const p = projectMollweide(ra, 0);
    if (ra === 0) g.moveTo(p.x, p.y); else g.lineTo(p.x, p.y);
  }
  g.stroke();
  
  // Draw grid labels
  g.save();
  g.font = '500 10px Inter, sans-serif';
  g.fillStyle = 'rgba(148, 163, 184, 0.8)';
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  g.shadowColor = 'rgba(0, 0, 0, 0.5)';
  g.shadowBlur = 3;
  
  // RA labels at dec=0 and dec=±45 for better distribution
  [0, 45, -45].forEach(dLabel => {
    for (let ra = 0; ra < 360; ra += 60) {
      const p = projectMollweide(ra, dLabel);
      const hours = Math.floor(ra / 15) + 'h';
      g.fillText(hours, p.x, p.y + (dLabel === 0 ? 12 : (dLabel > 0 ? -12 : 12)));
    }
  });

  // Dec labels along specific meridians (60°, 180°, 300°)
  g.textAlign = 'left';
  [60, 180, 300].forEach(raLabel => {
    for (let dec = -60; dec <= 60; dec += 30) {
      if (dec === 0) continue;
      const p = projectMollweide(raLabel, dec);
      g.fillText((dec > 0 ? '+' : '') + dec + '°', p.x + 5, p.y);
    }
  });
  g.restore();
  
  g.restore();
}

function drawPosterior() {
   const { probs, sorted, cols, rows, res } = posteriorMap;
   let sum = 0;
   let thresh = 0;
   for(let p of sorted) {
      sum += p;
      if (sum >= credibleLevel) { thresh = p; break; }
   }
   
   ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
   for(let r=0; r<rows; r++) {
      for(let c=0; c<cols; c++) {
         if (probs[r*cols+c] >= thresh && probs[r*cols+c] > 0) {
             ctx.fillRect(c*res, r*res, res, res);
         }
      }
   }
}

function drawLens(mx, my) {
    const r = 60;
    const zoom = 2.5;
    
    ctx.save();
    ctx.beginPath();
    ctx.arc(mx, my, r, 0, 2*PI);
    ctx.clip();
    
    ctx.fillStyle = '#020617';
    ctx.fillRect(mx-r, my-r, r*2, r*2);
    
    const visible = getVisiblePoints();
    visible.forEach(d => {
        const dx = d.px - mx;
        const dy = d.py - my;
        const distFromCenter = Math.sqrt(dx*dx + dy*dy);
        if (distFromCenter > r / zoom) return; 
        
        let tx = mx + dx * zoom;
        let ty = my + dy * zoom;
        
        if (d.type === 'Pulsar') {
           ctx.fillStyle = '#eab308';
           drawStar(ctx, tx, ty, 5, 8, 4);
        } else {
           ctx.beginPath();
           if (d.id === clickedId) {
               ctx.fillStyle = '#f472b6'; 
               ctx.arc(tx, ty, 5, 0, 2*PI);
           } else {
               ctx.fillStyle = selectedIds.has(d.id) ? '#22d3ee' : '#94a3b8';
               ctx.arc(tx, ty, 3, 0, 2*PI);
           }
           ctx.fill();
        }
    });
    
    ctx.restore();
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(mx, my, r, 0, 2*PI);
    ctx.stroke();
}

function drawStar(ctx, cx, cy, spikes, outerRadius, innerRadius) {
    var rot = PI / 2 * 3;
    var x = cx;
    var y = cy;
    var step = PI / spikes;

    ctx.beginPath();
    ctx.moveTo(cx, cy - outerRadius);
    for (let i = 0; i < spikes; i++) {
        x = cx + Math.cos(rot) * outerRadius;
        y = cy + Math.sin(rot) * outerRadius;
        ctx.lineTo(x, y);
        rot += step;

        x = cx + Math.cos(rot) * innerRadius;
        y = cy + Math.sin(rot) * innerRadius;
        ctx.lineTo(x, y);
        rot += step;
    }
    ctx.lineTo(cx, cy - outerRadius);
    ctx.closePath();
    ctx.fill();
}

function setMode(m) {
  mode = m;
  document.querySelectorAll('.btn-group button').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-'+(m==='posterior' ? 'posterior' : (m==='magnify' ? 'magnify' : (m==='polygon' ? 'poly' : 'lasso')))).classList.add('active');
  lassoPoints = [];
  selectedIds.clear();
  inspector.style.display = 'none';
  if (m === 'posterior') {
      posteriorControl.style.display = 'block';
      updateSelectionPosterior();
  } else {
      posteriorControl.style.display = 'none';
  }
  draw();
  drawHistograms();
  updateStats();
}

function handleStart(e) {
   const rect = canvas.getBoundingClientRect();
   const x = e.clientX - rect.left;
   const y = e.clientY - rect.top;
   mousePos = {x, y};
   
   if (mode === 'magnify') {
       const r = 60;
       const zoom = 2.5;
       let minD = 1000;
       let closest = null;
       getVisiblePoints().forEach(d => {
           const dx = d.px - x;
           const dy = d.py - y;
           const distFromCenter = Math.sqrt(dx*dx + dy*dy);
           if (distFromCenter > r / zoom) return; 
           const tx = x + dx * zoom;
           const ty = y + dy * zoom;
           const screenDist = (tx - x)**2 + (ty - y)**2;
           if (screenDist < 400 && screenDist < minD) { minD = screenDist; closest = d; }
       });
       if (closest) {
           clickedId = closest.id;
           showInspector([closest]);
       } else {
           clickedId = null;
       }
       return;
   }
   if (mode === 'posterior') return;
   if (mode === 'polygon') {
       if (!isDrawing) {
           isDrawing = true;
           lassoPoints = [{x, y}];
           selectedIds.clear();
       } else {
           lassoPoints.push({x, y});
       }
       draw();
       return;
   }
   isDrawing = true;
   lassoPoints = [{x, y}];
   selectedIds.clear();
}

function handleMove(e) {
   const rect = canvas.getBoundingClientRect();
   const x = e.clientX - rect.left;
   const y = e.clientY - rect.top;
   mousePos = {x, y};
   
   // Hover detection for tooltip (only if enabled)
   if (!isDrawing && tooltipsEnabled) {
     const nearbyPoints = queryGrid(x, y, 15);
     let closest = null;
     let closestDist = Infinity;
     
     nearbyPoints.forEach(d => {
       const dist = Math.sqrt((d.px - x) ** 2 + (d.py - y) ** 2);
       if (dist < closestDist && dist < 15) {
         closestDist = dist;
         closest = d;
       }
     });
     
     if (closest !== hoveredPoint) {
       hoveredPoint = closest;
       updateTooltip(closest, e.clientX, e.clientY);
     } else if (closest) {
       // Update position even if same point
       positionTooltip(e.clientX, e.clientY);
     }
   } else if (!isDrawing && !tooltipsEnabled && hoveredPoint) {
     hoveredPoint = null;
     tooltip.classList.remove('visible');
   }
   
   if (mode === 'magnify') {
       draw(); 
       return;
   }
   if (isDrawing && mode === 'lasso') {
       lassoPoints.push({x, y});
       draw();
   } else if (isDrawing && mode === 'polygon') {
       draw(); 
   }
}

function updateTooltip(point, clientX, clientY) {
  if (!point) {
    tooltip.classList.remove('visible');
    return;
  }
  
  document.getElementById('tooltip-id').textContent = point.id;
  document.getElementById('tooltip-ra').textContent = point.ra.toFixed(2) + '°';
  document.getElementById('tooltip-dec').textContent = point.dec.toFixed(2) + '°';
  
  const distRow = document.getElementById('tooltip-dist-row');
  const massRow = document.getElementById('tooltip-mass-row');
  
  if (point.type === 'Pulsar') {
    distRow.style.display = 'none';
    massRow.querySelector('#tooltip-mass').textContent = point.p0.toFixed(2) + ' ms';
    massRow.querySelector('.tooltip-label').textContent = 'Period';
    massRow.style.display = 'flex';
  } else {
    distRow.style.display = 'flex';
    massRow.style.display = 'flex';
    massRow.querySelector('.tooltip-label').textContent = 'Mass';
    document.getElementById('tooltip-dist').textContent = point.dist.toFixed(1) + ' Mpc';
    document.getElementById('tooltip-mass').textContent = point.mass.toFixed(2) + ' M☉';
  }
  
  const typeEl = document.getElementById('tooltip-type');
  typeEl.textContent = point.type;
  typeEl.className = 'tooltip-type ' + point.type.toLowerCase();
  
  positionTooltip(clientX, clientY);
  tooltip.classList.add('visible');
}

function positionTooltip(clientX, clientY) {
  const container = document.getElementById('map-container');
  const containerRect = container.getBoundingClientRect();
  
  let left = clientX - containerRect.left + 15;
  let top = clientY - containerRect.top - 10;
  
  // Keep tooltip within container bounds
  if (left + 200 > containerRect.width) {
    left = clientX - containerRect.left - 215;
  }
  if (top + 150 > containerRect.height) {
    top = containerRect.height - 160;
  }
  if (top < 10) top = 10;
  
  tooltip.style.left = left + 'px';
  tooltip.style.top = top + 'px';
}

function handleEnd(e) {
    if (!isDrawing) return;
    if (mode === 'lasso') {
        isDrawing = false;
        closeSelection();
    }
    if (mode === 'polygon') {
       const dx = mousePos.x - lassoPoints[0].x;
       const dy = mousePos.y - lassoPoints[0].y;
       if (lassoPoints.length > 2 && Math.sqrt(dx*dx + dy*dy) < 10) {
           isDrawing = false;
           closeSelection();
       }
    }
}

canvas.addEventListener('dblclick', () => {
    if (mode === 'polygon' && isDrawing) {
        isDrawing = false;
        closeSelection();
    }
});

function closeSelection() {
    if (lassoPoints.length < 5) {
        // Try single point selection
        const p = lassoPoints[0];
        const nearby = queryGrid(p.x, p.y, 15);
        let closest = null;
        let minD = 225; // 15^2
        nearby.forEach(d => {
            const distSq = (d.px - p.x)**2 + (d.py - p.y)**2;
            if (distSq < minD) { minD = distSq; closest = d; }
        });
        if (closest) {
            clickedId = closest.id;
            selectedIds.clear();
            selectedIds.add(closest.id);
            showInspector([closest]);
        } else {
            selectedIds.clear();
            clickedId = null;
            inspector.style.display = 'none';
        }
        lassoPoints = [];
        draw();
        drawHistograms();
        updateStats();
        return;
    }

    const vs = lassoPoints.map(p => [p.x, p.y]);
    projectedData.forEach(d => {
        if (!showPulsars && d.type === 'Pulsar') return;
        const x = d.px, y = d.py;
        let inside = false;
        for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
            const xi = vs[i][0], yi = vs[i][1];
            const xj = vs[j][0], yj = vs[j][1];
            const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
            if (intersect) inside = !inside;
        }
        if (inside) selectedIds.add(d.id);
    });
    
    // Auto-inspect if only one point in selection
    if (selectedIds.size === 1) {
      const id = Array.from(selectedIds)[0];
      const point = projectedData.find(d => d.id === id);
      if (point) {
        clickedId = id;
        showInspector([point]);
      }
    } else {
      clickedId = null;
      if (selectedIds.size > 0) {
        const selPoints = projectedData.filter(d => selectedIds.has(d.id));
        showInspector(selPoints.slice(0, 50));
      } else {
        inspector.style.display = 'none';
      }
    }

    draw();
    drawHistograms();
    updateStats();
}

function updateSelectionPosterior() {
    if (!posteriorMap) return;
    const { probs, sorted, cols, rows, res } = posteriorMap;
    let sum = 0; 
    let thresh = 0;
    for(let p of sorted) { sum+=p; if(sum>=credibleLevel) { thresh=p; break; } }
    selectedIds.clear();
    getVisiblePoints().forEach(d => {
        const c = Math.floor(d.px / res);
        const r = Math.floor(d.py / res);
        if (c >=0 && c < cols && r>=0 && r<rows) {
            if (probs[r*cols + c] >= thresh) selectedIds.add(d.id);
        }
    });
    updateStats();
    drawHistograms(); 
}

function getVisiblePoints() {
    return showPulsars ? projectedData : projectedData.filter(d => d.type !== 'Pulsar');
}

function updateStats() {
    document.getElementById('count-sel').innerText = selectedIds.size;
}

function showInspector(items) {
    inspector.style.display = 'block';
    const tbody = document.getElementById('inspector-body');
    tbody.innerHTML = '';
    items.forEach(d => {
        const tr = document.createElement('tr');
        if (d.type === 'Pulsar') {
           tr.innerHTML = `<td>${d.id}</td><td style="color:#eab308">P0: ${d.p0.toFixed(2)}ms</td><td>${Math.round(d.ra)}/${Math.round(d.dec)}</td>`;
        } else {
           tr.innerHTML = `<td>${d.id}</td><td>D:${d.dist.toFixed(1)} | log₁₀M:${d.mass.toFixed(1)}</td><td>${Math.round(d.ra)}/${Math.round(d.dec)}</td>`;
        }
        tbody.appendChild(tr);
    });
}

function drawHistograms() {
    distCtx.fillStyle = '#0f172a'; distCtx.fillRect(0,0,270,85);
    massCtx.fillStyle = '#0f172a'; massCtx.fillRect(0,0,270,85);
    const subset = getVisiblePoints().filter(d => selectedIds.has(d.id) && d.type !== 'Pulsar');
    const all = getVisiblePoints().filter(d => d.type !== 'Pulsar');
    if (all.length === 0) return;
    drawBarChart(distCtx, all, subset, 'dist', 0, 500, '#d946ef');
    drawBarChart(massCtx, all, subset, 'mass', 6, 10.5, '#22d3ee');
}

function drawBarChart(ctx, allData, selData, field, min, max, color) {
    const bins = 30;
    const step = (max-min)/bins;
    const allCounts = new Array(bins).fill(0);
    const selCounts = new Array(bins).fill(0);
    allData.forEach(d => {
       let b = Math.floor((d[field]-min)/step);
       if(b>=0 && b<bins) allCounts[b]++;
    });
    if (selData) {
        selData.forEach(d => {
           let b = Math.floor((d[field]-min)/step);
           if(b>=0 && b<bins) selCounts[b]++;
        });
    }
    const allTotal = allData.length || 1;
    const selTotal = selData ? selData.length || 1 : 1;
    const allDensity = allCounts.map(c => c / (allTotal * step));
    const selDensity = selCounts.map(c => c / (selTotal * step));
    const maxH = Math.max(...allDensity, 0.001);
    const w = 270 / bins;
    const chartH = 60; 
    ctx.fillStyle = '#334155';
    allDensity.forEach((d, i) => {
        const h = (d/maxH) * chartH;
        ctx.fillRect(i*w, chartH-h, w-1, h);
    });
    if (selData && selData.length > 0) {
        ctx.fillStyle = color;
        selDensity.forEach((d, i) => {
            const h = (d/maxH) * chartH;
            ctx.fillRect(i*w, chartH-h, w-1, h);
        });
    }
    ctx.strokeStyle = '#334155';
    ctx.fillStyle = '#94a3b8';
    ctx.font = '9px monospace';
    ctx.textAlign = 'center';
    ctx.lineWidth = 1;
    const numTicks = 5;
    for (let i = 0; i < numTicks; i++) {
        const val = min + (i * (max - min) / (numTicks - 1));
        const x = (i * 270 / (numTicks - 1));
        ctx.beginPath();
        ctx.moveTo(x, chartH);
        ctx.lineTo(x, chartH + 5);
        ctx.stroke();
        if (i === 0) ctx.textAlign = 'left';
        else if (i === numTicks - 1) ctx.textAlign = 'right';
        else ctx.textAlign = 'center';
        ctx.fillText(val.toFixed(field === 'mass' ? 1 : 0), x, chartH + 15);
    }
}

init();
</script>
</body>
</html>
"""

html_code = html_code_template.replace("@@@PULSARS_JSON@@@", json.dumps(PULSARS))

# --- RENDER COMPONENT ---
components.html(html_code, height=850, scrolling=False)