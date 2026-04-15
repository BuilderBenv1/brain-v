"""
Vowel-section decoding — first pass.

Strategic pivot: the coverage game is rigged (H-BV-NULL-01). The vowel
layer (H-BV-VOWEL-01) is where the actual signal lives. Goal of this
cycle: figure out WHAT the vowel patterns encode.

Method
------
  1. For every skeleton with chi-square-significant vowel/section coupling
     at p<0.01, extract each (variant, section-distribution) pair.
  2. Normalise each variant's section distribution to a probability vector
     over 8 sections (astronomical, biological, cosmological, herbal,
     pharmaceutical, recipes, text-only, zodiac).
  3. For each variant, identify its MODAL section (the section it occurs
     most in relative to overall baseline).
  4. Examine the vowel patterns of variants by modal-section cluster:
     - Is there a shared vowel at a shared position?
     - Does position-1 'e' correlate with biological?
     - Does position-2 'o' correlate with herbal?
  5. Build a naive Bayes classifier: vowel-pattern -> section. Measure
     accuracy via 5-fold cross-validation on variants.
  6. Emit candidate vowel-coding rules with their empirical support.
"""
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "scripts")

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
VOWELS = set("aoei")
SECTIONS = ["astronomical","biological","cosmological","herbal",
            "pharmaceutical","recipes","text-only","zodiac"]

def split_skel_vowels(word):
    if word and word[0] in "tp" and (len(word) == 1 or word[1] != "h"):
        word = word[1:]
    cons = []
    vowel_slots = []  # list of (position_after_consonant_idx, vowel_char)
    pos = 0  # position after consonants consumed
    i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                cons.append(sy); pos += 1; i += len(ev); matched = True; break
        if not matched:
            if word[i] in VOWELS:
                vowel_slots.append((pos, word[i]))
            i += 1
    # Produce a canonical vowel pattern: string of vowels in positional order,
    # separated by '.' when slots are non-contiguous
    if not vowel_slots:
        return "".join(cons), ""
    # Compress repeated same-position vowels (e.g. 'ee')
    vs = sorted(vowel_slots)
    # Build a slot string: slot k = concatenation of vowels at position k
    by_pos = defaultdict(list)
    for p, v in vs:
        by_pos[p].append(v)
    max_p = max(by_pos)
    parts = []
    for p in range(max_p + 1):
        parts.append("".join(by_pos.get(p, [])) or "_")
    return "".join(cons), ".".join(parts)

# Per-word section counts
word_section = defaultdict(Counter)
section_totals = Counter()
for folio in CORPUS["folios"]:
    sec = folio["section"]
    for line in folio["lines"]:
        for w in line["words"]:
            word_section[w][sec] += 1
            section_totals[sec] += 1

grand_total = sum(section_totals.values())
baseline = {s: section_totals[s] / grand_total for s in SECTIONS}

# Group words by skeleton
by_skel = defaultdict(list)  # skel -> [(word, vowel_pattern, total, sec_counts)]
for w, counts in word_section.items():
    sk, vp = split_skel_vowels(w)
    if not sk: continue
    total = sum(counts.values())
    by_skel[sk].append((w, vp, total, dict(counts)))

# Chi-square + crit as before
def chisq(observed):
    secs = sorted({s for row in observed for s in row.keys()})
    mat = [[row.get(s, 0) for s in secs] for row in observed]
    tr = [sum(r) for r in mat]; tc = [sum(c) for c in zip(*mat)]
    N = sum(tr)
    if N == 0: return 0, 0
    chi = 0.0
    for i in range(len(mat)):
        for j in range(len(secs)):
            e = tr[i]*tc[j]/N
            if e > 0: chi += (mat[i][j]-e)**2/e
    df = (len(mat)-1)*(len(secs)-1)
    return chi, df

CRIT_01 = {1:6.63,2:9.21,3:11.34,4:13.28,5:15.09,6:16.81,7:18.48,8:20.09,
           9:21.67,10:23.21,12:26.22,15:30.58,20:37.57,25:44.31,30:50.89,
           40:63.69,50:76.15}
def crit(df):
    for k in sorted(CRIT_01):
        if df <= k: return CRIT_01[k]
    return df + 2*math.sqrt(2*df)

# Filter to significant skeletons with >=3 variants, >=100 tokens
significant = []
for sk, vs in by_skel.items():
    if len(vs) < 3 or sum(v[2] for v in vs) < 100: continue
    top = sorted(vs, key=lambda x: -x[2])[:5]
    chi, df = chisq([v[3] for v in top])
    if df > 0 and chi > crit(df):
        significant.append((sk, top, chi, df))

print(f"Significant skeleton groups (p<0.01): {len(significant)}")
print(f"Total variants in those groups: "
      f"{sum(len(top) for _, top, _, _ in significant)}")

# =========================================================================
# For each variant, compute section-preference relative to baseline.
# Modal section = argmax_s (prob(variant|s) / baseline(s))
# =========================================================================
variants = []   # (word, skeleton, vowel_pattern, modal_section, enrichment, total)
for sk, top, _, _ in significant:
    for word, vp, total, secs in top:
        if total < 20: continue
        # Observed probability per section
        probs = {s: secs.get(s, 0) / total for s in SECTIONS}
        # Enrichment = prob / baseline
        enr = {s: probs[s] / baseline[s] if baseline[s] > 0 else 0 for s in SECTIONS}
        modal = max(enr, key=enr.get)
        variants.append({
            "word": word, "skel": sk, "vp": vp,
            "modal": modal, "enrichment": enr[modal], "total": total,
            "probs": probs,
        })

print(f"Variants with >=20 tokens: {len(variants)}")

# =========================================================================
# Q1: Do variants with SAME vowel pattern cluster on SAME modal section,
# across different consonant skeletons?
# =========================================================================
print("\n  Q1. Does a vowel pattern predict a section ACROSS skeletons?")
print("  " + "-"*66)

by_vp = defaultdict(list)
for v in variants:
    by_vp[v["vp"]].append(v)

print(f"  {'vowel pattern':<18} {'n':>3} {'modal mode':<16} {'agreement':>10} {'conc modal'}")
patterns_with_agreement = []
for vp, vs in sorted(by_vp.items(), key=lambda x: -len(x[1])):
    if len(vs) < 3: continue
    modals = Counter(v["modal"] for v in vs)
    top_modal, top_n = modals.most_common(1)[0]
    agreement = top_n / len(vs)
    patterns_with_agreement.append((vp, len(vs), top_modal, agreement, modals))
    if agreement >= 0.50:  # interesting
        modals_str = ",".join(f"{k}:{v}" for k, v in modals.most_common(3))
        print(f"  {vp:<18} {len(vs):>3} {top_modal:<16} {agreement:>9.1%} {modals_str}")

# Baseline: expected agreement if random = max(baseline)
max_base = max(baseline.values())
print(f"\n  Random-agreement baseline (dominant section): {max_base:.1%} (herbal)")

# =========================================================================
# Q2: Vowel-at-position -> section correlations
# =========================================================================
print("\n  Q2. Does a specific vowel at a specific slot predict section?")
print("  " + "-"*66)
# For each (slot_index, vowel_char), what modal section do variants
# containing that (slot, char) feature cluster on?
features = defaultdict(Counter)  # (slot, char) -> Counter(modal_section -> n)
for v in variants:
    parts = v["vp"].split(".")
    for slot_i, part in enumerate(parts):
        for ch in part:
            features[(slot_i, ch)][v["modal"]] += 1

print(f"  {'slot':<5} {'vowel':<6} {'n':>4} {'modal mode':<16} {'rate':>8}")
strong_features = []
for (slot, ch), modals in sorted(features.items(),
                                  key=lambda x: -sum(x[1].values())):
    n = sum(modals.values())
    if n < 15: continue
    top_modal, top_n = modals.most_common(1)[0]
    rate = top_n / n
    if rate > max_base + 0.10:  # at least 10pp above random baseline
        strong_features.append(((slot, ch), n, top_modal, rate))
        print(f"  {slot:<5} {ch:<6} {n:>4} {top_modal:<16} {rate:>7.1%}")

# =========================================================================
# Q3: Naive Bayes classifier — vowel pattern -> section
# =========================================================================
print("\n  Q3. Classifier: vowel pattern -> modal section")
print("  " + "-"*66)
# 5-fold CV. Features: (slot, char) tuples. P(sec|features) ~ product.
random.seed(42)
shuffled = variants[:]
random.shuffle(shuffled)
folds = 5
fold_size = len(shuffled) // folds

accuracies = []
majority_accs = []
for f in range(folds):
    test = shuffled[f*fold_size:(f+1)*fold_size]
    train = shuffled[:f*fold_size] + shuffled[(f+1)*fold_size:]
    # Count priors and likelihoods
    prior = Counter(v["modal"] for v in train)
    likelihood = defaultdict(Counter)  # (slot,ch) -> Counter(sec)
    sec_totals = Counter()
    for v in train:
        sec_totals[v["modal"]] += 1
        for slot_i, part in enumerate(v["vp"].split(".")):
            for ch in part:
                likelihood[(slot_i, ch)][v["modal"]] += 1
    alpha = 1.0
    # Predict
    correct = 0
    majority_correct = 0
    majority_sec = prior.most_common(1)[0][0]
    for v in test:
        best_sec = None; best_log = -1e9
        for sec in SECTIONS:
            if sec_totals[sec] == 0: continue
            lp = math.log((prior[sec] + alpha) / (sum(prior.values()) + alpha*len(SECTIONS)))
            for slot_i, part in enumerate(v["vp"].split(".")):
                for ch in part:
                    c = likelihood[(slot_i, ch)][sec]
                    lp += math.log((c + alpha) / (sec_totals[sec] + alpha * 20))
            if lp > best_log:
                best_log = lp; best_sec = sec
        if best_sec == v["modal"]: correct += 1
        if majority_sec == v["modal"]: majority_correct += 1
    acc = correct / len(test) if test else 0
    majority_acc = majority_correct / len(test) if test else 0
    accuracies.append(acc); majority_accs.append(majority_acc)

import statistics
mean_acc = statistics.mean(accuracies)
mean_maj = statistics.mean(majority_accs)
print(f"  5-fold CV accuracy:        {mean_acc:.1%}  (chance floor = {1/len(SECTIONS):.1%})")
print(f"  Majority-class baseline:   {mean_maj:.1%}")
print(f"  Gain over majority:        {(mean_acc - mean_maj)*100:+.1f}pp")
if mean_acc > mean_maj + 0.05:
    print("  -> vowel pattern carries predictive information for section")
elif mean_acc > mean_maj + 0.01:
    print("  -> weak signal, borderline")
else:
    print("  -> no signal over majority")

# =========================================================================
# Q4: For the headline skeleton 'kdy', can we predict which section each
# variant serves just from its vowel pattern?
# =========================================================================
print("\n  Q4. Case study: skeleton 'kdy' internal consistency")
print("  " + "-"*66)
kdy_vs = [v for v in variants if v["skel"] == "kdy"]
kdy_vs.sort(key=lambda v: -v["total"])
for v in kdy_vs[:6]:
    top3 = sorted(v["probs"].items(), key=lambda x: -x[1])[:3]
    t3s = ", ".join(f"{s}={p:.0%}" for s, p in top3)
    print(f"  {v['word']:<10} vp={v['vp']:<10} n={v['total']:>4}  "
          f"modal={v['modal']:<14} enr={v['enrichment']:.2f}x  [{t3s}]")

# =========================================================================
# Save findings summary
# =========================================================================
findings = {
    "generated": "2026-04-15",
    "cycle": "vowel_decode_v1",
    "skeletons_significant": len(significant),
    "variants_analyzed": len(variants),
    "patterns_with_section_agreement": [
        {"pattern": vp, "n_skeletons": n, "top_modal_section": tm,
         "agreement": round(ag, 3)}
        for vp, n, tm, ag, _ in sorted(patterns_with_agreement,
                                       key=lambda x: -x[3])[:15]
    ],
    "strong_slot_features": [
        {"slot": s, "vowel": c, "n": n, "modal": m, "rate": round(r, 3)}
        for (s, c), n, m, r in sorted(strong_features, key=lambda x: -x[3])[:15]
    ],
    "classifier": {
        "cv_folds": folds,
        "mean_accuracy": round(mean_acc, 3),
        "majority_baseline": round(mean_maj, 3),
        "gain_over_majority_pp": round((mean_acc - mean_maj) * 100, 2),
        "sections": SECTIONS,
    },
    "case_kdy": [
        {"word": v["word"], "vp": v["vp"], "total": v["total"],
         "modal": v["modal"], "enrichment": round(v["enrichment"], 2)}
        for v in kdy_vs[:6]
    ],
}
out = ROOT / "outputs" / "vowel_decode_v1.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(findings, indent=2, ensure_ascii=False),
               encoding="utf-8")
print(f"\nSaved: {out}")

# Also sync into dashboard data for immediate surfacing
dash = ROOT / "dashboard" / "data" / "vowel-decode.json"
dash.write_text(json.dumps(findings, indent=2, ensure_ascii=False),
                encoding="utf-8")
print(f"Synced: {dash}")
