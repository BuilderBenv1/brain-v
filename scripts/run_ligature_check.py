"""
Execute pre-registered H-BV-LIGATURE-CHECK-01.

Sanity check on EVA tokenisation. For each candidate bigram
AB in {qo, ol, ch, sh, cth, ckh, cph}, compute:

  M1 frequency enrichment over independence
  M2 cross-word-boundary split rate
  M3 positional chi-square vs A-followed-by-non-B

Classification (locked):
  LIGATURE if enrichment >= 3.0 AND split_rate <= 0.05 AND chi2 p < 0.01
  TRUE BIGRAM if enrichment <= 1.5 AND split_rate >= 0.15
  AMBIGUOUS otherwise

Overall tokenisation verdict:
  VALIDATED if all 5 currently-collapsed (ch/sh/ckh/cth/cph) test LIGATURE
    and qo/ol test non-LIGATURE
  MIS-PARSING DETECTED if any candidate tests against current treatment
  AMBIGUOUS otherwise
"""
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# =============================================================================
# Flatten full corpus (all hands) to list of words in document order
# =============================================================================
words = []
for f in CORPUS["folios"]:
    for line in f["lines"]:
        words.extend(line["words"])

n_words = len(words)
print(f"Corpus words: {n_words}")

# =============================================================================
# Character-level stats (within-word only; does NOT count word-boundary chars)
# =============================================================================
all_chars = "".join(words)
total_chars = len(all_chars)
char_freq = Counter(all_chars)
# For true probability of a char within a word:
char_p = {c: v / total_chars for c, v in char_freq.items()}

# Total 2-grams and 3-grams WITHIN words
total_2grams = sum(max(0, len(w) - 1) for w in words)
total_3grams = sum(max(0, len(w) - 2) for w in words)

print(f"Within-word characters: {total_chars}")
print(f"Within-word 2-grams: {total_2grams}")
print(f"Within-word 3-grams: {total_3grams}")

# Top single-char frequencies
print(f"\nTop 15 character frequencies:")
for c, v in char_freq.most_common(15):
    print(f"  {c!r}: {v:>6}  ({100*v/total_chars:.2f}%)")

# =============================================================================
# Candidate bigrams and 3-grams
# =============================================================================
CANDIDATES_2 = ["qo", "ol", "ch", "sh"]
CANDIDATES_3 = ["cth", "ckh", "cph"]
CURRENTLY_COLLAPSED = {"ch", "sh", "cth", "ckh", "cph"}

# =============================================================================
# For each candidate, compute the three metrics
# =============================================================================
def count_subsequence_within_words(seq):
    """Count non-overlapping occurrences of seq within each word; sum."""
    n = 0
    L = len(seq)
    for w in words:
        i = 0
        while i <= len(w) - L:
            if w[i:i+L] == seq:
                n += 1
                i += 1  # allow overlap for counting purposes (they rarely overlap for our seqs)
            else:
                i += 1
    return n

def count_word_position(seq, position):
    """Count occurrences of seq AT a specific position within words.
    position: 'initial' = seq starts at index 0 AND word length >= len(seq)
              'final'   = seq ends at the last index of the word
              'medial'  = neither initial nor final"""
    n = 0
    L = len(seq)
    for w in words:
        if len(w) < L: continue
        for i in range(len(w) - L + 1):
            if w[i:i+L] == seq:
                if i == 0 and len(w) == L:
                    # whole word = seq; count as initial
                    if position == "initial": n += 1
                elif i == 0:
                    if position == "initial": n += 1
                elif i + L == len(w):
                    if position == "final": n += 1
                else:
                    if position == "medial": n += 1
    return n

def count_cross_boundary(a, b):
    """Count word pairs where word N ends with char 'a' and word N+1 starts
    with char 'b'."""
    n = 0
    for i in range(len(words) - 1):
        if words[i] and words[i+1] and words[i][-1] == a and words[i+1][0] == b:
            n += 1
    return n

def count_A_followed_by_notB(a, b, position):
    """Count occurrences within-word of 'a' followed by a char != b, at given
    position. For 3-char candidates, the comparator is 'c' followed by {t,k,p}
    followed by a char != 'h', handled separately below."""
    n = 0
    for w in words:
        if len(w) < 2: continue
        for i in range(len(w) - 1):
            if w[i] == a and w[i+1] != b:
                L = 2
                if i == 0 and len(w) > L:
                    if position == "initial": n += 1
                elif i == 0 and len(w) == L:
                    if position == "initial": n += 1
                elif i + L == len(w):
                    if position == "final": n += 1
                else:
                    if position == "medial": n += 1
    return n

def count_3_comparator(prefix_ab, c_after, position):
    """For 3-char candidate 'a'+'b'+'c', the comparator is 'a'+'b' followed by
    NOT 'c'. position as above."""
    n = 0
    L = 3
    a, b = prefix_ab[0], prefix_ab[1]
    for w in words:
        if len(w) < 3: continue
        for i in range(len(w) - 2):
            if w[i] == a and w[i+1] == b and w[i+2] != c_after:
                if i == 0 and len(w) > L:
                    if position == "initial": n += 1
                elif i == 0 and len(w) == L:
                    if position == "initial": n += 1
                elif i + L == len(w):
                    if position == "final": n += 1
                else:
                    if position == "medial": n += 1
    return n

# Chi-square for 2x3 contingency
def chi_square_2x3(row1, row2):
    """row1, row2 each = [initial, medial, final] counts.
    Returns chi2, df=2, p_value."""
    total = sum(row1) + sum(row2)
    if total == 0: return 0, 2, 1
    col_sums = [row1[i] + row2[i] for i in range(3)]
    r1_sum = sum(row1); r2_sum = sum(row2)
    chi2 = 0
    for i in range(3):
        for r_sum, r_val in ((r1_sum, row1[i]), (r2_sum, row2[i])):
            exp = r_sum * col_sums[i] / total if total else 0
            if exp > 0:
                chi2 += (r_val - exp) ** 2 / exp
    return chi2, 2, chi2_sf(chi2, 2)

def chi2_sf(x, df):
    if df <= 0 or x <= 0: return 1.0
    a = df / 2.0; z = x / 2.0
    if z < a + 1.0:
        term = 1.0 / a; s = term; ap = a
        for _ in range(500):
            ap += 1; term *= z / ap; s += term
            if abs(term) < abs(s) * 1e-14: break
        P = s * math.exp(-z + a * math.log(z) - math.lgamma(a))
        return max(0.0, 1.0 - P)
    b = z + 1.0 - a; c_ = 1.0 / 1e-300; d = 1.0 / b; h = d
    for i in range(1, 500):
        an = -i * (i - a); b += 2.0
        d = an * d + b
        if abs(d) < 1e-300: d = 1e-300
        c_ = b + an / c_
        if abs(c_) < 1e-300: c_ = 1e-300
        d = 1.0 / d
        delta = d * c_; h *= delta
        if abs(delta - 1.0) < 1e-14: break
    Q = h * math.exp(-z + a * math.log(z) - math.lgamma(a))
    return max(0.0, min(1.0, Q))

# =============================================================================
# Evaluate each candidate
# =============================================================================
results = []

def eval_2gram(ab):
    a, b = ab[0], ab[1]
    observed = count_subsequence_within_words(ab)
    expected = total_2grams * char_p[a] * char_p[b] if a in char_p and b in char_p else 0
    enrichment = observed / expected if expected > 0 else float("inf")
    within_word = observed
    cross = count_cross_boundary(a, b)
    split_rate = cross / (within_word + cross) if (within_word + cross) else 0
    # positional
    ab_init = count_word_position(ab, "initial")
    ab_med = count_word_position(ab, "medial")
    ab_fin = count_word_position(ab, "final")
    a_star_init = count_A_followed_by_notB(a, b, "initial")
    a_star_med = count_A_followed_by_notB(a, b, "medial")
    a_star_fin = count_A_followed_by_notB(a, b, "final")
    chi2, df, p = chi_square_2x3([ab_init, ab_med, ab_fin],
                                   [a_star_init, a_star_med, a_star_fin])
    return {
        "candidate": ab, "length": 2,
        "observed": observed, "expected": round(expected, 1),
        "enrichment": round(enrichment, 2),
        "within_word": within_word, "cross_boundary": cross,
        "split_rate": round(split_rate, 4),
        "AB_positions": {"initial": ab_init, "medial": ab_med, "final": ab_fin},
        "A_not_B_positions": {"initial": a_star_init, "medial": a_star_med,
                                "final": a_star_fin},
        "chi2": round(chi2, 2), "df": df, "p_value": round(p, 6),
    }

def eval_3gram(abc):
    a, b, c = abc[0], abc[1], abc[2]
    observed = count_subsequence_within_words(abc)
    expected = total_3grams * char_p[a] * char_p[b] * char_p[c]
    enrichment = observed / expected if expected > 0 else float("inf")
    within_word = observed
    # cross boundary for 3-gram: pair (ab | c) or (a | bc) — for the 3-gram
    # "a split at word-break c" means last two chars of word N are ab AND first
    # char of word N+1 is c. OR last char of N is a AND first two of N+1 are bc.
    split1 = 0  # ab | c
    split2 = 0  # a | bc
    for i in range(len(words) - 1):
        if words[i] and words[i+1]:
            if len(words[i]) >= 2 and words[i][-2:] == a+b and words[i+1][0] == c:
                split1 += 1
            if words[i][-1] == a and len(words[i+1]) >= 2 and words[i+1][:2] == b+c:
                split2 += 1
    cross = split1 + split2
    split_rate = cross / (within_word + cross) if (within_word + cross) else 0
    abc_init = count_word_position(abc, "initial")
    abc_med = count_word_position(abc, "medial")
    abc_fin = count_word_position(abc, "final")
    # comparator: a+b followed by something != c
    ab_star_init = count_3_comparator(a+b, c, "initial")
    ab_star_med = count_3_comparator(a+b, c, "medial")
    ab_star_fin = count_3_comparator(a+b, c, "final")
    chi2, df, p = chi_square_2x3([abc_init, abc_med, abc_fin],
                                   [ab_star_init, ab_star_med, ab_star_fin])
    return {
        "candidate": abc, "length": 3,
        "observed": observed, "expected": round(expected, 1),
        "enrichment": round(enrichment, 2),
        "within_word": within_word, "cross_boundary": cross,
        "split_rate": round(split_rate, 4),
        "ABC_positions": {"initial": abc_init, "medial": abc_med, "final": abc_fin},
        "AB_not_C_positions": {"initial": ab_star_init, "medial": ab_star_med,
                                 "final": ab_star_fin},
        "chi2": round(chi2, 2), "df": df, "p_value": round(p, 6),
    }

for ab in CANDIDATES_2:
    results.append(eval_2gram(ab))
for abc in CANDIDATES_3:
    results.append(eval_3gram(abc))

# =============================================================================
# Classify and report
# =============================================================================
print("\n" + "="*94)
print("  EVA BIGRAM/TRIGRAM LIGATURE CHECK")
print("="*94)
print(f"  {'cand':<6}{'obs':>8}{'exp':>10}{'enrich':>8}"
      f"{'within':>8}{'cross':>8}{'split':>8}{'chi2':>8}{'p':>10}{'class':>14}")

for r in results:
    enrich = r["enrichment"]
    split = r["split_rate"]
    pval = r["p_value"]
    # Classification
    if enrich >= 3.0 and split <= 0.05 and pval < 0.01:
        cls = "LIGATURE"
    elif enrich <= 1.5 and split >= 0.15:
        cls = "TRUE BIGRAM"
    else:
        cls = "AMBIGUOUS"
    r["classification"] = cls
    currently_collapsed = r["candidate"] in CURRENTLY_COLLAPSED
    r["currently_collapsed"] = currently_collapsed
    expected_class = "LIGATURE" if currently_collapsed else "TRUE BIGRAM"
    r["matches_current_treatment"] = (
        (cls == "LIGATURE" and currently_collapsed) or
        (cls == "TRUE BIGRAM" and not currently_collapsed) or
        (cls == "AMBIGUOUS")
    )
    print(f"  {r['candidate']:<6}{r['observed']:>8}{r['expected']:>10}"
          f"{enrich:>8.2f}{r['within_word']:>8}{r['cross_boundary']:>8}"
          f"{split:>8.3f}{r['chi2']:>8.1f}{pval:>10.4f}{cls:>14}")

# =============================================================================
# Overall verdict
# =============================================================================
collapsed_tests = [r for r in results if r["currently_collapsed"]]
noncollapsed_tests = [r for r in results if not r["currently_collapsed"]]
all_collapsed_ligature = all(r["classification"] == "LIGATURE" for r in collapsed_tests)
any_noncollapsed_ligature = any(r["classification"] == "LIGATURE" for r in noncollapsed_tests)
any_collapsed_true_bigram = any(r["classification"] == "TRUE BIGRAM" for r in collapsed_tests)

print("\n" + "="*94)
print("  OVERALL TOKENISATION VERDICT")
print("="*94)
print(f"  Currently-collapsed ({', '.join(sorted(CURRENTLY_COLLAPSED))}):")
for r in collapsed_tests:
    print(f"    {r['candidate']:<5} -> {r['classification']}  "
          f"{'(matches current treatment)' if r['classification']=='LIGATURE' else '(CONTRADICTS current treatment)'}")
print(f"  Currently-uncollapsed (qo, ol):")
for r in noncollapsed_tests:
    print(f"    {r['candidate']:<5} -> {r['classification']}  "
          f"{'(CONTRADICTS current treatment — should be collapsed)' if r['classification']=='LIGATURE' else '(matches current treatment)'}")

if any_collapsed_true_bigram or any_noncollapsed_ligature:
    overall = "MIS-PARSING DETECTED"
    print(f"\n  -> MIS-PARSING DETECTED. The current EVA tokenisation disagrees with")
    print(f"     the locked classification for at least one candidate.")
elif all_collapsed_ligature and not any_noncollapsed_ligature:
    overall = "VALIDATED"
    print(f"\n  -> VALIDATED. Current EVA tokenisation is consistent with the locked")
    print(f"     classification for all tested candidates. H-BV-SUFFIX-SEQUENCE-01")
    print(f"     can proceed on existing data without re-tokenisation.")
else:
    overall = "AMBIGUOUS"
    print(f"\n  -> AMBIGUOUS. Mixed classifications; some candidates fall in the")
    print(f"     AMBIGUOUS zone. Current tokenisation not contradicted but not")
    print(f"     strongly validated either. Interpret downstream morphology with care.")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "ligature_check_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-LIGATURE-CHECK-01",
    "corpus_words": n_words,
    "total_within_word_chars": total_chars,
    "total_2grams_within_words": total_2grams,
    "total_3grams_within_words": total_3grams,
    "candidates": results,
    "currently_collapsed_ligatures": list(CURRENTLY_COLLAPSED),
    "overall_verdict": overall,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
