"""
Execute pre-registered H-BV-CAPPELLI-MATCH-01.

Score each Hand A Layer-2 outer against 5 documented Latin scribal
abbreviation conventions on 3 dimensions (positional, selectional,
frequency). An outer matches a Latin convention at >=2/3; an outer
shows 'strong correspondence' if it matches at least one convention.

Locked decision rule:
  CONFIRMED: >=3/5 outers show strong correspondence
  MARGINAL: 1-2/5 match
  REFUTED: 0/5 match
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

VOWEL_INNERS = {"i", "e", "o", "a"}
CONSONANT_INNERS = {"ch", "d", "k", "t", "sh", "l"}
LAYER2_OUTERS = ["y", "n", "r", "ol", "l"]

# =============================================================================
# Build Hand A corpus
# =============================================================================
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

tokenised = [tokenize(w) for w in hand_a_words]

print(f"Hand A words: {len(hand_a_words)}")

# =============================================================================
# STEP 1 — Observed profile per Layer-2 outer
# =============================================================================

# For each candidate glyph-unit, across ALL Hand A positions:
#   - fraction where it appears as the last glyph-unit of a word (TERMINAL)
#   - fraction as medial
#   - overall frequency in Layer-2 position (= last glyph-unit)
# Plus sub-class selection from N>=3 tokens (reuse SUFFIX-SUBCLASS-01 data)

total_word_count = len(tokenised)

# Per-glyph occurrence positions
occ_total = Counter()
occ_terminal = Counter()
occ_medial = Counter()
for t in tokenised:
    if not t:
        continue
    for i, g in enumerate(t):
        occ_total[g] += 1
        if i == len(t) - 1:
            occ_terminal[g] += 1
        else:
            occ_medial[g] += 1

# Outer-position frequency (last glyph-unit)
total_terminal_positions = sum(occ_terminal.values())

# Sub-class selection (N>=3 tokens)
valid = [t for t in tokenised if len(t) >= 3]
inners_valid = [t[-2] for t in valid]
outers_valid = [t[-1] for t in valid]
n_valid = len(valid)

count_V_inner = {o: 0 for o in LAYER2_OUTERS}
count_C_inner = {o: 0 for o in LAYER2_OUTERS}
total_V_inner = sum(1 for i in inners_valid if i in VOWEL_INNERS)
total_C_inner = sum(1 for i in inners_valid if i in CONSONANT_INNERS)

for i, o in zip(inners_valid, outers_valid):
    if o in LAYER2_OUTERS:
        if i in VOWEL_INNERS:
            count_V_inner[o] += 1
        elif i in CONSONANT_INNERS:
            count_C_inner[o] += 1

profiles = {}
for o in LAYER2_OUTERS:
    tot = occ_total[o]
    term = occ_terminal[o]
    med = occ_medial[o]
    pos_term = term / tot if tot else 0.0
    pos_med = med / tot if tot else 0.0
    layer2_freq = term / total_terminal_positions if total_terminal_positions else 0.0

    cV = count_V_inner[o]
    cC = count_C_inner[o]
    pV = cV / total_V_inner if total_V_inner else 0.0
    pC = cC / total_C_inner if total_C_inner else 0.0
    if pC > 0:
        diff_vc = pV / pC
    elif pV > 0:
        diff_vc = float("inf")
    else:
        diff_vc = 1.0

    profiles[o] = {
        "total_occurrences": tot,
        "terminal_fraction": round(pos_term, 4),
        "medial_fraction": round(pos_med, 4),
        "layer2_frequency": round(layer2_freq, 4),
        "count_V_inner": cV,
        "count_C_inner": cC,
        "p_V_inner": round(pV, 4),
        "p_C_inner": round(pC, 4),
        "diff_V_over_C": diff_vc if diff_vc != float("inf") else "inf",
    }

print("\n" + "="*78)
print("  STEP 1 — Observed profiles for Hand A Layer-2 outers")
print("="*78)
for o in LAYER2_OUTERS:
    p = profiles[o]
    print(f"\n  '{o}':")
    print(f"    total occurrences: {p['total_occurrences']}")
    print(f"    terminal fraction: {p['terminal_fraction']}  (medial: {p['medial_fraction']})")
    print(f"    Layer-2 frequency: {p['layer2_frequency']}  (fraction of word-terminal positions)")
    print(f"    V-inner / C-inner counts: {p['count_V_inner']} / {p['count_C_inner']}")
    print(f"    diff V/C: {p['diff_V_over_C']}")

# =============================================================================
# STEP 2 — Latin reference conventions (pre-specified)
# =============================================================================
LATIN = {
    "L1_Tironian_us": {
        "description": "Tironian -us (9-shape): word-terminal only, replaces declension ending. Stems of any type.",
        "position_rule": "terminal_only",   # requires term fraction >= 0.80
        "selection_rule": "any",            # no strong preference
        "frequency_range": (0.05, 0.25),    # 'very high'
    },
    "L2_macron_nasal": {
        "description": "Macron/overline (nasal suspension): mark over a vowel indicating omitted n/m. Strictly over vowels.",
        "position_rule": "flexible",        # terminal OR medial, mark itself is anywhere there is a vowel
        "selection_rule": "vowel_only",     # structurally impossible after a consonant
        "frequency_range": (0.05, 0.20),    # 'very high'
    },
    "L3_rum_suspension": {
        "description": "-rum / -orum / -arum: word-terminal, follows stem vowel (-Vrum).",
        "position_rule": "terminal_only",
        "selection_rule": "vowel_only",     # stem vowel required
        "frequency_range": (0.02, 0.15),    # 'moderate-to-high'
    },
    "L4_bus_dative": {
        "description": "-bus (dative/ablative plural): word-terminal, follows consonant or i-theme stems.",
        "position_rule": "terminal_only",
        "selection_rule": "consonant_preferring",
        "frequency_range": (0.01, 0.10),    # 'moderate'
    },
    "L5_lis_adjectival": {
        "description": "-alis / -ilis / -olis adjectival: word-terminal, follows stem vowel.",
        "position_rule": "terminal_only",
        "selection_rule": "vowel_preferring",
        "frequency_range": (0.01, 0.10),    # 'moderate'
    },
}

# =============================================================================
# STEP 3 — Score each outer against each Latin reference
# =============================================================================
def score_outer_vs_latin(outer_profile, latin_ref):
    # Positional match
    if latin_ref["position_rule"] == "terminal_only":
        pos = 1 if outer_profile["terminal_fraction"] >= 0.80 else 0
    else:  # flexible
        pos = 1 if outer_profile["terminal_fraction"] >= 0.40 else 0

    # Selectional match
    sel_rule = latin_ref["selection_rule"]
    diff = outer_profile["diff_V_over_C"]
    is_inf = (diff == "inf" or diff == float("inf"))
    if sel_rule == "any":
        sel = 1
    elif sel_rule == "vowel_only":
        # V-exclusive or strongly V-preferring (diff>=3 or inf)
        sel = 1 if (is_inf or (isinstance(diff, (int, float)) and diff >= 3.0)) else 0
    elif sel_rule == "vowel_preferring":
        sel = 1 if (is_inf or (isinstance(diff, (int, float)) and diff >= 2.0)) else 0
    elif sel_rule == "consonant_preferring":
        sel = 1 if (isinstance(diff, (int, float)) and diff <= 0.5 and diff > 0) else 0
    else:
        sel = 0

    # Frequency match
    fmin, fmax = latin_ref["frequency_range"]
    freq = outer_profile["layer2_frequency"]
    frq = 1 if (fmin <= freq <= fmax) else 0

    return pos, sel, frq

print("\n" + "="*78)
print("  STEP 3 — Scoring each Hand A outer vs each Latin reference")
print("="*78)

outer_results = {}
for o in LAYER2_OUTERS:
    print(f"\n  Outer '{o}':")
    ref_scores = {}
    strong_match_found = False
    best_latin = None
    best_sum = 0
    for latin_id, latin_ref in LATIN.items():
        pos, sel, frq = score_outer_vs_latin(profiles[o], latin_ref)
        total = pos + sel + frq
        match = (total >= 2)
        ref_scores[latin_id] = {"pos": pos, "sel": sel, "frq": frq, "total": total, "match": match}
        flag = "MATCH" if match else "no match"
        print(f"    vs {latin_id}: pos={pos} sel={sel} frq={frq}  total={total}/3  {flag}")
        if total > best_sum:
            best_sum = total
            best_latin = latin_id
        if match:
            strong_match_found = True
    outer_results[o] = {
        "profile": profiles[o],
        "reference_scores": ref_scores,
        "best_latin": best_latin,
        "best_match_score": best_sum,
        "strong_correspondence": strong_match_found,
    }
    print(f"    => strong_correspondence = {strong_match_found}  (best: {best_latin} at {best_sum}/3)")

# =============================================================================
# STEP 4 — Word-initial markers qo- and da- (descriptive, not decision-feeding)
# =============================================================================
print("\n" + "="*78)
print("  STEP 4 — Word-initial markers (descriptive)")
print("="*78)

# qo-
qo_total = sum(1 for t in tokenised if t and t[0] == "q" and len(t) >= 2 and t[1] == "o")
qo_word_count = qo_total  # simple: count words starting with q followed by o
# initial 'q' count
q_initial = sum(1 for t in tokenised if t and t[0] == "q")
# 'qo' anywhere
qo_anywhere = sum(1 for t in tokenised for i in range(len(t)-1) if t[i] == "q" and t[i+1] == "o")

# da-
da_initial = sum(1 for t in tokenised if t and t[0] == "d" and len(t) >= 2 and t[1] == "a")

print(f"\n  qo- word-initial (q followed by o at position 0): {qo_total}")
print(f"  q as first glyph (any): {q_initial}")
print(f"  qo anywhere in word:    {qo_anywhere}")
print(f"  qo word-initial rate:   {qo_total / q_initial:.4f} of all q-initial (reproduces 98.9% claim)" if q_initial else "")
print(f"  da- word-initial (d followed by a): {da_initial}  ({da_initial / total_word_count:.4f} of all words)")
print(f"\n  Comparison: Latin qu- word-initial frequency estimate ~5-10% of word-initial positions.")
qo_word_frac = qo_total / total_word_count if total_word_count else 0.0
print(f"  Hand A qo- word-initial: {qo_total}/{total_word_count} = {qo_word_frac:.4f} ({qo_word_frac*100:.2f}% of Hand A words)")

# =============================================================================
# LOCKED DECISION
# =============================================================================
print("\n" + "="*78)
print("  LOCKED DECISION")
print("="*78)
n_strong = sum(1 for o in LAYER2_OUTERS if outer_results[o]["strong_correspondence"])
print(f"\n  Outers with strong correspondence: {n_strong}/5")
for o in LAYER2_OUTERS:
    r = outer_results[o]
    s = "STRONG" if r["strong_correspondence"] else "no match"
    print(f"    {o}: {s} (best: {r['best_latin']} at {r['best_match_score']}/3)")

if n_strong >= 3:
    verdict = "CONFIRMED"
    rationale = f"{n_strong}/5 outers show strong correspondence (>=2/3 dimensions) to Latin scribal conventions; scribal-abbreviation hypothesis gains material support"
elif n_strong >= 1:
    verdict = "MARGINAL"
    rationale = f"{n_strong}/5 outers show strong correspondence; partial support for scribal-abbreviation candidate"
else:
    verdict = "REFUTED"
    rationale = "0/5 outers show strong correspondence; scribal-abbreviation candidate (a) weakens significantly"

print(f"\n  VERDICT: {verdict}")
print(f"  {rationale}")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "cappelli_match_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-17",
    "hypothesis": "H-BV-CAPPELLI-MATCH-01",
    "hand_a_word_count": total_word_count,
    "latin_references": {k: {
        "description": v["description"],
        "position_rule": v["position_rule"],
        "selection_rule": v["selection_rule"],
        "frequency_range": list(v["frequency_range"]),
    } for k, v in LATIN.items()},
    "outer_results": outer_results,
    "word_initial_markers": {
        "qo_initial_count": qo_total,
        "qo_initial_fraction_of_words": round(qo_word_frac, 4),
        "da_initial_count": da_initial,
        "da_initial_fraction_of_words": round(da_initial / total_word_count, 4) if total_word_count else 0.0,
    },
    "n_strong_correspondences": n_strong,
    "verdict": verdict,
    "rationale": rationale,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
