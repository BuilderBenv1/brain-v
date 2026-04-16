"""
Held-out validation + volvelle null for Hand-B plant markers.

Patterns under test: _.e.e, _.eeo, _.o.eo
Discovery set: 25 Hand-B plant folios, 7 Hand-B non-plant herbal folios.
Each pattern showed infinite enrichment (zero non-plant hits) in discovery.

Test 1 — 5-fold CV over Hand-B plant folios:
  For each pattern, for each fold, measure enrichment on held-out folds
  vs the fixed non-plant baseline. Require >=2x enrichment in all 5 folds
  to call the pattern held-out-validated.

Test 2 — Volvelle null:
  Generate 200 volvelle corpora with folio-level cartridges drawn from
  corpus-derived root pool (analogous to volvelle_v4). For each, compute
  aggregate fire rate of ALL THREE patterns combined on Hand-B plant
  folios vs Hand-B non-plant folios. Compare real to null distribution.
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
PATTERNS = ["_.e.e", "_.eeo", "_.o.eo"]
PATTERN_SET = set(PATTERNS)

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

# Index corpus
folio_tokens = defaultdict(list)
folio_hand = {}
folio_section = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_hand[fid] = f.get("currier_language","?")
    folio_section[fid] = f["section"]
    for line in f["lines"]:
        folio_tokens[fid].extend(line["words"])

plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        plant_folios.add(r["folio"])

b_plants = sorted(f for f in plant_folios
                  if folio_hand.get(f) == "B" and len(folio_tokens[f]) >= 20)
b_non = sorted(f for f,s in folio_section.items()
               if s == "herbal" and folio_hand.get(f) == "B"
               and f not in plant_folios and len(folio_tokens[f]) >= 20)
print(f"Hand-B plant folios: {len(b_plants)}")
print(f"Hand-B non-plant baseline: {len(b_non)}")

def rate(folios, pattern):
    toks = [w for f in folios for w in folio_tokens[f]]
    if not toks: return 0.0
    return sum(1 for w in toks if split_skel_vowels(w)[1] == pattern) / len(toks)

def combined_rate(folios):
    toks = [w for f in folios for w in folio_tokens[f]]
    if not toks: return 0.0
    return sum(1 for w in toks if split_skel_vowels(w)[1] in PATTERN_SET) / len(toks)

# =========================================================================
# TEST 1 — 5-fold CV on Hand-B plant folios
# =========================================================================
print("\n" + "="*72)
print("  TEST 1 — 5-fold CV over Hand-B plant folios")
print("="*72)

random.seed(42)
shuffled = b_plants[:]
random.shuffle(shuffled)
K = 5
fold_size = max(1, len(shuffled) // K)
folds = [shuffled[i*fold_size:(i+1)*fold_size] for i in range(K-1)]
folds.append(shuffled[(K-1)*fold_size:])

# Non-plant baseline: fixed
print(f"  {'pattern':<10} " + "  ".join(f"fold{i+1}" for i in range(K)) +
      "  all>=2x")
for pat in PATTERNS:
    base_rate = rate(b_non, pat)
    fold_enrs = []
    for fold in folds:
        held_out = fold
        ho_rate = rate(held_out, pat)
        if base_rate > 0:
            enr = ho_rate / base_rate
        else:
            enr = float("inf") if ho_rate > 0 else 0.0
        fold_enrs.append(enr)
    # When baseline is 0 (infinite), stability = all fold held-out rates > 0
    if base_rate == 0:
        all_positive = all(r > 0 for _, r in
                           ((f, rate(fold, pat)) for f, fold in zip(folds, folds)))
        fold_str = "  ".join("inf" if math.isinf(e) else f"{e:>5.2f}" for e in fold_enrs)
        ho_rates = [rate(fold, pat) for fold in folds]
        pass_count = sum(1 for r in ho_rates if r > 0)
        print(f"  {pat:<10} {fold_str}  stable_folds={pass_count}/{K}  "
              f"(baseline=0; substitute: fold has any hits)")
    else:
        fold_str = "  ".join(f"{e:>5.2f}" if not math.isinf(e) else "inf"
                              for e in fold_enrs)
        pass_count = sum(1 for e in fold_enrs if e >= 2.0 or math.isinf(e))
        print(f"  {pat:<10} {fold_str}  pass {pass_count}/{K}")

# Combined-rate CV
print(f"\n  COMBINED rate (any of {PATTERNS}) per fold:")
base_combined = combined_rate(b_non)
print(f"  Baseline (non-plant) combined rate: {base_combined:.5f}")
for i, fold in enumerate(folds, 1):
    r = combined_rate(fold)
    enr = r / base_combined if base_combined > 0 else float("inf")
    print(f"    fold {i}: n_folios={len(fold)} combined_rate={r:.5f}  "
          f"enr={'inf' if math.isinf(enr) else f'{enr:.2f}x'}")

# =========================================================================
# TEST 2 — Volvelle null on Hand-B plant enrichment
# =========================================================================
print("\n" + "="*72)
print("  TEST 2 — Volvelle null on Hand-B plant pattern enrichment")
print("="*72)

# Root pool (same as v4)
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

all_real = [w for f in CORPUS["folios"]
              for line in f["lines"] for w in line["words"]]
rc = Counter()
for w in all_real:
    r = strip_affixes(w)
    if 2 <= len(r) <= 6: rc[r] += 1
root_types = list(rc.keys()); root_weights = [rc[r] for r in root_types]
# Count roots that produce any of the three patterns
roots_for = {p: [r for r in root_types if split_skel_vowels(r)[1] == p] for p in PATTERNS}
for p in PATTERNS:
    print(f"  Roots producing {p}: {len(roots_for[p])}")

RING_A = ["", "q", "qo", "o", "d", "ch"]
RING_C = ["", "y", "n", "r", "l", "in", "ain", "aiin"]
WT_A = [3, 4, 3, 2, 2, 2, 2, 3]
WT_B = [2, 6, 2, 3, 1, 3, 3, 1]

def generate_folio_level(seed, cart_size=100):
    rng = random.Random(seed)
    folio_carts = {}
    for folio in CORPUS["folios"]:
        picks = set(); attempts = 0
        while len(picks) < cart_size and attempts < cart_size * 50:
            r = rng.choices(root_types, weights=root_weights, k=1)[0]
            picks.add(r); attempts += 1
        folio_carts[folio["folio"]] = list(picks)
    synth = defaultdict(list)
    for folio in CORPUS["folios"]:
        cur = folio.get("currier_language","?"); fid = folio["folio"]
        cart = folio_carts[fid]
        weights = WT_B if cur == "B" else WT_A
        for line in folio["lines"]:
            for _ in line["words"]:
                prefix = rng.choice(RING_A)
                root   = rng.choice(cart)
                suffix = rng.choices(RING_C, weights=weights, k=1)[0]
                synth[fid].append(prefix + root + suffix)
    return synth

# Real enrichment
real_p_rate = combined_rate(b_plants)
real_n_rate = combined_rate(b_non)
real_enr = real_p_rate / real_n_rate if real_n_rate > 0 else float("inf")
print(f"\n  Real Hand-B combined rate — plant: {real_p_rate:.5f}")
print(f"  Real Hand-B combined rate — non-plant: {real_n_rate:.5f}")
print(f"  Real enrichment: {'inf' if math.isinf(real_enr) else f'{real_enr:.2f}x'}")

# Since real baseline is 0 (infinite enrichment), the test is whether
# volvelle can produce plant rate >= real AND non-plant rate = 0
# More robust: compute difference (plant - non) and measure z vs null

print(f"\n  Generating 200 volvelle corpora (folio-level, cart_size=100)...")
plant_rates = []; non_rates = []; diffs = []
zero_non_count = 0
plant_ge_real_count = 0
for seed in range(200):
    toks = generate_folio_level(seed, 100)
    p_hits = sum(1 for f in b_plants for w in toks[f]
                 if split_skel_vowels(w)[1] in PATTERN_SET)
    p_tot  = sum(len(toks[f]) for f in b_plants)
    n_hits = sum(1 for f in b_non for w in toks[f]
                 if split_skel_vowels(w)[1] in PATTERN_SET)
    n_tot  = sum(len(toks[f]) for f in b_non)
    pr = p_hits / p_tot if p_tot else 0
    nr = n_hits / n_tot if n_tot else 0
    plant_rates.append(pr); non_rates.append(nr); diffs.append(pr - nr)
    if nr == 0: zero_non_count += 1
    if pr >= real_p_rate: plant_ge_real_count += 1
    if (seed+1) % 50 == 0:
        print(f"    {seed+1}/200  plant={pr:.5f} non={nr:.5f} diff={pr-nr:+.5f}")

mu_p = statistics.mean(plant_rates); mu_n = statistics.mean(non_rates)
mu_d = statistics.mean(diffs); sd_d = statistics.pstdev(diffs)
real_diff = real_p_rate - real_n_rate
z = (real_diff - mu_d) / sd_d if sd_d > 0 else float("inf")
p_emp_diff = sum(1 for d in diffs if d >= real_diff) / len(diffs)
# Joint condition: plant_rate >= real AND non_rate = 0
joint = sum(1 for pr, nr in zip(plant_rates, non_rates)
            if pr >= real_p_rate and nr == 0)
p_emp_joint = joint / len(plant_rates)

print(f"\n  Null plant rate (mean):     {mu_p:.5f}")
print(f"  Null non-plant rate (mean): {mu_n:.5f}")
print(f"  Null diff (mean, sd):       {mu_d:.5f}, {sd_d:.5f}")
print(f"  Null runs with non-plant rate = 0: {zero_non_count}/200")
print(f"  Null runs with plant rate >= real {real_p_rate:.5f}: {plant_ge_real_count}/200")
print(f"\n  Real diff:      {real_diff:+.5f}")
print(f"  z-score:        {z:.2f}")
print(f"  Empirical p (diff >= real):  {p_emp_diff:.4f}")
print(f"  Empirical p (joint plant>=real AND non=0): {p_emp_joint:.4f}")

if p_emp_diff == 0:
    print(f"\n  -> Zero null runs match real difference.")
    print(f"     Volvelle cannot reproduce Hand-B plant marker enrichment.")
elif p_emp_diff < 0.05:
    print(f"\n  -> Volvelle null rejected at p<0.05.")
else:
    print(f"\n  -> Volvelle can reproduce Hand-B enrichment in {p_emp_diff*100:.1f}% of runs.")

# Save
out = ROOT / "outputs" / "hand_b_holdout_and_volvelle.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "patterns": PATTERNS,
    "hand_b_plants_n": len(b_plants),
    "hand_b_non_plant_n": len(b_non),
    "real_plant_combined_rate": round(real_p_rate, 5),
    "real_non_plant_combined_rate": round(real_n_rate, 5),
    "holdout_5fold": {
        p: [rate(fold, p) for fold in folds] for p in PATTERNS
    },
    "holdout_combined_by_fold": [round(combined_rate(fold), 5) for fold in folds],
    "volvelle_null": {
        "runs": 200,
        "null_plant_mean": round(mu_p, 5),
        "null_non_mean": round(mu_n, 5),
        "null_diff_mean": round(mu_d, 5),
        "null_diff_sd": round(sd_d, 5),
        "zero_non_runs": zero_non_count,
        "plant_ge_real_runs": plant_ge_real_count,
        "z": round(z, 2) if not math.isinf(z) else None,
        "p_emp_diff": round(p_emp_diff, 4),
        "p_emp_joint": round(p_emp_joint, 4),
    },
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
