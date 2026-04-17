"""
Execute pre-registered H-BV-STOLFI-RECONCILIATION-01.

Runs 5 sub-tests (S1-S5) to diagnose the 3x Brain-V-vs-Stolfi suffix
dealer mean drift. Primary corpus = whole manuscript (A+B); also
reports Hand A and Hand B separately.

Stolfi DEALERS (verbatim from voynich.nu/hist/stolfi/grammar.html):
  {d, l, r, s, n, x, i, m, g}  — 9 letters
"""
import json
import statistics
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

CRUST_BV = {"d", "l", "r", "s", "n", "x", "i", "m", "g", "q", "o", "y", "a", "e"}
DEALERS_STOLFI_STRICT = {"d", "l", "r", "s", "n", "x", "i", "m", "g"}
CORE_SET = {"t", "p", "k", "f", "cth", "cph", "ckh", "cfh"}
MANTLE_SET = {"ch", "sh", "ee"}
CIRCLES = {"a", "o", "y"}
NON_STANDARD = {"b", "c", "j", "u", "v", "z"}

STOLFI_TARGET = 0.80
STOLFI_TOLERANCE = 0.05


def make_tokenizer(multi):
    multi_sorted = sorted(multi, key=lambda s: -len(s))
    def tokenize(word):
        out = []
        i = 0
        while i < len(word):
            matched = False
            for t in multi_sorted:
                if word.startswith(t, i):
                    out.append(t)
                    i += len(t)
                    matched = True
                    break
            if not matched:
                out.append(word[i])
                i += 1
        return out
    return tokenize


MULTI_STANDARD = ["cth", "cph", "ckh", "cfh", "ch", "sh", "ee"]
tokenize_standard = make_tokenizer(MULTI_STANDARD)


def load_words(currier_filter=None):
    words = []
    for f in CORPUS["folios"]:
        if currier_filter is not None and f.get("currier_language") != currier_filter:
            continue
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    words.append(w)
    return words


raw_whole = load_words(None)
raw_A = load_words("A")
raw_B = load_words("B")
print(f"Whole manuscript tokens (all currier_language): {len(raw_whole)}")
print(f"Hand A: {len(raw_A)}  Hand B: {len(raw_B)}")


def suffix_dealer_counts(
    raw_words,
    tokenize_fn=tokenize_standard,
    dealer_set=CRUST_BV,
    suffix_mode="after_first_core",
    core_set=CORE_SET,
    exclude_q_initial=False,
    exclude_non_standard=False,
    only_split_crust=False,
):
    counts = []
    for w in raw_words:
        t = tokenize_fn(w)
        if not t:
            continue
        if exclude_q_initial and t[0] == "q":
            continue
        if exclude_non_standard and any(g in NON_STANDARD for g in t):
            continue

        core_positions = [i for i, g in enumerate(t) if g in core_set]
        if not core_positions:
            continue

        if suffix_mode == "after_first_core":
            split_at = core_positions[0]
        elif suffix_mode == "after_last_core":
            split_at = core_positions[-1]
        else:
            split_at = core_positions[0]

        prefix = t[:split_at]
        suffix = t[split_at + 1:]

        if only_split_crust:
            if not prefix or not suffix:
                continue

        if suffix_mode == "strict_layer_before_mantle":
            trimmed = []
            for g in suffix:
                if g in MANTLE_SET:
                    break
                trimmed.append(g)
            suffix = trimmed

        counts.append(sum(1 for g in suffix if g in dealer_set))
    return counts


def mean_or_zero(arr):
    return statistics.mean(arr) if arr else 0.0


def mean_on(config, raw_words):
    return mean_or_zero(suffix_dealer_counts(raw_words, **config))


BASELINE = dict(
    tokenize_fn=tokenize_standard,
    dealer_set=CRUST_BV,
    suffix_mode="after_first_core",
    core_set=CORE_SET,
    exclude_q_initial=False,
    exclude_non_standard=False,
    only_split_crust=False,
)

baseline_whole = mean_on(BASELINE, raw_whole)
baseline_A = mean_on(BASELINE, raw_A)
baseline_B = mean_on(BASELINE, raw_B)
print(f"\nBaseline suffix_dealer_mean (Brain-V defaults):")
print(f"  whole={baseline_whole:.4f}  A={baseline_A:.4f}  B={baseline_B:.4f}")


def run_variant(label, config_override, raw_words):
    cfg = dict(BASELINE)
    cfg.update(config_override)
    m = mean_on(cfg, raw_words)
    return {"label": label, "mean": round(m, 4), "delta_vs_baseline": round(m - baseline_whole, 4)}


print("\n=== S1: TOKENISATION SUB-TEST (whole manuscript) ===")
s1_variants = []
for label, multi in [
    ("T1a MULTI = [cth,cph,ckh,cfh,ch,sh,ee]  (Brain-V / Stolfi literal)", ["cth", "cph", "ckh", "cfh", "ch", "sh", "ee"]),
    ("T1b MULTI = [cth,cph,ckh,cfh,ch,sh]      (no ee)", ["cth", "cph", "ckh", "cfh", "ch", "sh"]),
    ("T1c MULTI = [cth,cph,ckh,cfh]            (core ligatures only)", ["cth", "cph", "ckh", "cfh"]),
    ("T1d MULTI = []                           (no ligatures)", []),
]:
    tok = make_tokenizer(multi)
    r = run_variant(label, {"tokenize_fn": tok}, raw_whole)
    s1_variants.append(r)
    print(f"  {label}: mean = {r['mean']:.4f}  delta = {r['delta_vs_baseline']:+.4f}")
s1_max = max(s1_variants, key=lambda r: abs(r["delta_vs_baseline"]))

print("\n=== S2: SLOT-ASSIGNMENT SUB-TEST (whole manuscript) ===")
s2_variants = []
for label, dset in [
    ("S2a CRUST_BV (14 letters, Brain-V current)", CRUST_BV),
    ("S2b DEALERS_STOLFI_STRICT (9 letters)", DEALERS_STOLFI_STRICT),
    ("S2c DEALERS_STOLFI_WITH_Q (10 letters)", DEALERS_STOLFI_STRICT | {"q"}),
    ("S2d CRUST_BV - {e} (13 letters)", CRUST_BV - {"e"}),
    ("S2e CRUST_BV - {a,o,y} (11 letters)", CRUST_BV - {"a", "o", "y"}),
]:
    r = run_variant(label, {"dealer_set": dset}, raw_whole)
    s2_variants.append(r)
    print(f"  {label}: mean = {r['mean']:.4f}  delta = {r['delta_vs_baseline']:+.4f}")
s2_max = max(s2_variants, key=lambda r: abs(r["delta_vs_baseline"]))

print("\n=== S3: SUFFIX-DEFINITION SUB-TEST (whole manuscript) ===")
s3_variants = []
for label, override in [
    ("D3a after_first_core (Brain-V current)", {"suffix_mode": "after_first_core"}),
    ("D3b after_last_core", {"suffix_mode": "after_last_core"}),
    ("D3c strict_layer_before_mantle", {"suffix_mode": "strict_layer_before_mantle"}),
    ("D3d only_split_crust", {"only_split_crust": True}),
]:
    r = run_variant(label, override, raw_whole)
    s3_variants.append(r)
    print(f"  {label}: mean = {r['mean']:.4f}  delta = {r['delta_vs_baseline']:+.4f}")
s3_max = max(s3_variants, key=lambda r: abs(r["delta_vs_baseline"]))

print("\n=== S4: TOKEN-FILTERING SUB-TEST (whole manuscript) ===")
s4_variants = []
for label, override in [
    ("F4a all tokens (Brain-V current)", {}),
    ("F4b exclude q-initial", {"exclude_q_initial": True}),
    ("F4c exclude non-standard glyphs", {"exclude_non_standard": True}),
    ("F4d F4b + F4c", {"exclude_q_initial": True, "exclude_non_standard": True}),
]:
    r = run_variant(label, override, raw_whole)
    s4_variants.append(r)
    print(f"  {label}: mean = {r['mean']:.4f}  delta = {r['delta_vs_baseline']:+.4f}")
s4_max = max(s4_variants, key=lambda r: abs(r["delta_vs_baseline"]))

print("\n=== S5: CUMULATIVE STOLFI-LITERAL TEST ===")
CUMULATIVE = dict(
    tokenize_fn=tokenize_standard,
    dealer_set=DEALERS_STOLFI_STRICT,
    suffix_mode="after_first_core",
    core_set=CORE_SET,
    exclude_q_initial=True,
    exclude_non_standard=True,
    only_split_crust=False,
)
cum_whole = mean_on(CUMULATIVE, raw_whole)
cum_A = mean_on(CUMULATIVE, raw_A)
cum_B = mean_on(CUMULATIVE, raw_B)
delta_whole = cum_whole - STOLFI_TARGET
print(f"  Cumulative (Stolfi strict dealers + q-exclusion + non-standard exclusion):")
print(f"    whole = {cum_whole:.4f}  delta vs 0.80 = {delta_whole:+.4f}")
print(f"    A     = {cum_A:.4f}")
print(f"    B     = {cum_B:.4f}")

cumulative_pass = abs(delta_whole) <= STOLFI_TOLERANCE
print(f"  Threshold |delta| <= 0.05:  {'PASS' if cumulative_pass else 'FAIL'}")

print("\n=== DIAGNOSTIC (not locked): EXTENDED CUMULATIVE with S3c strict-layer ===")
EXTENDED_CUM = dict(
    tokenize_fn=tokenize_standard,
    dealer_set=DEALERS_STOLFI_STRICT,
    suffix_mode="strict_layer_before_mantle",
    core_set=CORE_SET,
    exclude_q_initial=True,
    exclude_non_standard=True,
    only_split_crust=False,
)
ext_whole = mean_on(EXTENDED_CUM, raw_whole)
ext_A = mean_on(EXTENDED_CUM, raw_A)
ext_B = mean_on(EXTENDED_CUM, raw_B)
ext_delta = ext_whole - STOLFI_TARGET
print(f"  Extended (adds S3c strict_layer_before_mantle):")
print(f"    whole = {ext_whole:.4f}  delta vs 0.80 = {ext_delta:+.4f}")
print(f"    A     = {ext_A:.4f}")
print(f"    B     = {ext_B:.4f}")

deltas_by_subtest = {
    "S1_tokenisation": s1_max,
    "S2_slot_assignment": s2_max,
    "S3_suffix_definition": s3_max,
    "S4_token_filtering": s4_max,
}
largest = max(
    deltas_by_subtest.items(),
    key=lambda kv: abs(kv[1]["delta_vs_baseline"]),
)
largest_name, largest_variant = largest

print("\n" + "=" * 78)
print("  LOCKED DECISION")
print("=" * 78)
print(f"  LARGEST_SINGLE_SOURCE: {largest_name}")
print(f"    variant: {largest_variant['label']}")
print(f"    delta:   {largest_variant['delta_vs_baseline']:+.4f}")
print(f"  CUMULATIVE: mean={cum_whole:.4f}  delta vs 0.80 = {delta_whole:+.4f}  {'PASS' if cumulative_pass else 'FAIL'}")

if cumulative_pass and largest_name == "S2_slot_assignment":
    verdict = "DIAGNOSED_SLOT_ASSIGNMENT"
elif cumulative_pass:
    verdict = "DIAGNOSED_OTHER_DRIFT"
elif abs(delta_whole) <= 0.15:
    verdict = "PARTIAL_RECONCILIATION"
else:
    verdict = "FUNDAMENTAL_DIFFERENCE"
print(f"  VERDICT: {verdict}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-STOLFI-RECONCILIATION-01",
    "n_whole_tokens": len(raw_whole),
    "n_A_tokens": len(raw_A),
    "n_B_tokens": len(raw_B),
    "baseline_suffix_mean_whole": round(baseline_whole, 4),
    "baseline_suffix_mean_A": round(baseline_A, 4),
    "baseline_suffix_mean_B": round(baseline_B, 4),
    "S1_tokenisation_variants": s1_variants,
    "S2_slot_assignment_variants": s2_variants,
    "S3_suffix_definition_variants": s3_variants,
    "S4_token_filtering_variants": s4_variants,
    "S5_cumulative": {
        "config": "tokenize_standard + DEALERS_STOLFI_STRICT + after_first_core + exclude_q_initial + exclude_non_standard",
        "mean_whole": round(cum_whole, 4),
        "mean_A": round(cum_A, 4),
        "mean_B": round(cum_B, 4),
        "stolfi_target": STOLFI_TARGET,
        "delta_whole_vs_target": round(delta_whole, 4),
        "tolerance": STOLFI_TOLERANCE,
        "pass": cumulative_pass,
    },
    "diagnostic_extended_cumulative": {
        "config": "S2b + S3c + F4b + F4c (adds strict_layer_before_mantle)",
        "mean_whole": round(ext_whole, 4),
        "mean_A": round(ext_A, 4),
        "mean_B": round(ext_B, 4),
        "delta_whole_vs_target": round(ext_delta, 4),
        "note": "Not locked. Diagnostic showing what happens if the cumulative adds S3c (strict layer before mantle) as a fifth component.",
    },
    "largest_single_source": {
        "sub_test": largest_name,
        "variant_label": largest_variant["label"],
        "delta_vs_baseline": largest_variant["delta_vs_baseline"],
    },
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "stolfi_reconciliation_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
