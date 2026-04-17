"""
Execute pre-registered H-BV-EXTERNAL-CORRELATION-01.

8 correlations between external folio features and Hand A text statistics.
1000 shuffle nulls per correlation.
"""
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

TOP5_OUTERS = {"y", "n", "r", "ol", "l"}


def build_folio_records():
    records = []
    sorted_folios = sorted(CORPUS["folios"], key=lambda f: f["folio"])
    for position, f in enumerate(sorted_folios):
        if f.get("currier_language") != "A":
            continue
        tokens = []
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    tokens.append(w)
        if len(tokens) < 30:
            continue
        types = set(tokens)
        ttr = len(types) / len(tokens)
        mean_len = statistics.mean(len(t) for t in tokens)
        outers_present = set()
        for t in tokens:
            for o in TOP5_OUTERS:
                if t.endswith(o):
                    outers_present.add(o)
        l2_outer_count = len(outers_present)
        daiin_freq = sum(1 for t in tokens if t == "daiin") / len(tokens)
        records.append({
            "folio": f["folio"],
            "section": f.get("section", "unknown"),
            "quire": f.get("quire", "?"),
            "position": position,
            "word_count": len(tokens),
            "line_count": f.get("line_count", len(f["lines"])),
            "tokens": tokens,
            "TTR": ttr,
            "mean_length": mean_len,
            "L2_outer_usage": l2_outer_count,
            "daiin_freq": daiin_freq,
        })
    return records


records = build_folio_records()
print(f"Hand A folios with >=30 tokens: {len(records)}")
section_counts = Counter(r["section"] for r in records)
print(f"Sections represented: {dict(section_counts)}")
quire_counts = Counter(r["quire"] for r in records)
print(f"Quires represented: {len(quire_counts)} distinct")


def f_statistic(groups_values):
    all_values = [v for g in groups_values for v in g]
    if len(all_values) < 2:
        return 0.0
    grand_mean = statistics.mean(all_values)
    n_total = len(all_values)
    k = len(groups_values)
    ss_between = sum(len(g) * (statistics.mean(g) - grand_mean) ** 2 for g in groups_values if len(g) > 0)
    ss_within = sum((v - statistics.mean(g)) ** 2 for g in groups_values if len(g) > 1 for v in g)
    df_between = k - 1
    df_within = n_total - k
    if df_between <= 0 or df_within <= 0 or ss_within == 0:
        return 0.0
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    return ms_between / ms_within if ms_within > 0 else 0.0


def anova_test(records, group_key, value_key, min_group_size=3):
    groups = {}
    for r in records:
        k = r[group_key]
        groups.setdefault(k, []).append(r[value_key])
    valid_groups = [v for v in groups.values() if len(v) >= min_group_size]
    if len(valid_groups) < 2:
        return None, 0
    F = f_statistic(valid_groups)
    return F, sum(len(g) for g in valid_groups)


def spearman_rho(xs, ys):
    def rank(values):
        sorted_indexed = sorted(enumerate(values), key=lambda p: p[1])
        ranks = [0] * len(values)
        for rank_i, (orig_i, _) in enumerate(sorted_indexed):
            ranks[orig_i] = rank_i + 1
        return ranks
    if len(xs) < 3:
        return 0.0
    rx = rank(xs)
    ry = rank(ys)
    mean_rx = sum(rx) / len(rx)
    mean_ry = sum(ry) / len(ry)
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(len(xs)))
    den_x = math.sqrt(sum((v - mean_rx) ** 2 for v in rx))
    den_y = math.sqrt(sum((v - mean_ry) ** 2 for v in ry))
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def shuffle_null_anova(records, group_key, value_key, n_shuffles=1000, seed=42):
    random.seed(seed)
    observed_F, _ = anova_test(records, group_key, value_key)
    null_Fs = []
    values = [r[value_key] for r in records]
    for _ in range(n_shuffles):
        shuffled_values = values[:]
        random.shuffle(shuffled_values)
        temp = [dict(r) for r in records]
        for i, rec in enumerate(temp):
            rec[value_key] = shuffled_values[i]
        null_F, _ = anova_test(temp, group_key, value_key)
        null_Fs.append(null_F)
    p = sum(1 for f in null_Fs if f >= observed_F) / n_shuffles
    return observed_F, p


def shuffle_null_spearman(xs, ys, n_shuffles=1000, seed=42):
    random.seed(seed)
    observed_rho = abs(spearman_rho(xs, ys))
    null_rhos = []
    for _ in range(n_shuffles):
        shuffled_ys = ys[:]
        random.shuffle(shuffled_ys)
        null_rhos.append(abs(spearman_rho(xs, shuffled_ys)))
    p = sum(1 for r in null_rhos if r >= observed_rho) / n_shuffles
    return spearman_rho(xs, ys), p


print("\n=== 8 CORRELATIONS ===")
results = []

for i, (name, group_key, value_key) in enumerate([
    ("C1 Section x TTR", "section", "TTR"),
    ("C2 Section x mean_length", "section", "mean_length"),
    ("C3 Section x L2_outer_usage", "section", "L2_outer_usage"),
    ("C4 Section x daiin_freq", "section", "daiin_freq"),
    ("C5 Quire x TTR", "quire", "TTR"),
], 1):
    stat, p = shuffle_null_anova(records, group_key, value_key, n_shuffles=1000, seed=42 + i)
    sig_01 = p < 0.01
    sig_bonf = p < 0.00125
    results.append({"correlation": name, "test": "ANOVA", "statistic": round(stat, 4), "p_value": round(p, 4), "sig_01": sig_01, "sig_bonferroni": sig_bonf})
    print(f"  {name:<35} F={stat:.4f}  p={p:.4f}  {'SIG(0.01)' if sig_01 else '---'}  {'SIG(bonf)' if sig_bonf else '   '}")

for i, (name, x_key, y_key) in enumerate([
    ("C6 Position x TTR", "position", "TTR"),
    ("C7 Position x mean_length", "position", "mean_length"),
    ("C8 Word_count x TTR", "word_count", "TTR"),
], 6):
    xs = [r[x_key] for r in records]
    ys = [r[y_key] for r in records]
    rho, p = shuffle_null_spearman(xs, ys, n_shuffles=1000, seed=42 + i)
    sig_01 = p < 0.01
    sig_bonf = p < 0.00125
    results.append({"correlation": name, "test": "Spearman", "statistic": round(rho, 4), "p_value": round(p, 4), "sig_01": sig_01, "sig_bonferroni": sig_bonf})
    print(f"  {name:<35} rho={rho:+.4f}  p={p:.4f}  {'SIG(0.01)' if sig_01 else '---'}  {'SIG(bonf)' if sig_bonf else '   '}")

sig_count = sum(1 for r in results if r["sig_01"])
bonf_count = sum(1 for r in results if r["sig_bonferroni"])
print(f"\n  Significant at p<0.01 uncorrected: {sig_count}/8")
print(f"  Significant at Bonferroni p<0.00125: {bonf_count}/8")

if sig_count >= 3:
    verdict = "CONFIRMED"
    if bonf_count >= 2:
        verdict = "ROBUSTLY_CONFIRMED"
elif sig_count >= 1:
    verdict = "PARTIAL"
else:
    verdict = "REFUTED"

print(f"\n  VERDICT: {verdict}")

for r in results:
    if r["sig_01"]:
        print(f"  SIG: {r['correlation']} — stat={r['statistic']} p={r['p_value']}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-EXTERNAL-CORRELATION-01",
    "n_folios_filtered": len(records),
    "section_distribution": dict(section_counts),
    "correlation_results": results,
    "significant_count_01": sig_count,
    "significant_count_bonferroni": bonf_count,
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "external_correlation_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
