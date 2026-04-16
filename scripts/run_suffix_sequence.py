"""
Execute pre-registered H-BV-SUFFIX-SEQUENCE-01.

Dual-tokenisation morphology test on Hand A:
  Tokenisation A: MULTI_GLYPHS + 'ol'
  Tokenisation B: MULTI_GLYPHS + 'ol' + 'qo'

Five-criterion test per tokenisation:
  C1 Layer-1 (inner) closure: top-10 inners cover >= 70%
  C2 Layer-2 (outer) closure: top-5 outers cover >= 70%
  C3 Productivity: mean distinct inners per productive stem >= 2.0
                   AND >= 40% of productive stems take >= 2 inners
  C4 Ordering: P(outer top5 | inner top10) / P(outer top5 | inner not top10)
               >= 2.0
  C5 Coverage: top-10 inners x top-5 outers termination set covers
               >= 60% of N>=3 tokens

Overall verdict:
  Both A and B CONFIRMED -> CONFIRMED morphology (robust)
  Only A CONFIRMED       -> CONFIRMED + qo is NOT a ligature
  Only B CONFIRMED       -> CONFIRMED + qo IS a ligature
  Neither                -> REFUTED (flat morphology)
  Mixed                  -> MARGINAL
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# Base MULTI_GLYPHS (from NOMENCLATOR-01 etc.)
BASE_MULTI = ["ckh", "cth", "cph", "ch", "sh"]

def make_tokenizer(extra):
    """Return tokenize function with longest-match-first rule."""
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

# =============================================================================
# Build Hand A token list
# =============================================================================
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

print(f"Hand A tokens: {len(hand_a_words)}")

# =============================================================================
# Five-criterion test
# =============================================================================
def test_morphology(tokenize, label):
    print(f"\n{'='*78}")
    print(f"  TOKENISATION {label}")
    print(f"{'='*78}")

    tokenised = [tokenize(w) for w in hand_a_words]
    # keep tokens with N >= 3 glyph-units
    valid = [t for t in tokenised if len(t) >= 3]
    n_valid = len(valid)
    print(f"  Tokens with >=3 glyph-units: {n_valid}")

    # Decompose
    stems = [tuple(t[:-2]) for t in valid]
    inners = [t[-2] for t in valid]
    outers = [t[-1] for t in valid]

    inner_counts = Counter(inners)
    outer_counts = Counter(outers)

    # C1 Layer-1 inner closure
    top10_inner = [g for g, _ in inner_counts.most_common(10)]
    inner_cov = sum(inner_counts[g] for g in top10_inner) / n_valid
    C1 = inner_cov >= 0.70
    print(f"\n  C1 Layer-1 inner closure:")
    print(f"    Top-10 inners: {top10_inner}")
    print(f"    Coverage: {inner_cov:.3f} (threshold >= 0.70)  {'PASS' if C1 else 'FAIL'}")

    # C2 Layer-2 outer closure
    top5_outer = [g for g, _ in outer_counts.most_common(5)]
    outer_cov = sum(outer_counts[g] for g in top5_outer) / n_valid
    C2 = outer_cov >= 0.70
    print(f"\n  C2 Layer-2 outer closure:")
    print(f"    Top-5 outers: {top5_outer}")
    print(f"    Coverage: {outer_cov:.3f} (threshold >= 0.70)  {'PASS' if C2 else 'FAIL'}")

    # C3 Productivity
    stem_to_inners = defaultdict(set)
    stem_to_count = Counter()
    for stem, inner in zip(stems, inners):
        stem_to_inners[stem].add(inner)
        stem_to_count[stem] += 1
    productive = [s for s, c in stem_to_count.items() if c >= 3]
    if productive:
        distinct_inners = [len(stem_to_inners[s]) for s in productive]
        mean_inners = sum(distinct_inners) / len(productive)
        pct_ge2 = sum(1 for d in distinct_inners if d >= 2) / len(productive)
    else:
        mean_inners = 0.0; pct_ge2 = 0.0
    C3 = mean_inners >= 2.0 and pct_ge2 >= 0.40
    print(f"\n  C3 Productivity:")
    print(f"    Productive stems (>=3 tokens): {len(productive)}")
    print(f"    Mean distinct inners per stem: {mean_inners:.3f} (threshold >= 2.0)")
    print(f"    Pct stems with >=2 inners:     {pct_ge2:.3f} (threshold >= 0.40)")
    print(f"    {'PASS' if C3 else 'FAIL'}")

    # C4 Ordering: P(outer top5 | inner top10) / P(outer top5 | inner not top10)
    top10_set = set(top10_inner)
    top5_set = set(top5_outer)
    n_in10 = sum(1 for i in inners if i in top10_set)
    n_out10 = sum(1 for i in inners if i not in top10_set)
    n_out5_given_in10 = sum(1 for i, o in zip(inners, outers)
                             if i in top10_set and o in top5_set)
    n_out5_given_out10 = sum(1 for i, o in zip(inners, outers)
                              if i not in top10_set and o in top5_set)
    p_a = n_out5_given_in10 / n_in10 if n_in10 else 0
    p_b = n_out5_given_out10 / n_out10 if n_out10 else 0
    ratio = p_a / p_b if p_b > 0 else float("inf")
    C4 = ratio >= 2.0 and p_a > 0 and p_b > 0 and p_a != 1.0
    print(f"\n  C4 Ordering:")
    print(f"    P(outer top5 | inner top10):    {p_a:.3f}  ({n_out5_given_in10}/{n_in10})")
    print(f"    P(outer top5 | inner not top10): {p_b:.3f}  ({n_out5_given_out10}/{n_out10})")
    print(f"    Ratio: {ratio:.2f} (threshold >= 2.0)  {'PASS' if C4 else 'FAIL'}")

    # C5 Coverage: tokens whose (inner, outer) are in (top10 × top5)
    in_set = sum(1 for i, o in zip(inners, outers)
                   if i in top10_set and o in top5_set)
    cov = in_set / n_valid
    C5 = cov >= 0.60
    print(f"\n  C5 Coverage:")
    print(f"    Tokens with (inner in top10) AND (outer in top5): {in_set}/{n_valid}")
    print(f"    Coverage: {cov:.3f} (threshold >= 0.60)  {'PASS' if C5 else 'FAIL'}")

    passes = [C1, C2, C3, C4, C5]
    n_pass = sum(passes)
    if n_pass == 5: verdict = "CONFIRMED"
    elif n_pass >= 3: verdict = "MARGINAL"
    else: verdict = "REFUTED"
    print(f"\n  TOKENISATION {label}: {n_pass}/5 criteria pass -> {verdict}")

    return {
        "label": label,
        "n_valid_tokens": n_valid,
        "C1_inner_closure": {"top10": top10_inner,
                              "coverage": round(inner_cov, 3),
                              "pass": C1},
        "C2_outer_closure": {"top5": top5_outer,
                              "coverage": round(outer_cov, 3),
                              "pass": C2},
        "C3_productivity": {"productive_stems": len(productive),
                             "mean_distinct_inners": round(mean_inners, 3),
                             "pct_ge2_inners": round(pct_ge2, 3),
                             "pass": C3},
        "C4_ordering": {"p_outer5_given_inner10": round(p_a, 4),
                         "p_outer5_given_not_inner10": round(p_b, 4),
                         "ratio": round(ratio, 2) if ratio != float("inf") else "inf",
                         "pass": C4},
        "C5_coverage": {"coverage": round(cov, 3), "pass": C5},
        "n_pass": n_pass,
        "verdict": verdict,
    }

# =============================================================================
# Run both tokenisations
# =============================================================================
tokenize_A = make_tokenizer(["ol"])
tokenize_B = make_tokenizer(["ol", "qo"])

result_A = test_morphology(tokenize_A, "A (ol only)")
result_B = test_morphology(tokenize_B, "B (ol + qo)")

# =============================================================================
# Overall decision
# =============================================================================
print("\n" + "="*78)
print("  OVERALL TWO-TOKENISATION VERDICT")
print("="*78)
vA = result_A["verdict"]; vB = result_B["verdict"]
print(f"  Tokenisation A (+ol):       {vA} ({result_A['n_pass']}/5)")
print(f"  Tokenisation B (+ol +qo):   {vB} ({result_B['n_pass']}/5)")

if vA == "CONFIRMED" and vB == "CONFIRMED":
    overall = "CONFIRMED"
    print(f"\n  -> CONFIRMED morphology. Two-layer structure robust to qo treatment.")
elif vA == "CONFIRMED" and vB != "CONFIRMED":
    overall = "CONFIRMED_QO_NOT_LIGATURE"
    print(f"\n  -> CONFIRMED morphology; qo is NOT a ligature. Adding qo to")
    print(f"     tokenisation disrupts the two-layer structure.")
elif vB == "CONFIRMED" and vA != "CONFIRMED":
    overall = "CONFIRMED_QO_IS_LIGATURE"
    print(f"\n  -> CONFIRMED morphology; qo IS a ligature. The two-layer")
    print(f"     structure only emerges when qo is atomised.")
elif vA == "REFUTED" and vB == "REFUTED":
    overall = "REFUTED"
    print(f"\n  -> REFUTED. Hand A has no ordered two-layer morphology under")
    print(f"     either tokenisation. Morphology is flat.")
else:
    overall = "MARGINAL"
    print(f"\n  -> MARGINAL. Mixed results; morphology is present but not cleanly")
    print(f"     two-layered under either tokenisation.")

# Save
out_path = ROOT / "outputs" / "suffix_sequence_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-SUFFIX-SEQUENCE-01",
    "tokenisation_A_ol_only": result_A,
    "tokenisation_B_ol_and_qo": result_B,
    "overall_verdict": overall,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
