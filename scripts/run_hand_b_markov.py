"""
Execute pre-registered H-BV-HAND-B-MARKOV-01.

Same 6-metric character-level methodology as CONSTRUCTED-SIGNATURE-01,
applied to Hand B. Side-by-side reporting with Hand A for comparison.
"""
import json
import math
import random
import re
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")


def load_hand_text(currier):
    CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
    words = []
    for f in CORPUS["folios"]:
        if f.get("currier_language") == currier:
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
    vs = [len(set(words[:p])) for p in positions]
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


def all_metrics(text):
    H_raw, alpha = shannon_entropy(text)
    H_max = math.log2(alpha) if alpha > 1 else 1
    H_norm = H_raw / H_max if H_max > 0 else 0
    return {
        "M1_H_norm": round(H_norm, 4),
        "M2_H_cond": round(conditional_entropy(text), 4),
        "M3_reach": round(markov_reachability(text), 4),
        "M4_zipf": round(zipf_slope(text), 4),
        "M5_ttr": round(type_token_ratio(text), 4),
        "M6_heaps": round(heaps_slope(text), 4),
        "alphabet": alpha,
    }


print("Loading corpora...")
hand_a_text = normalise(load_hand_text("A"))
hand_b_text = normalise(load_hand_text("B"))
basque_text = normalise(load_conllu_plaintext(ROOT / "raw/corpus/reference-corpora/eu_bdt-ud-train.conllu"))
hungarian_text = normalise(load_conllu_plaintext(ROOT / "raw/corpus/reference-corpora/hu_szeged-ud-train.conllu"))
turkish_text = normalise(load_conllu_plaintext(ROOT / "raw/corpus/reference-corpora/tr_imst-ud-train.conllu"))
esperanto_text = normalise(load_plaintext(ROOT / "raw/corpus/reference-corpora/esperanto-sample.txt"))

print(f"  Hand A: {len(hand_a_text)} chars")
print(f"  Hand B: {len(hand_b_text)} chars")
print(f"  Basque: {len(basque_text)} chars")
print(f"  Hungarian: {len(hungarian_text)} chars")
print(f"  Turkish: {len(turkish_text)} chars")
print(f"  Esperanto: {len(esperanto_text)} chars")

random.seed(42)
shuffled_b = list(hand_b_text)
random.shuffle(shuffled_b)
shuffled_b_text = "".join(shuffled_b)
print(f"  Shuffled Hand B: {len(shuffled_b_text)} chars")

random.seed(43)
bigram_counts = Counter()
for i in range(len(hand_b_text) - 1):
    bigram_counts[(hand_b_text[i], hand_b_text[i + 1])] += 1
transitions = {}
for (a, b), c in bigram_counts.items():
    transitions.setdefault(a, []).append((b, c))
chars = list(hand_b_text)
gen = [chars[0]]
for _ in range(len(hand_b_text) - 1):
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
markov_b_text = "".join(gen)
print(f"  Markov-1 Hand B: {len(markov_b_text)} chars")

CORPORA = {
    "Hand_A": hand_a_text,
    "Hand_B": hand_b_text,
    "Basque": basque_text,
    "Hungarian": hungarian_text,
    "Turkish": turkish_text,
    "Esperanto": esperanto_text,
    "Shuffled_B": shuffled_b_text,
    "Markov_B": markov_b_text,
}

print("\n=== METRICS PER CORPUS ===")
results = {}
for name, text in CORPORA.items():
    m = all_metrics(text)
    results[name] = m
    print(f"  {name:<15} alphabet={m['alphabet']:<4} H_norm={m['M1_H_norm']:.4f}  H_cond={m['M2_H_cond']:.4f}  reach={m['M3_reach']:.4f}  zipf={m['M4_zipf']:.4f}  ttr={m['M5_ttr']:.4f}  heaps={m['M6_heaps']:.4f}")

print("\n=== SIDE-BY-SIDE HAND A vs HAND B ===")
metric_keys = ["M1_H_norm", "M2_H_cond", "M3_reach", "M4_zipf", "M5_ttr", "M6_heaps"]
metric_labels = ["M1 H_norm", "M2 H_cond", "M3 reach", "M4 zipf", "M5 ttr", "M6 heaps"]
for mk, ml in zip(metric_keys, metric_labels):
    print(f"  {ml:<12}  HA={results['Hand_A'][mk]:<8}  HB={results['Hand_B'][mk]}")

print("\n=== BASELINES AND HAND B DISTANCES ===")
hand_b = results["Hand_B"]
natural_names = ["Basque", "Hungarian", "Turkish"]
random_names = ["Shuffled_B", "Markov_B"]
constructed_name = "Esperanto"
closest_counts = {"natural": 0, "constructed": 0, "random": 0}
per_metric = []
for mk, ml in zip(metric_keys, metric_labels):
    nat_vals = [results[n][mk] for n in natural_names]
    nat_mean = statistics.mean(nat_vals)
    con = results[constructed_name][mk]
    rand_vals = [results[r][mk] for r in random_names]
    rand_mean = statistics.mean(rand_vals)
    hb = hand_b[mk]
    d_nat = abs(hb - nat_mean)
    d_con = abs(hb - con)
    d_rand = abs(hb - rand_mean)
    closest = min([("natural", d_nat), ("constructed", d_con), ("random", d_rand)], key=lambda x: x[1])
    closest_counts[closest[0]] += 1
    per_metric.append({"metric": ml, "hand_b": hb, "natural_mean": round(nat_mean, 4), "constructed": con, "random_mean": round(rand_mean, 4), "closest": closest[0]})
    print(f"  {ml:<12} HB={hb:<8} nat={nat_mean:.4f}  con={con:<8} rand={rand_mean:.4f}  closest={closest[0]}")

print(f"\n  Closest counts (Hand B): natural={closest_counts['natural']}  constructed={closest_counts['constructed']}  random={closest_counts['random']}")

if closest_counts["random"] >= 4:
    verdict = "CONFIRMED_MARKOV_B"
elif closest_counts["natural"] >= 4:
    verdict = "REFUTED_MARKOV_B"
elif closest_counts["constructed"] >= 4:
    verdict = "CLOSEST_TO_CONSTRUCTED_B"
else:
    verdict = "PARTIAL_B"

print(f"\n  LOCKED VERDICT: {verdict}")

hb_hcond = hand_b["M2_H_cond"]
if 2.0 <= hb_hcond <= 2.5:
    m2_verdict = "MARKOV_FLAT_CONFIRMED"
elif hb_hcond >= 3.0:
    m2_verdict = "NATURAL_LIKE_M2"
else:
    m2_verdict = "INTERMEDIATE"
print(f"  M2 SHARP DIAGNOSTIC: H_cond(Hand B) = {hb_hcond:.4f}  -> {m2_verdict}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-HAND-B-MARKOV-01",
    "corpus_sizes_chars": {name: len(text) for name, text in CORPORA.items()},
    "per_corpus_metrics": results,
    "side_by_side_hand_a_vs_b": {ml: {"Hand_A": results["Hand_A"][mk], "Hand_B": results["Hand_B"][mk]} for mk, ml in zip(metric_keys, metric_labels)},
    "per_metric_report": per_metric,
    "closest_counts": closest_counts,
    "locked_verdict": verdict,
    "m2_sharp_diagnostic": m2_verdict,
}
out_path = ROOT / "outputs" / "hand_b_markov_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
