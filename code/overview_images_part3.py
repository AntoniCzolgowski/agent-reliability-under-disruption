"""Explanatory images for the Overview sections of the NaiveBayes and DecTrees tabs (o06 to o10).
o06, o07 and o09 use toy numbers. o08 draws a real person-day from data/samples/nb_days_sample.csv (person 14892, day 58). o10 marks the
split worked by hand on the DecTrees tab (training people, notebook 04, logged in logs/part3_log.json).
Usage: python overview_images_part3.py --out ../site/src/assets/figures
"""
import argparse
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c3c2b7",
    "axes.grid": True, "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "text.color": "#0b0b0b", "axes.labelcolor": "#52514e", "xtick.color": "#898781", "ytick.color": "#898781",
    "font.family": "sans-serif", "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "figure.dpi": 110, "savefig.dpi": 150, "savefig.bbox": "tight"})
GREY = "#898781"
STATE_COL = {"H": "#2a78d6", "P": "#1baf7a", "E": "#eda100"}


def nb_reading(out):
    """A toy day with six seen half hours: each word's probability in the two classes, and the evidence added up."""
    words = ["work 07:30 home", "work 08:30 elsewhere", "work 09:30 place", "work 12:30 place", "work 17:30 elsewhere", "work 19:30 home"]
    p_ord = np.array([0.30, 0.42, 0.38, 0.40, 0.45, 0.50])
    p_emg = np.array([0.36, 0.38, 0.30, 0.31, 0.40, 0.56])
    llr = np.log(p_emg / p_ord); cum = np.cumsum(llr)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.1), gridspec_kw={"width_ratios": [1.25, 1]})
    y = np.arange(len(words))[::-1]
    axes[0].barh(y + 0.18, p_ord, height=0.34, color=C[0], label="P(word | ordinary day)")
    axes[0].barh(y - 0.18, p_emg, height=0.34, color=C[1], label="P(word | emergency day)")
    axes[0].set_yticks(y); axes[0].set_yticklabels(words); axes[0].yaxis.grid(False)
    axes[0].set(xlabel="how often the word appears in its half hour on training days", title="1. Training: count each word in each class")
    axes[0].legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2)
    axes[1].bar(range(len(words)), llr, color=[C[1] if v > 0 else C[0] for v in llr], width=0.6)
    axes[1].plot(range(len(words)), cum, color="#0b0b0b", marker="o", lw=2, label="running total")
    axes[1].axhline(0, color=GREY, lw=1)
    axes[1].set_xticks(range(len(words))); axes[1].set_xticklabels([w.split()[1] for w in words])
    post = 1 / (1 + np.exp(-cum[-1]))
    axes[1].set(ylabel="evidence for 'emergency' (log of the ratio)", title=f"2. Prediction: add up the evidence, P(emergency) = {post:.0%}")
    axes[1].text(5.3, 0.13, "above 0: points to an emergency day\nbelow 0: points to an ordinary day", ha="right", va="bottom", fontsize=8.5, color="#52514e")
    axes[1].legend(frameon=False, fontsize=9, loc="lower left")
    fig.suptitle("How Naive Bayes reads a day (toy numbers, the two classes equally common)", x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.03)
    fig.savefig(out / "o06_nb_reading_a_day.png"); plt.close(fig)


def smoothing(out):
    """One word never seen on emergency training days: without smoothing it rules out the emergency for any day that contains it."""
    n_emg = np.array([12, 30, 0, 8]); n_ord = np.array([10, 25, 3, 12]); labels = ["home\n08:00", "elsewhere\n08:00", "place\n03:00", "place\n12:00"]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 3.9))
    xx = np.arange(4)
    axes[0].bar(xx - 0.2, n_ord, width=0.4, color=C[0], label="ordinary training days")
    axes[0].bar(xx + 0.2, n_emg, width=0.4, color=C[1], label="emergency training days")
    axes[0].text(2.2, 0.6, "0", ha="center", fontsize=10, fontweight="bold", color=C[7])
    axes[0].set_xticks(xx); axes[0].set_xticklabels(labels); axes[0].set(ylabel="times the word was written", title="Counts: one word never appears in one class")
    axes[0].legend(frameon=False, fontsize=9); axes[0].xaxis.grid(False)
    for a, c, nm in [(0, C[7], "alpha = 0, no smoothing"), (1, C[2], "alpha = 1 (Laplace)")]:
        p = (n_emg + a) / (n_emg.sum() + a * 4)
        axes[1].plot(xx, p, marker="o", lw=2, color=c, label=nm)
    axes[1].annotate("probability 0: any day with\nthis word would be ruled out\nas an emergency day", (2, 0.0), (2.5, 0.27), fontsize=8.5, ha="center",
                     arrowprops=dict(arrowstyle="->", color="#0b0b0b", shrinkB=4))
    axes[1].set_xticks(xx); axes[1].set_xticklabels(labels); axes[1].set(ylabel="P(word | emergency)", title="Smoothing adds alpha to every count")
    axes[1].legend(frameon=False, fontsize=9, loc="upper right")
    fig.suptitle("Why Naive Bayes needs smoothing (toy counts)", x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.03)
    fig.savefig(out / "o07_nb_smoothing.png"); plt.close(fig)


def bernoulli(out, day="···········HHHPEEEEEEPP··PPPPPPPEPE·····EHH·HH·"):
    """The same person-day read two ways: multinomial NB reads the seen half hours as words, Bernoulli NB reads every half hour as seen or not."""
    n = len(day)
    fig, axes = plt.subplots(2, 1, figsize=(13, 3.3), gridspec_kw={"hspace": 1.0})
    for ax in axes:
        ax.set_xlim(-0.5, n - 0.5); ax.set_ylim(-0.1, 1.1); ax.set_yticks([]); ax.grid(False)
        for s in ["left", "right", "top"]: ax.spines[s].set_visible(False)
        ticks = [i for i in range(n) if (i + 1) % 6 == 0]
        ax.set_xticks(ticks); ax.set_xticklabels([f"{(i + 1) // 2:02d}:{30 * ((i + 1) % 2):02d}" for i in ticks], fontsize=8.5)
    for i, ch in enumerate(day):
        if ch == "·": axes[0].add_patch(Rectangle((i - 0.42, 0.1), 0.84, 0.8, fc="#ffffff", ec="#e1e0d9", lw=0.8))
        else:
            axes[0].add_patch(Rectangle((i - 0.42, 0.1), 0.84, 0.8, fc=STATE_COL[ch], ec="none"))
            axes[0].text(i, 0.5, ch, ha="center", va="center", fontsize=7.5, color="#ffffff", fontweight="bold")
        seen = ch != "·"
        axes[1].add_patch(Rectangle((i - 0.42, 0.1), 0.84, 0.8, fc="#52514e" if seen else "#ffffff", ec="#c3c2b7", lw=0.8))
        axes[1].text(i, 0.5, "1" if seen else "0", ha="center", va="center", fontsize=7.5, color="#ffffff" if seen else "#898781")
    k = sum(ch != "·" for ch in day)
    axes[0].set_title(f"Multinomial NB reads the {k} seen half hours as words (H home, P daytime place, E elsewhere) and skips the {n - k} empty ones", fontsize=10.5)
    axes[1].set_title(f"Bernoulli NB reads all {n} half hours as yes or no: seen or not seen. A 0 is evidence too", fontsize=10.5)
    fig.suptitle("One person-day, two ways of reading it (person 14892, workday 58, from the linked sample)", x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.08)
    fig.savefig(out / "o08_nb_bernoulli.png"); plt.close(fig)


def tree_partition(out):
    """Two features, two classes: a depth-2 tree cuts the plane into rectangles, one question at a time."""
    rng = np.random.default_rng(7)
    X = rng.random((260, 2)); p = 0.15 + 0.55 * ((X[:, 0] > 0.6) & (X[:, 1] > 0.35)) + 0.15 * (X[:, 0] > 0.6)
    yv = rng.random(260) < p
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.3), gridspec_kw={"width_ratios": [1, 1.1]})
    ax = axes[0]
    ax.add_patch(plt.Rectangle((0.6, 0.35), 0.4, 0.65, color=C[1], alpha=0.10, lw=0))
    ax.scatter(X[~yv, 0], X[~yv, 1], s=16, color=C[0], lw=0, label="held")
    ax.scatter(X[yv, 0], X[yv, 1], s=16, color=C[1], lw=0, label="broke")
    ax.axvline(0.6, color="#0b0b0b", lw=1.5); ax.plot([0.6, 1], [0.35, 0.35], color="#0b0b0b", lw=1.5)
    ax.text(0.3, 1.02, "question 1: x1 > 0.6?", ha="center", fontsize=9)
    ax.text(0.8, 0.37, "question 2: x2 > 0.35?", ha="center", va="bottom", fontsize=9, bbox=dict(fc="#fcfcfb", ec="none", pad=1))
    ax.set(xlim=(0, 1), ylim=(0, 1.06), xlabel="feature x1", ylabel="feature x2", title="Splits cut the space into boxes")
    ax.legend(frameon=True, fontsize=9, loc="lower left", markerscale=2, facecolor="#fcfcfb", edgecolor="#e1e0d9")
    ax = axes[1]; ax.axis("off"); ax.grid(False)
    def box(x, y, txt, fc): ax.text(x, y, txt, ha="center", va="center", fontsize=9.5, bbox=dict(boxstyle="round,pad=0.5", fc=fc, ec="#c3c2b7"))
    def line(a, b, lab):
        ax.annotate("", b, a, arrowprops=dict(arrowstyle="-", color=GREY, lw=1.2))
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, lab, fontsize=8.5, color="#52514e", ha="center")
    m1 = X[:, 0] > 0.6; m2 = m1 & (X[:, 1] > 0.35)
    box(0.5, 0.88, f"x1 > 0.6?\n{len(X)} people, {yv.mean():.0%} broke", "#ffffff")
    box(0.2, 0.5, f"leaf: held\n{(~m1).sum()} people, {yv[~m1].mean():.0%} broke", "#e8f0fb")
    box(0.75, 0.5, f"x2 > 0.35?\n{m1.sum()} people, {yv[m1].mean():.0%} broke", "#ffffff")
    box(0.55, 0.1, f"leaf: held\n{(m1 & ~m2).sum()} people, {yv[m1 & ~m2].mean():.0%} broke", "#e8f0fb")
    box(0.92, 0.1, f"leaf: broke\n{m2.sum()} people, {yv[m2].mean():.0%} broke", "#fbe9e1")
    line((0.45, 0.8), (0.22, 0.58), "no"); line((0.55, 0.8), (0.73, 0.58), "yes"); line((0.72, 0.42), (0.57, 0.18), "no"); line((0.78, 0.42), (0.9, 0.18), "yes")
    ax.set(xlim=(0, 1.05), ylim=(0, 1)); ax.set_title("The same splits as a tree")
    fig.suptitle("A decision tree asks one yes or no question at a time (toy data)", x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.03)
    fig.savefig(out / "o09_tree_partition.png"); plt.close(fig)


def impurity(out, n_left=11896, b_left=1862, n_right=4873, b_right=1364):
    """Entropy and Gini against the share of people who broke, with the split worked by hand on the DecTrees tab marked."""
    e = lambda q: -(q * np.log2(q) + (1 - q) * np.log2(1 - q))
    g = lambda q: 1 - q ** 2 - (1 - q) ** 2
    left, right = b_left / n_left, b_right / n_right
    n = n_left + n_right; parent = (b_left + b_right) / n
    p = np.linspace(0.001, 0.999, 300)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axes[0]
    ax.plot(p, e(p), color=C[0], lw=2.2, label="entropy (bits)"); ax.plot(p, g(p), color=C[1], lw=2.2, label="Gini")
    for q, nm, c in [(parent, f"all {n:,} people, {parent:.1%} broke", "#0b0b0b"), (left, f"regularity at most 0.71: {left:.1%}", C[2]),
                     (right, f"regularity above 0.71: {right:.1%}", C[3])]:
        ax.scatter([q, q], [e(q), g(q)], color=c, s=40, zorder=3)
    ax.annotate(f"all {n:,} people\n{parent:.1%} broke", (parent, g(parent)), (0.30, 0.13), fontsize=8.5, color="#0b0b0b",
                arrowprops=dict(arrowstyle="-", color="#0b0b0b", lw=0.8))
    ax.annotate(f"regularity at most 0.71\n{left:.1%} broke", (left, e(left)), (0.02, 0.86), fontsize=8.5, color=C[2],
                arrowprops=dict(arrowstyle="-", color=C[2], lw=0.8))
    ax.annotate(f"regularity above 0.71\n{right:.1%} broke", (right, e(right)), (0.36, 0.62), fontsize=8.5, color="#a66f00",
                arrowprops=dict(arrowstyle="-", color=C[3], lw=0.8))
    ax.set(xlabel="share of the group that broke", ylabel="impurity", ylim=(0, 1.08), title="Pure groups score 0, a 50:50 group scores most")
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax = axes[1]
    w_e = (n_left * e(left) + n_right * e(right)) / n; w_g = (n_left * g(left) + n_right * g(right)) / n
    vals = [(e(parent), w_e, "entropy (bits)", C[0]), (g(parent), w_g, "Gini", C[1])]
    for j, (before, after, nm, c) in enumerate(vals):
        ax.bar([j * 3, j * 3 + 1], [before, after], color=[c, c], alpha=1, width=0.8)
        ax.patches[-1].set_alpha(0.45)
        ax.text(j * 3, before + 0.015, f"{before:.5f}", ha="center", fontsize=8.5, color="#52514e")
        ax.text(j * 3 + 1, after + 0.015, f"{after:.5f}", ha="center", fontsize=8.5, color="#52514e")
        ax.text(j * 3 + 0.5, max(before, after) + 0.1, f"drop {before - after:.5f}", ha="center", fontsize=9, fontweight="bold", color=c)
    ax.set_xticks([0, 1, 3, 4]); ax.set_xticklabels(["before", "after", "before", "after"]); ax.xaxis.grid(False)
    ax.text(0.5, -0.17, "entropy", ha="center", transform=ax.get_xaxis_transform(), fontsize=9.5, color=C[0])
    ax.text(3.5, -0.17, "Gini", ha="center", transform=ax.get_xaxis_transform(), fontsize=9.5, color=C[1])
    ax.set(ylim=(0, 0.9), ylabel="impurity, weighted by group size", title="The split worked by hand: information gain")
    fig.suptitle("Measuring how mixed a group is (training people of the DecTrees tab)", x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.03)
    fig.savefig(out / "o10_impurity.png"); plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="../site/src/assets/figures"); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for f in [nb_reading, smoothing, bernoulli, tree_partition, impurity]: f(out); print("saved", f.__name__)
