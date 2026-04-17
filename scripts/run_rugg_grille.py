"""
Execute pre-registered H-BV-RUGG-GRILLE-01.

Simulate 1000 Cardan-grille generators at varying forbidden-cell
densities k in {0.0, 0.10, 0.20, 0.30, 0.50} and measure how often
each reproduces Hand A's n/C-inner categorical gap.

Locked decision rule:
  CONFIRMED (Rugg REFUTED):  <1% of sims reproduce the gap
  MARGINAL:                  1-10% reproduce
  REFUTED (gap not diagnostic): >10% reproduce
"""
import json
import random
from collections import Counter
from pathlib import Path
import numpy as np

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

BASE_MULTI = ["ckh", "cth", "cph", "ch", "sh"]
EXTRA = ["ol"]
MULTI = sorted(BASE_MULTI + EXTRA, key=lambda s: -len(s))

def tokenize(word):
    out = []; i = 0
    while i < len(word):
        matched = False
        for t in MULTI:
            if word.startswith(t, i):
                out.append(t); i += len(t); matched = True; break
        if not matched:
            out.append(word[i]); i += 1
    return out

VOWEL_INNERS = ["i", "e", "o", "a"]
CONSONANT_INNERS = ["ch", "d", "k", "t", "sh", "l"]
INNER_INVENTORY = VOWEL_INNERS + CONSONANT_INNERS  # 10 inners (indices: 0-3 V, 4-9 C)
OUTER_INVENTORY = ["y", "n", "r", "ol", "l"]       # 5 outers

# =============================================================================
# Build Hand A frequency distributions for inners/outers (for weighted sampling)
# =============================================================================
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

tokenised = [tokenize(w) for w in hand_a_words]
valid = [t for t in tokenised if len(t) >= 3]

inner_freq = Counter()
outer_freq = Counter()
for t in valid:
    inn = t[-2]
    out = t[-1]
    if inn in INNER_INVENTORY:
        inner_freq[inn] += 1
    if out in OUTER_INVENTORY:
        outer_freq[out] += 1

inner_weights = np.array([inner_freq[g] for g in INNER_INVENTORY], dtype=float)
inner_weights /= inner_weights.sum()
outer_weights = np.array([outer_freq[g] for g in OUTER_INVENTORY], dtype=float)
outer_weights /= outer_weights.sum()

print("Hand A inner frequencies (for sampling weights):")
for g, w in zip(INNER_INVENTORY, inner_weights):
    print(f"  {g:<4} {w:.4f}")
print("\nHand A outer frequencies:")
for g, w in zip(OUTER_INVENTORY, outer_weights):
    print(f"  {g:<4} {w:.4f}")

# =============================================================================
# Grille simulation
# =============================================================================
N_INNER = len(INNER_INVENTORY)   # 10
N_OUTER = len(OUTER_INVENTORY)   # 5
N_TOKENS_PER_SIM = 11022
N_SIMS_PER_K = 200
K_VALUES = [0.0, 0.10, 0.20, 0.30, 0.50]

# Hand A raw total tokens before N>=3 filter is ~11022; we need the resulting
# N>=3 filtered set to have enough consonant-inner attachments (>=2000) to
# meet the detection criterion. At Hand A's observed rates, ~8794 valid
# tokens yield ~2240 C-inner attachments. Sample enough to match.

VOWEL_IDX = set(range(0, 4))
CONSONANT_IDX = set(range(4, 10))

def simulate(k, rng):
    """Run one simulation at forbidden-cell density k.
    Returns (n_count_when_inner_C, count_inner_C).
    """
    # Build forbidden mask: 10x5 boolean, each cell forbidden w.p. k
    forbidden = rng.random((N_INNER, N_OUTER)) < k

    # Pre-compute allowed outer probabilities per inner
    allowed_outer_probs = []
    for i in range(N_INNER):
        w = outer_weights.copy()
        for o in range(N_OUTER):
            if forbidden[i, o]:
                w[o] = 0.0
        s = w.sum()
        if s == 0:
            allowed_outer_probs.append(None)  # no valid outers for this inner
        else:
            allowed_outer_probs.append(w / s)

    # Filter inner_weights to only those with at least one allowed outer
    viable_inners = [i for i in range(N_INNER) if allowed_outer_probs[i] is not None]
    if not viable_inners:
        return None

    viable_inner_weights = inner_weights[viable_inners]
    viable_inner_weights = viable_inner_weights / viable_inner_weights.sum()

    # Generate tokens
    inner_samples = rng.choice(viable_inners, size=N_TOKENS_PER_SIM, p=viable_inner_weights)

    # For each inner, sample outer using allowed probs
    # Count n-as-outer after C-inner, and total C-inner count
    n_outer_idx = OUTER_INVENTORY.index("n")
    count_C_inner = 0
    count_n_after_C = 0
    # Group inner indices by value for vectorised outer sampling
    for inner_val in range(N_INNER):
        probs = allowed_outer_probs[inner_val]
        if probs is None:
            continue
        mask = (inner_samples == inner_val)
        n = int(mask.sum())
        if n == 0:
            continue
        outer_samples = rng.choice(N_OUTER, size=n, p=probs)
        if inner_val in CONSONANT_IDX:
            count_C_inner += n
            count_n_after_C += int((outer_samples == n_outer_idx).sum())
    return count_n_after_C, count_C_inner

rng = np.random.default_rng(seed=20260417)

print(f"\nRunning {N_SIMS_PER_K * len(K_VALUES)} total simulations "
      f"({N_SIMS_PER_K} per k in {K_VALUES})...")

results_by_k = {}
total_reproduce = 0
total_sims = 0
for k in K_VALUES:
    reproduce = 0
    sim_details = []
    for s in range(N_SIMS_PER_K):
        r = simulate(k, rng)
        if r is None:
            continue
        n_after_C, C_total = r
        total_sims += 1
        # Detection criterion: count_n_after_C == 0 AND count_C_inner >= 2000
        if n_after_C == 0 and C_total >= 2000:
            reproduce += 1
            total_reproduce += 1
        sim_details.append((n_after_C, C_total))
    rate = reproduce / N_SIMS_PER_K
    results_by_k[k] = {
        "n_sims": N_SIMS_PER_K,
        "n_reproduce": reproduce,
        "reproduction_rate": round(rate, 4),
        "mean_C_total": round(np.mean([d[1] for d in sim_details]), 1) if sim_details else 0,
        "mean_n_after_C": round(np.mean([d[0] for d in sim_details]), 2) if sim_details else 0,
    }
    print(f"  k={k:.2f}:  {reproduce}/{N_SIMS_PER_K} reproduce ({rate*100:.2f}%)  "
          f"mean_C_total={results_by_k[k]['mean_C_total']}  "
          f"mean_n_after_C={results_by_k[k]['mean_n_after_C']}")

overall_rate = total_reproduce / total_sims if total_sims else 0.0
print(f"\nOverall: {total_reproduce}/{total_sims} reproduce ({overall_rate*100:.2f}%)")

# =============================================================================
# LOCKED DECISION
# =============================================================================
print("\n" + "="*78)
print("  LOCKED DECISION")
print("="*78)
if overall_rate < 0.01:
    verdict = "CONFIRMED_RUGG_REFUTED"
    rationale = f"Only {overall_rate*100:.2f}% (<1%) of 1000 simulations reproduce the n/C-inner gap; the gap requires a grammatical constraint, Rugg-grille REFUTED as explanation for Hand A"
elif overall_rate <= 0.10:
    verdict = "MARGINAL"
    rationale = f"{overall_rate*100:.2f}% (1-10%) of simulations reproduce the gap; achievable by grille but uncommon"
else:
    verdict = "REFUTED_FINDING_NOT_DIAGNOSTIC"
    rationale = f"{overall_rate*100:.2f}% (>10%) of simulations reproduce the gap; the categorical gap is mechanically achievable and not diagnostic for grammar"

print(f"  Reproduction rate: {overall_rate*100:.2f}%")
print(f"  VERDICT: {verdict}")
print(f"  {rationale}")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "rugg_grille_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-17",
    "hypothesis": "H-BV-RUGG-GRILLE-01",
    "seed": 20260417,
    "n_sims_per_k": N_SIMS_PER_K,
    "k_values": K_VALUES,
    "tokens_per_sim": N_TOKENS_PER_SIM,
    "inner_inventory": INNER_INVENTORY,
    "outer_inventory": OUTER_INVENTORY,
    "inner_weights": [round(float(w), 4) for w in inner_weights],
    "outer_weights": [round(float(w), 4) for w in outer_weights],
    "results_by_k": results_by_k,
    "total_sims": total_sims,
    "total_reproduce": total_reproduce,
    "overall_reproduction_rate": round(overall_rate, 4),
    "verdict": verdict,
    "rationale": rationale,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
