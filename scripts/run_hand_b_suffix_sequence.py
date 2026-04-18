"""
Execute pre-registered H-BV-HAND-B-SUFFIX-SEQUENCE-01.

Identical methodology to run_suffix_sequence.py with corpus filter
changed from currier_language=='A' to 'B'.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

BASE_MULTI = ["ckh", "cth", "cph", "ch", "sh"]


def make_tokenizer(extra):
    multi = sorted(BASE_MULTI + list(extra), key=lambda s: -len(s))
    def tokenize(word):
        out = []; i = 0
        while i < len(word):
            matched = False
            for t in multi:
                if word.startswith(t, i):
                    out.append(t); i += len(t); matched = True; break
            if not matched:
                out.append(word[i]); i += 1
        return out
    return tokenize


hand_b_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "B":
        continue
    for line in f["lines"]:
        hand_b_words.extend(line["words"])
print(f"Hand B tokens: {len(hand_b_words)}")


def test_morphology(tokenize, label):
    print(f"\n{'='*78}\n  TOKENISATION {label}\n{'='*78}")
    tokenised = [tokenize(w) for w in hand_b_words]
    valid = [t for t in tokenised if len(t) >= 3]
    n_valid = len(valid)
    print(f"  N>=3 tokens: {n_valid}")
    stems = [tuple(t[:-2]) for t in valid]
    inners = [t[-2] for t in valid]
    outers = [t[-1] for t in valid]
    inner_counts = Counter(inners); outer_counts = Counter(outers)
    top10_inner = [g for g, _ in inner_counts.most_common(10)]
    inner_cov = sum(inner_counts[g] for g in top10_inner) / n_valid
    C1 = inner_cov >= 0.70
    print(f"  C1 inner closure: top10={top10_inner} cov={inner_cov:.3f} {'PASS' if C1 else 'FAIL'}")
    top5_outer = [g for g, _ in outer_counts.most_common(5)]
    outer_cov = sum(outer_counts[g] for g in top5_outer) / n_valid
    C2 = outer_cov >= 0.70
    print(f"  C2 outer closure: top5={top5_outer} cov={outer_cov:.3f} {'PASS' if C2 else 'FAIL'}")
    stem_to_inners = defaultdict(set)
    stem_to_count = Counter()
    for stem, inner in zip(stems, inners):
        stem_to_inners[stem].add(inner)
        stem_to_count[stem] += 1
    productive = [s for s, c in stem_to_count.items() if c >= 3]
    if productive:
        distinct = [len(stem_to_inners[s]) for s in productive]
        mean_in = sum(distinct) / len(productive)
        pct_ge2 = sum(1 for d in distinct if d >= 2) / len(productive)
    else:
        mean_in = 0; pct_ge2 = 0
    C3 = mean_in >= 2.0 and pct_ge2 >= 0.40
    print(f"  C3 productivity: n_prod={len(productive)} mean_inners={mean_in:.3f} pct_ge2={pct_ge2:.3f} {'PASS' if C3 else 'FAIL'}")
    top10_set = set(top10_inner); top5_set = set(top5_outer)
    n_in10 = sum(1 for i in inners if i in top10_set)
    n_out10 = sum(1 for i in inners if i not in top10_set)
    n_o5_in10 = sum(1 for i,o in zip(inners,outers) if i in top10_set and o in top5_set)
    n_o5_out10 = sum(1 for i,o in zip(inners,outers) if i not in top10_set and o in top5_set)
    p_a = n_o5_in10 / n_in10 if n_in10 else 0
    p_b = n_o5_out10 / n_out10 if n_out10 else 0
    ratio = p_a/p_b if p_b > 0 else float('inf')
    C4 = ratio >= 2.0 and p_a > 0 and p_b > 0 and p_a != 1.0
    print(f"  C4 ordering: p_a={p_a:.3f} p_b={p_b:.3f} ratio={ratio:.2f} {'PASS' if C4 else 'FAIL'}")
    in_set = sum(1 for i,o in zip(inners,outers) if i in top10_set and o in top5_set)
    cov = in_set/n_valid
    C5 = cov >= 0.60
    print(f"  C5 coverage: {in_set}/{n_valid} = {cov:.3f} {'PASS' if C5 else 'FAIL'}")
    n_pass = sum([C1,C2,C3,C4,C5])
    verdict = 'CONFIRMED' if n_pass==5 else ('MARGINAL' if n_pass>=3 else 'REFUTED')
    print(f"  -> {n_pass}/5 {verdict}")
    return {"label": label, "n_valid": n_valid,
            "C1": {"top10": top10_inner, "cov": round(inner_cov,3), "pass": C1},
            "C2": {"top5": top5_outer, "cov": round(outer_cov,3), "pass": C2},
            "C3": {"n_prod": len(productive), "mean_inners": round(mean_in,3), "pct_ge2": round(pct_ge2,3), "pass": C3},
            "C4": {"p_a": round(p_a,4), "p_b": round(p_b,4), "ratio": round(ratio,2) if ratio != float('inf') else 'inf', "pass": C4},
            "C5": {"cov": round(cov,3), "pass": C5},
            "n_pass": n_pass, "verdict": verdict}


tA = make_tokenizer(["ol"])
tB = make_tokenizer(["ol", "qo"])
rA = test_morphology(tA, "A (ol only)")
rB = test_morphology(tB, "B (ol+qo)")

vA, vB = rA['verdict'], rB['verdict']
print(f"\n  Hand B Tokenisation A: {vA} ({rA['n_pass']}/5)")
print(f"  Hand B Tokenisation B: {vB} ({rB['n_pass']}/5)")
if vA == 'CONFIRMED' and vB == 'CONFIRMED': overall='CONFIRMED'
elif vA == 'CONFIRMED' and vB != 'CONFIRMED': overall='CONFIRMED_QO_NOT_LIGATURE'
elif vB == 'CONFIRMED' and vA != 'CONFIRMED': overall='CONFIRMED_QO_IS_LIGATURE'
elif vA == 'REFUTED' and vB == 'REFUTED': overall='REFUTED'
else: overall='MARGINAL'
print(f"  OVERALL: {overall}")

print(f"\n  HAND A vs HAND B comparison (from prior SUFFIX-SEQUENCE-01):")
print(f"    Hand A: 4/5 MARGINAL (only C4 ordering failed at 1.12)")
print(f"    Hand B: {rA['n_pass']}/5 {vA} (Tokenisation A)")

out = {"generated": "2026-04-18", "hypothesis": "H-BV-HAND-B-SUFFIX-SEQUENCE-01",
       "hand_b_tokenisation_A_ol": rA, "hand_b_tokenisation_B_ol_qo": rB,
       "hand_b_overall_verdict": overall,
       "hand_a_reference_verdict": "MARGINAL 4/5 (C4 ordering failed at ratio 1.12)"}
out_path = ROOT / "outputs" / "hand_b_suffix_sequence_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
