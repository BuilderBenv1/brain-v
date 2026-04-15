"""
Execute pre-registered H-BV-PSYCHOACTIVE-02.

Spec LOCKED in hypotheses/H-BV-PSYCHOACTIVE-02.json (commit 85b8915):
  - Restrict to Hand A folios only
  - Comparison: Hand-A psychoactive plants (n=4) vs Hand-A non-psychoactive plants
  - One-tailed Welch's t-test, H1: psycho > non-psycho
  - Decision rules:
      p < 0.05 AND Cohen's d >= 0.4   -> confirmed
      p >= 0.10                        -> refuted
      0.05 <= p < 0.10 OR d < 0.4      -> marginal
  - Required: Mann-Whitney U, bootstrap 95% CI
"""
import csv
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from scipy import stats

sys.path.insert(0, "scripts")

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
PLANT_CSV = ROOT / "raw/research/plant-identifications.csv"

# Locked spec
PSYCHO_KEYWORDS = ["narcotic", "hallucinogenic", "soporific", "psychedelic",
                   "psychoactive", "consciousness-altering", "hypnotic",
                   "entheogen"]
ALPHA = 0.05
D_THRESHOLD = 0.4
RESTRICT_HAND = "A"

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
    if not vs:
        return "".join(cons), ""
    by_pos = defaultdict(list)
    for p,v in vs: by_pos[p].append(v)
    return "".join(cons), ".".join("".join(by_pos.get(p,[])) or "_"
                                    for p in range(max(by_pos)+1))

# Corpus index
folio_tokens = defaultdict(list)
folio_hand = {}
for folio in CORPUS["folios"]:
    fid = folio["folio"]
    folio_hand[fid] = folio.get("currier_language","?")
    for line in folio["lines"]:
        folio_tokens[fid].extend(line["words"])

def oii_rate(fid):
    toks = folio_tokens.get(fid, [])
    if len(toks) < 20: return None
    return sum(1 for w in toks if split_skel_vowels(w)[1] == "_.oii") / len(toks)

# Classify plants with psychoactive flag, then restrict to Hand A
psycho_hand_a = []
non_psycho_hand_a = []
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        notes = (r.get("notes") or "")
        if "CONFLICT" in notes.upper(): continue
        fid = r["folio"]
        if folio_hand.get(fid) != RESTRICT_HAND: continue
        text = ((r.get("medicinal_use") or "") + " " + notes).lower()
        is_psycho = any(kw in text for kw in PSYCHO_KEYWORDS)
        rec = (fid, r.get("latin_name",""), r.get("common_name",""))
        if is_psycho:
            psycho_hand_a.append(rec)
        else:
            non_psycho_hand_a.append(rec)

print(f"Locked spec: Hand={RESTRICT_HAND}, alpha={ALPHA}, d>={D_THRESHOLD}")
print(f"Psychoactive Hand-A folios:     {len(psycho_hand_a)}")
print(f"Non-psychoactive Hand-A folios: {len(non_psycho_hand_a)}")

psycho_rates = [r for fid,_,_ in psycho_hand_a if (r := oii_rate(fid)) is not None]
non_rates    = [r for fid,_,_ in non_psycho_hand_a if (r := oii_rate(fid)) is not None]
print(f"Usable (>=20 tokens): psycho={len(psycho_rates)}, non={len(non_rates)}")

print("\nPsychoactive Hand-A folios:")
for fid, lat, com in sorted(psycho_hand_a):
    r = oii_rate(fid)
    name = (lat or com).strip()[:30]
    print(f"  {fid:<8} rate={r:.4f}  {name}")

# Descriptive
mp = statistics.mean(psycho_rates); sp = statistics.stdev(psycho_rates) if len(psycho_rates)>1 else 0
mn = statistics.mean(non_rates); sn = statistics.stdev(non_rates) if len(non_rates)>1 else 0

print(f"\n{'='*72}")
print(f"  LOCKED TEST — H-BV-PSYCHOACTIVE-02")
print(f"{'='*72}")
print(f"  Psycho:    mean {mp:.5f}  sd {sp:.5f}  n={len(psycho_rates)}")
print(f"  Non-psycho: mean {mn:.5f}  sd {sn:.5f}  n={len(non_rates)}")
print(f"  Difference: {mp-mn:+.5f}   Ratio: {mp/mn if mn>0 else float('inf'):.2f}x")

# One-tailed Welch
t, p_two = stats.ttest_ind(psycho_rates, non_rates, equal_var=False)
p_one = p_two/2 if t > 0 else 1 - p_two/2

va = statistics.variance(psycho_rates) if len(psycho_rates)>1 else 0
vb = statistics.variance(non_rates) if len(non_rates)>1 else 0
na, nb = len(psycho_rates), len(non_rates)
df = ((va/na + vb/nb)**2 / (
    (va**2/(na**2*(na-1)) if na>1 else 0) +
    (vb**2/(nb**2*(nb-1)) if nb>1 else 0))) if (va/na + vb/nb) > 0 else 0

pooled_sd = ((va*(na-1) + vb*(nb-1))/(na+nb-2))**0.5 if na+nb>2 else 0
d = (mp-mn)/pooled_sd if pooled_sd > 0 else 0
J = 1 - 3/(4*(na+nb)-9) if na+nb > 2 else 1
g = d * J

print(f"\n  t = {t:+.4f}, Welch df = {df:.2f}")
print(f"  Two-tailed p = {p_two:.6f}")
print(f"  ONE-TAILED p = {p_one:.6f}")
print(f"  Cohen's d = {d:.3f}")
print(f"  Hedges' g = {g:.3f}")

# Bootstrap CI
rng = random.Random(7); B = 10000
diffs = []
for _ in range(B):
    a = [rng.choice(psycho_rates) for _ in psycho_rates]
    b = [rng.choice(non_rates) for _ in non_rates]
    diffs.append(statistics.mean(a) - statistics.mean(b))
diffs.sort()
lo, hi = diffs[int(B*0.025)], diffs[int(B*0.975)]
print(f"\n  Bootstrap 95% CI on (psycho - non): [{lo:+.5f}, {hi:+.5f}]")
print(f"  CI excludes zero: {'YES' if (lo>0 or hi<0) else 'no'}")

u, p_u = stats.mannwhitneyu(psycho_rates, non_rates, alternative="greater")
print(f"  Mann-Whitney U = {u:.1f}, one-tailed p = {p_u:.6f}")

# Pre-registered decision
print(f"\n{'='*72}")
print(f"  PRE-REGISTERED DECISION")
print(f"{'='*72}")
if p_one < ALPHA and d >= D_THRESHOLD and t > 0:
    verdict = "CONFIRMED"
    print(f"  p = {p_one:.4f} < {ALPHA} AND Cohen's d = {d:.3f} >= {D_THRESHOLD}")
    print(f"  -> HYPOTHESIS CONFIRMED within Hand A")
    print(f"  The psychoactive signal SURVIVES the Hand-A confound.")
elif p_one >= 0.10:
    verdict = "REFUTED"
    print(f"  p = {p_one:.4f} >= 0.10")
    print(f"  -> HYPOTHESIS REFUTED under pre-registered rules")
    print(f"  The H-BV-PSYCHOACTIVE-01 signal was a Hand-A artefact.")
else:
    verdict = "MARGINAL"
    print(f"  p = {p_one:.4f}  d = {d:.3f}")
    print(f"  -> MARGINAL (0.05 <= p < 0.10 OR d < 0.4)")

out = ROOT / "outputs" / "psychoactive_v2_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-PSYCHOACTIVE-02",
    "restricted_to_hand": RESTRICT_HAND,
    "psycho_n": len(psycho_rates),
    "non_n": len(non_rates),
    "psycho_mean": round(mp, 6),
    "non_mean": round(mn, 6),
    "difference": round(mp-mn, 6),
    "ratio": round(mp/mn, 3) if mn>0 else None,
    "t_stat": round(t, 4), "df": round(df, 2),
    "p_one_tailed": round(p_one, 6),
    "cohens_d": round(d, 3), "hedges_g": round(g, 3),
    "bootstrap_ci_95": [round(lo, 6), round(hi, 6)],
    "ci_excludes_zero": (lo>0 or hi<0),
    "mann_whitney_p": round(p_u, 6),
    "verdict": verdict,
    "psycho_folios": [{"folio": fid, "latin": l, "common": c, "rate": oii_rate(fid)}
                      for fid,l,c in psycho_hand_a],
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
print(f"\nVERDICT: {verdict}")
