"""
Execute pre-registered H-BV-MARKOV-VALIDATION-01.

Four sub-tests:
  S1 Tokenisation invariance on Hand A/B H_cond
  S2 Reference corpus recomputation + alphabet normalisation
  S3 Higher-order H_cond (k=1..4) comparison
  S4 Subset stability within Hand A
"""
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")


def load_hand_text_and_folios(currier):
    CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
    entries = []
    for f in CORPUS["folios"]:
        if f.get("currier_language") == currier:
            words = []
            for line in f["lines"]:
                for w in line["words"]:
                    if w:
                        words.append(w)
            entries.append({"folio": f["folio"], "section": f.get("section"), "text": " ".join(words)})
    return entries


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
            if not line or line.startswith("==="):
                continue
            text_parts.append(line)
    return "\n".join(text_parts).lower()


def normalise(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


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


def h_cond_order_k(text, k, min_context=5):
    context_counts = Counter()
    joint_counts = Counter()
    for i in range(len(text) - k):
        context = text[i:i + k]
        nxt = text[i + k]
        context_counts[context] += 1
        joint_counts[(context, nxt)] += 1
    total = sum(c for (ctx, _), c in joint_counts.items() if context_counts[ctx] >= min_context)
    if total == 0:
        return 0.0
    H = 0.0
    for (ctx, x), c in joint_counts.items():
        if context_counts[ctx] < min_context:
            continue
        p_joint = c / total
        p_x_given_ctx = c / context_counts[ctx]
        if p_x_given_ctx > 0:
            H += p_joint * math.log2(1 / p_x_given_ctx)
    return H


print("Loading corpora...")
hand_a_entries = load_hand_text_and_folios("A")
hand_b_entries = load_hand_text_and_folios("B")

hand_a_text = normalise(" ".join(e["text"] for e in hand_a_entries))
hand_b_text = normalise(" ".join(e["text"] for e in hand_b_entries))
basque_text = normalise(load_conllu_plaintext(ROOT / "raw/corpus/reference-corpora/eu_bdt-ud-train.conllu"))
hungarian_text = normalise(load_conllu_plaintext(ROOT / "raw/corpus/reference-corpora/hu_szeged-ud-train.conllu"))
turkish_text = normalise(load_conllu_plaintext(ROOT / "raw/corpus/reference-corpora/tr_imst-ud-train.conllu"))
esperanto_text = normalise(load_plaintext(ROOT / "raw/corpus/reference-corpora/esperanto-sample.txt"))

print(f"  Hand A: {len(hand_a_text)} chars ({len(hand_a_entries)} folios)")
print(f"  Hand B: {len(hand_b_text)} chars ({len(hand_b_entries)} folios)")
print(f"  Reference corpora loaded.")

print("\n" + "=" * 70)
print("S1 TOKENISATION INVARIANCE")
print("=" * 70)

def substitute(text, pairs):
    out = text
    for src, tgt in pairs:
        out = out.replace(src, tgt)
    return out

s1_results = {}
for hand_name, text in [("Hand_A", hand_a_text), ("Hand_B", hand_b_text)]:
    s1_results[hand_name] = {}
    t1a = text
    t1b = substitute(text, [("ol", "Q")])
    t1c = substitute(text, [("ol", "Q"), ("qo", "X")])
    t1d = substitute(text, [("cth", "W"), ("cph", "X"), ("ckh", "Y"), ("cfh", "Z")])
    for variant, tt in [("T1a_raw", t1a), ("T1b_ol", t1b), ("T1c_ol_qo", t1c), ("T1d_benchgallows", t1d)]:
        hc = conditional_entropy(tt)
        s1_results[hand_name][variant] = round(hc, 4)
        print(f"  {hand_name} {variant:<22} H_cond = {hc:.4f}")

s1_pass = True
s1_max_dev = 0.0
for hand in ["Hand_A", "Hand_B"]:
    baseline = s1_results[hand]["T1a_raw"]
    for v, val in s1_results[hand].items():
        dev = abs(val - baseline)
        if dev > s1_max_dev:
            s1_max_dev = dev
print(f"\n  Max deviation across all variants + hands: {s1_max_dev:.4f}")
s1_verdict = "PASS" if s1_max_dev <= 0.30 else "FAIL"
print(f"  S1 VERDICT: {s1_verdict}")

print("\n" + "=" * 70)
print("S2 REFERENCE RECOMPUTATION + NORMALISATION")
print("=" * 70)

corpora = {
    "Hand_A": hand_a_text, "Hand_B": hand_b_text,
    "Basque": basque_text, "Hungarian": hungarian_text,
    "Turkish": turkish_text, "Esperanto": esperanto_text,
}

expected = {"Basque": 3.2433, "Hungarian": 3.7029, "Turkish": 3.4833, "Esperanto": 3.4501}
reproduction_ok = True
s2_data = {}
for name, text in corpora.items():
    h_raw = conditional_entropy(text)
    alphabet = len(set(text))
    h_norm = h_raw / math.log2(alphabet) if alphabet > 1 else 0
    s2_data[name] = {"h_raw": round(h_raw, 4), "alphabet": alphabet, "h_norm": round(h_norm, 4)}
    expected_val = expected.get(name)
    repro = "—"
    if expected_val is not None:
        diff = abs(h_raw - expected_val)
        repro = f"expected {expected_val}, diff {diff:.4f} {'OK' if diff < 0.01 else 'FAIL'}"
        if diff >= 0.01:
            reproduction_ok = False
    print(f"  {name:<12} H_raw={h_raw:.4f}  alphabet={alphabet}  H_norm={h_norm:.4f}  {repro}")

ha_norm = s2_data["Hand_A"]["h_norm"]
hb_norm = s2_data["Hand_B"]["h_norm"]
nat_norm_mean = statistics.mean([s2_data[n]["h_norm"] for n in ["Basque", "Hungarian", "Turkish"]])
con_norm = s2_data["Esperanto"]["h_norm"]
diff_ha_nat = nat_norm_mean - ha_norm
diff_hb_nat = nat_norm_mean - hb_norm
print(f"\n  Normalised H_cond: Hand A={ha_norm:.4f}  Hand B={hb_norm:.4f}  Natural mean={nat_norm_mean:.4f}  Esperanto={con_norm:.4f}")
print(f"  Hand A gap to natural (normalised): {diff_ha_nat:.4f}  (threshold >= 0.10)")
print(f"  Hand B gap to natural (normalised): {diff_hb_nat:.4f}")

if reproduction_ok and diff_ha_nat >= 0.10 and diff_hb_nat >= 0.10:
    s2_verdict = "PASS"
elif reproduction_ok:
    s2_verdict = "PARTIAL"
else:
    s2_verdict = "FAIL"
print(f"  S2 VERDICT: {s2_verdict}")

print("\n" + "=" * 70)
print("S3 HIGHER-ORDER H_cond")
print("=" * 70)

s3_corpora = {"Hand_A": hand_a_text, "Hand_B": hand_b_text, "Basque": basque_text, "Hungarian": hungarian_text, "Esperanto": esperanto_text}
s3_results = {}
for name, text in s3_corpora.items():
    vals = {}
    for k in [1, 2, 3, 4]:
        vals[f"k={k}"] = round(h_cond_order_k(text, k, min_context=5), 4)
    ratio_3_1 = vals["k=3"] / vals["k=1"] if vals["k=1"] > 0 else 0
    vals["ratio_3_1"] = round(ratio_3_1, 4)
    s3_results[name] = vals
    print(f"  {name:<12} k=1={vals['k=1']:<8} k=2={vals['k=2']:<8} k=3={vals['k=3']:<8} k=4={vals['k=4']:<8} ratio(k=3/k=1)={vals['ratio_3_1']}")

hand_a_ratio = s3_results["Hand_A"]["ratio_3_1"]
hand_b_ratio = s3_results["Hand_B"]["ratio_3_1"]
nat_ratios = [s3_results[n]["ratio_3_1"] for n in ["Basque", "Hungarian"]]
nat_ratio_mean = statistics.mean(nat_ratios)

print(f"\n  Hand A ratio: {hand_a_ratio}")
print(f"  Hand B ratio: {hand_b_ratio}")
print(f"  Natural mean ratio: {nat_ratio_mean:.4f}")

if hand_a_ratio >= 0.75 and hand_b_ratio >= 0.75 and nat_ratio_mean <= 0.60:
    s3_verdict = "PASS"
elif hand_a_ratio <= 0.60 and hand_b_ratio <= 0.60 and nat_ratio_mean > 0.60:
    s3_verdict = "FAIL"
else:
    s3_verdict = "PARTIAL"
print(f"  S3 VERDICT: {s3_verdict}")

print("\n" + "=" * 70)
print("S4 SUBSET STABILITY (Hand A)")
print("=" * 70)

herbal = normalise(" ".join(e["text"] for e in hand_a_entries if e["section"] == "herbal"))
pharma = normalise(" ".join(e["text"] for e in hand_a_entries if e["section"] == "pharmaceutical"))

total_chars = sum(len(e["text"]) for e in hand_a_entries)
acc = 0
first_half = []
second_half = []
for e in hand_a_entries:
    if acc < total_chars / 2:
        first_half.append(e["text"])
    else:
        second_half.append(e["text"])
    acc += len(e["text"])
first_half_text = normalise(" ".join(first_half))
second_half_text = normalise(" ".join(second_half))

s4_results = {}
for name, t in [("A-herbal", herbal), ("A-pharma", pharma), ("A-first_half", first_half_text), ("A-second_half", second_half_text)]:
    h = conditional_entropy(t)
    s4_results[name] = {"h_cond": round(h, 4), "chars": len(t)}
    print(f"  {name:<16} chars={len(t):<8} H_cond={h:.4f}")

s4_vals = [r["h_cond"] for r in s4_results.values()]
s4_range = max(s4_vals) - min(s4_vals)
print(f"\n  H_cond range (max - min): {s4_range:.4f}  (threshold <= 0.30)")
s4_verdict = "PASS" if s4_range <= 0.30 else "FAIL"
print(f"  S4 VERDICT: {s4_verdict}")

print("\n" + "=" * 70)
print("AGGREGATE VERDICT")
print("=" * 70)

score = {"PASS": 1.0, "PARTIAL": 0.5, "FAIL": 0.0}
subtests = [("S1 tokenisation", s1_verdict), ("S2 reference+norm", s2_verdict), ("S3 higher-order", s3_verdict), ("S4 subset", s4_verdict)]
total = sum(score[v] for _, v in subtests)
print(f"  S1 {s1_verdict}  S2 {s2_verdict}  S3 {s3_verdict}  S4 {s4_verdict}")
print(f"  Aggregate: {total}/4")
if total >= 3.5:
    overall = "ROBUST"
elif total >= 2.5:
    overall = "VALIDATED_WITH_CAVEATS"
elif total >= 1.5:
    overall = "FRAGILE"
else:
    overall = "ARTEFACT_DRIVEN"
print(f"  VERDICT: {overall}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-MARKOV-VALIDATION-01",
    "S1_tokenisation": {"results": s1_results, "max_deviation": round(s1_max_dev, 4), "verdict": s1_verdict},
    "S2_reference_normalisation": {"per_corpus": s2_data, "reproduction_ok": reproduction_ok, "ha_gap_normalised": round(diff_ha_nat, 4), "hb_gap_normalised": round(diff_hb_nat, 4), "verdict": s2_verdict},
    "S3_higher_order": {"per_corpus": s3_results, "hand_a_ratio": hand_a_ratio, "hand_b_ratio": hand_b_ratio, "natural_mean_ratio": round(nat_ratio_mean, 4), "verdict": s3_verdict},
    "S4_subset_stability": {"subsets": s4_results, "range": round(s4_range, 4), "verdict": s4_verdict},
    "aggregate_score": total,
    "overall_verdict": overall,
}
out_path = ROOT / "outputs" / "markov_validation_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
