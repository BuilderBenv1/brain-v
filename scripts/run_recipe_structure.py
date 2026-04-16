"""
Execute pre-registered H-BV-RECIPE-STRUCTURE-01.

Three-criterion recipe-structure test on Hand A:
  (1) Vocabulary disjunction: paragraph-INITIAL types vs MIDDLE-types.
      PASS if >=70% of INITIAL types never appear medially.
  (2) Recipe-verb properties: top-20 MIDDLE tokens inflected (>=2 stem
      variants) AND cross-folio (>=30% of Hand-A folios). PASS if
      >=15 of 20 pass both.
  (3) LOW-class INITIAL recurrence: >=10% of LOW paragraph-initial
      types initiate >=3 paragraphs.

Decision:
  3/3 -> CONFIRMED (pharmaceutical recipes)
  2/3 -> MARGINAL (follow up with ingredient clustering)
  0-1/3 -> REFUTED
"""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# =============================================================================
# HIGH/LOW split (same R=146 as NOMENCLATOR-01)
# =============================================================================
hand_a_words_flat = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words_flat.extend(line["words"])

freq = Counter(hand_a_words_flat)
N_total = sum(freq.values())
sorted_types = freq.most_common()
cum = 0; R = 0
for i, (t, c) in enumerate(sorted_types, 1):
    cum += c
    if cum >= N_total / 2:
        R = i; break
HIGH_TYPES = {t for t, _ in sorted_types[:R]}
assert R == 146
print(f"HIGH: {R} types; LOW: {len(freq) - R} types")

# =============================================================================
# Paragraph detection (same as HIGH-LOW-STRUCTURE-01)
# =============================================================================
def starts_with_plain_gallows(word):
    if not word: return False
    if word[0] not in "tp": return False
    if len(word) == 1: return True
    return word[1] != "h"

# Track (paragraph_tokens, folio) for cross-folio per-token analysis
folio_lines = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    if f["lines"]:
        folio_lines.append((f["folio"], f["lines"]))

paragraphs = []  # list of (tokens_list, folio_id)
for fid, lines in folio_lines:
    current = []
    for line in lines:
        w = line["words"]
        if not w: continue
        if starts_with_plain_gallows(w[0]) and current:
            paragraphs.append((current, fid))
            current = []
        current.extend(w)
    if current:
        paragraphs.append((current, fid))

print(f"Paragraphs detected: {len(paragraphs)}")

# =============================================================================
# Position bins per paragraph
# =============================================================================
# INITIAL = position 0
# FIRST   = 1 .. ceil(N/3)-1
# MIDDLE  = ceil(N/3) .. ceil(2N/3)-1
# FINAL   = ceil(2N/3) .. N-1
def bin_of(pos, n):
    if pos == 0: return "INITIAL"
    third = math.ceil(n / 3)
    if pos < third: return "FIRST"
    if pos < math.ceil(2*n / 3): return "MIDDLE"
    return "FINAL"

bin_tokens = defaultdict(list)       # bin -> [tokens]
bin_types = defaultdict(set)         # bin -> {types}
token_folios = defaultdict(set)      # token -> {folio_ids}
initial_tokens_list = []             # flat list of INITIAL-position tokens
initial_token_paragraph_count = Counter()  # token -> # of paragraphs where it initiates

for tokens, fid in paragraphs:
    n = len(tokens)
    if n == 0: continue
    for pos, w in enumerate(tokens):
        b = bin_of(pos, n)
        bin_tokens[b].append(w)
        bin_types[b].add(w)
        token_folios[w].add(fid)
    initial_tokens_list.append(tokens[0])
    initial_token_paragraph_count[tokens[0]] += 1

for b in ("INITIAL", "FIRST", "MIDDLE", "FINAL"):
    print(f"  {b:<8}: {len(bin_tokens[b]):>5} tokens, {len(bin_types[b]):>4} types")

# =============================================================================
# CRITERION 1 — VOCABULARY DISJUNCTION
# =============================================================================
print("\n" + "="*78)
print("  CRITERION 1 — vocabulary disjunction INITIAL vs MIDDLE")
print("="*78)
I_types = bin_types["INITIAL"]
M_types = bin_types["MIDDLE"]
disjunct = I_types - M_types
disj_ratio = len(disjunct) / len(I_types) if I_types else 0
print(f"  |INITIAL types|: {len(I_types)}")
print(f"  |MIDDLE  types|: {len(M_types)}")
print(f"  INITIAL types NOT in MIDDLE: {len(disjunct)}")
print(f"  disjunction ratio |I\\M|/|I|: {disj_ratio:.3f} (threshold >=0.70)")
crit1 = disj_ratio >= 0.70
print(f"  CRITERION 1: {'PASS' if crit1 else 'FAIL'}")

# =============================================================================
# CRITERION 2 — RECIPE-VERB PROPERTIES
# =============================================================================
print("\n" + "="*78)
print("  CRITERION 2 — top-20 MIDDLE tokens show recipe-verb properties")
print("="*78)

# Brady-style consonant-skeleton for stemming
EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
def skeleton(word):
    out = []; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                out.append(sy); i += len(ev); matched = True; break
        if not matched:
            i += 1
    return "".join(out)

middle_counts = Counter(bin_tokens["MIDDLE"])
top20 = middle_counts.most_common(20)

# Global consonant-skeleton index (across all Hand A)
skel_to_words = defaultdict(set)
for w in set(hand_a_words_flat):
    skel_to_words[skeleton(w)].add(w)

# Hand A folios for cross-folio coverage
hand_a_folios = {f["folio"] for f in CORPUS["folios"]
                  if f.get("currier_language") == "A"}
n_hand_a_folios = len(hand_a_folios)

print(f"  {'rank':<5}{'token':<14}{'count':>7}{'skel':<12}"
      f"{'variants':>10}{'folios':>9}{'cov%':>7}{'pass':>6}")

crit2_passes = 0
top20_details = []
for rank, (tok, cnt) in enumerate(top20, 1):
    sk = skeleton(tok)
    variants = skel_to_words[sk] & set(hand_a_words_flat)
    n_variants = len(variants)
    n_folios = len(token_folios[tok] & hand_a_folios)
    cov = n_folios / n_hand_a_folios if n_hand_a_folios else 0
    infl_ok = n_variants >= 2
    cov_ok = cov >= 0.30
    passed = infl_ok and cov_ok
    if passed: crit2_passes += 1
    print(f"  {rank:<5}{tok:<14}{cnt:>7}{sk:<12}{n_variants:>10}"
          f"{n_folios:>9}{cov*100:>6.1f}%{'YES' if passed else 'no':>6}")
    top20_details.append({
        "token": tok, "count": cnt, "skeleton": sk,
        "n_variants": n_variants, "n_folios": n_folios,
        "coverage": round(cov, 3), "pass": passed,
    })

print(f"\n  Top-20 passing BOTH inflection(>=2) AND coverage(>=30%): "
      f"{crit2_passes}/20")
crit2 = crit2_passes >= 15
print(f"  CRITERION 2: {'PASS' if crit2 else 'FAIL'} (threshold >=15 of 20)")

# =============================================================================
# CRITERION 3 — LOW-CLASS INITIAL RECURRENCE
# =============================================================================
print("\n" + "="*78)
print("  CRITERION 3 — LOW-class paragraph-initial recurrence (>=3 paragraphs)")
print("="*78)

low_initials = [t for t in initial_tokens_list if t not in HIGH_TYPES]
low_initial_types = set(low_initials)
# how many distinct LOW initial types appear at INITIAL in >= 3 paragraphs?
initial_paragraph_count_low = {t: initial_token_paragraph_count[t]
                                for t in low_initial_types}
recur = {t: n for t, n in initial_paragraph_count_low.items() if n >= 3}
n_recur = len(recur)
n_low_init_types = len(low_initial_types)
recur_ratio = n_recur / n_low_init_types if n_low_init_types else 0
print(f"  LOW-class paragraph-initial tokens: {len(low_initials)}")
print(f"  Distinct LOW-class initial types:   {n_low_init_types}")
print(f"  Types initiating >=3 paragraphs:    {n_recur}")
print(f"  Recurrence ratio:                   {recur_ratio:.3f} (threshold >=0.10)")
if recur:
    top_recur = sorted(recur.items(), key=lambda x: -x[1])[:10]
    print(f"  Top-10 recurring LOW initials:")
    for t, n in top_recur:
        print(f"    '{t}': {n} paragraphs")
crit3 = recur_ratio >= 0.10
print(f"  CRITERION 3: {'PASS' if crit3 else 'FAIL'}")

# =============================================================================
# Decision
# =============================================================================
n_pass = sum([crit1, crit2, crit3])
print("\n" + "="*78)
print("  PRE-REGISTERED DECISION")
print("="*78)
print(f"  Criterion 1 (disjunction):      {'PASS' if crit1 else 'FAIL'}")
print(f"  Criterion 2 (recipe-verbs):     {'PASS' if crit2 else 'FAIL'}")
print(f"  Criterion 3 (LOW recurrence):   {'PASS' if crit3 else 'FAIL'}")
print(f"  Total: {n_pass}/3")

if n_pass == 3:
    verdict = "CONFIRMED"
    print("  -> CONFIRMED. Hand A is medieval pharmaceutical recipe structure.")
elif n_pass == 2:
    verdict = "MARGINAL"
    print("  -> MARGINAL. Two criteria pass; ingredient-clustering follow-up warranted.")
else:
    verdict = "REFUTED"
    print("  -> REFUTED. Hand A is NOT pharmaceutical recipe structure under")
    print("     the locked criteria. The HIGH-LOW-STRUCTURE-01 regime-alternation")
    print("     signal has a different generative mechanism.")

out_path = ROOT / "outputs" / "recipe_structure_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-RECIPE-STRUCTURE-01",
    "n_paragraphs": len(paragraphs),
    "bin_sizes": {b: len(bin_tokens[b]) for b in ("INITIAL","FIRST","MIDDLE","FINAL")},
    "bin_types": {b: len(bin_types[b]) for b in ("INITIAL","FIRST","MIDDLE","FINAL")},
    "criterion_1": {
        "initial_types": len(I_types),
        "middle_types": len(M_types),
        "initial_not_in_middle": len(disjunct),
        "disjunction_ratio": round(disj_ratio, 4),
        "threshold": 0.70,
        "pass": crit1,
    },
    "criterion_2": {
        "top20_details": top20_details,
        "n_passing_both": crit2_passes,
        "threshold": 15,
        "pass": crit2,
    },
    "criterion_3": {
        "low_initial_types": n_low_init_types,
        "types_in_ge3_paragraphs": n_recur,
        "recurrence_ratio": round(recur_ratio, 4),
        "top_recurring": [{"token": t, "paragraphs": n}
                          for t, n in sorted(recur.items(), key=lambda x: -x[1])[:15]],
        "threshold": 0.10,
        "pass": crit3,
    },
    "n_criteria_passing": n_pass,
    "verdict": verdict,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
