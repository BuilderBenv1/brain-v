"""Execute pre-registered H-BV-HAND-B-SUFFIX-SUBCLASS-01."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI = sorted(["ckh","cth","cph","ch","sh","ol"], key=lambda s: -len(s))
VOWEL_INNERS = {"i","e","o","a"}
CONSONANT_INNERS = {"d","k","ch","t","ckh","r"}  # Hand B-specific
TOP10 = VOWEL_INNERS | CONSONANT_INNERS
TOP5_OUTERS = ["y","n","r","l","ol"]


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
inners = [t[-2] for t in valid]
outers = [t[-1] for t in valid]

n_v = sum(1 for i in inners if i in VOWEL_INNERS)
n_c = sum(1 for i in inners if i in CONSONANT_INNERS)
n_other = sum(1 for i in inners if i not in TOP10)
print(f"Hand B N>=3 tokens: {len(valid)}")
print(f"  Vowel-inner tokens:    {n_v}")
print(f"  Consonant-inner tokens: {n_c}")
print(f"  Other-inner tokens:     {n_other}")


def cond_p_in_top5(predicate):
    n_match = sum(1 for i, o in zip(inners, outers) if predicate(i))
    n_outer5 = sum(1 for i, o in zip(inners, outers) if predicate(i) and o in TOP5_OUTERS)
    return n_outer5 / n_match if n_match else 0


p_v_t5 = cond_p_in_top5(lambda i: i in VOWEL_INNERS)
p_c_t5 = cond_p_in_top5(lambda i: i in CONSONANT_INNERS)
p_notv_t5 = cond_p_in_top5(lambda i: i not in VOWEL_INNERS)
p_notc_t5 = cond_p_in_top5(lambda i: i not in CONSONANT_INNERS)
p_combined_t5 = cond_p_in_top5(lambda i: i in TOP10)
p_outside_t5 = cond_p_in_top5(lambda i: i not in TOP10)

ratio_V = p_v_t5 / p_notv_t5 if p_notv_t5 else float("inf")
ratio_C = p_c_t5 / p_notc_t5 if p_notc_t5 else float("inf")
ratio_combined = p_combined_t5 / p_outside_t5 if p_outside_t5 else float("inf")

print(f"\nM1 ORDERING RATIOS:")
print(f"  ratio_VOWEL     = {ratio_V:.4f}  (P(top5|vowel) {p_v_t5:.4f} / P(top5|not vowel) {p_notv_t5:.4f})")
print(f"  ratio_CONSONANT = {ratio_C:.4f}  (P(top5|cons)  {p_c_t5:.4f} / P(top5|not cons) {p_notc_t5:.4f})")
print(f"  M1b combined    = {ratio_combined:.4f}  (sanity vs Hand B SUFFIX-SEQUENCE C4=1.14)")

print(f"\nM2 OUTER PREFERENCE TABLE:")
print(f"{'outer':<6}{'p_vowel':<12}{'p_cons':<12}{'diff(V/C)':<14}{'note'}")
m2_table = []
for o in TOP5_OUTERS:
    n_v_o = sum(1 for i, ot in zip(inners, outers) if i in VOWEL_INNERS and ot == o)
    n_c_o = sum(1 for i, ot in zip(inners, outers) if i in CONSONANT_INNERS and ot == o)
    p_vo = n_v_o / n_v if n_v else 0
    p_co = n_c_o / n_c if n_c else 0
    if p_vo > 0 and p_co > 0:
        diff = p_vo / p_co
        note = ""
    elif p_vo > 0:
        diff = float("inf"); note = "vowel-EXCLUSIVE"
    elif p_co > 0:
        diff = 0; note = "cons-EXCLUSIVE"
    else:
        diff = 1.0; note = "absent"
    diff_str = f"{diff:.3f}" if diff not in (float('inf'), 0) else ('inf' if diff==float('inf') else '0')
    print(f"{o:<6}{p_vo:<12.4f}{p_co:<12.4f}{diff_str:<14}{note}")
    m2_table.append({"outer": o, "p_vowel": round(p_vo,4), "p_cons": round(p_co,4),
                     "diff": diff_str, "note": note,
                     "n_vowel_outer": n_v_o, "n_cons_outer": n_c_o,
                     "ratio_ge_3x": (diff >= 3.0 or diff <= 1/3.0) if diff not in (float('inf'),0) else True})

n_outers_3x = sum(1 for r in m2_table if r["ratio_ge_3x"])

if max(ratio_V, ratio_C) >= 2.0:
    verdict = "CONFIRMED"
elif ratio_V < 1.5 and ratio_C < 1.5 and n_outers_3x == 0:
    verdict = "REFUTED"
else:
    verdict = "MARGINAL"

print(f"\n  M1 max ratio = {max(ratio_V, ratio_C):.4f} (threshold >= 2.0)")
print(f"  M2 outers with >=3x V/C differential: {n_outers_3x}/5")
print(f"  VERDICT: {verdict}")
print(f"\n  HAND A reference: MARGINAL (M1 ratios 0.985/1.055; M2 5/5 outers >=3x; n vowel-exclusive 0/2240)")

out = {"generated": "2026-04-18", "hypothesis": "H-BV-HAND-B-SUFFIX-SUBCLASS-01",
       "n_valid_tokens": len(valid), "n_vowel_inner": n_v, "n_consonant_inner": n_c,
       "M1_ratio_VOWEL": round(ratio_V,4), "M1_ratio_CONSONANT": round(ratio_C,4),
       "M1b_combined": round(ratio_combined,4),
       "M2_outer_preference": m2_table,
       "n_outers_with_3x_differential": n_outers_3x,
       "verdict": verdict,
       "hand_a_reference": "MARGINAL: M1 0.985/1.055; M2 5/5 outers >=3x; n vowel-exclusive 0/2240"}
out_path = ROOT / "outputs" / "hand_b_suffix_subclass_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
