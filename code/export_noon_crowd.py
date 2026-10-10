"""Data for the Introduction figure "The missing noon crowd".
Regular commuters (the k-means kind from notebooks/03_kinds_of_movers.ipynb) on workdays: on how many of the ten ordinary workdays
(days 45-59) and the ten emergency workdays (60-74) each one spent the middle of the day (10:00-16:00, most frequent cell) at their
usual day anchor, counted at the anchor's 3 km square (6 x 6 cells). Squares with at least 3 commuters there on an average ordinary
workday are kept. Output: site/src/data/noon_crowd.json, one row per square.
Usage: python export_noon_crowd.py --root /projects/ancz7294/yjmob --out ../site/src/data/noon_crowd.json
"""
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd

B = 6

def main(root, out):
    proc = Path(root) / "data/processed"
    kinds = pd.read_parquet(proc / "person_kinds.parquet")
    anc = pd.read_parquet(proc / "person_anchors.parquet")
    who = kinds.index[kinds.kind == "regular commuters"]
    an = pd.read_parquet(proc / "yjmob_analysis.parquet", columns=["uid", "d", "t", "x", "y", "weekend", "holiday_like"],
                         filters=[("d", ">=", 45)])
    an = an[an.uid.isin(who) & ~an.weekend & ~an.holiday_like & an.t.between(20, 31)]
    an["cell"] = an.x.astype("int32") * 256 + an.y
    day = an.groupby(["uid", "d", "cell"]).size().rename("n").reset_index()
    day = day.sort_values("n", ascending=False).drop_duplicates(["uid", "d"]).join(anc.day_anchor, on="uid").dropna(subset=["day_anchor"])
    a = day.day_anchor.astype("int64")
    day["at_work"] = np.maximum((day.cell // 256 - a // 256).abs(), (day.cell % 256 - a % 256).abs()) <= 1
    day["sx"], day["sy"] = (a // 256 - 1) // B, (a % 256 - 1) // B
    day["period"] = np.where(day.d >= 60, "emergency", "ordinary")
    n_days = day.groupby("period").d.nunique()
    att = day[day.at_work].groupby(["sx", "sy", "period"]).size().unstack(fill_value=0) / n_days
    att = att[att.ordinary >= 3]
    rows = [{"x": int(x), "y": int(y), "usual": round(float(r.ordinary), 2), "emergency": round(float(r.emergency), 2)} for (x, y), r in att.iterrows()]
    meta = {"square_cells": B, "grid": 200, "workdays": {k: int(v) for k, v in n_days.items()},
            "usual_total": round(float(att.ordinary.sum()), 1), "emergency_total": round(float(att.emergency.sum()), 1),
            "squares_losing": int((att.emergency < att.ordinary).sum()), "squares_gaining": int((att.emergency > att.ordinary).sum()),
            "commuter_middays_recorded_per_workday": {k: round(float(v), 1) for k, v in (day.groupby("period").size() / n_days).items()}}
    Path(out).write_text(json.dumps({"meta": meta, "squares": rows}, separators=(",", ":")))
    print(json.dumps(meta, indent=2))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="/projects/ancz7294/yjmob"); ap.add_argument("--out", default="noon_crowd.json")
    a = ap.parse_args(); main(a.root, a.out)
