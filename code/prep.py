"""Data preparation for 'Agent reliability under disruption'.
Derived from notebooks/01_first_look.ipynb (2026-09-17). Reproduces the processed tables from the raw files.
Decisions (see notebook): nothing is deleted from YJMob; records are flagged. Windows fit 0-44 / val 45-59 / fb 60-66 / tgt 67-74.
Weekly phase (corrected 2026-09-17, notebooks/02_review_and_fix.ipynb): d mod 7 on days 0-59, (d + 4) mod 7 on days 60-74, because
the weekly rhythm of the emergency block is shifted by 4 days. Phases {0, 6} are weekend-like. Days 1, 8, 29, 37, 50 and 67 sit on a
weekday phase but run like a rest day and are flagged holiday_like. The script checks this day typing against the data and stops if
it does not hold. Split 70/30 by uid, seed 20260917. Eligibility: >= 20 adjacent pairs in every window.
Flags: adjacent (gap 1 slot), big_jump (> 100 cells in 30 min), flicker_mid (middle of a one-cell A-B-A). Foursquare: exact
duplicates dropped, JST local time for all rows (tz_flag), names normalised, 500 m local grid, coarse groups from the reviewed csv.
Usage: python prep.py [--root /projects/ancz7294/yjmob]
"""
import argparse, hashlib, zipfile, json, time
from pathlib import Path
import numpy as np, pandas as pd

SEED, N_PEOPLE = 20260917, 25000
SHIFT_FROM, SHIFT = 60, 4                      # weekly phase = (d + SHIFT) mod 7 from day SHIFT_FROM on
HOLIDAY_LIKE = [1, 8, 29, 37, 50, 67]          # weekday phase, no morning peak
MD5 = {"yjmob100k-dataset2.csv.gz": "ec769fafa7a746caa3d48d2844b9735c", "cell_POIcat.csv.gz": "93af4bb0b417cd20e95fdc1d8f7b459f",
       "POI_datacategories.csv": "fd024e10c1d1dd91356d010413ace390", "foursquare/dataset_tsmc2014.zip": "a9534dc06f0495b36f216017d2f47701"}

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()

def day_table(yj):
    """One row per day: corrected weekly phase, day type and the two signals the day typing is checked against."""
    m = yj.groupby(["d", "t"]).size().unstack(fill_value=0).to_numpy() / N_PEOPLE
    dt = pd.DataFrame({"d": np.arange(len(m), dtype="int16")})
    dt["phase"] = np.where(dt.d < SHIFT_FROM, dt.d % 7, (dt.d + SHIFT) % 7).astype("int8")
    dt["weekend"] = dt.phase.isin([0, 6])
    dt["holiday_like"] = dt.d.isin(HOLIDAY_LIKE)
    dt["workday"] = ~dt.weekend & ~dt.holiday_like
    dt["emergency"] = dt.d >= 60
    dt["coverage"] = m.mean(axis=1)
    dt["morning_ratio"] = m[:, 15:17].mean(axis=1) / m[:, 20:23].mean(axis=1)      # 07:30-08:30 against 10:00-11:30
    # guard: workdays have a morning peak, weekend-like and holiday-like days do not
    wrong = dt[(dt.morning_ratio > 1) != dt.workday]
    assert wrong.empty, f"day typing does not match the data on days {wrong.d.tolist()}"
    return dt

def prep_yjmob(raw, out, log):
    yj = pd.read_csv(raw / "yjmob100k-dataset2.csv.gz", engine="pyarrow",
                     dtype={"uid": "int32", "d": "int16", "t": "int16", "x": "int16", "y": "int16"})
    assert yj.isna().sum().sum() == 0 and not yj.duplicated(["uid", "d", "t"]).any()
    key = yj.uid.astype("int64") * 10000 + yj.d.astype("int64") * 100 + yj.t
    assert key.is_monotonic_increasing, "raw file expected sorted by uid, d, t"
    log["yjmob_rows"] = len(yj)

    same = yj.uid.values[1:] == yj.uid.values[:-1]
    gap = (yj.d.values[1:].astype("int32") - yj.d.values[:-1]) * 48 + (yj.t.values[1:].astype("int32") - yj.t.values[:-1])
    x, y = yj.x.values.astype("int32"), yj.y.values.astype("int32")
    cheb = np.maximum(np.abs(x[1:] - x[:-1]), np.abs(y[1:] - y[:-1]))
    g = np.r_[gap, 0]
    trip = (yj.uid.values[2:] == yj.uid.values[:-2]) & (g[:-2] == 1) & (g[1:-1] == 1)
    back = (x[2:] == x[:-2]) & (y[2:] == y[:-2]) & ((x[1:-1] != x[:-2]) | (y[1:-1] != y[:-2]))
    one = np.maximum(np.abs(x[1:-1] - x[:-2]), np.abs(y[1:-1] - y[:-2])) == 1

    dt = day_table(yj)
    dt.to_parquet(out / "day_table.parquet", index=False)
    log["weekend_days"], log["holiday_like_days"] = dt.d[dt.weekend].tolist(), dt.d[dt.holiday_like].tolist()

    an = yj.copy()
    for c in ["phase", "weekend", "holiday_like"]: an[c] = dt[c].to_numpy()[an.d.to_numpy()]
    an["window"] = pd.cut(an.d, bins=[-1, 44, 59, 66, 74], labels=["fit", "val", "fb", "tgt"]).astype("category")
    an["slot"] = (an.d.astype("int32") * 48 + an.t).astype("int32")
    prev_same = np.r_[False, same]
    an["gap_prev"] = np.where(prev_same, np.r_[0, gap], -1).astype("int16")
    an["step_prev"] = np.where(prev_same, np.r_[0, cheb], -1).astype("int16")
    an["adjacent"] = an.gap_prev == 1
    an["big_jump"] = an.adjacent & (an.step_prev > 100)
    fl = np.zeros(len(an), bool); fl[1:-1] = trip & back & one; an["flicker_mid"] = fl

    # person table, split, eligibility
    adj = an[an.adjacent]
    ppw = adj.groupby(["uid", "window"], observed=False).size().unstack(fill_value=0)
    ppw.columns = ["fit_0_44", "val_45_59", "fb_60_66", "tgt_67_74"]
    prof = an.groupby("uid").agg(rows=("d", "size"), days=("d", "nunique"))
    prof["ncells"] = an.drop_duplicates(["uid", "x", "y"]).groupby("uid").size()
    prof["big_jumps"] = an.groupby("uid").big_jump.sum().astype("int64")
    rng = np.random.default_rng(SEED)
    dev = np.zeros(N_PEOPLE, bool); dev[rng.choice(N_PEOPLE, size=int(0.7 * N_PEOPLE), replace=False)] = True
    prof = prof.join(ppw)
    prof["split"] = np.where(dev[prof.index], "dev", "eval")
    prof["eligible"] = (ppw >= 20).all(axis=1)
    prof.to_parquet(out / "person_table.parquet")
    log["eligible_dev_share"] = float(prof.eligible[prof.split == "dev"].mean())

    an = an.join(prof[["split", "eligible"]], on="uid"); an["split"] = an.split.astype("category")
    an.to_parquet(out / "yjmob_analysis.parquet", index=False)
    log["flag_shares"] = {c: float(an[c].mean()) for c in ["adjacent", "big_jump", "flicker_mid"]}

    # cell table
    poi = pd.read_csv(raw / "cell_POIcat.csv.gz")
    wide = poi.pivot_table(index=["x", "y"], columns="POIcategory", values="POI_count", fill_value=0, aggfunc="sum")
    wide.columns = [f"cat{c}" for c in wide.columns]
    cells = yj[["x", "y"]].drop_duplicates().set_index(["x", "y"]).join(wide, how="left")
    cells["has_poi"] = cells["cat1"].notna()
    cells = cells.fillna(0).astype({c: "int32" for c in wide.columns})
    cells["poi_total"] = cells[wide.columns].sum(axis=1)
    cells.to_parquet(out / "cell_table.parquet")
    log["cells"] = len(cells)

def prep_foursquare(raw, out, code, log):
    zf = zipfile.ZipFile(raw / "foursquare/dataset_tsmc2014.zip")
    name = [n for n in zf.namelist() if "TKY" in n and n.endswith(".txt")][0]
    cols = ["user_id", "venue_id", "venue_cat_id", "venue_cat_name", "lat", "lon", "tz_offset", "utc_time"]
    fs = pd.read_csv(zf.open(name), sep="\t", header=None, names=cols, encoding="latin-1")
    log["fsq_raw_rows"] = len(fs)
    fs = fs.drop_duplicates().copy()
    fs["tz_flag"] = fs.tz_offset != 540
    utc = pd.to_datetime(fs.utc_time, format="%a %b %d %H:%M:%S %z %Y", utc=True)
    fs["local"] = (utc + pd.Timedelta(minutes=540)).dt.tz_localize(None)
    fs["venue_cat_name"] = fs.venue_cat_name.str.replace(r"\s+", " ", regex=True).str.strip()
    lat0, lon0 = fs.lat.min(), fs.lon.min()
    kx = 111.32 * np.cos(np.deg2rad(fs.lat.mean())); ky = 111.32
    fs["cx"] = ((fs.lon - lon0) * kx / 0.5).astype("int16") + 1
    fs["cy"] = ((fs.lat - lat0) * ky / 0.5).astype("int16") + 1
    fs["hour"] = fs.local.dt.hour.astype("int8"); fs["weekday"] = fs.local.dt.weekday.astype("int8")
    fs["weekend"] = fs.weekday >= 5; fs["month"] = fs.local.dt.to_period("M").astype(str)
    cmap = pd.read_csv(code / "foursquare_category_groups.csv").set_index("venue_cat_name").group
    missing = set(fs.venue_cat_name) - set(cmap.index)
    assert not missing, f"names without a group: {missing}"
    fs["group"] = fs.venue_cat_name.map(cmap)
    keep = ["user_id", "venue_id", "venue_cat_id", "venue_cat_name", "lat", "lon", "local", "tz_flag", "cx", "cy", "hour", "weekday", "weekend", "month", "group"]
    fs = fs.sort_values(["user_id", "local"]).reset_index(drop=True)[keep]
    fs.to_parquet(out / "foursquare_tky.parquet", index=False)
    log["fsq_clean_rows"] = len(fs)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="/projects/ancz7294/yjmob"); a = ap.parse_args()
    root = Path(a.root); raw, out, code = root / "data/raw", root / "data/processed", root / "code"
    out.mkdir(parents=True, exist_ok=True); t0 = time.time(); log = {}
    for rel, want in MD5.items():
        got = md5(raw / rel); assert got == want, f"md5 mismatch for {rel}: {got}"
    prep_yjmob(raw, out, log); prep_foursquare(raw, out, code, log)
    log["seconds"] = round(time.time() - t0, 1)
    (root / "logs/prep_log.json").write_text(json.dumps(log, indent=2)); print(json.dumps(log, indent=2))
