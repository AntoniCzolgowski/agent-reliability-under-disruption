"""When routines broke and whose broke, for 'Agent reliability under disruption', Part 3 (Naive Bayes and decision trees).
A person-day is 48 half-hour slots, each unseen or seen at home (3 x 3 block around the night anchor), at the daytime place
(3 x 3 block around the workday midday anchor) or elsewhere, with anchors from days 0-44 (profiles.py). Slot 0 (00:00) is left
out everywhere: it is thinly recorded on every emergency day, a recording artefact rather than behaviour.
"""
import numpy as np, pandas as pd
from scipy.special import gammaln

HOME, PLACE, ELSE = 1, 2, 3
STATES = ["home", "daytime place", "elsewhere"]
SLOTS = np.arange(1, 48)
MIN_SLOTS = 4

def slot_states(an, anc, uids):
    """S[person, day, slot]: 0 unseen, 1 home, 2 daytime place, 3 elsewhere, people in the order of uids."""
    a = an[["uid", "d", "t", "x", "y"]].join(anc[["home", "day_anchor"]], on="uid")
    near_home = np.maximum((a.x - a.home // 256).abs(), (a.y - a.home % 256).abs()) <= 1
    near_place = (np.maximum((a.x - a.day_anchor // 256).abs(), (a.y - a.day_anchor % 256).abs()) <= 1) & a.day_anchor.notna()
    st = np.where(near_home, HOME, np.where(near_place, PLACE, ELSE)).astype("int8")
    S = np.zeros((len(uids), 75, 48), dtype="int8")
    S[pd.Series(np.arange(len(uids)), index=uids).reindex(a.uid).to_numpy(), a.d.to_numpy(), a.t.to_numpy()] = st
    return S

def day_rows(S, uids, days, rest_day, min_slots=MIN_SLOTS):
    """Readable person-days (at least min_slots seen slots): row index i, uid, day, rest-day flag, seen slots."""
    n_seen = (S[:, :, SLOTS] > 0).sum(axis=2)
    i, d = np.nonzero(n_seen >= min_slots)
    keep = np.isin(d, days); i, d = i[keep], d[keep]
    return pd.DataFrame({"i": i, "uid": np.asarray(uids)[i], "d": d, "rest": rest_day[d], "seen": n_seen[i, d]})

def words(S, rows):
    """Multinomial NB input: each seen slot writes one word 'day type, slot, state' (2 x 47 x 3 = 282 possible words)."""
    k = S[rows.i.to_numpy(), rows.d.to_numpy()][:, SLOTS].astype("int16") - 1
    col = rows.rest.to_numpy()[:, None] * len(SLOTS) * 3 + np.arange(len(SLOTS))[None, :] * 3 + k
    W = np.zeros((len(rows), 2 * len(SLOTS) * 3), dtype="float32")
    r, c = np.nonzero(k >= 0); W[r, col[r, c]] = 1
    return W

def seen(S, rows, slots=SLOTS):
    """Bernoulli NB input: seen or not in each slot."""
    return (S[rows.i.to_numpy(), rows.d.to_numpy()][:, slots] > 0).astype("float32")

def counts(S, rows):
    """n[day type, slot, state] over the given person-days, seen slots only."""
    k = (S[rows.i.to_numpy(), rows.d.to_numpy()][:, SLOTS].astype("int16") - 1).ravel()
    rest = np.repeat(rows.rest.to_numpy().astype(int), len(SLOTS)); sl = np.tile(np.arange(len(SLOTS)), len(rows))
    n = np.zeros((2, len(SLOTS), 3)); m = k >= 0
    np.add.at(n, (rest[m], sl[m], k[m]), 1)
    return n

def person_counts(S, idx, days, rest_day):
    """n[person, day type, slot, state] for each person in idx over the given days, seen slots only."""
    n = np.zeros((len(idx), 2, len(SLOTS), 3))
    for d in days:
        k = S[idx, d][:, SLOTS].astype("int16") - 1
        r, s = np.nonzero(k >= 0)
        np.add.at(n, (r, int(rest_day[d]), s, k[r, s]), 1)
    return n

def smooth(n, a):
    """Laplace (additive) smoothing of categorical counts along the last axis."""
    return (n + a) / (n.sum(axis=-1, keepdims=True) + n.shape[-1] * a)

def shrink(n, prior, m):
    """Posterior mean under a Dirichlet(m * prior) prior: the person's counts pulled toward the prior by m pseudo-observations."""
    return (n + m * prior) / (n.sum(axis=-1, keepdims=True) + m)

def dm_loglik(n, prior, m):
    """Dirichlet-multinomial log marginal likelihood of counts n under Dirichlet(m * prior), summed over everything."""
    a = m * prior
    return float((gammaln(m) - gammaln(n.sum(axis=-1) + m) + (gammaln(n + a) - gammaln(a)).sum(axis=-1)).sum())

def best_m(n, prior, grid):
    """Empirical Bayes: the prior strength under which the observed counts are most likely."""
    ll = pd.Series({m: dm_loglik(n, prior, m) for m in grid})
    return ll.idxmax(), ll

def where_loglr(S, rows, theta_o, theta_e):
    """Evidence for 'emergency' over 'ordinary' (log-likelihood ratio, seen slots only) for each person-day. theta_* is either
    [day type, slot, state] (one model for everyone) or [person, day type, slot, state] with the person in rows.p."""
    k = S[rows.i.to_numpy(), rows.d.to_numpy()][:, SLOTS].astype("int16") - 1
    lr = np.log(theta_e) - np.log(theta_o)
    rest = rows.rest.to_numpy().astype(int); out = np.zeros(len(rows))
    p = rows.p.to_numpy() if lr.ndim == 4 else None
    for s in range(len(SLOTS)):
        m = k[:, s] >= 0
        out[m] += lr[rest[m], s, k[m, s]] if p is None else lr[p[m], rest[m], s, k[m, s]]
    return out

def surprise(S, rows, theta):
    """Total surprise (-log probability) and number of seen slots of each person-day under each person's habit model."""
    k = S[rows.i.to_numpy(), rows.d.to_numpy()][:, SLOTS].astype("int16") - 1
    rest = rows.rest.to_numpy().astype(int); p = rows.p.to_numpy()
    tot = np.zeros(len(rows)); cnt = np.zeros(len(rows))
    for s in range(len(SLOTS)):
        m = k[:, s] >= 0
        tot[m] -= np.log(theta[p[m], rest[m], s, k[m, s]]); cnt[m] += 1
    return tot, cnt

def cusum(L, k):
    """Page's CUSUM over the columns (days) of L: S = max(0, S + evidence - k)."""
    x = L.to_numpy() - k; s = np.zeros(len(x)); out = np.zeros_like(x)
    for j in range(x.shape[1]):
        s = np.maximum(0, s + x[:, j]); out[:, j] = s
    return pd.DataFrame(out, index=L.index, columns=L.columns)

def alarm_onset(C, h):
    """First day the CUSUM crosses h, and the onset: the day after it last stood at zero before the alarm."""
    hit = C.to_numpy() > h; cols = C.columns.to_numpy()
    alarm = pd.Series(np.nan, index=C.index); onset = pd.Series(np.nan, index=C.index)
    for r in np.where(hit.any(axis=1))[0]:
        f = hit[r].argmax(); z = np.where(C.iloc[r, :f + 1].to_numpy() == 0)[0]
        alarm.iloc[r] = cols[f]; onset.iloc[r] = cols[z[-1] + 1] if len(z) else cols[0]
    return alarm, onset
