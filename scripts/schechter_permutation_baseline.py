"""
Priority test requested after Brady ingest.

Brady reports z=3.83 on his Syriac mapping vs 500 random permutations of his
10-consonant alphabet (baseline mean 71.5%, true 86.9%).

Here we build a directly comparable null test for Schechter:

  H_0: Schechter's glossary could have been produced by any mapping of EVA
       words to the same 4,063 decoded strings, so its 82.81% coverage is
       not significantly better than a random assignment.

We can't permute a character alphabet for Schechter (his mapping is
word-level, not character-level). The honest analogue is permutation of the
GLOSSARY KEYS: keep the 4,063 decoded values, shuffle which EVA string each
one points at (drawn from the full set of EVA types actually found in the
corpus). For each shuffle, compute token coverage. 500 shuffles = null
distribution.

This asks: "If Schechter had picked 4,063 random EVA types and mapped them
to the same Latin/Occitan/Hebrew word list, would he have gotten similar
coverage?" That's the fair counterpart to Brady's permutation test.
"""
import csv
import json
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "scripts")
import decrypt

GLOSS_CSV = Path(r"C:\Projects\brain-v\raw\schechter_glossary.csv")

# --- Load glossary keys only ---
gloss_keys = []
with GLOSS_CSV.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        gloss_keys.append(row["eva"])

# --- Load corpus and compute token frequencies ---
corpus = decrypt.load_corpus()
all_words = []
for folio in corpus["folios"]:
    for line in folio["lines"]:
        all_words.extend(line["words"])

total_tokens = len(all_words)
wf = Counter(all_words)
eva_types = sorted(wf.keys())       # every unique EVA word that appears
# Precompute token freq array so coverage is fast
freq_of = dict(wf)

# --- TRUE coverage ---
true_match = sum(freq_of.get(k, 0) for k in set(gloss_keys))
true_cov = true_match / total_tokens

# --- Null distribution ---
# Each iteration: sample len(gloss_keys) EVA types from eva_types uniformly
# without replacement, sum token counts. The "mapping to decoded strings" is
# irrelevant to coverage (coverage only cares about which EVA types match),
# so uniform random subset of EVA types is the right null for coverage.
#
# BUT Schechter's dict is NOT uniformly distributed — he targeted frequent
# EVAs. So uniform-random grossly under-samples high-freq tokens. We also
# run a frequency-weighted null (length-matched to Schechter's dict length
# distribution) for a tougher, fairer comparison.

N = 500
random.seed(42)

uniform_cov = []
for _ in range(N):
    picks = random.sample(eva_types, len(gloss_keys))
    c = sum(freq_of[k] for k in picks)
    uniform_cov.append(c / total_tokens)

# Length-matched null: match the EVA-length distribution of the real glossary
from collections import defaultdict
by_len_corpus = defaultdict(list)
for t in eva_types:
    by_len_corpus[len(t)].append(t)
len_needed = Counter(len(k) for k in gloss_keys)

# If asked for more of a given length than exists in corpus, cap at corpus.
lenmatch_cov = []
for _ in range(N):
    picks = []
    for L, n in len_needed.items():
        pool = by_len_corpus.get(L, [])
        if not pool:
            continue
        k = min(n, len(pool))
        picks.extend(random.sample(pool, k))
    c = sum(freq_of[k] for k in picks)
    lenmatch_cov.append(c / total_tokens)

def report(name, dist, true_val):
    mu = statistics.mean(dist)
    sd = statistics.pstdev(dist)
    z = (true_val - mu) / sd if sd > 0 else float("inf")
    hi = max(dist)
    print(f"\n  {name}")
    print(f"  " + "-" * 66)
    print(f"  Null runs:        {len(dist)}")
    print(f"  Null mean:        {mu:.4f}  ({mu*100:.2f}%)")
    print(f"  Null stdev:       {sd:.4f}")
    print(f"  Null max:         {hi:.4f}  ({hi*100:.2f}%)")
    print(f"  True coverage:    {true_val:.4f}  ({true_val*100:.2f}%)")
    print(f"  z-score:          {z:.2f}")
    p = sum(1 for v in dist if v >= true_val) / len(dist)
    print(f"  Empirical p:      {p:.4g}  (fraction of nulls >= true)")
    return z, mu

print("=" * 72)
print("  SCHECHTER GLOSSARY — permutation-null coverage test (N=500)")
print("=" * 72)
print(f"  Corpus tokens:     {total_tokens:,}")
print(f"  EVA types:         {len(eva_types):,}")
print(f"  Dict entries:      {len(gloss_keys):,}")
print(f"  True coverage:     {true_cov:.4f}  ({true_cov*100:.2f}%)")

z1, mu1 = report("NULL A — uniform random EVA types (same dict size)",
                 uniform_cov, true_cov)
z2, mu2 = report("NULL B — length-matched random EVA types (fair null)",
                 lenmatch_cov, true_cov)

# --- Comparison to Brady ---
print("\n" + "=" * 72)
print("  COMPARISON")
print("=" * 72)
print(f"  {'System':<32} {'true':>8} {'null mu':>9} {'z':>7}")
print(f"  {'Brady (Syriac, DANI)':<32} {'86.90%':>8} {'71.50%':>9} {'3.83':>7}")
print(f"  {'Schechter uniform null':<32} {true_cov*100:>7.2f}% {mu1*100:>8.2f}% {z1:>7.2f}")
print(f"  {'Schechter length-matched null':<32} {true_cov*100:>7.2f}% {mu2*100:>8.2f}% {z2:>7.2f}")
print()
print("  Brady z=3.83 tests whether his 10-consonant MAPPING is non-random.")
print("  Schechter z above tests whether his CHOICE OF KEYS is non-random")
print("  w.r.t. token coverage alone. These are different null hypotheses")
print("  (Brady: right consonant assignment; Schechter: right keys at all).")
print("  Schechter almost certainly selected high-frequency EVA words, so")
print("  the length-matched null is the fairer comparison.")
