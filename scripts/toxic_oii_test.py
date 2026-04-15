"""
Single-hypothesis one-tailed test:
  H1: _.oii fire rate on TOXIC plant folios > non-toxic plant folios.

Toxic plants specified by user (15 Latin names). Match each to the
CSV plant-identifications entries to find folios. All other plant
folios (non-conflict) are the non-toxic group.

One-tailed Welch's t-test, bootstrap 95% CI on mean difference,
Cohen's d effect size. No batteries, no multiple hypotheses.
"""
import csv
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

sys.path.insert(0, "scripts")

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
PLANT_CSV = ROOT / "raw/research/plant-identifications.csv"

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

# User's authoritative toxic list
TOXIC_LATIN = {
    "atropa belladonna", "helleborus foetidus", "aristolochia",
    "rhododendron", "pulsatilla vulgaris", "aquilegia vulgaris",
    "delphinium", "paris quadrifolia", "actaea spicata",
    "ricinus communis", "euphorbia myrsinites", "mandragora",
    "nymphaea caerulea", "adonis vernalis", "cuscuta europaea",
}
# Loose match: also allow match on genus alone for genus-only entries
TOXIC_GENUS = {t.split()[0] for t in TOXIC_LATIN}

# Load CSV
toxic_folios = set()
nontoxic_plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        notes = (r.get("notes") or "").upper()
        if "CONFLICT" in notes: continue
        fid = r["folio"]
        lat = (r.get("latin_name") or "").strip().lower()
        common = (r.get("common_name") or "").strip().lower()
        # Match against toxic list
        is_toxic = False
        if lat:
            if lat in TOXIC_LATIN: is_toxic = True
            elif lat.split()[0] in TOXIC_GENUS and any(
                lat.startswith(tl) or tl.startswith(lat) for tl in TOXIC_LATIN
            ): is_toxic = True
            elif lat in TOXIC_GENUS: is_toxic = True
        # Specific common-name matches for genus-only user entries
        if not is_toxic:
            if "mandrake" in common: is_toxic = True
            if "casteroil" in common or "castor" in common: is_toxic = True
            if "blue nile lotus" in common: is_toxic = True
        if is_toxic:
            toxic_folios.add(fid)
        else:
            nontoxic_plant_folios.add(fid)

print("Toxic folios matched:")
# Re-scan to report which Latin names matched
toxic_records = []
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        notes = (r.get("notes") or "").upper()
        if "CONFLICT" in notes: continue
        if r["folio"] in toxic_folios:
            toxic_records.append(r)
for r in sorted(toxic_records, key=lambda x: x["folio"]):
    print(f"  {r['folio']:<8} {r.get('latin_name',''):<30} {r.get('common_name','')}")

print(f"\nToxic folios:     {len(toxic_folios)}")
print(f"Non-toxic plants: {len(nontoxic_plant_folios)}")

# Verify we got all 15 from the user list
missing = set()
matched_latins = {r.get("latin_name","").strip().lower() for r in toxic_records}
for t in TOXIC_LATIN:
    if t not in matched_latins:
        missing.add(t)
if missing:
    print(f"\nUser-list entries NOT matched in CSV: {missing}")

# Build folio -> tokens
folio_tokens = defaultdict(list)
for folio in CORPUS["folios"]:
    fid = folio["folio"]
    for line in folio["lines"]:
        folio_tokens[fid].extend(line["words"])

def oii_rate(fid):
    toks = folio_tokens[fid]
    if len(toks) < 20: return None
    hits = 0
    for w in toks:
        _, vp = split_skel_vowels(w)
        if vp == "_.oii": hits += 1
    return hits / len(toks)

toxic_rates = [r for fid in toxic_folios if (r := oii_rate(fid)) is not None]
nontoxic_rates = [r for fid in nontoxic_plant_folios if (r := oii_rate(fid)) is not None]

print(f"\nToxic folios with >=20 tokens:     {len(toxic_rates)}")
print(f"Non-toxic folios with >=20 tokens: {len(nontoxic_rates)}")

# =========================================================================
# Descriptive stats
# =========================================================================
print("\n" + "="*72)
print("  DESCRIPTIVE STATISTICS")
print("="*72)
mt = statistics.mean(toxic_rates); st = statistics.stdev(toxic_rates) if len(toxic_rates)>1 else 0
mn = statistics.mean(nontoxic_rates); sn = statistics.stdev(nontoxic_rates) if len(nontoxic_rates)>1 else 0
print(f"  Toxic:     mean _.oii rate = {mt:.5f}  sd = {st:.5f}  n = {len(toxic_rates)}")
print(f"  Non-toxic: mean _.oii rate = {mn:.5f}  sd = {sn:.5f}  n = {len(nontoxic_rates)}")
print(f"  Difference (toxic - non-toxic): {mt - mn:+.5f}")
print(f"  Ratio:                           {mt/mn if mn>0 else float('inf'):.2f}x")

# =========================================================================
# Welch's one-tailed t-test
# =========================================================================
print("\n" + "="*72)
print("  ONE-TAILED WELCH'S T-TEST: H1: toxic > non-toxic")
print("="*72)
t_stat, p_two = stats.ttest_ind(toxic_rates, nontoxic_rates, equal_var=False)
# One-tailed: since we predicted toxic > non-toxic
if t_stat > 0:
    p_one = p_two / 2
else:
    p_one = 1 - p_two / 2

# Welch-Satterthwaite df
va = statistics.variance(toxic_rates) if len(toxic_rates)>1 else 0
vb = statistics.variance(nontoxic_rates) if len(nontoxic_rates)>1 else 0
na = len(toxic_rates); nb = len(nontoxic_rates)
if va/na + vb/nb > 0:
    df = (va/na + vb/nb)**2 / (
        (va**2/(na**2*(na-1)) if na>1 else 0) +
        (vb**2/(nb**2*(nb-1)) if nb>1 else 0)
    )
else:
    df = 0

print(f"  t-statistic:          {t_stat:+.4f}")
print(f"  Welch-Satterthwaite df: {df:.2f}")
print(f"  Two-tailed p:         {p_two:.6f}")
print(f"  One-tailed p (H1):    {p_one:.6f}")

# Cohen's d (Hedges correction for small samples)
pooled_sd = ((va*(na-1) + vb*(nb-1)) / (na + nb - 2))**0.5 if na+nb>2 else 0
cohens_d = (mt - mn) / pooled_sd if pooled_sd > 0 else 0
# Hedges correction
J = 1 - 3/(4*(na+nb)-9) if na+nb > 2 else 1
g = cohens_d * J
print(f"  Cohen's d:            {cohens_d:.3f}")
print(f"  Hedges' g (corrected): {g:.3f}")

# =========================================================================
# Bootstrap 95% CI on mean difference
# =========================================================================
print("\n  BOOTSTRAP 95% CI on (toxic_mean - nontoxic_mean)")
rng = random.Random(7)
B = 10000
diffs = []
for _ in range(B):
    a = [rng.choice(toxic_rates) for _ in toxic_rates]
    b = [rng.choice(nontoxic_rates) for _ in nontoxic_rates]
    diffs.append(statistics.mean(a) - statistics.mean(b))
diffs.sort()
lo = diffs[int(B*0.025)]; hi = diffs[int(B*0.975)]
print(f"    Bootstrap mean diff:    {statistics.mean(diffs):+.5f}")
print(f"    95% CI:                 [{lo:+.5f}, {hi:+.5f}]")
print(f"    CI excludes zero:       {'YES' if (lo>0 or hi<0) else 'no'}")

# =========================================================================
# Verdict
# =========================================================================
print("\n" + "="*72)
print("  VERDICT")
print("="*72)
if p_one < 0.05 and t_stat > 0:
    print(f"  p = {p_one:.4f} < 0.05 — REJECT null in direction of H1")
    print(f"  _.oii fires more often on toxic plant folios than non-toxic.")
    print(f"  This is Brain-V's first evidence of illustration-CONTENT encoding.")
elif p_one < 0.10 and t_stat > 0:
    print(f"  p = {p_one:.4f} - marginal evidence; larger sample needed")
else:
    print(f"  p = {p_one:.4f} — fails to reject null; toxic _.oii signal not")
    print(f"  distinguishable from non-toxic at alpha=0.05.")

# Per-folio detail
print("\n  Per-toxic-folio _.oii rates:")
for fid in sorted(toxic_folios):
    r = oii_rate(fid)
    n = len(folio_tokens[fid])
    lat = next((t.get('latin_name','') for t in toxic_records if t['folio']==fid), '')
    if r is not None:
        print(f"    {fid:<8} n={n:>4}  rate = {r:.4f}   ({lat})")
    else:
        print(f"    {fid:<8} SKIPPED (<20 tokens)  ({lat})")

# Save
out = ROOT / "outputs" / "toxic_oii_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-15",
    "toxic_folios": sorted(toxic_folios),
    "toxic_n": len(toxic_rates),
    "nontoxic_n": len(nontoxic_rates),
    "toxic_mean": round(mt, 6),
    "nontoxic_mean": round(mn, 6),
    "difference": round(mt - mn, 6),
    "ratio": round(mt/mn, 3) if mn > 0 else None,
    "t_stat": round(t_stat, 4),
    "df": round(df, 2),
    "p_one_tailed": round(p_one, 6),
    "cohens_d": round(cohens_d, 3),
    "hedges_g": round(g, 3),
    "bootstrap_ci_95": [round(lo, 6), round(hi, 6)],
    "ci_excludes_zero": (lo > 0 or hi < 0),
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
