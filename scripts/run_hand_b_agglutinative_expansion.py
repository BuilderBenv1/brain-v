"""Execute pre-registered H-BV-HAND-B-AGGLUTINATIVE-EXPANSION-01."""
import json
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")

HAND_B = {"M1":4.4935, "M2_L1":10, "M2_L2":5, "M3":2.7901, "M4":0.26, "M5":0.80}

CANDIDATES = {
    "Basque":     {"M1":(2.5,4.5),"M2_L1":(8,16),"M2_L2":(3,8), "M3":(2.0,5.0),"M4":(0.02,0.20),"M5":(0.60,1.00)},
    "Georgian":   {"M1":(2.0,4.0),"M2_L1":(10,20),"M2_L2":(4,10),"M3":(2.0,4.5),"M4":(0.10,0.30),"M5":(0.70,0.95)},
    "Swahili":    {"M1":(3.0,5.5),"M2_L1":(6,12),"M2_L2":(8,16),"M3":(2.5,5.0),"M4":(0.05,0.20),"M5":(0.85,1.00)},
    "Tagalog":    {"M1":(1.8,3.2),"M2_L1":(15,30),"M2_L2":(2,6), "M3":(1.5,3.5),"M4":(0.25,0.55),"M5":(0.40,0.70)},
    "Mapudungun": {"M1":(3.0,6.0),"M2_L1":(20,40),"M2_L2":(6,14),"M3":(2.0,5.0),"M4":(0.30,0.60),"M5":(0.55,0.80)},
    "Ainu":       {"M1":(2.5,5.0),"M2_L1":(12,25),"M2_L2":(4,10),"M3":(2.0,4.5),"M4":(0.20,0.50),"M5":(0.50,0.80)},
    "Inuktitut":  {"M1":(4.0,8.0),"M2_L1":(300,500),"M2_L2":(6,14),"M3":(3.0,7.0),"M4":(0.60,0.90),"M5":(0.75,0.95)},
}

METRICS = ["M1","M2_L1","M2_L2","M3","M4","M5"]

def dist(v, rng):
    lo, hi = rng
    w = hi - lo
    if lo <= v <= hi:
        return 0.0, True
    return min(abs(v-lo), abs(v-hi))/w, False

results = []
for lang, profile in CANDIDATES.items():
    total = 0.0; matches = 0
    per_m = {}
    for m in METRICS:
        d, in_r = dist(HAND_B[m], profile[m])
        per_m[m] = {"v":HAND_B[m], "range":profile[m], "d":round(d,4), "in_range":in_r}
        total += d
        if in_r: matches += 1
    results.append({"language":lang, "distance":round(total,4), "matches":matches, "per_metric":per_m})

results.sort(key=lambda r: r["distance"])

print("=== HAND B PROFILE DISTANCE RANKING ===")
print(f"{'Rank':<5}{'Language':<14}{'Distance':<12}{'Matches'}")
for i, r in enumerate(results, 1):
    print(f"  {i:<3}{r['language']:<14}{r['distance']:<12.4f}{r['matches']}/6")

r1, r2 = results[0], results[1]
margin = float('inf') if r1["distance"]==0 and r2["distance"]>0 else (r2["distance"]/r1["distance"] if r1["distance"]>0 else 1.0)
print(f"\n  rank 1: {r1['language']} (distance {r1['distance']})")
print(f"  rank 2: {r2['language']} (distance {r2['distance']})")
print(f"  margin: {'inf' if margin==float('inf') else f'{margin:.4f}'}")

if r1["language"] == "Basque":
    if r1["distance"] == 0 or margin >= 1.10:
        verdict = "BASQUE_UNIQUELY_BEST"
    else:
        verdict = "BASQUE_BEST_NOT_UNIQUELY"
else:
    verdict = "NOT_BASQUE_FIRST"
top3_margins = [results[i+1]["distance"]/results[i]["distance"] if results[i]["distance"]>0 else float('inf') for i in range(2)]
if all(m < 1.10 for m in top3_margins):
    verdict = "FAMILY_LEVEL"

print(f"\n  VERDICT: {verdict}")
print(f"\n  HAND A reference: BASQUE_UNIQUELY_BEST (Basque dist 0.0, Georgian dist 0.26)")

print("\n=== PER-METRIC DETAIL (top 3) ===")
for r in results[:3]:
    print(f"\n  {r['language']}  distance={r['distance']}  matches={r['matches']}/6")
    for m in METRICS:
        pm = r["per_metric"][m]
        tag = "MATCH" if pm["in_range"] else f"MISS d={pm['d']}"
        print(f"    {m:8s} v={pm['v']:<8} range={pm['range']}  {tag}")

out = {"generated":"2026-04-18","hypothesis":"H-BV-HAND-B-AGGLUTINATIVE-EXPANSION-01",
       "hand_b_values":HAND_B,"ranked_results":results,
       "rank_1":r1["language"],"rank_2":r2["language"],
       "margin": "inf" if margin==float('inf') else round(margin,4),
       "verdict":verdict,
       "hand_a_reference":"BASQUE_UNIQUELY_BEST (Basque 0.0, Georgian 0.26, Swahili 0.375)"}
out_path = ROOT / "outputs" / "hand_b_agglutinative_expansion_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
