"""Execute pre-registered H-BV-HAND-B-CLUSTER-DIAGNOSTIC-01.

Recover FRONT/BACK cluster assignments from H-BV-HAND-B-VOWEL-HARMONY-01
(re-run with same seed/methodology), then test whether cluster membership
tracks suffix-family preference (-edy family vs -aiin family).
"""
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI = sorted(["ckh","cth","cph","ch","sh","ol"], key=lambda s: -len(s))
VOWEL_INNERS = ["i","e","o","a"]
FRONT_SET = {"i","e"}; BACK_SET = {"o","a"}

EDY_FAMILY = sorted({"edy", "eedy", "eody", "chedy", "shedy", "qokedy", "qokeedy", "otedy"}, key=len, reverse=True)
AIIN_FAMILY = sorted({"aiin", "ain", "iin", "aiiin", "daiin", "qokain", "qokaiin", "okaiin"}, key=len, reverse=True)
ALL_ENDINGS = sorted(set(EDY_FAMILY) | set(AIIN_FAMILY), key=len, reverse=True)


def tokenize(word):
    out = []; i = 0
    while i < len(word):
        matched = False
        for t in MULTI:
            if word.startswith(t, i):
                out.append(t); i += len(t); matched = True; break
        if not matched:
            out.append(word[i]); i += 1
    return out


def classify_ending(token):
    """Return 'edy' or 'aiin' if token ends in a family member (longest match), else None."""
    for ending in ALL_ENDINGS:
        if token.endswith(ending):
            if ending in EDY_FAMILY:
                return "edy"
            return "aiin"
    return None


hand_b_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") == "B":
        for line in f["lines"]:
            hand_b_words.extend(line["words"])

tokenised = [tokenize(w) for w in hand_b_words]
valid_idx = [i for i, t in enumerate(tokenised) if len(t) >= 3]
valid = [tokenised[i] for i in valid_idx]
raw_tokens = [hand_b_words[i] for i in valid_idx]

stem_tokens_raw = defaultdict(list)
stem_inner_counts = defaultdict(Counter)
for t, raw in zip(valid, raw_tokens):
    stem = tuple(t[:-2]); inner = t[-2]
    stem_tokens_raw[stem].append(raw)
    if inner in VOWEL_INNERS:
        stem_inner_counts[stem][inner] += 1

eligible = {}
for stem, ctr in stem_inner_counts.items():
    if len(ctr) >= 3 and sum(ctr.values()) >= 5:
        eligible[stem] = ctr

print(f"Eligible stems (replication of Hand B harmony test): {len(eligible)}")
stems_list = list(eligible.keys())
X = np.zeros((len(eligible), 4))
for i, stem in enumerate(stems_list):
    ctr = eligible[stem]; total = sum(ctr.values())
    for j, v in enumerate(VOWEL_INNERS):
        X[i, j] = ctr.get(v, 0) / total

km = KMeans(n_clusters=2, n_init=50, random_state=42)
labels = km.fit_predict(X)
centers = km.cluster_centers_
fs0 = centers[0, 0] + centers[0, 1]
fs1 = centers[1, 0] + centers[1, 1]
cluster_label = ({0: "FRONT", 1: "BACK"} if fs0 > fs1 else {0: "BACK", 1: "FRONT"})
print(f"  Cluster 0 ({cluster_label[0]}) centre: {centers[0].round(3).tolist()}")
print(f"  Cluster 1 ({cluster_label[1]}) centre: {centers[1].round(3).tolist()}")

stem_cluster = {stem: cluster_label[labels[i]] for i, stem in enumerate(stems_list)}
front_stems = [s for s, c in stem_cluster.items() if c == "FRONT"]
back_stems = [s for s, c in stem_cluster.items() if c == "BACK"]
print(f"\n  FRONT stems: {len(front_stems)}  BACK stems: {len(back_stems)}")

def per_stem_fractions(stem):
    toks = stem_tokens_raw[stem]
    n = len(toks)
    edy_count = sum(1 for t in toks if classify_ending(t) == "edy")
    aiin_count = sum(1 for t in toks if classify_ending(t) == "aiin")
    return (edy_count / n, aiin_count / n, n)

front_edy = []; front_aiin = []; front_n = []
back_edy = []; back_aiin = []; back_n = []
for stem in front_stems:
    e, a, n = per_stem_fractions(stem)
    front_edy.append(e); front_aiin.append(a); front_n.append(n)
for stem in back_stems:
    e, a, n = per_stem_fractions(stem)
    back_edy.append(e); back_aiin.append(a); back_n.append(n)

print(f"\nFRONT cluster per-stem mean EDY-family fraction:  {statistics.mean(front_edy):.4f}  (std {statistics.stdev(front_edy):.4f})")
print(f"FRONT cluster per-stem mean AIIN-family fraction: {statistics.mean(front_aiin):.4f}  (std {statistics.stdev(front_aiin):.4f})")
print(f"BACK cluster per-stem mean EDY-family fraction:   {statistics.mean(back_edy):.4f}  (std {statistics.stdev(back_edy):.4f})")
print(f"BACK cluster per-stem mean AIIN-family fraction:  {statistics.mean(back_aiin):.4f}  (std {statistics.stdev(back_aiin):.4f})")


def welch_t(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    vx = statistics.variance(xs) if len(xs) > 1 else 0
    vy = statistics.variance(ys) if len(ys) > 1 else 0
    nx, ny = len(xs), len(ys)
    se = math.sqrt(vx / nx + vy / ny) if vx + vy > 0 else 0
    if se == 0:
        return 0.0, 1.0
    t = (mx - my) / se
    df_num = (vx / nx + vy / ny) ** 2
    df_den = (vx / nx) ** 2 / (nx - 1) if vx > 0 and nx > 1 else 0
    df_den += (vy / ny) ** 2 / (ny - 1) if vy > 0 and ny > 1 else 0
    df = df_num / df_den if df_den > 0 else nx + ny - 2
    from math import lgamma

    def betainc(x, a, b, n_terms=80):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        lbeta = lgamma(a) + lgamma(b) - lgamma(a + b)
        front = a * math.log(x) + b * math.log(1 - x) - lbeta - math.log(a)
        front = math.exp(front)
        c = 1.0; result = c
        for n in range(1, n_terms):
            if n % 2 == 1:
                m = (n - 1) // 2
                num = -(a + m) * (a + b + m) * x
                den = (a + 2 * m) * (a + 2 * m + 1)
            else:
                m = n // 2
                num = m * (b - m) * x
                den = (a + 2 * m - 1) * (a + 2 * m)
            c = c * num / den; result += c
            if abs(c) < 1e-15: break
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
    vx = statistics.variance(xs); vy = statistics.variance(ys)
    sd = math.sqrt((vx * (len(xs) - 1) + vy * (len(ys) - 1)) / (len(xs) + len(ys) - 2))
    return (statistics.mean(xs) - statistics.mean(ys)) / sd if sd > 0 else 0


t_edy, p_edy = welch_t(front_edy, back_edy)
d_edy = cohens_d(front_edy, back_edy)
t_aiin, p_aiin = welch_t(back_aiin, front_aiin)  # BACK vs FRONT for AIIN direction
d_aiin = cohens_d(back_aiin, front_aiin)

print(f"\nFRONT-EDY vs BACK-EDY Welch t-test: t={t_edy:+.3f}  p={p_edy:.6f}  d={d_edy:+.3f}")
print(f"BACK-AIIN vs FRONT-AIIN Welch t-test: t={t_aiin:+.3f}  p={p_aiin:.6f}  d={d_aiin:+.3f}")

front_edy_advantage = (p_edy < 0.001 and d_edy > 1.0)
back_aiin_advantage = (p_aiin < 0.001 and d_aiin > 1.0)

if front_edy_advantage and back_aiin_advantage:
    verdict = "CONFIRMED"
elif p_edy >= 0.01 and p_aiin >= 0.01:
    verdict = "REFUTED"
else:
    verdict = "PARTIAL"

print(f"\n  VERDICT: {verdict}")
print(f"\n  Interpretation:")
if verdict == "CONFIRMED":
    print(f"    Harmony finding dissolves into suffix-family preference.")
    print(f"    Consistent with Bowern & Lindemann positional-constraint framework.")
elif verdict == "REFUTED":
    print(f"    Clustering doesn't track suffix-family preference.")
    print(f"    Harmony interpretation survives this diagnostic.")
else:
    print(f"    Partial tracking; one direction strong, other weak.")

out = {
    "generated": "2026-04-18",
    "hypothesis": "H-BV-HAND-B-CLUSTER-DIAGNOSTIC-01",
    "n_eligible_stems": len(eligible),
    "n_front": len(front_stems), "n_back": len(back_stems),
    "edy_family_set": list(EDY_FAMILY),
    "aiin_family_set": list(AIIN_FAMILY),
    "front_cluster_mean_edy_fraction": round(statistics.mean(front_edy), 4),
    "front_cluster_mean_aiin_fraction": round(statistics.mean(front_aiin), 4),
    "back_cluster_mean_edy_fraction": round(statistics.mean(back_edy), 4),
    "back_cluster_mean_aiin_fraction": round(statistics.mean(back_aiin), 4),
    "welch_edy": {"t": round(t_edy, 4), "p": round(p_edy, 6), "d": round(d_edy, 4)},
    "welch_aiin": {"t": round(t_aiin, 4), "p": round(p_aiin, 6), "d": round(d_aiin, 4)},
    "front_edy_advantage_meets_threshold": front_edy_advantage,
    "back_aiin_advantage_meets_threshold": back_aiin_advantage,
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "hand_b_cluster_diagnostic_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
