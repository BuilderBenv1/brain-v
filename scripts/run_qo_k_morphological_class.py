"""
Execute pre-registered H-BV-QO-K-MORPHOLOGICAL-CLASS-01.

Aggregate per-folio rates for qo-k- vs qo-non-k- classes; Welch
t-test biological vs non-biological; decision rule.
"""
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))


def build_folios():
    records = []
    for f in sorted(CORPUS["folios"], key=lambda x: x["folio"]):
        if f.get("currier_language") != "B":
            continue
        tokens = []
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    tokens.append(w)
        if len(tokens) < 30:
            continue
        n = len(tokens)
        count_qok = sum(1 for t in tokens if t.startswith("qok"))
        count_qo_non_k = sum(1 for t in tokens if t.startswith("qo") and not t.startswith("qok"))
        records.append({
            "folio": f["folio"], "section": f.get("section", "unknown"),
            "n_tokens": n,
            "rate_qok": count_qok / n,
            "rate_qo_non_k": count_qo_non_k / n,
            "count_qok": count_qok, "count_qo_non_k": count_qo_non_k,
        })
    return records


records = build_folios()
print(f"Hand B folios (n>=30): {len(records)}")
bio = [r for r in records if r["section"] == "biological"]
non_bio = [r for r in records if r["section"] != "biological"]
print(f"  biological: {len(bio)}  non-biological: {len(non_bio)}")

print(f"\nTotal qok tokens across Hand B folios: {sum(r['count_qok'] for r in records)}")
print(f"Total qo-non-k tokens across Hand B folios: {sum(r['count_qo_non_k'] for r in records)}")


def welch_t(xs, ys):
    if len(xs) < 2 or len(ys) < 2:
        return None, None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    vx = statistics.variance(xs) if len(xs) > 1 else 0
    vy = statistics.variance(ys) if len(ys) > 1 else 0
    nx, ny = len(xs), len(ys)
    se = math.sqrt(vx / nx + vy / ny)
    if se == 0:
        return 0.0, 1.0
    t = (mx - my) / se
    df_num = (vx / nx + vy / ny) ** 2
    df_den_1 = (vx / nx) ** 2 / (nx - 1) if vx > 0 and nx > 1 else 0
    df_den_2 = (vy / ny) ** 2 / (ny - 1) if vy > 0 and ny > 1 else 0
    df = df_num / (df_den_1 + df_den_2) if (df_den_1 + df_den_2) > 0 else nx + ny - 2
    from math import lgamma

    def betainc(x, a, b, n_terms=80):
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
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
            if abs(c) < 1e-15:
                break
        return front * result

    def cdf_t(tx, dfx):
        x_beta = dfx / (dfx + tx * tx)
        p = 0.5 * betainc(x_beta, dfx / 2, 0.5)
        return 1 - p if tx > 0 else p
    p_two = 2 * (1 - cdf_t(abs(t), df))
    return t, p_two


def cohens_d(xs, ys):
    if len(xs) < 2 or len(ys) < 2:
        return 0.0
    mx, my = statistics.mean(xs), statistics.mean(ys)
    vx = statistics.variance(xs) if len(xs) > 1 else 0
    vy = statistics.variance(ys) if len(ys) > 1 else 0
    sd = math.sqrt((vx * (len(xs) - 1) + vy * (len(ys) - 1)) / (len(xs) + len(ys) - 2))
    return (mx - my) / sd if sd > 0 else 0


qok_bio = [r["rate_qok"] for r in bio]
qok_non_bio = [r["rate_qok"] for r in non_bio]
qo_non_k_bio = [r["rate_qo_non_k"] for r in bio]
qo_non_k_non_bio = [r["rate_qo_non_k"] for r in non_bio]

t_qok, p_qok = welch_t(qok_bio, qok_non_bio)
d_qok = cohens_d(qok_bio, qok_non_bio)
t_qonk, p_qonk = welch_t(qo_non_k_bio, qo_non_k_non_bio)
d_qonk = cohens_d(qo_non_k_bio, qo_non_k_non_bio)

print(f"\n=== CLASS A: qo-k- ===")
print(f"  mean_in_bio:     {statistics.mean(qok_bio):.5f}")
print(f"  mean_non_bio:    {statistics.mean(qok_non_bio):.5f}")
print(f"  Cohen's d:       {d_qok:+.4f}")
print(f"  Welch t:         {t_qok:+.4f}")
print(f"  p-value:         {p_qok:.6f}")

print(f"\n=== CLASS B: qo-non-k- ===")
print(f"  mean_in_bio:     {statistics.mean(qo_non_k_bio):.5f}")
print(f"  mean_non_bio:    {statistics.mean(qo_non_k_non_bio):.5f}")
print(f"  Cohen's d:       {d_qonk:+.4f}")
print(f"  Welch t:         {t_qonk:+.4f}")
print(f"  p-value:         {p_qonk:.6f}")

ratio = d_qok / d_qonk if d_qonk != 0 else float("inf")
print(f"\n  d_qok / d_qo_non_k ratio: {ratio:+.4f}" if not math.isinf(ratio) else "  d ratio: infinity")

qok_confirmed = d_qok >= 0.8 and p_qok is not None and p_qok < 0.001
qo_non_k_weak = d_qonk < 0.5 or (p_qonk is not None and p_qonk >= 0.01)
both_strong = d_qok >= 0.5 and d_qonk >= 0.5 and p_qok < 0.01 and p_qonk < 0.01
opposing = (d_qok > 0 and d_qonk < 0 and p_qok < 0.01 and p_qonk < 0.01)

if opposing:
    verdict = "OPPOSING_SIGN"
elif qok_confirmed and qo_non_k_weak:
    verdict = "CONFIRMED"
elif both_strong:
    verdict = "PARTIAL"
elif d_qok < 0.5 or p_qok >= 0.01:
    verdict = "REFUTED"
else:
    verdict = "AMBIGUOUS"

print(f"\n  VERDICT: {verdict}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-QO-K-MORPHOLOGICAL-CLASS-01",
    "n_biological_folios": len(bio),
    "n_non_biological_folios": len(non_bio),
    "total_qok_tokens": sum(r["count_qok"] for r in records),
    "total_qo_non_k_tokens": sum(r["count_qo_non_k"] for r in records),
    "class_A_qo_k": {
        "mean_bio": round(statistics.mean(qok_bio), 5),
        "mean_non_bio": round(statistics.mean(qok_non_bio), 5),
        "cohens_d": round(d_qok, 4),
        "t": round(t_qok, 4) if t_qok is not None else None,
        "p": round(p_qok, 6) if p_qok is not None else None,
    },
    "class_B_qo_non_k": {
        "mean_bio": round(statistics.mean(qo_non_k_bio), 5),
        "mean_non_bio": round(statistics.mean(qo_non_k_non_bio), 5),
        "cohens_d": round(d_qonk, 4),
        "t": round(t_qonk, 4) if t_qonk is not None else None,
        "p": round(p_qonk, 6) if p_qonk is not None else None,
    },
    "d_ratio_qok_over_qo_non_k": round(ratio, 4) if not math.isinf(ratio) else "infinity",
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "qo_k_morphological_class_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
