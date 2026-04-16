"""
Execute pre-registered H-BV-SUFFIX-SUBCLASS-01.

Partition H-BV-SUFFIX-SEQUENCE-01's top-10 inner inventory into:
  VOWEL-INNERS   = {i, e, o, a}
  CONSONANT-INNERS = {ch, d, k, t, sh, l}

Using Tokenisation A (MULTI_GLYPHS + 'ol'), Hand A tokens with
N >= 3 glyph-units, re-decompose as STEM+INNER+OUTER and compute:

  M1   ratio_S = P(outer top5 | inner in S) / P(outer top5 | inner not in S)
        per sub-class S
  M1b  combined ratio (sanity: must match SUFFIX-SEQUENCE-01 value ~1.12
        or ~1.10 depending on comparator definition — here using
        'inner not in S' as comparator for M1, so M1b uses
        'inner outside top-10' comparator)
  M2   2x5 outer preference table with vowel/consonant differentials

DECISION (LOCKED):
  CONFIRMED if max(ratio_VOWEL, ratio_CONSONANT) >= 2.0
  REFUTED   if both < 1.5 AND no outer differential >= 3.0 or <= 1/3
  MARGINAL  otherwise
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

VOWEL_INNERS = {"i", "e", "o", "a"}
CONSONANT_INNERS = {"ch", "d", "k", "t", "sh", "l"}
TOP10 = VOWEL_INNERS | CONSONANT_INNERS
TOP5_OUTERS = {"y", "n", "r", "ol", "l"}

# Build Hand A token list
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

print(f"Hand A tokens: {len(hand_a_words)}")

tokenised = [tokenize(w) for w in hand_a_words]
valid = [t for t in tokenised if len(t) >= 3]
n_valid = len(valid)
print(f"Tokens with >=3 glyph-units (Tokenisation A): {n_valid}")

inners = [t[-2] for t in valid]
outers = [t[-1] for t in valid]

# Sanity: reproduce top-10 inner and top-5 outer
inner_counts = Counter(inners)
outer_counts = Counter(outers)
print("\nSanity check — top-10 inner (from SUFFIX-SEQUENCE-01 expected i,e,o,a,ch,d,k,t,sh,l):")
print(f"  {[g for g,_ in inner_counts.most_common(10)]}")
print("Sanity check — top-5 outer (expected y,n,r,ol,l):")
print(f"  {[g for g,_ in outer_counts.most_common(5)]}")

# =============================================================================
# M1 — per-sub-class ordering ratios
# =============================================================================
def ratio_for(subclass, label):
    n_in = sum(1 for i in inners if i in subclass)
    n_out = sum(1 for i in inners if i not in subclass)
    n_top5_given_in = sum(1 for i, o in zip(inners, outers)
                          if i in subclass and o in TOP5_OUTERS)
    n_top5_given_out = sum(1 for i, o in zip(inners, outers)
                            if i not in subclass and o in TOP5_OUTERS)
    p_in = n_top5_given_in / n_in if n_in else 0.0
    p_out = n_top5_given_out / n_out if n_out else 0.0
    ratio = p_in / p_out if p_out > 0 else float("inf")
    print(f"\n  M1 ratio for {label}:")
    print(f"    Inner in {label}:        {n_in} tokens")
    print(f"    Inner not in {label}:    {n_out} tokens")
    print(f"    P(outer top5 | in {label}):     {p_in:.4f}  ({n_top5_given_in}/{n_in})")
    print(f"    P(outer top5 | not in {label}): {p_out:.4f}  ({n_top5_given_out}/{n_out})")
    print(f"    ratio = {ratio:.3f}")
    return {
        "label": label,
        "n_in_subclass": n_in,
        "n_not_in_subclass": n_out,
        "p_top5_given_in": round(p_in, 4),
        "p_top5_given_not_in": round(p_out, 4),
        "ratio": round(ratio, 3) if ratio != float("inf") else "inf",
    }

print("\n" + "="*78)
print("  M1 — per-sub-class ordering ratios")
print("="*78)
vowel_result = ratio_for(VOWEL_INNERS, "VOWEL")
consonant_result = ratio_for(CONSONANT_INNERS, "CONSONANT")

# =============================================================================
# M1b — combined ratio (comparator = outside top-10)
# =============================================================================
print("\n" + "="*78)
print("  M1b — combined ratio (comparator = outside top-10)")
print("="*78)
n_top10 = sum(1 for i in inners if i in TOP10)
n_out10 = sum(1 for i in inners if i not in TOP10)
n_top5_given_top10 = sum(1 for i, o in zip(inners, outers)
                          if i in TOP10 and o in TOP5_OUTERS)
n_top5_given_out10 = sum(1 for i, o in zip(inners, outers)
                          if i not in TOP10 and o in TOP5_OUTERS)
p_top10 = n_top5_given_top10 / n_top10 if n_top10 else 0.0
p_out10 = n_top5_given_out10 / n_out10 if n_out10 else 0.0
combined_ratio = p_top10 / p_out10 if p_out10 > 0 else float("inf")
print(f"  P(outer top5 | inner in top-10):     {p_top10:.4f}  ({n_top5_given_top10}/{n_top10})")
print(f"  P(outer top5 | inner outside top-10): {p_out10:.4f}  ({n_top5_given_out10}/{n_out10})")
print(f"  combined ratio = {combined_ratio:.3f}  (SUFFIX-SEQUENCE-01 reported 1.12)")

# =============================================================================
# M2 — sub-class outer preference table
# =============================================================================
print("\n" + "="*78)
print("  M2 — sub-class outer preference")
print("="*78)

vowel_outer_counts = Counter()
cons_outer_counts = Counter()
vowel_total = 0
cons_total = 0
for i, o in zip(inners, outers):
    if i in VOWEL_INNERS:
        vowel_total += 1
        if o in TOP5_OUTERS:
            vowel_outer_counts[o] += 1
    elif i in CONSONANT_INNERS:
        cons_total += 1
        if o in TOP5_OUTERS:
            cons_outer_counts[o] += 1

print(f"\n  Vowel-inner tokens: {vowel_total};  Consonant-inner tokens: {cons_total}")
print(f"\n  {'outer':<6} {'p_vowel':>10} {'p_cons':>10} {'diff (V/C)':>14} {'note':<20}")
print(f"  {'-'*6} {'-'*10} {'-'*10} {'-'*14} {'-'*20}")

m2_table = {}
max_diff_from_1 = 1.0
strong_differential = False
for o in ["y", "n", "r", "ol", "l"]:
    p_v = vowel_outer_counts[o] / vowel_total if vowel_total else 0.0
    p_c = cons_outer_counts[o] / cons_total if cons_total else 0.0
    if p_c > 0:
        diff = p_v / p_c
        diff_str = f"{diff:.3f}"
    elif p_v > 0:
        diff = float("inf")
        diff_str = "vowel-excl"
    else:
        diff = 1.0
        diff_str = "0/0"
    note = ""
    if isinstance(diff, float) and diff != float("inf"):
        if diff >= 3.0:
            note = ">=3x vowel-preferring"
            strong_differential = True
        elif diff <= 1/3.0 and diff > 0:
            note = ">=3x cons-preferring"
            strong_differential = True
    elif diff == float("inf"):
        note = "vowel-exclusive"
        strong_differential = True
    print(f"  {o:<6} {p_v:>10.4f} {p_c:>10.4f} {diff_str:>14} {note:<20}")
    m2_table[o] = {
        "p_vowel": round(p_v, 4),
        "p_cons": round(p_c, 4),
        "diff_v_over_c": diff_str,
        "note": note,
    }

# =============================================================================
# LOCKED DECISION
# =============================================================================
print("\n" + "="*78)
print("  LOCKED DECISION")
print("="*78)

r_v = vowel_result["ratio"] if vowel_result["ratio"] != "inf" else float("inf")
r_c = consonant_result["ratio"] if consonant_result["ratio"] != "inf" else float("inf")

max_ratio = max(
    r_v if isinstance(r_v, (int, float)) else float("inf"),
    r_c if isinstance(r_c, (int, float)) else float("inf"),
)

if max_ratio >= 2.0:
    verdict = "CONFIRMED"
    rationale = f"max(ratio_VOWEL={r_v}, ratio_CONSONANT={r_c}) = {max_ratio:.3f} >= 2.0; strict morphology in at least one sub-class"
elif (isinstance(r_v, (int, float)) and r_v < 1.5 and
      isinstance(r_c, (int, float)) and r_c < 1.5 and
      not strong_differential):
    verdict = "REFUTED"
    rationale = f"both ratios < 1.5 (V={r_v}, C={r_c}) AND no outer with >=3x differential; morphology genuinely permissive"
else:
    verdict = "MARGINAL"
    rationale = (f"ratios V={r_v}, C={r_c}; strong_differential={strong_differential}; "
                 f"partial sub-slot structure")

print(f"\n  ratio_VOWEL     = {r_v}")
print(f"  ratio_CONSONANT = {r_c}")
print(f"  combined_ratio  = {combined_ratio:.3f}  (sanity ref = 1.12)")
print(f"  strong sub-class outer differential (>=3x): {strong_differential}")
print(f"\n  VERDICT: {verdict}")
print(f"  {rationale}")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "suffix_subclass_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-SUFFIX-SUBCLASS-01",
    "tokenisation": "A (MULTI_GLYPHS + 'ol')",
    "n_valid_tokens": n_valid,
    "partition": {
        "VOWEL_INNERS": sorted(VOWEL_INNERS),
        "CONSONANT_INNERS": sorted(CONSONANT_INNERS),
        "TOP5_OUTERS": sorted(TOP5_OUTERS),
    },
    "M1_vowel": vowel_result,
    "M1_consonant": consonant_result,
    "M1b_combined": {
        "p_top5_given_top10": round(p_top10, 4),
        "p_top5_given_out10": round(p_out10, 4),
        "ratio": round(combined_ratio, 3),
        "sanity_expected": 1.12,
    },
    "M2_outer_preference": m2_table,
    "strong_differential": strong_differential,
    "verdict": verdict,
    "rationale": rationale,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
