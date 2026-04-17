"""
Execute pre-registered H-BV-BASQUE-HEADER-MAP-01.

Test whether the 14-item header pool from GALLOWS-STRIP-HEADER-01
is structurally compatible with a Basque medical/herbal vocabulary.

Locked decision:
  CONFIRMED: >=3/5 properties pass
  MARGINAL:  1-2/5
  REFUTED:   0/5
"""
import json
from collections import Counter
from pathlib import Path

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

VOWEL_LIKE = {"i", "e", "o", "a"}
LAYER2_OUTERS = {"y", "n", "r", "ol", "l"}

HEADERS = ["chor", "ol", "shol", "cho", "or", "cheol", "aiin",
           "chol", "odaiin", "cheody", "chody", "chocthy", "shor", "eol"]

tokens = {h: tokenize(h) for h in HEADERS}
print("Header pool tokenizations:")
for h in HEADERS:
    print(f"  {h:<10} -> {tokens[h]}  (len {len(tokens[h])})")

# =============================================================================
# H1 — No r-initial
# =============================================================================
r_initial = [h for h in HEADERS if tokens[h][0] == "r"]
H1_pass = len(r_initial) == 0
print(f"\nH1 r-initial count: {len(r_initial)}   {'PASS' if H1_pass else 'FAIL'}")

# =============================================================================
# H2 — Length distribution
# =============================================================================
lengths = [len(tokens[h]) for h in HEADERS]
mean_len = sum(lengths) / len(lengths)
sorted_lens = sorted(lengths)
median_len = sorted_lens[len(sorted_lens)//2] if len(sorted_lens) % 2 == 1 else \
             (sorted_lens[len(sorted_lens)//2 - 1] + sorted_lens[len(sorted_lens)//2]) / 2
H2_pass = (2.5 <= mean_len <= 6.0) and (2 <= median_len <= 6)
print(f"\nH2 length: mean {mean_len:.2f}  median {median_len}   "
      f"{'PASS' if H2_pass else 'FAIL'}")

# =============================================================================
# H3 — Vowel-final compatibility (>=35%)
# =============================================================================
vfinal = sum(1 for h in HEADERS if tokens[h][-1] in VOWEL_LIKE)
vfinal_frac = vfinal / len(HEADERS)
H3_pass = vfinal_frac >= 0.35
print(f"\nH3 vowel-final: {vfinal}/{len(HEADERS)} = {vfinal_frac:.4f}   "
      f"(threshold >=0.35)  {'PASS' if H3_pass else 'FAIL'}")
print(f"   Vowel-final headers: {[h for h in HEADERS if tokens[h][-1] in VOWEL_LIKE]}")

# =============================================================================
# H4 — Stem diversity: edit-distance-<=1 cluster count >=8
# =============================================================================
def edit_dist(a, b):
    """Standard Levenshtein on sequences (glyph-unit-level)."""
    m, n = len(a), len(b)
    if m == 0: return n
    if n == 0: return m
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0]*n
        for j in range(1, n + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            cur[j] = min(cur[j-1] + 1, prev[j] + 1, prev[j-1] + cost)
        prev = cur
    return prev[n]

# Build graph
adj = {h: [] for h in HEADERS}
for i, h1 in enumerate(HEADERS):
    for h2 in HEADERS[i+1:]:
        d = edit_dist(tokens[h1], tokens[h2])
        if d <= 1:
            adj[h1].append(h2)
            adj[h2].append(h1)

# BFS components
visited = set()
components = []
for h in HEADERS:
    if h in visited: continue
    comp = []
    stack = [h]
    while stack:
        x = stack.pop()
        if x in visited: continue
        visited.add(x)
        comp.append(x)
        stack.extend(adj[x])
    components.append(comp)

n_clusters = len(components)
H4_pass = n_clusters >= 8
print(f"\nH4 cluster count (edit-dist <=1): {n_clusters}   "
      f"(threshold >=8)  {'PASS' if H4_pass else 'FAIL'}")
for c in components:
    print(f"   cluster size {len(c)}: {c}")

# =============================================================================
# H5 — Hand A stem consistency: each header has a non-header occurrence
# =============================================================================
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

hand_a_tok = [tokenize(w) for w in hand_a_words]

header_with_non_header_occ = 0
per_header_counts = {}
for h in HEADERS:
    ht = tokens[h]
    # Count occurrences of this header as:
    # (a) exact token elsewhere in Hand A (not just the paragraph-initial recurrences — any occurrence)
    # (b) followed by a Layer-2 outer to form a longer word (like chor+y = chory)
    # (c) with gallows prefix (tchor, pchor) — this is the original header recurrence; does not count as 'non-header'
    total_occ = 0
    exact_match = 0
    with_outer = 0
    for t in hand_a_tok:
        # Exact match
        if t == ht:
            exact_match += 1
        # Header + Layer-2 outer
        if len(t) == len(ht) + 1 and t[:len(ht)] == ht and t[-1] in LAYER2_OUTERS:
            with_outer += 1
    total_occ = exact_match + with_outer
    per_header_counts[h] = {"exact": exact_match, "with_outer": with_outer, "total": total_occ}
    if total_occ > 0:
        header_with_non_header_occ += 1

H5_frac = header_with_non_header_occ / len(HEADERS)
H5_pass = H5_frac >= 0.70
print(f"\nH5 Header-stem Hand-A consistency: {header_with_non_header_occ}/{len(HEADERS)} = "
      f"{H5_frac:.4f}   (threshold >=0.70)  {'PASS' if H5_pass else 'FAIL'}")
for h, c in per_header_counts.items():
    print(f"   {h:<10} exact={c['exact']:<4} +outer={c['with_outer']:<4} total={c['total']}")

# =============================================================================
# LOCKED DECISION
# =============================================================================
print("\n" + "="*78)
print("  LOCKED DECISION")
print("="*78)
passes = [H1_pass, H2_pass, H3_pass, H4_pass, H5_pass]
n_pass = sum(passes)
print(f"  Properties passing: {n_pass}/5")
print(f"    H1 No r-initial:              {'PASS' if H1_pass else 'FAIL'}")
print(f"    H2 Length distribution:       {'PASS' if H2_pass else 'FAIL'}")
print(f"    H3 Vowel-final >=35%:         {'PASS' if H3_pass else 'FAIL'}")
print(f"    H4 Clusters >=8:              {'PASS' if H4_pass else 'FAIL'}")
print(f"    H5 Hand-A consistency >=70%:  {'PASS' if H5_pass else 'FAIL'}")

if n_pass >= 3:
    verdict = "CONFIRMED"
    rationale = f"{n_pass}/5 header-pool properties consistent with Basque-compatible vocabulary"
elif n_pass >= 1:
    verdict = "MARGINAL"
    rationale = f"{n_pass}/5 consistent; partial compatibility"
else:
    verdict = "REFUTED"
    rationale = "0/5 consistent; header pool incompatible with Basque vocabulary profile"

print(f"\n  VERDICT: {verdict}")
print(f"  {rationale}")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "basque_header_map_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-17",
    "hypothesis": "H-BV-BASQUE-HEADER-MAP-01",
    "header_pool": HEADERS,
    "tokenizations": {h: tokens[h] for h in HEADERS},
    "H1_r_initial": {"count": len(r_initial), "pass": H1_pass},
    "H2_length": {"mean": round(mean_len, 2), "median": median_len, "pass": H2_pass},
    "H3_vowel_final": {"fraction": round(vfinal_frac, 4), "pass": H3_pass,
                       "vowel_final_headers": [h for h in HEADERS if tokens[h][-1] in VOWEL_LIKE]},
    "H4_clusters": {"count": n_clusters, "components": components, "pass": H4_pass},
    "H5_hand_a_consistency": {"fraction": round(H5_frac, 4), "pass": H5_pass,
                               "per_header": per_header_counts},
    "n_pass": n_pass,
    "verdict": verdict,
    "rationale": rationale,
    "caveat": "No 15th-c. Basque medical/herbal corpus available; test rules out structural incompatibility only, cannot positively identify headers as Basque lexical items.",
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
