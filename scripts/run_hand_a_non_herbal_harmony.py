"""Execute pre-registered H-BV-HAND-A-NON-HERBAL-HARMONY-01."""
import json
import random
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


def get_folio_words(folio):
    return [w for line in folio["lines"] for w in line["words"] if w]


def harmony_test(folios, label):
    words = []
    for f in folios:
        words.extend(get_folio_words(f))
    tokenised = [tokenize(w) for w in words]
    valid = [t for t in tokenised if len(t) >= 3]
    print(f"\n--- {label} ---")
    print(f"  Folios: {len(folios)}, Tokens: {len(words)}, N>=3 tokens: {len(valid)}")

    stem_inner = defaultdict(Counter)
    for t in valid:
        s = tuple(t[:-2]); inn = t[-2]
        if inn in VOWEL_INNERS:
            stem_inner[s][inn] += 1

    eligible = {s: c for s, c in stem_inner.items() if len(c) >= 3 and sum(c.values()) >= 5}
    n_e = len(eligible)
    print(f"  Eligible stems: {n_e}")
    if n_e < 4:
        print(f"  -> too few stems for k=2 clustering")
        return {"label": label, "n_eligible": n_e, "silhouette": None, "accuracy": None,
                "verdict": "INSUFFICIENT_DATA"}

    stems_list = list(eligible.keys())
    X = np.zeros((n_e, 4))
    for i, stem in enumerate(stems_list):
        ctr = eligible[stem]; total = sum(ctr.values())
        for j, v in enumerate(VOWEL_INNERS):
            X[i, j] = ctr.get(v, 0) / total
    km = KMeans(n_clusters=2, n_init=50, random_state=42)
    labels = km.fit_predict(X)
    centers = km.cluster_centers_
    sil = silhouette_score(X, labels) if len(set(labels)) == 2 else float("nan")
    print(f"  Silhouette: {sil:.4f}")
    fs0 = centers[0,0] + centers[0,1]; fs1 = centers[1,0] + centers[1,1]
    cluster_label = ({0:"FRONT",1:"BACK"} if fs0 > fs1 else {0:"BACK",1:"FRONT"})

    correct = 0; total_eval = 0; skipped = 0
    for i, stem in enumerate(stems_list):
        nf = sum(1 for g in stem if g in FRONT)
        nb = sum(1 for g in stem if g in BACK)
        if nf == nb:
            skipped += 1; continue
        predicted = "FRONT" if nf > nb else "BACK"
        actual = cluster_label[labels[i]]
        total_eval += 1
        if predicted == actual: correct += 1
    accuracy = correct/total_eval if total_eval > 0 else 0
    print(f"  Accuracy: {accuracy:.4f}  ({correct}/{total_eval}, {skipped} skipped)")

    if sil >= 0.50 and accuracy >= 0.65:
        v = "CONFIRMED"
    elif 0.35 <= sil < 0.50 or (sil >= 0.50 and accuracy < 0.65):
        v = "PARTIAL"
    elif sil < 0.35:
        v = "REFUTED"
    else:
        v = "INDETERMINATE"
    if n_e < 30:
        v += "_LOW_POWER"
    print(f"  Verdict: {v}")

    return {"label": label, "n_folios": len(folios), "n_tokens": len(words),
            "n_eligible_stems": n_e,
            "silhouette": round(float(sil), 4) if not np.isnan(sil) else None,
            "accuracy": round(accuracy, 4),
            "cluster_0_centre": [round(float(c),3) for c in centers[0]],
            "cluster_1_centre": [round(float(c),3) for c in centers[1]],
            "verdict": v}


def bootstrap_silhouette(folios, n_boot=200, seed=42):
    random.seed(seed)
    n = len(folios)
    sils = []
    for _ in range(n_boot):
        sampled = [folios[random.randrange(n)] for _ in range(n)]
        words = []
        for f in sampled:
            words.extend(get_folio_words(f))
        tokenised = [tokenize(w) for w in words]
        valid = [t for t in tokenised if len(t) >= 3]
        stem_inner = defaultdict(Counter)
        for t in valid:
            s = tuple(t[:-2]); inn = t[-2]
            if inn in VOWEL_INNERS: stem_inner[s][inn] += 1
        eligible = {s: c for s, c in stem_inner.items() if len(c) >= 3 and sum(c.values()) >= 5}
        if len(eligible) < 4:
            continue
        stems_list = list(eligible.keys())
        X = np.zeros((len(eligible), 4))
        for i, stem in enumerate(stems_list):
            ctr = eligible[stem]; total = sum(ctr.values())
            for j, v in enumerate(VOWEL_INNERS):
                X[i, j] = ctr.get(v, 0) / total
        km = KMeans(n_clusters=2, n_init=20, random_state=42)
        labels = km.fit_predict(X)
        if len(set(labels)) == 2:
            sils.append(silhouette_score(X, labels))
    if sils:
        sils.sort()
        return round(sils[int(0.025*len(sils))], 4), round(sils[int(0.975*len(sils))], 4), len(sils)
    return None, None, 0


hand_a_folios = [f for f in CORPUS["folios"] if f.get("currier_language") == "A"]
non_herbal = [f for f in hand_a_folios if f.get("section") in {"pharmaceutical","recipes","text-only"}]
herbal = [f for f in hand_a_folios if f.get("section") == "herbal"]

print(f"Hand A folios total: {len(hand_a_folios)}")
print(f"  Non-herbal (pharma+recipes+text): {len(non_herbal)}")
print(f"  Herbal: {len(herbal)}")

result_nh = harmony_test(non_herbal, "Hand A NON-HERBAL")
result_h = harmony_test(herbal, "Hand A HERBAL (control)")

print(f"\n--- BOOTSTRAP 95% CI on silhouette (200 resamples) ---")
nh_lo, nh_hi, nh_n = bootstrap_silhouette(non_herbal)
h_lo, h_hi, h_n = bootstrap_silhouette(herbal)
print(f"  Non-herbal silhouette 95% CI: [{nh_lo}, {nh_hi}]  (n_boot={nh_n})")
print(f"  Herbal silhouette 95% CI:     [{h_lo}, {h_hi}]  (n_boot={h_n})")

print(f"\n--- COMPARISON SUMMARY ---")
print(f"  Hand A all       silhouette 0.3305  REFUTED  (from H-BV-VOWEL-HARMONY-01)")
print(f"  Hand A non-herbal silhouette {result_nh['silhouette']}  {result_nh['verdict']}")
print(f"  Hand A herbal     silhouette {result_h['silhouette']}  {result_h['verdict']}")
print(f"  Hand B all       silhouette 0.6495  CONFIRMED  (from H-BV-HAND-B-VOWEL-HARMONY-01)")

# Final verdict per locked rule
nh_sil = result_nh["silhouette"] or 0
nh_acc = result_nh["accuracy"] or 0
if nh_sil >= 0.50 and nh_acc >= 0.65:
    final = "CONFIRMED_SAMPLE_COMPOSITION_MASKING"
elif 0.35 <= nh_sil < 0.50 or (nh_sil >= 0.50 and nh_acc < 0.65):
    final = "PARTIAL"
elif nh_sil < 0.35:
    final = "REFUTED_SAMPLE_COMPOSITION_HYPOTHESIS"
else:
    final = "INSUFFICIENT_DATA"
print(f"\n  FINAL VERDICT: {final}")

out = {"generated":"2026-04-18","hypothesis":"H-BV-HAND-A-NON-HERBAL-HARMONY-01",
       "hand_a_folios": len(hand_a_folios),
       "non_herbal_subset": result_nh, "herbal_control": result_h,
       "non_herbal_silhouette_95_ci": [nh_lo, nh_hi],
       "herbal_silhouette_95_ci": [h_lo, h_hi],
       "hand_a_all_reference": "silhouette 0.3305 REFUTED",
       "hand_b_all_reference": "silhouette 0.6495 CONFIRMED",
       "final_verdict": final}
out_path = ROOT / "outputs" / "hand_a_non_herbal_harmony_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
