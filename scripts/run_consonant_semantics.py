"""
Execute pre-registered H-BV-CONSONANT-SEMANTICS-01 (locked 0abc1ad).

For every EVA word:
  strip line-initial plain gallows t/p (not bench-gallows)
  strip trailing suffix char from {y,n,r,m,g}
  strip EVA vowels {a,o,e,i}
  apply Brain-V's EVA->skeleton char map

Per folio, build Counter(consonant_skeleton).

Metrics:
  (a) Top-20 skeleton Jaccard: HandA plant vs HandB plant
  (b) Top-20 skeleton Jaccard: HandA plant vs HandB non-plant herbal
  (c) Same for other content groupings
  (d) Mean per-folio Jaccard within vs across content groups

Decision rule:
  CONFIRMED if (a)/(b) >= 2 AND within-group mean / across-group mean >= 2
  REFUTED if (a)/(b) <= 1.2
  MARGINAL in between
"""
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
PLANT_CSV = ROOT / "raw/research/plant-identifications.csv"

EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
VOWELS = set("aoei")
SUFFIX_STRIP = set("ynrmg")

def skeleton(word, is_line_initial=False):
    # line-initial plain gallows stripped
    if is_line_initial and word and word[0] in "tp" and (len(word)==1 or word[1]!="h"):
        word = word[1:]
    # strip one trailing suffix char
    if word and word[-1] in SUFFIX_STRIP and len(word) > 2:
        word = word[:-1]
    # char map, vowels dropped
    out = []; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                out.append(sy); i += len(ev); matched = True; break
        if not matched:
            if word[i] not in VOWELS:
                # unknown
                pass
            i += 1
    return "".join(out)

# Per folio counters (using line-initial flag)
folio_skels = defaultdict(Counter)
folio_hand = {}
folio_section = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_hand[fid] = f.get("currier_language", "?")
    folio_section[fid] = f["section"]
    for line in f["lines"]:
        words = line["words"]
        for i, w in enumerate(words):
            sk = skeleton(w, is_line_initial=(i == 0))
            if sk and len(sk) >= 1:
                folio_skels[fid][sk] += 1

# Load plant IDs
plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        plant_folios.add(r["folio"])

def group(hand=None, section=None, is_plant=None, min_tokens=20):
    out = []
    for fid, skels in folio_skels.items():
        if sum(skels.values()) < min_tokens: continue
        if hand is not None and folio_hand.get(fid) != hand: continue
        if section is not None and folio_section.get(fid) != section: continue
        if is_plant is True and fid not in plant_folios: continue
        if is_plant is False and fid in plant_folios: continue
        out.append(fid)
    return out

groups = {
    "A_plant":       group(hand="A", is_plant=True),
    "A_nonplant_h":  group(hand="A", section="herbal", is_plant=False),
    "A_pharma":      group(hand="A", section="pharmaceutical"),
    "B_plant":       group(hand="B", is_plant=True),
    "B_nonplant_h":  group(hand="B", section="herbal", is_plant=False),
    "B_biological":  group(hand="B", section="biological"),
    "B_recipes":     group(hand="B", section="recipes"),
    "zodiac":        group(section="zodiac"),
    "astronomical":  group(section="astronomical"),
}
print("Group sizes:")
for g, fs in groups.items():
    print(f"  {g:<16} {len(fs)} folios")

# Top-K skeleton set per group (by total count)
K = 20
group_top = {}
for g, fs in groups.items():
    c = Counter()
    for fid in fs:
        for sk, n in folio_skels[fid].items():
            c[sk] += n
    group_top[g] = {sk for sk, _ in c.most_common(K)}

def jaccard(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

print(f"\nTop-{K} skeleton Jaccard matrix")
print(f"  {'':<16} " + "  ".join(f"{g[:14]:<14}" for g in groups))
for g1 in groups:
    row = [g1] + [f"{jaccard(group_top[g1], group_top[g2]):.3f}" for g2 in groups]
    print(f"  {g1:<16} " + "  ".join(f"{v:<14}" for v in row[1:]))

# Primary ratio: A_plant/B_plant vs A_plant/B_nonplant_h
j_plant = jaccard(group_top["A_plant"], group_top["B_plant"])
j_control = jaccard(group_top["A_plant"], group_top["B_nonplant_h"])
ratio = j_plant / j_control if j_control > 0 else float("inf")

print(f"\n  Jaccard(A_plant, B_plant):        {j_plant:.3f}")
print(f"  Jaccard(A_plant, B_nonplant_h):   {j_control:.3f}")
print(f"  Ratio (plant / non-plant):        {ratio:.2f}x")

# Mean per-folio Jaccard within vs across content groups
def per_folio_skels_set(fid, topk=20):
    return {sk for sk, _ in folio_skels[fid].most_common(topk)}

def mean_pairwise_jaccard(folios):
    if len(folios) < 2: return 0.0
    sets = [per_folio_skels_set(f) for f in folios]
    js = []
    for i in range(len(sets)):
        for j in range(i+1, len(sets)):
            js.append(jaccard(sets[i], sets[j]))
    return statistics.mean(js) if js else 0.0

def cross_group_mean_jaccard(ga, gb):
    sa = [per_folio_skels_set(f) for f in ga]
    sb = [per_folio_skels_set(f) for f in gb]
    js = []
    for a in sa:
        for b in sb:
            js.append(jaccard(a, b))
    return statistics.mean(js) if js else 0.0

plant_all = groups["A_plant"] + groups["B_plant"]
nonplant_all = groups["A_nonplant_h"] + groups["B_nonplant_h"]

within_plant = mean_pairwise_jaccard(plant_all)
within_nonplant = mean_pairwise_jaccard(nonplant_all)
across_plant_nonplant = cross_group_mean_jaccard(plant_all, nonplant_all)

print(f"\nPer-folio mean pairwise Jaccard (top-{K} skeletons):")
print(f"  within plant (all hands):           {within_plant:.3f}")
print(f"  within non-plant herbal (all hands): {within_nonplant:.3f}")
print(f"  across plant vs non-plant:          {across_plant_nonplant:.3f}")
print(f"  within-plant / across ratio:         "
      f"{within_plant/across_plant_nonplant if across_plant_nonplant else float('inf'):.2f}x")

# Cross-hand detail
within_A_plant = mean_pairwise_jaccard(groups["A_plant"])
within_B_plant = mean_pairwise_jaccard(groups["B_plant"])
across_AB_plant = cross_group_mean_jaccard(groups["A_plant"], groups["B_plant"])
across_A_plant_B_nonplant = cross_group_mean_jaccard(
    groups["A_plant"], groups["B_nonplant_h"])

print(f"\n  within A_plant:                     {within_A_plant:.3f}")
print(f"  within B_plant:                     {within_B_plant:.3f}")
print(f"  across A_plant vs B_plant:          {across_AB_plant:.3f}")
print(f"  across A_plant vs B_nonplant_h:     {across_A_plant_B_nonplant:.3f}")
print(f"  (A_plant vs B_plant) / (A_plant vs B_nonplant) ratio: "
      f"{across_AB_plant/across_A_plant_B_nonplant if across_A_plant_B_nonplant else float('inf'):.2f}x")

# Decision
print("\n" + "="*72)
print("  PRE-REGISTERED DECISION")
print("="*72)

jacc_ratio = ratio
folio_ratio = within_plant / across_plant_nonplant if across_plant_nonplant else 0

if jacc_ratio >= 2.0 and folio_ratio >= 2.0:
    verdict = "CONFIRMED"
elif jacc_ratio <= 1.2 or folio_ratio <= 1.2:
    verdict = "REFUTED"
else:
    verdict = "MARGINAL"

print(f"  Top-20 Jaccard ratio (plant/nonplant): {jacc_ratio:.2f}x  "
      f"({'pass' if jacc_ratio >= 2.0 else 'fail'})")
print(f"  Per-folio within/across ratio:          {folio_ratio:.2f}x  "
      f"({'pass' if folio_ratio >= 2.0 else 'fail'})")
print(f"  -> {verdict}")

# Save
out = ROOT / "outputs" / "consonant_semantics_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-CONSONANT-SEMANTICS-01",
    "locked_in_commit": "0abc1ad",
    "group_sizes": {g: len(fs) for g, fs in groups.items()},
    "top_k": K,
    "jaccard_matrix_top_k": {
        g1: {g2: jaccard(group_top[g1], group_top[g2]) for g2 in groups}
        for g1 in groups
    },
    "primary_jaccard": {
        "A_plant_vs_B_plant": round(j_plant, 4),
        "A_plant_vs_B_nonplant_h": round(j_control, 4),
        "ratio": round(ratio, 3) if ratio != float("inf") else None,
    },
    "per_folio": {
        "within_plant_all_hands": round(within_plant, 4),
        "within_nonplant_all_hands": round(within_nonplant, 4),
        "across_plant_nonplant": round(across_plant_nonplant, 4),
        "within_plant_over_across_ratio": round(folio_ratio, 3) if across_plant_nonplant else None,
        "within_A_plant": round(within_A_plant, 4),
        "within_B_plant": round(within_B_plant, 4),
        "across_A_plant_B_plant": round(across_AB_plant, 4),
        "across_A_plant_B_nonplant_h": round(across_A_plant_B_nonplant, 4),
    },
    "verdict": verdict,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
