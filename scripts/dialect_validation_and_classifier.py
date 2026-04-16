"""
Tasks 1, 2, 3, 4-execution.

TASK 1 — 5-fold CV on each (section, hand) marker set that has n>=10 folios
TASK 2 — Volvelle null on each (section, hand) marker set
TASK 3 — Classifier: given folio vowel-pattern distribution, predict (section, hand)
TASK 4 — Run pre-registered H-BV-EO-FAMILY-01

Marker sets from H-BV-DIALECT-01:
  HandA_pharma   (16 folios): _.o.eo, o.eo, o.eeo, _.oo, o.ee, _.eeo
  HandA_herbal   (95 folios): _.o._.o, _._._.o, _._.o, _._.o.o, _.eaii
  HandA_recipes  (2 folios)   — skip (too thin for CV)
  HandB_biological(19 folios): o._.ai
  HandB_recipes  (23 folios):  oai, ai.o, o.ea, o._.eeo, o.eeo, _.eo.ai, o.ee.a, _.o.eeo
  HandB_cosmological(3 folios) — skip
"""
import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

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

def split_skel_vowels(word):
    if word and word[0] in "tp" and (len(word)==1 or word[1]!="h"):
        word = word[1:]
    cons=[]; vs=[]; pos=0; i=0
    while i<len(word):
        matched=False
        for ev,sy in EVA_MAP:
            if word.startswith(ev,i):
                cons.append(sy); pos+=1; i+=len(ev); matched=True; break
        if not matched:
            if word[i] in VOWELS: vs.append((pos, word[i]))
            i+=1
    if not vs: return "".join(cons), ""
    by_pos = defaultdict(list)
    for p,v in vs: by_pos[p].append(v)
    return "".join(cons), ".".join("".join(by_pos.get(p,[])) or "_"
                                    for p in range(max(by_pos)+1))

folio_tokens = defaultdict(list)
folio_hand = {}
folio_section = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_hand[fid] = f.get("currier_language","?")
    folio_section[fid] = f["section"]
    for line in f["lines"]:
        folio_tokens[fid].extend(line["words"])

def in_hand_section(hand, section):
    return [f for f,m in folio_hand.items()
            if m == hand and folio_section.get(f) == section
            and len(folio_tokens[f]) >= 20]

def out_hand_section(hand, section):
    return [f for f,m in folio_hand.items()
            if m == hand and folio_section.get(f) != section
            and folio_section.get(f) != "?"
            and len(folio_tokens[f]) >= 20]

def rate_in_folios(folios, patterns):
    toks = [w for f in folios for w in folio_tokens[f]]
    if not toks: return 0.0
    return sum(1 for w in toks if split_skel_vowels(w)[1] in patterns) / len(toks)

MARKER_SETS = [
    ("HandA_pharma", "A", "pharmaceutical",
     ["_.o.eo", "o.eo", "o.eeo", "_.oo", "o.ee", "_.eeo"]),
    ("HandA_herbal", "A", "herbal",
     ["_.o._.o", "_._._.o", "_._.o", "_._.o.o", "_.eaii"]),
    ("HandB_biological", "B", "biological",
     ["o._.ai"]),
    ("HandB_recipes", "B", "recipes",
     ["oai", "ai.o", "o.ea", "o._.eeo", "o.eeo", "_.eo.ai", "o.ee.a", "_.o.eeo"]),
]

# =========================================================================
# TASK 1 — 5-fold CV per marker set
# =========================================================================
print("="*72)
print("  TASK 1 — 5-fold CV per (section, hand) marker set")
print("="*72)
task1_results = {}
for name, hand, section, patterns in MARKER_SETS:
    ins = in_hand_section(hand, section)
    outs = out_hand_section(hand, section)
    if len(ins) < 5:
        print(f"\n  {name}: n_in={len(ins)} — too thin for 5-fold CV, skipping")
        continue
    print(f"\n  {name}: n_in={len(ins)}, n_out={len(outs)}, {len(patterns)} patterns")
    out_rate = rate_in_folios(outs, set(patterns))

    random.seed(42)
    shuffled = ins[:]; random.shuffle(shuffled)
    K = 5
    fs = max(1, len(shuffled)//K)
    folds = [shuffled[i*fs:(i+1)*fs] for i in range(K-1)]
    folds.append(shuffled[(K-1)*fs:])

    # Combined marker-set CV
    fold_rates = []
    fold_enrs = []
    for fold in folds:
        r = rate_in_folios(fold, set(patterns))
        fold_rates.append(r)
        fold_enrs.append(r/out_rate if out_rate > 0 else (float("inf") if r > 0 else 0))

    combined_pass = sum(1 for e in fold_enrs if e >= 2.0 or math.isinf(e))
    print(f"    Combined-set baseline rate (out): {out_rate:.5f}")
    print(f"    Fold rates: " + ", ".join(f"{r:.5f}" for r in fold_rates))
    print(f"    Fold enrichments: " + ", ".join(
        "inf" if math.isinf(e) else f"{e:.2f}x" for e in fold_enrs))
    print(f"    Folds >= 2x: {combined_pass}/{K}")

    # Per-pattern CV
    per_pattern = {}
    for pat in patterns:
        out_r = rate_in_folios(outs, {pat})
        pat_fold_enrs = []
        for fold in folds:
            r = rate_in_folios(fold, {pat})
            pat_fold_enrs.append(r/out_r if out_r > 0 else (float("inf") if r > 0 else 0))
        pass_count = sum(1 for e in pat_fold_enrs if e >= 2.0 or math.isinf(e))
        per_pattern[pat] = {"fold_enrs": [round(e,3) if not math.isinf(e) else None
                                            for e in pat_fold_enrs],
                            "pass_4_5": pass_count >= 4}

    task1_results[name] = {
        "n_in": len(ins), "n_out": len(outs),
        "combined_baseline": round(out_rate, 5),
        "fold_rates": [round(r,5) for r in fold_rates],
        "fold_enrs": ["inf" if math.isinf(e) else round(e,3) for e in fold_enrs],
        "combined_pass_4_5": combined_pass >= 4,
        "per_pattern": per_pattern,
    }

# =========================================================================
# TASK 2 — Volvelle null per marker set
# =========================================================================
print("\n" + "="*72)
print("  TASK 2 — Volvelle null per marker set (200 runs, folio-level cartridges)")
print("="*72)

PREFIXES = ["qo", "q", "ch", "sh", "o", "d"]
SUFFIXES = ["aiin", "ain", "in", "y", "n", "r", "l"]
def strip_affixes(w):
    for p in PREFIXES:
        if w.startswith(p) and len(w) > len(p)+1: w = w[len(p):]; break
    for s in SUFFIXES:
        if w.endswith(s) and len(w) > len(s)+1: w = w[:-len(s)]; break
    return w

all_real = [w for f in CORPUS["folios"]
              for line in f["lines"] for w in line["words"]]
rc = Counter()
for w in all_real:
    r = strip_affixes(w)
    if 2 <= len(r) <= 6: rc[r] += 1
root_types = list(rc.keys()); root_weights = [rc[r] for r in root_types]

RING_A = ["", "q", "qo", "o", "d", "ch"]
RING_C = ["", "y", "n", "r", "l", "in", "ain", "aiin"]
WT_A = [3, 4, 3, 2, 2, 2, 2, 3]
WT_B = [2, 6, 2, 3, 1, 3, 3, 1]

def generate_folio_level(seed, cart_size=100):
    rng = random.Random(seed)
    folio_carts = {}
    for folio in CORPUS["folios"]:
        picks = set(); attempts = 0
        while len(picks) < cart_size and attempts < cart_size*50:
            r = rng.choices(root_types, weights=root_weights, k=1)[0]
            picks.add(r); attempts += 1
        folio_carts[folio["folio"]] = list(picks)
    synth = defaultdict(list)
    for folio in CORPUS["folios"]:
        cur = folio.get("currier_language","?"); fid = folio["folio"]
        cart = folio_carts[fid]
        weights = WT_B if cur == "B" else WT_A
        for line in folio["lines"]:
            for _ in line["words"]:
                prefix = rng.choice(RING_A)
                root   = rng.choice(cart)
                suffix = rng.choices(RING_C, weights=weights, k=1)[0]
                synth[fid].append(prefix + root + suffix)
    return synth

def synth_rate(synth, folios, patterns):
    toks = [w for f in folios for w in synth[f]]
    if not toks: return 0.0
    return sum(1 for w in toks if split_skel_vowels(w)[1] in patterns) / len(toks)

task2_results = {}
N_VOL = 100  # keep runtime reasonable; 100 suffices at the margins we see
for name, hand, section, patterns in MARKER_SETS:
    ins = in_hand_section(hand, section)
    outs = out_hand_section(hand, section)
    if len(ins) < 5:
        continue
    # Real diff
    real_in = rate_in_folios(ins, set(patterns))
    real_out = rate_in_folios(outs, set(patterns))
    real_diff = real_in - real_out

    print(f"\n  {name}: real in={real_in:.5f}, out={real_out:.5f}, diff={real_diff:+.5f}")
    diffs = []
    for seed in range(N_VOL):
        synth = generate_folio_level(seed, 100)
        s_in = synth_rate(synth, ins, set(patterns))
        s_out = synth_rate(synth, outs, set(patterns))
        diffs.append(s_in - s_out)
    mu = statistics.mean(diffs); sd = statistics.pstdev(diffs)
    p_emp = sum(1 for d in diffs if d >= real_diff) / len(diffs)
    z = (real_diff - mu) / sd if sd > 0 else float("inf")
    print(f"    Null diffs: mean {mu:+.5f}, sd {sd:.5f}, z {z:.2f}, p_emp {p_emp:.4f}")
    task2_results[name] = {
        "real_in_rate": round(real_in, 5),
        "real_out_rate": round(real_out, 5),
        "real_diff": round(real_diff, 5),
        "null_mean": round(mu, 5),
        "null_sd": round(sd, 5),
        "z": round(z, 2) if not math.isinf(z) else None,
        "p_emp": round(p_emp, 4),
    }

# =========================================================================
# TASK 3 — Classifier: vowel-pattern distribution -> (section, hand)
# =========================================================================
print("\n" + "="*72)
print("  TASK 3 — Classifier: folio vowel patterns -> (section, hand)")
print("="*72)

# Use folios with hand in A/B and section not '?' and tokens>=20.
# Label = (hand, section). Only classes with n>=5 folios.
records = []
for f, h in folio_hand.items():
    if h not in ("A","B"): continue
    sec = folio_section.get(f)
    if not sec: continue
    if len(folio_tokens[f]) < 20: continue
    records.append((f, h, sec))

label_counts = Counter((h,s) for _, h, s in records)
valid_labels = {lbl: n for lbl, n in label_counts.items() if n >= 5}
print(f"  Records: {len(records)} folios")
print(f"  Classes with n>=5: {len(valid_labels)}")
for lbl, n in sorted(valid_labels.items(), key=lambda x: -x[1]):
    print(f"    {lbl} -> {n} folios")

records = [(f, h, s) for f, h, s in records if (h, s) in valid_labels]
print(f"  Using {len(records)} folios across {len(valid_labels)} classes")

# Folio feature: counter of vowel patterns (bag-of-patterns)
def folio_feature(fid):
    vp = Counter()
    total = 0
    for w in folio_tokens[fid]:
        _, p = split_skel_vowels(w)
        vp[p] += 1; total += 1
    return vp, total

# Naive Bayes over bag-of-patterns with add-one smoothing
def train_nb(train_records):
    prior = Counter()
    per_class = defaultdict(Counter)
    class_totals = Counter()
    for fid, h, s in train_records:
        lbl = (h, s)
        prior[lbl] += 1
        vp, _ = folio_feature(fid)
        for p, c in vp.items():
            per_class[lbl][p] += c
            class_totals[lbl] += c
    return prior, per_class, class_totals

def nb_predict(fid, prior, per_class, class_totals, vocab_size):
    vp, total = folio_feature(fid)
    if total == 0: return None
    best = None; best_lp = -1e18
    N_classes = len(prior)
    log_N = math.log(sum(prior.values()) + N_classes)
    for lbl, pc in prior.items():
        lp = math.log((pc + 1)) - log_N
        for p, c in vp.items():
            num = per_class[lbl].get(p, 0) + 1
            den = class_totals[lbl] + vocab_size
            lp += c * math.log(num/den)
        if lp > best_lp: best_lp = lp; best = lbl
    return best

# 5-fold CV on records
random.seed(101)
shuffled = records[:]; random.shuffle(shuffled)
K = 5
fs = max(1, len(shuffled)//K)
cv_folds = [shuffled[i*fs:(i+1)*fs] for i in range(K-1)]
cv_folds.append(shuffled[(K-1)*fs:])

# Vocab = all patterns across corpus
all_vocab = set()
for f in folio_tokens:
    for w in folio_tokens[f]:
        _, p = split_skel_vowels(w)
        all_vocab.add(p)
vocab_size = len(all_vocab)

correct = 0; majority_correct = 0; total = 0
per_class_right = Counter(); per_class_total = Counter()
for k in range(K):
    test = cv_folds[k]
    train = [r for i, fold in enumerate(cv_folds) if i != k for r in fold]
    prior, per_class, class_totals = train_nb(train)
    majority = max(prior, key=prior.get)
    for fid, h, s in test:
        pred = nb_predict(fid, prior, per_class, class_totals, vocab_size)
        total += 1
        per_class_total[(h,s)] += 1
        if pred == (h, s):
            correct += 1
            per_class_right[(h,s)] += 1
        if majority == (h, s):
            majority_correct += 1

acc = correct / total
maj_acc = majority_correct / total
chance = 1.0 / len(valid_labels)
print(f"\n  5-fold CV multi-class accuracy:     {acc:.1%}")
print(f"  Majority-class baseline:            {maj_acc:.1%}")
print(f"  Chance (uniform):                   {chance:.1%}")
print(f"  Gain over majority:                 {acc - maj_acc:+.1%}")
print(f"\n  Per-class accuracy:")
for lbl in sorted(valid_labels):
    rate = per_class_right[lbl] / per_class_total[lbl] if per_class_total[lbl] else 0
    print(f"    {str(lbl):<40} {per_class_right[lbl]}/{per_class_total[lbl]} = {rate:.1%}")

# =========================================================================
# TASK 4 — Run pre-registered H-BV-EO-FAMILY-01
# =========================================================================
print("\n" + "="*72)
print("  TASK 4 — Pre-registered H-BV-EO-FAMILY-01")
print("="*72)

# Load plant folios to exclude them (we want PREPARATION vs NON-PREPARATION NON-PLANT)
plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        plant_folios.add(r["folio"])

def eo_family_rate(fid):
    toks = folio_tokens[fid]
    if len(toks) < 20: return None
    return sum(1 for w in toks if "eo" in split_skel_vowels(w)[1]) / len(toks)

PREP_SECTIONS = {"pharmaceutical", "recipes"}
task4_results = {}
for hand in ("A", "B"):
    prep = [f for f,m in folio_hand.items()
            if m == hand and folio_section.get(f) in PREP_SECTIONS
            and eo_family_rate(f) is not None]
    nonprep = [f for f,m in folio_hand.items()
               if m == hand
               and folio_section.get(f) not in PREP_SECTIONS
               and folio_section.get(f) not in {"?"}
               and f not in plant_folios
               and eo_family_rate(f) is not None]
    if len(prep) < 3 or len(nonprep) < 3:
        print(f"\n  Hand {hand}: prep={len(prep)} nonprep={len(nonprep)} — too thin")
        task4_results[hand] = {"status": "too_thin", "prep_n": len(prep), "nonprep_n": len(nonprep)}
        continue
    prep_rates = [eo_family_rate(f) for f in prep]
    nonprep_rates = [eo_family_rate(f) for f in nonprep]
    mp = statistics.mean(prep_rates)
    mn = statistics.mean(nonprep_rates)
    t, p2 = stats.ttest_ind(prep_rates, nonprep_rates, equal_var=False)
    p1 = p2/2 if t > 0 else 1 - p2/2
    va = statistics.variance(prep_rates) if len(prep_rates)>1 else 0
    vb = statistics.variance(nonprep_rates) if len(nonprep_rates)>1 else 0
    na, nb = len(prep_rates), len(nonprep_rates)
    pooled = ((va*(na-1)+vb*(nb-1))/(na+nb-2))**0.5 if na+nb > 2 else 0
    d = (mp-mn)/pooled if pooled > 0 else 0
    u, p_u = stats.mannwhitneyu(prep_rates, nonprep_rates, alternative="greater")
    # Bootstrap CI
    rng = random.Random(7); B = 5000
    diffs = []
    for _ in range(B):
        a = [rng.choice(prep_rates) for _ in prep_rates]
        b = [rng.choice(nonprep_rates) for _ in nonprep_rates]
        diffs.append(statistics.mean(a) - statistics.mean(b))
    diffs.sort()
    lo, hi = diffs[int(B*0.025)], diffs[int(B*0.975)]
    print(f"\n  Hand {hand}:")
    print(f"    Prep    n={len(prep):>3}  mean eo-rate {mp:.5f}")
    print(f"    NonPrep n={len(nonprep):>3}  mean eo-rate {mn:.5f}")
    print(f"    Ratio {mp/mn if mn>0 else float('inf'):.2f}x")
    print(f"    t={t:+.3f}, one-tailed p={p1:.6f}")
    print(f"    Cohen d={d:.3f}")
    print(f"    Mann-Whitney U p={p_u:.6f}")
    print(f"    Bootstrap 95% CI [{lo:+.5f}, {hi:+.5f}]")
    passed = (p1 < 0.05 and d >= 0.4)
    task4_results[hand] = {
        "prep_n": len(prep), "nonprep_n": len(nonprep),
        "prep_mean": round(mp, 6), "nonprep_mean": round(mn, 6),
        "ratio": round(mp/mn, 3) if mn > 0 else None,
        "t": round(t, 4), "p_one_tailed": round(p1, 6),
        "cohens_d": round(d, 3),
        "mann_whitney_p": round(p_u, 6),
        "ci_95": [round(lo, 6), round(hi, 6)],
        "passed": bool(passed),
    }

both_passed = all(v.get("passed") for v in task4_results.values() if isinstance(v, dict) and "passed" in v)
any_passed = any(v.get("passed") for v in task4_results.values() if isinstance(v, dict) and "passed" in v)
print(f"\n  PRE-REGISTERED DECISION:")
if both_passed:
    print("    Both hands pass -> CONFIRMED cross-hand 'eo' meta-feature")
elif any_passed:
    print("    One hand passes -> PARTIAL (hand-specific)")
else:
    print("    Neither hand passes -> REFUTED")

# =========================================================================
# Save all
# =========================================================================
out = ROOT / "outputs" / "dialect_validation_and_classifier.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "task1_holdout_cv": task1_results,
    "task2_volvelle_null": task2_results,
    "task3_classifier": {
        "n_classes": len(valid_labels),
        "class_counts": {str(k): v for k,v in valid_labels.items()},
        "accuracy": round(acc, 4),
        "majority_baseline": round(maj_acc, 4),
        "chance": round(chance, 4),
        "gain_over_majority": round(acc - maj_acc, 4),
        "per_class": {str(k): {"correct": per_class_right[k], "total": per_class_total[k]}
                      for k in valid_labels},
    },
    "task4_eo_family": task4_results,
    "task4_verdict": ("confirmed" if both_passed else ("partial" if any_passed else "refuted")),
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
