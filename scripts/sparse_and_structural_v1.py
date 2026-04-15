"""
Two continuations of the vowel-decode work, both honestly evaluated.

A. Sparse high-precision dictionary
   -----------------------------------
   Stratified 80/20 split by folio (not by token). Train: learn vowel
   pattern -> section rules. Holdout: measure each rule's precision
   on truly unseen folios. Keep ONLY rules with held-out precision
   >= 0.70 AND >= 10 held-out fires. Report the final sparse
   dictionary with its honest coverage.

B. Non-vowel structural features
   -------------------------------
   Features per token:
     - q_initial         (word starts with 'q')
     - suffix_class      (y/n/r/m/g final)
     - bench_gallows     (contains cth/ckh/cph)
     - plain_gallows_li  (word is line-initial AND starts with t/p)
     - skel_length       (length of consonant skeleton)
     - line_position     (normalised: early/mid/late)
     - vowel_pattern     (for comparison)
   Naive-Bayes classifier on non-vowel features alone; then combined.
   Report held-out multi-class accuracy vs (majority baseline, vowel-only).
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
    cons = []; vs = []; pos = 0; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                cons.append(sy); pos += 1; i += len(ev); matched = True; break
        if not matched:
            if word[i] in VOWELS: vs.append((pos, word[i]))
            i += 1
    if not vs:
        return "".join(cons), ""
    by_pos = defaultdict(list)
    for p, v in vs: by_pos[p].append(v)
    return "".join(cons), ".".join("".join(by_pos.get(p, [])) or "_"
                                    for p in range(max(by_pos) + 1))

# =========================================================================
# 80/20 folio split, stratified by section
# =========================================================================
random.seed(42)
folios_by_section = defaultdict(list)
for f in CORPUS["folios"]:
    folios_by_section[f["section"]].append(f["folio"])

train_folios = set(); holdout_folios = set()
for sec, fl in folios_by_section.items():
    fl_shuf = fl[:]; random.shuffle(fl_shuf)
    k = max(1, int(round(len(fl_shuf) * 0.2)))
    holdout_folios.update(fl_shuf[:k])
    train_folios.update(fl_shuf[k:])

print(f"Train folios: {len(train_folios)}, Holdout folios: {len(holdout_folios)}")

# Gather tokens with metadata
def token_iter():
    for folio in CORPUS["folios"]:
        fid = folio["folio"]; sec = folio["section"]
        nlines = len(folio["lines"])
        for line_i, line in enumerate(folio["lines"]):
            is_line_initial_word = True  # first word of line
            for word in line["words"]:
                yield {
                    "word": word, "folio": fid, "section": sec,
                    "line_i": line_i, "nlines": nlines,
                    "is_li": is_line_initial_word,
                    "split": "holdout" if fid in holdout_folios else "train",
                }
                is_line_initial_word = False

all_tokens = list(token_iter())
train_tokens = [t for t in all_tokens if t["split"] == "train"]
holdout_tokens = [t for t in all_tokens if t["split"] == "holdout"]
print(f"Train tokens: {len(train_tokens)}, Holdout tokens: {len(holdout_tokens)}")

# =========================================================================
# A. SPARSE HIGH-PRECISION DICTIONARY
# =========================================================================
print("\n" + "="*72)
print("  PART A — Sparse high-precision vowel-pattern dictionary")
print("="*72)

# Step 1: discover rules on TRAIN only
train_pat_sec = defaultdict(Counter)
for t in train_tokens:
    _, vp = split_skel_vowels(t["word"])
    train_pat_sec[vp][t["section"]] += 1

# For each pattern, identify its modal section on train
train_rules = {}  # vp -> (modal_sec, train_prec, train_support)
for vp, counts in train_pat_sec.items():
    n = sum(counts.values())
    if n < 20: continue  # need at least 20 training tokens
    sec, c = counts.most_common(1)[0]
    train_rules[vp] = (sec, c/n, n)

print(f"Training rules (>=20 train tokens): {len(train_rules)}")

# Step 2: evaluate on holdout
holdout_pat_sec = defaultdict(Counter)
for t in holdout_tokens:
    _, vp = split_skel_vowels(t["word"])
    holdout_pat_sec[vp][t["section"]] += 1

sparse_dict = []
for vp, (modal, train_prec, train_n) in train_rules.items():
    ho_counts = holdout_pat_sec.get(vp, Counter())
    ho_n = sum(ho_counts.values())
    if ho_n < 10: continue
    ho_hits = ho_counts.get(modal, 0)
    ho_prec = ho_hits / ho_n
    if ho_prec >= 0.70:
        sparse_dict.append({
            "vowel_pattern": vp, "section": modal,
            "train_prec": round(train_prec, 3), "train_n": train_n,
            "holdout_prec": round(ho_prec, 3), "holdout_n": ho_n,
            "holdout_hits": ho_hits,
        })

sparse_dict.sort(key=lambda r: (-r["holdout_prec"], -r["holdout_n"]))
print(f"Rules surviving holdout >=0.70 precision AND >=10 fires: {len(sparse_dict)}")

# Coverage of the sparse dict on holdout
ho_total = len(holdout_tokens)
covered_tokens = 0
correct_tokens = 0
for t in holdout_tokens:
    _, vp = split_skel_vowels(t["word"])
    for r in sparse_dict:
        if r["vowel_pattern"] == vp:
            covered_tokens += 1
            if r["section"] == t["section"]:
                correct_tokens += 1
            break
coverage = covered_tokens / ho_total if ho_total else 0
honest_prec = correct_tokens / covered_tokens if covered_tokens else 0
print(f"Holdout token coverage:  {covered_tokens}/{ho_total} = {coverage:.1%}")
print(f"Holdout precision:       {correct_tokens}/{covered_tokens} = {honest_prec:.1%}")

# Show top 15
print(f"\n  Top sparse dictionary entries (sorted by holdout precision):")
print(f"  {'vp':<14} {'section':<15} {'train-prec':>10} {'train-n':>8} "
      f"{'ho-prec':>8} {'ho-n':>6}")
for r in sparse_dict[:15]:
    print(f"  {r['vowel_pattern']:<14} {r['section']:<15} "
          f"{r['train_prec']:>10.3f} {r['train_n']:>8} "
          f"{r['holdout_prec']:>8.3f} {r['holdout_n']:>6}")

# =========================================================================
# B. NON-VOWEL STRUCTURAL FEATURES
# =========================================================================
print("\n" + "="*72)
print("  PART B — Non-vowel structural features")
print("="*72)

SUFFIX_CHARS = set("ynrmg")
MULTICHAR = ["cth", "ckh", "cph"]

def features(t):
    w = t["word"]
    sk, vp = split_skel_vowels(w)
    f = {}
    # q-initial
    f["q_init"] = int(w.startswith("q"))
    # suffix class
    f["suffix"] = w[-1] if w and w[-1] in SUFFIX_CHARS else "none"
    # bench gallows present
    f["bench"] = int(any(m in w for m in MULTICHAR))
    # plain gallows line-initial (word is line-initial AND starts with t/p non-bench)
    plain_gallow = (w and w[0] in "tp" and (len(w)==1 or w[1]!="h"))
    f["pg_li"] = int(t["is_li"] and plain_gallow)
    # skel length bucket
    f["skel_len"] = min(len(sk), 5)
    # line position bucket
    if t["nlines"] > 0:
        r = t["line_i"] / t["nlines"]
        f["line_bucket"] = "early" if r < 0.33 else ("mid" if r < 0.67 else "late")
    else:
        f["line_bucket"] = "mid"
    # vowel pattern (kept for comparison)
    f["vp"] = vp
    return f

# Build feature counts on train
def train_nb(tokens, feat_keys):
    prior = Counter()
    likelihood = defaultdict(Counter)  # (feat_name, value) -> Counter(section)
    sec_totals = Counter()
    for t in tokens:
        f = features(t)
        prior[t["section"]] += 1
        sec_totals[t["section"]] += 1
        for k in feat_keys:
            likelihood[(k, f[k])][t["section"]] += 1
    return prior, likelihood, sec_totals

def nb_predict(t, feat_keys, prior, likelihood, sec_totals):
    f = features(t)
    N = sum(prior.values())
    best = None; best_lp = -1e18
    for sec in SECTIONS:
        if sec_totals[sec] == 0: continue
        lp = math.log((prior[sec]+1) / (N + len(SECTIONS)))
        for k in feat_keys:
            c = likelihood[(k, f[k])][sec]
            lp += math.log((c + 1) / (sec_totals[sec] + 20))
        if lp > best_lp: best_lp = lp; best = sec
    return best

def evaluate_nb(feat_keys, label):
    prior, likelihood, sec_totals = train_nb(train_tokens, feat_keys)
    correct = 0
    for t in holdout_tokens:
        p = nb_predict(t, feat_keys, prior, likelihood, sec_totals)
        if p == t["section"]: correct += 1
    acc = correct / len(holdout_tokens)
    majority = prior.most_common(1)[0][0]
    maj_acc = sum(1 for t in holdout_tokens
                  if t["section"] == majority) / len(holdout_tokens)
    return dict(label=label, acc=acc, maj_acc=maj_acc,
                gain=acc - maj_acc, feat_keys=feat_keys)

vowel_only = evaluate_nb(["vp"], "vowel pattern only")
struct_only = evaluate_nb(
    ["q_init", "suffix", "bench", "pg_li", "skel_len", "line_bucket"],
    "non-vowel structural only")
combined = evaluate_nb(
    ["vp", "q_init", "suffix", "bench", "pg_li", "skel_len", "line_bucket"],
    "combined (vowel + structural)")

print(f"\n  {'Classifier':<35} {'accuracy':>10} {'majority':>10} {'gain':>8}")
for r in [vowel_only, struct_only, combined]:
    print(f"  {r['label']:<35} {r['acc']:>9.1%} "
          f"{r['maj_acc']:>9.1%} {r['gain']:>+7.1%}")

# Feature-importance proxy: compute single-feature held-out accuracy
print(f"\n  Single-feature held-out accuracy:")
for k in ["q_init", "suffix", "bench", "pg_li", "skel_len", "line_bucket", "vp"]:
    r = evaluate_nb([k], k)
    print(f"    {k:<15} {r['acc']:>7.1%} (gain {r['gain']:+.1%})")

# =========================================================================
# Per-target precision on non-vowel features
# =========================================================================
prior, likelihood, sec_totals = train_nb(
    train_tokens, ["q_init","suffix","bench","pg_li","skel_len","line_bucket"])
print(f"\n  Per-target held-out precision under structural-only NB:")
print(f"  {'target':<16} {'precision':>10} {'recall':>8} {'F1':>8} {'prev':>6}")
for target in SECTIONS:
    tp = fp = fn = 0
    for t in holdout_tokens:
        pred = nb_predict(t, ["q_init","suffix","bench","pg_li","skel_len","line_bucket"],
                          prior, likelihood, sec_totals)
        is_tgt = (pred == target); is_t = (t["section"] == target)
        if is_tgt and is_t: tp += 1
        elif is_tgt and not is_t: fp += 1
        elif not is_tgt and is_t: fn += 1
    prev = sum(1 for t in holdout_tokens if t["section"] == target) / len(holdout_tokens)
    prec = tp/(tp+fp) if (tp+fp) else 0
    rec = tp/(tp+fn) if (tp+fn) else 0
    f1 = 2*prec*rec/(prec+rec) if (prec+rec) else 0
    if tp + fp + fn > 0:
        print(f"  {target:<16} {prec:>10.3f} {rec:>8.3f} {f1:>8.3f} {prev:>6.1%}")

# =========================================================================
# Save
# =========================================================================
out = ROOT / "outputs" / "sparse_and_structural_v1.json"
out.write_text(json.dumps({
    "generated": "2026-04-15",
    "split": {"train_folios": len(train_folios),
              "holdout_folios": len(holdout_folios),
              "train_tokens": len(train_tokens),
              "holdout_tokens": len(holdout_tokens)},
    "sparse_dictionary": {
        "size": len(sparse_dict),
        "coverage": round(coverage, 4),
        "honest_precision": round(honest_prec, 4),
        "entries": sparse_dict,
    },
    "structural_classifiers": {
        "vowel_only": {k: v for k, v in vowel_only.items() if k != "feat_keys"},
        "struct_only": {k: v for k, v in struct_only.items() if k != "feat_keys"},
        "combined": {k: v for k, v in combined.items() if k != "feat_keys"},
    },
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")

# Also save sparse dict as CSV for human review
import csv
csv_path = ROOT / "outputs" / "brainv_sparse_dictionary.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["vowel_pattern","section","train_prec","train_n","holdout_prec","holdout_n"])
    for r in sparse_dict:
        w.writerow([r["vowel_pattern"], r["section"],
                    r["train_prec"], r["train_n"],
                    r["holdout_prec"], r["holdout_n"]])
print(f"CSV: {csv_path}")
