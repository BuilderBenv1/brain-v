"""
Execute pre-registered H-BV-CARBON-SAMPLE-VALIDATION-01.

Apply Hand-A (SUFFIX-SUBCLASS-01) and Hand-B (HAND-B-SUBCLASS-01)
paradigms to the four carbon-dated reference folios: f8, f26, f47, f68.

Locked match rule per folio:
  HARD: n-exclusivity (count_C(n) must be 0)
  DIRECTIONAL: for outers with count_V + count_C >= 3, the larger-count
    sub-class must match expected direction

Expected paradigms:
  f8, f47 (Hand A): y cons-pref, n vowel-excl, r vowel-pref,
                    ol cons-pref, l vowel-pref
  f26 (Hand B):     y cons-pref, n vowel-excl, r vowel-pref,
                    ol UNCONSTRAINED, l vowel-pref
  f68 (Unassigned): descriptive only, compared against both paradigms

Overall verdict (Hand A+B folios only, f68 excluded):
  3/3 match -> CONFIRMED
  2/3 match -> MARGINAL
  <=1/3     -> CONCERNING
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
TOP5_OUTERS = ["y", "n", "r", "ol", "l"]

# Folio membership by prefix
FOLIO_GROUPS = {
    "f8":  ["f8r", "f8v"],
    "f26": ["f26r", "f26v"],
    "f47": ["f47r", "f47v"],
    "f68": ["f68r1", "f68r2", "f68r3", "f68v1", "f68v2", "f68v3"],
}

PARADIGMS = {
    "hand_A": {"y": "cons", "n": "vowel_excl", "r": "vowel", "ol": "cons", "l": "vowel"},
    "hand_B": {"y": "cons", "n": "vowel_excl", "r": "vowel", "ol": None,   "l": "vowel"},
}

FOLIO_ASSIGNMENT = {
    "f8": "hand_A",
    "f47": "hand_A",
    "f26": "hand_B",
    "f68": None,   # descriptive against both
}

# =============================================================================
# Per-folio token collection
# =============================================================================
def collect_folio_tokens(sides):
    out = []
    for f in CORPUS["folios"]:
        fid = f.get("folio_id") or f.get("id") or f.get("folio") or ""
        if fid in sides:
            for line in f["lines"]:
                out.extend(line["words"])
    return out

def analyse(words, label):
    tokenised = [tokenize(w) for w in words]
    valid = [t for t in tokenised if len(t) >= 3]
    inners = [t[-2] for t in valid]
    outers = [t[-1] for t in valid]

    # Build per-outer V/C counts
    counts = {}
    for o in TOP5_OUTERS:
        count_V = sum(1 for i, x in zip(inners, outers)
                      if i in VOWEL_INNERS and x == o)
        count_C = sum(1 for i, x in zip(inners, outers)
                      if i in CONSONANT_INNERS and x == o)
        p_V_total = sum(1 for i in inners if i in VOWEL_INNERS)
        p_C_total = sum(1 for i in inners if i in CONSONANT_INNERS)
        p_V = count_V / p_V_total if p_V_total else 0.0
        p_C = count_C / p_C_total if p_C_total else 0.0
        counts[o] = {"count_V": count_V, "count_C": count_C,
                     "p_V": round(p_V, 4), "p_C": round(p_C, 4)}
    return {
        "n_words": len(words),
        "n_valid_tokens": len(valid),
        "n_vowel_inner_tokens": sum(1 for i in inners if i in VOWEL_INNERS),
        "n_cons_inner_tokens": sum(1 for i in inners if i in CONSONANT_INNERS),
        "counts": counts,
    }

def check_match(folio_label, data, paradigm):
    """Return (match_bool, details) against the given paradigm."""
    counts = data["counts"]
    violations = []
    neutral = []
    matched = []

    # HARD n-exclusivity
    n_cons_count = counts["n"]["count_C"]
    if n_cons_count > 0:
        violations.append(f"n-exclusivity FAILED: {n_cons_count} n-attachments on consonant-class inner")
    else:
        matched.append("n-exclusivity holds (count_C(n) = 0)")

    # DIRECTIONAL checks
    for o in TOP5_OUTERS:
        if o == "n":
            continue  # handled above
        expected = paradigm.get(o)
        if expected is None:
            neutral.append(f"{o}: no expectation (unconstrained)")
            continue
        cv = counts[o]["count_V"]
        cc = counts[o]["count_C"]
        total = cv + cc
        if total < 3:
            neutral.append(f"{o}: count_V={cv}, count_C={cc} (total<3, neutral)")
            continue
        if cv == cc:
            neutral.append(f"{o}: count_V=count_C={cv} (tie, neutral)")
            continue
        # Which side is larger?
        larger = "vowel" if cv > cc else "cons"
        if larger == expected:
            matched.append(f"{o}: {larger}-preferring as expected (V={cv}, C={cc})")
        else:
            violations.append(f"{o} REVERSED: expected {expected}-preferring, observed {larger}-preferring (V={cv}, C={cc})")

    match = (len(violations) == 0)
    return match, {"matched": matched, "neutral": neutral, "violations": violations}

# =============================================================================
# Run per folio
# =============================================================================
results = {}
for folio, sides in FOLIO_GROUPS.items():
    words = collect_folio_tokens(sides)
    data = analyse(words, folio)
    assignment = FOLIO_ASSIGNMENT[folio]

    print(f"\n{'='*78}")
    print(f"  FOLIO {folio}   sides={sides}   assignment={assignment}")
    print(f"{'='*78}")
    print(f"  words: {data['n_words']};  N>=3 tokens: {data['n_valid_tokens']};  "
          f"vowel-inner: {data['n_vowel_inner_tokens']};  cons-inner: {data['n_cons_inner_tokens']}")

    print(f"\n  {'outer':<6} {'count_V':>8} {'count_C':>8} {'p_V':>8} {'p_C':>8}")
    for o in TOP5_OUTERS:
        c = data["counts"][o]
        print(f"  {o:<6} {c['count_V']:>8} {c['count_C']:>8} {c['p_V']:>8.4f} {c['p_C']:>8.4f}")

    # f68 descriptive against both
    if assignment is None:
        match_A, detail_A = check_match(folio, data, PARADIGMS["hand_A"])
        match_B, detail_B = check_match(folio, data, PARADIGMS["hand_B"])
        print(f"\n  [descriptive] Hand-A paradigm match: {match_A}")
        for v in detail_A["violations"]: print(f"    VIOLATION: {v}")
        for m in detail_A["matched"]: print(f"    OK: {m}")
        for n in detail_A["neutral"]: print(f"    neutral: {n}")
        print(f"\n  [descriptive] Hand-B paradigm match: {match_B}")
        for v in detail_B["violations"]: print(f"    VIOLATION: {v}")
        for m in detail_B["matched"]: print(f"    OK: {m}")
        for n in detail_B["neutral"]: print(f"    neutral: {n}")
        results[folio] = {
            "assignment": None, "data": data,
            "descriptive_hand_A": {"match": match_A, **detail_A},
            "descriptive_hand_B": {"match": match_B, **detail_B},
        }
    else:
        paradigm = PARADIGMS[assignment]
        match, detail = check_match(folio, data, paradigm)
        print(f"\n  Paradigm: {assignment}")
        for v in detail["violations"]: print(f"    VIOLATION: {v}")
        for m in detail["matched"]: print(f"    OK: {m}")
        for n in detail["neutral"]: print(f"    neutral: {n}")
        print(f"\n  FOLIO {folio} MATCH: {match}")
        results[folio] = {
            "assignment": assignment,
            "data": data,
            "match": match,
            **detail,
        }

# =============================================================================
# Overall decision (excludes f68)
# =============================================================================
print("\n" + "="*78)
print("  OVERALL DECISION (f8, f26, f47; f68 descriptive only)")
print("="*78)
ref_folios = ["f8", "f26", "f47"]
matches = sum(1 for f in ref_folios if results[f]["match"])
print(f"  Matches: {matches}/3")
for f in ref_folios:
    print(f"    {f} ({FOLIO_ASSIGNMENT[f]}): {'MATCH' if results[f]['match'] else 'NON-MATCH'}")

if matches == 3:
    verdict = "CONFIRMED"
    rationale = "All 3 reference folios match their predicted paradigm within power limits"
elif matches == 2:
    verdict = "MARGINAL"
    rationale = "2 of 3 reference folios match; one diverges — investigate which and why"
else:
    verdict = "CONCERNING"
    rationale = f"Only {matches}/3 match; paradigms may be section-driven rather than hand-driven"

print(f"\n  VERDICT: {verdict}")
print(f"  {rationale}")

# f68 descriptive report
print(f"\n  f68 (descriptive, not feeding decision):")
print(f"    Hand-A paradigm: {'match' if results['f68']['descriptive_hand_A']['match'] else 'NON-match'}")
print(f"    Hand-B paradigm: {'match' if results['f68']['descriptive_hand_B']['match'] else 'NON-match'}")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "carbon_sample_validation_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-17",
    "hypothesis": "H-BV-CARBON-SAMPLE-VALIDATION-01",
    "tokenisation": "A (MULTI_GLYPHS + 'ol')",
    "paradigms": PARADIGMS,
    "folio_assignment": FOLIO_ASSIGNMENT,
    "folio_groups": FOLIO_GROUPS,
    "results": results,
    "n_reference_matches": matches,
    "verdict": verdict,
    "rationale": rationale,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
