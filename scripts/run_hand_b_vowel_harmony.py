"""Execute pre-registered H-BV-HAND-B-VOWEL-HARMONY-01."""
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI = sorted(["ckh","cth","cph","ch","sh","ol"], key=lambda s: -len(s))
VOWEL_INNERS = ["i","e","o","a"]
FRONT = {"i","e"}; BACK = {"o","a"}


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


hand_b_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") == "B":
        for line in f["lines"]:
            hand_b_words.extend(line["words"])
tokenised = [tokenize(w) for w in hand_b_words]
valid = [t for t in tokenised if len(t) >= 3]
print(f"Hand B N>=3 tokens: {len(valid)}")

stem_inner_counts = defaultdict(Counter)
for t in valid:
    stem = tuple(t[:-2]); inner = t[-2]
    if inner in VOWEL_INNERS:
        stem_inner_counts[stem][inner] += 1

eligible = {}
for stem, ctr in stem_inner_counts.items():
    if len(ctr) >= 3 and sum(ctr.values()) >= 5:
        eligible[stem] = ctr

n_eligible = len(eligible)
print(f"Eligible stems (>=3 distinct, >=5 total): {n_eligible}")
low_power = n_eligible < 50
if low_power:
    print(f"  *** LOW-POWER (<50) ***")

stems_list = list(eligible.keys())
X = np.zeros((n_eligible, 4))
for idx, stem in enumerate(stems_list):
    ctr = eligible[stem]
    total = sum(ctr.values())
    for j, v in enumerate(VOWEL_INNERS):
        X[idx, j] = ctr.get(v, 0) / total

print(f"Column means: i={X[:,0].mean():.3f} e={X[:,1].mean():.3f} o={X[:,2].mean():.3f} a={X[:,3].mean():.3f}")

km = KMeans(n_clusters=2, n_init=50, random_state=42)
labels = km.fit_predict(X)
centers = km.cluster_centers_
sil = silhouette_score(X, labels) if n_eligible >= 2 and len(set(labels)) == 2 else float("nan")
print(f"\nK-means k=2:")
print(f"  Cluster 0 size: {(labels==0).sum()}; Cluster 1 size: {(labels==1).sum()}")
print(f"  Cluster 0 centre: i={centers[0,0]:.3f} e={centers[0,1]:.3f} o={centers[0,2]:.3f} a={centers[0,3]:.3f}")
print(f"  Cluster 1 centre: i={centers[1,0]:.3f} e={centers[1,1]:.3f} o={centers[1,2]:.3f} a={centers[1,3]:.3f}")
print(f"  Silhouette: {sil:.4f}")

front_score_c0 = centers[0,0] + centers[0,1]
front_score_c1 = centers[1,0] + centers[1,1]
cluster_label = ({0:"FRONT",1:"BACK"} if front_score_c0 > front_score_c1 else {0:"BACK",1:"FRONT"})

correct = 0; skipped = 0; total_eval = 0
for idx, stem in enumerate(stems_list):
    nf = sum(1 for g in stem if g in FRONT)
    nb = sum(1 for g in stem if g in BACK)
    if nf == nb:
        skipped += 1; continue
    predicted = "FRONT" if nf > nb else "BACK"
    actual = cluster_label[labels[idx]]
    total_eval += 1
    if predicted == actual:
        correct += 1
accuracy = correct/total_eval if total_eval > 0 else 0
print(f"\nStem-internal vowel prediction:")
print(f"  Eval: {total_eval}, Skipped: {skipped}, Correct: {correct}, Accuracy: {accuracy:.4f}")

if sil >= 0.50 and accuracy >= 0.70: verdict = "CONFIRMED_HARMONY"
elif sil >= 0.50 and accuracy < 0.70: verdict = "CONFIRMED_TWO_CLASS_NON_HARMONIC"
elif sil < 0.35: verdict = "REFUTED"
elif sil >= 0.35 and sil < 0.50: verdict = "MARGINAL"
elif sil >= 0.50 and 0.60 <= accuracy < 0.70: verdict = "MARGINAL"
else: verdict = "MARGINAL"

print(f"\n  VERDICT: {verdict}{' (LOW-POWER)' if low_power else ''}")
print(f"  HAND A reference: REFUTED at silhouette 0.3305 / accuracy not relevant (n=73 stems)")

out = {"generated":"2026-04-18","hypothesis":"H-BV-HAND-B-VOWEL-HARMONY-01",
       "n_eligible_stems": n_eligible, "low_power_flag": low_power,
       "silhouette": round(float(sil),4),
       "cluster_0_centre": [round(float(c),3) for c in centers[0]],
       "cluster_1_centre": [round(float(c),3) for c in centers[1]],
       "cluster_0_label": cluster_label[0], "cluster_1_label": cluster_label[1],
       "prediction_eval": total_eval, "prediction_correct": correct,
       "prediction_accuracy": round(accuracy,4),
       "verdict": verdict,
       "hand_a_reference": "REFUTED at silhouette 0.3305"}
out_path = ROOT / "outputs" / "hand_b_vowel_harmony_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
