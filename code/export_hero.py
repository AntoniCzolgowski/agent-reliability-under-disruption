"""Export the data behind the Home page figure ("the breathing city") as one small image atlas plus a JSON header.

Definition (WEBSITE-BRIEF.md section 4, DECISIONS R1, R2, R8):
- development people only (split == dev)
- ordinary workdays = days 0-59 with workday true in day_table.parquet; emergency workdays = days 60-74 with workday true
- value(cell, slot, condition) = distinct people observed in the cell during the slot, averaged over the days of the condition
- cell mask: at least MIN_PEOPLE distinct development people observed in the cell during days 0-59, applied to both conditions
- atlas: 48 frames of 200 x 200 in an 8 x 6 grid, frame i at column i % 8, row i // 8; R = ordinary, G = emergency, B = 0
- pixel = round(255 * sqrt(value / vmax)) with one vmax over both conditions; frame row 0 is y = 1
The atlas is written as lossless WebP (pixel-identical to PNG, about half the size); --format png writes a PNG instead.
Usage: python export_hero.py --root <folder with data/processed> --out <site/public/data> [--format webp|png]
"""
import argparse, json, subprocess, datetime
from pathlib import Path
import numpy as np, pandas as pd
from PIL import Image

GRID, SLOTS, COLS, ROWS = 200, 48, 8, 6
MIN_PEOPLE = 5

def frames(an, days):
    """Mean distinct people per cell and slot over the given days, as an array [slot, y, x]."""
    sub = an[an.d.isin(days)]
    counts = sub.groupby(["t", "y", "x"]).size()
    arr = np.zeros((SLOTS, GRID, GRID), dtype="float64")
    idx = counts.index
    arr[idx.get_level_values("t"), idx.get_level_values("y") - 1, idx.get_level_values("x") - 1] = counts.to_numpy()
    return arr / len(days)

def main(root, out, fmt="webp"):
    proc = Path(root) / "data/processed"
    dt = pd.read_parquet(proc / "day_table.parquet")
    ordinary = dt.d[dt.workday & (dt.d < 60)].tolist()
    emergency = dt.d[dt.workday & (dt.d >= 60)].tolist()
    an = pd.read_parquet(proc / "yjmob_analysis.parquet", columns=["uid", "d", "t", "x", "y", "split"])
    an = an[an.split == "dev"]
    people = int(an.uid.nunique())

    # mask from all days 0-59, distinct development people per cell
    early = an[an.d < 60]
    per_cell = early.drop_duplicates(["uid", "x", "y"]).groupby(["y", "x"]).size()
    mask = np.zeros((GRID, GRID), dtype=bool)
    keep = per_cell[per_cell >= MIN_PEOPLE].index
    mask[keep.get_level_values("y") - 1, keep.get_level_values("x") - 1] = True
    cells_occupied = int(len(per_cell))
    in_mask = an.merge(pd.DataFrame({"y": keep.get_level_values("y"), "x": keep.get_level_values("x"), "m": True}), how="left").m.fillna(False)
    records_removed_share = float(1 - in_mask.mean())

    ord_f, emg_f = frames(an, ordinary), frames(an, emergency)
    ord_f[:, ~mask] = 0; emg_f[:, ~mask] = 0
    vmax = float(max(ord_f.max(), emg_f.max()))
    enc = lambda a: np.round(255 * np.sqrt(np.clip(a / vmax, 0, 1))).astype("uint8")
    atlas = np.zeros((ROWS * GRID, COLS * GRID, 3), dtype="uint8")
    for i in range(SLOTS):
        r, c = i // COLS, i % COLS
        atlas[r * GRID:(r + 1) * GRID, c * GRID:(c + 1) * GRID, 0] = enc(ord_f[i])
        atlas[r * GRID:(r + 1) * GRID, c * GRID:(c + 1) * GRID, 1] = enc(emg_f[i])
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    atlas_name = "hero.webp" if fmt == "webp" else "hero.png"
    if fmt == "webp":
        Image.fromarray(atlas).save(out / atlas_name, lossless=True, quality=100, method=6)
    else:
        Image.fromarray(atlas).save(out / atlas_name, optimize=True)

    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=Path(__file__).parent).stdout.strip()
    except Exception:
        commit = ""
    header = {
        "atlas": atlas_name,
        "grid": GRID, "slots": SLOTS, "frame_columns": COLS, "frame_rows": ROWS,
        "frame_layout": "frame i at column i % 8, row i // 8; inside a frame, pixel column = x - 1, pixel row = y - 1 (row 0 at the top of the frame)",
        "channels": {"R": "ordinary workday", "G": "emergency workday", "B": "reserved"},
        "encoding": "pixel = round(255 * sqrt(value / vmax)); value = mean distinct development people observed in the cell during the slot",
        "vmax": vmax,
        "people": people, "split": "dev", "seed": 20260917,
        "days_ordinary": ordinary, "days_emergency": emergency,
        "mask": {"rule": f"at least {MIN_PEOPLE} distinct development people observed in the cell on days 0-59",
                 "cells_shown": int(mask.sum()), "cells_occupied": cells_occupied, "records_removed_share": records_removed_share},
        "slot_totals_ordinary": [float(v) for v in ord_f.sum(axis=(1, 2))],
        "slot_totals_emergency": [float(v) for v in emg_f.sum(axis=(1, 2))],
        "peak_slot_ordinary": int(ord_f.sum(axis=(1, 2)).argmax()), "peak_slot_emergency": int(emg_f.sum(axis=(1, 2)).argmax()),
        "exported": datetime.date.today().isoformat(), "script_commit": commit,
    }
    (out / "hero.json").write_text(json.dumps(header, indent=1))
    print(json.dumps({k: v for k, v in header.items() if not k.startswith("slot_totals")}, indent=1))
    print(atlas_name, (out / atlas_name).stat().st_size // 1024, "KB | hero.json", (out / "hero.json").stat().st_size // 1024, "KB")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--format", default="webp", choices=["webp", "png"])
    a = ap.parse_args(); main(a.root, a.out, a.format)
