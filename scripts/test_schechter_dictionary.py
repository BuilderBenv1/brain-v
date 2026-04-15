"""
Honest test of Schechter's 4,063-entry glossary against the full Voynich corpus.

Repo: https://github.com/scott-schechter/voynich-decoded
Claim: 87.8% token coverage over 37,886 tokens, Latin/Occitan/Hebrew trilingual.

Brain-V rules:
  - Score against the FULL corpus (all sections).
  - Unmapped tokens count against coverage (no cherry-picking).
  - Section-by-section breakdown with Currier A/B if available.
  - Compare to Pagel's 81-term dictionary and Brain-V's other top hypotheses.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "scripts")
import decrypt

GLOSS_CSV = Path(r"C:\Projects\brain-v\raw\schechter_glossary.csv")

# --- Load glossary ---
GLOSS = {}
LANG_OF = {}
with GLOSS_CSV.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        GLOSS[row["eva"]] = row["decoded"]
        LANG_OF[row["eva"]] = row["language"]

# --- Load corpus ---
corpus = decrypt.load_corpus()
all_words = []
section_words = {}
for folio in corpus["folios"]:
    sec = folio["section"]
    section_words.setdefault(sec, [])
    for line in folio["lines"]:
        all_words.extend(line["words"])
        section_words[sec].extend(line["words"])

wf = Counter(all_words)
total_tokens = len(all_words)
total_types = len(wf)

print("=" * 80)
print("  SCHECHTER GLOSSARY — HONEST SCORING PIPELINE")
print(f"  Dictionary: {len(GLOSS):,} entries  |  Corpus: {total_tokens:,} tokens, {total_types:,} types")
print("=" * 80)

# --- Coverage (tokens include unmatched) ---
matched = 0
lang_tokens = Counter()
for w in all_words:
    if w in GLOSS:
        matched += 1
        lang_tokens[LANG_OF[w]] += 1

coverage_tok = matched / total_tokens
matched_types = sum(1 for w in wf if w in GLOSS)
coverage_typ = matched_types / total_types

print(f"\n  OVERALL COVERAGE")
print(f"  ----------------------------------------------------------------")
print(f"  Total tokens:      {total_tokens:,}")
print(f"  Matched tokens:    {matched:,}")
print(f"  Unmatched tokens:  {total_tokens - matched:,}")
print(f"  Token coverage:    {coverage_tok:.2%}   (Schechter claims 87.8%)")
print(f"  Type coverage:     {coverage_typ:.2%}   ({matched_types:,}/{total_types:,})")
print(f"  Dict entries unused in corpus: {len(GLOSS) - matched_types:,}")

print(f"\n  TOKENS MATCHED BY LANGUAGE TAG")
print(f"  ----------------------------------------------------------------")
for lang, n in lang_tokens.most_common():
    print(f"  {lang:<10} {n:>8,}  ({n/total_tokens:.1%} of all tokens)")

# --- Section breakdown ---
print(f"\n  SECTION-BY-SECTION COVERAGE")
print(f"  ----------------------------------------------------------------")
print(f"  {'Section':<18} {'Tokens':>8} {'Matched':>9} {'Coverage':>10} {'Latin':>7} {'Occ':>6} {'Heb':>5}")
for sec in sorted(section_words):
    sw = section_words[sec]
    m = [w for w in sw if w in GLOSS]
    lat = sum(1 for w in m if LANG_OF[w] == "latin")
    occ = sum(1 for w in m if LANG_OF[w] == "occitan")
    heb = sum(1 for w in m if LANG_OF[w] == "hebrew")
    pct = len(m) / len(sw) * 100 if sw else 0
    print(f"  {sec:<18} {len(sw):>8,} {len(m):>9,} {pct:>9.1f}% {lat:>7,} {occ:>6,} {heb:>5,}")

# --- Honest dict hit rate: fraction of DICT that actually maps real tokens ---
dict_useful = matched_types  # types in glossary that appear in corpus
dict_hit_rate = dict_useful / len(GLOSS)
print(f"\n  HONEST DICT HIT RATE")
print(f"  ----------------------------------------------------------------")
print(f"  Dict entries:                  {len(GLOSS):,}")
print(f"  Dict entries that match corpus: {dict_useful:,}")
print(f"  Dict hit rate:                 {dict_hit_rate:.2%}")
print(f"  (Fraction of glossary that earns its keep; inverse of dead weight)")

# --- Top unmatched tokens (what the dict misses) ---
unmatched_freq = Counter()
for w, c in wf.items():
    if w not in GLOSS:
        unmatched_freq[w] = c
print(f"\n  TOP 15 UNMATCHED TOKENS  (what Schechter's glossary misses)")
print(f"  ----------------------------------------------------------------")
for w, c in unmatched_freq.most_common(15):
    print(f"  {w:<15} {c:>6,}  ({c/total_tokens:.2%})")

# --- Compare to Pagel and to Brain-V baselines ---
print(f"\n  COMPARISON VS BRAIN-V'S OWN BEST ATTACKS")
print(f"  ----------------------------------------------------------------")
# Pagel's dict (inline copy from test_pagel_dictionary.py)
PAGEL = {
    "daiin","chedy","chol","shedy","dam","ol","otal","or","sam","sal","chom","kor",
    "sar","chor","y","sho","qokain","qokeey","otar","oteey","dain","kal","rar",
    "ar","al","shol","cheol","cheor","s","dan","shy","qokedy","lchedy","keol","qol","qokor","otedy",
    "bar","lach","chey","shey","chy","sheol","por","teody","oky","kchy","saiin","cholaiin","qoky",
    "chckhy","shekar","darchiin","qokal","aiindy","dago",
}
pagel_matched = sum(1 for w in all_words if w in PAGEL)
pagel_cov = pagel_matched / total_tokens

# Random baseline: what does matching 3648 random EVA words give?
# (The claimed 2.1% baseline from their README is comparable.)
print(f"  {'System':<35} {'Dict size':>10} {'Coverage':>10}")
print(f"  {'Schechter (this test)':<35} {len(GLOSS):>10,} {coverage_tok:>9.2%}")
print(f"  {'Schechter (claimed)':<35} {'3,648':>10} {'87.80%':>10}")
print(f"  {'Pagel (81 terms, verified)':<35} {len(PAGEL):>10,} {pagel_cov:>9.2%}")
print(f"  {'Pagel (claimed)':<35} {'81':>10} {'96.00%':>10}")

# Brain-V's best hypothesis attacks have not produced a dictionary — they produce
# structural claims. Coverage isn't directly comparable, but Brain-V has ZERO
# honest decoded tokens to date.
print(f"  {'Brain-V structural hypotheses':<35} {'n/a':>10} {'0.00%':>10}  (no dict yet)")

# --- Verdict ---
print(f"\n{'=' * 80}")
print(f"  VERDICT")
print(f"{'=' * 80}")
gap = 0.878 - coverage_tok
if coverage_tok >= 0.85:
    verdict = "CLAIM VERIFIED"
elif coverage_tok >= 0.70:
    verdict = "PARTIALLY VERIFIED (below claim)"
elif coverage_tok >= 0.40:
    verdict = "MODERATE COVERAGE (well below claim)"
else:
    verdict = "CLAIM NOT SUPPORTED"
print(f"  Honest token coverage:  {coverage_tok:.2%}")
print(f"  Schechter claim:        87.80%")
print(f"  Gap:                    {gap:+.2%}")
print(f"  -> {verdict}")
print()
print(f"  Caveat: coverage is NECESSARY but not SUFFICIENT. A dictionary that")
print(f"  maps 87% of tokens to Latin words can still be wrong if the resulting")
print(f"  'Latin' text is not grammatical, not coherent, or fits random glyph")
print(f"  strings equally well. That test is separate (permutation / grammar).")
