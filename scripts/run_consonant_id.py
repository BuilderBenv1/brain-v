"""
Execute pre-registered H-BV-CONSONANT-ID-01 (locked in commit 7fc990f).

For each Hand-A plant folio where _.oii fires, extract every word whose
vowel pattern is exactly _.oii. Record its consonant skeleton. Group
results by Sherwood-assigned species. For species appearing on >=2
folios, test whether the same skeleton recurs.

Decision rule:
  >=3 species x >=2 folios each with SAME skeleton AND different species
  using different skeletons -> CONFIRMED
  Weaker pattern -> MARGINAL
  No species repeats a skeleton -> REFUTED
"""
import csv
import json
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
folio_tokens = defaultdict(list)
folio_hand = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_hand[fid] = f.get("currier_language", "?")
    for line in f["lines"]:
        folio_tokens[fid].extend(line["words"])

# Load plant IDs (exclude conflicts). Capture both Latin and common name.
plant_records = []
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        plant_records.append(r)

# Group folios by species (Latin if present, else common)
def species_key(r):
    lat = (r.get("latin_name") or "").strip().lower()
    if lat: return lat
    return (r.get("common_name") or "").strip().lower() or None

def genus_key(r):
    lat = (r.get("latin_name") or "").strip().lower()
    if lat: return lat.split()[0]
    return None

species_folios = defaultdict(list)
genus_folios = defaultdict(list)
for r in plant_records:
    fid = r["folio"]
    if folio_hand.get(fid) != "A": continue
    if fid not in folio_tokens: continue
    sp = species_key(r); gn = genus_key(r)
    if sp: species_folios[sp].append((fid, r.get("latin_name"), r.get("common_name")))
    if gn: genus_folios[gn].append((fid, r.get("latin_name"), r.get("common_name")))

print(f"Hand-A plant records total: {sum(1 for r in plant_records if folio_hand.get(r['folio']) == 'A')}")
print(f"Unique species on Hand-A folios: {len(species_folios)}")
print(f"Species appearing on >=2 Hand-A folios: "
      f"{sum(1 for fs in species_folios.values() if len(fs) >= 2)}")
print(f"Unique genera on Hand-A folios: {len(genus_folios)}")
print(f"Genera appearing on >=2 Hand-A folios: "
      f"{sum(1 for fs in genus_folios.values() if len(fs) >= 2)}")

# Extract _.oii words per Hand-A plant folio
oii_words = defaultdict(list)  # folio -> list of (word, skeleton)
for r in plant_records:
    fid = r["folio"]
    if folio_hand.get(fid) != "A": continue
    if fid not in folio_tokens: continue
    for w in folio_tokens[fid]:
        sk, vp = split_skel_vowels(w)
        if vp == "_.oii":
            oii_words[fid].append((w, sk))

oii_firing = [fid for fid in oii_words if oii_words[fid]]
print(f"\nHand-A plant folios with >=1 _.oii fire: {len(oii_firing)}")
total_oii = sum(len(oii_words[f]) for f in oii_firing)
print(f"Total _.oii words across those folios: {total_oii}")

# Show raw data per firing folio
print(f"\nPer-folio _.oii words and skeletons:")
for fid in sorted(oii_firing):
    sp = next((r.get("latin_name") or r.get("common_name")
               for r in plant_records if r["folio"] == fid), "?")
    words = oii_words[fid]
    pairs = ", ".join(f"{w}[{sk}]" for w, sk in words)
    print(f"  {fid:<8} {sp[:30]:<30} n={len(words)}  {pairs}")

# =========================================================================
# Test: for species with >=2 Hand-A folios, check skeleton repetition
# =========================================================================
print(f"\n{'='*72}")
print(f"  SPECIES-LEVEL TEST")
print(f"{'='*72}")

species_level_results = []
for sp, folios in species_folios.items():
    if len(folios) < 2: continue
    # Gather skeletons per folio
    per_folio_skels = {}
    for fid, lat, com in folios:
        sks = [sk for w, sk in oii_words.get(fid, [])]
        per_folio_skels[fid] = sks
    # Only interesting if >=2 folios have >=1 _.oii fire
    firing = {fid: sks for fid, sks in per_folio_skels.items() if sks}
    if len(firing) < 2:
        continue
    # Count skeletons appearing across folios
    all_skels = Counter()
    for fid, sks in firing.items():
        for sk in set(sks):
            all_skels[sk] += 1  # count of folios that use this skeleton
    shared = [(sk, n) for sk, n in all_skels.items() if n >= 2]
    species_level_results.append({
        "species": sp,
        "firing_folios": list(firing.keys()),
        "per_folio_skeletons": per_folio_skels,
        "shared_skeletons": shared,
    })
    print(f"\n  {sp}")
    for fid, sks in firing.items():
        print(f"    {fid}: {sks}")
    if shared:
        print(f"    SHARED SKELETONS: {shared}")

# =========================================================================
# Genus-level secondary test
# =========================================================================
print(f"\n{'='*72}")
print(f"  GENUS-LEVEL TEST (secondary)")
print(f"{'='*72}")
genus_level_results = []
for gn, folios in genus_folios.items():
    if len(folios) < 2: continue
    per_folio_skels = {}
    for fid, lat, com in folios:
        sks = [sk for w, sk in oii_words.get(fid, [])]
        per_folio_skels[fid] = sks
    firing = {fid: sks for fid, sks in per_folio_skels.items() if sks}
    if len(firing) < 2: continue
    all_skels = Counter()
    for fid, sks in firing.items():
        for sk in set(sks):
            all_skels[sk] += 1
    shared = [(sk, n) for sk, n in all_skels.items() if n >= 2]
    genus_level_results.append({
        "genus": gn,
        "firing_folios": list(firing.keys()),
        "per_folio_skeletons": per_folio_skels,
        "shared_skeletons": shared,
    })
    print(f"\n  genus {gn}")
    for fid, sks in firing.items():
        sp = next((r.get("latin_name") for r in plant_records if r["folio"] == fid), "?")
        print(f"    {fid} ({sp}): {sks}")
    if shared:
        print(f"    SHARED SKELETONS: {shared}")

# =========================================================================
# Decision
# =========================================================================
print(f"\n{'='*72}")
print(f"  PRE-REGISTERED DECISION")
print(f"{'='*72}")

# Count species with shared skeletons and distinct dominant skeletons
species_with_shared = [r for r in species_level_results if r["shared_skeletons"]]
# Dominant skeleton per species: the most-common across firing folios
dom = {}
for r in species_with_shared:
    sk_counts = Counter(sk for sks in r["per_folio_skeletons"].values() for sk in sks)
    if sk_counts:
        dom[r["species"]] = sk_counts.most_common(1)[0][0]
distinct_dom = len(set(dom.values()))

print(f"  Species on >=2 Hand-A folios with >=1 _.oii fire each: "
      f"{sum(1 for r in species_level_results if len(r['firing_folios']) >= 2)}")
print(f"  Species with SHARED skeleton across folios: {len(species_with_shared)}")
print(f"  Distinct dominant skeletons: {distinct_dom}")

if len(species_with_shared) >= 3 and distinct_dom >= 3:
    verdict = "CONFIRMED"
    print(f"  -> CONFIRMED: >=3 species with repeated skeleton AND "
          f"distinct species use distinct skeletons.")
elif species_with_shared or genus_level_results:
    # Check genus-level shared
    gen_shared = [r for r in genus_level_results if r["shared_skeletons"]]
    if gen_shared:
        verdict = "MARGINAL"
        print(f"  -> MARGINAL: {len(species_with_shared)} species and "
              f"{len(gen_shared)} genera show repeated skeletons.")
    else:
        verdict = "MARGINAL"
        print(f"  -> MARGINAL: {len(species_with_shared)} species show shared skeletons, "
              f"below the 3-species threshold.")
else:
    verdict = "REFUTED"
    print(f"  -> REFUTED: no species shows repeated skeleton across its folios.")
    print(f"     _.oii appears to be a category-level marker only.")

# Save
out = ROOT / "outputs" / "consonant_id_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-CONSONANT-ID-01",
    "locked_in_commit": "7fc990f",
    "hand_a_plant_folios_firing_oii": len(oii_firing),
    "total_oii_words": total_oii,
    "species_with_multiple_hand_a_folios": {
        sp: [{"folio": f[0], "latin": f[1], "common": f[2]} for f in folios]
        for sp, folios in species_folios.items() if len(folios) >= 2
    },
    "genera_with_multiple_hand_a_folios": {
        gn: [{"folio": f[0], "latin": f[1], "common": f[2]} for f in folios]
        for gn, folios in genus_folios.items() if len(folios) >= 2
    },
    "species_level_results": species_level_results,
    "genus_level_results": genus_level_results,
    "verdict": verdict,
    "distinct_dominant_skeletons": distinct_dom,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
print(f"VERDICT: {verdict}")
