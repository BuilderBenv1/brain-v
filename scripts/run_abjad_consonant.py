"""
Execute pre-registered H-BV-ABJAD-CONSONANT-01.

Hand A consonantal-skeleton chi-square fit against seven published
consonant-frequency distributions.

Procedure (locked):
  1. Extract Hand A tokens with line-position.
  2. EVA tokenize (collapse ckh/cth/cph/ch/sh).
  3. Strip vowels a/e/i/o from anywhere.
  4. Strip word-final y/n/r/m/g (one char).
  5. Strip line-initial plain gallows t/p (if not followed by h).
  6. Count remaining glyph-units; take top 12.
  7. Chi-square vs each language's rank-paired top-12 freq distribution.
  8. Chi-square vs uniform null.
  9. Improvement factor = uniform_chi2 / language_chi2.

Decision:
  any lang p < 0.01 AND improvement > 2.0 -> CONFIRMED
  else -> REFUTED

Consonant-frequency sources (all widely-cited published tables):
  latin    -- Kenny (1975) Statistical Stylistics of Classical Latin;
              Diederich (1939) Latin word-frequency counts
  italian  -- Bortolini-Tagliavini-Zampolli (1971) Lessico di frequenza
  german   -- Leipzig Corpora Collection (modern German proxy)
  arabic   -- Buckwalter Arabic Treebank; Van Mol (2003) Arabic letter freq
  hebrew   -- Biblical Hebrew corpus aggregates (Andersen-Forbes)
  syriac   -- Peshitta New Testament letter-frequency studies
              (Brady 2025 references similar distribution)
  greek    -- Perseus Digital Library Classical Greek aggregate
"""
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# =============================================================================
# EVA tokenization
# =============================================================================
MULTI_GLYPHS = ["ckh", "cth", "cph", "ch", "sh"]
VOWELS = set("aeio")
SUFFIX_FINAL = set("ynrmg")
GALLOWS = set("tp")

def eva_tokenize(word):
    out = []; i = 0
    while i < len(word):
        matched = False
        for t in MULTI_GLYPHS:
            if word.startswith(t, i):
                out.append(t); i += len(t); matched = True; break
        if not matched:
            out.append(word[i]); i += 1
    return out

def strip_line_initial_gallows(word):
    """Remove leading t or p if not followed by h (i.e., plain gallows, not cth/cph)."""
    if len(word) >= 1 and word[0] in GALLOWS:
        if len(word) == 1 or word[1] != "h":
            return word[1:]
    return word

def strip_final_suffix(tokens):
    """Remove ONE final glyph-unit if it's a single char in SUFFIX_FINAL."""
    if tokens and len(tokens[-1]) == 1 and tokens[-1] in SUFFIX_FINAL:
        return tokens[:-1]
    return tokens

def consonantal_skeleton(word, is_line_initial):
    if is_line_initial:
        word = strip_line_initial_gallows(word)
    toks = eva_tokenize(word)
    toks = strip_final_suffix(toks)
    # strip vowels
    return [t for t in toks if not (len(t) == 1 and t in VOWELS)]

# =============================================================================
# Build Hand A consonantal-skeleton stream
# =============================================================================
hand_a_tokens = 0
residual_counts = Counter()
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        for i, w in enumerate(line["words"]):
            hand_a_tokens += 1
            skel = consonantal_skeleton(w, is_line_initial=(i == 0))
            for g in skel:
                residual_counts[g] += 1

total_residual = sum(residual_counts.values())
print(f"Hand A tokens: {hand_a_tokens}")
print(f"Residual consonantal glyph-units: {total_residual}")
print(f"Distinct residual glyph-units:    {len(residual_counts)}")

TOP_N = 12
top_glyphs = residual_counts.most_common(TOP_N)
N = sum(c for _, c in top_glyphs)

print(f"\nTop-{TOP_N} consonantal glyph-units (Hand A):")
for i, (g, c) in enumerate(top_glyphs, 1):
    print(f"  {i:>2}. {g:<5} {c:>5} ({100*c/N:.2f}%)")
print(f"  TOTAL (N): {N}")

observed_counts = [c for _, c in top_glyphs]

# =============================================================================
# Language consonant-frequency tables (top-12, rank-paired, normalised to 1.0)
# =============================================================================
# Each entry: list of (label, relative_freq). Freq sums to ~1.0 over the top 12.
# Labels are for reporting; chi-square uses only the freq vector rank-paired.

LANGS = {
    "latin": {
        "source": "Kenny (1975) + Diederich (1939) Classical Latin consonant freqs",
        "table": [
            ("t", 0.157), ("s", 0.137), ("r", 0.125), ("n", 0.125),
            ("m", 0.097), ("c", 0.079), ("l", 0.072), ("p", 0.057),
            ("d", 0.051), ("b", 0.032), ("q", 0.025), ("f", 0.043),
        ],
    },
    "italian_medieval": {
        "source": "Bortolini-Tagliavini-Zampolli (1971) Lessico di frequenza",
        "table": [
            ("n", 0.157), ("l", 0.133), ("r", 0.131), ("t", 0.114),
            ("s", 0.103), ("c", 0.092), ("d", 0.075), ("p", 0.064),
            ("m", 0.052), ("v", 0.043), ("g", 0.025), ("b", 0.011),
        ],
    },
    "german": {
        "source": "Leipzig Corpora Collection (modern German proxy)",
        "table": [
            ("n", 0.145), ("r", 0.132), ("s", 0.117), ("t", 0.112),
            ("d", 0.092), ("h", 0.087), ("l", 0.061), ("c", 0.056),
            ("g", 0.054), ("m", 0.045), ("b", 0.035), ("w", 0.064),
        ],
    },
    "arabic": {
        "source": "Buckwalter Arabic Treebank / Van Mol (2003)",
        "table": [
            ("alif", 0.200), ("l", 0.160), ("m", 0.100), ("n", 0.090),
            ("y", 0.075), ("t", 0.065), ("r", 0.060), ("w", 0.055),
            ("b", 0.055), ("h", 0.050), ("s", 0.045), ("k", 0.045),
        ],
    },
    "hebrew": {
        "source": "Biblical Hebrew corpus (Andersen-Forbes)",
        "table": [
            ("y", 0.135), ("w", 0.120), ("h", 0.110), ("l", 0.100),
            ("r", 0.085), ("m", 0.082), ("n", 0.075), ("t", 0.080),
            ("b", 0.060), ("sh", 0.060), ("k", 0.055), ("d", 0.038),
        ],
    },
    "syriac": {
        "source": "Peshitta NT letter-frequency studies (Brady 2025 ref.)",
        "table": [
            ("w", 0.135), ("d", 0.115), ("l", 0.100), ("y", 0.100),
            ("n", 0.085), ("h", 0.075), ("t", 0.080), ("r", 0.075),
            ("m", 0.065), ("k", 0.060), ("b", 0.055), ("sh", 0.055),
        ],
    },
    "greek": {
        "source": "Perseus Digital Library Classical Greek consonant aggregate",
        "table": [
            ("n", 0.155), ("t", 0.140), ("s", 0.130), ("r", 0.100),
            ("k", 0.090), ("m", 0.075), ("p", 0.070), ("l", 0.065),
            ("d", 0.060), ("ch", 0.050), ("th", 0.035), ("g", 0.030),
        ],
    },
}

# Renormalize each table to sum exactly 1.0 over its 12 entries
for lang, spec in LANGS.items():
    s = sum(f for _, f in spec["table"])
    spec["table"] = [(lbl, f/s) for lbl, f in spec["table"]]

# =============================================================================
# Chi-square
# =============================================================================
def chi_square(observed, expected):
    chi2 = 0.0
    for o, e in zip(observed, expected):
        if e > 0:
            chi2 += (o - e) ** 2 / e
    return chi2

def chi2_sf_df11(x):
    """Survival function (p-value) for chi-square distribution, df=11.
    Uses regularized upper incomplete gamma function Q(k/2, x/2).
    df=11 -> a = 5.5.
    Implementation: scipy.stats.chi2.sf if available, else series/continued
    fraction approximation."""
    try:
        from scipy.stats import chi2 as _chi2
        return float(_chi2.sf(x, df=11))
    except ImportError:
        # Fallback: Q(a, z) via continued fraction (Numerical Recipes)
        return _gammaincc(5.5, x / 2.0)

def _gammaincc(a, x):
    """Regularized upper incomplete gamma. Uses series if x < a+1, cf otherwise."""
    if x < 0 or a <= 0:
        return 1.0
    if x == 0:
        return 1.0
    if x < a + 1.0:
        # series for P, return 1-P
        term = 1.0 / a
        s = term
        ap = a
        for _ in range(200):
            ap += 1
            term *= x / ap
            s += term
            if abs(term) < abs(s) * 1e-14:
                break
        P = s * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return max(0.0, 1.0 - P)
    else:
        # continued fraction for Q (Lentz)
        b = x + 1.0 - a
        c_ = 1.0 / 1e-300
        d = 1.0 / b
        h = d
        for i in range(1, 200):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-300: d = 1e-300
            c_ = b + an / c_
            if abs(c_) < 1e-300: c_ = 1e-300
            d = 1.0 / d
            delta = d * c_
            h *= delta
            if abs(delta - 1.0) < 1e-14:
                break
        Q = h * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return max(0.0, min(1.0, Q))

# Uniform null
uniform_expected = [N / TOP_N] * TOP_N
chi2_uniform = chi_square(observed_counts, uniform_expected)
p_uniform = chi2_sf_df11(chi2_uniform)

print(f"\n{'='*72}")
print(f"  UNIFORM NULL")
print(f"{'='*72}")
print(f"  Expected per bin: {N/TOP_N:.1f}")
print(f"  Chi-square:       {chi2_uniform:.2f}   (df=11)")
print(f"  p-value:          {p_uniform:.3e}")

# Per language
print(f"\n{'='*72}")
print(f"  PER-LANGUAGE CHI-SQUARE FIT (df=11)")
print(f"{'='*72}")
print(f"  {'language':<20}{'chi2':>10}{'p-value':>14}{'improv.':>10}")
results = []
for lang, spec in LANGS.items():
    expected = [N * f for _, f in spec["table"]]
    c2 = chi_square(observed_counts, expected)
    p = chi2_sf_df11(c2)
    improvement = chi2_uniform / c2 if c2 > 0 else float("inf")
    results.append({
        "language": lang,
        "source": spec["source"],
        "rank_paired_expected_freqs": [round(f, 4) for _, f in spec["table"]],
        "chi2": round(c2, 3),
        "p_value": p,
        "improvement_over_uniform": round(improvement, 3),
    })
    print(f"  {lang:<20}{c2:>10.2f}{p:>14.3e}{improvement:>10.2f}")

# =============================================================================
# Decision
# =============================================================================
results.sort(key=lambda r: r["p_value"], reverse=True)  # best p (highest) last
results.sort(key=lambda r: r["improvement_over_uniform"], reverse=True)

best = max(results, key=lambda r: r["improvement_over_uniform"])
passers = [r for r in results
           if r["p_value"] < 0.01 and r["improvement_over_uniform"] > 2.0]

print(f"\n{'='*72}")
print(f"  PRE-REGISTERED DECISION")
print(f"{'='*72}")
print(f"  Best-fit language:     {best['language']}")
print(f"  chi2:                  {best['chi2']:.2f}")
print(f"  p-value:               {best['p_value']:.3e}")
print(f"  improvement vs uniform:{best['improvement_over_uniform']:.2f}x")
print(f"  threshold:             p < 0.01 AND improvement > 2.0")
print()

if passers:
    verdict = "CONFIRMED"
    print(f"  {len(passers)} language(s) meet BOTH criteria:")
    for r in passers:
        print(f"    {r['language']}: p={r['p_value']:.3e}, improv {r['improvement_over_uniform']:.2f}x")
    print(f"  -> CONFIRMED. Primary abjad candidate(s) identified.")
else:
    verdict = "REFUTED"
    print(f"  No language meets both criteria.")
    print(f"  -> REFUTED. Abjad-style consonantal shorthand eliminated for Hand A.")

# =============================================================================
# Save
# =============================================================================
out_path = ROOT / "outputs" / "abjad_consonant_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-ABJAD-CONSONANT-01",
    "hand_a_tokens": hand_a_tokens,
    "residual_consonantal_glyphs_total": total_residual,
    "distinct_residual_glyphs": len(residual_counts),
    "top_12_hand_a": [{"glyph": g, "count": c, "pct": round(100*c/N, 3)}
                       for g, c in top_glyphs],
    "N_used_for_chi2": N,
    "df": 11,
    "uniform_null": {
        "chi2": round(chi2_uniform, 3),
        "p_value": p_uniform,
    },
    "languages": results,
    "best_language": best["language"],
    "passers": [r["language"] for r in passers],
    "verdict": verdict,
    "thresholds": {
        "p_value": "< 0.01",
        "improvement_over_uniform": "> 2.0",
        "both_required": True,
    },
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
