// --- DATA ---
let initialPulsars = window.galaxyAppData?.pulsars || [];
let galaxyData = [];
let rawData = [];
let posteriorSamples = [];
let projectedData = [];
let pulsarPoints = [];

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
    const raVal = (parseFloat(hh) + parseFloat(mmRa) / 60 + raSeconds / 3600) * 15.0;
    const decArcsec = parseFloat(dsDec) + parseFloat(tsDec) / 10.0;
    const sign = signStr === '-' ? -1 : 1;
    return [raVal, sign * (parseFloat(dd) + parseFloat(dm) / 60 + decArcsec / 3600)];
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
    if (!file) return;

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

    const lines = text.split(/\r?\n/);
    const totalLines = lines.length;
    const newData = [];

    // Process in chunks to allow UI updates
    const chunkSize = 5000;
    for (let i = 0; i < totalLines; i += chunkSize) {
        const chunk = lines.slice(i, Math.min(i + chunkSize, totalLines));
        chunk.forEach(line => {
            line = line.trim();
            if (!line || !/^\d/.test(line)) return;
            const parts = line.split(/\s+/);
            if (parts.length < 3) return;
            const coords = parseCoordinate(parts[0]);
            if (coords) newData.push({ id: parts[0], ra: coords[0], dec: coords[1], dist: parseFloat(parts[1]), mass: parseFloat(parts[2]), type: "Galaxy" });
        });

        // Update progress (20% to 80% for parsing)
        const progress = 20 + (Math.min(i + chunkSize, totalLines) / totalLines) * 60;
        progressBar.style.width = progress + '%';
        await new Promise(r => setTimeout(r, 0));
    }

    if (newData.length > 0) {
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
    if (!file) return;

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

    const lines = text.split(/\r?\n/);
    const totalLines = lines.length;
    const newSamples = [];

    const chunkSize = 5000;
    for (let i = 0; i < totalLines; i += chunkSize) {
        const chunk = lines.slice(i, Math.min(i + chunkSize, totalLines));
        chunk.forEach(line => {
            line = line.trim();
            if (!line || !(/^[0-9-]/.test(line))) return;
            const parts = line.split(/[ ,\s]+/);
            if (parts.length >= 2) {
                const ra = parseFloat(parts[0]);
                const dec = parseFloat(parts[1]);
                if (!isNaN(ra) && !isNaN(dec)) newSamples.push({ ra, dec });
            }
        });

        const progress = 20 + (Math.min(i + chunkSize, totalLines) / totalLines) * 50;
        progressBar.style.width = progress + '%';
        await new Promise(r => setTimeout(r, 0));
    }

    if (newSamples.length > 0) {
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
    rawData = [...galaxyData, ...initialPulsars.map(p => ({ ...p, dist: 0, mass: 0, type: "Pulsar" }))];
    projectedData = rawData.map(d => {
        const coords = getDisplayCoords(d);
        const p = projectMollweide(coords.coord1, coords.coord2);
        return { ...d, px: p.x, py: p.y, displayCoord1: coords.coord1, displayCoord2: coords.coord2 };
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

    const containerWidth = container.clientWidth - 40;
    const containerHeight = container.clientHeight - 40;

    const aspectRatio = 2;
    let newWidth = containerWidth;
    let newHeight = containerWidth / aspectRatio;

    if (newHeight > containerHeight) {
        newHeight = containerHeight;
        newWidth = containerHeight * aspectRatio;
    }

    WIDTH = Math.max(400, Math.floor(newWidth));
    HEIGHT = Math.max(200, Math.floor(newHeight));
    SCALE = (HEIGHT - PADDING * 2) / (2 * Math.sqrt(2));

    if (ctx) {
        ctx = setupHighDPI(canvas, WIDTH, HEIGHT);

        const dpr = window.devicePixelRatio || 1;
        gridCanvas.width = WIDTH * dpr;
        gridCanvas.height = HEIGHT * dpr;
        gridCtx.scale(dpr, dpr);
        drawCoordinateGrid(gridCtx);

        canvas.style.position = 'absolute';
        canvas.style.left = '50%';
        canvas.style.top = '50%';
        canvas.style.transform = 'translate(-50%, -50%)';

        projectedData = rawData.map(d => {
            const coords = getDisplayCoords(d);
            const p = projectMollweide(coords.coord1, coords.coord2);
            return { ...d, px: p.x, py: p.y, displayCoord1: coords.coord1, displayCoord2: coords.coord2 };
        });
        pulsarPoints = projectedData.filter(d => d.type === 'Pulsar');
        buildSpatialGrid();
        draw();
    }
}

// --- STATE ---
let mode = 'lasso';
let selectedIds = new Set();
let lassoPoints = [];
let isDrawing = false;
let showPulsars = true;
let mousePos = { x: 0, y: 0 };
let spatialGrid = {};
let posteriorMap = null;
let credibleLevel = 0.95;
let animationTime = 0;
let periodScale = 400;
let clickedId = null;
let hoveredPoint = null;
let tooltipsEnabled = true;
let showGrid = true;
let coordSystem = 'equatorial'; // 'equatorial' or 'galactic'

// Filter state
let filterDistMin = 0;
let filterDistMax = 500;
let filterMassMin = 6.0;
let filterMassMax = 10.5;

let centerLon = 180;

// --- COORDINATE CONVERSION ---
function equatorialToGalactic(ra, dec) {
    const d2r = Math.PI / 180;
    const r2d = 180 / Math.PI;

    const ra_ngp = 192.85948 * d2r;
    const dec_ngp = 27.12825 * d2r;
    const l_ncp = 122.93192 * d2r;

    const ra_rad = ra * d2r;
    const dec_rad = dec * d2r;

    const sin_b = Math.sin(dec_ngp) * Math.sin(dec_rad) +
        Math.cos(dec_ngp) * Math.cos(dec_rad) * Math.cos(ra_rad - ra_ngp);
    const b = Math.asin(sin_b);

    const y = Math.cos(dec_rad) * Math.sin(ra_rad - ra_ngp);
    const x = Math.cos(dec_ngp) * Math.sin(dec_rad) -
        Math.sin(dec_ngp) * Math.cos(dec_rad) * Math.cos(ra_rad - ra_ngp);
    let l = l_ncp - Math.atan2(y, x);

    l = l * r2d;
    while (l < 0) l += 360;
    while (l >= 360) l -= 360;

    return { l: l, b: b * r2d };
}

function getDisplayCoords(d) {
    if (coordSystem === 'galactic') {
        const gal = equatorialToGalactic(d.ra, d.dec);
        return { coord1: gal.l, coord2: gal.b };
    }
    return { coord1: d.ra, coord2: d.dec };
}

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

    // Always use mock data by default for faster startup
    galaxyData = generateMockData();
    const statusText = document.getElementById('status-galaxies');
    if (statusText) statusText.innerText = 'Using synthetic data';

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
        document.getElementById('cred-val').innerText = Math.round(credibleLevel * 100) + '%';
        if (mode === 'posterior') updateSelectionPosterior();
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

    document.getElementById('coord-system').onchange = (e) => {
        coordSystem = e.target.value;

        // Center on galactic center (l=0) for galactic coords, or RA=180 for equatorial
        centerLon = coordSystem === 'galactic' ? 0 : 180;

        projectedData = rawData.map(d => {
            const coords = getDisplayCoords(d);
            const p = projectMollweide(coords.coord1, coords.coord2);
            return { ...d, px: p.x, py: p.y, displayCoord1: coords.coord1, displayCoord2: coords.coord2 };
        });
        pulsarPoints = projectedData.filter(d => d.type === 'Pulsar');
        buildSpatialGrid();

        if (posteriorSamples.length > 0) {
            computePosteriorMap();
        }

        const dpr = window.devicePixelRatio || 1;
        gridCtx.setTransform(1, 0, 0, 1, 0, 0);
        gridCtx.scale(dpr, dpr);
        drawCoordinateGrid(gridCtx);

        draw();
    };

    draw();
    drawHistograms();

    window.addEventListener('resize', () => {
        updateCanvasSize();
    });

    updateCanvasSize();

    document.getElementById('btn-search').onclick = searchGalaxy;
    document.getElementById('search-input').onkeypress = (e) => {
        if (e.key === 'Enter') searchGalaxy();
    };

    document.getElementById('btn-export').onclick = exportSelection;

    const distMinSlider = document.getElementById('filter-dist-min');
    const distMaxSlider = document.getElementById('filter-dist-max');
    const massMinSlider = document.getElementById('filter-mass-min');
    const massMaxSlider = document.getElementById('filter-mass-max');

    distMinSlider.oninput = (e) => {
        filterDistMin = parseFloat(e.target.value);
        if (filterDistMin > filterDistMax) {
            filterDistMax = filterDistMin;
            distMaxSlider.value = filterDistMax;
        }
        updateFilterLabels();
        draw();
        drawHistograms();
    };

    distMaxSlider.oninput = (e) => {
        filterDistMax = parseFloat(e.target.value);
        if (filterDistMax < filterDistMin) {
            filterDistMin = filterDistMax;
            distMinSlider.value = filterDistMin;
        }
        updateFilterLabels();
        draw();
        drawHistograms();
    };

    massMinSlider.oninput = (e) => {
        filterMassMin = parseFloat(e.target.value);
        if (filterMassMin > filterMassMax) {
            filterMassMax = filterMassMin;
            massMinSlider.value = filterMassMax;
        }
        updateFilterLabels();
        draw();
        drawHistograms();
    };

    massMaxSlider.oninput = (e) => {
        filterMassMax = parseFloat(e.target.value);
        if (filterMassMax < filterMassMin) {
            filterMassMin = filterMassMax;
            massMinSlider.value = filterMassMin;
        }
        updateFilterLabels();
        draw();
        drawHistograms();
    };

    function animate(timestamp) {
        animationTime = timestamp;
        draw();
        requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
}

// --- MATH ---
function projectMollweide(ra, dec) {
    const defaultCenter = coordSystem === 'galactic' ? 0 : centerLon;

    let lambda = (ra - centerLon);
    while (lambda > 180) lambda -= 360;
    while (lambda <= -180) lambda += 360;
    lambda = lambda * (PI / 180);

    lambda = -lambda;

    let phi = dec * (PI / 180);

    let theta = phi;
    for (let i = 0; i < 10; i++) {
        let f = 2 * theta + Math.sin(2 * theta) - PI * Math.sin(phi);
        let fprime = 2 + 2 * Math.cos(2 * theta) + 1e-12;
        theta -= f / fprime;
    }

    let x = (2 * Math.sqrt(2) / PI) * lambda * Math.cos(theta);
    let y = Math.sqrt(2) * Math.sin(theta);

    return {
        x: (x * SCALE) + (WIDTH / 2),
        y: -(y * SCALE) + (HEIGHT / 2)
    };
}

function buildSpatialGrid() {
    const cellSize = 20;
    const cols = Math.ceil(WIDTH / cellSize);
    const rows = Math.ceil(HEIGHT / cellSize);
    spatialGrid = { cellSize, cols, rows, bins: new Array(cols * rows).fill(null).map(() => []) };

    projectedData.forEach(d => {
        let c = Math.floor(d.px / cellSize);
        let r = Math.floor(d.py / cellSize);
        if (c >= 0 && c < cols && r >= 0 && r < rows) {
            spatialGrid.bins[r * cols + c].push(d);
        }
    });
}

function queryGrid(x, y, radius) {
    const { cellSize, cols, rows, bins } = spatialGrid;
    const results = [];

    const cellRadius = Math.ceil(radius / cellSize);
    const centerCol = Math.floor(x / cellSize);
    const centerRow = Math.floor(y / cellSize);

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
    const cols = Math.ceil(WIDTH / res);
    const rows = Math.ceil(HEIGHT / res);
    const bins = new Float32Array(cols * rows).fill(0);

    posteriorSamples.forEach(s => {
        let coord1, coord2;
        if (coordSystem === 'galactic') {
            const gal = equatorialToGalactic(s.ra, s.dec);
            coord1 = gal.l;
            coord2 = gal.b;
        } else {
            coord1 = s.ra;
            coord2 = s.dec;
        }
        const p = projectMollweide(coord1, coord2);
        const c = Math.floor(p.x / res);
        const r = Math.floor(p.y / res);
        if (c >= 0 && c < cols && r >= 0 && r < rows) bins[r * cols + c]++;
    });

    const total = posteriorSamples.length;
    const probs = Array.from(bins).map(v => v / total);
    const sorted = [...probs].sort((a, b) => b - a);
    posteriorMap = { probs, sorted, cols, rows, res };
}

// --- DRAWING ---
function draw() {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);

    if (mode === 'posterior' && posteriorMap) {
        drawPosterior();
    }

    if (showGrid) {
        ctx.drawImage(gridCanvas, 0, 0, WIDTH, HEIGHT);
    }

    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 2;
    ctx.beginPath();
    const rx = (HEIGHT / 2 - PADDING) * 2;
    const ry = HEIGHT / 2 - PADDING;
    ctx.ellipse(WIDTH / 2, HEIGHT / 2, rx, ry, 0, 0, 2 * PI);
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

    ctx.save();
    ctx.fillStyle = '#94a3b8';
    ctx.globalAlpha = 0.35;
    ctx.beginPath();
    unselectedGalaxies.forEach(d => {
        ctx.moveTo(d.px, d.py);
        ctx.arc(d.px, d.py, 2.0, 0, 2 * PI);
    });
    ctx.fill();

    ctx.globalAlpha = 0.8;
    ctx.beginPath();
    unselectedGalaxies.forEach(d => {
        ctx.moveTo(d.px, d.py);
        ctx.arc(d.px, d.py, 0.8, 0, 2 * PI);
    });
    ctx.fill();
    ctx.restore();

    if (selectedGalaxies.length > 0) {
        ctx.save();
        ctx.shadowColor = 'rgba(34, 211, 238, 0.6)';
        ctx.shadowBlur = 12;
        ctx.fillStyle = 'rgba(34, 211, 238, 0.3)';
        ctx.beginPath();
        selectedGalaxies.forEach(d => {
            ctx.moveTo(d.px, d.py);
            ctx.arc(d.px, d.py, 5, 0, 2 * PI);
        });
        ctx.fill();

        ctx.shadowColor = 'rgba(34, 211, 238, 0.9)';
        ctx.shadowBlur = 6;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        selectedGalaxies.forEach(d => {
            ctx.moveTo(d.px, d.py);
            ctx.arc(d.px, d.py, 2.0, 0, 2 * PI);
        });
        ctx.fill();

        ctx.restore();
    }

    if (hoveredPoint && hoveredPoint.type !== 'Pulsar') {
        ctx.save();
        ctx.shadowColor = 'rgba(244, 114, 182, 0.9)';
        ctx.shadowBlur = 15;
        ctx.fillStyle = '#f472b6';
        ctx.beginPath();
        ctx.arc(hoveredPoint.px, hoveredPoint.py, 4.5, 0, 2 * PI);
        ctx.fill();

        const pulse = 0.5 + 0.5 * Math.sin(animationTime * 0.005);
        ctx.strokeStyle = 'rgba(244, 114, 182, ' + (0.4 + pulse * 0.4) + ')';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(hoveredPoint.px, hoveredPoint.py, 8 + pulse * 4, 0, 2 * PI);
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
            ctx.arc(d.px, d.py, 6 + pulse * 2, 0, 2 * PI);
            ctx.stroke();

            ctx.globalAlpha = 0.4;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.arc(d.px, d.py, 12 + pulse * 4, 0, 2 * PI);
            ctx.stroke();
            ctx.restore();
        }
    }

    if (showPulsars) {
        pulsarPoints.forEach(p => {
            const period = p.p0 * periodScale;
            const phase = (animationTime % period) / period;
            const brightness = 0.4 + 0.6 * (0.5 + 0.5 * Math.sin(phase * 2 * PI));

            ctx.save();
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

            drawStar(ctx, p.px, p.py, 5, sz, sz / 2);

            ctx.shadowColor = (p.id === clickedId || p === hoveredPoint) ? 'white' : 'rgba(255, 255, 255, ' + (brightness * 0.8) + ')';
            ctx.shadowBlur = 4 * brightness;
            drawStar(ctx, p.px, p.py, 5, sz, sz / 2);

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
        for (let i = 1; i < lassoPoints.length; i++) ctx.lineTo(lassoPoints[i].x, lassoPoints[i].y);
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

function drawCoordinateGrid(g) {
    g.clearRect(0, 0, WIDTH, HEIGHT);
    g.save();
    g.strokeStyle = 'rgba(71, 85, 105, 0.25)';
    g.lineWidth = 0.5;
    g.setLineDash([2, 4]);

    const centerLon = coordSystem === 'galactic' ? 0 : 180;

    for (let lon = centerLon - 180; lon <= centerLon + 180; lon += 30) {
        g.beginPath();
        let started = false;
        for (let lat = -90; lat <= 90; lat += 2) {
            const p = projectMollweide(lon, lat);
            if (!started) {
                g.moveTo(p.x, p.y);
                started = true;
            } else {
                g.lineTo(p.x, p.y);
            }
        }
        g.stroke();
    }

    for (let lat = -60; lat <= 60; lat += 30) {
        if (lat === 0) continue;
        g.beginPath();
        let started = false;
        for (let lon = centerLon - 180; lon <= centerLon + 180; lon += 2) {
            const p = projectMollweide(lon, lat);
            if (!started) {
                g.moveTo(p.x, p.y);
                started = true;
            } else {
                g.lineTo(p.x, p.y);
            }
        }
        g.stroke();
    }

    g.strokeStyle = 'rgba(71, 85, 105, 0.4)';
    g.setLineDash([]);
    g.beginPath();
    for (let lon = centerLon - 180; lon <= centerLon + 180; lon += 2) {
        const p = projectMollweide(lon, 0);
        if (lon === centerLon - 180) g.moveTo(p.x, p.y); else g.lineTo(p.x, p.y);
    }
    g.stroke();

    g.save();
    g.font = '500 10px Inter, sans-serif';
    g.fillStyle = 'rgba(148, 163, 184, 0.8)';
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    g.shadowColor = 'rgba(0, 0, 0, 0.5)';
    g.shadowBlur = 3;

    if (coordSystem === 'equatorial') {
        [0, 45, -45].forEach(latLabel => {
            for (let lon = centerLon - 180; lon < centerLon + 180; lon += 60) {
                const p = projectMollweide(lon, latLabel);
                let displayLon = (lon % 360 + 360) % 360;
                const hours = Math.floor(displayLon / 15) + 'h';
                g.fillText(hours, p.x, p.y + (latLabel === 0 ? 12 : (latLabel > 0 ? -12 : 12)));
            }
        });

        g.textAlign = 'left';
        [centerLon - 120, centerLon, centerLon + 120].forEach(lonLabel => {
            for (let lat = -60; lat <= 60; lat += 30) {
                if (lat === 0) continue;
                const p = projectMollweide(lonLabel, lat);
                g.fillText((lat > 0 ? '+' : '') + lat + '°', p.x + 5, p.y);
            }
        });
    } else {
        [0, 45, -45].forEach(latLabel => {
            for (let lon = centerLon - 180; lon < centerLon + 180; lon += 60) {
                const p = projectMollweide(lon, latLabel);
                let displayLon = (lon % 360 + 360) % 360;
                g.fillText(displayLon + '°', p.x, p.y + (latLabel === 0 ? 12 : (latLabel > 0 ? -12 : 12)));
            }
        });

        g.textAlign = 'left';
        [centerLon - 120, centerLon, centerLon + 120].forEach(lonLabel => {
            for (let lat = -60; lat <= 60; lat += 30) {
                if (lat === 0) continue;
                const p = projectMollweide(lonLabel, lat);
                g.fillText((lat > 0 ? '+' : '') + lat + '°', p.x + 5, p.y);
            }
        });
    }
    g.restore();
    g.restore();
}

function drawPosterior() {
    const { probs, sorted, cols, rows, res } = posteriorMap;
    let sum = 0;
    let thresh = 0;
    for (let p of sorted) {
        sum += p;
        if (sum >= credibleLevel) { thresh = p; break; }
    }

    ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (probs[r * cols + c] >= thresh && probs[r * cols + c] > 0) {
                ctx.fillRect(c * res, r * res, res, res);
            }
        }
    }
}

function drawLens(mx, my) {
    const r = 60;
    const zoom = 2.5;

    ctx.save();
    ctx.beginPath();
    ctx.arc(mx, my, r, 0, 2 * PI);
    ctx.clip();

    ctx.fillStyle = '#020617';
    ctx.fillRect(mx - r, my - r, r * 2, r * 2);

    const visible = getVisiblePoints();
    visible.forEach(d => {
        const dx = d.px - mx;
        const dy = d.py - my;
        const distFromCenter = Math.sqrt(dx * dx + dy * dy);
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
                ctx.arc(tx, ty, 5, 0, 2 * PI);
            } else {
                ctx.fillStyle = selectedIds.has(d.id) ? '#22d3ee' : '#94a3b8';
                ctx.arc(tx, ty, 3, 0, 2 * PI);
            }
            ctx.fill();
        }
    });

    ctx.restore();
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(mx, my, r, 0, 2 * PI);
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
    document.getElementById('btn-' + (m === 'posterior' ? 'posterior' : (m === 'magnify' ? 'magnify' : (m === 'polygon' ? 'poly' : 'lasso')))).classList.add('active');
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
    mousePos = { x, y };

    if (mode === 'magnify') {
        const r = 60;
        const zoom = 2.5;
        let minD = 1000;
        let closest = null;
        getVisiblePoints().forEach(d => {
            const dx = d.px - x;
            const dy = d.py - y;
            const distFromCenter = Math.sqrt(dx * dx + dy * dy);
            if (distFromCenter > r / zoom) return;
            const tx = x + dx * zoom;
            const ty = y + dy * zoom;
            const screenDist = (tx - x) ** 2 + (ty - y) ** 2;
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
            lassoPoints = [{ x, y }];
            selectedIds.clear();
        } else {
            lassoPoints.push({ x, y });
        }
        draw();
        return;
    }
    isDrawing = true;
    lassoPoints = [{ x, y }];
    selectedIds.clear();
}

function handleMove(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    mousePos = { x, y };

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
        lassoPoints.push({ x, y });
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

    const coord1Label = document.getElementById('tooltip-coord1-label');
    const coord2Label = document.getElementById('tooltip-coord2-label');
    const coord1Val = document.getElementById('tooltip-coord1');
    const coord2Val = document.getElementById('tooltip-coord2');

    if (coordSystem === 'galactic') {
        const gal = equatorialToGalactic(point.ra, point.dec);
        coord1Label.textContent = 'l';
        coord2Label.textContent = 'b';
        coord1Val.textContent = gal.l.toFixed(2) + '°';
        coord2Val.textContent = gal.b.toFixed(2) + '°';
    } else {
        coord1Label.textContent = 'RA';
        coord2Label.textContent = 'Dec';
        coord1Val.textContent = point.ra.toFixed(2) + '°';
        coord2Val.textContent = point.dec.toFixed(2) + '°';
    }

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
        if (lassoPoints.length > 2 && Math.sqrt(dx * dx + dy * dy) < 10) {
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
        const p = lassoPoints[0];
        const nearby = queryGrid(p.x, p.y, 15);
        let closest = null;
        let minD = 225;
        nearby.forEach(d => {
            const distSq = (d.px - p.x) ** 2 + (d.py - p.y) ** 2;
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
    for (let p of sorted) { sum += p; if (sum >= credibleLevel) { thresh = p; break; } }
    selectedIds.clear();
    getVisiblePoints().forEach(d => {
        const c = Math.floor(d.px / res);
        const r = Math.floor(d.py / res);
        if (c >= 0 && c < cols && r >= 0 && r < rows) {
            if (probs[r * cols + c] >= thresh) selectedIds.add(d.id);
        }
    });
    updateStats();
    drawHistograms();
}

function getVisiblePoints() {
    let pts = showPulsars ? projectedData : projectedData.filter(d => d.type !== 'Pulsar');
    return pts.filter(d => {
        if (d.type === 'Pulsar') return true;
        return d.dist >= filterDistMin && d.dist <= filterDistMax &&
            d.mass >= filterMassMin && d.mass <= filterMassMax;
    });
}

function searchGalaxy() {
    const query = document.getElementById('search-input').value.trim().toLowerCase();
    if (!query) return;

    const point = projectedData.find(d => d.id.toLowerCase().includes(query));
    if (point) {
        // Update center longitude to the galaxy's RA
        if (coordSystem !== 'galactic') {
            centerLon = point.ra;
            // Re-project everything
            projectedData = rawData.map(d => {
                const coords = getDisplayCoords(d);
                const p = projectMollweide(coords.coord1, coords.coord2);
                return { ...d, px: p.x, py: p.y, displayCoord1: coords.coord1, displayCoord2: coords.coord2 };
            });
            pulsarPoints = projectedData.filter(d => d.type === 'Pulsar');
            buildSpatialGrid();

            // Re-draw coordinate grid
            const dpr = window.devicePixelRatio || 1;
            gridCtx.setTransform(1, 0, 0, 1, 0, 0);
            gridCtx.scale(dpr, dpr);
            drawCoordinateGrid(gridCtx);

            // Find the point again since coordinates changed
            const updatedPoint = projectedData.find(d => d.id === point.id);
            if (updatedPoint) {
                clickedId = updatedPoint.id;
                selectedIds.clear();
                selectedIds.add(updatedPoint.id);
                showInspector([updatedPoint]);
            }
        } else {
            clickedId = point.id;
            selectedIds.clear();
            selectedIds.add(point.id);
            showInspector([point]);
        }

        draw();
        drawHistograms();
        updateStats();

        animationTime = performance.now();

        // Brief flash effect
        const statusText = document.getElementById('status-galaxies');
        if (statusText) {
            const oldText = statusText.innerText;
            statusText.innerText = `Found: ${point.id}`;
            statusText.style.color = '#22d3ee';
            setTimeout(() => {
                statusText.innerText = oldText;
                statusText.style.color = '';
            }, 3000);
        }
    } else {
        const btn = document.getElementById('btn-search');
        btn.innerText = 'Not Found';
        btn.style.color = '#f87171';
        setTimeout(() => {
            btn.innerText = 'Find';
            btn.style.color = '';
        }, 2000);
    }
}

function exportSelection() {
    if (selectedIds.size === 0) {
        alert("Please select some galaxies first using the Lasso or Polygon tool.");
        return;
    }

    const selectedPoints = projectedData.filter(d => selectedIds.has(d.id));
    let csv = "id,ra,dec,dist,mass,type\n";
    selectedPoints.forEach(p => {
        csv += `${p.id},${p.ra},${p.dec},${p.dist},${p.mass},${p.type}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `galaxy_selection_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function updateFilterLabels() {
    document.getElementById('dist-range-val').innerText = `${filterDistMin} - ${filterDistMax}`;
    document.getElementById('mass-range-val').innerText = `${filterMassMin.toFixed(1)} - ${filterMassMax.toFixed(1)}`;
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
        let coordStr;
        if (coordSystem === 'galactic') {
            const gal = equatorialToGalactic(d.ra, d.dec);
            coordStr = `${Math.round(gal.l)}/${Math.round(gal.b)}`;
        } else {
            coordStr = `${Math.round(d.ra)}/${Math.round(d.dec)}`;
        }
        if (d.type === 'Pulsar') {
            tr.innerHTML = `<td>${d.id}</td><td style="color:#eab308">P0: ${d.p0.toFixed(2)}ms</td><td>${coordStr}</td>`;
        } else {
            tr.innerHTML = `<td>${d.id}</td><td>D:${d.dist.toFixed(1)} | log₁₀M:${d.mass.toFixed(1)}</td><td>${coordStr}</td>`;
        }
        tbody.appendChild(tr);
    });
}

function drawHistograms() {
    distCtx.fillStyle = '#0f172a'; distCtx.fillRect(0, 0, 270, 85);
    massCtx.fillStyle = '#0f172a'; massCtx.fillRect(0, 0, 270, 85);
    const subset = getVisiblePoints().filter(d => selectedIds.has(d.id) && d.type !== 'Pulsar');
    const all = getVisiblePoints().filter(d => d.type !== 'Pulsar');
    if (all.length === 0) return;
    drawBarChart(distCtx, all, subset, 'dist', 0, 500, '#d946ef');
    drawBarChart(massCtx, all, subset, 'mass', 6, 10.5, '#22d3ee');
}

function drawBarChart(ctx, allData, selData, field, min, max, color) {
    const bins = 30;
    const step = (max - min) / bins;
    const allCounts = new Array(bins).fill(0);
    const selCounts = new Array(bins).fill(0);
    allData.forEach(d => {
        let b = Math.floor((d[field] - min) / step);
        if (b >= 0 && b < bins) allCounts[b]++;
    });
    if (selData) {
        selData.forEach(d => {
            let b = Math.floor((d[field] - min) / step);
            if (b >= 0 && b < bins) selCounts[b]++;
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
        const h = (d / maxH) * chartH;
        ctx.fillRect(i * w, chartH - h, w - 1, h);
    });
    if (selData && selData.length > 0) {
        ctx.fillStyle = color;
        selDensity.forEach((d, i) => {
            const h = (d / maxH) * chartH;
            ctx.fillRect(i * w, chartH - h, w - 1, h);
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

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', init);
