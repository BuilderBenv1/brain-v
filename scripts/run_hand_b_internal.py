"""
Execute pre-registered H-BV-HAND-B-INTERNAL-01 (locked 2b8171b).
Identical methodology to run_hand_a_internal.py, restricted to Hand B.
Same thresholds — no retune.
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
            i += 1
    return "".join(out), suffix

hand_b_folios = []
folio_tokens = defaultdict(list)
folio_lines_per = defaultdict(list)
folio_section = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    if f.get("currier_language") != "B": continue
    folio_section[fid] = f["section"]
    hand_b_folios.append(fid)
    for line in f["lines"]:
        folio_lines_per[fid].append(line["words"])
        folio_tokens[fid].extend(line["words"])
hand_b_folios = [f for f in hand_b_folios if len(folio_tokens[f]) >= 20]
print(f"Hand B folios (>=20 tokens): {len(hand_b_folios)}")

plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        plant_folios.add(r["folio"])
hand_b_plant = [f for f in hand_b_folios if f in plant_folios]
hand_b_nonplant_h = [f for f in hand_b_folios
                     if folio_section.get(f) == "herbal" and f not in plant_folios]
print(f"  Plant: {len(hand_b_plant)}  Non-plant herbal: {len(hand_b_nonplant_h)}")

# ==== TEST 1: INFLECTION ====
print("\n" + "="*72)
print("  TEST 1 — inflectional morphology")
print("="*72)
skel_suffixes = defaultdict(Counter)
skel_tokens = Counter()
for fid in hand_b_folios:
    for line_words in folio_lines_per[fid]:
        for i, w in enumerate(line_words):
            sk, sfx = consonant_skeleton_no_suffix(w, is_line_initial=(i == 0))
            if not sk: continue
            skel_tokens[sk] += 1
            if sfx:
                skel_suffixes[sk][sfx] += 1
            else:
                skel_suffixes[sk][""] += 1

frequent_skels = [sk for sk, c in skel_tokens.items() if c >= 5]
print(f"  Frequent skeletons (>=5): {len(frequent_skels)}")
suffix_counts = [len({s for s in skel_suffixes[sk] if s}) for sk in frequent_skels]
if suffix_counts:
    mean_sfx = statistics.mean(suffix_counts)
    med_sfx = statistics.median(suffix_counts)
    ge2 = sum(1 for n in suffix_counts if n >= 2)
    ge2_pct = ge2/len(suffix_counts)
    print(f"  Mean distinct suffixes: {mean_sfx:.2f}")
    print(f"  Median: {med_sfx}  Max: {max(suffix_counts)}")
    print(f"  >=2 suffixes: {ge2}/{len(suffix_counts)} = {ge2_pct:.1%}")
    dist = Counter(suffix_counts)
    for k in sorted(dist):
        print(f"    {k} distinct suffixes: {dist[k]} skeletons")
    test1_pass = mean_sfx >= 2.0 and ge2_pct >= 0.50
else:
    mean_sfx = 0; ge2_pct = 0; test1_pass = False
print(f"  TEST 1: {'PASS' if test1_pass else 'FAIL'}")

# ==== TEST 2: PLANT-FOLIO BIGRAM SPECIFICITY ====
print("\n" + "="*72)
print("  TEST 2 — plant-folio bigram specificity")
print("="*72)
def folio_bigram_top(fid, k=50):
    bg = Counter()
    for line_words in folio_lines_per[fid]:
        for a, b in zip(line_words, line_words[1:]):
            bg[(a, b)] += 1
    return {bgp for bgp, _ in bg.most_common(k)}

def mean_pairwise(folios, k=50):
    if len(folios) < 2: return 0.0
    sets = [folio_bigram_top(f, k) for f in folios]
    js = []
    for i in range(len(sets)):
        for j in range(i+1, len(sets)):
            a, b = sets[i], sets[j]
            js.append(len(a & b)/len(a | b) if a | b else 0)
    return statistics.mean(js) if js else 0.0

def mean_cross(ga, gb, k=50):
    sa = [folio_bigram_top(f, k) for f in ga]
    sb = [folio_bigram_top(f, k) for f in gb]
    js = []
    for a in sa:
        for b in sb:
            js.append(len(a & b)/len(a | b) if a | b else 0)
    return statistics.mean(js) if js else 0.0

within_plant = mean_pairwise(hand_b_plant)
across = mean_cross(hand_b_plant, hand_b_nonplant_h)
ratio2 = within_plant / across if across else 0
print(f"  within-plant Jaccard:                {within_plant:.4f}")
print(f"  across plant/non-plant herbal:       {across:.4f}")
print(f"  ratio:                                {ratio2:.2f}x")
test2_pass = ratio2 >= 1.3
print(f"  TEST 2: {'PASS' if test2_pass else 'FAIL'}")

# ==== TEST 3: LDA ====
print("\n" + "="*72)
print("  TEST 3 — LDA K=8 section purity")
print("="*72)
docs = [" ".join(folio_tokens[fid]) for fid in hand_b_folios]
labels = [folio_section.get(fid, "?") for fid in hand_b_folios]
vec = CountVectorizer(min_df=2, token_pattern=r"\S+")
X = vec.fit_transform(docs)
print(f"  Hand B folios: {X.shape[0]}, vocab: {X.shape[1]}")
K = 8
lda = LatentDirichletAllocation(n_components=K, random_state=42,
                                learning_method="batch", max_iter=50)
topic_folio = lda.fit_transform(X)

purities = []
for t in range(K):
    top_idx = np.argsort(topic_folio[:, t])[::-1][:min(20, len(docs))]
    sec_counts = Counter(labels[i] for i in top_idx)
    top_sec, top_n = sec_counts.most_common(1)[0]
    pur = top_n / len(top_idx)
    purities.append(pur)
    print(f"  topic {t}: dominant={top_sec:<14} purity={pur:.2f} "
          f"dist={dict(sec_counts)}")
mean_purity = statistics.mean(purities)
print(f"\n  Mean top-20 section purity: {mean_purity:.3f}")
test3_pass = mean_purity >= 0.60
print(f"  TEST 3: {'PASS' if test3_pass else 'FAIL'}")

# ==== Decision ====
print("\n" + "="*72)
print("  PRE-REGISTERED DECISION")
print("="*72)
passes = sum([test1_pass, test2_pass, test3_pass])
print(f"  Test 1: {'PASS' if test1_pass else 'FAIL'} (mean {mean_sfx:.2f}, >=2 {ge2_pct:.1%})")
print(f"  Test 2: {'PASS' if test2_pass else 'FAIL'} (ratio {ratio2:.2f}x)")
print(f"  Test 3: {'PASS' if test3_pass else 'FAIL'} (purity {mean_purity:.3f})")
print(f"  {passes}/3")

if passes == 3:
    verdict = "CONFIRMED (natural-language-like)"
elif passes == 0:
    verdict = "REFUTED"
else:
    verdict = f"PARTIAL ({passes}/3)"
print(f"\n  OVERALL: {verdict}")

# ==== Hand-A comparison ====
print(f"\n  Comparison to Hand A (H-BV-HAND-A-INTERNAL-01 confirmed):")
print(f"    Hand A:  inflection mean 2.46 / 69.8%, plant 1.44x, LDA 0.831")
print(f"    Hand B:  inflection mean {mean_sfx:.2f} / {ge2_pct:.1%}, plant {ratio2:.2f}x, LDA {mean_purity:.3f}")

out = ROOT / "outputs" / "hand_b_internal_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-HAND-B-INTERNAL-01",
    "locked_in_commit": "2b8171b",
    "n_hand_b_folios": len(hand_b_folios),
    "test_1_inflection": {
        "frequent_skeletons": len(frequent_skels),
        "mean_distinct_suffixes": round(mean_sfx, 3),
        "pct_with_ge2": round(ge2_pct, 3),
        "pass": test1_pass,
    },
    "test_2_plant_specificity": {
        "within_plant": round(within_plant, 4),
        "across": round(across, 4),
        "ratio": round(ratio2, 3) if across else None,
        "pass": test2_pass,
    },
    "test_3_lda": {
        "K": K, "per_topic_purity": purities,
        "mean_purity": round(mean_purity, 4),
        "pass": test3_pass,
    },
    "verdict": verdict,
    "passes": passes,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out}")
