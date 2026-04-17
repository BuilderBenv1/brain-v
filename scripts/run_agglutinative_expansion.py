"""
Execute pre-registered H-BV-AGGLUTINATIVE-EXPANSION-01.

7-candidate morphological profile distance comparison. Hand A's
metric values are fixed from the prior test; candidate ranges
are locked in the hypothesis pre-registration.
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")

HAND_A = {
    "M1": 4.12,
    "M2_L1": 10,
    "M2_L2": 5,
    "M3": 3.16,
    "M4": 0.20,
    "M5": 1.00,
}

CANDIDATES = {
    "Basque": {
        "M1": (2.5, 4.5), "M2_L1": (8, 16), "M2_L2": (3, 8),
        "M3": (2.0, 5.0), "M4": (0.02, 0.20), "M5": (0.60, 1.00),
        "confidence": "high",
    },
    "Georgian": {
        "M1": (2.0, 4.0), "M2_L1": (10, 20), "M2_L2": (4, 10),
        "M3": (2.0, 4.5), "M4": (0.10, 0.30), "M5": (0.70, 0.95),
        "confidence": "moderate",
    },
    "Swahili": {
        "M1": (3.0, 5.5), "M2_L1": (6, 12), "M2_L2": (8, 16),
        "M3": (2.5, 5.0), "M4": (0.05, 0.20), "M5": (0.85, 1.00),
        "confidence": "high",
    },
    "Tagalog": {
        "M1": (1.8, 3.2), "M2_L1": (15, 30), "M2_L2": (2, 6),
        "M3": (1.5, 3.5), "M4": (0.25, 0.55), "M5": (0.40, 0.70),
        "confidence": "moderate",
    },
    "Mapudungun": {
        "M1": (3.0, 6.0), "M2_L1": (20, 40), "M2_L2": (6, 14),
        "M3": (2.0, 5.0), "M4": (0.30, 0.60), "M5": (0.55, 0.80),
        "confidence": "low-moderate",
    },
    "Ainu": {
        "M1": (2.5, 5.0), "M2_L1": (12, 25), "M2_L2": (4, 10),
        "M3": (2.0, 4.5), "M4": (0.20, 0.50), "M5": (0.50, 0.80),
        "confidence": "low-moderate",
    },
    "Inuktitut": {
        "M1": (4.0, 8.0), "M2_L1": (300, 500), "M2_L2": (6, 14),
        "M3": (3.0, 7.0), "M4": (0.60, 0.90), "M5": (0.75, 0.95),
        "confidence": "high inventory / moderate other",
    },
}

METRICS = ["M1", "M2_L1", "M2_L2", "M3", "M4", "M5"]


def distance_per_metric(v, range_tuple):
    lo, hi = range_tuple
    width = hi - lo
    if lo <= v <= hi:
        return 0.0, True
    out = min(abs(v - lo), abs(v - hi))
    return (out / width, False) if width > 0 else (out, False)


results = []
for lang, profile in CANDIDATES.items():
    total = 0.0
    match_count = 0
    per_metric = {}
    for m in METRICS:
        d, in_range = distance_per_metric(HAND_A[m], profile[m])
        per_metric[m] = {
            "hand_a_value": HAND_A[m],
            "range": profile[m],
            "distance": round(d, 4),
            "in_range": in_range,
        }
        total += d
        if in_range:
            match_count += 1
    results.append({
        "language": lang,
        "profile_distance": round(total, 4),
        "match_count": match_count,
        "per_metric": per_metric,
        "confidence": profile["confidence"],
    })

results.sort(key=lambda r: r["profile_distance"])

print("=== AGGLUTINATIVE EXPANSION RANKING ===")
print(f"{'Rank':<5}{'Language':<14}{'Distance':<12}{'Matches':<10}{'Confidence'}")
for i, r in enumerate(results, 1):
    print(f"  {i:<3}{r['language']:<14}{r['profile_distance']:<12.4f}{r['match_count']}/6        {r['confidence']}")

rank1 = results[0]
rank2 = results[1]
if rank1["profile_distance"] == 0.0 and rank2["profile_distance"] > 0.0:
    margin = float("inf")
elif rank1["profile_distance"] > 0.0:
    margin = rank2["profile_distance"] / rank1["profile_distance"]
else:
    margin = 1.0

print(f"\n  rank 1: {rank1['language']} (distance {rank1['profile_distance']:.4f})")
print(f"  rank 2: {rank2['language']} (distance {rank2['profile_distance']:.4f})")
print(f"  margin (rank2 / rank1): {margin:.4f}" if margin != float('inf') else f"  margin: infinity (rank1 is 0, rank2 is > 0)")

top3_margins = []
for j in range(1, min(3, len(results))):
    if results[j-1]["profile_distance"] > 0:
        top3_margins.append(results[j]["profile_distance"] / results[j-1]["profile_distance"])
family_level = len(top3_margins) >= 2 and all(m < 1.10 for m in top3_margins)

if rank1["language"] == "Basque":
    if rank1["profile_distance"] == 0.0 and rank2["profile_distance"] > 0.0:
        verdict = "BASQUE_UNIQUELY_BEST"
    elif margin >= 1.10:
        verdict = "BASQUE_UNIQUELY_BEST"
    else:
        verdict = "BASQUE_BEST_NOT_UNIQUELY"
else:
    verdict = "NOT_BASQUE_FIRST"

if family_level and rank1["language"] == "Basque":
    verdict = "FAMILY_LEVEL"

print(f"\n  VERDICT: {verdict}")

print("\n=== PER-METRIC DETAIL ===")
for r in results:
    print(f"\n  {r['language']}  distance={r['profile_distance']:.4f}  matches={r['match_count']}/6")
    for m in METRICS:
        pm = r["per_metric"][m]
        tag = "MATCH" if pm["in_range"] else f"MISS d={pm['distance']:.4f}"
        print(f"    {m:8s}  v={pm['hand_a_value']:<6}  range={pm['range']}  {tag}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-AGGLUTINATIVE-EXPANSION-01",
    "hand_a_values": HAND_A,
    "candidates": CANDIDATES,
    "ranked_results": results,
    "rank_1_language": rank1["language"],
    "rank_2_language": rank2["language"],
    "margin_rank2_over_rank1": None if margin == float("inf") else round(margin, 4),
    "margin_is_infinite": margin == float("inf"),
    "family_level_cluster": family_level,
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "agglutinative_expansion_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
