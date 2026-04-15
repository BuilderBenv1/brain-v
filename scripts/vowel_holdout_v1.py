"""
Held-out validation for H-BV-VOWEL-CODE-01.

Training set: ALL folios EXCEPT the 4 held-out ones.
Held-out:
  Pharma:  f101r (226 tokens), f89r2 (233 tokens)
  Biology: f78r  (293 tokens), f82r  (285 tokens)

These four folios contribute zero tokens to:
  - the skeleton-significance test,
  - the vowel-pattern -> section rule discovery,
  - the classifier training.

For every word on the held-out folios we then:
  1. Extract (skeleton, vowel_pattern)
  2. Predict section from vowel pattern alone (rules + NB classifier)
  3. Score precision/recall/F1 for the ground-truth section label.

No lexicon, no language assumption. Pure structural prediction.
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

HELDOUT = {"f101r", "f89r2", "f78r", "f82r"}

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
    cons = []; vowel_slots = []
    pos = 0; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                cons.append(sy); pos += 1; i += len(ev); matched = True; break
        if not matched:
            if word[i] in VOWELS:
                vowel_slots.append((pos, word[i]))
            i += 1
    if not vowel_slots:
        return "".join(cons), ""
    by_pos = defaultdict(list)
    for p, v in vowel_slots: by_pos[p].append(v)
    max_p = max(by_pos)
    return "".join(cons), ".".join("".join(by_pos.get(p, [])) or "_"
                                    for p in range(max_p + 1))

# =========================================================================
# 1. Partition corpus into train / holdout
# =========================================================================
train_word_section = defaultdict(Counter)
train_section_totals = Counter()
holdout_words = []  # (word, true_section, folio)

for folio in CORPUS["folios"]:
    fid = folio["folio"]; sec = folio["section"]
    is_heldout = fid in HELDOUT
    for line in folio["lines"]:
        for w in line["words"]:
            if is_heldout:
                holdout_words.append((w, sec, fid))
            else:
                train_word_section[w][sec] += 1
                train_section_totals[sec] += 1

held_by_folio = Counter(fid for _, _, fid in holdout_words)
print("Held-out tokens per folio:")
for fid, n in sorted(held_by_folio.items()):
    sec = next(s for w, s, f in holdout_words if f == fid)
    print(f"  {fid:<8} {sec:<15} {n:>4} tokens")
print(f"  Total held-out: {len(holdout_words)} tokens")

train_grand = sum(train_section_totals.values())
train_baseline = {s: train_section_totals[s] / train_grand for s in SECTIONS}

# =========================================================================
# 2. Re-derive vowel-pattern -> section rules from TRAIN only
# =========================================================================
by_skel = defaultdict(list)
for w, counts in train_word_section.items():
    sk, vp = split_skel_vowels(w)
    if not sk: continue
    by_skel[sk].append((w, vp, sum(counts.values()), dict(counts)))

def chisq(observed):
    secs = sorted({s for r in observed for s in r.keys()})
    mat = [[r.get(s, 0) for s in secs] for r in observed]
    tr = [sum(r) for r in mat]; tc = [sum(c) for c in zip(*mat)]
    N = sum(tr)
    if N == 0: return 0, 0
    chi = 0.0
    for i in range(len(mat)):
        for j in range(len(secs)):
            e = tr[i]*tc[j]/N
            if e > 0: chi += (mat[i][j]-e)**2/e
    return chi, (len(mat)-1)*(len(secs)-1)

CRIT_01 = {1:6.63,2:9.21,3:11.34,4:13.28,5:15.09,6:16.81,7:18.48,8:20.09,
           9:21.67,10:23.21,12:26.22,15:30.58,20:37.57,25:44.31,30:50.89,
           40:63.69,50:76.15}
def crit(df):
    for k in sorted(CRIT_01):
        if df <= k: return CRIT_01[k]
    return df + 2*math.sqrt(2*df)

sig = []
for sk, vs in by_skel.items():
    if len(vs) < 3 or sum(v[2] for v in vs) < 100: continue
    top = sorted(vs, key=lambda x: -x[2])[:5]
    chi, df = chisq([v[3] for v in top])
    if df > 0 and chi > crit(df):
        sig.append((sk, top))

# Training variants and their modal sections
train_variants = []
for sk, top in sig:
    for w, vp, tot, secs in top:
        if tot < 20: continue
        probs = {s: secs.get(s,0)/tot for s in SECTIONS}
        enr = {s: probs[s]/train_baseline[s] if train_baseline[s] > 0 else 0
               for s in SECTIONS}
        modal = max(enr, key=enr.get)
        train_variants.append({"skel": sk, "vp": vp, "modal": modal,
                               "total": tot, "enr": enr[modal]})

# Rules: vowel_pattern -> most-common modal across training skeletons
rule_map = defaultdict(Counter)
for v in train_variants:
    rule_map[v["vp"]][v["modal"]] += 1

rules = {}
for vp, modals in rule_map.items():
    n = sum(modals.values())
    if n < 3: continue
    top_sec, top_n = modals.most_common(1)[0]
    agreement = top_n / n
    if agreement >= 0.50:
        rules[vp] = (top_sec, agreement, n)

print(f"\nTraining rules (>=3 skeletons, >=50% agreement): {len(rules)}")
for vp, (sec, ag, n) in sorted(rules.items(), key=lambda x: -x[1][2])[:10]:
    print(f"  {vp:<14} -> {sec:<15} agreement={ag:.0%} n={n}")

# =========================================================================
# 3. Train naive-Bayes classifier on train variants
# =========================================================================
prior = Counter(v["modal"] for v in train_variants)
sec_totals = Counter(v["modal"] for v in train_variants)
likelihood = defaultdict(Counter)
for v in train_variants:
    for slot_i, part in enumerate(v["vp"].split(".")):
        for ch in part:
            likelihood[(slot_i, ch)][v["modal"]] += 1

alpha = 1.0
N_prior = sum(prior.values())

def nb_predict(vp):
    best = None; best_lp = -1e18
    for sec in SECTIONS:
        if sec_totals[sec] == 0: continue
        lp = math.log((prior[sec] + alpha) / (N_prior + alpha*len(SECTIONS)))
        for slot_i, part in enumerate(vp.split(".")):
            for ch in part:
                c = likelihood[(slot_i, ch)][sec]
                lp += math.log((c + alpha) / (sec_totals[sec] + alpha * 20))
        if lp > best_lp: best_lp = lp; best = sec
    return best

# Majority class for rule fallback
majority = prior.most_common(1)[0][0]

def rule_predict(vp):
    """Return rule-based prediction, or None if no rule applies."""
    if vp in rules:
        return rules[vp][0]
    return None

# =========================================================================
# 4. Predict held-out tokens
# =========================================================================
def evaluate(target_section, method):
    """Compute precision/recall/F1 for predicting `target_section`."""
    tp = fp = fn = tn = 0
    covered = 0  # for rule method, how many tokens had an applicable rule
    for w, true_sec, fid in holdout_words:
        sk, vp = split_skel_vowels(w)
        if method == "rule":
            pred = rule_predict(vp)
            if pred is None:
                pred = majority
            else:
                covered += 1
        else:  # nb
            pred = nb_predict(vp)
            covered += 1
        is_target = (pred == target_section)
        is_truth  = (true_sec == target_section)
        if is_target and is_truth: tp += 1
        elif is_target and not is_truth: fp += 1
        elif not is_target and is_truth: fn += 1
        else: tn += 1
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec  = tp / (tp + fn) if (tp + fn) else 0.0
    f1   = 2*prec*rec / (prec + rec) if (prec + rec) else 0.0
    return dict(tp=tp, fp=fp, fn=fn, tn=tn,
                precision=prec, recall=rec, f1=f1,
                coverage=covered/len(holdout_words))

# Baseline: random chance that a prediction lands on target_section
def random_baseline(target_section):
    # Random prediction weighted by train prior -> expected precision = prior(target)
    # Predict ALL as target -> recall=1, precision = prevalence in holdout
    holdout_prev = sum(1 for _, s, _ in holdout_words if s == target_section) / len(holdout_words)
    return holdout_prev

def always_predict_target(target_section):
    """Baseline: predict target for every held-out token."""
    tp = fp = fn = 0
    for w, true_sec, fid in holdout_words:
        is_truth = (true_sec == target_section)
        if is_truth: tp += 1
        else: fp += 1
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec  = 1.0 if tp > 0 else 0.0
    f1   = 2*prec*rec / (prec + rec) if (prec + rec) else 0.0
    return dict(precision=prec, recall=rec, f1=f1)

print("\n" + "="*72)
print("  HELD-OUT VALIDATION — H-BV-VOWEL-CODE-01")
print("="*72)
for target in ("pharmaceutical", "biological"):
    print(f"\n  Target section: {target}")
    print("  " + "-"*66)
    rule_r = evaluate(target, "rule")
    nb_r   = evaluate(target, "nb")
    blind  = always_predict_target(target)
    prev   = random_baseline(target)

    print(f"  Held-out prevalence of '{target}': {prev:.1%}")
    print(f"  {'method':<20} {'prec':>8} {'recall':>8} {'F1':>8} {'cov':>8}")
    print(f"  {'always-predict-target':<20} {blind['precision']:>8.3f} "
          f"{blind['recall']:>8.3f} {blind['f1']:>8.3f} {'100%':>8}")
    print(f"  {'vowel-rule table':<20} {rule_r['precision']:>8.3f} "
          f"{rule_r['recall']:>8.3f} {rule_r['f1']:>8.3f} "
          f"{rule_r['coverage']:>7.1%}")
    print(f"  {'naive-Bayes (vowels)':<20} {nb_r['precision']:>8.3f} "
          f"{nb_r['recall']:>8.3f} {nb_r['f1']:>8.3f} "
          f"{nb_r['coverage']:>7.1%}")

    # Verdict
    best = max(rule_r["f1"], nb_r["f1"])
    if best > blind["f1"] + 0.05:
        print(f"  -> signal SURVIVES holdout: best F1 {best:.3f} > blind F1 {blind['f1']:.3f} by >=5pp")
    elif best > blind["f1"]:
        print(f"  -> signal WEAK: best F1 {best:.3f} > blind F1 {blind['f1']:.3f} by <5pp")
    else:
        print(f"  -> signal DIES: best F1 {best:.3f} <= blind F1 {blind['f1']:.3f}")

# =========================================================================
# 5. Per-folio detail for transparency
# =========================================================================
print("\n" + "="*72)
print("  PER-FOLIO NB PREDICTION DISTRIBUTION")
print("="*72)
by_folio = defaultdict(list)
for w, true_sec, fid in holdout_words:
    _, vp = split_skel_vowels(w)
    by_folio[fid].append((w, vp, true_sec, nb_predict(vp)))

for fid in sorted(by_folio):
    preds = [p for _, _, _, p in by_folio[fid]]
    true_sec = by_folio[fid][0][2]
    pred_counts = Counter(preds)
    top3 = pred_counts.most_common(3)
    n = len(preds)
    hit = pred_counts[true_sec] / n
    print(f"  {fid:<8} true={true_sec:<15} n={n:>4}  "
          f"hit-rate={hit:.1%}  top: {top3}")

# =========================================================================
# 6. Multi-class accuracy (NOT just one target)
# =========================================================================
print("\n" + "="*72)
print("  MULTI-CLASS EXACT-MATCH ACCURACY")
print("="*72)
total = 0; correct_rule = 0; correct_nb = 0; rule_covered = 0
for w, true_sec, fid in holdout_words:
    _, vp = split_skel_vowels(w)
    rp = rule_predict(vp); np = nb_predict(vp)
    total += 1
    if rp is not None:
        rule_covered += 1
        if rp == true_sec: correct_rule += 1
    if np == true_sec: correct_nb += 1

majority_truth_rate = sum(1 for _, s, _ in holdout_words
                          if s == majority) / total
print(f"  Majority class on holdout: {majority} "
      f"(rate {majority_truth_rate:.1%})")
print(f"  Rule table: {correct_rule}/{rule_covered} = "
      f"{correct_rule/rule_covered:.1%}  (coverage {rule_covered/total:.1%})")
print(f"  Naive Bayes: {correct_nb}/{total} = {correct_nb/total:.1%}")

# Save
out = ROOT / "outputs" / "vowel_holdout_v1.json"
out.write_text(json.dumps({
    "generated": "2026-04-15",
    "heldout_folios": sorted(HELDOUT),
    "heldout_tokens": len(holdout_words),
    "heldout_token_per_folio": dict(held_by_folio),
    "training_variants": len(train_variants),
    "training_rules": len(rules),
    "results": {
        "pharmaceutical": {
            "prevalence": sum(1 for _, s, _ in holdout_words
                              if s == "pharmaceutical") / len(holdout_words),
            "always_predict": always_predict_target("pharmaceutical"),
            "rule": evaluate("pharmaceutical", "rule"),
            "nb":   evaluate("pharmaceutical", "nb"),
        },
        "biological": {
            "prevalence": sum(1 for _, s, _ in holdout_words
                              if s == "biological") / len(holdout_words),
            "always_predict": always_predict_target("biological"),
            "rule": evaluate("biological", "rule"),
            "nb":   evaluate("biological", "nb"),
        },
    },
    "multiclass_accuracy": {
        "nb_on_holdout": correct_nb / total,
        "rule_on_covered": correct_rule / rule_covered if rule_covered else 0,
        "rule_coverage": rule_covered / total,
        "majority_baseline": majority_truth_rate,
    },
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
