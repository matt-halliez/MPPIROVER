#!/usr/bin/env python3
"""
convert_tracks.py
─────────────────
Convert one or several minimalist F1TENTH track CSVs
(x_m, y_m, …) into the full 7-column Liniger format:

   s_m; x_m; y_m; psi_rad; kappa_radpm; vx_mps; ax_mps2

HOW TO USE
----------
1. Put this file next to your *.csv* tracks.
2. Open it and edit the CONFIGURATION block:
      - files_in   : list of source CSVs
      - files_out  : list of destination names
      - vx_default : constant reference speed  [m/s]
      - ax_default : constant acceleration     [m/s²]
3. Run:
      $ python3 convert_tracks.py
"""

# ─────────────────────────── CONFIGURATION ─────────────────────────── #
#files_in   = ["siccs_first_floor_1.csv"]          # add more if you like
#files_out  = ["siccs_first_floor_dyn.csv"]        # must match length of files_in
files_in = ["generated_square_trajectory_small.csv"]
files_out = ["/home/sdc6/f1tenth_ws/gsts.csv"]
vx_default = 5.00                         # m/s
ax_default = 0.00                         # m/s²
# ────────────────────────────────────────────────────────────────────── #

import numpy as np
import pandas as pd
from pathlib import Path
import sys

# ------ geometry helpers ---------------------------------------------- #
def compute_geometry(x: np.ndarray, y: np.ndarray):
    """Return cumulative arc length s, heading ψ, curvature κ."""
    dx, dy = np.diff(x, prepend=x[0]), np.diff(y, prepend=y[0])
    ds = np.hypot(dx, dy)
    s = np.cumsum(ds)

    psi = np.unwrap(np.arctan2(np.gradient(y, s), np.gradient(x, s)))
    psi = (psi + np.pi) % (2*np.pi) - np.pi      # wrap to (-π, π]

    kappa = np.gradient(psi, s, edge_order=2)    # rad per metre
    return s, psi, kappa

# ------ main conversion loop ----------------------------------------- #
if len(files_in) != len(files_out):
    sys.exit("files_in and files_out must have the same length!")

for src, dst in zip(files_in, files_out):
    src_p = Path(src).expanduser()
    if not src_p.is_file():
        print(f"[warn]   {src_p} not found – skipping")
        continue

    # ----- read minimal track (ignore the 3rd/4th columns for geometry)
    df_xy = pd.read_csv(src_p, comment="#", header=None,
                        names=["x_m", "y_m", "w_tr_r", "w_tr_l"])

    s, psi, kappa = compute_geometry(df_xy.x_m.values, df_xy.y_m.values)

    df_out = pd.DataFrame({
        "s_m":          np.round(s, 7),
        "x_m":          np.round(df_xy.x_m, 7),
        "y_m":          np.round(df_xy.y_m, 7),
        "psi_rad":      np.round(psi, 7),
        "kappa_radpm":  np.round(kappa, 7),
        "vx_mps":       vx_default,
        "ax_mps2":      ax_default
    })

    with open(dst, "w") as f:
        f.write(f"# Generated from {src_p.name}\n")
        f.write("# s_m; x_m; y_m; psi_rad; kappa_radpm; vx_mps; ax_mps2\n")
        df_out.to_csv(f, sep=";", index=False, header=False, float_format="%.7f")

    print(f"[ok]     wrote {len(df_out)} rows → {dst}")
