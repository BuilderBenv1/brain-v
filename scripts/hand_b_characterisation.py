"""
Characterise Hand B. Since _.oii is a Hand-A phenomenon (zero Hand-B fires),
what DO Hand-B folios use? Does Hand B have its own plant-folio marker?

Method
------
  1. Isolate Hand-B folios (plant vs non-plant herbal).
  2. For every vowel pattern with >=10 Hand-B hits, compute enrichment on
     plant vs non-plant Hand-B folios.
  3. Compare top Hand-B enriched patterns with top Hand-A enriched patterns
     to see if they're different vocabularies.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "scripts")

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

def split_skel_vowels(word):
    if word and word[0] in "tp" and (len(word)==1 or word[1]!="h"):
        word = word[1:]
    cons=[]; vs=[]; pos=0; i=0
    while i<len(word):
        matched=False
        for ev,sy in EVA_MAP:
            if word.startswith(ev,i):
                cons.append(sy); pos+=1; i+=len(ev); matched=True; break
        if not matched:
            if word[i] in VOWELS: vs.append((pos, word[i]))
            i+=1
    if not vs: return "".join(cons), ""
    by_pos = defaultdict(list)
    for p,v in vs: by_pos[p].append(v)
    return "".join(cons), ".".join("".join(by_pos.get(p,[])) or "_"
                                    for p in range(max(by_pos)+1))

# Index
folio_meta = {f["folio"]: {"hand": f.get("currier_language","?"),
                           "section": f["section"]}
              for f in CORPUS["folios"]}
folio_tokens = defaultdict(list)
for f in CORPUS["folios"]:
    for line in f["lines"]:
        folio_tokens[f["folio"]].extend(line["words"])

plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        plant_folios.add(r["folio"])

# Partition
def by_hand_plant(hand):
    plants = [f for f in plant_folios
              if folio_meta.get(f,{}).get("hand") == hand
              and len(folio_tokens[f]) >= 20]
    nonplants = [f for f,m in folio_meta.items()
                 if m["hand"] == hand and m["section"] == "herbal"
                 and f not in plant_folios and len(folio_tokens[f]) >= 20]
    return plants, nonplants

a_plants, a_non = by_hand_plant("A")
b_plants, b_non = by_hand_plant("B")

print(f"Hand A: plant {len(a_plants)}, non-plant herbal {len(a_non)}")
print(f"Hand B: plant {len(b_plants)}, non-plant herbal {len(b_non)}")

def pattern_tally(folios):
    vp = Counter()
    total = 0
    for f in folios:
        for w in folio_tokens[f]:
            _, p = split_skel_vowels(w)
            vp[p] += 1
            total += 1
    return vp, total

def enrichment_table(plant_folios_list, non_folios_list, min_hits=10):
    pvp, pt = pattern_tally(plant_folios_list)
    nvp, nt = pattern_tally(non_folios_list)
    rows = []
    for p, ph in pvp.items():
        if ph < min_hits: continue
        nh = nvp.get(p, 0)
        p_rate = ph / pt
        n_rate = nh / nt if nt else 0
        enr = (p_rate / n_rate) if n_rate > 0 else (float("inf") if p_rate > 0 else 1.0)
        rows.append({"pattern": p, "plant_hits": ph, "non_hits": nh,
                     "plant_rate": p_rate, "non_rate": n_rate, "enr": enr})
    rows.sort(key=lambda r: -r["enr"] if r["enr"] != float("inf") else -1e9)
    return rows

print("\n" + "="*72)
print("  HAND B — vowel-pattern enrichment on plant folios (min 10 hits)")
print("="*72)
b_rows = enrichment_table(b_plants, b_non, min_hits=10)
print(f"  {'pattern':<14} {'pl_hits':>8} {'nt_hits':>8} "
      f"{'pl_rate':>10} {'nt_rate':>10} {'enr':>8}")
for r in b_rows[:15]:
    enr_str = f"{r['enr']:.2f}x" if r['enr'] != float("inf") else "inf"
    print(f"  {r['pattern']:<14} {r['plant_hits']:>8} {r['non_hits']:>8} "
          f"{r['plant_rate']:>10.5f} {r['non_rate']:>10.5f} {enr_str:>8}")

# Null check: is _.oii really zero on Hand B as the confound check said?
print(f"\n  Sanity: _.oii on Hand B:")
for f in b_plants + b_non:
    for w in folio_tokens[f]:
        _, vp = split_skel_vowels(w)
        if vp == "_.oii":
            print(f"    FOUND _.oii in {f}: word={w}")

b_oii_in_plants = sum(1 for f in b_plants for w in folio_tokens[f]
                     if split_skel_vowels(w)[1] == "_.oii")
b_oii_in_non = sum(1 for f in b_non for w in folio_tokens[f]
                   if split_skel_vowels(w)[1] == "_.oii")
print(f"  _.oii total Hand-B plants: {b_oii_in_plants}")
print(f"  _.oii total Hand-B non-plants: {b_oii_in_non}")

print("\n" + "="*72)
print("  HAND A — top 15 vowel-pattern enrichment on plant folios")
print("="*72)
a_rows = enrichment_table(a_plants, a_non, min_hits=10)
print(f"  {'pattern':<14} {'pl_hits':>8} {'nt_hits':>8} "
      f"{'pl_rate':>10} {'nt_rate':>10} {'enr':>8}")
for r in a_rows[:15]:
    enr_str = f"{r['enr']:.2f}x" if r['enr'] != float("inf") else "inf"
    print(f"  {r['pattern']:<14} {r['plant_hits']:>8} {r['non_hits']:>8} "
          f"{r['plant_rate']:>10.5f} {r['non_rate']:>10.5f} {enr_str:>8}")

# Overlap
a_top = {r["pattern"] for r in a_rows[:10]}
b_top = {r["pattern"] for r in b_rows[:10]}
print(f"\n  Top-10 Hand-A enriched: {sorted(a_top)}")
print(f"  Top-10 Hand-B enriched: {sorted(b_top)}")
print(f"  Overlap: {sorted(a_top & b_top)}")
print(f"  Hand-B-only candidates: {sorted(b_top - a_top)}")

# Save
out = ROOT / "outputs" / "hand_b_characterisation.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hand_a": {"plants": len(a_plants), "non_plants": len(a_non)},
    "hand_b": {"plants": len(b_plants), "non_plants": len(b_non),
               "oii_plant_hits": b_oii_in_plants,
               "oii_non_hits": b_oii_in_non},
    "top_hand_b_enriched": [{k: (round(v, 5) if isinstance(v, float) and v != float("inf") else
                                  (999 if v == float("inf") else v))
                             for k, v in r.items()} for r in b_rows[:15]],
    "top_hand_a_enriched": [{k: (round(v, 5) if isinstance(v, float) and v != float("inf") else
                                  (999 if v == float("inf") else v))
                             for k, v in r.items()} for r in a_rows[:15]],
    "a_top10": sorted(a_top),
    "b_top10": sorted(b_top),
    "overlap": sorted(a_top & b_top),
    "b_only": sorted(b_top - a_top),
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
