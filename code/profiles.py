"""Person profiles for 'Agent reliability under disruption', Part 2 (clustering and PCA).
One row per person per fortnight block: B1 0-14, B2 15-29, B3 30-44 (reference), B4 45-59 (ordinary test), B5 60-74 (emergency).
Anchors (home, day anchor) come from days 0-44 only. Traits are shares and rates, so fewer records do not by themselves move a
person. "At home" and "at the day anchor" mean inside the 3 x 3 block of cells around the anchor, because consecutive records of a
person who stays put often land in neighbouring 500 m cells. Behaviour traits: spread, rootedness, rhythm. Observability traits
are kept apart and held out of any fit.
Usage: python profiles.py [--root /projects/ancz7294/yjmob]
"""
import argparse, json, time
from pathlib import Path
import numpy as np, pandas as pd

BLOCK_DAYS, KM = 15, 0.5
NIGHT, MORNING, MIDDAY, EVENING, DAYTIME = (0, 9), (14, 17), (20, 31), (36, 43), (14, 43)   # half-hour slots, inclusive
MIN_DAYS, MIN_PAIRS, ANCHOR_SHARE = 5, 20, 0.05
BEHAVIOUR = ["rg_km", "cells_per_day", "entropy", "moving_share", "step_km", "extent_km",
             "home_share", "top2_share", "n_anchors",
             "morning_away", "midday_away", "evening_away", "night_share", "weekend_away_ratio", "regularity"]
OBSERVABILITY = ["records_per_day", "days_share", "span_h"]

def modal_cell(df):
    """Most visited cell per uid in df (ties broken by first occurrence)."""
    c = df.groupby(["uid", "cell"]).size().rename("n").reset_index().sort_values(["uid", "n"], ascending=[True, False])
    return c.drop_duplicates("uid").set_index("uid").cell

def anchors(an):
    """Home = modal night cell, day anchor = modal workday midday cell, both from days 0-44. People without any record in 0-44
    get anchors from all their days and anchor_fit False; they are kept in the table and left out of every fit."""
    fit = an[an.d <= 44]
    home = modal_cell(fit[fit.t.between(*NIGHT)]).reindex(fit.uid.unique())
    home = home.fillna(modal_cell(fit))                                       # no night record in 0-44: fall back to the modal cell
    day = modal_cell(fit[fit.workday & fit.t.between(*MIDDAY)])
    anc = pd.DataFrame({"home": home, "day_anchor": day.reindex(home.index), "anchor_fit": True})
    late = an[~an.uid.isin(anc.index)]
    if len(late):
        h = modal_cell(late[late.t.between(*NIGHT)]).reindex(late.uid.unique()).fillna(modal_cell(late))
        d = modal_cell(late[late.workday & late.t.between(*MIDDAY)])
        anc = pd.concat([anc, pd.DataFrame({"home": h, "day_anchor": d.reindex(h.index), "anchor_fit": False})])
    return anc.astype({"home": "int32"}).sort_index()

def profiles(an, anc):
    an = an.join(anc, on="uid")
    an["dist_home"] = np.maximum((an.x - an.home // 256).abs(), (an.y - an.home % 256).abs()).astype("int16")
    an["away"] = an.dist_home > 1                                             # outside the 3 x 3 block around home, absorbs cell jitter
    g = an.groupby(["uid", "block"], observed=True)
    out = pd.DataFrame(index=g.size().index)
    out["records"] = g.size(); out["days_obs"] = g.d.nunique()
    # spread
    keys = [an.uid, an.block]
    xy = an[["x", "y"]].astype("float64")
    sq = (xy.x - xy.x.groupby(keys, observed=True).transform("mean")) ** 2 + (xy.y - xy.y.groupby(keys, observed=True).transform("mean")) ** 2
    out["rg_km"] = np.sqrt(sq.groupby(keys, observed=True).mean()) * KM
    counts = an.groupby(["uid", "block", "cell"], observed=True).size().rename("n").reset_index()
    tot = counts.groupby(["uid", "block"], observed=True).n.transform("sum"); p = counts.n / tot
    counts["plogp"] = -p * np.log(p)
    cg = counts.groupby(["uid", "block"], observed=True)
    ncell = cg.size()
    out["cells_per_day"] = ncell / out.days_obs
    out["entropy"] = (cg.plogp.sum() / np.log(ncell.clip(lower=2))).where(ncell > 1, 0.0)
    adj = an[an.adjacent]
    out["pairs"] = adj.groupby(["uid", "block"], observed=True).size()
    out["moving_share"] = (adj.step_prev >= 1).groupby([adj.uid, adj.block], observed=True).mean()
    mv = adj[adj.step_prev >= 1]
    out["step_km"] = mv.step_prev.groupby([mv.uid, mv.block], observed=True).median() * KM
    daymax = an.groupby(["uid", "block", "d"], observed=True).dist_home.max()
    out["extent_km"] = daymax.groupby(level=["uid", "block"], observed=True).mean() * KM
    # rootedness
    out["home_share"] = 1 - g.away.mean()
    top2 = counts.sort_values(["uid", "block", "n"], ascending=[True, True, False]).groupby(["uid", "block"], observed=True).head(2)
    out["top2_share"] = top2.groupby(["uid", "block"], observed=True).n.sum() / out.records
    out["n_anchors"] = (p >= ANCHOR_SHARE).groupby([counts.uid, counts.block], observed=True).sum()
    # rhythm
    wd = an[an.workday]
    for name, band in [("morning_away", MORNING), ("midday_away", MIDDAY), ("evening_away", EVENING)]:
        s = wd[wd.t.between(*band)]
        out[name] = s.away.groupby([s.uid, s.block], observed=True).mean()
    out["night_share"] = an.t.between(*NIGHT).groupby(keys, observed=True).mean()
    dt = an[an.t.between(*DAYTIME)]
    we = dt[dt.weekend].away.groupby([dt.uid[dt.weekend], dt.block[dt.weekend]], observed=True).mean()
    wk = dt[dt.workday].away.groupby([dt.uid[dt.workday], dt.block[dt.workday]], observed=True).mean()
    out["weekend_away_ratio"] = (we / wk.clip(lower=0.02)).clip(upper=5)
    mid = wd[wd.t.between(*MIDDAY)]
    dm = mid.groupby(["uid", "block", "d", "cell"], observed=True).size().rename("n").reset_index()
    dm = dm.sort_values(["uid", "block", "d", "n"], ascending=[True, True, True, False]).drop_duplicates(["uid", "block", "d"])
    dm = dm.join(anc.day_anchor, on="uid")
    near = np.maximum((dm.cell // 256 - dm.day_anchor // 256).abs(), (dm.cell % 256 - dm.day_anchor % 256).abs()) <= 1
    out["regularity"] = near.groupby([dm.uid, dm.block], observed=True).mean()
    # observability
    out["records_per_day"] = out.records / out.days_obs
    out["days_share"] = out.days_obs / BLOCK_DAYS
    span = an.groupby(["uid", "block", "d"], observed=True).t.agg(["min", "max"])
    out["span_h"] = ((span["max"] - span["min"]) / 2).groupby(level=["uid", "block"], observed=True).mean()
    out["eligible_block"] = (out.days_obs >= MIN_DAYS) & (out.pairs >= MIN_PAIRS)
    return out.reset_index()

COLS = ["uid", "d", "t", "x", "y", "weekend", "holiday_like", "adjacent", "step_prev", "split"]

def build(an):
    an = an[COLS].copy()
    an["workday"] = ~an.weekend & ~an.holiday_like
    an["block"] = (an.d // BLOCK_DAYS).astype("int8")
    an["cell"] = (an.x.astype("int32") * 256 + an.y).astype("int32")
    anc = anchors(an)
    prof = profiles(an, anc)
    prof = prof.join(an.drop_duplicates("uid").set_index("uid").split, on="uid")
    return prof, anc

def build_chunked(path, step=5000, n=25000):
    """Same result as build() on the whole table, people in slices of `step` to keep memory flat."""
    parts = [build(pd.read_parquet(path, columns=COLS, filters=[("uid", ">=", lo), ("uid", "<", lo + step)])) for lo in range(0, n, step)]
    return pd.concat([p for p, _ in parts], ignore_index=True), pd.concat([a for _, a in parts])

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="/projects/ancz7294/yjmob"); a = ap.parse_args()
    root = Path(a.root); out = root / "data/processed"; t0 = time.time()
    prof, anc = build_chunked(out / "yjmob_analysis.parquet")
    prof.to_parquet(out / "person_blocks.parquet", index=False); anc.to_parquet(out / "person_anchors.parquet")
    log = {"rows": len(prof), "people": int(prof.uid.nunique()), "eligible_share_by_block": prof.groupby("block").eligible_block.mean().round(4).to_dict(),
           "seconds": round(time.time() - t0, 1)}
    print(json.dumps(log, indent=2))
