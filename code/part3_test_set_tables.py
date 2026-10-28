"""Images of the test sets for the NaiveBayes and DecTrees tabs (tables t17 and t18), drawn in the same style as t11-t16 of
notebook 04. t17: six person-days of evaluation (test) people from data/samples/nb_days_sample.csv; the person split comes from
person_kinds.parquet (Part 2). t18: six evaluation people (three who broke, three who held) from
data/samples/who_breaks_sample.csv.
Usage: python code/part3_test_set_tables.py <folder with person_kinds.parquet> <output folder>"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]
PROC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
SEED = 20260917
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "text.color": "#0b0b0b", "font.family": "sans-serif",
                     "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "figure.dpi": 110, "savefig.dpi": 150, "savefig.bbox": "tight"})

def table_png(df, name, title, width=11, mono=(), widths=None):
    # the same table drawing as notebook 04: the table fills the figure, 0.08 in of padding in every column, headers aligned left
    fig, ax = plt.subplots(figsize=(width, 0.3 * (len(df) + 1))); fig.subplots_adjust(0, 0, 1, 1); ax.axis("off"); ax.grid(False)
    w = np.asarray(widths if widths is not None else [1.0] * df.shape[1], float); w = w / w.sum()
    tb = ax.table(cellText=df.astype(str).values, colLabels=list(df.columns), cellLoc="left", colLoc="left", colWidths=list(w), bbox=[0, 0, 1, 1])
    tb.auto_set_font_size(False); tb.set_fontsize(8.5)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor("#e1e0d9"); cell.PAD = 0.08 / (w[c] * width)
        if r == 0: cell.set_facecolor("#e8f0fb"); cell.set_text_props(weight="bold")
        elif df.columns[c] in mono: cell.set_text_props(family="monospace")
    ax.set_title(title, loc="left", fontweight="bold", fontsize=11, pad=8)
    fig.savefig(OUT / f"{name}.png"); plt.close(fig); print("saved", name)

# t17: test person-days, as notebook 04 writes them (t11 shows training days)
split = pd.read_parquet(PROC / "person_kinds.parquet").split
days = pd.read_csv(REPO / "data/samples/nb_days_sample.csv")
days = days[days.uid.map(split).eq("eval")]
pick = pd.concat([days[days.label == 0].sample(3, random_state=SEED), days[days.label == 1].sample(3, random_state=SEED)])
t17 = pd.DataFrame({"uid": pick.uid.to_numpy(), "day": pick.day.to_numpy(), "day type": np.where(pick.rest_day, "rest", "work"),
                    "label": np.where(pick.label == 1, "emergency", "ordinary"), "half hours 00:30 to 23:30": pick.half_hours.to_numpy()})
table_png(t17, "t17_nb_test_days", "Six test person-days (evaluation people), one letter per half hour\nH home, P daytime place, E elsewhere, · not seen", 7.4,
          mono=("half hours 00:30 to 23:30",), widths=[0.09, 0.07, 0.11, 0.13, 0.60])

# t18: test people for the trees, the same columns as t14 (training people)
wb = pd.read_csv(REPO / "data/samples/who_breaks_sample.csv", index_col=0)
ev = wb[wb.split == "eval"]
te = pd.concat([ev[ev.broke == 1].sample(3, random_state=SEED), ev[ev.broke == 0].sample(3, random_state=SEED)])
place_cols = [c for c in wb.columns if c.startswith("daytime place: ")]
t18 = te[["regularity", "midday_away", "home_share", "rg_km", "records_per_day", "habit_surprise_30_44"]].round(3).assign(
    kind=te.kind, daytime_place=te[place_cols].idxmax(axis=1).str.replace("daytime place: ", "", regex=False),
    broke=te.broke.astype(bool)).reset_index()
table_png(t18, "t18_tree_test_people", "Test people for the trees (three who broke, three who held; features from days 0-44, label from 45-74)", 13,
          widths=[0.06, 0.08, 0.09, 0.09, 0.06, 0.11, 0.15, 0.14, 0.11, 0.06])
