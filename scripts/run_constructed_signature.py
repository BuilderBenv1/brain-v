"""
Execute pre-registered H-BV-CONSTRUCTED-SIGNATURE-01.

6 metrics on 7 corpora. Rank Hand A's closeness to natural /
constructed / random baselines per metric.
"""
import json
import math
import random
import re
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")


def load_hand_a_text():
    CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
    words = []
    for f in CORPUS["folios"]:
        if f.get("currier_language") == "A":
            for line in f["lines"]:
                for w in line["words"]:
                    if w:
                        words.append(w)
    return " ".join(words)


def load_conllu_plaintext(path):
    words = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            if "-" in parts[0] or "." in parts[0]:
                continue
            form = parts[1]
            if form and form != "_":
                words.append(form.lower())
    return " ".join(words)


def load_plaintext(path):
    text_parts = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("==="):
                continue
            text_parts.append(line)
    return "\n".join(text_parts).lower()


def normalise(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


print("Loading corpora...")
hand_a_raw = load_hand_a_text()
hand_a_text = normalise(hand_a_raw)
print(f"  Hand A: {len(hand_a_text)} chars")

basque_text = normalise(load_conllu_plaintext(ROOT / "raw/corpus/reference-corpora/eu_bdt-ud-train.conllu"))
print(f"  Basque: {len(basque_text)} chars")

hungarian_text = normalise(load_conllu_plaintext(ROOT / "raw/corpus/reference-corpora/hu_szeged-ud-train.conllu"))
print(f"  Hungarian: {len(hungarian_text)} chars")

turkish_text = normalise(load_conllu_plaintext(ROOT / "raw/corpus/reference-corpora/tr_imst-ud-train.conllu"))
print(f"  Turkish: {len(turkish_text)} chars")

esperanto_text = normalise(load_plaintext(ROOT / "raw/corpus/reference-corpora/esperanto-sample.txt"))
print(f"  Esperanto: {len(esperanto_text)} chars")

random.seed(42)
char_dist = list(hand_a_text)
random.shuffle(char_dist)
shuffled_text = "".join(char_dist)
print(f"  Shuffled Hand A: {len(shuffled_text)} chars")

random.seed(43)
bigram_counts = Counter()
for i in range(len(hand_a_text) - 1):
    bigram_counts[(hand_a_text[i], hand_a_text[i + 1])] += 1
first_char_counts = Counter()
for (a, _), c in bigram_counts.items():
    first_char_counts[a] += c
transitions = {}
for (a, b), c in bigram_counts.items():
    if a not in transitions:
        transitions[a] = []
    transitions[a].append((b, c))

chars = list(hand_a_text)
gen = [chars[0]]
for _ in range(len(hand_a_text) - 1):
    prev = gen[-1]
    if prev not in transitions:
        gen.append(random.choice(chars))
        continue
    opts = transitions[prev]
    total = sum(c for _, c in opts)
    r = random.random() * total
    acc = 0
    for b, c in opts:
        acc += c
        if r <= acc:
            gen.append(b)
            break
markov_text = "".join(gen)
print(f"  Markov-1 Hand A: {len(markov_text)} chars")

CORPORA = {
    "Hand_A": hand_a_text,
    "Basque": basque_text,
    "Hungarian": hungarian_text,
    "Turkish": turkish_text,
    "Esperanto": esperanto_text,
    "Shuffled_HA": shuffled_text,
    "Markov_HA": markov_text,
}


def shannon_entropy(text):
    counts = Counter(text)
    total = sum(counts.values())
    if total == 0:
        return 0.0, 0
    H = -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)
    return H, len(counts)


def conditional_entropy(text):
    bigrams = Counter()
    firsts = Counter()
    for i in range(len(text) - 1):
        bigrams[(text[i], text[i + 1])] += 1
        firsts[text[i]] += 1
    total = sum(bigrams.values())
    if total == 0:
        return 0.0
    H = 0.0
    for (a, b), ab_c in bigrams.items():
        p_ab = ab_c / total
        p_b_given_a = ab_c / firsts[a] if firsts[a] > 0 else 0
        if p_b_given_a > 0:
            H += p_ab * math.log2(1 / p_b_given_a)
    return H


def markov_reachability(text):
    alphabet = set(text)
    bigrams = set()
    for i in range(len(text) - 1):
        bigrams.add((text[i], text[i + 1]))
    possible = len(alphabet) ** 2
    return len(bigrams) / possible if possible else 0.0


def zipf_slope(text, top_n=1000):
    words = [w for w in text.split() if w]
    if not words:
        return 0.0
    freqs = Counter(words)
    ranked = sorted(freqs.values(), reverse=True)[:top_n]
    if len(ranked) < 10:
        return 0.0
    xs = [math.log(r + 1) for r in range(len(ranked))]
    ys = [math.log(f) for f in ranked]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    return abs(num / den)


def type_token_ratio(text, window=5000):
    words = [w for w in text.split() if w]
    if not words:
        return 0.0
    w = min(window, len(words))
    return len(set(words[:w])) / w


def heaps_slope(text):
    words = [w for w in text.split() if w]
    if len(words) < 100:
        return 0.0
    positions = [1, 2, 5, 10, 50, 100, 500, 1000, 2000, 5000, 10000]
    positions = [p for p in positions if p <= len(words)]
    vs = []
    for p in positions:
        vs.append(len(set(words[:p])))
    xs = [math.log(p) for p in positions]
    ys = [math.log(v) for v in vs]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    return num / den


print("\n=== COMPUTING 6 METRICS PER CORPUS ===")
results = {}
for name, text in CORPORA.items():
    H_raw, alpha = shannon_entropy(text)
    H_max = math.log2(alpha) if alpha > 1 else 1
    H_norm = H_raw / H_max if H_max > 0 else 0
    H_cond = conditional_entropy(text)
    reach = markov_reachability(text)
    zipf = zipf_slope(text)
    ttr = type_token_ratio(text)
    heaps = heaps_slope(text)
    results[name] = {
        "M1_H_norm": round(H_norm, 4),
        "M1_H_raw": round(H_raw, 4),
        "alphabet_size": alpha,
        "M2_H_cond": round(H_cond, 4),
        "M3_reach": round(reach, 4),
        "M4_zipf": round(zipf, 4),
        "M5_ttr": round(ttr, 4),
        "M6_heaps": round(heaps, 4),
    }
    print(f"  {name:<15} alphabet={alpha:<4} H_norm={H_norm:.4f}  H_cond={H_cond:.4f}  reach={reach:.4f}  zipf={zipf:.4f}  ttr={ttr:.4f}  heaps={heaps:.4f}")

print("\n=== BASELINES AND DISTANCES ===")
metric_keys = ["M1_H_norm", "M2_H_cond", "M3_reach", "M4_zipf", "M5_ttr", "M6_heaps"]
metric_labels = ["M1 H_norm", "M2 H_cond", "M3 reach", "M4 zipf", "M5 ttr", "M6 heaps"]

hand_a = results["Hand_A"]
natural_names = ["Basque", "Hungarian", "Turkish"]
random_names = ["Shuffled_HA", "Markov_HA"]
constructed_name = "Esperanto"

closest_counts = {"natural": 0, "constructed": 0, "random": 0}
per_metric_report = []

for mk, ml in zip(metric_keys, metric_labels):
    nat_vals = [results[n][mk] for n in natural_names]
    nat_mean = statistics.mean(nat_vals)
    constructed_val = results[constructed_name][mk]
    rand_vals = [results[r][mk] for r in random_names]
    rand_mean = statistics.mean(rand_vals)
    ha_val = hand_a[mk]
    d_nat = abs(ha_val - nat_mean)
    d_con = abs(ha_val - constructed_val)
    d_rand = abs(ha_val - rand_mean)
    closest = min([("natural", d_nat), ("constructed", d_con), ("random", d_rand)], key=lambda x: x[1])
    closest_counts[closest[0]] += 1
    per_metric_report.append({
        "metric": ml,
        "hand_a": ha_val,
        "natural_mean": round(nat_mean, 4),
        "constructed": constructed_val,
        "random_mean": round(rand_mean, 4),
        "d_natural": round(d_nat, 4),
        "d_constructed": round(d_con, 4),
        "d_random": round(d_rand, 4),
        "closest": closest[0],
    })
    print(f"  {ml:<14} HA={ha_val:<8} nat={nat_mean:.4f} con={constructed_val:<8} rand={rand_mean:.4f}  closest={closest[0]}")

print(f"\n  Closest counts: natural={closest_counts['natural']}  constructed={closest_counts['constructed']}  random={closest_counts['random']}")

if closest_counts["constructed"] >= 4:
    verdict = "CONFIRMED_CONSTRUCTED"
elif closest_counts["natural"] >= 4:
    verdict = "REFUTED_CONSTRUCTED"
elif closest_counts["random"] >= 4:
    verdict = "CLOSEST_TO_RANDOM"
elif max(closest_counts.values()) == 3 and closest_counts["constructed"] == 3:
    verdict = "NEAR_CONSTRUCTED"
else:
    verdict = "PARTIAL"

print(f"\n  VERDICT: {verdict}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-CONSTRUCTED-SIGNATURE-01",
    "corpus_sizes_chars": {name: len(text) for name, text in CORPORA.items()},
    "per_corpus_metrics": results,
    "per_metric_report": per_metric_report,
    "closest_counts": closest_counts,
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "constructed_signature_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
