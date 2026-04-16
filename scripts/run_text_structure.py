"""
Execute pre-registered H-BV-TEXT-STRUCTURE-01.

On Hand A tokens only, compute four statistics and tag each against
prose vs list baselines (no external corpora consulted):

  (1) Repetition rate = share of all tokens belonging to the top-50
      most frequent types.
  (2) Type-token ratio at window size 500 = mean unique-types / 500
      across non-overlapping windows.
  (3) Mean distance between consecutive repeat occurrences of the
      top-20 tokens.
  (4) Standard deviation of token counts in units delimited by
      gallows-initial markers (tokens whose first character is one of
      t, k, p, f).

Baselines:
  prose: repetition 0.45, TTR 0.35, variable spacing, high variation
  list : repetition 0.60+, TTR 0.25, regular spacing, low variation
"""
import json
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

GALLOWS_INITIAL = set("tkpf")

# Collect Hand A tokens in document order (folio order, line order).
hand_a_tokens = []
for folio in CORPUS["folios"]:
    if folio.get("currier_language") != "A":
        continue
    for line in folio["lines"]:
        hand_a_tokens.extend(line["words"])

N = len(hand_a_tokens)
freq = Counter(hand_a_tokens)

# (1) Repetition rate over top-50 types.
top50 = [w for w, _ in freq.most_common(50)]
top50_set = set(top50)
top50_token_count = sum(1 for w in hand_a_tokens if w in top50_set)
repetition_rate = top50_token_count / N

# (2) Mean type-token ratio at window size 500 (non-overlapping).
W = 500
ttrs = []
for start in range(0, N - W + 1, W):
    window = hand_a_tokens[start:start + W]
    ttrs.append(len(set(window)) / W)
ttr_500 = statistics.mean(ttrs) if ttrs else 0.0

# (3) Mean distance between consecutive repeats of the top-20 tokens.
top20 = [w for w, _ in freq.most_common(20)]
positions_by_token = {w: [] for w in top20}
for i, w in enumerate(hand_a_tokens):
    if w in positions_by_token:
        positions_by_token[w].append(i)
all_gaps = []
per_token_means = []
per_token_cvs = []
for w in top20:
    pos = positions_by_token[w]
    if len(pos) < 2:
        continue
    gaps = [pos[i + 1] - pos[i] for i in range(len(pos) - 1)]
    all_gaps.extend(gaps)
    per_token_means.append(statistics.mean(gaps))
    if len(gaps) > 1 and statistics.mean(gaps) > 0:
        per_token_cvs.append(statistics.pstdev(gaps) / statistics.mean(gaps))
mean_repeat_distance = statistics.mean(all_gaps) if all_gaps else 0.0
gap_cv = statistics.mean(per_token_cvs) if per_token_cvs else 0.0

# (4) Standard deviation of token counts between gallows-initial markers.
# Walk the token stream; every time a token starts with t/k/p/f, close
# the current unit (count of tokens since the last marker) and open a new
# one. Unit length = number of non-marker tokens between two markers.
unit_lengths = []
current = 0
seen_first_marker = False
for tok in hand_a_tokens:
    if tok and tok[0] in GALLOWS_INITIAL:
        if seen_first_marker:
            unit_lengths.append(current)
        seen_first_marker = True
        current = 0
    else:
        current += 1
unit_std = statistics.pstdev(unit_lengths) if len(unit_lengths) > 1 else 0.0
unit_mean = statistics.mean(unit_lengths) if unit_lengths else 0.0
unit_cv = unit_std / unit_mean if unit_mean > 0 else 0.0

# Baseline tagging.
def tag_repetition(x):
    return "list" if x >= (0.45 + 0.60) / 2 else "prose"

def tag_ttr(x):
    return "list" if x <= (0.35 + 0.25) / 2 else "prose"

def tag_spacing(cv):
    # Lower CV = more regular spacing => list. Higher CV => variable => prose.
    return "list" if cv < 1.0 else "prose"

def tag_unit_variation(cv):
    return "list" if cv < 1.0 else "prose"

tag1 = tag_repetition(repetition_rate)
tag2 = tag_ttr(ttr_500)
tag3 = tag_spacing(gap_cv)
tag4 = tag_unit_variation(unit_cv)

verdict_counts = Counter([tag1, tag2, tag3, tag4])
overall = verdict_counts.most_common(1)[0][0]

print("=" * 72)
print("  H-BV-TEXT-STRUCTURE-01 — Hand A four-statistic baseline test")
print("=" * 72)
print(f"  Hand A tokens analysed: {N:,}")
print(f"  Hand A unique types:    {len(freq):,}")
print(f"  Window count (W=500):   {len(ttrs)}")
print(f"  Top-20 gap samples:     {len(all_gaps):,}")
print(f"  Inter-marker units:     {len(unit_lengths):,}")
print()
print(f"  (1) Repetition rate (top-50 share):     {repetition_rate:.4f}   -> {tag1}")
print(f"  (2) Type-token ratio @ window 500:      {ttr_500:.4f}   -> {tag2}")
print(f"  (3) Mean repeat distance, top-20:       {mean_repeat_distance:.4f}   -> {tag3}")
print(f"  (4) Gallows-unit length std deviation:  {unit_std:.4f}   -> {tag4}")
print()
print(f"  Auxiliary (not part of the four numbers):")
print(f"    top-20 inter-occurrence CV (mean):    {gap_cv:.4f}")
print(f"    gallows-unit length mean:             {unit_mean:.4f}")
print(f"    gallows-unit length CV:               {unit_cv:.4f}")
print()
print(f"  Per-statistic tags: {[tag1, tag2, tag3, tag4]}")
print(f"  Majority verdict: {overall}")

out = ROOT / "outputs" / "text_structure_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-TEXT-STRUCTURE-01",
    "hand_a_tokens": N,
    "hand_a_types": len(freq),
    "stat_1_repetition_rate_top50": round(repetition_rate, 6),
    "stat_2_ttr_window_500": round(ttr_500, 6),
    "stat_3_mean_repeat_distance_top20": round(mean_repeat_distance, 6),
    "stat_4_gallows_unit_length_std": round(unit_std, 6),
    "auxiliary": {
        "top20_gap_cv_mean": round(gap_cv, 6),
        "gallows_unit_length_mean": round(unit_mean, 6),
        "gallows_unit_length_cv": round(unit_cv, 6),
        "n_windows_500": len(ttrs),
        "n_top20_gaps": len(all_gaps),
        "n_gallows_units": len(unit_lengths),
    },
    "baselines": {
        "prose": {"repetition": 0.45, "ttr": 0.35, "spacing": "variable", "unit_variation": "high"},
        "list":  {"repetition": 0.60, "ttr": 0.25, "spacing": "regular",  "unit_variation": "low"},
    },
    "tags": {
        "repetition_rate": tag1,
        "ttr_500": tag2,
        "repeat_spacing": tag3,
        "unit_length_variation": tag4,
    },
    "majority_verdict": overall,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
