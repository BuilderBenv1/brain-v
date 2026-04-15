"""
Gap-close test: can the volvelle produce the 4.84x _.oii enrichment
on plant folios vs non-plant herbal folios that Brain-V observed in
real Voynich (H-BV-PLANT-01)?

Method
------
  - Generate 100 independent volvelle corpora (different seeds).
  - Each corpus uses per-section root cartridge swap identical to
    the volvelle_simulator design.
  - On each synthetic corpus, compute _.oii rate on:
      (a) same folios marked as plant-ID in plant-identifications.csv
      (b) same non-plant herbal folios used as baseline
    Compute enrichment = plant-rate / baseline-rate.
  - The 100 enrichments form the volvelle null distribution.
  - Compare real Voynich's 4.84x to this null distribution.

Interpretation
--------------
  If volvelle null mean ~1.0 and volvelle max < 4.84:
      _.oii is NOT reproducible by volvelle -> SIGNAL IS REAL.
  If volvelle null produces enrichment >= 3x routinely:
      _.oii may be a mechanical artefact.
  Report z-score of real Voynich against volvelle null.
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
CONSONANTS = list("kdrslnymg") + ["ch","sh","cth","ckh","cph","f","t","p"]
SECTIONS = ["astronomical","biological","cosmological","herbal",
            "pharmaceutical","recipes","text-only","zodiac"]

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
    hits = sum(1 for w in tokens if split_skel_vowels(w)[1] == "_.oii")
    return hits / len(tokens)

# =========================================================================
# Load plant folios (non-conflict) and build baseline set
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

plant_in_corpus = [f for f in plant_folios if f in folio_section]
baseline_folios = [f for f, s in folio_section.items()
                   if s == "herbal"
                   and f not in plant_folios
                   and sum(folio_line_sizes[f]) >= 20]
plant_folios_usable = [f for f in plant_in_corpus
                       if sum(folio_line_sizes[f]) >= 20]

print(f"Plant-ID folios (usable, >=20 tokens): {len(plant_folios_usable)}")
print(f"Baseline (non-plant herbal >=20 tokens): {len(baseline_folios)}")

# =========================================================================
# Real Voynich baseline (what we're comparing to)
# =========================================================================
real_folio_tokens = defaultdict(list)
for folio in CORPUS["folios"]:
    for line in folio["lines"]:
        real_folio_tokens[folio["folio"]].extend(line["words"])

real_plant_hits = sum(oii_rate(real_folio_tokens[f]) * sum(folio_line_sizes[f])
                      for f in plant_folios_usable)
real_plant_tot = sum(sum(folio_line_sizes[f]) for f in plant_folios_usable)
real_base_hits = sum(oii_rate(real_folio_tokens[f]) * sum(folio_line_sizes[f])
                     for f in baseline_folios)
real_base_tot = sum(sum(folio_line_sizes[f]) for f in baseline_folios)
real_enr = (real_plant_hits/real_plant_tot) / (real_base_hits/real_base_tot)
print(f"\nReal Voynich _.oii enrichment (plant / non-plant herbal): {real_enr:.2f}x")

# =========================================================================
# Volvelle generator
# =========================================================================
RING_A_PREFIXES = ["", "q", "qo", "o", "d", "ch"]
RING_C_SUFFIXES = ["", "y", "n", "r", "l", "in", "ain", "aiin"]
RING_C_WEIGHTS_A = [3, 4, 3, 2, 2, 2, 2, 3]
RING_C_WEIGHTS_B = [2, 6, 2, 3, 1, 3, 3, 1]

def generate_cartridge(rng):
    roots = []
    while len(roots) < 26:
        L = rng.choices([2,3,4], weights=[1,3,2], k=1)[0]
        out = []
        start_vowel = rng.random() < 0.3
        for i in range(L):
            if (i + (1 if start_vowel else 0)) % 2 == 0:
                out.append(rng.choice(CONSONANTS))
            else:
                out.append(rng.choice("aoei"))
        root = "".join(out)
        if 2 <= len(root) <= 5:
            roots.append(root)
    return roots

def generate_corpus(seed):
    rng = random.Random(seed)
    cartridges = {s: generate_cartridge(rng) for s in SECTIONS}
    synth_folio_tokens = defaultdict(list)
    for folio in CORPUS["folios"]:
        sec = folio["section"]; cur = folio.get("currier_language","?"); fid = folio["folio"]
        cart = cartridges[sec]
        weights = RING_C_WEIGHTS_B if cur == "B" else RING_C_WEIGHTS_A
        for line in folio["lines"]:
            for _ in line["words"]:
                prefix = rng.choice(RING_A_PREFIXES)
                root   = rng.choice(cart)
                suffix = rng.choices(RING_C_SUFFIXES, weights=weights, k=1)[0]
                synth_folio_tokens[fid].append(prefix + root + suffix)
    return synth_folio_tokens

# =========================================================================
# Null distribution: 100 volvelle corpora
# =========================================================================
print("\nGenerating 100 volvelle corpora...")
enr_samples = []
plant_rate_samples = []
base_rate_samples = []
for seed in range(100):
    toks = generate_corpus(seed)
    plant_hits = sum(oii_rate(toks[f]) * len(toks[f]) for f in plant_folios_usable)
    plant_tot  = sum(len(toks[f]) for f in plant_folios_usable)
    base_hits  = sum(oii_rate(toks[f]) * len(toks[f]) for f in baseline_folios)
    base_tot   = sum(len(toks[f]) for f in baseline_folios)
    p_rate = plant_hits / plant_tot if plant_tot else 0
    b_rate = base_hits / base_tot if base_tot else 0
    enr = p_rate / b_rate if b_rate > 0 else (float("inf") if p_rate > 0 else 0)
    if not math.isinf(enr):
        enr_samples.append(enr)
    plant_rate_samples.append(p_rate)
    base_rate_samples.append(b_rate)
    if (seed+1) % 20 == 0:
        print(f"  ...{seed+1}/100 complete (latest enr={enr:.2f}x)")

# Trim any inf
valid = [e for e in enr_samples if not math.isinf(e)]
mu = statistics.mean(valid)
sd = statistics.pstdev(valid)
lo = min(valid); hi = max(valid)
# z-score of real vs null
z = (real_enr - mu) / sd if sd > 0 else float("inf")
# Empirical p (fraction of null enrichments >= real)
p_emp = sum(1 for e in valid if e >= real_enr) / len(valid)

print(f"\n{'='*72}")
print(f"  VOLVELLE NULL DISTRIBUTION — 100 corpora")
print(f"{'='*72}")
print(f"  Enrichment mean:     {mu:.3f}x")
print(f"  Enrichment stdev:    {sd:.3f}")
print(f"  Enrichment range:    [{lo:.2f}x, {hi:.2f}x]")
print(f"  Plant-folio rate mean: {statistics.mean(plant_rate_samples):.5f}")
print(f"  Baseline rate mean:    {statistics.mean(base_rate_samples):.5f}")
print(f"\n  Real Voynich enrichment: {real_enr:.2f}x")
print(f"  z-score vs null:         {z:.2f}")
print(f"  Empirical p:             {p_emp:.4f}  "
      f"(fraction of null >= real)")

print(f"\n{'='*72}")
print(f"  VERDICT")
print(f"{'='*72}")
if p_emp == 0 and hi < real_enr:
    print(f"  Volvelle maximum ({hi:.2f}x) < real Voynich ({real_enr:.2f}x).")
    print(f"  ZERO of 100 volvelle corpora produced enrichment as extreme as real.")
    print(f"  -> _.oii ON PLANT FOLIOS IS NOT EXPLAINED BY VOLVELLE.")
    print(f"  *** This is evidence that _.oii carries real signal the volvelle cannot reproduce. ***")
elif p_emp < 0.05:
    print(f"  Real enrichment {real_enr:.2f}x vs volvelle null mean {mu:.2f}x.")
    print(f"  Empirical p = {p_emp:.4f} < 0.05.")
    print(f"  -> _.oii is NOT a mechanical artefact at alpha=0.05.")
else:
    print(f"  Volvelle reproduces enrichment >= {real_enr:.2f}x in {p_emp*100:.1f}% of runs.")
    print(f"  -> _.oii plant-folio enrichment is within the volvelle null distribution.")
    print(f"     Brain-V's last strong positive finding falls to the same mechanical")
    print(f"     explanation that demolished H-BV-VOWEL-01.")

# Save
out = ROOT / "outputs" / "volvelle_vs_oii.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "trials": 100,
    "real_enrichment": round(real_enr, 3),
    "volvelle_null": {
        "mean": round(mu, 4),
        "stdev": round(sd, 4),
        "min": round(lo, 4),
        "max": round(hi, 4),
        "plant_rate_mean": round(statistics.mean(plant_rate_samples), 6),
        "base_rate_mean": round(statistics.mean(base_rate_samples), 6),
    },
    "z_score": round(z, 2),
    "empirical_p": round(p_emp, 4),
    "verdict": ("signal_real_volvelle_cannot_explain" if p_emp < 0.05
                else "signal_may_be_mechanical"),
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
