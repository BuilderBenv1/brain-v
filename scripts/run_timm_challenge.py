"""
Execute pre-registered H-BV-TIMM-CHALLENGE-01.

Spec LOCKED in commit c90b171:
  For each of 8 markers/marker-sets, fit three linear regressions on
  per-folio fire rate:
    (a) rate ~ hand           (binary: 0 for A, 1 for B)
    (b) rate ~ quire_position (numeric)
    (c) rate ~ hand + quire_position

  Markers:
    1. _.oii                  (Hand-A plant marker)
    2. _.e.e                  (Hand-B plant marker)
    3. _.eeo                  (Hand-B plant marker)
    4. _.o.eo                 (Hand-B plant marker)
    5. HandA_pharma combined  (_.o.eo, o.eo, o.eeo, _.oo, o.ee, _.eeo)
    6. HandA_herbal combined  (_.o._.o, _._._.o, _._.o, _._.o.o, _.eaii)
    7. HandB_biological       (o._.ai)
    8. HandB_recipes combined (oai, ai.o, o.ea, o._.eeo, o.eeo, _.eo.ai,
                                 o.ee.a, _.o.eeo)

  Decision rule:
    quire R^2 >= hand R^2 for >=5 of 8 markers  -> Timm prevails
    hand R^2 > quire R^2 for >=5 of 8           -> Brain-V prevails
    combined substantially > either for >=5     -> both partial

  Quire position: use ordering given by the minimum-numeric folio id
  within each quire, ranked 1..N.

Sample restricted to folios with a defined Currier hand (A or B) and
>= 20 tokens.
"""
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from scipy import stats
import numpy as np

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
VOWELS = set("aoei")

def split_skel_vowels(word):
    if word and word[0] in "tp" and (len(word)==1 or word[1]!="h"):
        word = word[1:]
    cons=[]; vs=[]; pos=0; i=0
    while i<len(word):
        matched=False
        for ev,sy in EVA_MAP:
            if word.startswith(ev,i):
                cons.append(sy); pos+=1; i+=len(ev); matched=True; break
        if not matched:
            if word[i] in VOWELS: vs.append((pos, word[i]))
            i+=1
    if not vs: return "".join(cons), ""
    by_pos = defaultdict(list)
    for p,v in vs: by_pos[p].append(v)
    return "".join(cons), ".".join("".join(by_pos.get(p,[])) or "_"
                                    for p in range(max(by_pos)+1))

# Folio metadata + tokens
folio_meta = {}
folio_tokens = defaultdict(list)
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_meta[fid] = {"quire": f["quire"],
                       "hand": f.get("currier_language","?"),
                       "section": f["section"],
                       "word_count": f["word_count"]}
    for line in f["lines"]:
        folio_tokens[fid].extend(line["words"])

# Order quires by the minimum numeric folio id they contain
def folio_num(fid):
    m = re.match(r"f(\d+)", fid)
    return int(m.group(1)) if m else 9999

quire_min_folio = defaultdict(lambda: 9999)
for fid, m in folio_meta.items():
    q = m["quire"]
    quire_min_folio[q] = min(quire_min_folio[q], folio_num(fid))

sorted_quires = [q for q,_ in sorted(quire_min_folio.items(), key=lambda x: x[1])]
quire_rank = {q: i+1 for i, q in enumerate(sorted_quires)}
print("Quire ordering (by first folio):")
for q in sorted_quires:
    print(f"  {q} -> rank {quire_rank[q]}  (starts at f{quire_min_folio[q]})")

# Filter: Currier A/B only, >=20 tokens
def hand_code(h):
    if h == "A": return 0
    if h == "B": return 1
    return None

samples = []
for fid, m in folio_meta.items():
    h = hand_code(m["hand"])
    if h is None: continue
    if m["word_count"] < 20: continue
    toks = folio_tokens[fid]
    if not toks: continue
    samples.append({"folio": fid, "hand": h,
                    "quire": quire_rank[m["quire"]],
                    "tokens": toks,
                    "n_tokens": len(toks)})
print(f"\nUsable folios (hand in A/B, >=20 tokens): {len(samples)}")

# Marker sets
MARKERS = [
    ("_.oii",               {"_.oii"}),
    ("_.e.e",               {"_.e.e"}),
    ("_.eeo",               {"_.eeo"}),
    ("_.o.eo",              {"_.o.eo"}),
    ("HandA_pharma",        {"_.o.eo", "o.eo", "o.eeo", "_.oo", "o.ee", "_.eeo"}),
    ("HandA_herbal",        {"_.o._.o", "_._._.o", "_._.o", "_._.o.o", "_.eaii"}),
    ("HandB_biological",    {"o._.ai"}),
    ("HandB_recipes",       {"oai", "ai.o", "o.ea", "o._.eeo", "o.eeo",
                             "_.eo.ai", "o.ee.a", "_.o.eeo"}),
]

def folio_rate(toks, patterns):
    if not toks: return 0.0
    return sum(1 for w in toks
               if split_skel_vowels(w)[1] in patterns) / len(toks)

# Compute rates
for s in samples:
    s["rates"] = {name: folio_rate(s["tokens"], pats)
                  for name, pats in MARKERS}

def r_squared(y, y_pred):
    y_mean = np.mean(y)
    ss_tot = np.sum((y - y_mean)**2)
    ss_res = np.sum((y - y_pred)**2)
    return 1 - ss_res/ss_tot if ss_tot > 0 else 0

def lin_fit(X, y):
    """Fit y = X @ b via least squares; X should include a constant column."""
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_pred = X @ b
    r2 = r_squared(y, y_pred)
    # Compute p-values for each non-intercept coefficient
    n, k = X.shape
    if n <= k: return b, r2, [None]*k
    residuals = y - y_pred
    rss = np.sum(residuals**2)
    sigma2 = rss / (n - k)
    try:
        cov = sigma2 * np.linalg.inv(X.T @ X)
        se = np.sqrt(np.diag(cov))
        t_vals = b / se
        p_vals = [2*(1 - stats.t.cdf(abs(t), n-k)) for t in t_vals]
    except np.linalg.LinAlgError:
        p_vals = [None]*k
    return b, r2, p_vals

print("\n" + "="*96)
print(f"  {'marker':<20} {'hand_R2':>8} {'quire_R2':>9} {'both_R2':>8} "
      f"{'both>either':>12} {'hand_p':>8} {'quire_p':>8}")
print("="*96)

results = []
for name, pats in MARKERS:
    y = np.array([s["rates"][name] for s in samples])
    hand = np.array([s["hand"] for s in samples], dtype=float)
    quire = np.array([s["quire"] for s in samples], dtype=float)
    intercept = np.ones_like(y)

    X_hand  = np.column_stack([intercept, hand])
    X_quire = np.column_stack([intercept, quire])
    X_both  = np.column_stack([intercept, hand, quire])

    b_h, r2_h, p_h = lin_fit(X_hand, y)
    b_q, r2_q, p_q = lin_fit(X_quire, y)
    b_c, r2_c, p_c = lin_fit(X_both, y)

    better_combined = (r2_c > r2_h + 0.02) and (r2_c > r2_q + 0.02)
    # p-values in combined model: intercept, hand, quire
    hand_p_combined = p_c[1] if p_c[1] is not None else float("nan")
    quire_p_combined = p_c[2] if p_c[2] is not None else float("nan")

    results.append({
        "marker": name, "r2_hand": r2_h, "r2_quire": r2_q, "r2_both": r2_c,
        "hand_coef_combined": b_c[1], "quire_coef_combined": b_c[2],
        "hand_p_combined": hand_p_combined,
        "quire_p_combined": quire_p_combined,
        "better_combined": better_combined,
    })
    print(f"  {name:<20} {r2_h:>8.4f} {r2_q:>9.4f} {r2_c:>8.4f} "
          f"{str(better_combined):>12} {hand_p_combined:>8.3g} {quire_p_combined:>8.3g}")

# =========================================================================
# Apply pre-registered decision rule
# =========================================================================
print("\n" + "="*72)
print("  PRE-REGISTERED DECISION")
print("="*72)

quire_wins = sum(1 for r in results if r["r2_quire"] >= r["r2_hand"])
hand_wins  = sum(1 for r in results if r["r2_hand"] > r["r2_quire"])
combined_substantially_better = sum(1 for r in results if r["better_combined"])

n_markers = len(results)
majority = n_markers // 2 + 1
print(f"  Markers tested: {n_markers}")
print(f"  Majority threshold: {majority}")
print(f"  Quire >= hand: {quire_wins}/{n_markers}")
print(f"  Hand > quire:  {hand_wins}/{n_markers}")
print(f"  Combined substantially > either: {combined_substantially_better}/{n_markers}")

if quire_wins >= majority:
    verdict = "TIMM_PREVAILS"
    print(f"\n  -> TIMM'S CONTINUOUS-EVOLUTION FRAMING PREVAILS")
    print(f"     Quire position explains >= hand for {quire_wins}/{n_markers} markers.")
    print(f"     Brain-V's two-scribe framing is REFUTED under locked rule.")
elif hand_wins >= majority:
    verdict = "BRAINV_PREVAILS"
    print(f"\n  -> BRAIN-V'S TWO-SCRIBE FRAMING PREVAILS")
    print(f"     Hand explains more variance than quire for {hand_wins}/{n_markers} markers.")
elif combined_substantially_better >= majority:
    verdict = "BOTH_PARTIAL"
    print(f"\n  -> BOTH PARTIALLY TRUE")
    print(f"     Combined model substantially better for {combined_substantially_better}/{n_markers}.")
    print(f"     Hand and quire each explain distinct variance components.")
else:
    verdict = "MIXED"
    print(f"\n  -> MIXED / INCONCLUSIVE")
    print(f"     No majority criterion met.")

# =========================================================================
# Detail per-marker
# =========================================================================
print("\n" + "="*72)
print("  DETAIL — coefficients and significance (combined model)")
print("="*72)
print(f"  {'marker':<20} {'hand_coef':>10} {'hand_p':>10} "
      f"{'quire_coef':>12} {'quire_p':>10}")
for r in results:
    print(f"  {r['marker']:<20} {r['hand_coef_combined']:>10.5f} "
          f"{r['hand_p_combined']:>10.3g} "
          f"{r['quire_coef_combined']:>12.6f} "
          f"{r['quire_p_combined']:>10.3g}")

# Save
out = ROOT / "outputs" / "timm_challenge.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-TIMM-CHALLENGE-01",
    "pre_registered_in_commit": "c90b171",
    "n_folios": len(samples),
    "markers_tested": n_markers,
    "quire_ordering": {q: quire_rank[q] for q in sorted_quires},
    "results": [
        {k: (float(v) if hasattr(v,'item') or isinstance(v, float) else v)
         for k, v in r.items()}
        for r in results
    ],
    "quire_wins": quire_wins,
    "hand_wins": hand_wins,
    "combined_substantially_better": combined_substantially_better,
    "majority_threshold": majority,
    "verdict": verdict,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out}")
print(f"\nVERDICT: {verdict}")
