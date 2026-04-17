"""
Execute pre-registered H-BV-BASQUE-DIRECT-CORPUS-01.

Direct measurement of all 6 sub-metrics on UD_Basque-BDT.
Operational mapping per pre-reg; tolerance bands locked.
"""
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
UD_FILE = ROOT / "raw/corpus/reference-corpora/eu_bdt-ud-train.conllu"

HAND_A = {"M1": 4.12, "M2_L1": 10, "M2_L2": 5, "M3": 3.16, "M4": 0.20, "M5": 1.00}
PUBLISHED = {
    "M1": (2.5, 4.5),
    "M2_L1": (8, 16),
    "M2_L2": (3, 8),
    "M3": (2.0, 5.0),
    "M4": (0.02, 0.20),
    "M5": (0.60, 1.00),
}

INNER_CATEGORIES = {"Number", "Aspect", "Person", "PronType"}
OUTER_CATEGORIES = {"Case", "Mood", "Tense", "Definite", "VerbForm"}
CONTENT_POS = {"NOUN", "VERB", "ADJ", "PROPN"}


def parse_conllu(path):
    sentences = []
    current = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                if current:
                    sentences.append(current)
                    current = []
                continue
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 8:
                continue
            if "-" in parts[0] or "." in parts[0]:
                continue
            current.append({
                "id": parts[0],
                "form": parts[1],
                "lemma": parts[2],
                "upos": parts[3],
                "feats_raw": parts[5],
                "feats": {f.split("=")[0]: f.split("=")[1] for f in parts[5].split("|") if "=" in f} if parts[5] != "_" else {},
            })
    if current:
        sentences.append(current)
    return sentences


print(f"Loading UD_Basque-BDT...")
sentences = parse_conllu(UD_FILE)
all_tokens = [t for s in sentences for t in s]
content_tokens = [t for t in all_tokens if t["upos"] in CONTENT_POS]
print(f"  total tokens: {len(all_tokens)}")
print(f"  content tokens (NOUN/VERB/ADJ/PROPN): {len(content_tokens)}")

feat_counts_per_word = [1 + len(t["feats"]) for t in content_tokens]
m1_direct = statistics.mean(feat_counts_per_word) if feat_counts_per_word else 0.0
print(f"\nM1 direct (mean feature count per content word): {m1_direct:.4f}")

inner_values = defaultdict(set)
outer_values = defaultdict(set)
for t in content_tokens:
    for cat, val in t["feats"].items():
        if cat in INNER_CATEGORIES:
            inner_values[cat].add(val)
        if cat in OUTER_CATEGORIES:
            outer_values[cat].add(val)

m2_l1_direct = sum(len(v) for v in inner_values.values())
m2_l2_direct = sum(len(v) for v in outer_values.values())
print(f"M2 L1 direct (inner categories summed): {m2_l1_direct}")
for cat in INNER_CATEGORIES:
    if cat in inner_values:
        print(f"    {cat}: {sorted(inner_values[cat])}  (|{len(inner_values[cat])}|)")
print(f"M2 L2 direct (outer categories summed): {m2_l2_direct}")
for cat in OUTER_CATEGORIES:
    if cat in outer_values:
        print(f"    {cat}: {sorted(outer_values[cat])}  (|{len(outer_values[cat])}|)")

forms_per_lemma = defaultdict(set)
for t in content_tokens:
    forms_per_lemma[(t["lemma"], t["upos"])].add(t["form"])
lemma_token_counts = Counter((t["lemma"], t["upos"]) for t in content_tokens)
productive_lemmas = [k for k, count in lemma_token_counts.items() if count >= 3]
distinct_forms_counts = [len(forms_per_lemma[k]) for k in productive_lemmas]
m3_direct = statistics.mean(distinct_forms_counts) if distinct_forms_counts else 0.0
print(f"\nM3 direct (mean distinct forms per productive lemma): {m3_direct:.4f}")
print(f"  productive lemmas (>=3 tokens): {len(productive_lemmas)}")

number_case_cells = Counter()
number_totals = Counter()
case_totals = Counter()
for t in content_tokens:
    num = t["feats"].get("Number")
    case = t["feats"].get("Case")
    if num:
        number_totals[num] += 1
    if case:
        case_totals[case] += 1
    if num and case:
        number_case_cells[(num, case)] += 1

total_cells = len(number_totals) * len(case_totals)
nonzero_cells = len(number_case_cells)
zero_cells = total_cells - nonzero_cells
m4_direct = zero_cells / total_cells if total_cells else 0.0
print(f"\nM4 direct (gap density in Number x Case):")
print(f"  Number values: {dict(number_totals)}")
print(f"  Case values: {dict(case_totals)}")
print(f"  total cells: {total_cells}  nonzero: {nonzero_cells}  zero: {zero_cells}")
print(f"  M4 direct: {m4_direct:.4f}")

m5_asymmetric = 0
m5_qualifying = 0
for case, case_total in case_totals.items():
    if case_total < 20:
        continue
    m5_qualifying += 1
    sing_count = number_case_cells.get(("Sing", case), 0)
    plur_count = number_case_cells.get(("Plur", case), 0)
    if sing_count > 0 and plur_count > 0:
        ratio = max(sing_count / plur_count, plur_count / sing_count)
    elif sing_count > 0 or plur_count > 0:
        ratio = float("inf")
    else:
        ratio = 1.0
    if ratio >= 3.0:
        m5_asymmetric += 1
m5_direct = m5_asymmetric / m5_qualifying if m5_qualifying else 0.0
print(f"\nM5 direct (Case values with >=3x Number asymmetry): {m5_asymmetric}/{m5_qualifying} = {m5_direct:.4f}")

print("\n" + "=" * 70)
print("COMPARISON")
print("=" * 70)


def check_published(metric, direct, pub_range):
    lo, hi = pub_range
    return lo <= direct <= hi


def check_hand_a_fit(metric, hand_a_val, direct_val):
    if metric in ("M1", "M3"):
        tolerance = direct_val * 0.5
        lo = direct_val - tolerance
        hi = direct_val + tolerance
    elif metric in ("M2_L1", "M2_L2"):
        tolerance = direct_val * 0.3
        lo = direct_val - tolerance
        hi = direct_val + tolerance
    elif metric == "M4":
        tolerance = direct_val * 0.5
        lo = direct_val - tolerance
        hi = direct_val + tolerance
    elif metric == "M5":
        lo = max(0, direct_val - 0.1)
        hi = min(1.0, direct_val + 0.1)
    else:
        return False, (0, 0)
    return lo <= hand_a_val <= hi, (lo, hi)


direct_values = {
    "M1": m1_direct, "M2_L1": m2_l1_direct, "M2_L2": m2_l2_direct,
    "M3": m3_direct, "M4": m4_direct, "M5": m5_direct,
}

per_metric_report = {}
pub_validated_count = 0
hand_a_fits_count = 0

for metric in ["M1", "M2_L1", "M2_L2", "M3", "M4", "M5"]:
    direct = direct_values[metric]
    pub_range = PUBLISHED[metric]
    pub_validated = check_published(metric, direct, pub_range)
    hand_a = HAND_A[metric]
    fits, tol_range = check_hand_a_fit(metric, hand_a, direct)
    if pub_validated:
        pub_validated_count += 1
    if fits:
        hand_a_fits_count += 1
    per_metric_report[metric] = {
        "direct": round(direct, 4),
        "published_range": pub_range,
        "published_validated": pub_validated,
        "hand_a": hand_a,
        "tolerance_band_around_direct": [round(tol_range[0], 4), round(tol_range[1], 4)],
        "hand_a_fits": fits,
    }
    print(f"  {metric:7s} direct={direct:<10.4f} pub_range={pub_range} pub_val={'YES' if pub_validated else 'NO '}  "
          f"hand_a={hand_a:<6} tol_band=[{tol_range[0]:.4f}, {tol_range[1]:.4f}] fits={'YES' if fits else 'NO '}")

print(f"\n  PUBLISHED_VALIDATED count: {pub_validated_count}/6")
print(f"  HAND_A_FITS count:         {hand_a_fits_count}/6")

if hand_a_fits_count == 6:
    verdict = "CORPUS_CONFIRMED"
elif hand_a_fits_count in (4, 5):
    verdict = "CORPUS_PARTIAL"
elif hand_a_fits_count == 3:
    verdict = "CORPUS_WEAK"
else:
    verdict = "CORPUS_REFUTED"

published_range_failure = (6 - pub_validated_count) >= 3

print(f"\n  VERDICT: {verdict}")
if published_range_failure:
    print(f"  PUBLISHED_RANGE_FAILURE overlay: {6 - pub_validated_count}/6 published ranges miss direct measurements")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-BASQUE-DIRECT-CORPUS-01",
    "ud_basque_content_tokens": len(content_tokens),
    "direct_measurements": {
        "M1": round(m1_direct, 4),
        "M2_L1": m2_l1_direct,
        "M2_L2": m2_l2_direct,
        "M3": round(m3_direct, 4),
        "M4": round(m4_direct, 4),
        "M5": round(m5_direct, 4),
        "M2_L1_breakdown": {cat: sorted(inner_values[cat]) for cat in INNER_CATEGORIES if cat in inner_values},
        "M2_L2_breakdown": {cat: sorted(outer_values[cat]) for cat in OUTER_CATEGORIES if cat in outer_values},
        "M4_breakdown": {"number_values": dict(number_totals), "case_values_count": len(case_totals), "total_cells": total_cells, "zero_cells": zero_cells},
        "M5_breakdown": {"asymmetric_cases": m5_asymmetric, "qualifying_cases": m5_qualifying},
    },
    "hand_a_values": HAND_A,
    "published_ranges": PUBLISHED,
    "per_metric_report": per_metric_report,
    "published_validated_count": pub_validated_count,
    "hand_a_fits_count": hand_a_fits_count,
    "published_range_failure_overlay": published_range_failure,
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "basque_direct_corpus_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
