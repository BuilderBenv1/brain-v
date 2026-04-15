"""
Richer volvelle: per-section cartridges drawn from CORPUS-derived roots.

Fix for H-BV-VOLVELLE-OII-01's caveat. The previous volvelle generated
roots from an alternating C-V template that cannot produce 'oii' vowel
clusters. The richer volvelle below uses roots drawn from the REAL
Voynich's word-interior substrings — matching corpus vowel-cluster
statistics exactly — and therefore CAN produce _.oii.

The fair test:
  Does per-section cartridge swap ALONE, with corpus-realistic roots,
  concentrate _.oii on the specific 115 plant-ID folios enough to
  produce the 5.04x enrichment observed in real Voynich?

Method
------
  1. Strip canonical prefixes {q, qo, o, d, ch} and canonical suffixes
     {y, n, r, l, in, ain, aiin} from every real-corpus word to build
     the ROOT POOL. This captures real-Voynich root statistics including
     vowel clusters.
  2. For each section, draw a 26-root random cartridge from the pool.
  3. Generate synthetic corpus: each token = prefix (Ring A, 6) + root
     (Ring B, 26 per section) + suffix (Ring C, 8) with Currier-aware
     suffix weighting.
  4. Verify: synthetic _.oii aggregate rate matches real aggregate rate
     (sanity check - if not, roots aren't rich enough).
  5. Null test: 200 independent synthetic corpora; measure _.oii
     enrichment on plant folios vs non-plant herbal folios.
  6. Compare real 5.04x to this null distribution.
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

def oii_rate(tokens):
    if not tokens: return 0.0
    return sum(1 for w in tokens if split_skel_vowels(w)[1] == "_.oii") / len(tokens)

# =========================================================================
# Build root pool from real corpus
# =========================================================================
PREFIXES = ["qo", "q", "ch", "sh", "o", "d"]  # longest-first
SUFFIXES = ["aiin", "ain", "in", "y", "n", "r", "l"]

def strip_affixes(word):
    w = word
    for p in PREFIXES:
        if w.startswith(p) and len(w) > len(p) + 1:
            w = w[len(p):]; break
    for s in SUFFIXES:
        if w.endswith(s) and len(w) > len(s) + 1:
            w = w[:-len(s)]; break
    return w

all_real_tokens = []
for folio in CORPUS["folios"]:
    for line in folio["lines"]:
        all_real_tokens.extend(line["words"])

root_pool_counter = Counter()
for w in all_real_tokens:
    r = strip_affixes(w)
    if 2 <= len(r) <= 6:
        root_pool_counter[r] += 1

# Weighted pool
root_types = list(root_pool_counter.keys())
root_weights = [root_pool_counter[r] for r in root_types]
print(f"Root pool: {len(root_types)} unique roots, "
      f"{sum(root_weights)} total occurrences")
# Sanity: does pool include _.oii-producing roots?
oii_roots = [r for r in root_types if split_skel_vowels(r)[1] == "_.oii"]
print(f"Roots that produce _.oii pattern: {len(oii_roots)} (e.g. "
      f"{', '.join(oii_roots[:5])})")

# =========================================================================
# Plant-folio and baseline sets
# =========================================================================
plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        notes = (r.get("notes") or "").upper()
        if "CONFLICT" in notes: continue
        plant_folios.add(r["folio"])

folio_section = {f["folio"]: f["section"] for f in CORPUS["folios"]}
folio_line_sizes = {
    f["folio"]: [len(line["words"]) for line in f["lines"]]
    for f in CORPUS["folios"]
}
folio_currier = {f["folio"]: f.get("currier_language","?") for f in CORPUS["folios"]}

plant_folios_usable = [f for f in plant_folios
                       if f in folio_section and sum(folio_line_sizes[f]) >= 20]
baseline_folios = [f for f, s in folio_section.items()
                   if s == "herbal" and f not in plant_folios
                   and sum(folio_line_sizes[f]) >= 20]
print(f"Plant folios usable: {len(plant_folios_usable)}")
print(f"Non-plant herbal baseline: {len(baseline_folios)}")

# Real Voynich enrichment
real_folio_tokens = defaultdict(list)
for folio in CORPUS["folios"]:
    for line in folio["lines"]:
        real_folio_tokens[folio["folio"]].extend(line["words"])
real_plant_hits = sum(oii_rate(real_folio_tokens[f]) * len(real_folio_tokens[f])
                      for f in plant_folios_usable)
real_plant_tot = sum(len(real_folio_tokens[f]) for f in plant_folios_usable)
real_base_hits = sum(oii_rate(real_folio_tokens[f]) * len(real_folio_tokens[f])
                     for f in baseline_folios)
real_base_tot = sum(len(real_folio_tokens[f]) for f in baseline_folios)
real_plant_rate = real_plant_hits / real_plant_tot
real_base_rate = real_base_hits / real_base_tot
real_enr = real_plant_rate / real_base_rate
print(f"\nReal Voynich:")
print(f"  Aggregate _.oii rate: {(real_plant_hits+real_base_hits)/(real_plant_tot+real_base_tot):.5f}")
print(f"  Plant rate:           {real_plant_rate:.5f}")
print(f"  Baseline rate:        {real_base_rate:.5f}")
print(f"  Enrichment:           {real_enr:.2f}x")

# =========================================================================
# Richer volvelle
# =========================================================================
RING_A_PREFIXES = ["", "q", "qo", "o", "d", "ch"]
RING_C_SUFFIXES = ["", "y", "n", "r", "l", "in", "ain", "aiin"]
RING_C_WEIGHTS_A = [3, 4, 3, 2, 2, 2, 2, 3]
RING_C_WEIGHTS_B = [2, 6, 2, 3, 1, 3, 3, 1]
SECTIONS = ["astronomical","biological","cosmological","herbal",
            "pharmaceutical","recipes","text-only","zodiac"]

def generate_cartridge_rich(rng):
    # Weighted sample without replacement: 26 distinct roots
    picks = set()
    # For weighted sampling without replacement, do multiple attempts
    attempts = 0
    while len(picks) < 26 and attempts < 2000:
        r = rng.choices(root_types, weights=root_weights, k=1)[0]
        picks.add(r); attempts += 1
    return list(picks)

def generate_corpus(seed):
    rng = random.Random(seed)
    cartridges = {s: generate_cartridge_rich(rng) for s in SECTIONS}
    synth = defaultdict(list)
    for folio in CORPUS["folios"]:
        sec = folio["section"]; cur = folio.get("currier_language","?")
        fid = folio["folio"]
        cart = cartridges[sec]
        weights = RING_C_WEIGHTS_B if cur == "B" else RING_C_WEIGHTS_A
        for line in folio["lines"]:
            for _ in line["words"]:
                prefix = rng.choice(RING_A_PREFIXES)
                root   = rng.choice(cart)
                suffix = rng.choices(RING_C_SUFFIXES, weights=weights, k=1)[0]
                synth[fid].append(prefix + root + suffix)
    return synth

# =========================================================================
# Sanity pass — does the volvelle produce _.oii at all?
# =========================================================================
print("\nSanity check: 5 volvelle-v2 corpora, aggregate _.oii rate")
for seed in range(5):
    t = generate_corpus(seed)
    all_synth = [w for toks in t.values() for w in toks]
    rate = oii_rate(all_synth)
    print(f"  seed {seed}: {rate:.5f}  ({rate*100:.2f}%)")

# =========================================================================
# Null distribution: 200 richer-volvelle corpora
# =========================================================================
N = 200
print(f"\nGenerating {N} rich-volvelle corpora for null distribution...")
enr_samples = []
plant_rate_samples = []
base_rate_samples = []
agg_samples = []
for seed in range(N):
    toks = generate_corpus(seed)
    plant_hits = sum(oii_rate(toks[f]) * len(toks[f]) for f in plant_folios_usable)
    plant_tot  = sum(len(toks[f]) for f in plant_folios_usable)
    base_hits  = sum(oii_rate(toks[f]) * len(toks[f]) for f in baseline_folios)
    base_tot   = sum(len(toks[f]) for f in baseline_folios)
    p_rate = plant_hits / plant_tot if plant_tot else 0
    b_rate = base_hits / base_tot if base_tot else 0
    agg = (plant_hits + base_hits) / (plant_tot + base_tot)
    if b_rate > 0 and not math.isnan(p_rate / b_rate):
        enr = p_rate / b_rate
    else:
        enr = float("inf") if p_rate > 0 else 1.0
    if not math.isinf(enr):
        enr_samples.append(enr)
    plant_rate_samples.append(p_rate)
    base_rate_samples.append(b_rate)
    agg_samples.append(agg)
    if (seed+1) % 50 == 0:
        print(f"  ...{seed+1}/{N} (latest enr={enr:.2f}x, agg rate {agg:.5f})")

valid = enr_samples
mu = statistics.mean(valid)
sd = statistics.pstdev(valid)
lo = min(valid); hi = max(valid)
z = (real_enr - mu) / sd if sd > 0 else float("inf")
p_emp = sum(1 for e in valid if e >= real_enr) / len(valid)
agg_mean = statistics.mean(agg_samples)

print(f"\n{'='*72}")
print(f"  RICHER VOLVELLE NULL DISTRIBUTION (N={N})")
print(f"{'='*72}")
print(f"  Aggregate _.oii rate (synth mean): {agg_mean:.5f}")
print(f"  Real Voynich aggregate rate:       "
      f"{(real_plant_hits+real_base_hits)/(real_plant_tot+real_base_tot):.5f}")
print(f"  --> volvelle-v2 {'MATCHES' if abs(agg_mean - (real_plant_hits+real_base_hits)/(real_plant_tot+real_base_tot)) < 0.002 else 'DOES NOT MATCH'} corpus _.oii rate")
print(f"\n  Enrichment mean:  {mu:.3f}x")
print(f"  Enrichment stdev: {sd:.3f}")
print(f"  Enrichment range: [{lo:.2f}x, {hi:.2f}x]")
print(f"\n  Real Voynich enrichment: {real_enr:.2f}x")
print(f"  z-score vs null:         {z:.2f}")
print(f"  Empirical p:             {p_emp:.4f}  (null >= real out of {len(valid)})")

print(f"\n{'='*72}")
print(f"  VERDICT")
print(f"{'='*72}")
if p_emp == 0:
    print(f"  ZERO of {N} rich-volvelle runs produced enrichment >= {real_enr:.2f}x")
    print(f"  Volvelle max: {hi:.2f}x  (real: {real_enr:.2f}x)")
    print(f"  -> _.oii plant-folio enrichment is NOT reproducible by volvelle,")
    print(f"     even when roots are drawn from the real Voynich's own root pool.")
    print(f"  *** H-BV-PLANT-01 survives the richer volvelle test. ***")
elif p_emp < 0.05:
    print(f"  Real enrichment {real_enr:.2f}x; volvelle null mean {mu:.2f}x")
    print(f"  Empirical p = {p_emp:.4f} < 0.05")
    print(f"  -> H-BV-PLANT-01 survives at alpha=0.05 under richer volvelle")
else:
    print(f"  Volvelle reproduces enrichment >= {real_enr:.2f}x in {p_emp*100:.1f}% of runs")
    print(f"  -> H-BV-PLANT-01 FALLS: the _.oii plant enrichment is mechanical")

# Save
out = ROOT / "outputs" / "volvelle_v2_vs_oii.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "trials": N,
    "root_pool_size": len(root_types),
    "oii_producing_roots": len(oii_roots),
    "synth_aggregate_oii_rate": round(agg_mean, 5),
    "real_aggregate_oii_rate": round((real_plant_hits+real_base_hits)/(real_plant_tot+real_base_tot), 5),
    "real_enrichment": round(real_enr, 3),
    "volvelle_null": {
        "mean": round(mu, 4), "stdev": round(sd, 4),
        "min": round(lo, 4), "max": round(hi, 4),
        "plant_rate_mean": round(statistics.mean(plant_rate_samples), 6),
        "base_rate_mean": round(statistics.mean(base_rate_samples), 6),
    },
    "z_score": round(z, 2) if not math.isinf(z) else None,
    "empirical_p": round(p_emp, 4),
    "verdict": ("H-BV-PLANT-01 survives richer volvelle" if p_emp < 0.05
                else "_.oii may be mechanical under richer volvelle"),
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
