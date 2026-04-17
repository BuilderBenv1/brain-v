"""
Execute pre-registered H-BV-RECONCILED-RERUN-01.

Prerequisite sanity check + three re-runs (T1, T2, M4) under the
reconciled configuration from H-BV-STOLFI-RECONCILIATION-01.
"""
import json
import statistics
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI = sorted(["cth", "cph", "ckh", "cfh", "ch", "sh", "ee"], key=lambda s: -len(s))
CORE_SET = {"t", "p", "k", "f", "cth", "cph", "ckh", "cfh"}
MANTLE_SET = {"ch", "sh", "ee"}
DEALERS = {"d", "l", "r", "s", "n", "x", "i", "m", "g"}
CIRCLES = {"a", "o", "y"}
NON_STANDARD = {"b", "c", "j", "u", "v", "z"}

STOLFI_TARGET = 0.80
SANITY_TOLERANCE = 0.05

COMPOSITE_PAIRS = [
    ("l", "y"), ("r", "y"), ("ol", "y"), ("r", "ol"), ("l", "ol"),
    ("n", "y"), ("r", "l"), ("y", "l"), ("n", "ol"), ("y", "ol"),
]
COMPOSITE_LOOKUP = set(COMPOSITE_PAIRS)


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


def load_words(currier_filter=None):
    words = []
    for f in CORPUS["folios"]:
        if currier_filter is not None and f.get("currier_language") != currier_filter:
            continue
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    words.append(w)
    return [tokenize(w) for w in words]


whole = load_words(None)
hand_a = load_words("A")
hand_b = load_words("B")
print(f"Whole manuscript tokens: {len(whole)}")
print(f"Hand A: {len(hand_a)}  Hand B: {len(hand_b)}")


def passes_filters(t):
    if not t:
        return False
    if t[0] == "q":
        return False
    if any(g in NON_STANDARD for g in t):
        return False
    return True


def strict_layer_suffix(t, first_core_idx):
    out = []
    for g in t[first_core_idx + 1:]:
        if g in MANTLE_SET:
            break
        out.append(g)
    return out


def strict_layer_prefix(t, first_core_idx):
    out = []
    for g in reversed(t[:first_core_idx]):
        if g in MANTLE_SET:
            break
        out.append(g)
    return list(reversed(out))


def reconciled_suffix_dealer_mean(tokens):
    counts = []
    for t in tokens:
        if not passes_filters(t):
            continue
        core_positions = [i for i, g in enumerate(t) if g in CORE_SET]
        if not core_positions:
            continue
        suffix = strict_layer_suffix(t, core_positions[0])
        counts.append(sum(1 for g in suffix if g in DEALERS))
    return counts


print("\n=== PREREQUISITE SANITY CHECK ===")
sanity_counts = reconciled_suffix_dealer_mean(whole)
sanity_mean = statistics.mean(sanity_counts) if sanity_counts else 0.0
sanity_delta = sanity_mean - STOLFI_TARGET
sanity_pass = abs(sanity_delta) <= SANITY_TOLERANCE
print(f"  reconciled_whole_suffix_mean = {sanity_mean:.4f}")
print(f"  stolfi_target                = {STOLFI_TARGET}")
print(f"  |delta|                      = {abs(sanity_delta):.4f}  tolerance {SANITY_TOLERANCE}")
print(f"  SANITY: {'PASS' if sanity_pass else 'FAIL'}")

if not sanity_pass:
    print("\nHALTING: sanity check failed. Reconciled config not correctly implemented.")
    raise SystemExit(1)


def crust_only_fraction(tokens):
    numer = 0
    denom = 0
    for t in tokens:
        if not passes_filters(t):
            continue
        denom += 1
        if not any(g in CORE_SET for g in t) and not any(g in MANTLE_SET for g in t):
            numer += 1
    return numer, denom, (numer / denom if denom else 0.0)


print("\n=== RE-RUN T1: RECONCILED CRUST-ONLY FRACTION ===")
t1_n_whole, t1_d_whole, t1_frac_whole = crust_only_fraction(whole)
t1_n_A, t1_d_A, t1_frac_A = crust_only_fraction(hand_a)
t1_n_B, t1_d_B, t1_frac_B = crust_only_fraction(hand_b)
t1_pass = 0.70 <= t1_frac_whole <= 0.80
print(f"  whole: {t1_n_whole}/{t1_d_whole} = {t1_frac_whole:.4f}  band [0.70, 0.80]  {'PASS' if t1_pass else 'FAIL'}")
print(f"  A:     {t1_n_A}/{t1_d_A} = {t1_frac_A:.4f}")
print(f"  B:     {t1_n_B}/{t1_d_B} = {t1_frac_B:.4f}")

def crust_only_fraction_no_filter(tokens):
    """Diagnostic only: same definition but without q-initial or non-standard exclusion.
    Stolfi's 75% figure was on 'normal tokens' which includes q-initial."""
    numer = 0
    denom = 0
    for t in tokens:
        if not t:
            continue
        if any(g in NON_STANDARD for g in t):
            continue
        denom += 1
        if not any(g in CORE_SET for g in t) and not any(g in MANTLE_SET for g in t):
            numer += 1
    return numer, denom, (numer / denom if denom else 0.0)

t1d_n_whole, t1d_d_whole, t1d_frac_whole = crust_only_fraction_no_filter(whole)
print(f"  DIAGNOSTIC (no q-exclusion, matches Stolfi scope): {t1d_n_whole}/{t1d_d_whole} = {t1d_frac_whole:.4f}")


def reconciled_prefix_suffix(tokens):
    prefix_counts = []
    suffix_counts = []
    for t in tokens:
        if not passes_filters(t):
            continue
        core_positions = [i for i, g in enumerate(t) if g in CORE_SET]
        if not core_positions:
            continue
        first_core_idx = core_positions[0]
        prefix = strict_layer_prefix(t, first_core_idx)
        suffix = strict_layer_suffix(t, first_core_idx)
        prefix_counts.append(sum(1 for g in prefix if g in DEALERS))
        suffix_counts.append(sum(1 for g in suffix if g in DEALERS))
    return prefix_counts, suffix_counts


print("\n=== RE-RUN T2: RECONCILED PREFIX/SUFFIX ASYMMETRY ===")
pc_whole, sc_whole = reconciled_prefix_suffix(whole)
pc_A, sc_A = reconciled_prefix_suffix(hand_a)
pc_B, sc_B = reconciled_prefix_suffix(hand_b)

pm_whole = statistics.mean(pc_whole) if pc_whole else 0.0
sm_whole = statistics.mean(sc_whole) if sc_whole else 0.0
ratio_whole = pm_whole / sm_whole if sm_whole else float("inf")
pm_A = statistics.mean(pc_A) if pc_A else 0.0
sm_A = statistics.mean(sc_A) if sc_A else 0.0
ratio_A = pm_A / sm_A if sm_A else float("inf")
pm_B = statistics.mean(pc_B) if pc_B else 0.0
sm_B = statistics.mean(sc_B) if sc_B else 0.0
ratio_B = pm_B / sm_B if sm_B else float("inf")

t2_pass = ratio_whole < 0.25
print(f"  whole: prefix_mean={pm_whole:.4f}  suffix_mean={sm_whole:.4f}  ratio={ratio_whole:.4f}  "
      f"threshold < 0.25  {'PASS' if t2_pass else 'FAIL'}")
print(f"    n split tokens (whole): {len(pc_whole)}")
print(f"  A: prefix={pm_A:.4f}  suffix={sm_A:.4f}  ratio={ratio_A:.4f}")
print(f"  B: prefix={pm_B:.4f}  suffix={sm_B:.4f}  ratio={ratio_B:.4f}")


def composite_reduced_suffix_mean(tokens):
    counts = []
    for t in tokens:
        if not passes_filters(t):
            continue
        core_positions = [i for i, g in enumerate(t) if g in CORE_SET]
        if not core_positions:
            continue
        suffix = strict_layer_suffix(t, core_positions[0])
        n = 0
        i = 0
        while i < len(suffix):
            if (
                i + 1 < len(suffix)
                and (suffix[i], suffix[i + 1]) in COMPOSITE_LOOKUP
                and suffix[i] in DEALERS
                and suffix[i + 1] in DEALERS
            ):
                n += 1
                i += 2
                continue
            if suffix[i] in DEALERS:
                n += 1
            i += 1
        counts.append(n)
    return counts


print("\n=== RE-RUN M4: RECONCILED COMPOSITE DECOMPOSITION EFFECT ===")
baseline_A_counts = reconciled_suffix_dealer_mean(hand_a)
composite_A_counts = composite_reduced_suffix_mean(hand_a)
baseline_A = statistics.mean(baseline_A_counts)
composite_A = statistics.mean(composite_A_counts)
delta_A = baseline_A - composite_A

baseline_whole_counts = sanity_counts
composite_whole_counts = composite_reduced_suffix_mean(whole)
baseline_whole = statistics.mean(baseline_whole_counts)
composite_whole = statistics.mean(composite_whole_counts)
delta_whole = baseline_whole - composite_whole

m4_pass = abs(delta_A) >= 0.05
print(f"  Hand A baseline (reconciled):    {baseline_A:.4f}")
print(f"  Hand A composite-reduced:        {composite_A:.4f}")
print(f"  composite_delta_A:               {delta_A:+.4f}  threshold |delta|>=0.05  {'PASS' if m4_pass else 'FAIL'}")
print(f"  Whole baseline (reconciled):     {baseline_whole:.4f}")
print(f"  Whole composite-reduced:         {composite_whole:.4f}")
print(f"  composite_delta_whole:           {delta_whole:+.4f}")

print("\n" + "=" * 78)
print("  AGGREGATE VERDICT")
print("=" * 78)
passes = [("T1", t1_pass), ("T2", t2_pass), ("M4", m4_pass)]
n_pass = sum(1 for _, p in passes if p)
if n_pass == 3:
    aggregate = "STRONG_SURVIVAL"
elif n_pass == 2:
    aggregate = "MODERATE_SURVIVAL"
elif n_pass == 1:
    aggregate = "WEAK_SURVIVAL"
else:
    aggregate = "NO_SURVIVAL"

for name, p in passes:
    print(f"  {name} reconciled: {'PASS' if p else 'FAIL'}")
print(f"  AGGREGATE: {n_pass}/3 -> {aggregate}")

status_map = {}

t1_original_verdict = "FAIL (0.2718, band [0.70, 0.80])"
t1_reconciled_verdict = f"{'PASS' if t1_pass else 'FAIL'} ({t1_frac_whole:.4f}, band [0.70, 0.80])"
status_map["T1"] = {
    "original_scope": "Hand A only",
    "reconciled_scope": "whole manuscript",
    "original_verdict": t1_original_verdict,
    "reconciled_verdict": t1_reconciled_verdict,
    "status": "survived" if t1_pass else "still_fails",
}

t2_original_verdict = "FAIL (ratio 0.2912, threshold < 0.25)"
t2_reconciled_verdict = f"{'PASS' if t2_pass else 'FAIL'} (ratio {ratio_whole:.4f}, threshold < 0.25)"
status_map["T2"] = {
    "original_scope": "Hand A only, BV CRUST",
    "reconciled_scope": "whole manuscript, Stolfi DEALERS + strict_layer",
    "original_verdict": t2_original_verdict,
    "reconciled_verdict": t2_reconciled_verdict,
    "status": "reversed_to_pass" if t2_pass else "still_fails",
}

m4_original_verdict = "FAIL (anomaly_reduction 0.244, threshold >= 0.50)"
m4_reconciled_verdict = f"{'PASS' if m4_pass else 'FAIL'} (|composite_delta_A| = {abs(delta_A):.4f}, threshold >= 0.05)"
status_map["M4"] = {
    "original_scope": "Hand A under BV CRUST, 'close 1.62 excess'",
    "reconciled_scope": "Hand A under DEALERS + strict_layer, 'meaningful effect >=0.05'",
    "original_verdict": m4_original_verdict,
    "reconciled_verdict": m4_reconciled_verdict,
    "status": "moot_under_reconciliation" if not m4_pass else "meaningful_effect",
}

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-RECONCILED-RERUN-01",
    "n_whole_tokens": len(whole),
    "n_hand_a_tokens": len(hand_a),
    "n_hand_b_tokens": len(hand_b),
    "sanity_check": {
        "reconciled_whole_suffix_mean": round(sanity_mean, 4),
        "stolfi_target": STOLFI_TARGET,
        "delta": round(sanity_delta, 4),
        "tolerance": SANITY_TOLERANCE,
        "pass": sanity_pass,
    },
    "T1_crust_only_fraction": {
        "whole": {"numerator": t1_n_whole, "denominator": t1_d_whole, "fraction": round(t1_frac_whole, 4)},
        "A": {"numerator": t1_n_A, "denominator": t1_d_A, "fraction": round(t1_frac_A, 4)},
        "B": {"numerator": t1_n_B, "denominator": t1_d_B, "fraction": round(t1_frac_B, 4)},
        "pass_band": [0.70, 0.80],
        "pass": t1_pass,
        "diagnostic_no_q_exclusion": {
            "numerator": t1d_n_whole,
            "denominator": t1d_d_whole,
            "fraction": round(t1d_frac_whole, 4),
            "note": "Stolfi's 75% figure was on normal tokens including q-initial. q-initial tokens have a CORE (q-word like qokedy has k core), so they are NOT crust-only — adding them to the denominator while adding none to the numerator REDUCES the crust-only fraction, not increases it. Diagnostic lets us see direction and magnitude.",
        },
    },
    "T2_asymmetry": {
        "whole": {"prefix_mean": round(pm_whole, 4), "suffix_mean": round(sm_whole, 4), "ratio": round(ratio_whole, 4), "n_split": len(pc_whole)},
        "A": {"prefix_mean": round(pm_A, 4), "suffix_mean": round(sm_A, 4), "ratio": round(ratio_A, 4), "n_split": len(pc_A)},
        "B": {"prefix_mean": round(pm_B, 4), "suffix_mean": round(sm_B, 4), "ratio": round(ratio_B, 4), "n_split": len(pc_B)},
        "threshold": "< 0.25",
        "pass": t2_pass,
    },
    "M4_composite_effect": {
        "baseline_A": round(baseline_A, 4),
        "composite_A": round(composite_A, 4),
        "composite_delta_A": round(delta_A, 4),
        "baseline_whole": round(baseline_whole, 4),
        "composite_whole": round(composite_whole, 4),
        "composite_delta_whole": round(delta_whole, 4),
        "threshold": "|composite_delta_A| >= 0.05",
        "pass": m4_pass,
    },
    "per_test_status": status_map,
    "n_pass": n_pass,
    "aggregate_verdict": aggregate,
}
out_path = ROOT / "outputs" / "reconciled_rerun_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
