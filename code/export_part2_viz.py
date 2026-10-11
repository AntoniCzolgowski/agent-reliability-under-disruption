"""Data for the interactive openers of the Clustering and PCA tabs.
Everything comes from the frozen objects of notebooks/03_kinds_of_movers.ipynb (data/processed/frozen_part2.joblib and the tables
it wrote). The reference rows are rebuilt the way the notebook built them and checked against person_kinds.parquet before anything
is written. Three files:
  kinds_flow.json    kind on days 0-44 against kind in every later fortnight, counts of people (Clustering opener)
  pca_people.json    the same 6,000 development people as Figure 5 of the Clustering tab: standardised traits, loadings, centres (PCA opener)
  kinds_traces.json  for each kind, three typical people (one who stayed, two who left) with their records of days 45-74 (Clustering opener)
Usage: python export_part2_viz.py [--root /projects/ancz7294/yjmob] [--out /projects/ancz7294/yjmob/exports]
"""
import argparse, json, sys, zipfile
from pathlib import Path
import numpy as np, pandas as pd, joblib

SEED = 20260917
ORDER = ["far roamers", "mid-range movers", "regular commuters", "local regulars", "weekend movers", "homebodies"]
BLOCKS = {0: "B1", 1: "B2", 2: "B3", 3: "ordinary", 4: "emergency"}
NAMES = ["PC1 range", "PC2 weekday routine", "PC3 night and weekends", "PC4 regular long day", "PC5 night anchors"]
LABELS = {"rg_km": "radius of gyration", "cells_per_day": "cells per day", "entropy": "spread over places", "moving_share": "moving share",
          "step_km": "step length", "extent_km": "daily reach", "home_share": "home share", "top2_share": "two main places",
          "n_anchors": "regular places", "morning_away": "away in the morning", "midday_away": "away at midday",
          "evening_away": "away in the evening", "night_share": "night records", "weekend_away_ratio": "weekend ratio", "regularity": "regularity"}
MIN_RPD, MIN_DAYS = 12, 0.8                      # people shown on the map are recorded often enough for a readable trace


def main(root, out):
    proc, out = Path(root) / "data/processed", Path(out)
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(Path(root) / "code"))
    from profiles import BEHAVIOUR, OBSERVABILITY
    fz = joblib.load(proc / "frozen_part2.joblib")
    scaler, pca, km, LOG, name = fz["scaler"], fz["pca"], fz["kmeans"], fz["log_traits"], fz["kind_of_label"]
    kinds = pd.read_parquet(proc / "person_kinds.parquet")
    blocks = pd.read_parquet(proc / "person_blocks_kinds.parquet")
    anc = pd.read_parquet(proc / "person_anchors.parquet")
    days = pd.read_parquet(proc / "day_table.parquet")

    # reference rows, rebuilt as in the notebook: eligible fortnights of days 0-44, at least two, every trait defined
    prof = pd.read_parquet(proc / "person_blocks.parquet")
    ok = prof[prof.eligible_block & prof.uid.map(anc.anchor_fit)]
    rb = ok[ok.block <= 2]
    ref = rb.groupby("uid")[BEHAVIOUR + OBSERVABILITY].mean()
    ref = ref[rb.groupby("uid").size() >= 2].dropna(subset=BEHAVIOUR)
    ref["split"] = prof.drop_duplicates("uid").set_index("uid").split.reindex(ref.index)
    prepare = lambda df: df[BEHAVIOUR].assign(**{c: np.log1p(df[c]) for c in LOG})
    Z = scaler.transform(prepare(ref))
    lab = pd.Series(km.predict(Z), index=ref.index).map(name)
    same = (lab == kinds.kind.reindex(ref.index)).mean()
    S = pca.transform(Z)
    dpc = np.abs(S[:, :5] - kinds[[f"pc{i}" for i in range(1, 6)]].reindex(ref.index).to_numpy()).max()
    print(f"reference rows rebuilt: {len(ref):,} people, kinds agree with person_kinds {same:.4%}, max score difference {dpc:.2e}")
    assert len(ref) == len(kinds) and same == 1 and dpc < 1e-6
    centres = {name[j]: c for j, c in enumerate(km.cluster_centers_)}
    inv = {v: k for k, v in name.items()}
    ref_dist = np.linalg.norm(Z - km.cluster_centers_[lab.map(inv).to_numpy()], axis=1)

    # 1. the flow: kind on days 0-44 (rows) against kind in each fortnight (columns), counts of people, all people
    flow = {}
    for b, nm in BLOCKS.items():
        t = pd.crosstab(blocks.ref_kind[blocks.block == b], blocks.kind[blocks.block == b]).reindex(index=ORDER, columns=ORDER, fill_value=0)
        flow[nm] = t.to_numpy().tolist()
    still = {nm: round(float(blocks[blocks.block == b].same.mean()), 4) for b, nm in BLOCKS.items()}
    by_kind = {nm: blocks[blocks.block == b].groupby("ref_kind").same.mean().reindex(ORDER).round(4).tolist() for b, nm in BLOCKS.items()}
    (out / "kinds_flow.json").write_text(json.dumps({
        "kinds": ORDER, "people": kinds.kind.value_counts().reindex(ORDER).tolist(), "people_dev": lab[ref.split == "dev"].value_counts().reindex(ORDER).tolist(),
        "fortnights": {"B1": [0, 14], "B2": [15, 29], "B3": [30, 44], "ordinary": [45, 59], "emergency": [60, 74]},
        "flow": flow, "still": still, "still_by_kind": by_kind,
        "note": "rows: kind fitted on days 0-44; columns: nearest frozen centre in that fortnight; counts of people with an eligible fortnight"}, indent=1))

    # 2. the PCA cloud: the 6,000 development people of Figure 5, standardised traits quantised to 0.02 standard deviations
    dev = ref[ref.split == "dev"]
    Zd = scaler.transform(prepare(dev))
    rng = np.random.default_rng(SEED)
    rng.choice(len(Zd), 5000, replace=False)                 # the silhouette subsample came first in the notebook, so the rng matches
    show = rng.choice(len(Zd), 6000, replace=False)
    q = np.clip(np.round(Zd[show] * 50), -300, 300).astype(int)
    (out / "pca_people.json").write_text(json.dumps({
        "traits": BEHAVIOUR, "labels": [LABELS[t] for t in BEHAVIOUR], "log_traits": LOG, "components": NAMES,
        "evr": pca.explained_variance_ratio_.round(4).tolist(), "loadings": np.round(pca.components_, 4).tolist(),
        "scaler_mean": np.round(scaler.mean_, 5).tolist(), "scaler_scale": np.round(scaler.scale_, 5).tolist(),
        "centres": {k: np.round(centres[k], 4).tolist() for k in ORDER}, "kinds": ORDER,
        "n": int(len(show)), "scale": 50, "kind": lab.loc[dev.index[show]].map(ORDER.index).tolist(), "z": q.ravel().tolist(),
        "note": "z is n x 15 row-major, divide by scale; loadings are rows of pca.components_ with PC1 and PC2 flipped as in the notebook"}, separators=(",", ":")))

    # 3. typical people for the map: per kind, the development person closest to the centre on days 0-44 who kept the kind in the
    #    ordinary fortnight and (a) kept it in the emergency, (b, c) moved to the two most common other kinds
    b4 = blocks[blocks.block == 3].set_index("uid")
    b5 = blocks[blocks.block == 4].set_index("uid")
    pool = ref[(ref.split == "dev")].index
    pool = pool[pool.isin(b4.index) & pool.isin(b5.index)]
    well = (b4.records_per_day.reindex(pool) >= MIN_RPD) & (b5.records_per_day.reindex(pool) >= MIN_RPD) & \
           (b4.days_share.reindex(pool) >= MIN_DAYS) & (b5.days_share.reindex(pool) >= MIN_DAYS)
    pool = pool[well.to_numpy()]
    dist = pd.Series(ref_dist, index=ref.index)
    picks = []
    for k in ORDER:
        cand = pool[((lab.reindex(pool) == k) & b4.same.reindex(pool).astype(bool)).to_numpy()]
        dest = pd.Series(flow["emergency"][ORDER.index(k)], index=ORDER).drop(k).sort_values(ascending=False)
        for role, to in [("stayed", k), ("left", dest.index[0]), ("left", dest.index[1])]:
            c = cand[(b5.kind.reindex(cand) == to).to_numpy()]
            if len(c) == 0: continue
            uid = int(dist.reindex(c).idxmin())
            picks.append({"uid": uid, "kind": k, "role": role, "to": to, "ordinary_kind": b4.kind[uid], "emergency_kind": b5.kind[uid],
                          "ref_distance": round(float(dist[uid]), 3), "records_per_day": [round(float(b4.records_per_day[uid]), 1), round(float(b5.records_per_day[uid]), 1)],
                          "share_same_outcome": round(float(flow["emergency"][ORDER.index(k)][ORDER.index(to)] / sum(flow["emergency"][ORDER.index(k)])), 4)})
    uids = [p["uid"] for p in picks]
    an = pd.read_parquet(proc / "yjmob_analysis.parquet", columns=["uid", "d", "t", "x", "y"], filters=[("d", ">=", 45), ("uid", "in", uids)])
    for p in picks:
        r = an[an.uid == p["uid"]].sort_values(["d", "t"])
        h, a = int(anc.home[p["uid"]]), anc.day_anchor[p["uid"]]
        p["home"] = [h // 256, h % 256]
        p["day_anchor"] = None if pd.isna(a) else [int(a) // 256, int(a) % 256]
        p["records"] = r[["d", "t", "x", "y"]].to_numpy().astype(int).tolist()
    (out / "kinds_traces.json").write_text(json.dumps({
        "kinds": ORDER, "fortnights": {"ordinary": [45, 59], "emergency": [60, 74]},
        "day_type": {int(d): ("weekend" if w else "holiday" if h else "workday") for d, w, h in zip(days.d, days.weekend, days.holiday_like) if d >= 45},
        "people": picks, "note": "records are [day, half-hour slot, x, y]; home and day anchor are [x, y] cells fixed on days 0-44"}, separators=(",", ":")))
    for p in picks: print(f"{p['kind']:18s} {p['role']:6s} -> {p['to']:18s} uid {p['uid']:6d} distance {p['ref_distance']:.2f} records {len(p['records'])}")
    files = ["kinds_flow.json", "pca_people.json", "kinds_traces.json"]
    for f in files: print(f"{f:20s} {(out / f).stat().st_size / 1e3:7.1f} KB")
    with zipfile.ZipFile(out / "part2_viz.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in files: z.write(out / f, f)
    print(f"all three in {out / 'part2_viz.zip'} ({(out / 'part2_viz.zip').stat().st_size / 1e3:.0f} KB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/projects/ancz7294/yjmob")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    main(a.root, a.out or str(Path(a.root) / "exports"))
