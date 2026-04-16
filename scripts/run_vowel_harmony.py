"""
Execute pre-registered H-BV-VOWEL-HARMONY-01.

Cluster Hand-A stems by their vowel-inner attachment distribution over
{i, e, o, a}, then test whether stem-internal vowels predict cluster
membership (the signature of Turkic/Finno-Ugric vowel harmony).

Locked decision rule:
  CONFIRMED harmony:   silhouette >= 0.50 AND accuracy >= 0.70
  CONFIRMED two-class: silhouette >= 0.50 AND accuracy < 0.70
  REFUTED:             silhouette < 0.35
  MARGINAL:            in-between
  LOW-POWER flag if <50 eligible stems
"""
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

BASE_MULTI = ["ckh", "cth", "cph", "ch", "sh"]
EXTRA = ["ol"]
MULTI = sorted(BASE_MULTI + EXTRA, key=lambda s: -len(s))

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

VOWEL_INNERS = ["i", "e", "o", "a"]
FRONT = {"i", "e"}
BACK = {"o", "a"}

# Build Hand A tokens
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

tokenised = [tokenize(w) for w in hand_a_words]
valid = [t for t in tokenised if len(t) >= 3]
n_valid = len(valid)
print(f"Hand A tokens with >=3 glyph-units: {n_valid}")

# =============================================================================
# STEP 1 — Eligible stems
# =============================================================================
stem_inner_counts = defaultdict(Counter)  # stem -> Counter over vowel inners
for t in valid:
    stem = tuple(t[:-2])
    inner = t[-2]
    if inner in VOWEL_INNERS:
        stem_inner_counts[stem][inner] += 1

eligible = {}
for stem, ctr in stem_inner_counts.items():
    distinct = len(ctr)
    total = sum(ctr.values())
    if distinct >= 3 and total >= 5:
        eligible[stem] = ctr

n_eligible = len(eligible)
print(f"Eligible stems (>=3 distinct vowel-inners AND >=5 total): {n_eligible}")
low_power = n_eligible < 50
if low_power:
    print("  *** LOW-POWER flag raised (< 50 eligible stems) ***")

# =============================================================================
# STEP 2 — Feature vectors
# =============================================================================
stems_list = list(eligible.keys())
X = np.zeros((n_eligible, 4))
for idx, stem in enumerate(stems_list):
    ctr = eligible[stem]
    total = sum(ctr.values())
    for j, v in enumerate(VOWEL_INNERS):
        X[idx, j] = ctr.get(v, 0) / total

print(f"\nFeature matrix shape: {X.shape}  (columns: {VOWEL_INNERS})")
print(f"Column means (global vowel-inner distribution across eligible stems):")
print(f"  i={X[:,0].mean():.3f}  e={X[:,1].mean():.3f}  o={X[:,2].mean():.3f}  a={X[:,3].mean():.3f}")

# =============================================================================
# STEP 3 — K-means clustering
# =============================================================================
km = KMeans(n_clusters=2, n_init=50, random_state=42)
labels = km.fit_predict(X)
centers = km.cluster_centers_
sil = silhouette_score(X, labels) if n_eligible >= 2 and len(set(labels)) == 2 else float("nan")
print(f"\nK-means k=2 (50 restarts):")
print(f"  Cluster 0 size: {(labels == 0).sum()};  Cluster 1 size: {(labels == 1).sum()}")
print(f"  Cluster 0 centre: i={centers[0,0]:.3f} e={centers[0,1]:.3f} o={centers[0,2]:.3f} a={centers[0,3]:.3f}")
print(f"  Cluster 1 centre: i={centers[1,0]:.3f} e={centers[1,1]:.3f} o={centers[1,2]:.3f} a={centers[1,3]:.3f}")
print(f"  Silhouette score: {sil:.4f}")

# =============================================================================
# STEP 4 — Front/Back labelling
# =============================================================================
front_score_c0 = centers[0, 0] + centers[0, 1]  # p(i) + p(e)
front_score_c1 = centers[1, 0] + centers[1, 1]
if front_score_c0 > front_score_c1:
    cluster_label = {0: "FRONT", 1: "BACK"}
else:
    cluster_label = {0: "BACK", 1: "FRONT"}
print(f"\nLabelling by mean p(i)+p(e):")
print(f"  Cluster 0 front-score {front_score_c0:.3f} -> {cluster_label[0]}")
print(f"  Cluster 1 front-score {front_score_c1:.3f} -> {cluster_label[1]}")

# =============================================================================
# STEP 5 — Stem-internal vowel prediction
# =============================================================================
correct = 0
skipped = 0
total_eval = 0
prediction_breakdown = Counter()
for idx, stem in enumerate(stems_list):
    n_front_inside = sum(1 for g in stem if g in FRONT)
    n_back_inside = sum(1 for g in stem if g in BACK)
    if n_front_inside == n_back_inside:
        skipped += 1
        prediction_breakdown["skip"] += 1
        continue
    predicted = "FRONT" if n_front_inside > n_back_inside else "BACK"
    actual = cluster_label[labels[idx]]
    total_eval += 1
    if predicted == actual:
        correct += 1
        prediction_breakdown[f"correct_{predicted}"] += 1
    else:
        prediction_breakdown[f"wrong_{predicted}_actual_{actual}"] += 1

accuracy = correct / total_eval if total_eval > 0 else 0.0
print(f"\nStem-internal vowel prediction:")
print(f"  Evaluated stems: {total_eval}  (skipped tied/zero: {skipped})")
print(f"  Correct: {correct}")
print(f"  Accuracy: {accuracy:.4f}")
print(f"  Breakdown: {dict(prediction_breakdown)}")

# =============================================================================
# LOCKED DECISION
# =============================================================================
print("\n" + "="*78)
print("  LOCKED DECISION")
print("="*78)
print(f"  silhouette = {sil:.4f}")
print(f"  accuracy   = {accuracy:.4f}")
print(f"  low-power  = {low_power}")

if sil >= 0.50 and accuracy >= 0.70:
    verdict = "CONFIRMED_VOWEL_HARMONY"
    rationale = f"silhouette={sil:.3f} >= 0.50 AND accuracy={accuracy:.3f} >= 0.70; matches Turkic/Finno-Ugric pattern"
elif sil >= 0.50 and accuracy < 0.70:
    verdict = "CONFIRMED_TWO_CLASS_NOT_HARMONIC"
    rationale = f"silhouette={sil:.3f} >= 0.50 but accuracy={accuracy:.3f} < 0.70; two vowel-preference classes exist but stem-internal vowels do not drive them"
elif sil < 0.35:
    verdict = "REFUTED"
    rationale = f"silhouette={sil:.3f} < 0.35; no meaningful clustering, n/r/l vs y/ol split is NOT vowel-harmony driven"
else:
    verdict = "MARGINAL"
    rationale = f"silhouette={sil:.3f} in [0.35, 0.50) or silhouette>=0.50 with accuracy in [0.60, 0.70); in-between zone"

print(f"\n  VERDICT: {verdict}")
print(f"  {rationale}")
if low_power:
    print(f"  *** LOW-POWER caveat: only {n_eligible} eligible stems ***")

# =============================================================================
# Additional diagnostics (do not feed decision rule — reporting only)
# =============================================================================
print("\n" + "-"*78)
print("  Additional diagnostics (non-decision-feeding)")
print("-"*78)

# Per-cluster exemplar stems
for c in [0, 1]:
    lbl = cluster_label[c]
    members = [stems_list[i] for i in range(n_eligible) if labels[i] == c]
    # Sort by most extreme front/back preference
    def extremeness(stem):
        ctr = eligible[stem]
        total = sum(ctr.values())
        p_front = (ctr.get("i", 0) + ctr.get("e", 0)) / total
        p_back = (ctr.get("o", 0) + ctr.get("a", 0)) / total
        return p_front if lbl == "FRONT" else p_back
    members.sort(key=extremeness, reverse=True)
    print(f"\n  Cluster {c} ({lbl}): {len(members)} stems. Top-8 exemplars:")
    for stem in members[:8]:
        ctr = eligible[stem]
        total = sum(ctr.values())
        stem_str = "".join(stem) if stem else "(empty)"
        dist = {v: ctr.get(v, 0) for v in VOWEL_INNERS}
        n_front_inside = sum(1 for g in stem if g in FRONT)
        n_back_inside = sum(1 for g in stem if g in BACK)
        print(f"    {stem_str:<12} total={total:<3} dist={dist}  inside: F={n_front_inside} B={n_back_inside}")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "vowel_harmony_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-VOWEL-HARMONY-01",
    "tokenisation": "A (MULTI_GLYPHS + 'ol')",
    "n_hand_a_valid_tokens": n_valid,
    "n_eligible_stems": n_eligible,
    "low_power_flag": low_power,
    "kmeans": {
        "k": 2,
        "n_init": 50,
        "random_state": 42,
        "cluster_0_size": int((labels == 0).sum()),
        "cluster_1_size": int((labels == 1).sum()),
        "cluster_0_centre": [round(float(x), 4) for x in centers[0]],
        "cluster_1_centre": [round(float(x), 4) for x in centers[1]],
        "cluster_0_label": cluster_label[0],
        "cluster_1_label": cluster_label[1],
    },
    "silhouette_score": round(float(sil), 4),
    "stem_internal_prediction": {
        "evaluated_stems": total_eval,
        "skipped_ties_or_zero": skipped,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "breakdown": dict(prediction_breakdown),
    },
    "verdict": verdict,
    "rationale": rationale,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
