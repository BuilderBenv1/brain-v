"""
Execute pre-registered H-BV-NOMENCLATOR-01.

Hand A vocabulary head/tail split test for nomenclator-style cipher.
Split point R = first rank where cumulative tokens reach 50% of total.
Compare HIGH (head) vs LOW (tail) on five measures; permutation null with
1000 trials of random type-relabelling.

Decision (locked):
  4 of 5 nomenclator predictions hold AND >=2 with permutation p<0.01 -> CONFIRMED
  2-3 of 5 hold AND >=1 with p<0.05 -> MARGINAL
  0-1 of 5 hold OR none reach permutation significance -> REFUTED

Predictions (HIGH minus LOW):
  zipf_gap > 0
  glyph_entropy_gap < 0
  mean_length_gap < 0
  length_stddev_gap > 0
  type_glyph_entropy_gap < 0
"""
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI_GLYPHS = ["ckh", "cth", "cph", "ch", "sh"]

def eva_tokenize(word):
    out = []; i = 0
    while i < len(word):
        matched = False
        for t in MULTI_GLYPHS:
            if word.startswith(t, i):
                out.append(t); i += len(t); matched = True; break
        if not matched:
            out.append(word[i]); i += 1
    return out

# Build Hand-A token list
hand_a_tokens = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        for w in line["words"]:
            hand_a_tokens.append(w)

freq = Counter(hand_a_tokens)
N_total = sum(freq.values())
N_types = len(freq)
print(f"Hand A: {N_total} tokens, {N_types} types")

# Sort types by descending frequency
sorted_types = freq.most_common()

# Split point: cumulative tokens reach 50%
cum = 0; R = 0
for i, (t, c) in enumerate(sorted_types, 1):
    cum += c
    if cum >= N_total / 2:
        R = i
        break

print(f"\nHead/tail split rank R = {R} (cumulative tokens = {cum} >= {N_total/2:.0f})")
print(f"  HIGH class: {R} types covering {cum} tokens ({100*cum/N_total:.1f}%)")
print(f"  LOW  class: {N_types - R} types covering {N_total - cum} tokens ({100*(N_total-cum)/N_total:.1f}%)")

high_types = sorted_types[:R]
low_types = sorted_types[R:]

# =============================================================================
# Measures
# =============================================================================
def zipf_exponent(items):
    """Slope of log(rank) vs log(freq) within a class. items = [(type, freq), ...]
    returns -slope (positive = steeper)."""
    n = len(items)
    if n < 3:
        return 0.0
    log_rank = [math.log(i+1) for i in range(n)]
    log_freq = [math.log(c) for _, c in items]
    mr = sum(log_rank)/n
    mf = sum(log_freq)/n
    num = sum((log_rank[i]-mr)*(log_freq[i]-mf) for i in range(n))
    den = sum((log_rank[i]-mr)**2 for i in range(n))
    slope = num/den if den else 0.0
    return -slope

def glyph_entropy_weighted(items):
    """Entropy of glyph-unit distribution, weighted by token count."""
    counts = Counter()
    for t, c in items:
        for g in eva_tokenize(t):
            counts[g] += c
    total = sum(counts.values())
    if total == 0:
        return 0.0
    H = 0.0
    for c in counts.values():
        p = c/total
        if p > 0:
            H -= p * math.log2(p)
    return H

def type_glyph_entropy(items):
    """Entropy of glyph-unit distribution counting each TYPE once (unweighted).
    Probes whether the code-set is uniform across types."""
    counts = Counter()
    for t, _ in items:
        for g in eva_tokenize(t):
            counts[g] += 1
    total = sum(counts.values())
    if total == 0:
        return 0.0
    H = 0.0
    for c in counts.values():
        p = c/total
        if p > 0:
            H -= p * math.log2(p)
    return H

def mean_length_stddev(items, weighted=True):
    """Mean and stddev of word length in glyph-units. Weighted by token count."""
    lengths = []
    for t, c in items:
        L = len(eva_tokenize(t))
        if weighted:
            lengths.extend([L] * c)
        else:
            lengths.append(L)
    if len(lengths) < 2:
        return 0.0, 0.0
    return statistics.mean(lengths), statistics.stdev(lengths)

def measure_class(items):
    z = zipf_exponent(items)
    H_w = glyph_entropy_weighted(items)
    H_t = type_glyph_entropy(items)
    mL, sL = mean_length_stddev(items, weighted=True)
    return {"zipf": z, "glyph_entropy_weighted": H_w,
            "type_glyph_entropy": H_t,
            "mean_length": mL, "length_stddev": sL}

# Observed
m_high = measure_class(high_types)
m_low = measure_class(low_types)

print("\n" + "="*72)
print("  OBSERVED MEASURES")
print("="*72)
print(f"  {'measure':<28}{'HIGH':>14}{'LOW':>14}{'gap (H-L)':>14}")
gaps = {}
for k in ("zipf", "glyph_entropy_weighted", "type_glyph_entropy",
         "mean_length", "length_stddev"):
    h = m_high[k]; l = m_low[k]; g = h - l
    gaps[k] = g
    print(f"  {k:<28}{h:>14.4f}{l:>14.4f}{g:>+14.4f}")

# Predicted directions (nomenclator)
PREDICTED = {
    "zipf": +1,                    # HIGH steeper, gap > 0
    "glyph_entropy_weighted": -1,  # LOW flatter, gap < 0
    "type_glyph_entropy": -1,      # LOW more uniform, gap < 0
    "mean_length": -1,             # LOW longer, gap < 0
    "length_stddev": +1,           # LOW more uniform, gap > 0
}

# Direction check
direction_pass = {k: (gaps[k] * PREDICTED[k] > 0) for k in PREDICTED}
n_pass = sum(direction_pass.values())
print(f"\n  Direction-pass: {n_pass}/5 nomenclator predictions hold")
for k, ok in direction_pass.items():
    sign = "+" if PREDICTED[k] > 0 else "-"
    print(f"    {k:<28} predicted gap {sign}, observed {gaps[k]:+.4f}  {'PASS' if ok else 'fail'}")

# =============================================================================
# Permutation null: relabel types randomly
# =============================================================================
print("\n" + "="*72)
print("  PERMUTATION NULL (1000 trials, random type-relabelling)")
print("="*72)
print("  Recompute gaps under random HIGH/LOW assignment; report two-tailed p")
print("  in the nomenclator-predicted direction.")

rng = random.Random(0)
all_types = list(freq.items())
n_high = R
N_TRIALS = 1000

null_gaps = {k: [] for k in PREDICTED}
for trial in range(N_TRIALS):
    rng.shuffle(all_types)
    null_high = all_types[:n_high]
    null_low = all_types[n_high:]
    nm_h = measure_class(null_high)
    nm_l = measure_class(null_low)
    for k in PREDICTED:
        null_gaps[k].append(nm_h[k] - nm_l[k])

p_values = {}
for k in PREDICTED:
    obs = gaps[k]
    pred = PREDICTED[k]
    # one-sided in predicted direction:
    if pred > 0:
        p = sum(1 for g in null_gaps[k] if g >= obs) / N_TRIALS
    else:
        p = sum(1 for g in null_gaps[k] if g <= obs) / N_TRIALS
    p_values[k] = p

print(f"\n  {'measure':<28}{'observed gap':>14}{'p (1-sided)':>16}")
for k in PREDICTED:
    print(f"  {k:<28}{gaps[k]:>+14.4f}{p_values[k]:>16.4f}")

# =============================================================================
# Decision
# =============================================================================
n_p_001 = sum(1 for k, p in p_values.items()
              if direction_pass[k] and p < 0.01)
n_p_005 = sum(1 for k, p in p_values.items()
              if direction_pass[k] and p < 0.05)

print("\n" + "="*72)
print("  PRE-REGISTERED DECISION")
print("="*72)
print(f"  Direction-pass count: {n_pass}/5")
print(f"  With p < 0.01:        {n_p_001}/5")
print(f"  With p < 0.05:        {n_p_005}/5")

if n_pass >= 4 and n_p_001 >= 2:
    verdict = "CONFIRMED"
    print(f"  -> CONFIRMED: 4+ predictions hold AND >=2 reach p<0.01.")
    print(f"     Nomenclator-style two-population structure supported.")
elif 2 <= n_pass <= 3 and n_p_005 >= 1:
    verdict = "MARGINAL"
    print(f"  -> MARGINAL: 2-3 predictions hold with p<0.05 support.")
elif n_pass <= 1:
    verdict = "REFUTED"
    print(f"  -> REFUTED: 0-1 predictions hold; head/tail look statistically")
    print(f"     similar in glyph composition, length, and Zipf shape.")
else:
    # Edge cases: 4-5 pass but no permutation significance
    if n_p_005 == 0:
        verdict = "REFUTED"
        print(f"  -> REFUTED: gaps fall within natural permutation noise.")
    else:
        verdict = "MARGINAL"
        print(f"  -> MARGINAL: directionally aligned but weak permutation support.")

# Save
out_path = ROOT / "outputs" / "nomenclator_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-NOMENCLATOR-01",
    "hand_a_tokens": N_total,
    "hand_a_types": N_types,
    "split_rank_R": R,
    "high_class": {"n_types": R, "n_tokens": cum, "pct_tokens": round(100*cum/N_total, 2)},
    "low_class": {"n_types": N_types - R, "n_tokens": N_total - cum, "pct_tokens": round(100*(N_total-cum)/N_total, 2)},
    "measures_high": {k: round(v, 4) for k, v in m_high.items()},
    "measures_low": {k: round(v, 4) for k, v in m_low.items()},
    "gaps_high_minus_low": {k: round(v, 4) for k, v in gaps.items()},
    "predicted_directions": PREDICTED,
    "direction_pass": direction_pass,
    "n_direction_pass": n_pass,
    "permutation_p_values": {k: round(p, 4) for k, p in p_values.items()},
    "n_p_lt_001": n_p_001,
    "n_p_lt_005": n_p_005,
    "verdict": verdict,
    "thresholds": {
        "confirmed": "n_pass>=4 AND n_p<0.01>=2",
        "marginal": "2<=n_pass<=3 AND n_p<0.05>=1",
        "refuted": "n_pass<=1 OR no permutation significance",
    },
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
