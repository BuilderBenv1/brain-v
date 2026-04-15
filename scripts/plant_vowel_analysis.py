"""
Plant-ID folios vs vowel patterns.

The earlier H-BV-VOWEL-CODE-01 failure used SECTION metadata as the target.
Section is coarse — all herbal folios share one label. Image-label targets
(specific plant species) may be what the vowel layer actually encodes.

Method
------
  - Load raw/research/plant-identifications.csv (20+ folios with plant IDs).
  - For each high-confidence folio (no CONFLICT), extract all tokens and
    their vowel patterns.
  - Two questions:
    Q1: Do folios identified as the SAME PLANT share characteristic
        vowel patterns? (No pairs in current data, so we check via
        plant-family clusters.)
    Q2: Do the 3 held-out-validated sparse rules (_.o._.o, _._.eee,
        _.e.ai) fire more often on plant-ID folios than on other
        herbal folios? (These rules were train-holdout split validated;
        this is a third independent signal check.)
  - Compute for each plant-ID folio:
    - total tokens
    - hits on each of the 3 sparse rules
    - vowel pattern frequency profile
    - compare to random herbal folio baseline

Honest: the plant-ID dataset is small (21 rows, 20 unique folios, 1 conflict).
This is a signal-detection exercise, not a decipherment claim.
"""
import csv
import json
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

# Sparse rules from H-BV-SPARSE-01
SPARSE_RULES = {
    "_.o._.o": "herbal",
    "_._.eee": "recipes",
    "_.e.ai":  "recipes",
}

# Load plant IDs, skip conflicts
plants = []
with PLANT_CSV.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row.get("consensus") == "CONFLICT":
            continue
        plants.append(row)

plant_folios = {r["folio"] for r in plants}
print(f"Plant-ID folios (non-conflict): {len(plant_folios)}")
for r in sorted(plants, key=lambda x: x["folio"]):
    name = r["latin_name"] or r["common_name"]
    print(f"  {r['folio']:<8} {name:<30} [{r['source']}]")

# Index corpus by folio
folio_tokens = defaultdict(list)
folio_section = {}
for folio in CORPUS["folios"]:
    fid = folio["folio"]
    folio_section[fid] = folio["section"]
    for line in folio["lines"]:
        folio_tokens[fid].extend(line["words"])

# Check which plant folios exist in corpus
matched_folios = [f for f in plant_folios if f in folio_tokens]
print(f"\nPlant folios present in corpus: {len(matched_folios)}/{len(plant_folios)}")
missing = plant_folios - set(matched_folios)
if missing:
    print(f"  Missing from EVA corpus: {sorted(missing)}")

# =========================================================================
# Q2: Do sparse rules fire on plant-ID folios?
# =========================================================================
print("\n" + "="*72)
print("  Sparse-rule fire rates on plant-ID folios vs baseline")
print("="*72)

def rule_hits(tokens):
    hits = {r: 0 for r in SPARSE_RULES}
    for w in tokens:
        _, vp = split_skel_vowels(w)
        if vp in SPARSE_RULES:
            hits[vp] += 1
    total_hits = sum(hits.values())
    return hits, total_hits, total_hits / len(tokens) if tokens else 0

# Per plant-ID folio
print(f"\n  {'folio':<8} {'plant':<25} {'section':<10} {'n tok':>6} "
      f"{'_.o._.o':>9} {'_._.eee':>9} {'_.e.ai':>8} {'total':>6} {'rate':>6}")
plant_rates = []
for r in sorted(plants, key=lambda x: x["folio"]):
    fid = r["folio"]
    if fid not in folio_tokens: continue
    toks = folio_tokens[fid]
    hits, total, rate = rule_hits(toks)
    name = (r["latin_name"] or r["common_name"])[:24]
    sec = folio_section.get(fid, "?")[:9]
    print(f"  {fid:<8} {name:<25} {sec:<10} {len(toks):>6} "
          f"{hits['_.o._.o']:>9} {hits['_._.eee']:>9} {hits['_.e.ai']:>8} "
          f"{total:>6} {rate:>5.1%}")
    plant_rates.append(rate)

# Baseline: all non-plant-ID folios in the herbal section
herbal_baseline_folios = [f for f, s in folio_section.items()
                          if s == "herbal" and f not in plant_folios]
baseline_rates = []
for fid in herbal_baseline_folios:
    toks = folio_tokens[fid]
    if len(toks) < 20: continue
    _, _, r = rule_hits(toks)
    baseline_rates.append(r)

import statistics
mp = statistics.mean(plant_rates) if plant_rates else 0
sp = statistics.pstdev(plant_rates) if plant_rates else 0
mb = statistics.mean(baseline_rates) if baseline_rates else 0
sb = statistics.pstdev(baseline_rates) if baseline_rates else 0
print(f"\n  Plant-ID folios:    n={len(plant_rates):>3}  mean rate = {mp:.2%}  sigma = {sp:.2%}")
print(f"  Other herbal folios: n={len(baseline_rates):>3}  mean rate = {mb:.2%}  sigma = {sb:.2%}")
if sb > 0:
    z = (mp - mb) / (sb / max(1, len(plant_rates))**0.5)
    print(f"  z = {z:.2f}")

# =========================================================================
# Q3: Top vowel patterns on plant-ID folios
# =========================================================================
print("\n" + "="*72)
print("  Top vowel patterns concentrated on plant-ID folios")
print("="*72)

plant_vp = Counter()
plant_total = 0
for r in plants:
    fid = r["folio"]
    if fid not in folio_tokens: continue
    for w in folio_tokens[fid]:
        _, vp = split_skel_vowels(w)
        plant_vp[vp] += 1
        plant_total += 1

baseline_vp = Counter()
baseline_total = 0
for fid in herbal_baseline_folios:
    for w in folio_tokens[fid]:
        _, vp = split_skel_vowels(w)
        baseline_vp[vp] += 1
        baseline_total += 1

# Enrichment
print(f"  {'vowel_pattern':<16} {'plant%':>8} {'baseline%':>10} {'enr':>6} "
      f"{'n_plant':>8}")
rows = []
for vp, n in plant_vp.most_common():
    if n < 5: continue
    p_rate = n / plant_total
    b_rate = baseline_vp[vp] / baseline_total if baseline_total else 0
    if b_rate == 0: continue
    enr = p_rate / b_rate
    rows.append((vp, p_rate, b_rate, enr, n))
rows.sort(key=lambda r: -r[3])
for vp, p, b, enr, n in rows[:15]:
    print(f"  {vp:<16} {p*100:>7.2f}% {b*100:>9.2f}% {enr:>5.2f}x {n:>8}")

# =========================================================================
# Q4: Each plant folio — its TOP 3 distinct vowel patterns (signature)
# =========================================================================
print("\n" + "="*72)
print("  Per-folio vowel-pattern signature (top 3 patterns)")
print("="*72)
for r in sorted(plants, key=lambda x: x["folio"]):
    fid = r["folio"]
    if fid not in folio_tokens: continue
    vps = Counter()
    for w in folio_tokens[fid]:
        _, vp = split_skel_vowels(w)
        vps[vp] += 1
    top3 = vps.most_common(3)
    sig = ", ".join(f"{vp}:{n}" for vp, n in top3)
    name = (r["latin_name"] or r["common_name"])[:20]
    print(f"  {fid:<8} {name:<22} [{sig}]")

# Save
out = ROOT / "outputs" / "plant_vowel_analysis.json"
out.write_text(json.dumps({
    "generated": "2026-04-15",
    "plant_folios_in_corpus": len(matched_folios),
    "plant_folios_missing": sorted(missing),
    "sparse_rule_plant_rate": round(mp, 4),
    "sparse_rule_baseline_rate": round(mb, 4),
    "top_enriched_patterns_on_plant_folios": [
        {"vp": vp, "plant_rate": round(p, 4),
         "baseline_rate": round(b, 4), "enrichment": round(e, 2), "n": n}
        for vp, p, b, e, n in rows[:15]
    ],
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
