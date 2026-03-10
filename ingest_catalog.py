#!/usr/bin/env python3
"""
Convert a galaxy catalog .txt file to optimized Parquet for DuckDB-WASM.

Usage:
    python ingest_catalog.py data/tab2.txt --output data/catalog.parquet --nside 64

The input file should be the 2MRS-format catalog (or whitespace-delimited with
columns: name, dist, mass, ...).  The source name encodes RA/Dec as:
    HHMMSSCC+DDMMSSP   (16-char coordinate string)
"""

import argparse
import json
import math
import re
import sys

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


# ── Coordinate parsing ───────────────────────────────────────────────────────

def parse_coordinate(name):
    """Parse 2MRS-style source name into (RA, Dec) in degrees.

    Name format: HHMMSSCC±DDMMSSP
      HH    = hours of RA
      MM    = minutes of RA
      SS    = seconds of RA (integer part)
      CC    = centiseconds of RA
      ±     = sign of Dec
      DD    = degrees of Dec
      MM    = arcminutes of Dec
      SS    = arcseconds of Dec (integer part)
      P     = tenths of arcsecond of Dec
    """
    m = re.match(
        r'^(\d{2})(\d{2})(\d{2})(\d{2})([+-])(\d{2})(\d{2})(\d{2})(\d)$',
        name.strip()
    )
    if not m:
        return None
    hh, mm_ra, ss_ra, cs_ra, sign, dd, dm, ds_dec, ts_dec = m.groups()
    ra_sec = float(ss_ra) + float(cs_ra) / 100.0
    ra = (float(hh) + float(mm_ra) / 60.0 + ra_sec / 3600.0) * 15.0

    dec_arcsec = float(ds_dec) + float(ts_dec) / 10.0
    dec = float(dd) + float(dm) / 60.0 + dec_arcsec / 3600.0
    if sign == '-':
        dec = -dec

    return ra, dec


# ── HEALPix ang2pix (RING order) ─────────────────────────────────────────────

def ang2pix_ring(nside, theta, phi):
    """Convert (theta, phi) in radians to HEALPix RING pixel index.

    theta = colatitude [0, π], phi = longitude [0, 2π].
    Pure-Python implementation — no healpy needed.
    """
    npix = 12 * nside * nside
    z = math.cos(theta)
    za = abs(z)
    tt = (phi % (2 * math.pi)) / (math.pi / 2)  # in [0, 4)

    if za <= 2.0 / 3.0:
        # Equatorial belt
        temp1 = nside * (0.5 + tt)
        temp2 = nside * z * 0.75
        jp = int(temp1 - temp2)
        jm = int(temp1 + temp2)
        ir = nside + 1 + jp - jm
        kshift = 1 - (ir & 1)
        ip = (jp + jm - nside + kshift + 1) // 2
        ip = ip % (4 * nside)
        return 2 * nside * (nside - 1) + (ir - 1) * 4 * nside + ip
    else:
        tp = tt - int(tt)
        tmp = nside * math.sqrt(3 * (1 - za))
        jp = int(tp * tmp)
        jm = int((1.0 - tp) * tmp)
        ir = jp + jm + 1
        ip = int(tt * ir)
        ip = ip % (4 * ir)
        if z > 0:
            return 2 * ir * (ir - 1) + ip
        else:
            return npix - 2 * ir * (ir + 1) + ip


def radec_to_healpix(ra_deg, dec_deg, nside):
    """Convert (RA, Dec) in degrees to HEALPix RING pixel index."""
    theta = math.radians(90.0 - dec_deg)  # colatitude
    phi = math.radians(ra_deg)
    return ang2pix_ring(nside, theta, phi)


# ── Main ingestion ────────────────────────────────────────────────────────────

def ingest(input_path, output_path, nside=64):
    """Read catalog, compute HEALPix indices, write Parquet."""
    ids, ras, decs, dists, masses, hpx_indices = [], [], [], [], [], []
    skipped = 0

    with open(input_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            parts = line.split()
            if len(parts) < 3:
                skipped += 1
                continue
            name = parts[0]
            coords = parse_coordinate(name)
            if coords is None:
                skipped += 1
                continue
            ra, dec = coords
            dist = float(parts[1])
            mass = float(parts[2])

            # Skip invalid entries (mass = -9.00 means excluded AGN/quasar)
            if mass < 0:
                skipped += 1
                continue

            hpx = radec_to_healpix(ra, dec, nside)

            ids.append(name)
            ras.append(ra)
            decs.append(dec)
            dists.append(dist)
            masses.append(mass)
            hpx_indices.append(hpx)

    print(f"Parsed {len(ids)} galaxies ({skipped} skipped)")

    # Build Arrow table
    table = pa.table({
        'id': pa.array(ids, type=pa.utf8()),
        'ra': pa.array(ras, type=pa.float64()),
        'dec': pa.array(decs, type=pa.float64()),
        'dist': pa.array(dists, type=pa.float64()),
        'mass': pa.array(masses, type=pa.float64()),
        'healpix_idx': pa.array(hpx_indices, type=pa.int32()),
    })

    # Sort by HEALPix index for better row-group locality
    sort_indices = pa.compute.sort_indices(table, sort_keys=[('healpix_idx', 'ascending')])
    table = table.take(sort_indices)

    # Write Parquet with compression
    pq.write_table(
        table,
        output_path,
        compression='snappy',
        row_group_size=10000,
    )
    print(f"Wrote {output_path} ({table.num_rows} rows)")

    # Compute density summary
    hpx_arr = np.array(hpx_indices, dtype=np.int32)
    npix = 12 * nside * nside
    counts = np.bincount(hpx_arr, minlength=npix)

    # Only store nonzero pixels
    density = {}
    for ipix in range(npix):
        if counts[ipix] > 0:
            density[str(ipix)] = int(counts[ipix])

    density_path = output_path.rsplit('.', 1)[0] + f'_density_nside{nside}.json'
    with open(density_path, 'w') as f:
        json.dump({'nside': nside, 'npix': npix, 'pixels': density}, f)
    print(f"Wrote {density_path} ({len(density)} nonzero pixels)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert galaxy catalog to Parquet')
    parser.add_argument('input', help='Input catalog file (.txt)')
    parser.add_argument('--output', '-o', default='data/catalog.parquet',
                        help='Output Parquet file path')
    parser.add_argument('--nside', type=int, default=64,
                        help='HEALPix NSIDE for spatial index (default: 64)')
    args = parser.parse_args()

    ingest(args.input, args.output, args.nside)
