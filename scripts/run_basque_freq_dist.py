"""
Execute pre-registered H-BV-BASQUE-FREQ-DIST-01.

Compute Zipf exponent, top-10 token share, and rank-1/rank-10
frequency ratio on Hand A HIGH class (top 146 types, cumulative
50.1% token coverage). Compare against Basque-compatible ranges.

Locked decision:
  CONFIRMED: 3/3 in Basque-compatible ranges
  MARGINAL:  2/3
  REFUTED:   0-1/3
"""
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# =============================================================================
# Hand A full token list (not filtered to N>=3)
# =============================================================================
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

total_tokens = len(hand_a_words)
type_counts = Counter(hand_a_words)
print(f"Hand A total tokens: {total_tokens}")
print(f"Hand A unique types: {len(type_counts)}")

# =============================================================================
# Identify HIGH class: top 146 types, reproducing NOMENCLATOR-01 definition
# =============================================================================
ranked = type_counts.most_common()
cum = 0
high_cutoff_idx = None
for i, (tok, c) in enumerate(ranked):
    cum += c
    if cum >= 0.501 * total_tokens:
        high_cutoff_idx = i + 1
        break
print(f"HIGH class cutoff: top-{high_cutoff_idx} types cover "
      f"{cum}/{total_tokens} = {cum/total_tokens:.4f}")

HIGH_N = 146  # locked per pre-reg
high_types = ranked[:HIGH_N]
print(f"Using locked HIGH_N = {HIGH_N} (cumulative coverage "
      f"{sum(c for _, c in high_types)/total_tokens:.4f})")

# =============================================================================
# Z1 — Zipf exponent on HIGH class
# =============================================================================
# log(f_r) = C - alpha * log(r)
# Linear fit via closed-form least squares
xs = [math.log(r+1) for r in range(HIGH_N)]  # rank 1-indexed in equation, but log(1)=0; use log(r+1)
ys = [math.log(c) for _, c in high_types]
n = HIGH_N
sx = sum(xs); sy = sum(ys)
sxx = sum(x*x for x in xs); sxy = sum(x*y for x, y in zip(xs, ys))
alpha = -((n*sxy - sx*sy) / (n*sxx - sx*sx))
c_fit = (sy - (-alpha)*sx) / n

# Note: x = log(rank starting from 1) => use log(r+1) where r is 0-indexed rank
# Actually for rank r>=1, log(r). Let me redo:
xs = [math.log(r+1) for r in range(HIGH_N)]  # r+1 = 1,2,3,...
ys = [math.log(c) for _, c in high_types]
sx = sum(xs); sy = sum(ys)
sxx = sum(x*x for x in xs); sxy = sum(x*y for x, y in zip(xs, ys))
slope = (n*sxy - sx*sy) / (n*sxx - sx*sx)
alpha = -slope
print(f"\nZ1 Zipf exponent fit on top-{HIGH_N}: alpha = {alpha:.4f}")
Z1_pass = 0.85 <= alpha <= 1.15
print(f"   Basque range [0.85, 1.15]: {'PASS' if Z1_pass else 'FAIL'}")

# =============================================================================
# Z2 — Top-10 token share
# =============================================================================
top10_share = sum(c for _, c in ranked[:10]) / total_tokens
Z2_pass = 0.15 <= top10_share <= 0.30
print(f"\nZ2 Top-10 token share: {top10_share:.4f}")
print(f"   Basque range [0.15, 0.30]: {'PASS' if Z2_pass else 'FAIL'}")
print(f"   Top-10 types: {[t for t,_ in ranked[:10]]}")

# =============================================================================
# Z3 — Rank-1 / rank-10 frequency ratio
# =============================================================================
r1 = ranked[0][1]
r10 = ranked[9][1]
ratio_1_10 = r1 / r10
Z3_pass = 3.5 <= ratio_1_10 <= 7.0
print(f"\nZ3 rank-1 / rank-10 ratio: {r1} / {r10} = {ratio_1_10:.4f}")
print(f"   Basque range [3.5, 7.0]: {'PASS' if Z3_pass else 'FAIL'}")

# =============================================================================
# Diagnostic
# =============================================================================
print("\n  DIAGNOSTIC:")
r20 = ranked[19][1]
ratio_1_20 = r1 / r20
print(f"    rank-1 / rank-20 ratio: {ratio_1_20:.2f}")

one_glyph_high = sum(1 for t, _ in high_types if len(t) == 1)
print(f"    1-char types in HIGH class: {one_glyph_high}/{HIGH_N} = {one_glyph_high/HIGH_N:.3f}")

top10_mean_len = sum(len(t) for t, _ in ranked[:10]) / 10
print(f"    Mean length of top-10 types: {top10_mean_len:.2f}")

# =============================================================================
# LOCKED DECISION
# =============================================================================
print("\n" + "="*78)
print("  LOCKED DECISION")
print("="*78)
passes = [Z1_pass, Z2_pass, Z3_pass]
n_pass = sum(passes)
print(f"  Metrics passing: {n_pass}/3")
print(f"    Z1 Zipf exponent {alpha:.3f}:        {'PASS' if Z1_pass else 'FAIL'}")
print(f"    Z2 top-10 share {top10_share:.3f}:    {'PASS' if Z2_pass else 'FAIL'}")
print(f"    Z3 rank-1/rank-10 {ratio_1_10:.2f}:    {'PASS' if Z3_pass else 'FAIL'}")

if n_pass == 3:
    verdict = "CONFIRMED"
    rationale = "All 3 frequency-distribution metrics match Basque-compatible ranges"
elif n_pass == 2:
    verdict = "MARGINAL"
    rationale = f"{n_pass}/3 metrics match; partial compatibility"
else:
    verdict = "REFUTED"
    rationale = f"Only {n_pass}/3 metrics match; frequency distribution incompatible with Basque"

print(f"\n  VERDICT: {verdict}")
print(f"  {rationale}")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "basque_freq_dist_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-17",
    "hypothesis": "H-BV-BASQUE-FREQ-DIST-01",
    "total_tokens": total_tokens,
    "unique_types": len(type_counts),
    "high_class_size": HIGH_N,
    "high_class_coverage": round(sum(c for _, c in high_types)/total_tokens, 4),
    "Z1_zipf_exponent": {"value": round(alpha, 4), "range": [0.85, 1.15], "pass": Z1_pass},
    "Z2_top10_share": {"value": round(top10_share, 4), "range": [0.15, 0.30], "pass": Z2_pass},
    "Z3_rank_1_over_10": {"value": round(ratio_1_10, 4), "range": [3.5, 7.0], "pass": Z3_pass},
    "diagnostic": {
        "top10_types": [{"type": t, "count": c} for t, c in ranked[:10]],
        "rank1_over_rank20": round(ratio_1_20, 4),
        "one_glyph_types_in_high_class": one_glyph_high,
        "top10_mean_length": round(top10_mean_len, 2),
    },
    "n_pass": n_pass,
    "verdict": verdict,
    "rationale": rationale,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
