"""Explanatory images for the Overview sections of the Regression and AdaBoost tabs (o11 to o14), all with toy numbers.
o11 a straight line fitted by least squares and what one weight means; o12 how logistic regression turns a straight-line score into a
probability and a class; o13 bagging against boosting; o14 three rounds of AdaBoost on twelve toy people, with the reweighting, alpha and
the weighted vote, computed exactly as in notebook 09.
Usage: python overview_images_part4.py --out ../site/src/assets/figures
"""
import argparse
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c3c2b7",
    "axes.grid": True, "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "text.color": "#0b0b0b", "axes.labelcolor": "#52514e", "xtick.color": "#898781", "ytick.color": "#898781",
    "font.family": "sans-serif", "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "figure.dpi": 110, "savefig.dpi": 150, "savefig.bbox": "tight"})
GREY, INK = "#898781", "#52514e"


def linear(out):
    """Twelve toy people: share of a usual fortnight away from home against the share of the next week. The fitted line, its errors, one weight."""
    rng = np.random.default_rng(3)
    x = np.sort(rng.uniform(0.1, 0.95, 12)); y = np.clip(0.05 + 0.85 * x + rng.normal(0, 0.07, 12), 0, 1)
    b1, b0 = np.polyfit(x, y, 1); yhat = b0 + b1 * x
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    for xi, yi, hi in zip(x, y, yhat): ax.plot([xi, xi], [yi, hi], color=C[1], lw=1.2, alpha=0.8)
    ax.scatter(x, y, s=40, color=C[0], zorder=3, label="a person")
    xx = np.linspace(0, 1, 50); ax.plot(xx, b0 + b1 * xx, color="#0b0b0b", lw=2, label=f"fitted line: {b0:.2f} + {b1:.2f} x habit")
    ax.plot([], [], color=C[1], lw=1.2, label="error (residual)")
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="habit: share of a usual fortnight away from home", ylabel="next week: share away from home",
           title="1. Least squares: the line with the smallest squared errors")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax = axes[1]
    x0 = 0.4; ax.plot(xx, b0 + b1 * xx, color="#0b0b0b", lw=2)
    ax.plot([x0, x0 + 0.1], [b0 + b1 * x0] * 2, color=C[2], lw=2); ax.plot([x0 + 0.1] * 2, [b0 + b1 * x0, b0 + b1 * (x0 + 0.1)], color=C[2], lw=2)
    ax.text(x0 + 0.05, b0 + b1 * x0 - 0.05, "+10 points\nof habit", ha="center", va="top", fontsize=9, color=C[2])
    ax.text(x0 + 0.12, b0 + b1 * (x0 + 0.05), f"+{b1 * 10:.1f} points\nnext week", ha="left", va="center", fontsize=9, color=C[2])
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="habit", ylabel="predicted next week", title="2. A weight is a slope: what one more unit buys")
    fig.savefig(out / "o11_linear_regression.png"); plt.close(fig)


def logistic(out):
    """A straight-line score (the same kind of sum as in linear regression) squeezed by the sigmoid into a probability, then cut at 0.5."""
    z = np.linspace(-6, 6, 200); p = 1 / (1 + np.exp(-z))
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 3.9), gridspec_kw={"width_ratios": [1, 1.2, 0.9]})
    ax = axes[0]; terms = [("starting value", -0.3), ("seen elsewhere at 12:00", 0.11), ("at home at 20:00", 0.04), ("at the place at 09:00", -0.05), ("17 seen half hours", 0.62)]
    run = np.cumsum([v for _, v in terms])
    ax.barh(range(len(terms))[::-1], [v for _, v in terms], color=[C[1] if v > 0 else C[0] for _, v in terms], height=0.6)
    ax.set_yticks(range(len(terms))[::-1]); ax.set_yticklabels([t for t, _ in terms], fontsize=8.5); ax.yaxis.grid(False); ax.axvline(0, color=GREY, lw=1)
    ax.set(xlabel="contribution to the score (log of the odds)", title=f"1. A score: weights times inputs, z = {run[-1]:.2f}")
    ax = axes[1]
    ax.plot(z, p, color="#0b0b0b", lw=2.2); ax.axhline(0.5, color=GREY, lw=1, ls="--")
    zz = run[-1]; pz = 1 / (1 + np.exp(-zz))
    ax.plot([zz, zz], [0, pz], color=C[1], lw=1.5); ax.plot([-6, zz], [pz, pz], color=C[1], lw=1.5); ax.scatter([zz], [pz], color=C[1], zorder=4)
    ax.text(zz + 0.3, pz - 0.08, f"P = 1 / (1 + e^-z) = {pz:.2f}", fontsize=9, color=C[1])
    ax.set(xlabel="score z", ylabel="probability of an emergency day", ylim=(0, 1), title="2. The sigmoid turns any score into a probability")
    ax = axes[2]; ax.axis("off"); ax.grid(False)
    ax.text(0.02, 0.85, "3. A class", fontsize=12, fontweight="bold", transform=ax.transAxes)
    ax.text(0.02, 0.62, f"P = {pz:.2f} is above 0.5\n-> predicted: emergency day", fontsize=10, transform=ax.transAxes)
    ax.text(0.02, 0.30, f"Each weight is a log of an odds ratio:\na weight of 0.11 multiplies the odds\nby e^0.11 = {np.exp(0.11):.2f}, 12% higher odds", fontsize=9.5, color=INK, transform=ax.transAxes)
    fig.savefig(out / "o12_logistic_sigmoid.png"); plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec="#c3c2b7", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04", fc=fc, ec=ec, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, a, b, c=GREY):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, color=c, lw=1.2))


def bagging_boosting(out):
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.4))
    for ax in axes: ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off"); ax.grid(False)
    ax = axes[0]; ax.set_title("Bagging: many trees side by side, each on a resample, equal votes", fontsize=11.5)
    box(ax, 3.5, 5.0, 3, 0.7, "training people", "#e8f0fb")
    for j, x in enumerate([0.4, 2.8, 5.2, 7.6]):
        box(ax, x, 3.3, 2, 0.8, f"resample {j + 1}\n(drawn with replacement)", "#f3f2ee", fs=8)
        box(ax, x, 1.8, 2, 0.8, f"deep tree {j + 1}", "#ffffff", ec=C[0])
        arrow(ax, (5, 5.0), (x + 1, 4.1)); arrow(ax, (x + 1, 3.3), (x + 1, 2.6)); arrow(ax, (x + 1, 1.8), (5, 0.95))
    box(ax, 3.5, 0.25, 3, 0.7, "average of equal votes", "#e8f0fb")
    ax = axes[1]; ax.set_title("Boosting: small trees one after another, each fixing the last", fontsize=11.5)
    for j, x in enumerate([0.2, 2.7, 5.2, 7.7]):
        box(ax, x, 3.9, 2.1, 1.0, f"people, reweighted\n{'all equal' if j == 0 else 'misses weigh more'}", "#f3f2ee", fs=8)
        box(ax, x, 2.2, 2.1, 0.9, f"stump {j + 1}\nvote alpha {[0.35, 0.22, 0.17, 0.12][j]:.2f}", "#ffffff", ec=C[1], fs=8.5)
        arrow(ax, (x + 1.05, 3.9), (x + 1.05, 3.1), C[1]); arrow(ax, (x + 1.05, 2.2), (5, 0.95))
        if j < 3: arrow(ax, (x + 2.1, 2.65), (x + 2.6, 4.4), C[1])
    box(ax, 3.4, 0.25, 3.2, 0.7, "weighted vote: sum of alpha x vote", "#fbe9e0")
    fig.savefig(out / "o13_bagging_vs_boosting.png"); plt.close(fig)


def adaboost_rounds(out):
    """Twelve toy people on two features; three rounds of stumps, row weights drawn as dot size, alpha and the weighted vote."""
    x1 = np.array([0.15, 0.25, 0.35, 0.42, 0.55, 0.62, 0.70, 0.78, 0.85, 0.30, 0.66, 0.90])
    x2 = np.array([0.80, 0.30, 0.62, 0.20, 0.75, 0.40, 0.85, 0.25, 0.60, 0.10, 0.12, 0.88])
    yv = np.array([-1, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1])
    X = np.c_[x1, x2]; w = np.ones(12) / 12; F = np.zeros(12); rounds = []
    for r in range(3):
        best = None
        for f in (0, 1):
            for t in np.unique(X[:, f]):
                for s in (1, -1):
                    pred = np.where(X[:, f] > t, s, -s); e = w[pred != yv].sum()
                    if best is None or e < best[0]: best = (e, f, t, s, pred)
        e, f, t, s, pred = best; a = 0.5 * np.log((1 - e) / e)
        rounds.append((w.copy(), f, t, s, e, a)); F += a * pred
        w = w * np.exp(-a * yv * pred); w /= w.sum()
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.1), sharey=True)
    for r_, (ax, (wr, f, t, s, e, a)) in enumerate(zip(axes[:3], rounds), 1):
        ax.scatter(x1, x2, s=2400 * wr, c=[C[1] if v > 0 else C[0] for v in yv], edgecolor="#0b0b0b", lw=0.4, alpha=0.85)
        (ax.axvline if f == 0 else ax.axhline)(t, color="#0b0b0b", lw=1.6, ls="--")
        ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="feature 1", title=f"Round {r_}: weighted error {e:.2f}, alpha {a:.2f}")
    axes[0].set_ylabel("feature 2")
    ax = axes[3]; pred = np.sign(F)
    ax.scatter(x1, x2, s=120, c=[C[1] if v > 0 else C[0] for v in yv], edgecolor=["#0b0b0b" if p_ == v else C[7] for p_, v in zip(pred, yv)], lw=[0.4 if p_ == v else 2.2 for p_, v in zip(pred, yv)])
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="feature 1", title=f"Weighted vote: {np.mean(pred == yv):.0%} right")
    fig.suptitle("AdaBoost on twelve toy people: dot size is the row weight going into the round; orange broke, blue held", x=0.01, ha="left", fontweight="bold", fontsize=12.5, y=1.04)
    fig.savefig(out / "o14_adaboost_rounds.png"); plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="../site/src/assets/figures"); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    linear(out); logistic(out); bagging_boosting(out); adaboost_rounds(out)
    print("written o11 to o14 to", out)
