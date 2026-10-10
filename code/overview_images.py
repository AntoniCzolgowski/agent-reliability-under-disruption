"""Explanatory images for the Overview sections of the Clustering and PCA tabs. Synthetic toy data, not project data.
Usage: python overview_images.py --out ../site/src/assets/figures
"""
import argparse
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c3c2b7",
    "axes.grid": True, "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "text.color": "#0b0b0b", "axes.labelcolor": "#52514e", "xtick.color": "#898781", "ytick.color": "#898781",
    "font.family": "sans-serif", "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "figure.dpi": 110, "savefig.dpi": 150, "savefig.bbox": "tight"})
GREY = "#898781"

def kmeans_steps(out):
    rng = np.random.default_rng(4)
    X = np.vstack([rng.normal(m, 0.55, (40, 2)) for m in [(1, 1), (4, 1.4), (2.4, 4)]])
    cen = np.array([[0.4, 3.4], [1.2, 0.2], [1.6, 1.6]])
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.9), sharex=True, sharey=True); fig.subplots_adjust(left=0.01, right=0.99)
    titles = ["1. Start with k = 3 centres", "2. Assign to the nearest centre", "3. Move centres to the mean", "4. Repeat until stable"]
    hist = [cen.copy()]
    for _ in range(12):
        lab = np.argmin(((X[:, None] - cen[None]) ** 2).sum(-1), axis=1)
        cen = np.array([X[lab == j].mean(0) for j in range(3)]); hist.append(cen.copy())
    c0 = hist[0]; lab0 = np.argmin(((X[:, None] - c0[None]) ** 2).sum(-1), axis=1); c1 = hist[1]
    labF = np.argmin(((X[:, None] - hist[-1][None]) ** 2).sum(-1), axis=1)
    for i, ax in enumerate(axes):
        if i == 0: ax.scatter(X[:, 0], X[:, 1], s=14, color=GREY, lw=0)
        elif i in (1, 2): ax.scatter(X[:, 0], X[:, 1], s=14, color=[C[[0, 1, 2][l]] for l in lab0], lw=0, alpha=0.8)
        else: ax.scatter(X[:, 0], X[:, 1], s=14, color=[C[l] for l in labF], lw=0, alpha=0.8)
        if i == 2:
            for a, b in zip(c0, c1): ax.annotate("", b, a, arrowprops=dict(arrowstyle="->", color="#0b0b0b", lw=1.2))
        if i == 3:
            path = np.array(hist)
            for j in range(3): ax.plot(path[:, j, 0], path[:, j, 1], color="#0b0b0b", lw=1, ls=":")
        cc = {0: c0, 1: c0, 2: c1, 3: hist[-1]}[i]
        ax.scatter(cc[:, 0], cc[:, 1], s=130, marker="X", color=[C[0], C[1], C[2]] if i else "#0b0b0b", edgecolor="#0b0b0b", lw=1.2, zorder=5)
        ax.set_title(titles[i], fontsize=10.5); ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("How k-means finds groups", x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.04)
    fig.savefig(out / "o01_kmeans_steps.png"); plt.close(fig)

def distances(out):
    A, B, Cp = np.array([1.0, 0.6]), np.array([3.0, 1.95]), np.array([1.2, 1.5])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharex=True, sharey=True)
    for ax, kind in zip(axes, ["euclid", "cosine"]):
        for p, nm, col in [(A, "A", C[0]), (B, "B", C[0]), (Cp, "C", C[1])]:
            ax.annotate("", p, (0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=1.6))
            ax.scatter(*p, s=40, color=col, zorder=3); ax.text(p[0] + 0.07, p[1] + 0.07, nm, fontsize=12, fontweight="bold", color=col)
        if kind == "euclid":
            for q, d in [(B, np.linalg.norm(A - B)), (Cp, np.linalg.norm(A - Cp))]:
                ax.plot([A[0], q[0]], [A[1], q[1]], color="#0b0b0b", ls="--", lw=1)
                m = (A + q) / 2; ax.text(m[0] + 0.05, m[1] - 0.18, f"{d:.2f}", fontsize=10)
            ax.set_title("Euclidean: the straight line between points"); ax.text(0.05, 2.75, "A is closest to C", fontsize=10.5, color="#52514e")
        else:
            for q, col in [(B, C[0]), (Cp, C[1])]:
                ang = np.degrees(np.arccos(np.clip(A @ q / np.linalg.norm(A) / np.linalg.norm(q), -1, 1)))
                t = np.linspace(np.arctan2(A[1], A[0]), np.arctan2(q[1], q[0]), 30); rr = 0.55 if q is Cp else 0.85
                ax.plot(rr * np.cos(t), rr * np.sin(t), color=col, lw=1.2)
                nm = "B" if q is B else "C"
                ax.text(0.05, 2.45 if nm == "B" else 2.2, f"A to {nm}: {ang:.0f}°, cosine distance {1 - np.cos(np.radians(ang)):.2f}", fontsize=9.5, color=col)
            ax.set_title("Cosine: the angle between directions"); ax.text(0.05, 2.75, "A is closest to B", fontsize=10.5, color="#52514e")
        ax.set(xlim=(-0.1, 3.6), ylim=(-0.1, 3.0), xlabel="trait 1 (standardised)"); ax.set_aspect("equal")
    axes[0].set_ylabel("trait 2 (standardised)")
    fig.suptitle("The same three people, two notions of similar", x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.02)
    fig.savefig(out / "o02_euclidean_vs_cosine.png"); plt.close(fig)

def toy_dendrogram(out):
    pts = np.array([[0.0], [1.0], [4.0], [6.1], [7.4]])
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1, 1.2]})
    ax = axes[0]; ax.scatter(pts[:, 0], np.zeros(5), s=80, color=C[0], zorder=3)
    for i, p in enumerate(pts[:, 0]): ax.text(p, 0.12, f"{p:g}", ha="center", fontsize=10)
    ax.set(ylim=(-0.5, 0.6), yticks=[], xlabel="one trait"); ax.set_title("Five points on a line"); ax.yaxis.grid(False)
    L = linkage(pts, method="average")
    dendrogram(L, labels=[f"{p:g}" for p in pts[:, 0]], ax=axes[1], color_threshold=2.5, above_threshold_color=GREY)
    axes[1].axhline(2.5, color="#0b0b0b", ls="--", lw=1); axes[1].text(5.2, 2.6, "cut here: 2 groups", fontsize=9.5)
    axes[1].set(ylabel="distance at merge"); axes[1].set_title("Hierarchical clustering merges the closest pair, again and again"); axes[1].xaxis.grid(False)
    fig.savefig(out / "o03_toy_dendrogram.png"); plt.close(fig)

def pca_rotation(out):
    rng = np.random.default_rng(2)
    X = rng.multivariate_normal([0, 0], [[3.0, 1.9], [1.9, 1.7]], 400)
    Xc = X - X.mean(0); cov = np.cov(Xc.T); val, vec = np.linalg.eigh(cov); o = np.argsort(val)[::-1]; val, vec = val[o], vec[:, o]
    if vec[0, 0] < 0: vec[:, 0] *= -1
    if vec[1, 1] < 0: vec[:, 1] *= -1
    S = Xc @ vec
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    ax = axes[0]; ax.scatter(Xc[:, 0], Xc[:, 1], s=8, color=C[0], alpha=0.45, lw=0)
    for j, col in enumerate([C[1], C[2]]):
        v = vec[:, j] * 2 * np.sqrt(val[j]); ax.annotate("", v, (0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2.2))
        ax.text(v[0] * 1.08, v[1] * 1.08 + (0.25 if j == 0 else 0), f"PC{j + 1}\neigenvalue {val[j]:.2f}", color=col, fontsize=9.5, ha="center", bbox=dict(fc="#fcfcfb", ec="none", alpha=0.85, pad=1))
    ax.set(xlabel="trait 1", ylabel="trait 2", xlim=(-6, 6), ylim=(-5, 5)); ax.set_aspect("equal"); ax.set_title("Two correlated traits")
    ax = axes[1]; ax.scatter(S[:, 0], S[:, 1], s=8, color=C[0], alpha=0.45, lw=0)
    ax.axhline(0, color=C[1], lw=1.5); ax.axvline(0, color=C[2], lw=1.5)
    share = val / val.sum()
    ax.set(xlabel=f"PC1: {share[0]:.0%} of the variance", ylabel=f"PC2: {share[1]:.0%}", xlim=(-6, 6), ylim=(-5, 5)); ax.set_aspect("equal")
    ax.set_title("The same cloud on its principal axes")
    fig.suptitle("PCA rotates the data so the first axis follows the largest spread", x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.02)
    fig.savefig(out / "o04_pca_rotation.png"); plt.close(fig)

def many_dimensions(out):
    rng = np.random.default_rng(1)
    dims = [1, 2, 3, 5, 10, 15, 20, 50, 100, 200]
    ratio, shell = [], []
    for d in dims:
        X = rng.random((500, d)); r_ = []
        for q in rng.random((20, d)):
            dist = np.linalg.norm(X - q, axis=1); r_.append(dist.min() / dist.max())
        ratio.append(np.mean(r_))
        shell.append(1 - 0.9 ** d)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9))
    axes[0].plot(dims, ratio, color=C[0], marker="o", lw=2); axes[0].set_xscale("log")
    axes[0].set(xlabel="number of dimensions", ylabel="nearest / farthest distance", ylim=(0, 1.02), title="Near and far become alike")
    axes[1].plot(dims, np.array(shell) * 100, color=C[1], marker="o", lw=2); axes[1].set_xscale("log")
    axes[1].set(xlabel="number of dimensions", ylabel="% of a unit cube within 5% of its surface", ylim=(0, 102), title="Almost everything sits at the edge")
    for ax in axes: ax.set_xticks(dims); ax.set_xticklabels(dims); ax.minorticks_off()
    fig.suptitle("Why many dimensions are hard (500 random points)", x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.03)
    fig.savefig(out / "o05_many_dimensions.png"); plt.close(fig)
    return dict(zip(dims, np.round(ratio, 2)))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="."); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    kmeans_steps(out); distances(out); toy_dendrogram(out); pca_rotation(out); print(many_dimensions(out))
