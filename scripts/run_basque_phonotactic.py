"""
Execute pre-registered H-BV-BASQUE-PHONOTACTIC-01.

Strip Layer-2 outers and leading qo- from Hand A tokens; test 5
Basque-compatible phonotactic properties on the remaining stems.

Locked decision: >=3/5 properties PASS = CONFIRMED; 1-2 = MARGINAL; 0 = REFUTED.
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
LAYER2_OUTERS = {"y", "n", "r", "ol", "l"}

# Consonant-like: everything single-char that's not a vowel-like, plus ligatures
def is_vowel(g):
    return g in VOWEL_LIKE

def is_consonant(g):
    # treat ligatures ch, sh, ckh, cth, cph, ol as consonants (single consonant-like units)
    # single-char non-vowels as consonants
    if g in VOWEL_LIKE:
        return False
    return True

# =============================================================================
# Hand A tokens, N>=3 glyph-units, stripped
# =============================================================================
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

tokenised = [tokenize(w) for w in hand_a_words]
valid = [t for t in tokenised if len(t) >= 3]

def strip_token(t):
    """Strip leading qo if present, then trailing Layer-2 outer if present."""
    stem = list(t)
    # leading qo
    if len(stem) >= 2 and stem[0] == "q" and stem[1] == "o":
        stem = stem[2:]
    # trailing Layer-2 outer
    if stem and stem[-1] in LAYER2_OUTERS:
        stem = stem[:-1]
    return stem

stripped = [strip_token(t) for t in valid]
# Discard stems that are now empty
stripped = [s for s in stripped if s]
n_stripped = len(stripped)
print(f"Hand A N>=3 tokens: {len(valid)}")
print(f"Stripped stems (non-empty after stripping): {n_stripped}")

# =============================================================================
# P1 — Initial-r rarity
# =============================================================================
r_initial = sum(1 for s in stripped if s[0] == "r")
r_initial_frac = r_initial / n_stripped
P1_pass = r_initial_frac <= 0.05
print(f"\nP1 Initial-r: {r_initial}/{n_stripped} = {r_initial_frac:.4f}  "
      f"(threshold <=0.05)  {'PASS' if P1_pass else 'FAIL'}")

# =============================================================================
# P2 — 4-vowel balance (each of i, e, o, a appears in >=5% of stems)
# =============================================================================
vowel_presence = {v: 0 for v in VOWEL_LIKE}
for s in stripped:
    present = set(s) & VOWEL_LIKE
    for v in present:
        vowel_presence[v] += 1
vowel_pres_frac = {v: c / n_stripped for v, c in vowel_presence.items()}
P2_pass = all(f >= 0.05 for f in vowel_pres_frac.values())
print(f"\nP2 4-vowel balance:")
for v in ["i", "e", "o", "a"]:
    f = vowel_pres_frac[v]
    print(f"   {v}: {vowel_presence[v]}/{n_stripped} = {f:.4f}  {'>= 0.05 OK' if f >= 0.05 else '< 0.05 FAIL'}")
print(f"   P2 {'PASS' if P2_pass else 'FAIL'}")

# =============================================================================
# P3 — Vowel-consonant ratio (35-45%)
# =============================================================================
n_vowels = sum(1 for s in stripped for g in s if is_vowel(g))
n_consonants = sum(1 for s in stripped for g in s if is_consonant(g))
n_total = n_vowels + n_consonants
vc_ratio = n_vowels / n_total if n_total else 0
P3_pass = 0.35 <= vc_ratio <= 0.45
print(f"\nP3 V:C ratio: {n_vowels}/{n_total} = {vc_ratio:.4f}  "
      f"(threshold [0.35, 0.45])  {'PASS' if P3_pass else 'FAIL'}")

# =============================================================================
# P4 — Vowel-final preference (>=40%)
# =============================================================================
vfinal = sum(1 for s in stripped if is_vowel(s[-1]))
vfinal_frac = vfinal / n_stripped
P4_pass = vfinal_frac >= 0.40
print(f"\nP4 Vowel-final: {vfinal}/{n_stripped} = {vfinal_frac:.4f}  "
      f"(threshold >=0.40)  {'PASS' if P4_pass else 'FAIL'}")

# =============================================================================
# P5 — Consonant-cluster density (<=25%)
# =============================================================================
has_cluster = 0
for s in stripped:
    # check for 2+ consecutive consonants (ligatures count as 1 consonant unit)
    for i in range(len(s) - 1):
        if is_consonant(s[i]) and is_consonant(s[i+1]):
            has_cluster += 1
            break
cluster_frac = has_cluster / n_stripped
P5_pass = cluster_frac <= 0.25
print(f"\nP5 Consonant-cluster density: {has_cluster}/{n_stripped} = {cluster_frac:.4f}  "
      f"(threshold <=0.25)  {'PASS' if P5_pass else 'FAIL'}")

# =============================================================================
# LOCKED DECISION
# =============================================================================
print("\n" + "="*78)
print("  LOCKED DECISION")
print("="*78)
passes = [P1_pass, P2_pass, P3_pass, P4_pass, P5_pass]
n_pass = sum(passes)
print(f"  Properties passing: {n_pass}/5")
print(f"    P1 Initial-r rarity:         {'PASS' if P1_pass else 'FAIL'}")
print(f"    P2 4-vowel balance:          {'PASS' if P2_pass else 'FAIL'}")
print(f"    P3 V:C ratio 35-45%:         {'PASS' if P3_pass else 'FAIL'}")
print(f"    P4 Vowel-final >=40%:        {'PASS' if P4_pass else 'FAIL'}")
print(f"    P5 Consonant-cluster <=25%:  {'PASS' if P5_pass else 'FAIL'}")

if n_pass >= 3:
    verdict = "CONFIRMED"
    rationale = f"{n_pass}/5 phonotactic properties match Basque expectations; stems are Basque-compatible"
elif n_pass >= 1:
    verdict = "MARGINAL"
    rationale = f"{n_pass}/5 match; partial compatibility"
else:
    verdict = "REFUTED"
    rationale = "0/5 match; Basque-like hypothesis fails at phonotactic level"

print(f"\n  VERDICT: {verdict}")
print(f"  {rationale}")

# Diagnostic
print(f"\n  DIAGNOSTIC:")
print(f"    Top-10 stripped stem glyph-units (for reference):")
stem_start_counts = Counter(s[0] for s in stripped)
for g, c in stem_start_counts.most_common(10):
    print(f"      starts with '{g}': {c} ({c/n_stripped:.3f})")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "basque_phonotactic_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-17",
    "hypothesis": "H-BV-BASQUE-PHONOTACTIC-01",
    "n_valid_tokens": len(valid),
    "n_stripped_stems": n_stripped,
    "P1_initial_r": {"count": r_initial, "fraction": round(r_initial_frac, 4), "threshold": "<=0.05", "pass": P1_pass},
    "P2_vowel_balance": {
        "per_vowel_presence_fraction": {v: round(f, 4) for v, f in vowel_pres_frac.items()},
        "threshold": "each >=0.05", "pass": P2_pass,
    },
    "P3_vc_ratio": {"vowels": n_vowels, "consonants": n_consonants, "ratio": round(vc_ratio, 4),
                    "threshold": "[0.35, 0.45]", "pass": P3_pass},
    "P4_vowel_final": {"count": vfinal, "fraction": round(vfinal_frac, 4), "threshold": ">=0.40", "pass": P4_pass},
    "P5_cluster_density": {"count": has_cluster, "fraction": round(cluster_frac, 4), "threshold": "<=0.25", "pass": P5_pass},
    "n_pass": n_pass,
    "verdict": verdict,
    "rationale": rationale,
    "diagnostic_stem_initial_top10": stem_start_counts.most_common(10),
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
