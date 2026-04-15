"""
Plant-ID vowel analysis v2 — 120-entry dataset, with held-out validation
of the three candidate patterns from v1.

v1 candidates (enrichment vs other herbal folios):
    _.oii   3.71x   13 hits
    o._.o   2.17x   26 hits
    _._.eo  1.69x   15 hits

With a ~6x larger plant-ID dataset, held-out validation is feasible.

Method
------
  - Load plant-identifications.csv (120 rows), filter out CONFLICT rows
  - For each candidate pattern, compute:
      a) enrichment on full plant-ID set vs non-plant herbal baseline
      b) 5-fold cross-validation over plant folios: for each fold,
         compute enrichment on the HELD-OUT plant folios using rules
         derived from the other 4 folds' plant folios (constant here —
         we're testing 3 fixed patterns, not rediscovering them).
         Fold stability = fraction of folds where enrichment >= 1.5x.
      c) folio-level Wilcoxon-style comparison: % of plant folios
         with higher rate than the median non-plant herbal folio.
  - Report enrichment, z-score, holdout stability for each pattern.
"""
import csv
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

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
    if word and word[0] in "tp" and (len(word) == 1 or word[1] != "h"):
        word = word[1:]
    cons = []; vs = []; pos = 0; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                cons.append(sy); pos += 1; i += len(ev); matched = True; break
        if not matched:
            if word[i] in VOWELS: vs.append((pos, word[i]))
            i += 1
    if not vs:
        return "".join(cons), ""
    by_pos = defaultdict(list)
    for p, v in vs: by_pos[p].append(v)
    return "".join(cons), ".".join("".join(by_pos.get(p, [])) or "_"
                                    for p in range(max(by_pos) + 1))

# Load plant IDs
plants = []
conflict_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        notes = (row.get("notes") or "").upper()
        if "CONFLICT" in notes:
            conflict_folios.add(row["folio"])
            continue
        plants.append(row)

plant_folios = {r["folio"] for r in plants}
print(f"Plant-ID dataset (v2): {len(plants)} rows, {len(plant_folios)} unique folios")
print(f"Conflicts excluded: {len(conflict_folios)} folios: {sorted(conflict_folios)}")

# Index corpus
folio_tokens = defaultdict(list)
folio_section = {}
for folio in CORPUS["folios"]:
    fid = folio["folio"]
    folio_section[fid] = folio["section"]
    for line in folio["lines"]:
        folio_tokens[fid].extend(line["words"])

matched = [f for f in plant_folios if f in folio_tokens]
missing = sorted(plant_folios - set(matched))
print(f"Plant folios in EVA corpus: {len(matched)}/{len(plant_folios)}")
if missing: print(f"  Missing: {missing[:10]}{'...' if len(missing)>10 else ''}")

# =========================================================================
# Candidate patterns from v1
# =========================================================================
CANDIDATES = ["_.oii", "o._.o", "_._.eo"]

# Folio-level rate for a given pattern
def folio_rate(fid, vp_target):
    toks = folio_tokens[fid]
    if not toks: return 0.0
    hits = 0
    for w in toks:
        _, vp = split_skel_vowels(w)
        if vp == vp_target: hits += 1
    return hits / len(toks)

# Baseline folios: herbal-section folios that are NOT plant-ID or conflict
baseline_folios = [f for f, s in folio_section.items()
                   if s == "herbal"
                   and f not in plant_folios
                   and f not in conflict_folios
                   and len(folio_tokens[f]) >= 20]
plant_folios_usable = [f for f in matched if len(folio_tokens[f]) >= 20]
print(f"\nPlant-ID folios (>=20 tokens): {len(plant_folios_usable)}")
print(f"Baseline herbal folios:       {len(baseline_folios)}")

# =========================================================================
# A. Full-dataset enrichment + folio-level Wilcoxon
# =========================================================================
print("\n" + "="*72)
print("  FULL-DATASET ENRICHMENT (plant-ID vs baseline herbal)")
print("="*72)
print(f"  {'pattern':<10} {'plant%':>8} {'base%':>8} {'enr':>6} "
      f"{'z':>6} {'plant>med':>10}")

results = []
for vp in CANDIDATES:
    plant_rates = [folio_rate(f, vp) for f in plant_folios_usable]
    base_rates  = [folio_rate(f, vp) for f in baseline_folios]

    # Aggregate token rate
    plant_tok_total = sum(len(folio_tokens[f]) for f in plant_folios_usable)
    base_tok_total  = sum(len(folio_tokens[f]) for f in baseline_folios)
    plant_hits = sum(folio_rate(f, vp) * len(folio_tokens[f]) for f in plant_folios_usable)
    base_hits  = sum(folio_rate(f, vp) * len(folio_tokens[f]) for f in baseline_folios)
    plant_pct = plant_hits / plant_tok_total if plant_tok_total else 0
    base_pct  = base_hits  / base_tok_total  if base_tok_total else 0
    enr = plant_pct / base_pct if base_pct else float("inf")

    # Folio-level z-score
    mp = statistics.mean(plant_rates) if plant_rates else 0
    mb = statistics.mean(base_rates)  if base_rates  else 0
    sb = statistics.pstdev(base_rates) if base_rates else 0
    z = (mp - mb) / (sb / math.sqrt(max(1, len(plant_rates)))) if sb > 0 else 0

    # Plant folios above baseline median
    if base_rates:
        base_med = statistics.median(base_rates)
        above = sum(1 for r in plant_rates if r > base_med)
        above_pct = above / len(plant_rates)
    else:
        above_pct = 0

    results.append({
        "pattern": vp,
        "plant_pct": round(plant_pct, 5),
        "base_pct":  round(base_pct, 5),
        "enrichment": round(enr, 2),
        "z": round(z, 2),
        "plant_above_base_median": round(above_pct, 3),
        "plant_hits": int(plant_hits),
        "plant_rates": plant_rates,
        "base_rates": base_rates,
    })
    print(f"  {vp:<10} {plant_pct*100:>7.3f}% {base_pct*100:>7.3f}% "
          f"{enr:>5.2f}x {z:>6.2f} {above_pct:>9.1%}")

# =========================================================================
# B. 5-fold cross-validation: each fold measures enrichment on held-out
#    plant folios vs same fixed baseline.  Stability = fraction of folds
#    where enrichment >= 1.5x AND > baseline.
# =========================================================================
print("\n" + "="*72)
print("  5-FOLD HELD-OUT STABILITY of candidate patterns")
print("="*72)
random.seed(42)
shuffled_plants = plant_folios_usable[:]
random.shuffle(shuffled_plants)
K = 5
fold_size = max(1, len(shuffled_plants) // K)
folds = [shuffled_plants[i*fold_size:(i+1)*fold_size] for i in range(K-1)]
folds.append(shuffled_plants[(K-1)*fold_size:])

base_total_tokens = sum(len(folio_tokens[f]) for f in baseline_folios)
base_hits_cache = {}
for vp in CANDIDATES:
    base_hits_cache[vp] = sum(
        folio_rate(f, vp) * len(folio_tokens[f]) for f in baseline_folios
    )

print(f"  {'pattern':<10} " + "  ".join(f"fold{i+1}" for i in range(K)) +
      "   mean     stable")
for vp in CANDIDATES:
    fold_enrs = []
    for fold in folds:
        tok_total = sum(len(folio_tokens[f]) for f in fold)
        if tok_total == 0:
            fold_enrs.append(0); continue
        hits = sum(folio_rate(f, vp) * len(folio_tokens[f]) for f in fold)
        p_rate = hits / tok_total
        b_rate = base_hits_cache[vp] / base_total_tokens
        fold_enrs.append(p_rate / b_rate if b_rate else 0)
    stable = sum(1 for e in fold_enrs if e >= 1.5) / K
    fold_str = "  ".join(f"{e:>5.2f}" for e in fold_enrs)
    print(f"  {vp:<10} {fold_str}  {statistics.mean(fold_enrs):>5.2f}  "
          f"{stable*100:>5.0f}%")

# =========================================================================
# C. Re-discover TOP enriched patterns on the expanded dataset.
#    Purpose: do NEW candidates emerge with the 6x larger plant set?
# =========================================================================
print("\n" + "="*72)
print("  RE-DISCOVERY: top enriched vowel patterns on expanded plant-ID set")
print("="*72)
plant_vp = Counter(); plant_total = 0
for f in plant_folios_usable:
    for w in folio_tokens[f]:
        _, vp = split_skel_vowels(w)
        plant_vp[vp] += 1; plant_total += 1
base_vp = Counter(); base_total = 0
for f in baseline_folios:
    for w in folio_tokens[f]:
        _, vp = split_skel_vowels(w)
        base_vp[vp] += 1; base_total += 1

all_enr = []
for vp, n in plant_vp.items():
    if n < 20: continue
    p = n / plant_total
    b = base_vp[vp] / base_total if base_total else 0
    if b == 0: continue
    all_enr.append((vp, p, b, p/b, n))
all_enr.sort(key=lambda r: -r[3])

print(f"  {'pattern':<16} {'plant%':>8} {'base%':>8} {'enr':>6} {'n':>5}")
for vp, p, b, e, n in all_enr[:15]:
    print(f"  {vp:<16} {p*100:>7.3f}% {b*100:>7.3f}% {e:>5.2f}x {n:>5}")

# Save
out = ROOT / "outputs" / "plant_vowel_analysis_v2.json"
out.write_text(json.dumps({
    "generated": "2026-04-15",
    "dataset": {"rows": len(plants), "unique_folios": len(plant_folios),
                "in_corpus": len(matched),
                "conflicts_excluded": sorted(conflict_folios)},
    "baseline_folios": len(baseline_folios),
    "candidates_full_dataset": [
        {k: v for k, v in r.items() if k not in ("plant_rates","base_rates")}
        for r in results
    ],
    "top_enriched_patterns": [
        {"pattern": vp, "plant_pct": round(p,5),
         "base_pct": round(b,5), "enrichment": round(e,2), "n": n}
        for vp, p, b, e, n in all_enr[:15]
    ],
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
