"""
Execute pre-registered H-BV-TP-ALTERNATION-01.

Four-part test of whether t vs p gallows choice on Hand A paragraph-
initial tokens encodes structured information:
  A) section-type predictor
  B) quire-position predictor
  C) within-folio alternation/clustering (runs test)
  D) stem-conditional preference (top-10 stripped stems)

Decision: per-test pass at p<0.01 AND Cramer's V>=0.20 (or |z|>=2.58
for test C). Report all four; interpret jointly.
"""
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# =============================================================================
# Paragraph detection and metadata
# =============================================================================
def starts_gallows(w):
    if not w or w[0] not in "tp": return False
    return len(w) == 1 or w[1] != "h"

def strip_gallows(tok):
    if len(tok) >= 3 and tok[:3] in ("cth", "ckh", "cph"):
        return tok[3:]
    if tok and tok[0] in "tp":
        return tok[1:]
    return tok

paragraphs = []  # list of dicts
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    fid = f["folio"]; quire = f["quire"]; section = f["section"]
    current_para_tokens = []
    paragraph_idx_in_folio = 0
    for line in f["lines"]:
        ws = line["words"]
        if not ws: continue
        if starts_gallows(ws[0]) and current_para_tokens:
            # Flush previous paragraph
            if current_para_tokens:
                paragraphs.append({
                    "tokens": current_para_tokens, "folio": fid,
                    "quire": quire, "section": section,
                    "index_in_folio": paragraph_idx_in_folio,
                })
                paragraph_idx_in_folio += 1
            current_para_tokens = []
        current_para_tokens.extend(ws)
    if current_para_tokens:
        paragraphs.append({
            "tokens": current_para_tokens, "folio": fid,
            "quire": quire, "section": section,
            "index_in_folio": paragraph_idx_in_folio,
        })

paragraphs = [p for p in paragraphs if len(p["tokens"]) >= 3]
print(f"Hand A paragraphs detected: {len(paragraphs)}")

# =============================================================================
# Filter: keep only plain-gallows-initial (t or p, not cth/ckh/cph)
# =============================================================================
def first_gallows_letter(tok):
    """Return 't' or 'p' if plain gallows initial; None otherwise."""
    if not tok: return None
    if len(tok) >= 3 and tok[:3] in ("cth", "ckh", "cph"):
        return None  # benched gallows, excluded
    if tok[0] == "t" and (len(tok) == 1 or tok[1] != "h"):
        return "t"
    if tok[0] == "p" and (len(tok) == 1 or tok[1] != "h"):
        return "p"
    return None

kept = []
for p in paragraphs:
    g = first_gallows_letter(p["tokens"][0])
    if g is not None:
        p["gallows"] = g
        p["stripped"] = strip_gallows(p["tokens"][0])
        kept.append(p)
print(f"Retained (plain-gallows initial): {len(kept)}")

# Global baseline
t_count = sum(1 for p in kept if p["gallows"] == "t")
p_count = sum(1 for p in kept if p["gallows"] == "p")
tot = t_count + p_count
print(f"Global t-rate: {t_count}/{tot} = {t_count/tot:.3f}; p-rate: {p_count/tot:.3f}")

# =============================================================================
# Chi-square helpers (no scipy dependency)
# =============================================================================
def chi_square_contingency(table):
    """table: 2D list of int counts (rows x cols). Returns (chi2, df, cramers_v)."""
    rows = len(table); cols = len(table[0])
    total = sum(sum(r) for r in table)
    if total == 0:
        return 0.0, 0, 0.0
    row_sums = [sum(r) for r in table]
    col_sums = [sum(table[r][c] for r in range(rows)) for c in range(cols)]
    chi2 = 0.0
    for r in range(rows):
        for c in range(cols):
            obs = table[r][c]
            exp = row_sums[r] * col_sums[c] / total
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp
    df = (rows - 1) * (cols - 1)
    min_dim = min(rows, cols) - 1
    cramers_v = math.sqrt(chi2 / (total * min_dim)) if total and min_dim > 0 else 0.0
    return chi2, df, cramers_v

def chi2_sf(x, df):
    """Survival function (upper tail p-value)."""
    if df <= 0 or x <= 0: return 1.0
    # Use Q(df/2, x/2) regularized upper incomplete gamma
    a = df / 2.0; z = x / 2.0
    if z < a + 1.0:
        # series for P
        term = 1.0 / a; s = term; ap = a
        for _ in range(500):
            ap += 1; term *= z / ap; s += term
            if abs(term) < abs(s) * 1e-14: break
        P = s * math.exp(-z + a * math.log(z) - math.lgamma(a))
        return max(0.0, 1.0 - P)
    # continued fraction for Q
    b = z + 1.0 - a
    c_ = 1.0 / 1e-300
    d = 1.0 / b
    h = d
    for i in range(1, 500):
        an = -i * (i - a); b += 2.0
        d = an * d + b
        if abs(d) < 1e-300: d = 1e-300
        c_ = b + an / c_
        if abs(c_) < 1e-300: c_ = 1e-300
        d = 1.0 / d
        delta = d * c_; h *= delta
        if abs(delta - 1.0) < 1e-14: break
    Q = h * math.exp(-z + a * math.log(z) - math.lgamma(a))
    return max(0.0, min(1.0, Q))

# =============================================================================
# TEST A — Section predictor
# =============================================================================
print("\n" + "="*78)
print("  TEST A — Section predictor")
print("="*78)
section_tp = defaultdict(lambda: [0, 0])  # section -> [t, p]
for p in kept:
    idx = 0 if p["gallows"] == "t" else 1
    section_tp[p["section"]][idx] += 1

# Filter sections with >= 10 retained paragraphs
valid_secs = [s for s, tp in section_tp.items() if sum(tp) >= 10]
print(f"  Sections with >=10 paragraphs: {valid_secs}")
print(f"  {'section':<20}{'t':>6}{'p':>6}{'t%':>7}")
for s in valid_secs:
    t, p = section_tp[s]
    print(f"  {s:<20}{t:>6}{p:>6}{100*t/(t+p):>6.1f}%")

if len(valid_secs) >= 2:
    table = [[section_tp[s][0] for s in valid_secs],
              [section_tp[s][1] for s in valid_secs]]
    chi2, df, cv = chi_square_contingency(table)
    pA = chi2_sf(chi2, df)
    print(f"  chi2={chi2:.3f}  df={df}  p={pA:.4f}  Cramer's V={cv:.3f}")
    testA_pass = pA < 0.01 and cv >= 0.20
else:
    chi2 = df = cv = 0.0; pA = 1.0
    testA_pass = False
print(f"  TEST A: {'PASS' if testA_pass else 'fail'}")

# =============================================================================
# TEST B — Quire predictor
# =============================================================================
print("\n" + "="*78)
print("  TEST B — Quire predictor")
print("="*78)
quire_tp = defaultdict(lambda: [0, 0])
for p in kept:
    idx = 0 if p["gallows"] == "t" else 1
    quire_tp[p["quire"]][idx] += 1
valid_qs = [q for q, tp in quire_tp.items() if sum(tp) >= 10]
print(f"  Quires with >=10 paragraphs: {valid_qs}")
print(f"  {'quire':<8}{'t':>6}{'p':>6}{'t%':>7}")
for q in sorted(valid_qs):
    t, p = quire_tp[q]
    print(f"  {q:<8}{t:>6}{p:>6}{100*t/(t+p):>6.1f}%")

if len(valid_qs) >= 2:
    table = [[quire_tp[q][0] for q in valid_qs],
              [quire_tp[q][1] for q in valid_qs]]
    chi2B, dfB, cvB = chi_square_contingency(table)
    pB = chi2_sf(chi2B, dfB)
    print(f"  chi2={chi2B:.3f}  df={dfB}  p={pB:.4f}  Cramer's V={cvB:.3f}")
    testB_pass = pB < 0.01 and cvB >= 0.20
else:
    chi2B = dfB = cvB = 0.0; pB = 1.0
    testB_pass = False
print(f"  TEST B: {'PASS' if testB_pass else 'fail'}")

# =============================================================================
# TEST C — Within-folio alternation (runs test)
# =============================================================================
print("\n" + "="*78)
print("  TEST C — Within-folio alternation (runs test)")
print("="*78)
folio_sequences = defaultdict(list)
for p in kept:
    folio_sequences[p["folio"]].append(p["gallows"])

# Filter folios with >=3 gallows paragraphs
valid_folios = [f for f, seq in folio_sequences.items() if len(seq) >= 3]
print(f"  Folios with >=3 gallows-paragraphs: {len(valid_folios)}")

def runs_test(seq):
    """Wald-Wolfowitz runs test. Returns (runs_observed, n1, n2, expected, z)."""
    n1 = seq.count("t"); n2 = seq.count("p")
    n = n1 + n2
    if n1 == 0 or n2 == 0 or n < 2:
        return None
    runs = 1
    for i in range(1, n):
        if seq[i] != seq[i-1]:
            runs += 1
    expected = 2 * n1 * n2 / n + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n) / (n * n * (n - 1))
    if var <= 0: return None
    z = (runs - expected) / math.sqrt(var)
    return runs, n1, n2, expected, z

z_scores = []
for f in valid_folios:
    r = runs_test(folio_sequences[f])
    if r is not None:
        z_scores.append(r[4])

if z_scores:
    mean_z = statistics.mean(z_scores)
    n_folios = len(z_scores)
    # Aggregate z: sum of z / sqrt(n) — Stouffer's method for combining independent z
    stouffer_z = sum(z_scores) / math.sqrt(n_folios)
    print(f"  n folios with valid runs test: {n_folios}")
    print(f"  Mean per-folio z: {mean_z:+.3f}")
    print(f"  Stouffer combined z: {stouffer_z:+.3f}")
    print(f"    (positive = alternation, negative = clustering)")
    testC_pass = abs(stouffer_z) >= 2.58
else:
    stouffer_z = 0.0; mean_z = 0.0; n_folios = 0
    testC_pass = False
print(f"  TEST C: {'PASS' if testC_pass else 'fail'} (threshold |z|>=2.58)")

# =============================================================================
# TEST D — Stem-conditional preference
# =============================================================================
print("\n" + "="*78)
print("  TEST D — Stem-conditional t/p preference (top-10 recurring stems)")
print("="*78)
stem_tp = defaultdict(lambda: [0, 0])
for p in kept:
    idx = 0 if p["gallows"] == "t" else 1
    stem_tp[p["stripped"]][idx] += 1
top10 = sorted(stem_tp.items(), key=lambda x: -sum(x[1]))[:10]
valid_stems = [s for s, tp in top10 if sum(tp) >= 3]
print(f"  Top-10 (>=3 occurrences) stems: {len(valid_stems)}")
print(f"  {'stem':<14}{'t':>6}{'p':>6}{'t%':>7}")
for stem, tp in top10:
    tot_ = sum(tp)
    if tot_ < 3: continue
    print(f"  {stem:<14}{tp[0]:>6}{tp[1]:>6}{100*tp[0]/tot_:>6.1f}%")

if len(valid_stems) >= 2:
    table = [[stem_tp[s][0] for s in valid_stems],
              [stem_tp[s][1] for s in valid_stems]]
    chi2D, dfD, cvD = chi_square_contingency(table)
    pD = chi2_sf(chi2D, dfD)
    print(f"  chi2={chi2D:.3f}  df={dfD}  p={pD:.4f}  Cramer's V={cvD:.3f}")
    testD_pass = pD < 0.01 and cvD >= 0.20
else:
    chi2D = dfD = cvD = 0.0; pD = 1.0
    testD_pass = False
print(f"  TEST D: {'PASS' if testD_pass else 'fail'}")

# =============================================================================
# Interpretation
# =============================================================================
print("\n" + "="*78)
print("  INTERPRETATION")
print("="*78)
print(f"  A section-predictor:     {'PASS' if testA_pass else 'fail'}")
print(f"  B quire-predictor:       {'PASS' if testB_pass else 'fail'}")
print(f"  C within-folio runs:     {'PASS' if testC_pass else 'fail'}")
print(f"  D stem-conditional:      {'PASS' if testD_pass else 'fail'}")
n_pass = sum([testA_pass, testB_pass, testC_pass, testD_pass])

interpretations = []
if testA_pass:
    interpretations.append("Hand A encodes a binary CONTENT ATTRIBUTE at section level")
if testB_pass:
    interpretations.append("Hand A shows SCRIBAL-SESSION STRUCTURE (supports Timm)")
if testC_pass:
    if stouffer_z > 0:
        interpretations.append("Hand A has LITURGICAL/ANTIPHON-STYLE alternation")
    else:
        interpretations.append("Hand A has BLOCK-STRUCTURED paragraph grouping (t-block / p-block)")
if testD_pass:
    interpretations.append("t/p is STEM-LINKED (lexical-phonological constraint)")

if n_pass == 0:
    interpretations.append("t/p alternation is DECORATIVE NOISE; the 14-item header stem pool is the primary finding")

print(f"\n  Findings ({n_pass} of 4 tests pass):")
for interp in interpretations:
    print(f"    - {interp}")

out_path = ROOT / "outputs" / "tp_alternation_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-TP-ALTERNATION-01",
    "n_paragraphs_detected": len(paragraphs),
    "n_retained_plain_gallows_initial": len(kept),
    "global": {"t": t_count, "p": p_count, "t_rate": round(t_count/tot, 4)},
    "test_A_section": {
        "sections_used": valid_secs,
        "contingency": {s: {"t": section_tp[s][0], "p": section_tp[s][1]} for s in valid_secs},
        "chi2": round(chi2, 3), "df": df, "p_value": round(pA, 6),
        "cramers_v": round(cv, 3), "pass": testA_pass,
    },
    "test_B_quire": {
        "quires_used": sorted(valid_qs),
        "contingency": {q: {"t": quire_tp[q][0], "p": quire_tp[q][1]} for q in valid_qs},
        "chi2": round(chi2B, 3), "df": dfB, "p_value": round(pB, 6),
        "cramers_v": round(cvB, 3), "pass": testB_pass,
    },
    "test_C_within_folio_runs": {
        "n_folios_used": n_folios,
        "mean_per_folio_z": round(mean_z, 3),
        "stouffer_combined_z": round(stouffer_z, 3),
        "direction": ("alternation" if stouffer_z > 0 else "clustering") if stouffer_z != 0 else "neutral",
        "pass": testC_pass,
    },
    "test_D_stem_conditional": {
        "stems_used": valid_stems,
        "contingency": {s: {"t": stem_tp[s][0], "p": stem_tp[s][1]} for s in valid_stems},
        "chi2": round(chi2D, 3), "df": dfD, "p_value": round(pD, 6),
        "cramers_v": round(cvD, 3), "pass": testD_pass,
    },
    "n_tests_passing": n_pass,
    "interpretations": interpretations,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
