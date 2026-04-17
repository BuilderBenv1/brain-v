"""
Execute pre-registered H-BV-DENSITY-DIAGNOSIS-01.

Diagnoses the 3x Hand-A-vs-Stolfi suffix dealer density gap (Hand A
2.4182 vs Stolfi 0.80). Three non-exclusive candidates:
  (a) inventory richness
  (b) operationalisation drift
  (c) A/B productivity difference

Tokenisation (locked): MULTI = ['cth','cph','ckh','cfh','ch','sh','ee'].
'ol' is NOT a ligature in this test (matches EXTERNAL-PREDICTIONS-01).
"""
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path

try:
    from scipy.stats import ttest_ind
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI = sorted(["cth", "cph", "ckh", "cfh", "ch", "sh", "ee"], key=lambda s: -len(s))
CORE_SET = {"t", "p", "k", "f", "cth", "cph", "ckh", "cfh"}
MANTLE_SET = {"ch", "sh", "ee"}
CRUST_SET = {"d", "l", "r", "s", "n", "x", "i", "m", "g", "q", "o", "y", "a", "e"}

STOLFI_TARGET = 0.80
STOLFI_INVENTORY_PROXY = 15


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


def load_hand(lang):
    words = []
    for f in CORPUS["folios"]:
        if f.get("currier_language") != lang:
            continue
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    words.append(w)
    return [tokenize(w) for w in words]


def inventory_size_80(tokens):
    inner_counts = Counter()
    for t in tokens:
        if len(t) >= 3:
            inner_counts[t[len(t) - 2]] += 1
    if not inner_counts:
        return 0
    total = sum(inner_counts.values())
    ranked = inner_counts.most_common()
    cum = 0
    for k, (_, c) in enumerate(ranked, 1):
        cum += c
        if cum / total >= 0.80:
            return k
    return len(ranked)


def per_token_suffix_dealer_counts(tokens):
    counts = []
    for t in tokens:
        if not t or t[0] == "q":
            continue
        core_positions = [i for i, g in enumerate(t) if g in CORE_SET]
        if not core_positions:
            continue
        first_core = core_positions[0]
        suffix = t[first_core + 1:]
        counts.append(sum(1 for g in suffix if g in CRUST_SET))
    return counts


hand_a = load_hand("A")
hand_b = load_hand("B")
print(f"Hand A tokens: {len(hand_a)}")
print(f"Hand B tokens: {len(hand_b)}")

print("\n=== M1: LAYER-1 INNER INVENTORY SIZE (80% coverage) ===")
inv_a = inventory_size_80(hand_a)
inv_b = inventory_size_80(hand_b)
print(f"  inventory_size_80(A) = {inv_a}")
print(f"  inventory_size_80(B) = {inv_b}")
print(f"  Stolfi reference     = {STOLFI_INVENTORY_PROXY}")

random.seed(42)
B_RESAMPLES = 1000
boot_a = []
boot_b = []
a_geq_b = 0
for _ in range(B_RESAMPLES):
    sample_a = [hand_a[random.randrange(len(hand_a))] for _ in range(len(hand_a))]
    sample_b = [hand_b[random.randrange(len(hand_b))] for _ in range(len(hand_b))]
    ia = inventory_size_80(sample_a)
    ib = inventory_size_80(sample_b)
    boot_a.append(ia)
    boot_b.append(ib)
    if ia > ib:
        a_geq_b += 1
p_a_leq_b = 1 - (a_geq_b / B_RESAMPLES)
boot_a.sort()
boot_b.sort()
ci_a = (boot_a[24], boot_a[974])
ci_b = (boot_b[24], boot_b[974])
print(f"  bootstrap (1000 resamples):")
print(f"    A mean={statistics.mean(boot_a):.2f}  95% CI [{ci_a[0]}, {ci_a[1]}]")
print(f"    B mean={statistics.mean(boot_b):.2f}  95% CI [{ci_b[0]}, {ci_b[1]}]")
print(f"    P(A > B) = {a_geq_b/B_RESAMPLES:.4f}")
print(f"    p_a (one-sided, A <= B) = {p_a_leq_b:.4f}")

print("\n=== M2: MEAN TOKENISED LENGTH (morpheme proxy) ===")
len_a = [len(t) for t in hand_a]
len_b = [len(t) for t in hand_b]
mean_len_a = statistics.mean(len_a)
mean_len_b = statistics.mean(len_b)
std_len_a = statistics.stdev(len_a)
std_len_b = statistics.stdev(len_b)
print(f"  mean_length(A) = {mean_len_a:.4f}  std = {std_len_a:.4f}  n = {len(len_a)}")
print(f"  mean_length(B) = {mean_len_b:.4f}  std = {std_len_b:.4f}  n = {len(len_b)}")
if HAVE_SCIPY:
    t_stat_m2, p_m2 = ttest_ind(len_a, len_b, equal_var=False)
    print(f"  Welch t = {t_stat_m2:.4f}  p = {p_m2:.4e}")
else:
    t_stat_m2 = p_m2 = None
    print("  scipy missing; Welch test skipped")

print("\n=== M3: STOLFI-CONSISTENT SUFFIX DEALER MEAN ===")
sd_a = per_token_suffix_dealer_counts(hand_a)
sd_b = per_token_suffix_dealer_counts(hand_b)
mean_sd_a = statistics.mean(sd_a) if sd_a else 0.0
mean_sd_b = statistics.mean(sd_b) if sd_b else 0.0
std_sd_a = statistics.stdev(sd_a) if len(sd_a) > 1 else 0.0
std_sd_b = statistics.stdev(sd_b) if len(sd_b) > 1 else 0.0
print(f"  suffix_dealer_mean(A) = {mean_sd_a:.4f}  std = {std_sd_a:.4f}  n = {len(sd_a)}")
print(f"  suffix_dealer_mean(B) = {mean_sd_b:.4f}  std = {std_sd_b:.4f}  n = {len(sd_b)}")

sanity_A_matches_2p4182 = abs(mean_sd_a - 2.4182) < 0.01
print(f"  Sanity A ~= 2.4182:    {'OK' if sanity_A_matches_2p4182 else 'DEVIATION >0.01'}")

if HAVE_SCIPY:
    t_stat_m3, p_m3 = ttest_ind(sd_a, sd_b, equal_var=False)
    print(f"  Welch t = {t_stat_m3:.4f}  p = {p_m3:.4e}")
else:
    t_stat_m3 = p_m3 = None
    print("  scipy missing; Welch test skipped")

print("\n=== LOCKED DECISIONS ===")

a_cond_1 = inv_a > inv_b
a_cond_2 = p_a_leq_b < 0.01
a_cond_3 = inv_a > STOLFI_INVENTORY_PROXY
decision_a = a_cond_1 and a_cond_2 and a_cond_3
print(f"(a) Inventory richness:")
print(f"    inv_A > inv_B:           {inv_a} > {inv_b} = {a_cond_1}")
print(f"    p_a < 0.01:              {p_a_leq_b:.4f} < 0.01 = {a_cond_2}")
print(f"    inv_A > 15 (Stolfi):     {inv_a} > 15 = {a_cond_3}")
print(f"    (a) PASS = {decision_a}")

excess_a = mean_sd_a - STOLFI_TARGET
excess_b = mean_sd_b - STOLFI_TARGET
if excess_a > 0:
    fraction_methodological = excess_b / excess_a
else:
    fraction_methodological = 0.0
decision_b = fraction_methodological > 0.50
print(f"\n(b) Operationalisation drift:")
print(f"    (B - 0.80)/(A - 0.80) = ({mean_sd_b:.4f}-0.80)/({mean_sd_a:.4f}-0.80) = {fraction_methodological:.4f}")
print(f"    threshold > 0.50 = {decision_b}")
print(f"    (b) PASS = {decision_b}")

if excess_a > 0:
    fraction_productivity = (mean_sd_a - mean_sd_b) / excess_a
else:
    fraction_productivity = 0.0
c_cond_1 = (p_m3 is not None) and p_m3 < 0.01
c_cond_2 = fraction_productivity > 0.30
decision_c = c_cond_1 and c_cond_2
print(f"\n(c) A/B productivity:")
print(f"    Welch t-test p < 0.01:   {p_m3 if p_m3 is not None else 'NA':>.4e} < 0.01 = {c_cond_1}"
      if p_m3 is not None else f"    Welch t-test p: NA")
print(f"    (A - B)/(A - 0.80):      ({mean_sd_a:.4f}-{mean_sd_b:.4f})/({mean_sd_a:.4f}-0.80) = {fraction_productivity:.4f}")
print(f"    threshold > 0.30 = {c_cond_2}")
print(f"    (c) PASS = {decision_c}")

passes = [("a", decision_a), ("b", decision_b), ("c", decision_c)]
passing = [p[0] for p in passes if p[1]]
print(f"\nVERDICT: passing candidates = {passing if passing else 'NONE (UNDIAGNOSED)'}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-DENSITY-DIAGNOSIS-01",
    "n_hand_a_tokens": len(hand_a),
    "n_hand_b_tokens": len(hand_b),
    "M1_inventory_size_80": {
        "hand_a": inv_a,
        "hand_b": inv_b,
        "stolfi_reference": STOLFI_INVENTORY_PROXY,
        "bootstrap_resamples": B_RESAMPLES,
        "hand_a_bootstrap_mean": round(statistics.mean(boot_a), 4),
        "hand_a_bootstrap_ci_95": list(ci_a),
        "hand_b_bootstrap_mean": round(statistics.mean(boot_b), 4),
        "hand_b_bootstrap_ci_95": list(ci_b),
        "p_A_greater_B": round(a_geq_b / B_RESAMPLES, 4),
        "p_a_one_sided": round(p_a_leq_b, 4),
    },
    "M2_mean_tokenised_length": {
        "hand_a_mean": round(mean_len_a, 4),
        "hand_a_std": round(std_len_a, 4),
        "hand_a_n": len(len_a),
        "hand_b_mean": round(mean_len_b, 4),
        "hand_b_std": round(std_len_b, 4),
        "hand_b_n": len(len_b),
        "welch_t": round(t_stat_m2, 4) if t_stat_m2 is not None else None,
        "welch_p": p_m2,
    },
    "M3_suffix_dealer_mean": {
        "hand_a_mean": round(mean_sd_a, 4),
        "hand_a_std": round(std_sd_a, 4),
        "hand_a_n_split": len(sd_a),
        "hand_b_mean": round(mean_sd_b, 4),
        "hand_b_std": round(std_sd_b, 4),
        "hand_b_n_split": len(sd_b),
        "welch_t": round(t_stat_m3, 4) if t_stat_m3 is not None else None,
        "welch_p": p_m3,
        "sanity_hand_a_matches_2p4182": sanity_A_matches_2p4182,
    },
    "decisions": {
        "a_inventory_richness": {
            "inv_a_greater_inv_b": a_cond_1,
            "p_a_below_0_01": a_cond_2,
            "inv_a_greater_stolfi_15": a_cond_3,
            "pass": decision_a,
        },
        "b_operationalisation_drift": {
            "fraction_methodological": round(fraction_methodological, 4),
            "threshold": 0.50,
            "pass": decision_b,
        },
        "c_a_over_b_productivity": {
            "welch_p_below_0_01": c_cond_1,
            "fraction_productivity": round(fraction_productivity, 4),
            "threshold": 0.30,
            "pass": decision_c,
        },
    },
    "passing_candidates": passing if passing else "UNDIAGNOSED",
}
out_path = ROOT / "outputs" / "density_diagnosis_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
