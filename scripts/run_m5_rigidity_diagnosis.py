"""
Execute pre-registered H-BV-M5-RIGIDITY-DIAGNOSIS-01.

Three sub-tests:
  S1 UD_Basque partition variants
  S2 Hand A partition sensitivity (random + structured alternatives)
  S3 Hand A shuffle null distribution
"""
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
UD_FILE = ROOT / "raw/corpus/reference-corpora/eu_bdt-ud-train.conllu"

MULTI = sorted(["cth", "cph", "ckh", "cfh", "ch", "sh", "ee", "ol"], key=lambda s: -len(s))

TOP10_INNERS = {"i", "e", "o", "a", "ch", "d", "k", "t", "sh", "l"}
TOP5_OUTERS = ["y", "n", "r", "ol", "l"]
VOWEL_PARTITION = {"i", "e", "o", "a"}
CONSONANT_PARTITION = {"ch", "d", "k", "t", "sh", "l"}


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


hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") == "A":
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    hand_a_words.append(w)
tokenised = [tokenize(w) for w in hand_a_words]
valid = [t for t in tokenised if len(t) >= 3]
print(f"Hand A N>=3 tokens: {len(valid)}")

inner_outer_pairs = [(t[-2], t[-1]) for t in valid]


def m5_from_partition(pairs, set_A, set_B, outers):
    count_A = Counter()
    count_B = Counter()
    for inner, outer in pairs:
        if inner in set_A:
            count_A[outer] += 1
        elif inner in set_B:
            count_B[outer] += 1
    total_A = sum(count_A.values())
    total_B = sum(count_B.values())
    asymmetric = 0
    for o in outers:
        p_A = count_A.get(o, 0) / total_A if total_A else 0
        p_B = count_B.get(o, 0) / total_B if total_B else 0
        if p_A > 0 and p_B > 0:
            ratio = max(p_A / p_B, p_B / p_A)
        elif p_A > 0 or p_B > 0:
            ratio = float("inf")
        else:
            ratio = 1.0
        if ratio >= 3.0:
            asymmetric += 1
    return asymmetric / len(outers)


m5_original = m5_from_partition(inner_outer_pairs, VOWEL_PARTITION, CONSONANT_PARTITION, TOP5_OUTERS)
print(f"Hand A M5 (original V/C partition): {m5_original:.4f}")
print()

print("=" * 70)
print("S1 UD_BASQUE OPERATIONALISATION EQUIVALENCE")
print("=" * 70)


def parse_conllu_tokens(path):
    content = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 8:
                continue
            if "-" in parts[0] or "." in parts[0]:
                continue
            upos = parts[3]
            feats_raw = parts[5]
            feats = {}
            if feats_raw != "_":
                for f_ in feats_raw.split("|"):
                    if "=" in f_:
                        k, v = f_.split("=", 1)
                        feats[k] = v
            if upos in {"NOUN", "VERB", "ADJ", "PROPN"}:
                content.append({"upos": upos, "feats": feats})
    return content


ud_tokens = parse_conllu_tokens(UD_FILE)
print(f"UD_Basque content tokens: {len(ud_tokens)}")


def ud_m5(tokens, split_feat, set_A_vals, set_B_vals, outer_feat, min_total=20):
    count_A = Counter()
    count_B = Counter()
    for t in tokens:
        val = t["feats"].get(split_feat)
        if val in set_A_vals:
            bucket = "A"
        elif val in set_B_vals:
            bucket = "B"
        else:
            continue
        outer_val = t["feats"].get(outer_feat)
        if not outer_val:
            continue
        if bucket == "A":
            count_A[outer_val] += 1
        else:
            count_B[outer_val] += 1
    outers = sorted(set(count_A) | set(count_B))
    outers = [o for o in outers if count_A.get(o, 0) + count_B.get(o, 0) >= min_total]
    if not outers:
        return None, 0
    total_A = sum(count_A.values())
    total_B = sum(count_B.values())
    asymmetric = 0
    for o in outers:
        p_A = count_A.get(o, 0) / total_A if total_A else 0
        p_B = count_B.get(o, 0) / total_B if total_B else 0
        if p_A > 0 and p_B > 0:
            ratio = max(p_A / p_B, p_B / p_A)
        elif p_A > 0 or p_B > 0:
            ratio = float("inf")
        else:
            ratio = 1.0
        if ratio >= 3.0:
            asymmetric += 1
    return asymmetric / len(outers), len(outers)


u0, u0_n = ud_m5(ud_tokens, "Number", {"Sing"}, {"Plur"}, "Case")
print(f"  U0 (reference, Case x Number):           M5 = {u0:.4f}  (n_outers = {u0_n})")
u1, u1_n = ud_m5(ud_tokens, "Aspect", {"Perf"}, {"Imp"}, "Case")
print(f"  U1 Aspect Perf vs Imp, Case:              M5 = {u1 if u1 is not None else 'n/a'}  (n = {u1_n})" if u1 is not None else f"  U1: insufficient data")
u2, u2_n = ud_m5(ud_tokens, "Person", {"3"}, {"1", "2"}, "Case")
print(f"  U2 Person 3 vs 1/2, Case:                 M5 = {u2 if u2 is not None else 'n/a'}  (n = {u2_n})" if u2 is not None else f"  U2: insufficient data")
u3, u3_n = ud_m5(ud_tokens, "PronType", {"Prs"}, {"Dem", "Ind", "Int", "Rel", "Tot"}, "Case")
print(f"  U3 PronType Prs vs other, Case:           M5 = {u3 if u3 is not None else 'n/a'}  (n = {u3_n})" if u3 is not None else f"  U3: insufficient data")
u4, u4_n = ud_m5(ud_tokens, "Number", {"Sing"}, {"Plur"}, "Mood")
print(f"  U4 Number Sing vs Plur, Mood:             M5 = {u4 if u4 is not None else 'n/a'}  (n = {u4_n})" if u4 is not None else f"  U4: insufficient data")

u_values = [x for x in [u0, u1, u2, u3, u4] if x is not None]
u_max = max(u_values) if u_values else None
u_mean = statistics.mean(u_values) if u_values else None
print(f"\n  UD_Basque partitions tested: {len(u_values)}. Max M5 = {u_max:.4f}  Mean M5 = {u_mean:.4f}")

if u_max is not None and u_max >= 0.90:
    s1_verdict = "ARTEFACT"
elif u_max is not None and u_max <= 0.75:
    s1_verdict = "GENUINE"
else:
    s1_verdict = "MIXED"
print(f"  S1 VERDICT: {s1_verdict}")

print()
print("=" * 70)
print("S2 PARTITION SENSITIVITY ON HAND A")
print("=" * 70)

single_char = {g for g in TOP10_INNERS if len(g) == 1}
multi_char = {g for g in TOP10_INNERS if len(g) > 1}
m5_H2 = m5_from_partition(inner_outer_pairs, single_char, multi_char, TOP5_OUTERS)
print(f"  H2 Single-char vs multi-char ({len(single_char)}/{len(multi_char)}): M5 = {m5_H2:.4f}")

inner_freq = Counter(t[-2] for t in valid if t[-2] in TOP10_INNERS)
top5_inners = set(g for g, _ in inner_freq.most_common(5))
bottom5_inners = TOP10_INNERS - top5_inners
m5_H3 = m5_from_partition(inner_outer_pairs, top5_inners, bottom5_inners, TOP5_OUTERS)
print(f"  H3 Top-5 freq inners vs bottom-5 ({sorted(top5_inners)[:3]}... / {sorted(bottom5_inners)[:3]}...): M5 = {m5_H3:.4f}")

random.seed(42)
random_m5_4_6 = []
inners_list = list(TOP10_INNERS)
all_4_subsets = list(combinations(inners_list, 4))
random.shuffle(all_4_subsets)
all_4_subsets = all_4_subsets[:min(100, len(all_4_subsets))]
for subset in all_4_subsets:
    set_A = set(subset)
    set_B = TOP10_INNERS - set_A
    random_m5_4_6.append(m5_from_partition(inner_outer_pairs, set_A, set_B, TOP5_OUTERS))
rand_mean_4_6 = statistics.mean(random_m5_4_6)
rand_sorted = sorted(random_m5_4_6)
rand_p5_4_6 = rand_sorted[int(0.05 * len(rand_sorted))]
rand_p95_4_6 = rand_sorted[int(0.95 * len(rand_sorted))]
print(f"  H4 Random 4/6 partitions ({len(random_m5_4_6)} samples): mean={rand_mean_4_6:.4f}  p5={rand_p5_4_6:.4f}  p95={rand_p95_4_6:.4f}")

random.seed(43)
random_m5_5_5 = []
all_5_subsets = list(combinations(inners_list, 5))
random.shuffle(all_5_subsets)
all_5_subsets = all_5_subsets[:min(100, len(all_5_subsets))]
for subset in all_5_subsets:
    set_A = set(subset)
    set_B = TOP10_INNERS - set_A
    random_m5_5_5.append(m5_from_partition(inner_outer_pairs, set_A, set_B, TOP5_OUTERS))
rand_mean_5_5 = statistics.mean(random_m5_5_5)
rand_sorted_5 = sorted(random_m5_5_5)
rand_p5_5 = rand_sorted_5[int(0.05 * len(rand_sorted_5))]
rand_p95_5 = rand_sorted_5[int(0.95 * len(rand_sorted_5))]
print(f"  H5 Random 5/5 partitions ({len(random_m5_5_5)} samples): mean={rand_mean_5_5:.4f}  p5={rand_p5_5:.4f}  p95={rand_p95_5:.4f}")

fraction_random_ge_vc = sum(1 for m in random_m5_4_6 if m >= m5_original) / len(random_m5_4_6)
print(f"  V/C M5 = {m5_original:.4f}. Fraction of random 4/6 partitions with M5 >= V/C: {fraction_random_ge_vc:.4f}")
print(f"  V/C M5 exceeds 95th percentile of random 4/6 partitions? {m5_original >= rand_p95_4_6}")

if m5_original >= rand_p95_4_6:
    s2_verdict = "GENUINE"
elif m5_original <= statistics.median(random_m5_4_6):
    s2_verdict = "ARTEFACT"
else:
    s2_verdict = "MIXED"
print(f"  S2 VERDICT: {s2_verdict}")

print()
print("=" * 70)
print("S3 NOISE FLOOR (SHUFFLE NULL)")
print("=" * 70)

outers_list = [p[1] for p in inner_outer_pairs]
inners_list_all = [p[0] for p in inner_outer_pairs]

random.seed(44)
shuffle_m5 = []
for iteration in range(100):
    shuffled_outers = outers_list[:]
    random.shuffle(shuffled_outers)
    shuffled_pairs = list(zip(inners_list_all, shuffled_outers))
    shuffle_m5.append(m5_from_partition(shuffled_pairs, VOWEL_PARTITION, CONSONANT_PARTITION, TOP5_OUTERS))

shuf_mean = statistics.mean(shuffle_m5)
shuf_sorted = sorted(shuffle_m5)
shuf_p5 = shuf_sorted[int(0.05 * len(shuf_sorted))]
shuf_p95 = shuf_sorted[int(0.95 * len(shuf_sorted))]
p_ge_observed = sum(1 for m in shuffle_m5 if m >= m5_original) / len(shuffle_m5)
print(f"  100 shuffled corpora (V/C partition): mean={shuf_mean:.4f}  p5={shuf_p5:.4f}  p95={shuf_p95:.4f}")
print(f"  Observed Hand A M5 = {m5_original:.4f}")
print(f"  p(shuffled M5 >= observed): {p_ge_observed:.4f}")

if shuf_mean <= 0.50 and p_ge_observed <= 0.01:
    s3_verdict = "GENUINE"
elif shuf_mean >= 0.80:
    s3_verdict = "ARTEFACT"
else:
    s3_verdict = "MIXED"
print(f"  S3 VERDICT: {s3_verdict}")

print()
print("=" * 70)
print("AGGREGATE")
print("=" * 70)

score_map = {"GENUINE": 1.0, "MIXED": 0.5, "ARTEFACT": 0.0}
s1_score = score_map[s1_verdict]
s2_score = score_map[s2_verdict]
s3_score = score_map[s3_verdict]
aggregate = s1_score + s2_score + s3_score

print(f"  S1 operationalisation: {s1_verdict}  (score {s1_score})")
print(f"  S2 partition sensitivity: {s2_verdict}  (score {s2_score})")
print(f"  S3 noise floor: {s3_verdict}  (score {s3_score})")
print(f"  Aggregate: {aggregate}/3")

if aggregate >= 2.5:
    overall = "STRONG_GENUINE"
elif aggregate >= 1.5:
    overall = "PARTIAL_GENUINE"
elif aggregate >= 0.5:
    overall = "MOSTLY_ARTEFACT"
else:
    overall = "PURE_ARTEFACT"
print(f"  OVERALL: {overall}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-M5-RIGIDITY-DIAGNOSIS-01",
    "hand_a_m5_original": round(m5_original, 4),
    "S1_ud_basque_partitions": {
        "U0_case_number": round(u0, 4) if u0 is not None else None,
        "U1_case_aspect": round(u1, 4) if u1 is not None else None,
        "U2_case_person": round(u2, 4) if u2 is not None else None,
        "U3_case_prontype": round(u3, 4) if u3 is not None else None,
        "U4_mood_number": round(u4, 4) if u4 is not None else None,
        "max": round(u_max, 4) if u_max is not None else None,
        "mean": round(u_mean, 4) if u_mean is not None else None,
        "verdict": s1_verdict,
    },
    "S2_partition_sensitivity": {
        "H1_vc_original": round(m5_original, 4),
        "H2_single_vs_multi_char": round(m5_H2, 4),
        "H3_freq_top5_vs_rest": round(m5_H3, 4),
        "H4_random_4_6": {"n": len(random_m5_4_6), "mean": round(rand_mean_4_6, 4), "p5": round(rand_p5_4_6, 4), "p95": round(rand_p95_4_6, 4)},
        "H5_random_5_5": {"n": len(random_m5_5_5), "mean": round(rand_mean_5_5, 4), "p5": round(rand_p5_5, 4), "p95": round(rand_p95_5, 4)},
        "fraction_random_4_6_ge_vc": round(fraction_random_ge_vc, 4),
        "vc_at_or_above_95th_pct": m5_original >= rand_p95_4_6,
        "verdict": s2_verdict,
    },
    "S3_noise_floor": {
        "shuffled_mean": round(shuf_mean, 4),
        "shuffled_p5": round(shuf_p5, 4),
        "shuffled_p95": round(shuf_p95, 4),
        "p_ge_observed": round(p_ge_observed, 4),
        "verdict": s3_verdict,
    },
    "aggregate_score": aggregate,
    "overall_verdict": overall,
}
out_path = ROOT / "outputs" / "m5_rigidity_diagnosis_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
