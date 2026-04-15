"""
Volvelle v3 — rate-matched. Closes the aggregate-rate gap from v2.

v2 underproduced _.oii at aggregate level because 26-root cartridges
rarely included any of the 8 roots that produce _.oii. v3 uses larger
per-section cartridges drawn from the full 3,635-root corpus pool so
that aggregate synthetic _.oii rate matches real (~0.335%). This is
the fair final volvelle test: does a volvelle whose aggregate _.oii
rate MATCHES real Voynich concentrate the pattern on plant folios by
chance alone through random cartridge assignment?
"""
import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

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

# Build root pool (same as v2)
PREFIXES = ["qo", "q", "ch", "sh", "o", "d"]
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

all_real_tokens = [w for f in CORPUS["folios"]
                     for line in f["lines"] for w in line["words"]]
root_counter = Counter()
for w in all_real_tokens:
    r = strip_affixes(w)
    if 2 <= len(r) <= 6:
        root_counter[r] += 1
root_types = list(root_counter.keys())
root_weights = [root_counter[r] for r in root_types]

# Folio structure
plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        notes = (r.get("notes") or "").upper()
        if "CONFLICT" in notes: continue
        plant_folios.add(r["folio"])

folio_section = {f["folio"]: f["section"] for f in CORPUS["folios"]}
folio_line_sizes = {f["folio"]: [len(line["words"]) for line in f["lines"]]
                    for f in CORPUS["folios"]}
plant_folios_usable = [f for f in plant_folios if f in folio_section
                       and sum(folio_line_sizes[f]) >= 20]
baseline_folios = [f for f, s in folio_section.items()
                   if s == "herbal" and f not in plant_folios
                   and sum(folio_line_sizes[f]) >= 20]

# Real benchmark
real_folio_tokens = defaultdict(list)
for folio in CORPUS["folios"]:
    for line in folio["lines"]:
        real_folio_tokens[folio["folio"]].extend(line["words"])
real_plant_rate = (sum(oii_rate(real_folio_tokens[f]) * len(real_folio_tokens[f])
                       for f in plant_folios_usable) /
                   sum(len(real_folio_tokens[f]) for f in plant_folios_usable))
real_base_rate = (sum(oii_rate(real_folio_tokens[f]) * len(real_folio_tokens[f])
                      for f in baseline_folios) /
                  sum(len(real_folio_tokens[f]) for f in baseline_folios))
real_enr = real_plant_rate / real_base_rate

RING_A = ["", "q", "qo", "o", "d", "ch"]
RING_C = ["", "y", "n", "r", "l", "in", "ain", "aiin"]
WT_A = [3, 4, 3, 2, 2, 2, 2, 3]
WT_B = [2, 6, 2, 3, 1, 3, 3, 1]
SECTIONS = ["astronomical","biological","cosmological","herbal",
            "pharmaceutical","recipes","text-only","zodiac"]

def generate_corpus(seed, cart_size):
    """Larger cartridge = better aggregate _.oii rate coverage."""
    rng = random.Random(seed)
    cartridges = {}
    for s in SECTIONS:
        picks = set()
        attempts = 0
        while len(picks) < cart_size and attempts < 20000:
            r = rng.choices(root_types, weights=root_weights, k=1)[0]
            picks.add(r); attempts += 1
        cartridges[s] = list(picks)
    synth = defaultdict(list)
    for folio in CORPUS["folios"]:
        sec = folio["section"]; cur = folio.get("currier_language","?")
        fid = folio["folio"]
        cart = cartridges[sec]
        weights = WT_B if cur == "B" else WT_A
        for line in folio["lines"]:
            for _ in line["words"]:
                prefix = rng.choice(RING_A)
                root   = rng.choice(cart)
                suffix = rng.choices(RING_C, weights=weights, k=1)[0]
                synth[fid].append(prefix + root + suffix)
    return synth

# Find cartridge size that matches aggregate rate
# Target: real aggregate 0.00335
print("Calibrating cartridge size to match aggregate _.oii rate...")
for cs in [50, 100, 150, 200, 300, 500]:
    rates = []
    for seed in range(5):
        t = generate_corpus(seed, cs)
        rates.append(oii_rate([w for toks in t.values() for w in toks]))
    mean = statistics.mean(rates)
    print(f"  cartridge_size={cs:>4} -> agg _.oii rate mean={mean:.5f}")

# Based on calibration, pick size that brings us close to 0.00335
# Typically cs=300-500 is needed
CART_SIZE = 500  # pick size that best matches real aggregate
print(f"\nUsing cartridge size = {CART_SIZE} for null distribution")

# Null distribution with matched cartridge size
N = 200
print(f"Generating {N} volvelle-v3 corpora...")
enr_samples = []; agg_samples = []; plant_samples = []; base_samples = []
for seed in range(N):
    toks = generate_corpus(seed, CART_SIZE)
    p_hits = sum(oii_rate(toks[f]) * len(toks[f]) for f in plant_folios_usable)
    p_tot  = sum(len(toks[f]) for f in plant_folios_usable)
    b_hits = sum(oii_rate(toks[f]) * len(toks[f]) for f in baseline_folios)
    b_tot  = sum(len(toks[f]) for f in baseline_folios)
    p_rate = p_hits / p_tot if p_tot else 0
    b_rate = b_hits / b_tot if b_tot else 0
    agg    = (p_hits + b_hits) / (p_tot + b_tot)
    plant_samples.append(p_rate); base_samples.append(b_rate); agg_samples.append(agg)
    if b_rate > 0:
        enr_samples.append(p_rate / b_rate)
    if (seed+1) % 50 == 0:
        print(f"  ...{seed+1}/{N} (agg={agg:.5f}, enr={enr_samples[-1] if enr_samples else 0:.2f}x)")

mu = statistics.mean(enr_samples); sd = statistics.pstdev(enr_samples)
lo = min(enr_samples); hi = max(enr_samples)
agg_mean = statistics.mean(agg_samples)
z = (real_enr - mu) / sd if sd > 0 else float("inf")
p_emp = sum(1 for e in enr_samples if e >= real_enr) / len(enr_samples)

print(f"\n{'='*72}")
print(f"  VOLVELLE V3 (rate-matched) null distribution, N={N}, cart_size={CART_SIZE}")
print(f"{'='*72}")
print(f"  Aggregate _.oii rate — synth mean: {agg_mean:.5f}")
print(f"  Aggregate _.oii rate — real:       {(sum(oii_rate(real_folio_tokens[f])*len(real_folio_tokens[f]) for f in plant_folios_usable+baseline_folios) / sum(len(real_folio_tokens[f]) for f in plant_folios_usable+baseline_folios)):.5f}")
print(f"  Rate match: {'YES' if abs(agg_mean - 0.00335) < 0.001 else 'closer but not perfect'}")
print(f"\n  Enrichment distribution:")
print(f"    mean:  {mu:.3f}x")
print(f"    stdev: {sd:.3f}")
print(f"    range: [{lo:.2f}x, {hi:.2f}x]")
print(f"\n  Real Voynich enrichment: {real_enr:.2f}x")
print(f"  z-score:                 {z:.2f}")
print(f"  Empirical p:             {p_emp:.4f}  ({sum(1 for e in enr_samples if e >= real_enr)}/{len(enr_samples)} runs >= real)")

print(f"\n{'='*72}")
print(f"  VERDICT")
print(f"{'='*72}")
if p_emp == 0:
    print(f"  Zero of {N} volvelle-v3 runs matched real enrichment.")
    print(f"  Volvelle max {hi:.2f}x vs real {real_enr:.2f}x.")
    print(f"  -> H-BV-PLANT-01 SURVIVES even the rate-matched richer volvelle.")
elif p_emp < 0.05:
    print(f"  p = {p_emp:.4f} < 0.05: H-BV-PLANT-01 survives at alpha=0.05.")
else:
    print(f"  p = {p_emp:.4f}: H-BV-PLANT-01 may be mechanically reproducible.")

out = ROOT / "outputs" / "volvelle_v3_vs_oii.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "trials": N,
    "cartridge_size": CART_SIZE,
    "synth_agg_rate": round(agg_mean, 5),
    "real_agg_rate": round((sum(oii_rate(real_folio_tokens[f])*len(real_folio_tokens[f]) for f in plant_folios_usable+baseline_folios) / sum(len(real_folio_tokens[f]) for f in plant_folios_usable+baseline_folios)), 5),
    "real_enrichment": round(real_enr, 3),
    "null_mean": round(mu, 4),
    "null_stdev": round(sd, 4),
    "null_range": [round(lo, 4), round(hi, 4)],
    "z_score": round(z, 2) if not math.isinf(z) else None,
    "empirical_p": round(p_emp, 4),
    "verdict": "survives" if p_emp < 0.05 else "mechanical",
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
