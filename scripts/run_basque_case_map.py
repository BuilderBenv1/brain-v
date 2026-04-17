"""
Execute pre-registered H-BV-BASQUE-CASE-MAP-01.

For each Hand A Layer-2 outer, score against 6 Basque case markers on
(FREQ band, SEL profile, TERMINAL>=0.60). 2-of-3 = outer-case match.
Construct injective mapping greedy-best-first.

Locked decision rule:
  CONFIRMED: >=3 outers map injectively to distinct cases
  MARGINAL: exactly 2
  REFUTED:  <=1
"""
import json
from collections import Counter
from pathlib import Path

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

VOWEL_LIKE = {"i", "e", "o", "a"}
CONSONANT_INNERS_SET = {"ch", "d", "k", "t", "sh", "l"}
LAYER2_OUTERS = ["y", "n", "r", "ol", "l"]
OUTER_SET = set(LAYER2_OUTERS)

# =============================================================================
# Hand A outer profiles (from CAPPELLI-MATCH-01, recomputed locally)
# =============================================================================
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

tokenised = [tokenize(w) for w in hand_a_words]
valid = [t for t in tokenised if len(t) >= 3]
inners = [t[-2] for t in valid]
outers = [t[-1] for t in valid]

# Terminal fraction: fraction of all occurrences that are word-terminal
occ_total = Counter()
occ_terminal = Counter()
for t in tokenised:
    for i, g in enumerate(t):
        occ_total[g] += 1
        if i == len(t) - 1:
            occ_terminal[g] += 1

total_terminal_positions = sum(occ_terminal.values())

# Layer-2 frequency: fraction of total terminal positions
outer_profile = {}
for o in LAYER2_OUTERS:
    term_count = occ_terminal[o]
    tot = occ_total[o]
    layer2_freq = term_count / total_terminal_positions if total_terminal_positions else 0.0
    term_frac = term_count / tot if tot else 0.0
    n_V = sum(1 for i, out in zip(inners, outers) if out == o and i in VOWEL_LIKE)
    n_C = sum(1 for i, out in zip(inners, outers) if out == o and i in CONSONANT_INNERS_SET)
    tot_V_inner = sum(1 for i in inners if i in VOWEL_LIKE)
    tot_C_inner = sum(1 for i in inners if i in CONSONANT_INNERS_SET)
    p_V = n_V / tot_V_inner if tot_V_inner else 0.0
    p_C = n_C / tot_C_inner if tot_C_inner else 0.0
    if p_C > 0:
        diff = p_V / p_C
    elif p_V > 0:
        diff = float("inf")
    else:
        diff = 1.0
    # classify selection
    if diff == float("inf") or diff >= 3.0:
        sel_class = "V-pref"
    elif diff <= 1/3.0:
        sel_class = "C-pref"
    else:
        sel_class = "neutral"
    outer_profile[o] = {
        "freq": layer2_freq,
        "term_frac": term_frac,
        "diff": diff,
        "sel_class": sel_class,
    }

print("Hand A outer profile summary:")
for o in LAYER2_OUTERS:
    p = outer_profile[o]
    d_str = f"{p['diff']:.2f}" if p["diff"] != float("inf") else "inf"
    print(f"  {o}:  freq={p['freq']:.4f}  term={p['term_frac']:.4f}  diff={d_str}  sel={p['sel_class']}")

# Bare fraction (no top-5 outer)
bare_count = sum(1 for t in valid if t[-1] not in OUTER_SET)
bare_frac = bare_count / len(valid) if valid else 0.0
print(f"\nBare (N>=3 tokens ending NOT in top-5 outer): {bare_count}/{len(valid)} = {bare_frac:.4f}")

# =============================================================================
# Basque case profiles (locked)
# =============================================================================
CASES = {
    "C_ERG":  {"freq_range": (0.05, 0.15), "sel_req": "any",     "desc": "ergative -k"},
    "C_DAT":  {"freq_range": (0.03, 0.10), "sel_req": "V-pref",  "desc": "dative -(r)i"},
    "C_GEN":  {"freq_range": (0.05, 0.15), "sel_req": "V-pref",  "desc": "genitive -(r)en"},
    "C_INST": {"freq_range": (0.02, 0.08), "sel_req": "any",     "desc": "instrumental -z"},
    "C_LOC":  {"freq_range": (0.05, 0.15), "sel_req": "V-pref",  "desc": "locative -n"},
}
# C_ABS is absolutive (zero marker) — tested separately via bare_frac diagnostic

# =============================================================================
# Score each Hand A outer vs each Basque case
# =============================================================================
def score(outer, case):
    p = outer_profile[outer]
    ref = CASES[case]
    fmin, fmax = ref["freq_range"]
    # FREQ
    freq_pass = (fmin <= p["freq"] <= fmax)
    # SEL
    if ref["sel_req"] == "any":
        sel_pass = True
    elif ref["sel_req"] == "V-pref":
        sel_pass = (p["sel_class"] == "V-pref")
    elif ref["sel_req"] == "C-pref":
        sel_pass = (p["sel_class"] == "C-pref")
    else:
        sel_pass = False
    # TERM
    term_pass = (p["term_frac"] >= 0.60)
    score = int(freq_pass) + int(sel_pass) + int(term_pass)
    return {
        "freq_pass": freq_pass,
        "sel_pass": sel_pass,
        "term_pass": term_pass,
        "score": score,
        "match": score >= 2,
    }

print("\n" + "="*78)
print("  OUTER vs CASE scoring matrix (2/3 criteria = MATCH)")
print("="*78)
print(f"  {'outer':<6} {'case':<8} {'FREQ':>6} {'SEL':>5} {'TERM':>5} {'score':>6} {'match':<6}")
print(f"  {'-'*6} {'-'*8} {'-'*6} {'-'*5} {'-'*5} {'-'*6} {'-'*6}")
scoring_matrix = {}
for o in LAYER2_OUTERS:
    scoring_matrix[o] = {}
    for c in CASES.keys():
        s = score(o, c)
        scoring_matrix[o][c] = s
        mflag = "MATCH" if s["match"] else "-"
        print(f"  {o:<6} {c:<8} {int(s['freq_pass']):>6} {int(s['sel_pass']):>5} "
              f"{int(s['term_pass']):>5} {s['score']:>6} {mflag:<6}")

# =============================================================================
# Injective mapping, greedy best-first
# =============================================================================
print("\n" + "="*78)
print("  INJECTIVE MAPPING (greedy, best-first by score)")
print("="*78)

# Build all (outer, case, score) triples for matches
triples = []
for o in LAYER2_OUTERS:
    for c in CASES.keys():
        s = scoring_matrix[o][c]
        if s["match"]:
            triples.append((o, c, s["score"]))
triples.sort(key=lambda x: -x[2])  # highest score first

assigned_outers = set()
assigned_cases = set()
mapping = []
for o, c, sc in triples:
    if o in assigned_outers or c in assigned_cases:
        continue
    mapping.append((o, c, sc))
    assigned_outers.add(o)
    assigned_cases.add(c)
    print(f"  {o} -> {c} ({CASES[c]['desc']})  score {sc}/3")

unmatched_outers = [o for o in LAYER2_OUTERS if o not in assigned_outers]
for o in unmatched_outers:
    print(f"  {o} -> (no Basque case match, all unmatched cases scored <2/3)")

# =============================================================================
# Diagnostic: bare fraction vs Basque C_ABS expectation
# =============================================================================
print("\n" + "="*78)
print("  DIAGNOSTIC — bare-fraction vs Basque C_ABS (30-50% expected)")
print("="*78)
abs_pass = 0.30 <= bare_frac <= 0.50
print(f"  Hand A bare-fraction (tokens without top-5 outer): {bare_frac:.4f}")
print(f"  Basque C_ABS expected: [0.30, 0.50]")
print(f"  {'Within range' if abs_pass else 'OUTSIDE range (informational)'}")

# =============================================================================
# LOCKED DECISION
# =============================================================================
print("\n" + "="*78)
print("  LOCKED DECISION")
print("="*78)
n_mapped = len(mapping)
print(f"  Hand A outers mapped injectively to distinct Basque cases: {n_mapped}/5")

if n_mapped >= 3:
    verdict = "CONFIRMED"
    rationale = f"{n_mapped}/5 outers map injectively to distinct Basque cases at 2-of-3 criteria"
elif n_mapped == 2:
    verdict = "MARGINAL"
    rationale = "Exactly 2 outers map; partial support for Basque case structure"
else:
    verdict = f"REFUTED"
    rationale = f"Only {n_mapped} outer(s) map; Basque case mapping fails"

print(f"\n  VERDICT: {verdict}")
print(f"  {rationale}")
print(f"  Diagnostic (non-decision): bare-fraction {bare_frac:.4f}; "
      f"Basque ABS range [0.30, 0.50]: {'in range' if abs_pass else 'OUT of range'}")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "basque_case_map_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-17",
    "hypothesis": "H-BV-BASQUE-CASE-MAP-01",
    "outer_profile": {o: {k: (v if not isinstance(v, float) or v != float('inf') else "inf")
                          for k, v in p.items()} for o, p in outer_profile.items()},
    "basque_cases": CASES,
    "scoring_matrix": {o: {c: {k: v for k, v in s.items()} for c, s in d.items()}
                       for o, d in scoring_matrix.items()},
    "injective_mapping": [{"outer": o, "case": c, "score": sc, "desc": CASES[c]["desc"]}
                          for o, c, sc in mapping],
    "unmatched_outers": unmatched_outers,
    "bare_fraction": round(bare_frac, 4),
    "diagnostic_abs_in_range": abs_pass,
    "n_mapped": n_mapped,
    "verdict": verdict,
    "rationale": rationale,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
