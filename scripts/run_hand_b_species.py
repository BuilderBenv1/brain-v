"""
Execute pre-registered H-BV-HAND-B-SPECIES-01 (locked in commit bbf01c8).

PRIMARY: species-level skeleton consistency across Hand-B plant folios.
SECONDARY: stem concentration — mean folios-per-stem for recurring stems.
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

MARKERS = {"_.e.e", "_.eeo", "_.o.eo"}

folio_tokens = defaultdict(list)
folio_hand = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_hand[fid] = f.get("currier_language", "?")
    for line in f["lines"]:
        folio_tokens[fid].extend(line["words"])

# Hand-B plant records
plant_records = []
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        fid = r["folio"]
        if folio_hand.get(fid) != "B": continue
        if fid not in folio_tokens: continue
        plant_records.append(r)

print(f"Hand-B plant records: {len(plant_records)}")

# Per-folio marker-word extraction
folio_marker_entries = defaultdict(list)  # fid -> [(word, skel, vp)]
for r in plant_records:
    fid = r["folio"]
    for w in folio_tokens[fid]:
        sk, vp = split_skel_vowels(w)
        if vp in MARKERS:
            folio_marker_entries[fid].append((w, sk, vp))

firing_folios = [fid for fid in folio_marker_entries if folio_marker_entries[fid]]
print(f"Hand-B plant folios firing any marker: {len(firing_folios)}")
total_tokens = sum(len(folio_marker_entries[f]) for f in firing_folios)
print(f"Total marker tokens: {total_tokens}")

# Show per-folio
print("\nPer-folio Hand-B plant-marker words:")
for fid in sorted(firing_folios):
    sp = next((r.get("latin_name") or r.get("common_name")
               for r in plant_records if r["folio"] == fid), "?")
    entries = folio_marker_entries[fid]
    pairs = ", ".join(f"{w}[{sk}]" for w, sk, vp in entries)
    print(f"  {fid:<8} {sp[:28]:<28}  n={len(entries)}  {pairs}")

# =========================================================================
# PRIMARY: species-level repetition test
# =========================================================================
def species_key(r):
    lat = (r.get("latin_name") or "").strip().lower()
    if lat: return lat
    return (r.get("common_name") or "").strip().lower() or None

def genus_key(r):
    lat = (r.get("latin_name") or "").strip().lower()
    return lat.split()[0] if lat else None

species_folios = defaultdict(list)
genus_folios = defaultdict(list)
for r in plant_records:
    sp = species_key(r); gn = genus_key(r)
    if sp: species_folios[sp].append(r["folio"])
    if gn: genus_folios[gn].append(r["folio"])

species_ge2 = {sp: fs for sp, fs in species_folios.items() if len(fs) >= 2}
genus_ge2 = {gn: fs for gn, fs in genus_folios.items() if len(fs) >= 2}
print(f"\nSpecies on >=2 Hand-B folios: {len(species_ge2)}")
print(f"Genera on >=2 Hand-B folios:  {len(genus_ge2)}")

print("\n" + "="*72)
print("  PRIMARY: species-level skeleton consistency")
print("="*72)
species_with_shared = []
for sp, folios in species_ge2.items():
    firing = [f for f in folios if folio_marker_entries.get(f)]
    if len(firing) < 2: continue
    per_folio = {f: [sk for _, sk, _ in folio_marker_entries[f]] for f in firing}
    stems = Counter()
    for f, sks in per_folio.items():
        for sk in set(sks): stems[sk] += 1
    shared = [(sk, n) for sk, n in stems.items() if n >= 2]
    print(f"  {sp}:")
    for f, sks in per_folio.items():
        print(f"    {f}: {sks}")
    if shared:
        species_with_shared.append((sp, shared, per_folio))
        print(f"    SHARED: {shared}")
if not species_with_shared:
    print("  (no species with >=2 Hand-B folios both firing markers)")

print("\n  GENUS-LEVEL (secondary):")
genera_with_shared = []
for gn, folios in genus_ge2.items():
    firing = [f for f in folios if folio_marker_entries.get(f)]
    if len(firing) < 2: continue
    per_folio = {f: [sk for _, sk, _ in folio_marker_entries[f]] for f in firing}
    stems = Counter()
    for f, sks in per_folio.items():
        for sk in set(sks): stems[sk] += 1
    shared = [(sk, n) for sk, n in stems.items() if n >= 2]
    print(f"  genus {gn}: folios {list(per_folio.keys())}")
    for f, sks in per_folio.items():
        print(f"    {f}: {sks}")
    if shared:
        genera_with_shared.append((gn, shared, per_folio))
        print(f"    SHARED: {shared}")
if not genera_with_shared and not genus_ge2:
    print("  (no genera on >=2 Hand-B folios)")

# =========================================================================
# SECONDARY: stem concentration
# =========================================================================
print("\n" + "="*72)
print("  SECONDARY: stem concentration (folios-per-stem)")
print("="*72)

stem_to_folios = defaultdict(set)
for fid, entries in folio_marker_entries.items():
    for w, sk, vp in entries:
        stem_to_folios[sk].add(fid)

# Stems appearing at least twice overall
recurring = {sk: fs for sk, fs in stem_to_folios.items()
             if sum(1 for f, es in folio_marker_entries.items()
                    for w, s, v in es if s == sk) >= 2}
# Stem frequency count (total tokens)
stem_token_count = Counter()
for fid, entries in folio_marker_entries.items():
    for w, sk, vp in entries:
        stem_token_count[sk] += 1

print(f"  Unique stems: {len(stem_to_folios)}")
recurring_stems = [sk for sk, c in stem_token_count.items() if c >= 2]
print(f"  Stems with >=2 token occurrences: {len(recurring_stems)}")

if recurring_stems:
    folios_per_stem = [len(stem_to_folios[sk]) for sk in recurring_stems]
    mean_fps = statistics.mean(folios_per_stem)
    med_fps = statistics.median(folios_per_stem)
    max_fps = max(folios_per_stem)
    print(f"  Folios-per-stem (recurring): mean {mean_fps:.2f}, "
          f"median {med_fps}, max {max_fps}")
    print(f"\n  Per-stem detail:")
    print(f"  {'stem':<10} {'tokens':>7} {'folios':>7}  folios")
    for sk in sorted(recurring_stems, key=lambda x: -stem_token_count[x]):
        fs = sorted(stem_to_folios[sk])
        print(f"  {sk:<10} {stem_token_count[sk]:>7} {len(fs):>7}  {fs}")
else:
    mean_fps = 0; med_fps = 0; max_fps = 0
    print("  No recurring stems.")

# =========================================================================
# Decision
# =========================================================================
print("\n" + "="*72)
print("  PRE-REGISTERED DECISION")
print("="*72)

primary_confirmed = len(species_with_shared) >= 3 and len(
    {s for sp, sh, pf in species_with_shared for s in (x[0] for x in sh)}
) >= 3
primary_partial = (len(species_with_shared) >= 1 or len(genera_with_shared) >= 1)

if primary_confirmed:
    primary = "CONFIRMED"
elif primary_partial:
    primary = "PARTIAL"
else:
    primary = "REFUTED"

if recurring_stems:
    if mean_fps <= 1.5:
        secondary = "CONCENTRATED (stems folio-specific)"
    elif mean_fps >= 3.0:
        secondary = "DIFFUSE (stems not folio-specific)"
    else:
        secondary = "INTERMEDIATE"
else:
    secondary = "NO_RECURRING"

print(f"  PRIMARY (species-level): {primary}")
print(f"    Species with shared skeleton: {len(species_with_shared)}")
print(f"    Genera with shared skeleton: {len(genera_with_shared)}")
print(f"  SECONDARY (stem concentration): {secondary}")
print(f"    Mean folios-per-stem (recurring): {mean_fps:.2f}")

# Overall
if primary == "CONFIRMED":
    overall = "CONFIRMED"
elif primary == "REFUTED" and secondary.startswith("CONCENTRATED"):
    overall = "PARTIAL (species-level refuted but stems folio-specific)"
elif primary == "REFUTED" and secondary.startswith("DIFFUSE"):
    overall = "REFUTED"
elif primary == "PARTIAL":
    overall = "PARTIAL"
else:
    overall = secondary

print(f"\n  OVERALL: {overall}")

out = ROOT / "outputs" / "hand_b_species_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-HAND-B-SPECIES-01",
    "locked_in_commit": "bbf01c8",
    "n_hand_b_plant_folios": len(plant_records),
    "n_firing_folios": len(firing_folios),
    "total_marker_tokens": total_tokens,
    "species_ge2_count": len(species_ge2),
    "genera_ge2_count": len(genus_ge2),
    "primary_species_with_shared": [
        {"species": sp, "shared_skeletons": sh}
        for sp, sh, pf in species_with_shared
    ],
    "primary_genera_with_shared": [
        {"genus": gn, "shared_skeletons": sh}
        for gn, sh, pf in genera_with_shared
    ],
    "secondary_stem_concentration": {
        "unique_stems": len(stem_to_folios),
        "recurring_stems_ge2_tokens": len(recurring_stems),
        "mean_folios_per_stem": round(mean_fps, 3) if recurring_stems else None,
        "median_folios_per_stem": med_fps if recurring_stems else None,
        "max_folios_per_stem": max_fps if recurring_stems else None,
        "stem_detail": {sk: {"tokens": stem_token_count[sk],
                             "folios": sorted(stem_to_folios[sk])}
                        for sk in recurring_stems},
    },
    "primary_verdict": primary,
    "secondary_verdict": secondary,
    "overall_verdict": overall,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
