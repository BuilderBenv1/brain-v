"""
Execute pre-registered H-BV-HAND-A-REPEAT-STRUCTURE-01.

Three measurements on Hand A tokens only:

  (1) For each of the top-20 most frequent Hand A tokens:
        a. line_start_rate     = fraction of its occurrences that are the
                                 first token of a line
        b. folio_top_share     = largest per-folio share of its occurrences
           folio_herfindahl    = sum of squared per-folio shares
        c. chi_square_uniform  = chi-square statistic against a uniform
                                 distribution across Hand A folios,
                                 weighted by folio token count
  (2) Zipf exponent on Hand A rank-frequency over top-100 ranks
      (negative slope of log-rank vs log-frequency; report |slope| and R^2)
  (3) Clauset & Eagle 2012 burstiness
        B = (sigma - mu) / (sigma + mu)
      computed on inter-occurrence gaps per top-20 token, then averaged.
      B in [-1, +1]; near 0 => Poisson-like, > 0 => bursty, < 0 => regular.

Decision rule:
  - mean line-start rate > 0.40 -> formulaic / structured
  - else if mean burstiness >= 0.30 AND mean folio top-share < 0.20
      -> narrative / philosophical
  - else if mean folio top-share >= 0.20 OR mean Herfindahl >= 0.10
      -> didactic / technical
  - else mixed
"""
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# --------------------------------------------------------------------------
# Collect Hand A tokens with positional metadata.
# --------------------------------------------------------------------------
hand_a_tokens = []                # flat token stream (document order)
folio_tokens = defaultdict(list)  # folio -> token list
folio_order = []                  # folios in document order
line_start_positions = set()      # global token indices that begin a line
token_folio = []                  # parallel to hand_a_tokens: folio id

idx = 0
for folio in CORPUS["folios"]:
    if folio.get("currier_language") != "A":
        continue
    fid = folio["folio"]
    folio_order.append(fid)
    for line in folio["lines"]:
        words = line["words"]
        if not words:
            continue
        line_start_positions.add(idx)
        for w in words:
            hand_a_tokens.append(w)
            token_folio.append(fid)
            folio_tokens[fid].append(w)
            idx += 1

N = len(hand_a_tokens)
freq = Counter(hand_a_tokens)
top20 = [w for w, _ in freq.most_common(20)]

# Folio token counts (used as expected weights for chi-square uniformity).
folio_total = {f: len(folio_tokens[f]) for f in folio_order}
total_tokens = sum(folio_total.values())

# --------------------------------------------------------------------------
# (1a) Line-start rate per top-20 token.
# (1b) Folio concentration: top-folio share, Herfindahl.
# (1c) Chi-square against folio-token-weighted uniform.
# --------------------------------------------------------------------------
per_token_stats = []
for w in top20:
    occurrences = [i for i, t in enumerate(hand_a_tokens) if t == w]
    n_w = len(occurrences)
    if n_w == 0:
        continue

    # (a) line-start rate
    n_line_start = sum(1 for i in occurrences if i in line_start_positions)
    line_start_rate = n_line_start / n_w

    # (b) folio distribution
    by_folio = Counter(token_folio[i] for i in occurrences)
    shares = [c / n_w for c in by_folio.values()]
    top_share = max(shares) if shares else 0.0
    herfindahl = sum(s * s for s in shares)

    # (c) chi-square against folio-size-weighted expected counts
    chi2 = 0.0
    for f in folio_order:
        expected = n_w * (folio_total[f] / total_tokens)
        observed = by_folio.get(f, 0)
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected

    per_token_stats.append({
        "token": w,
        "freq": n_w,
        "line_start_rate": line_start_rate,
        "top_folio_share": top_share,
        "folio_herfindahl": herfindahl,
        "chi2_uniform": chi2,
        "n_folios_present": len(by_folio),
    })

mean_line_start = statistics.mean(s["line_start_rate"] for s in per_token_stats)
mean_top_share = statistics.mean(s["top_folio_share"] for s in per_token_stats)
mean_herfindahl = statistics.mean(s["folio_herfindahl"] for s in per_token_stats)
mean_chi2 = statistics.mean(s["chi2_uniform"] for s in per_token_stats)

# --------------------------------------------------------------------------
# (2) Zipf exponent on top-100 ranks.
# --------------------------------------------------------------------------
freqs_sorted = sorted(freq.values(), reverse=True)
K = min(100, len(freqs_sorted))
xs = [math.log(r + 1) for r in range(K)]
ys = [math.log(freqs_sorted[r]) for r in range(K)]
mx = sum(xs) / K
my = sum(ys) / K
num = sum((xs[i] - mx) * (ys[i] - my) for i in range(K))
den = sum((xs[i] - mx) ** 2 for i in range(K))
slope = num / den if den else 0.0
zipf_exp = -slope
ss_res = sum((ys[i] - (my + slope * (xs[i] - mx))) ** 2 for i in range(K))
ss_tot = sum((ys[i] - my) ** 2 for i in range(K))
zipf_r2 = 1 - ss_res / ss_tot if ss_tot else 0.0

# --------------------------------------------------------------------------
# (3) Clauset & Eagle 2012 burstiness per top-20 token; average.
# --------------------------------------------------------------------------
burstiness_per_token = []
for w in top20:
    pos = [i for i, t in enumerate(hand_a_tokens) if t == w]
    if len(pos) < 3:
        continue
    gaps = [pos[i + 1] - pos[i] for i in range(len(pos) - 1)]
    mu = statistics.mean(gaps)
    sigma = statistics.pstdev(gaps)
    if (sigma + mu) == 0:
        continue
    B = (sigma - mu) / (sigma + mu)
    burstiness_per_token.append({"token": w, "mu": mu, "sigma": sigma, "B": B})

mean_burstiness = statistics.mean(b["B"] for b in burstiness_per_token)

# --------------------------------------------------------------------------
# Decision rule.
# --------------------------------------------------------------------------
if mean_line_start > 0.40:
    verdict = "formulaic / structured"
elif mean_burstiness >= 0.30 and mean_top_share < 0.20:
    verdict = "narrative / philosophical"
elif mean_top_share >= 0.20 or mean_herfindahl >= 0.10:
    verdict = "didactic / technical"
else:
    verdict = "mixed (no archetype dominates)"

# --------------------------------------------------------------------------
# Print + save.
# --------------------------------------------------------------------------
print("=" * 72)
print("  H-BV-HAND-A-REPEAT-STRUCTURE-01 — Hand A repeat-structure test")
print("=" * 72)
print(f"  Hand A tokens: {N:,}   types: {len(freq):,}   folios: {len(folio_order)}")
print(f"  Top-20 tokens by frequency:")
for s in per_token_stats:
    print(f"    {s['token']:<10} freq={s['freq']:<5} "
          f"line_start={s['line_start_rate']:.3f}  "
          f"top_folio={s['top_folio_share']:.3f}  "
          f"H={s['folio_herfindahl']:.4f}  "
          f"folios_present={s['n_folios_present']}")
print()
print(f"  (1a) Mean line-start rate (top-20):          {mean_line_start:.4f}")
print(f"  (1b) Mean folio top-share (top-20):          {mean_top_share:.4f}")
print(f"       Mean folio Herfindahl (top-20):         {mean_herfindahl:.4f}")
print(f"  (1c) Mean chi-square vs folio-uniform:       {mean_chi2:.2f}")
print(f"  (2)  Zipf exponent (|slope| top-100):        {zipf_exp:.4f}  R^2={zipf_r2:.4f}")
print(f"  (3)  Mean burstiness B (top-20):             {mean_burstiness:.4f}")
print()
print("  Per-token burstiness (top-20):")
for b in burstiness_per_token:
    print(f"    {b['token']:<10} mu={b['mu']:.2f}  sigma={b['sigma']:.2f}  B={b['B']:.3f}")
print()
print(f"  Decision-rule verdict: {verdict}")

out = ROOT / "outputs" / "hand_a_repeat_structure_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-HAND-A-REPEAT-STRUCTURE-01",
    "hand_a_tokens": N,
    "hand_a_types": len(freq),
    "hand_a_folios": len(folio_order),
    "top20_per_token": per_token_stats,
    "summary": {
        "mean_line_start_rate": round(mean_line_start, 6),
        "mean_top_folio_share": round(mean_top_share, 6),
        "mean_folio_herfindahl": round(mean_herfindahl, 6),
        "mean_chi2_uniform": round(mean_chi2, 4),
        "zipf_exponent_top100": round(zipf_exp, 6),
        "zipf_r_squared": round(zipf_r2, 6),
        "mean_burstiness_top20": round(mean_burstiness, 6),
    },
    "burstiness_per_token": [
        {"token": b["token"], "mu": round(b["mu"], 4),
         "sigma": round(b["sigma"], 4), "B": round(b["B"], 6)}
        for b in burstiness_per_token
    ],
    "decision_rule": {
        "line_start_threshold_formulaic": 0.40,
        "burstiness_threshold_narrative": 0.30,
        "top_share_threshold_didactic": 0.20,
        "herfindahl_threshold_didactic": 0.10,
    },
    "verdict": verdict,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
