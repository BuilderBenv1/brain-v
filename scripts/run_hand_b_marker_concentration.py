"""
Execute pre-registered H-BV-HAND-B-MARKER-CONCENTRATION-01.

20 tokens x 5 sections = 100 Welch t-tests. Bonferroni p<0.0001.
Classifies each token as section-concentrated / distributed /
universal / variable.
"""
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

TOP20_TOKENS = [
    "ol", "shedy", "aiin", "daiin", "qokeedy", "ar", "qokain", "qokedy", "or",
    "qokeey", "chey", "qokaiin", "shey", "al", "dar", "y", "okaiin", "qokal",
    "otedy", "l",
]

BONFERRONI_P = 0.0001


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
        token_counter = Counter(tokens)
        token_freq = {t: token_counter.get(t, 0) / len(tokens) for t in TOP20_TOKENS}
        records.append({
            "folio": f["folio"], "section": f.get("section", "unknown"),
            "n_tokens": len(tokens), "token_freq": token_freq,
        })
    return records


records = build_folios()
print(f"Hand B folios (n>=30): {len(records)}")
sections = sorted(set(r["section"] for r in records))
section_counts = Counter(r["section"] for r in records)
valid_sections = [s for s, c in section_counts.items() if c >= 3]
print(f"Sections with n>=3: {valid_sections}  counts: {dict(section_counts)}")


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


print("\n=== 20 TOKENS x 5 SECTIONS ===")
print(f"{'token':<10}{'section':<15}{'mean_in':<10}{'mean_out':<10}{'d':<8}{'p':<10}{'sig':<5}")
all_tests = []
per_token_tests = defaultdict(list)
for token in TOP20_TOKENS:
    for section in valid_sections:
        xs = [r["token_freq"][token] for r in records if r["section"] == section]
        ys = [r["token_freq"][token] for r in records if r["section"] != section]
        t, p = welch_t(xs, ys)
        d = cohens_d(xs, ys)
        sig = p is not None and p < BONFERRONI_P
        entry = {
            "token": token, "section": section,
            "n_in": len(xs), "n_out": len(ys),
            "mean_in": round(statistics.mean(xs), 5) if xs else 0,
            "mean_out": round(statistics.mean(ys), 5) if ys else 0,
            "t": round(t, 4) if t is not None else None,
            "p": round(p, 6) if p is not None else None,
            "cohens_d": round(d, 4),
            "sig_bonferroni": sig,
        }
        all_tests.append(entry)
        per_token_tests[token].append(entry)
        marker = "SIG" if sig else ""
        t_s = f"{t:+.3f}" if t is not None else "n/a"
        p_s = f"{p:.4f}" if p is not None else "n/a"
        if sig or abs(d) >= 0.7:
            print(f"  {token:<10}{section:<15}{entry['mean_in']:<10}{entry['mean_out']:<10}{d:+.4f}  {p_s:<10}{marker}")

print("\n=== CLASSIFICATION PER TOKEN ===")
classifications = {}
for token in TOP20_TOKENS:
    tests = per_token_tests[token]
    sig_positive = [e for e in tests if e["sig_bonferroni"] and e["cohens_d"] >= 0.5]
    max_abs_d = max(abs(e["cohens_d"]) for e in tests)
    any_sig = any(e["sig_bonferroni"] for e in tests)

    if len(sig_positive) == 1:
        classification = "SECTION-CONCENTRATED"
        preferred_section = sig_positive[0]["section"]
        preferred_d = sig_positive[0]["cohens_d"]
    elif len(sig_positive) >= 2:
        classification = "DISTRIBUTED"
        preferred_section = ",".join(e["section"] for e in sig_positive)
        preferred_d = max(e["cohens_d"] for e in sig_positive)
    elif not any_sig and max_abs_d < 0.3:
        classification = "UNIVERSAL"
        preferred_section = "—"
        preferred_d = None
    else:
        classification = "VARIABLE"
        preferred_section = "—"
        preferred_d = None

    classifications[token] = {
        "classification": classification,
        "preferred_section": preferred_section,
        "preferred_d": preferred_d,
        "max_abs_d": round(max_abs_d, 4),
    }
    marker = "[CONCENTRATED]" if classification == "SECTION-CONCENTRATED" else f"[{classification}]"
    print(f"  {token:<12} {marker:<22} preferred: {preferred_section}  max|d|={max_abs_d:.3f}")

section_concentrated = [t for t, v in classifications.items() if v["classification"] == "SECTION-CONCENTRATED"]
preferred_sections = set(classifications[t]["preferred_section"] for t in section_concentrated)
distributed = [t for t, v in classifications.items() if v["classification"] == "DISTRIBUTED"]
universal = [t for t, v in classifications.items() if v["classification"] == "UNIVERSAL"]
variable = [t for t, v in classifications.items() if v["classification"] == "VARIABLE"]

print(f"\n  Section-concentrated ({len(section_concentrated)}): {section_concentrated}")
print(f"  Distributed ({len(distributed)}): {distributed}")
print(f"  Universal ({len(universal)}): {universal}")
print(f"  Variable ({len(variable)}): {variable}")
print(f"  Unique preferred sections: {len(preferred_sections)}: {sorted(preferred_sections)}")

if len(section_concentrated) >= 3 and len(preferred_sections) >= 2:
    verdict = "CONFIRMED_SYSTEMATIC"
elif len(section_concentrated) >= 1:
    verdict = "PARTIAL_PATTERN"
else:
    verdict = "CHEDY_OUTLIER"

print(f"\n  VERDICT: {verdict}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-HAND-B-MARKER-CONCENTRATION-01",
    "n_hand_b_folios": len(records),
    "sections": {s: c for s, c in section_counts.items()},
    "all_tests": all_tests,
    "classifications": classifications,
    "summary": {
        "section_concentrated": section_concentrated,
        "distributed": distributed,
        "universal": universal,
        "variable": variable,
        "unique_preferred_sections": sorted(preferred_sections),
    },
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "hand_b_marker_concentration_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
