"""
Execute pre-registered H-BV-COMPOSITE-OUTER-01.

Tests whether Hand A's Layer-2 outer region stacks multiple ordered
morphemes per slot, explaining the 3x suffix dealer density excess
(2.4182 observed vs Stolfi 0.80 baseline).

Five measurements (M1-M5), three pass/fail (M3, M4, M5):
  M1 descriptive - outer word-final rates
  M2 descriptive - multi-outer co-occurrence rate
  M3 pass/fail   - adjacent-outer pair ordering (max_asymmetry >= 0.80)
  M4 pass/fail   - dealer density anomaly reduction (>= 0.50)
  M5 pass/fail   - folio clustering (chi2 p < 0.05 AND Cramer's V >= 0.15)

Decision rule (locked in hypotheses/H-BV-COMPOSITE-OUTER-01.json).
"""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

try:
    from scipy.stats import chi2_contingency
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI = sorted(["ckh", "cth", "cph", "cfh", "ch", "sh", "ee", "ol"], key=lambda s: -len(s))

LAYER2_OUTER = {"y", "n", "r", "ol", "l"}
CORE_SET = {"t", "p", "k", "f", "cth", "cph", "ckh", "cfh"}
CRUST_SET = {"d", "l", "r", "s", "n", "x", "i", "m", "g", "q", "o", "y", "a", "e"}

OBSERVED_GLYPH_MEAN = 2.4182
STOLFI_TARGET = 0.80
OBSERVED_EXCESS = OBSERVED_GLYPH_MEAN - STOLFI_TARGET


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


folios_hand_a = [f for f in CORPUS["folios"] if f.get("currier_language") == "A"]
hand_a_words = []
token_folio = []
for f in folios_hand_a:
    for line in f["lines"]:
        for w in line["words"]:
            if w:
                hand_a_words.append(w)
                token_folio.append(f["folio"])

tokenised = [tokenize(w) for w in hand_a_words]
n_tokens = len(tokenised)
print(f"Hand A tokens: {n_tokens}")

print("\n=== M1: LAYER-2 OUTER POSITION FREQUENCY ===")
m1 = {}
for o in sorted(LAYER2_OUTER):
    denom = sum(1 for t in tokenised if o in t)
    numer = sum(1 for t in tokenised if t and t[-1] == o and o in t)
    rate = numer / denom if denom else 0.0
    m1[o] = {"numerator": numer, "denominator": denom, "final_rate": round(rate, 4)}
    print(f"  {o:3s}  final {numer:5d} / total {denom:5d}  = {rate:.4f}")

print("\n=== M2: MULTI-OUTER CO-OCCURRENCE RATE ===")
denom_m2 = sum(1 for t in tokenised if len(t) >= 2)
numer_m2 = sum(
    1 for t in tokenised if len(t) >= 2 and t[-1] in LAYER2_OUTER and t[-2] in LAYER2_OUTER
)
multi_outer_rate = numer_m2 / denom_m2 if denom_m2 else 0.0
m2 = {"numerator": numer_m2, "denominator": denom_m2, "multi_outer_rate": round(multi_outer_rate, 4)}
print(f"  last-2-glyphs both in Layer-2 outer: {numer_m2} / {denom_m2} = {multi_outer_rate:.4f}")

print("\n=== M3: ADJACENT-OUTER PAIR ORDERING ===")
ordered_pair_counts = Counter()
for t in tokenised:
    if len(t) >= 2 and t[-1] in LAYER2_OUTER and t[-2] in LAYER2_OUTER and t[-1] != t[-2]:
        ordered_pair_counts[(t[-2], t[-1])] += 1

pair_table = []
unordered_seen = set()
outers_sorted = sorted(LAYER2_OUTER)
for i, A in enumerate(outers_sorted):
    for B in outers_sorted[i + 1:]:
        if (A, B) in unordered_seen:
            continue
        unordered_seen.add((A, B))
        cnt_AB = ordered_pair_counts.get((A, B), 0)
        cnt_BA = ordered_pair_counts.get((B, A), 0)
        total = cnt_AB + cnt_BA
        if total >= 20:
            asym = abs(cnt_AB - cnt_BA) / total
            pair_table.append({
                "pair": f"{{{A},{B}}}",
                "count_AB": cnt_AB,
                "count_BA": cnt_BA,
                "pair_total": total,
                "pair_asymmetry": round(asym, 4),
                "A_first_direction": f"{A}->{B}" if cnt_AB > cnt_BA else f"{B}->{A}",
            })

pair_table.sort(key=lambda r: -r["pair_asymmetry"])
print(f"  {len(pair_table)} qualifying unordered pairs (pair_total >= 20):")
for row in pair_table:
    print(
        f"    {row['pair']:12s}  AB={row['count_AB']:4d}  BA={row['count_BA']:4d}  "
        f"total={row['pair_total']:4d}  asym={row['pair_asymmetry']:.4f}  "
        f"dir={row['A_first_direction']}"
    )

if pair_table:
    max_row = pair_table[0]
    max_asym = max_row["pair_asymmetry"]
    argmax_total = max_row["pair_total"]
    M3_PASS = max_asym >= 0.80 and argmax_total >= 50
else:
    max_asym = 0.0
    argmax_total = 0
    M3_PASS = False
print(
    f"\n  max_asymmetry: {max_asym:.4f}  argmax_pair_total: {argmax_total}  "
    f"threshold (>=0.80 AND total>=50)  {'PASS' if M3_PASS else 'FAIL'}"
)

print("\n=== M4: DEALER DENSITY ANOMALY REDUCTION ===")
composite_set = [
    (A, B) for (A, B), cnt in ordered_pair_counts.most_common()
    if A in LAYER2_OUTER and B in LAYER2_OUTER and A != B
][:10]

while len(composite_set) < 10:
    same = [
        (o, o)
        for o in LAYER2_OUTER
        if sum(1 for t in tokenised if len(t) >= 2 and t[-2] == o and t[-1] == o) > 0
    ]
    for s in same:
        if s not in composite_set:
            composite_set.append(s)
    if len(composite_set) >= 10:
        break
    break

composite_set = composite_set[:10]
print(f"  Composite set C (top-10 ordered outer pairs):")
for A, B in composite_set:
    print(f"    ({A},{B})  count={ordered_pair_counts.get((A,B), 0)}")

composite_set_list = [list(p) for p in composite_set]
composite_lookup = set(composite_set)


def count_suffix_morphemes(suffix_glyphs):
    count = 0
    i = 0
    while i < len(suffix_glyphs):
        if (
            i + 1 < len(suffix_glyphs)
            and (suffix_glyphs[i], suffix_glyphs[i + 1]) in composite_lookup
        ):
            if suffix_glyphs[i] in CRUST_SET and suffix_glyphs[i + 1] in CRUST_SET:
                count += 1
                i += 2
                continue
        if suffix_glyphs[i] in CRUST_SET:
            count += 1
        i += 1
    return count


morpheme_counts = []
glyph_counts = []
for t in tokenised:
    if not t or t[0] == "q":
        continue
    core_positions = [i for i, g in enumerate(t) if g in CORE_SET]
    if not core_positions:
        continue
    first_core = core_positions[0]
    suffix = t[first_core + 1:]
    morpheme_counts.append(count_suffix_morphemes(suffix))
    glyph_counts.append(sum(1 for g in suffix if g in CRUST_SET))

n_split = len(morpheme_counts)
glyph_mean_check = sum(glyph_counts) / n_split if n_split else 0.0
new_morpheme_mean = sum(morpheme_counts) / n_split if n_split else 0.0
anomaly_reduction = (OBSERVED_GLYPH_MEAN - new_morpheme_mean) / OBSERVED_EXCESS
M4_PASS = anomaly_reduction >= 0.50

print(f"\n  n split tokens (q-excluded, with core): {n_split}")
print(f"  glyph_mean sanity (should be ~2.418):    {glyph_mean_check:.4f}")
print(f"  new_morpheme_mean (composites as 1):     {new_morpheme_mean:.4f}")
print(f"  observed_glyph_mean:                     {OBSERVED_GLYPH_MEAN:.4f}")
print(f"  stolfi_target:                           {STOLFI_TARGET:.4f}")
print(f"  observed_excess:                         {OBSERVED_EXCESS:.4f}")
print(f"  anomaly_reduction (>=0.50):              {anomaly_reduction:.4f}  {'PASS' if M4_PASS else 'FAIL'}")

print("\n=== M5: FOLIO CLUSTERING ===")
folio_counts = defaultdict(int)
for t, folio in zip(tokenised, token_folio):
    folio_counts[folio] += 1

folio_pair_counts = defaultdict(lambda: Counter())
for t, folio in zip(tokenised, token_folio):
    if len(t) >= 2:
        pair = (t[-2], t[-1])
        if pair in composite_lookup:
            folio_pair_counts[folio][pair] += 1

eligible_folios = [
    f for f in folio_pair_counts
    if folio_counts[f] >= 20 and sum(folio_pair_counts[f].values()) > 0
]
print(f"  eligible folios (>=20 Hand A tokens, >=1 composite): {len(eligible_folios)}")

table = []
for f in eligible_folios:
    row = [folio_pair_counts[f].get(pair, 0) for pair in composite_set]
    table.append(row)

if HAVE_SCIPY and table and len(composite_set) >= 2 and len(eligible_folios) >= 2:
    col_sums = [sum(table[i][j] for i in range(len(table))) for j in range(len(composite_set))]
    nonzero_cols = [j for j, s in enumerate(col_sums) if s > 0]
    table_clean = [[row[j] for j in nonzero_cols] for row in table]
    table_clean = [row for row in table_clean if sum(row) > 0]
    if len(table_clean) >= 2 and len(nonzero_cols) >= 2:
        chi2, p_value, dof, expected = chi2_contingency(table_clean)
        n_total = sum(sum(row) for row in table_clean)
        k = min(len(table_clean), len(nonzero_cols))
        cramers_V = math.sqrt(chi2 / (n_total * (k - 1))) if n_total and k > 1 else 0.0
        M5_PASS = p_value < 0.05 and cramers_V >= 0.15
        print(f"  chi2 = {chi2:.2f}  dof = {dof}  p = {p_value:.2e}  Cramer V = {cramers_V:.4f}")
        print(f"  threshold (p<0.05 AND V>=0.15) {'PASS' if M5_PASS else 'FAIL'}")
    else:
        chi2 = p_value = cramers_V = None
        M5_PASS = False
        print("  insufficient data for chi-square")
else:
    chi2 = p_value = cramers_V = None
    M5_PASS = False
    print(f"  scipy not available or insufficient table size -> FAIL")

print("\n" + "=" * 78)
print("  LOCKED DECISION")
print("=" * 78)
if M3_PASS and M4_PASS and M5_PASS:
    verdict = "CONFIRMED"
elif M3_PASS and not M4_PASS:
    verdict = "PARTIAL_DENSITY"
elif M3_PASS and M4_PASS and not M5_PASS:
    verdict = "PARTIAL_NO_CLUSTERING"
elif not M3_PASS:
    verdict = "REFUTED"
else:
    verdict = "INDETERMINATE"

print(f"  M3 ordering:   {'PASS' if M3_PASS else 'FAIL'}")
print(f"  M4 density:    {'PASS' if M4_PASS else 'FAIL'}")
print(f"  M5 clustering: {'PASS' if M5_PASS else 'FAIL'}")
print(f"  VERDICT:       {verdict}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-COMPOSITE-OUTER-01",
    "n_hand_a_tokens": n_tokens,
    "M1_outer_position_frequency": m1,
    "M2_multi_outer_rate": m2,
    "M3_pair_ordering": {
        "qualifying_pairs": pair_table,
        "max_asymmetry": round(max_asym, 4),
        "argmax_pair_total": argmax_total,
        "threshold": "max_asymmetry >= 0.80 AND argmax_pair_total >= 50",
        "pass": M3_PASS,
    },
    "M4_density_reduction": {
        "composite_set_C": composite_set_list,
        "n_split_tokens": n_split,
        "observed_glyph_mean": OBSERVED_GLYPH_MEAN,
        "glyph_mean_check": round(glyph_mean_check, 4),
        "new_morpheme_mean": round(new_morpheme_mean, 4),
        "stolfi_target": STOLFI_TARGET,
        "observed_excess": round(OBSERVED_EXCESS, 4),
        "anomaly_reduction": round(anomaly_reduction, 4),
        "threshold": "anomaly_reduction >= 0.50",
        "pass": M4_PASS,
    },
    "M5_folio_clustering": {
        "eligible_folios": len(eligible_folios),
        "composite_columns": len(composite_set),
        "chi2": round(chi2, 4) if chi2 is not None else None,
        "p_value": p_value,
        "cramers_V": round(cramers_V, 4) if cramers_V is not None else None,
        "threshold": "p_value < 0.05 AND cramers_V >= 0.15",
        "pass": M5_PASS,
    },
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "composite_outer_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
