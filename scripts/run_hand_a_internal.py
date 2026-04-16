"""
Execute pre-registered H-BV-HAND-A-INTERNAL-01 (locked 0a57312).

Three tests within Hand A only:
  (1) Inflectional: mean suffixes per frequent skeleton; %-with->=2
  (2) Plant-folio specificity: bigram-Jaccard plant-plant vs plant-nonplant
  (3) LDA topic section purity

Decision: all three pass -> natural-language-like. Any fail -> code/cipher.
"""
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
PLANT_CSV = ROOT / "raw/research/plant-identifications.csv"

EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
VOWELS = set("aoei")
SUFFIX_CHARS = "ynrmg"

def consonant_skeleton_no_suffix(word, is_line_initial=False):
    """Strip vowels, line-init gallows, and ONE trailing suffix char; return (skel, suffix_char or empty)."""
    if is_line_initial and word and word[0] in "tp" and (len(word)==1 or word[1]!="h"):
        word = word[1:]
    suffix = ""
    if word and word[-1] in SUFFIX_CHARS and len(word) > 2:
        suffix = word[-1]
        word = word[:-1]
    out = []; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                out.append(sy); i += len(ev); matched = True; break
        if not matched:
            i += 1  # skip vowels/unknowns
    return "".join(out), suffix

# Index Hand A folios
hand_a_folios = []
folio_tokens = defaultdict(list)
folio_lines_per = defaultdict(list)
folio_section = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    if f.get("currier_language") != "A": continue
    folio_section[fid] = f["section"]
    hand_a_folios.append(fid)
    for line in f["lines"]:
        folio_lines_per[fid].append(line["words"])
        folio_tokens[fid].extend(line["words"])
# Filter to tokens>=20
hand_a_folios = [f for f in hand_a_folios if len(folio_tokens[f]) >= 20]
print(f"Hand A folios (>=20 tokens): {len(hand_a_folios)}")

plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        plant_folios.add(r["folio"])

hand_a_plant = [f for f in hand_a_folios if f in plant_folios]
hand_a_nonplant_h = [f for f in hand_a_folios
                     if folio_section.get(f) == "herbal" and f not in plant_folios]
print(f"  Plant: {len(hand_a_plant)}  Non-plant herbal: {len(hand_a_nonplant_h)}")

# =========================================================================
# TEST 1: INFLECTION
# =========================================================================
print("\n" + "="*72)
print("  TEST 1 — inflectional morphology")
print("="*72)

skel_suffixes = defaultdict(Counter)  # skel -> Counter(suffix)
skel_tokens = Counter()
for fid in hand_a_folios:
    for line_words in folio_lines_per[fid]:
        for i, w in enumerate(line_words):
            sk, sfx = consonant_skeleton_no_suffix(w, is_line_initial=(i == 0))
            if not sk: continue
            skel_tokens[sk] += 1
            if sfx:
                skel_suffixes[sk][sfx] += 1
            else:
                skel_suffixes[sk][""] += 1  # count no-suffix occurrences too

frequent_skels = [sk for sk, c in skel_tokens.items() if c >= 5]
print(f"  Consonant skeletons appearing >=5 times: {len(frequent_skels)}")

# For each frequent skeleton, count distinct suffix chars (not counting empty)
suffix_counts = []
for sk in frequent_skels:
    suffixes_used = {s for s in skel_suffixes[sk] if s}  # non-empty
    suffix_counts.append(len(suffixes_used))

if suffix_counts:
    mean_sfx = statistics.mean(suffix_counts)
    med_sfx = statistics.median(suffix_counts)
    max_sfx = max(suffix_counts)
    ge2_count = sum(1 for n in suffix_counts if n >= 2)
    ge2_pct = ge2_count / len(suffix_counts)
    print(f"  Distinct suffix chars per skeleton:")
    print(f"    mean:       {mean_sfx:.2f}")
    print(f"    median:     {med_sfx}")
    print(f"    max:        {max_sfx}")
    print(f"    >=2 suffixes: {ge2_count}/{len(suffix_counts)} = {ge2_pct:.1%}")
    sfx_distribution = Counter(suffix_counts)
    for k in sorted(sfx_distribution):
        print(f"      {k} distinct suffixes: {sfx_distribution[k]} skeletons")
    test1_pass = mean_sfx >= 2.0 and ge2_pct >= 0.50
else:
    mean_sfx = med_sfx = max_sfx = 0
    ge2_pct = 0.0
    test1_pass = False

print(f"  TEST 1: {'PASS' if test1_pass else 'FAIL'} (threshold mean >=2 AND >=50% take >=2)")

# =========================================================================
# TEST 2: PLANT-FOLIO SPECIFICITY
# =========================================================================
print("\n" + "="*72)
print("  TEST 2 — plant-folio bigram specificity")
print("="*72)

def folio_bigram_top(fid, k=50):
    bg = Counter()
    for line_words in folio_lines_per[fid]:
        for a, b in zip(line_words, line_words[1:]):
            bg[(a, b)] += 1
    return {bg_pair for bg_pair, _ in bg.most_common(k)}

def mean_pairwise_jaccard(folios, k=50):
    if len(folios) < 2: return 0.0
    sets = [folio_bigram_top(f, k) for f in folios]
    js = []
    for i in range(len(sets)):
        for j in range(i+1, len(sets)):
            a, b = sets[i], sets[j]
            js.append(len(a & b)/len(a | b) if a | b else 0)
    return statistics.mean(js) if js else 0.0

def mean_cross_jaccard(ga, gb, k=50):
    sa = [folio_bigram_top(f, k) for f in ga]
    sb = [folio_bigram_top(f, k) for f in gb]
    js = []
    for a in sa:
        for b in sb:
            js.append(len(a & b)/len(a | b) if a | b else 0)
    return statistics.mean(js) if js else 0.0

within_plant = mean_pairwise_jaccard(hand_a_plant)
across_plant_nonplant = mean_cross_jaccard(hand_a_plant, hand_a_nonplant_h)

print(f"  within-Hand-A plant bigram Jaccard: {within_plant:.4f}")
print(f"  Hand-A plant vs Hand-A non-plant herbal: {across_plant_nonplant:.4f}")
ratio2 = within_plant / across_plant_nonplant if across_plant_nonplant else 0
print(f"  ratio (within-plant / across): {ratio2:.2f}x")
test2_pass = ratio2 >= 1.3
print(f"  TEST 2: {'PASS' if test2_pass else 'FAIL'} (threshold >= 1.3x)")

# =========================================================================
# TEST 3: LDA topic section purity
# =========================================================================
print("\n" + "="*72)
print("  TEST 3 — LDA topic structure (K=8)")
print("="*72)

# Folio-level bag-of-words
docs = []
labels = []
for fid in hand_a_folios:
    text = " ".join(folio_tokens[fid])
    docs.append(text)
    labels.append(folio_section.get(fid, "?"))

vec = CountVectorizer(min_df=2, token_pattern=r"\S+")
X = vec.fit_transform(docs)
print(f"  Hand-A folios: {X.shape[0]}, vocab: {X.shape[1]}")

K = 8
lda = LatentDirichletAllocation(n_components=K, random_state=42,
                                learning_method="batch", max_iter=50)
topic_folio = lda.fit_transform(X)  # n_folios x K

print(f"\n  Per-topic top-20 folio section purity:")
purities = []
for t in range(K):
    # top-20 folios by weight on this topic
    top_idx = np.argsort(topic_folio[:, t])[::-1][:min(20, len(docs))]
    sec_counts = Counter(labels[i] for i in top_idx)
    top_sec, top_n = sec_counts.most_common(1)[0]
    purity = top_n / len(top_idx)
    purities.append(purity)
    print(f"    topic {t}: dominant={top_sec:<14} purity={purity:.2f}  distribution={dict(sec_counts)}")

mean_purity = statistics.mean(purities)
print(f"\n  Mean top-20 section purity across topics: {mean_purity:.3f}")
test3_pass = mean_purity >= 0.60
print(f"  TEST 3: {'PASS' if test3_pass else 'FAIL'} (threshold >=0.60)")

# =========================================================================
# Decision
# =========================================================================
print("\n" + "="*72)
print("  PRE-REGISTERED DECISION")
print("="*72)
print(f"  Test 1 (inflection):        {'PASS' if test1_pass else 'FAIL'}  "
      f"(mean {mean_sfx:.2f}, >=2 {ge2_pct:.1%})")
print(f"  Test 2 (plant specificity): {'PASS' if test2_pass else 'FAIL'}  "
      f"(ratio {ratio2:.2f}x)")
print(f"  Test 3 (LDA purity):        {'PASS' if test3_pass else 'FAIL'}  "
      f"(mean {mean_purity:.3f})")

passes = sum([test1_pass, test2_pass, test3_pass])
if passes == 3:
    verdict = "CONFIRMED (natural-language-like)"
elif passes == 0:
    verdict = "REFUTED (code/cipher)"
else:
    verdict = f"PARTIAL ({passes}/3 pass)"
print(f"\n  OVERALL: {verdict}")

out = ROOT / "outputs" / "hand_a_internal_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-HAND-A-INTERNAL-01",
    "locked_in_commit": "0a57312",
    "n_hand_a_folios": len(hand_a_folios),
    "test_1_inflection": {
        "frequent_skeletons": len(frequent_skels),
        "mean_distinct_suffixes": round(mean_sfx, 3),
        "median_suffixes": med_sfx,
        "max_suffixes": max_sfx,
        "pct_with_ge2": round(ge2_pct, 3),
        "pass": test1_pass,
    },
    "test_2_plant_specificity": {
        "within_plant_jaccard": round(within_plant, 4),
        "across_plant_nonplant_jaccard": round(across_plant_nonplant, 4),
        "ratio": round(ratio2, 3) if across_plant_nonplant else None,
        "pass": test2_pass,
    },
    "test_3_lda": {
        "K": K,
        "per_topic_purity": purities,
        "mean_purity": round(mean_purity, 4),
        "pass": test3_pass,
    },
    "verdict": verdict,
    "passes": passes,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out}")
