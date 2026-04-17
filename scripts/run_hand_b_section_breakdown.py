"""
Execute pre-registered H-BV-HAND-B-SECTION-BREAKDOWN-01.

Four sub-tests:
  S1 Pairwise section comparisons
  S2 Biological-exclusion ANOVA
  S3 Single-section-vs-rest effect sizes
  S4 Cross-hand herbal comparison
"""
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))


def build_folio_records(currier, marker):
    records = []
    sorted_folios = sorted(CORPUS["folios"], key=lambda f: f["folio"])
    for position, f in enumerate(sorted_folios):
        if f.get("currier_language") != currier:
            continue
        tokens = []
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    tokens.append(w)
        if len(tokens) < 30:
            continue
        ttr = len(set(tokens)) / len(tokens)
        mean_len = statistics.mean(len(t) for t in tokens)
        marker_freq = sum(1 for t in tokens if t == marker) / len(tokens)
        records.append({
            "folio": f["folio"], "section": f.get("section", "unknown"),
            "position": position, "TTR": ttr, "mean_length": mean_len,
            "marker_freq": marker_freq, "n_tokens": len(tokens),
        })
    return records


hand_b = build_folio_records("B", "chedy")
hand_a = build_folio_records("A", "daiin")
print(f"Hand B folios (n>=30): {len(hand_b)}  Hand A: {len(hand_a)}")


def welch_t(xs, ys):
    if len(xs) < 2 or len(ys) < 2:
        return None, None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    vx, vy = statistics.variance(xs) if len(xs) > 1 else 0, statistics.variance(ys) if len(ys) > 1 else 0
    nx, ny = len(xs), len(ys)
    se = math.sqrt(vx / nx + vy / ny) if vx > 0 or vy > 0 else 0
    if se == 0:
        return None, None
    t = (mx - my) / se
    df_num = (vx / nx + vy / ny) ** 2
    df_den = (vx / nx) ** 2 / (nx - 1) + (vy / ny) ** 2 / (ny - 1) if vy > 0 and vx > 0 else max(nx, ny)
    df = df_num / df_den if df_den > 0 else max(nx, ny) - 1

    def cdf_t(x, df):
        if df > 30:
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        a = df / 2
        b = 0.5
        x_beta = df / (df + x * x)
        from math import lgamma
        def betainc_regularized(x, a, b, n_terms=60):
            if x <= 0: return 0.0
            if x >= 1: return 1.0
            lbeta = lgamma(a) + lgamma(b) - lgamma(a + b)
            front = a * math.log(x) + b * math.log(1 - x) - lbeta - math.log(a)
            front = math.exp(front)
            c = 1.0
            result = c
            for n in range(1, n_terms):
                if n % 2 == 1:
                    m = (n - 1) // 2
                    num = -(a + m) * (a + b + m) * x
                    den = (a + 2 * m) * (a + 2 * m + 1)
                else:
                    m = n // 2
                    num = m * (b - m) * x
                    den = (a + 2 * m - 1) * (a + 2 * m)
                c = c * num / den
                result += c
                if abs(c) < 1e-12: break
            return front * result
        p = 0.5 * betainc_regularized(x_beta, a, b)
        if x > 0:
            return 1 - p
        return p
    p_two = 2 * (1 - cdf_t(abs(t), df))
    return t, p_two


def cohens_d(xs, ys):
    if len(xs) < 2 or len(ys) < 2:
        return 0.0
    mx, my = statistics.mean(xs), statistics.mean(ys)
    vx = statistics.variance(xs) if len(xs) > 1 else 0
    vy = statistics.variance(ys) if len(ys) > 1 else 0
    sd_pooled = math.sqrt((vx * (len(xs) - 1) + vy * (len(ys) - 1)) / (len(xs) + len(ys) - 2)) if (len(xs) + len(ys) - 2) > 0 else 0
    return (mx - my) / sd_pooled if sd_pooled > 0 else 0


print("\n" + "=" * 70)
print("S1 PAIRWISE SECTION COMPARISONS")
print("=" * 70)

section_records = defaultdict(list)
for r in hand_b:
    section_records[r["section"]].append(r)

sections = [s for s, v in section_records.items() if len(v) >= 3]
print(f"Sections with n>=3: {sections}")
print(f"Bonferroni threshold: p < 0.0025 (20 tests)")

s1_results = []
for s1, s2 in combinations(sections, 2):
    for metric in ["TTR", "marker_freq"]:
        xs = [r[metric] for r in section_records[s1]]
        ys = [r[metric] for r in section_records[s2]]
        t, p = welch_t(xs, ys)
        sig = p is not None and p < 0.0025
        s1_results.append({
            "pair": f"{s1} vs {s2}", "metric": metric,
            "n1": len(xs), "n2": len(ys),
            "mean1": round(statistics.mean(xs), 4), "mean2": round(statistics.mean(ys), 4),
            "t": round(t, 4) if t else None, "p": round(p, 6) if p else None,
            "sig_bonferroni": sig,
        })
        mark = "SIG" if sig else "   "
        t_str = f"{t:+.4f}" if t else "n/a"
        p_str = f"{p:.4f}" if p else "n/a"
        print(f"  [{mark}] {s1[:6]:<6} vs {s2[:6]:<6}  {metric:<12}  n={len(xs)}/{len(ys)}  t={t_str}  p={p_str}")

s1_sig_count = sum(1 for r in s1_results if r["sig_bonferroni"])
print(f"\n  Significant pairs at Bonferroni p<0.0025: {s1_sig_count}/{len(s1_results)}")

print("\n" + "=" * 70)
print("S2 BIOLOGICAL-EXCLUSION")
print("=" * 70)

hand_b_no_bio = [r for r in hand_b if r["section"] != "biological"]
print(f"  Hand B without biological: {len(hand_b_no_bio)} folios")
non_bio_sections = Counter(r["section"] for r in hand_b_no_bio)
print(f"  Sections: {dict(non_bio_sections)}")


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
    return (ss_between / df_between) / (ss_within / df_within) if ss_within > 0 else 0


def anova_with_null(records, value_key, n_shuffles=1000, seed=42):
    groups = defaultdict(list)
    for r in records:
        groups[r["section"]].append(r[value_key])
    valid = [v for v in groups.values() if len(v) >= 3]
    if len(valid) < 2:
        return None, None
    F_obs = f_statistic(valid)
    values = [r[value_key] for r in records]
    random.seed(seed)
    null_Fs = []
    for _ in range(n_shuffles):
        shuffled_vals = values[:]
        random.shuffle(shuffled_vals)
        temp = [dict(r) for r in records]
        for i, rec in enumerate(temp):
            rec[value_key] = shuffled_vals[i]
        temp_groups = defaultdict(list)
        for rec in temp:
            temp_groups[rec["section"]].append(rec[value_key])
        temp_valid = [v for v in temp_groups.values() if len(v) >= 3]
        null_Fs.append(f_statistic(temp_valid))
    p = sum(1 for f in null_Fs if f >= F_obs) / n_shuffles
    return F_obs, p


f_ttr_nobio, p_ttr_nobio = anova_with_null(hand_b_no_bio, "TTR", seed=100)
f_mf_nobio, p_mf_nobio = anova_with_null(hand_b_no_bio, "marker_freq", seed=101)

print(f"\n  C1 Section x TTR  without biological:       F={f_ttr_nobio:.4f}  p={p_ttr_nobio:.4f}  (original p<0.0001)")
print(f"  C4 Section x chedy without biological:       F={f_mf_nobio:.4f}  p={p_mf_nobio:.4f}  (original p<0.0001)")

print("\n" + "=" * 70)
print("S3 SINGLE-SECTION-VS-REST EFFECT SIZES")
print("=" * 70)

s3_results = []
for section in sections:
    in_sec = [r for r in hand_b if r["section"] == section]
    others = [r for r in hand_b if r["section"] != section]
    for metric in ["TTR", "marker_freq"]:
        xs = [r[metric] for r in in_sec]
        ys = [r[metric] for r in others]
        t, p = welch_t(xs, ys)
        d = cohens_d(xs, ys)
        s3_results.append({
            "section": section, "metric": metric,
            "n_in": len(xs), "n_out": len(ys),
            "mean_in": round(statistics.mean(xs), 4),
            "mean_out": round(statistics.mean(ys), 4),
            "t": round(t, 4) if t else None,
            "p": round(p, 6) if p else None,
            "cohens_d": round(d, 4),
        })
        t_str = f"{t:+.3f}" if t is not None else "n/a"
        p_str = f"{p:.4f}" if p is not None else "n/a"
        print(f"  {section:<15} {metric:<12}  mean_in={statistics.mean(xs):.4f}  mean_out={statistics.mean(ys):.4f}  d={d:+.4f}  t={t_str}  p={p_str}")

largest_ttr = max([r for r in s3_results if r["metric"] == "TTR"], key=lambda r: abs(r["cohens_d"]))
largest_mf = max([r for r in s3_results if r["metric"] == "marker_freq"], key=lambda r: abs(r["cohens_d"]))
print(f"\n  Largest |d| for TTR:          {largest_ttr['section']} (d = {largest_ttr['cohens_d']})")
print(f"  Largest |d| for marker_freq:  {largest_mf['section']} (d = {largest_mf['cohens_d']})")

print("\n" + "=" * 70)
print("S4 CROSS-HAND HERBAL COMPARISON")
print("=" * 70)

herbal_a = [r for r in hand_a if r["section"] == "herbal"]
herbal_b = [r for r in hand_b if r["section"] == "herbal"]
print(f"  Hand A herbal folios: {len(herbal_a)}  Hand B herbal folios: {len(herbal_b)}")

s4_results = {}
for metric in ["TTR", "mean_length", "marker_freq"]:
    xs = [r[metric] for r in herbal_a]
    ys = [r[metric] for r in herbal_b]
    t, p = welch_t(xs, ys)
    d = cohens_d(xs, ys)
    s4_results[metric] = {
        "hand_a_mean": round(statistics.mean(xs), 4) if xs else None,
        "hand_b_mean": round(statistics.mean(ys), 4) if ys else None,
        "t": round(t, 4) if t else None,
        "p": round(p, 6) if p else None,
        "cohens_d": round(d, 4),
    }
    t_str = f"{t:+.3f}" if t is not None else "n/a"
    p_str = f"{p:.4f}" if p is not None else "n/a"
    sig_marker = "SIG" if p and p < 0.01 else ""
    print(f"  {metric:<15} HA_mean={statistics.mean(xs):.4f}  HB_mean={statistics.mean(ys):.4f}  d={d:+.4f}  t={t_str}  p={p_str}  {sig_marker}")

print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

bio_sole_driver = (p_ttr_nobio >= 0.10 and p_mf_nobio >= 0.10)
bio_dominant = (not bio_sole_driver) and (p_ttr_nobio >= 0.01 or p_mf_nobio >= 0.01) and (largest_ttr["section"] == "biological" and largest_mf["section"] == "biological")
distributed = (p_ttr_nobio < 0.01 or p_mf_nobio < 0.01)

scribal_overlay = any(s4_results[m]["p"] is not None and s4_results[m]["p"] < 0.01 for m in ["TTR", "mean_length"])

if bio_sole_driver:
    primary = "BIOLOGICAL_SOLE_DRIVER"
elif bio_dominant:
    primary = "BIOLOGICAL_DOMINANT"
elif distributed:
    primary = "DISTRIBUTED_EFFECT"
else:
    primary = "AMBIGUOUS"

print(f"  Primary verdict: {primary}")
print(f"  Biological-exclusion: p_TTR={p_ttr_nobio:.4f}  p_chedy={p_mf_nobio:.4f}")
print(f"  Largest effect sections: TTR={largest_ttr['section']} (d={largest_ttr['cohens_d']})  marker={largest_mf['section']} (d={largest_mf['cohens_d']})")
print(f"  Cross-hand scribal overlay (herbal A vs B differs sig on TTR/length): {scribal_overlay}")
if scribal_overlay:
    print(f"    -> SCRIBAL OVERLAY also indicated")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-HAND-B-SECTION-BREAKDOWN-01",
    "hand_b_sections_n": {s: len(v) for s, v in section_records.items() if len(v) >= 3},
    "S1_pairwise": s1_results,
    "S1_sig_count": s1_sig_count,
    "S2_bio_exclusion": {"TTR": {"F": round(f_ttr_nobio, 4), "p": round(p_ttr_nobio, 4)}, "chedy": {"F": round(f_mf_nobio, 4), "p": round(p_mf_nobio, 4)}},
    "S3_single_vs_rest": s3_results,
    "S3_largest_ttr_driver": largest_ttr,
    "S3_largest_marker_driver": largest_mf,
    "S4_herbal_cross_hand": s4_results,
    "primary_verdict": primary,
    "scribal_overlay_detected": scribal_overlay,
}
out_path = ROOT / "outputs" / "hand_b_section_breakdown_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
