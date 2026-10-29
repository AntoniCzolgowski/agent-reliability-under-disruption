"""Data for the two Part 3 tab openers of 'Agent reliability under disruption': the alarm field on the NaiveBayes tab and the
tree the city falls through on the DecTrees tab. Reads notebook 04's outputs and writes small JSON files for the site.

Usage: python export_part3_viz.py --proc /projects/ancz7294/yjmob/data/processed --out ../site/src/data
       (the evidence can also come from notebook 06's export: --evidence exports/day_evidence_eval.csv.gz)
"""
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from breaks import cusum, alarm_onset

ORDER = ["far roamers", "mid-range movers", "regular commuters", "local regulars", "weekend movers", "homebodies"]
FIFTH = ["least regular", "2nd", "3rd", "4th", "most regular"]
K, H = 0.2, 9.96                     # the alarm of the NaiveBayes tab: allowance per day and line (5% of people on days 15-44)
CUTS = [0.7254629731178284, 0.8535533845424652, 0.6035533845424652]   # Tree 1: regularity, then commute on the low and high side
SEED = 20260917
CODE36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def evidence(proc, path):
    """Each evaluation person's daily evidence for the emergency (days as columns 0-74), as written by notebook 04."""
    if path:
        d = pd.read_csv(path).set_index("uid")
        L = d[[str(i) for i in range(75)]]; L.columns = range(75)
        return L
    L = pd.read_parquet(Path(proc) / "day_evidence_eval.parquet"); L.columns = L.columns.astype(int)
    return L


def alarm_field(proc, ev_path):
    lab = pd.read_parquet(Path(proc) / "person_breaks.parquet")
    T = pd.read_parquet(Path(proc) / "who_breaks_table.parquet")
    L = evidence(proc, ev_path)
    ev = lab[lab.split == "eval"][["kind", "broke", "alarm_day"]].join(T["regularity"]).join(L, how="inner")
    ev["fifth"] = pd.qcut(ev.regularity, 5, labels=False)
    al, _ = alarm_onset(cusum(ev[list(range(45, 75))].astype(float).fillna(0.0), K), H)
    assert (al.fillna(0) == ev.alarm_day.fillna(0)).all(), "alarm days differ from notebook 04"
    ev = ev.iloc[np.random.default_rng(SEED).permutation(len(ev))]     # a fixed mixed order inside each block
    a = al.reindex(ev.index).fillna(0).astype(int)
    out = {"note": "Evaluation people of notebook 04 in a fixed random order. kind and fifth (of regularity) as digits, broke as 0/1, "
                   "alarm as one base-36 character: 0 = never, otherwise day minus 44 (so 1 = day 45, u = day 74).",
           "k": K, "h": H, "kinds": ORDER, "fifths": FIFTH,
           "kind": "".join(str(ORDER.index(k)) for k in ev.kind), "fifth": "".join(str(int(f)) for f in ev.fifth),
           "broke": "".join(str(int(b)) for b in ev.broke), "alarm": "".join(CODE36[d - 44] if d else "0" for d in a)}
    b = ev.broke.astype(bool).to_numpy(); an = a.to_numpy()
    print(f"alarm field: {len(ev):,} people, rings for {(b & (an > 0)).sum() / b.sum():.3f} of broken routines, "
          f"caught in the emergency {(b & (an >= 60)).sum() / b.sum():.3f}, false alarms on days 45-59 {((an > 0) & (an <= 59)).mean():.3f}")
    return out


def drop_tree(proc):
    T = pd.read_parquet(Path(proc) / "who_breaks_table.parquet")
    te = T[T.split == "eval"]
    te = te.iloc[np.random.default_rng(11).permutation(len(te))]           # the order in which the beads fall
    reg, com = te.regularity.to_numpy("float32"), te.commute_km.to_numpy("float32")
    leaf = np.where(reg > CUTS[0], np.where(com > CUTS[2], 3, 2), np.where(com > CUTS[1], 1, 0))
    broke = te.broke.astype(int).to_numpy()
    # the strip under each question: people who reach it, by bins of the question's value, held and broke
    nb, cmax = 46, 120.0
    s_reg = np.minimum(nb - 1, (reg * nb).astype(int))
    s_com = np.minimum(nb - 1, (np.log1p(np.minimum(cmax, com)) / np.log1p(cmax) * nb).astype(int))
    def strip(mask, k):
        return {"held": np.bincount(k[mask & (broke == 0)], minlength=nb).tolist(), "broke": np.bincount(k[mask & (broke == 1)], minlength=nb).tolist()}
    out = {"note": "Evaluation people of notebook 04 in the order they fall. leaf 0-3 (Tree 1: regularity then commute), kind and broke as digits; "
                   "reg = regularity x 100, com = commute in km x 10, for the tooltips.",
           "cuts": CUTS, "cmax": cmax, "kinds": ORDER,
           "leaf": "".join(map(str, leaf)), "broke": "".join(map(str, broke)), "kind": "".join(str(ORDER.index(k)) for k in te.kind),
           "reg": np.round(reg * 100).astype(int).tolist(), "com": np.round(com * 10).astype(int).tolist(),
           "strips": [strip(np.ones(len(te), bool), s_reg), strip(reg <= CUTS[0], s_com), strip(reg > CUTS[0], s_com)]}
    f = leaf == 3
    print(f"drop tree: {len(te):,} people, flagged {f.sum():,}, of whom {broke[f].sum():,} broke")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--proc", default="/projects/ancz7294/yjmob/data/processed")
    ap.add_argument("--evidence", default=None)
    ap.add_argument("--out", default="../site/src/data")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "alarm_field.json").write_text(json.dumps(alarm_field(a.proc, a.evidence), separators=(",", ":")))
    (out / "drop_tree.json").write_text(json.dumps(drop_tree(a.proc), separators=(",", ":")))
