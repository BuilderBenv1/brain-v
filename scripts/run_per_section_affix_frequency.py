"""Diagnostic supplementary to H-BV-BL-AFFIX-REMOVAL-01.

Per-section -edy and qo- affix frequencies per hand. Tests whether
herbal-A and herbal-B are depleted in these affixes relative to other
sections in their respective hands.

If herbal sections have low affix rates, the within-herbal A/B
convergence (H-BV-HAND-B-SECTION-BREAKDOWN-01) is likely B&L's
affix-removal collapse manifesting at section granularity.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))


def per_section_per_hand_affix_stats():
    buckets = defaultdict(lambda: {"n_tokens": 0, "n_edy": 0, "n_qo": 0, "n_folios": 0})
    for f in CORPUS["folios"]:
        hand = f.get("currier_language")
        section = f.get("section")
        if hand not in ("A", "B"):
            continue
        key = (hand, section)
        tokens = []
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    tokens.append(w)
        if not tokens:
            continue
        buckets[key]["n_folios"] += 1
        buckets[key]["n_tokens"] += len(tokens)
        buckets[key]["n_edy"] += sum(1 for t in tokens if t.endswith("edy"))
        buckets[key]["n_qo"] += sum(1 for t in tokens if t.startswith("qo"))
    return buckets


stats = per_section_per_hand_affix_stats()
print(f"{'Hand':<6}{'Section':<17}{'Folios':<8}{'Tokens':<9}{'edy%':<10}{'qo%':<10}{'combined%'}")
print("-" * 70)

rows = []
for (hand, section), s in sorted(stats.items()):
    pct_edy = s["n_edy"] / s["n_tokens"] * 100 if s["n_tokens"] else 0
    pct_qo = s["n_qo"] / s["n_tokens"] * 100 if s["n_tokens"] else 0
    combined = pct_edy + pct_qo
    rows.append((hand, section, s["n_folios"], s["n_tokens"], pct_edy, pct_qo, combined))
    print(f"{hand:<6}{section:<17}{s['n_folios']:<8}{s['n_tokens']:<9}{pct_edy:<10.2f}{pct_qo:<10.2f}{combined:.2f}")

# Focus: herbal vs non-herbal per hand
print("\n--- HERBAL vs NON-HERBAL comparison per hand ---")
for hand in ("A", "B"):
    h_s = stats.get((hand, "herbal"), None)
    nh_totals = {"n_tokens": 0, "n_edy": 0, "n_qo": 0}
    for (hh, section), s in stats.items():
        if hh == hand and section != "herbal":
            for k in nh_totals:
                nh_totals[k] += s[k]
    if h_s:
        h_edy = h_s["n_edy"] / h_s["n_tokens"] * 100
        h_qo = h_s["n_qo"] / h_s["n_tokens"] * 100
    else:
        h_edy = h_qo = 0
    nh_edy = nh_totals["n_edy"] / nh_totals["n_tokens"] * 100 if nh_totals["n_tokens"] else 0
    nh_qo = nh_totals["n_qo"] / nh_totals["n_tokens"] * 100 if nh_totals["n_tokens"] else 0
    print(f"  Hand {hand}:")
    print(f"    Herbal:     edy={h_edy:.2f}%  qo={h_qo:.2f}%  combined={h_edy+h_qo:.2f}%")
    print(f"    Non-herbal: edy={nh_edy:.2f}%  qo={nh_qo:.2f}%  combined={nh_edy+nh_qo:.2f}%")
    print(f"    Non-herbal / herbal ratio: edy {nh_edy/h_edy if h_edy else 0:.2f}x, qo {nh_qo/h_qo if h_qo else 0:.2f}x")

print("\n--- INTERPRETATION ---")
print("  If herbal (in both hands) has LOW combined affix% vs other sections,")
print("  the within-herbal A/B convergence is B&L's affix collapse manifesting")
print("  at section granularity. Herbal depletion in the differentiating affixes")
print("  would naturally produce A/B convergence within herbal.")

# Save
out = {
    "generated": "2026-04-18",
    "test": "per_section_affix_frequency_diagnostic",
    "parent_hypothesis": "H-BV-BL-AFFIX-REMOVAL-01",
    "per_section": [
        {"hand": h, "section": s, "folios": nf, "tokens": nt,
         "edy_pct": round(e, 2), "qo_pct": round(q, 2), "combined_pct": round(c, 2)}
        for h, s, nf, nt, e, q, c in rows
    ],
}
out_path = ROOT / "outputs" / "per_section_affix_frequency.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
