"""Table snapshots for the DataPrep_EDA tab, drawn with the table function from notebooks/01_first_look.ipynb.
t02 is redrawn here from the current yjmob_analysis.parquet so that it shows the holiday_like column added by prep.py.
Usage: python table_images.py --root <folder with data/processed> --out <figures folder>
"""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "font.family": "sans-serif", "font.size": 10,
                     "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "figure.dpi": 110, "savefig.dpi": 150, "savefig.bbox": "tight"})

def table_png(df, path, title, width=11):
    fig, ax = plt.subplots(figsize=(width, 0.4 * len(df) + 0.9)); ax.axis("off"); ax.grid(False)
    tb = ax.table(cellText=df.astype(str).values, colLabels=list(df.columns), loc="center", cellLoc="left")
    tb.auto_set_font_size(False); tb.set_fontsize(8.5); tb.scale(1, 1.25)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor("#e1e0d9")
        if r == 0: cell.set_facecolor("#e8f0fb"); cell.set_text_props(weight="bold")
    ax.set_title(title, loc="left", fontweight="bold"); fig.savefig(path); plt.close(fig); print("saved", path)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    proc, out = Path(a.root) / "data/processed", Path(a.out)
    an = pd.read_parquet(proc / "yjmob_analysis.parquet", filters=[("uid", "==", 1)])
    table_png(an.head(8).drop(columns=["slot"]), out / "t02_yjmob_clean.png", "YJMob analysis table, cleaned (person 1, first 8 rows)", 16)
