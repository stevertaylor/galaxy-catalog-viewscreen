/**
 * DuckDB-WASM Web Worker for Galaxy Catalog Viewscreen
 *
 * Runs DuckDB in a Web Worker so queries don't block the UI.
 * Loads the duckdb-wasm library from jsDelivr CDN.
 *
 * Message protocol:
 *   Main → Worker:  { id, type, ...params }
 *   Worker → Main:  { id, type, result } | { id, type, error }
 */

// Import DuckDB-WASM from CDN
importScripts(
    'https://cdn.jsdelivr.net/npm/apache-arrow@17.0.0/Arrow.dom.min.js',
    'https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@1.29.0/dist/duckdb-browser-blocking.cjs'
);

let db = null;
let conn = null;

/**
 * Initialize DuckDB-WASM and register the remote Parquet file.
 */
function initDB(parquetUrl) {
    const logger = new duckdb.ConsoleLogger();
    db = new duckdb.DuckDBClient(logger);

    // Use the blocking (synchronous) API since we're in a Worker
    const bundle = duckdb.getJsDelivrBundles();

    // For the blocking worker, we instantiate directly
    db = new duckdb.DuckDB(logger);
    db.instantiate(bundle.mvp.mainModule);
    conn = db.connect();

    // Create a view over the remote Parquet file
    conn.query(`
        CREATE VIEW catalog AS
        SELECT * FROM read_parquet('${parquetUrl}')
    `);

    return { status: 'ready' };
}

/**
 * Query galaxies with spatial and property filters.
 */
function queryGalaxies(params) {
    const {
        ra_min = 0, ra_max = 360,
        dec_min = -90, dec_max = 90,
        dist_min = 0, dist_max = 99999,
        mass_min = -99, mass_max = 99,
        limit = 50000
    } = params;

    const result = conn.query(`
        SELECT id, ra, dec, dist, mass
        FROM catalog
        WHERE ra BETWEEN ${ra_min} AND ${ra_max}
          AND dec BETWEEN ${dec_min} AND ${dec_max}
          AND dist BETWEEN ${dist_min} AND ${dist_max}
          AND mass BETWEEN ${mass_min} AND ${mass_max}
        LIMIT ${limit}
    `);

    return arrowToJSON(result);
}

/**
 * Get galaxy counts per HEALPix pixel (for LOD density map).
 */
function queryDensity(params) {
    const {
        dist_min = 0, dist_max = 99999,
        mass_min = -99, mass_max = 99
    } = params;

    const result = conn.query(`
        SELECT healpix_idx, count(*) as cnt
        FROM catalog
        WHERE dist BETWEEN ${dist_min} AND ${dist_max}
          AND mass BETWEEN ${mass_min} AND ${mass_max}
        GROUP BY healpix_idx
    `);

    return arrowToJSON(result);
}

/**
 * Compute histogram bins server-side.
 */
function queryHistogram(params) {
    const { field, bins = 30, min_val, max_val, dist_min, dist_max, mass_min, mass_max } = params;
    const step = (max_val - min_val) / bins;

    let filterClause = 'WHERE 1=1';
    if (dist_min !== undefined) filterClause += ` AND dist BETWEEN ${dist_min} AND ${dist_max}`;
    if (mass_min !== undefined) filterClause += ` AND mass BETWEEN ${mass_min} AND ${mass_max}`;

    const result = conn.query(`
        SELECT CAST(floor((${field} - ${min_val}) / ${step}) AS INTEGER) as bin,
               count(*) as cnt
        FROM catalog
        ${filterClause}
          AND ${field} BETWEEN ${min_val} AND ${max_val}
        GROUP BY bin
        ORDER BY bin
    `);

    return arrowToJSON(result);
}

/**
 * Search galaxies by ID substring.
 */
function querySearch(params) {
    const { q, limit = 10 } = params;
    const escaped = q.replace(/'/g, "''");
    const result = conn.query(`
        SELECT id, ra, dec, dist, mass
        FROM catalog
        WHERE lower(id) LIKE '%${escaped.toLowerCase()}%'
        LIMIT ${limit}
    `);

    return arrowToJSON(result);
}

/**
 * Get total count with filters.
 */
function queryCount(params) {
    const {
        dist_min = 0, dist_max = 99999,
        mass_min = -99, mass_max = 99
    } = params;

    const result = conn.query(`
        SELECT count(*) as total
        FROM catalog
        WHERE dist BETWEEN ${dist_min} AND ${dist_max}
          AND mass BETWEEN ${mass_min} AND ${mass_max}
    `);

    const rows = arrowToJSON(result);
    return rows[0]?.total || 0;
}

/**
 * Select galaxies inside a polygon (point-in-polygon test).
 * vertices: [{ra, dec}, ...] defining the polygon on the sky.
 *
 * We do this by fetching all galaxies in the bounding box,
 * then filtering by point-in-polygon in JS.
 */
function querySelectPolygon(params) {
    const { vertices, dist_min = 0, dist_max = 99999, mass_min = -99, mass_max = 99 } = params;

    // Compute bounding box of polygon
    let raMin = 360, raMax = 0, decMin = 90, decMax = -90;
    vertices.forEach(v => {
        if (v.ra < raMin) raMin = v.ra;
        if (v.ra > raMax) raMax = v.ra;
        if (v.dec < decMin) decMin = v.dec;
        if (v.dec > decMax) decMax = v.dec;
    });

    // Pad slightly
    raMin = Math.max(0, raMin - 1);
    raMax = Math.min(360, raMax + 1);
    decMin = Math.max(-90, decMin - 1);
    decMax = Math.min(90, decMax + 1);

    const result = conn.query(`
        SELECT id, ra, dec, dist, mass
        FROM catalog
        WHERE ra BETWEEN ${raMin} AND ${raMax}
          AND dec BETWEEN ${decMin} AND ${decMax}
          AND dist BETWEEN ${dist_min} AND ${dist_max}
          AND mass BETWEEN ${mass_min} AND ${mass_max}
    `);

    const galaxies = arrowToJSON(result);

    // Point-in-polygon test
    const selected = galaxies.filter(g => {
        return pointInPolygon(g.ra, g.dec, vertices);
    });

    return selected;
}

/**
 * Select galaxies by HEALPix pixel indices (for posterior selection).
 */
function querySelectByPixels(params) {
    const { pixelIndices, dist_min = 0, dist_max = 99999, mass_min = -99, mass_max = 99 } = params;
    const pixelList = pixelIndices.join(',');

    const result = conn.query(`
        SELECT id, ra, dec, dist, mass
        FROM catalog
        WHERE healpix_idx IN (${pixelList})
          AND dist BETWEEN ${dist_min} AND ${dist_max}
          AND mass BETWEEN ${mass_min} AND ${mass_max}
    `);

    return arrowToJSON(result);
}

/**
 * Export full data for a list of galaxy IDs.
 */
function queryExport(params) {
    const { ids } = params;
    const idList = ids.map(id => `'${id.replace(/'/g, "''")}'`).join(',');

    const result = conn.query(`
        SELECT id, ra, dec, dist, mass
        FROM catalog
        WHERE id IN (${idList})
    `);

    return arrowToJSON(result);
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function arrowToJSON(arrowResult) {
    const rows = [];
    const schema = arrowResult.schema.fields.map(f => f.name);

    for (let i = 0; i < arrowResult.numRows; i++) {
        const row = {};
        for (const name of schema) {
            const col = arrowResult.getChild(name);
            row[name] = col.get(i);
        }
        rows.push(row);
    }
    return rows;
}

function pointInPolygon(x, y, polygon) {
    let inside = false;
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
        const xi = polygon[i].ra, yi = polygon[i].dec;
        const xj = polygon[j].ra, yj = polygon[j].dec;
        const intersect = ((yi > y) !== (yj > y)) &&
            (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

// ── Message Handler ──────────────────────────────────────────────────────────

self.onmessage = function (e) {
    const { id, type, ...params } = e.data;

    try {
        let result;
        switch (type) {
            case 'init':
                result = initDB(params.parquetUrl);
                break;
            case 'galaxies':
                result = queryGalaxies(params);
                break;
            case 'density':
                result = queryDensity(params);
                break;
            case 'histogram':
                result = queryHistogram(params);
                break;
            case 'search':
                result = querySearch(params);
                break;
            case 'count':
                result = queryCount(params);
                break;
            case 'select_polygon':
                result = querySelectPolygon(params);
                break;
            case 'select_posterior':
                result = querySelectByPixels(params);
                break;
            case 'export':
                result = queryExport(params);
                break;
            default:
                throw new Error(`Unknown message type: ${type}`);
        }
        self.postMessage({ id, type, result });
    } catch (error) {
        self.postMessage({ id, type, error: error.message });
    }
};
