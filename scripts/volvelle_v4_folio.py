"""
Volvelle v4 — folio-level cartridge swap. The final mechanical escape hatch.

Design
------
Under this most-permissive volvelle, EACH FOLIO gets its own independent
random cartridge drawn from the corpus root pool. This allows by-chance
concentration of _.oii-producing roots on a specific folio subset — the
mechanism the section-level volvelle structurally cannot produce.

This is the STRONGEST VOLVELLE we can construct. If even v4 fails to
reproduce the 5.04x plant-folio enrichment, no volvelle-family
hypothesis can explain H-BV-PLANT-01.

Two sub-variants:
  v4a: 26-root folio cartridges (Quevedo spec, extreme volvelle)
  v4b: 200-root folio cartridges (allows aggregate rate to approach real)

Metric
------
For each null run, compute _.oii rate on plant-ID folios (n=115) and
on non-plant herbal baseline folios (n=15), return ratio. 500 null runs.
Real enrichment = 5.04x.
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

# Root pool
PREFIXES = ["qo", "q", "ch", "sh", "o", "d"]
SUFFIXES = ["aiin", "ain", "in", "y", "n", "r", "l"]
def strip_affixes(w):
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
oii_roots = [r for r in root_types if split_skel_vowels(r)[1] == "_.oii"]
print(f"Root pool: {len(root_types)} unique roots, {len(oii_roots)} produce _.oii")

# Folio sets
plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        notes = (r.get("notes") or "").upper()
        if "CONFLICT" in notes: continue
        plant_folios.add(r["folio"])

folio_section = {f["folio"]: f["section"] for f in CORPUS["folios"]}
folio_word_counts = {f["folio"]: sum(len(line["words"]) for line in f["lines"])
                     for f in CORPUS["folios"]}
folio_currier = {f["folio"]: f.get("currier_language","?") for f in CORPUS["folios"]}

plant_folios_usable = [f for f in plant_folios
                       if f in folio_section and folio_word_counts[f] >= 20]
baseline_folios = [f for f, s in folio_section.items()
                   if s == "herbal" and f not in plant_folios
                   and folio_word_counts[f] >= 20]
print(f"Plant folios: {len(plant_folios_usable)}  Baseline: {len(baseline_folios)}")

# Real benchmark
real_folio_tokens = defaultdict(list)
for folio in CORPUS["folios"]:
    for line in folio["lines"]:
        real_folio_tokens[folio["folio"]].extend(line["words"])

def enrichment_from_corpus(folio_tokens_map):
    p_hits = sum(oii_rate(folio_tokens_map[f]) * len(folio_tokens_map[f])
                 for f in plant_folios_usable)
    p_tot  = sum(len(folio_tokens_map[f]) for f in plant_folios_usable)
    b_hits = sum(oii_rate(folio_tokens_map[f]) * len(folio_tokens_map[f])
                 for f in baseline_folios)
    b_tot  = sum(len(folio_tokens_map[f]) for f in baseline_folios)
    pr = p_hits / p_tot if p_tot else 0
    br = b_hits / b_tot if b_tot else 0
    agg = (p_hits + b_hits) / (p_tot + b_tot)
    return pr, br, agg, (pr/br if br > 0 else (float("inf") if pr > 0 else 1.0))

real_pr, real_br, real_agg, real_enr = enrichment_from_corpus(real_folio_tokens)
print(f"\nReal Voynich: plant rate {real_pr:.5f}, base {real_br:.5f}, "
      f"enr {real_enr:.2f}x, agg {real_agg:.5f}")

# Generator
RING_A = ["", "q", "qo", "o", "d", "ch"]
RING_C = ["", "y", "n", "r", "l", "in", "ain", "aiin"]
WT_A = [3, 4, 3, 2, 2, 2, 2, 3]
WT_B = [2, 6, 2, 3, 1, 3, 3, 1]

def generate_folio_level(seed, cart_size):
    rng = random.Random(seed)
    # Per-folio cartridges (NEW: no section-level constraint)
    folio_carts = {}
    for folio in CORPUS["folios"]:
        picks = set(); attempts = 0
        while len(picks) < cart_size and attempts < cart_size * 100:
            r = rng.choices(root_types, weights=root_weights, k=1)[0]
            picks.add(r); attempts += 1
        folio_carts[folio["folio"]] = list(picks)
    # Emit tokens
    synth = defaultdict(list)
    for folio in CORPUS["folios"]:
        cur = folio.get("currier_language","?")
        fid = folio["folio"]
        cart = folio_carts[fid]
        weights = WT_B if cur == "B" else WT_A
        for line in folio["lines"]:
            for _ in line["words"]:
                prefix = rng.choice(RING_A)
                root   = rng.choice(cart)
                suffix = rng.choices(RING_C, weights=weights, k=1)[0]
                synth[fid].append(prefix + root + suffix)
    return synth

def run_null(cart_size, N, label):
    print(f"\n{'='*72}")
    print(f"  V4 — folio-level volvelle, cartridge size = {cart_size}  (N={N})")
    print(f"  {label}")
    print(f"{'='*72}")
    enrs = []; aggs = []; plant_rates = []; base_rates = []
    for seed in range(N):
        toks = generate_folio_level(seed, cart_size)
        pr, br, agg, enr = enrichment_from_corpus(toks)
        if not math.isinf(enr):
            enrs.append(enr)
        plant_rates.append(pr); base_rates.append(br); aggs.append(agg)
        if (seed+1) % 100 == 0:
            print(f"    {seed+1}/{N}  agg={agg:.5f}  enr={enr:.2f}x")

    mu = statistics.mean(enrs); sd = statistics.pstdev(enrs)
    lo = min(enrs); hi = max(enrs)
    agg_mean = statistics.mean(aggs)
    z = (real_enr - mu) / sd if sd > 0 else float("inf")
    p_emp = sum(1 for e in enrs if e >= real_enr) / len(enrs)

    print(f"\n  Aggregate _.oii rate — synth: {agg_mean:.5f}  vs  real: {real_agg:.5f}")
    print(f"  Enrichment — mean {mu:.3f}x, sd {sd:.3f}, range [{lo:.2f}x, {hi:.2f}x]")
    print(f"  Real Voynich enrichment: {real_enr:.2f}x")
    print(f"  z = {z:.2f}")
    print(f"  Empirical p = {p_emp:.4f}  "
          f"({sum(1 for e in enrs if e >= real_enr)}/{len(enrs)} runs >= real)")
    if p_emp == 0:
        print(f"  -> Zero null runs match real. H-BV-PLANT-01 SURVIVES.")
    elif p_emp < 0.05:
        print(f"  -> p < 0.05. H-BV-PLANT-01 survives at alpha=0.05.")
    else:
        print(f"  -> Folio-level volvelle CAN reproduce enrichment. H-BV-PLANT-01 falls.")
    return dict(cart_size=cart_size, N=N, agg_mean=agg_mean,
                null_mean=mu, null_sd=sd, null_min=lo, null_max=hi,
                z=z if not math.isinf(z) else None, p_emp=p_emp,
                n_valid=len(enrs))

results = []
results.append(run_null(26, 500, "Quevedo-spec cartridge (extreme volvelle)"))
results.append(run_null(200, 200, "Larger cartridge - rate-matched"))

# Save
out = ROOT / "outputs" / "volvelle_v4_folio.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "real_enrichment": round(real_enr, 3),
    "real_agg_rate": round(real_agg, 5),
    "variants": [
        {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}
        for r in results
    ],
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")

# Combined verdict
print(f"\n{'='*72}")
print(f"  COMBINED VERDICT ACROSS FOUR VOLVELLE VARIANTS")
print(f"{'='*72}")
print(f"  v1 (simple, 26-root, CV template):     max 0.00x / real 5.04x")
print(f"  v2 (corpus roots, 26, section-level):  max 2.80x / real 5.04x")
print(f"  v3 (corpus roots, 500, section-level): max 2.66x / real 5.04x")
print(f"  v4a (corpus roots, 26, folio-level):   max {results[0]['null_max']:.2f}x / real 5.04x")
print(f"  v4b (corpus roots, 200, folio-level):  max {results[1]['null_max']:.2f}x / real 5.04x")
if all(r["p_emp"] < 0.05 for r in results):
    print(f"\n  H-BV-PLANT-01 SURVIVES all four volvelle variants at p < 0.05.")
    print(f"  The volvelle family is effectively ruled out as the mechanism for")
    print(f"  the _.oii plant-folio enrichment.")
