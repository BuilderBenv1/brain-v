"""
Execute pre-registered H-BV-EXTERNAL-PREDICTIONS-01.

Tests Hand A against three external structural predictions from prior
Voynich researchers:

  Test 1 (Stolfi 2000):  crust-only fraction in [0.70, 0.80]
  Test 2 (Stolfi 2000):  prefix/suffix dealer asymmetry ratio < 0.25 (q-initial excluded)
  Test 3 (Caveney 2020): word-final n fraction in [0.85, 1.00]

Decision rule (locked): 3/3 STRONG; 2/3 MODERATE; 0-1/3 WEAK.

Pre-registration file: hypotheses/H-BV-EXTERNAL-PREDICTIONS-01.json
Pass bands are locked there and not adjusted by this script.
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

CORE_LIGATURES = ["cth", "cph", "ckh", "cfh"]
MANTLE_LIGATURES = ["ch", "sh", "ee"]
CORE_SINGLES = ["t", "p", "k", "f"]

CORE_SET = set(CORE_LIGATURES + CORE_SINGLES)
MANTLE_SET = set(MANTLE_LIGATURES)
CRUST_SET = set(["d", "l", "r", "s", "n", "x", "i", "m", "g", "q", "o", "y", "a", "e"])

MULTI = sorted(CORE_LIGATURES + MANTLE_LIGATURES, key=lambda s: -len(s))


def tokenize(word):
    out = []
    i = 0
    while i < len(word):
        matched = False
        for t in MULTI:
            if word.startswith(t, i):
                out.append(t)
                i += len(t)
                matched = True
                break
        if not matched:
            out.append(word[i])
            i += 1
    return out


def classify(g):
    if g in CORE_SET:
        return "core"
    if g in MANTLE_SET:
        return "mantle"
    if g in CRUST_SET:
        return "crust"
    return "other"


hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

hand_a_words = [w for w in hand_a_words if w]
n_tokens = len(hand_a_words)
print(f"Hand A word tokens: {n_tokens}")

tokenised = [tokenize(w) for w in hand_a_words]

unknown_glyphs = set()
for t in tokenised:
    for g in t:
        if classify(g) == "other":
            unknown_glyphs.add(g)
print(f"Unknown/other glyphs encountered: {sorted(unknown_glyphs)}")


def has_core(toks):
    return any(g in CORE_SET for g in toks)


def has_mantle(toks):
    return any(g in MANTLE_SET for g in toks)


crust_only_count = sum(
    1 for t in tokenised if not has_core(t) and not has_mantle(t) and t
)
crust_only_fraction = crust_only_count / n_tokens

T1_pass = 0.70 <= crust_only_fraction <= 0.80
print(
    f"\nTest 1 (Stolfi crust-only): {crust_only_count}/{n_tokens} = "
    f"{crust_only_fraction:.4f}  band [0.70, 0.80]  "
    f"{'PASS' if T1_pass else 'FAIL'}"
)

q_initial_excluded_tokens = [t for t in tokenised if t and t[0] != "q"]
split_tokens = [t for t in q_initial_excluded_tokens if has_core(t)]
n_split = len(split_tokens)

prefix_dealer_counts = []
suffix_dealer_counts = []
for t in split_tokens:
    first_core_idx = next(i for i, g in enumerate(t) if g in CORE_SET)
    prefix = t[:first_core_idx]
    suffix = t[first_core_idx + 1:]
    prefix_dealer_counts.append(sum(1 for g in prefix if g in CRUST_SET))
    suffix_dealer_counts.append(sum(1 for g in suffix if g in CRUST_SET))

prefix_mean = sum(prefix_dealer_counts) / n_split if n_split else 0.0
suffix_mean = sum(suffix_dealer_counts) / n_split if n_split else 0.0
asymmetry_ratio = prefix_mean / suffix_mean if suffix_mean > 0 else float("inf")

T2_pass = asymmetry_ratio < 0.25
print(
    f"\nTest 2 (Stolfi asymmetry, q-initial excluded):"
    f"\n  tokens with >=1 core:      {n_split}"
    f"\n  prefix dealer mean:        {prefix_mean:.4f}  (Stolfi ~0.14)"
    f"\n  suffix dealer mean:        {suffix_mean:.4f}  (Stolfi ~0.80)"
    f"\n  asymmetry ratio (pfx/sfx): {asymmetry_ratio:.4f}  threshold < 0.25  "
    f"{'PASS' if T2_pass else 'FAIL'}"
)

final_n_count = sum(1 for t in tokenised if t and t[-1] == "n")
final_n_fraction = final_n_count / n_tokens
T3_pass = 0.85 <= final_n_fraction <= 1.00
print(
    f"\nTest 3 (Caveney word-final n, locked metric): {final_n_count}/{n_tokens} = "
    f"{final_n_fraction:.4f}  band [0.85, 1.00]  "
    f"{'PASS' if T3_pass else 'FAIL'}"
)

total_n_occurrences = sum(g == "n" for t in tokenised for g in t)
n_occurrences_final = sum(1 for t in tokenised if t and t[-1] == "n")
caveney_original_metric = (
    n_occurrences_final / total_n_occurrences if total_n_occurrences else 0.0
)
print(
    f"  DIAGNOSTIC (Caveney's actual claim, not locked): of all n occurrences, "
    f"word-final = {n_occurrences_final}/{total_n_occurrences} = "
    f"{caveney_original_metric:.4f}"
)

no_core_count = sum(1 for t in tokenised if t and not has_core(t))
no_core_fraction = no_core_count / n_tokens
print(
    f"\nDIAGNOSTIC (not locked): no-core fraction (allowing mantle): "
    f"{no_core_count}/{n_tokens} = {no_core_fraction:.4f}"
)

single_glyph_count = sum(1 for t in tokenised if len(t) == 1)
ch_sh_count = sum(1 for t in tokenised if has_mantle(t))
print(
    f"DIAGNOSTIC: tokens with mantle (ch/sh/ee present): "
    f"{ch_sh_count}/{n_tokens} = {ch_sh_count/n_tokens:.4f}"
)
print(
    f"DIAGNOSTIC: single-glyph tokens: "
    f"{single_glyph_count}/{n_tokens} = {single_glyph_count/n_tokens:.4f}"
)

print("\n" + "=" * 78)
print("  LOCKED DECISION")
print("=" * 78)
passes = [T1_pass, T2_pass, T3_pass]
n_pass = sum(passes)
if n_pass == 3:
    verdict = "STRONG_CONVERGENCE"
elif n_pass == 2:
    verdict = "MODERATE_CONVERGENCE"
else:
    verdict = "WEAK_CONVERGENCE"

print(f"  Passes: {n_pass}/3")
print(f"    T1 Stolfi crust-only:         {'PASS' if T1_pass else 'FAIL'}")
print(f"    T2 Stolfi asymmetry:          {'PASS' if T2_pass else 'FAIL'}")
print(f"    T3 Caveney word-final n:      {'PASS' if T3_pass else 'FAIL'}")
print(f"  VERDICT: {verdict}")

out_path = ROOT / "outputs" / "external_predictions_test.json"
out_path.write_text(
    json.dumps(
        {
            "generated": "2026-04-17",
            "hypothesis": "H-BV-EXTERNAL-PREDICTIONS-01",
            "n_hand_a_tokens": n_tokens,
            "unknown_glyphs": sorted(unknown_glyphs),
            "stolfi_categories": {
                "core": sorted(CORE_SET),
                "mantle": sorted(MANTLE_SET),
                "crust": sorted(CRUST_SET),
            },
            "test_1_stolfi_crust_only": {
                "count": crust_only_count,
                "fraction": round(crust_only_fraction, 4),
                "pass_band": [0.70, 0.80],
                "pass": T1_pass,
            },
            "test_2_stolfi_asymmetry": {
                "n_tokens_with_core_non_q_initial": n_split,
                "prefix_dealer_mean": round(prefix_mean, 4),
                "suffix_dealer_mean": round(suffix_mean, 4),
                "asymmetry_ratio": round(asymmetry_ratio, 4),
                "stolfi_expected_prefix": 0.14,
                "stolfi_expected_suffix": 0.80,
                "stolfi_expected_ratio": 0.175,
                "threshold": "< 0.25",
                "pass": T2_pass,
            },
            "test_3_caveney_final_n": {
                "count": final_n_count,
                "fraction": round(final_n_fraction, 4),
                "pass_band": [0.85, 1.00],
                "pass": T3_pass,
                "diagnostic_caveney_original_metric": {
                    "description": "of all n occurrences, fraction that are word-final",
                    "total_n_occurrences": total_n_occurrences,
                    "n_occurrences_word_final": n_occurrences_final,
                    "fraction": round(caveney_original_metric, 4),
                    "note": "not the pre-registered metric; included as diagnostic",
                },
            },
            "diagnostics": {
                "no_core_fraction_allowing_mantle": round(no_core_fraction, 4),
                "mantle_present_fraction": round(ch_sh_count / n_tokens, 4),
                "single_glyph_token_fraction": round(single_glyph_count / n_tokens, 4),
            },
            "n_pass": n_pass,
            "verdict": verdict,
        },
        indent=2,
        default=str,
    ),
    encoding="utf-8",
)
print(f"\nSaved: {out_path}")
