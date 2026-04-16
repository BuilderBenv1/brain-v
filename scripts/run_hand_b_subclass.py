"""
Execute pre-registered H-BV-HAND-B-SUBCLASS-01.

Replicate SUFFIX-SUBCLASS-01 methodology on Hand B tokens using the
same locked partition and top-5 outer set imported from Hand A.

Locked decision rule:
  CONFIRMED shared morphology: ALL 5 outers >=3x differential AND
    >=1 categorical (100% sub-class-exclusive) gap
  REFUTED Hand-B-differs: ALL 5 outers <2x differential AND 0
    categorical gaps
  MARGINAL: anything else
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
TOP5_OUTERS = ["y", "n", "r", "ol", "l"]
TOP5_SET = set(TOP5_OUTERS)

# =============================================================================
# Build Hand B tokens
# =============================================================================
hand_b_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "B":
        continue
    for line in f["lines"]:
        hand_b_words.extend(line["words"])

print(f"Hand B tokens: {len(hand_b_words)}")

tokenised = [tokenize(w) for w in hand_b_words]
valid = [t for t in tokenised if len(t) >= 3]
n_valid = len(valid)
print(f"Hand B tokens with >=3 glyph-units (Tokenisation A): {n_valid}")

inners = [t[-2] for t in valid]
outers = [t[-1] for t in valid]

# =============================================================================
# M4 — Diagnostic: Hand B's native top-10 inner and top-5 outer
# =============================================================================
inner_counts = Counter(inners)
outer_counts = Counter(outers)
native_top10_inner = [g for g, _ in inner_counts.most_common(10)]
native_top5_outer = [g for g, _ in outer_counts.most_common(5)]
print(f"\nHand B native top-10 inner (diagnostic): {native_top10_inner}")
print(f"Hand B native top-5 outer  (diagnostic): {native_top5_outer}")
print(f"(Hand A reference: inner {sorted(VOWEL_INNERS | CONSONANT_INNERS)}; outer {TOP5_OUTERS})")

# =============================================================================
# M1 — Per-sub-class ordering ratios
# =============================================================================
def ratio_for(subclass, label):
    n_in = sum(1 for i in inners if i in subclass)
    n_out = sum(1 for i in inners if i not in subclass)
    n_top5_given_in = sum(1 for i, o in zip(inners, outers)
                          if i in subclass and o in TOP5_SET)
    n_top5_given_out = sum(1 for i, o in zip(inners, outers)
                            if i not in subclass and o in TOP5_SET)
    p_in = n_top5_given_in / n_in if n_in else 0.0
    p_out = n_top5_given_out / n_out if n_out else 0.0
    ratio = p_in / p_out if p_out > 0 else float("inf")
    print(f"\n  M1 ratio for {label}:")
    print(f"    Inner in {label}:     {n_in} tokens")
    print(f"    Inner not in {label}: {n_out} tokens")
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
print("  M1 — per-sub-class ordering ratios (Hand B)")
print("="*78)
vowel_result = ratio_for(VOWEL_INNERS, "VOWEL")
consonant_result = ratio_for(CONSONANT_INNERS, "CONSONANT")

# =============================================================================
# M2 — 2x5 outer preference table
# =============================================================================
print("\n" + "="*78)
print("  M2 — sub-class outer preference (Hand B)")
print("="*78)

vowel_outer_counts = Counter()
cons_outer_counts = Counter()
vowel_total = 0
cons_total = 0
for i, o in zip(inners, outers):
    if i in VOWEL_INNERS:
        vowel_total += 1
        if o in TOP5_SET:
            vowel_outer_counts[o] += 1
    elif i in CONSONANT_INNERS:
        cons_total += 1
        if o in TOP5_SET:
            cons_outer_counts[o] += 1

print(f"\n  Vowel-inner tokens: {vowel_total};  Consonant-inner tokens: {cons_total}")
print(f"\n  {'outer':<6} {'p_vowel':>10} {'p_cons':>10} {'diff (V/C)':>14} {'note':<30}")
print(f"  {'-'*6} {'-'*10} {'-'*10} {'-'*14} {'-'*30}")

m2_table = {}
categorical_gaps = 0
all_3x = True
all_below_2x = True
flags = {}
for o in TOP5_OUTERS:
    p_v = vowel_outer_counts[o] / vowel_total if vowel_total else 0.0
    p_c = cons_outer_counts[o] / cons_total if cons_total else 0.0

    if p_c == 0 and p_v > 0:
        diff = float("inf"); diff_str = "vowel-excl"; flag = "vowel-exclusive (categorical)"
        categorical_gaps += 1
        all_below_2x = False
    elif p_v == 0 and p_c > 0:
        diff = 0.0; diff_str = "cons-excl"; flag = "consonant-exclusive (categorical)"
        categorical_gaps += 1
        all_below_2x = False
    elif p_v == 0 and p_c == 0:
        diff = 1.0; diff_str = "0/0"; flag = "no attachments either sub-class"
        all_3x = False
    else:
        diff = p_v / p_c
        diff_str = f"{diff:.3f}"
        if diff >= 3.0:
            flag = ">=3x vowel-preferring"
            all_below_2x = False
        elif diff <= 1.0/3.0:
            flag = ">=3x consonant-preferring"
            all_below_2x = False
        elif diff >= 2.0 or diff <= 0.5:
            flag = ">=2x but <3x"
            all_below_2x = False
            all_3x = False
        else:
            flag = "<2x (weak)"
            all_3x = False

    print(f"  {o:<6} {p_v:>10.4f} {p_c:>10.4f} {diff_str:>14} {flag:<30}")
    m2_table[o] = {
        "p_vowel": round(p_v, 4),
        "p_cons": round(p_c, 4),
        "diff_v_over_c": diff_str,
        "flag": flag,
    }
    flags[o] = flag

# =============================================================================
# M3 — Categorical-gap count + locked decision
# =============================================================================
print("\n" + "="*78)
print("  M3 — categorical-gap count + LOCKED DECISION")
print("="*78)
print(f"  Categorical (100% sub-class-exclusive) outers: {categorical_gaps}")
print(f"  All 5 outers >=3x differential? {all_3x}")
print(f"  All 5 outers <2x differential? {all_below_2x}")

if all_3x and categorical_gaps >= 1:
    verdict = "CONFIRMED_SHARED_MORPHOLOGY"
    rationale = f"All 5 top-5 outers >=3x sub-class-differential AND {categorical_gaps} categorical gap(s); Hand A pattern replicates in Hand B"
elif all_below_2x and categorical_gaps == 0:
    verdict = "REFUTED_HAND_B_DIFFERS"
    rationale = "All 5 outers show <2x differential AND zero categorical gaps; Hand B has different morphology from Hand A"
else:
    verdict = "MARGINAL"
    n_ge3 = sum(1 for o in TOP5_OUTERS if m2_table[o]["flag"].startswith(">=3x"))
    rationale = (f"{n_ge3}/5 outers cross the 3x threshold; "
                 f"{categorical_gaps} categorical gap(s); intermediate pattern")

print(f"\n  VERDICT: {verdict}")
print(f"  {rationale}")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "hand_b_subclass_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-17",
    "hypothesis": "H-BV-HAND-B-SUBCLASS-01",
    "tokenisation": "A (MULTI_GLYPHS + 'ol')",
    "n_hand_b_valid_tokens": n_valid,
    "locked_partition": {
        "VOWEL_INNERS": sorted(VOWEL_INNERS),
        "CONSONANT_INNERS": sorted(CONSONANT_INNERS),
        "TOP5_OUTERS": TOP5_OUTERS,
    },
    "M4_hand_b_native_inventories": {
        "top10_inner": native_top10_inner,
        "top5_outer": native_top5_outer,
        "note": "diagnostic only; not used in decision"
    },
    "M1_vowel": vowel_result,
    "M1_consonant": consonant_result,
    "M2_outer_preference": m2_table,
    "M3_categorical_gaps": categorical_gaps,
    "all_5_outers_above_3x": all_3x,
    "all_5_outers_below_2x": all_below_2x,
    "verdict": verdict,
    "rationale": rationale,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
