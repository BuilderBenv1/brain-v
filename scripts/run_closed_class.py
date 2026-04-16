"""
Execute pre-registered H-BV-CLOSED-CLASS-01 (locked in commit cb85f39).

For each Hand-B plant marker (_.e.e, _.eeo, _.o.eo), extract every
Hand-B plant-folio word exactly matching that vowel pattern. Count
unique consonant skeletons. Apply the pre-registered rule:
  top-5 skeletons > 80% of tokens -> CLOSED, else OPEN.

Also cross-hand: compare Hand-B skeletons to Hand-A _.oii closed set
{kn, sn, dn, tkn, kkn, dr}.
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

# Hand-B plant folios (non-CONFLICT)
plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        plant_folios.add(r["folio"])

hand_b_plant_folios = [f for f in plant_folios
                       if folio_hand.get(f) == "B" and f in folio_tokens]
print(f"Hand-B plant folios: {len(hand_b_plant_folios)}")

MARKERS = ["_.e.e", "_.eeo", "_.o.eo"]
HAND_A_OII_STEMS = {"kn", "sn", "dn", "tkn", "kkn", "dr"}

# Collect (word, skeleton) per marker pattern
per_marker = {m: [] for m in MARKERS}
for fid in hand_b_plant_folios:
    for w in folio_tokens[fid]:
        sk, vp = split_skel_vowels(w)
        if vp in per_marker:
            per_marker[vp].append({"folio": fid, "word": w, "skeleton": sk})

# Per-marker analysis
print("\n" + "="*72)
print("  PER-MARKER CLOSED-CLASS TEST")
print("="*72)
per_marker_verdicts = {}
for m in MARKERS:
    entries = per_marker[m]
    print(f"\n  Marker: {m}")
    print(f"  Total Hand-B plant-folio tokens: {len(entries)}")
    if not entries:
        print(f"  SKIP: no tokens")
        per_marker_verdicts[m] = {"verdict": "NO_DATA", "n": 0}
        continue
    sk_counts = Counter(e["skeleton"] for e in entries)
    print(f"  Unique skeletons: {len(sk_counts)}")
    print(f"  Skeleton distribution:")
    top5 = sk_counts.most_common(5)
    for sk, c in top5:
        pct = c / len(entries) * 100
        print(f"    {sk:<10} {c:>3}  ({pct:>5.1f}%)")
    if len(sk_counts) > 5:
        tail = sum(c for sk, c in sk_counts.most_common()[5:])
        print(f"    [others] {tail:>3}  ({tail/len(entries)*100:>5.1f}%)")
    top5_sum = sum(c for _, c in top5)
    top5_pct = top5_sum / len(entries) * 100
    print(f"  Top-5 coverage: {top5_sum}/{len(entries)} = {top5_pct:.1f}%")
    verdict = "CLOSED" if top5_pct > 80 else "OPEN"
    print(f"  -> {verdict}")
    per_marker_verdicts[m] = {
        "verdict": verdict,
        "n": len(entries),
        "unique_skeletons": len(sk_counts),
        "top_5": [{"skeleton": sk, "count": c} for sk, c in top5],
        "top_5_coverage": round(top5_pct/100, 4),
    }

# Combined analysis
print("\n" + "="*72)
print("  COMBINED (all three markers)")
print("="*72)
all_entries = [e for m in MARKERS for e in per_marker[m]]
all_sk_counts = Counter(e["skeleton"] for e in all_entries)
print(f"  Total tokens: {len(all_entries)}")
print(f"  Unique skeletons: {len(all_sk_counts)}")
top10_all = all_sk_counts.most_common(10)
print(f"  Top 10 skeletons overall:")
for sk, c in top10_all:
    pct = c/len(all_entries)*100
    hand_a_tag = " [ALSO IN HAND-A _.oii]" if sk in HAND_A_OII_STEMS else ""
    print(f"    {sk:<10} {c:>3}  ({pct:>5.1f}%){hand_a_tag}")

# Cross-hand overlap
print("\n" + "="*72)
print("  CROSS-HAND STEM OVERLAP")
print("="*72)
hand_b_stems = set(all_sk_counts.keys())
overlap = hand_b_stems & HAND_A_OII_STEMS
print(f"  Hand-A _.oii stems:   {sorted(HAND_A_OII_STEMS)}")
print(f"  Hand-B marker stems:  {sorted(hand_b_stems)}")
print(f"  Intersection:         {sorted(overlap)}  ({len(overlap)}/{len(HAND_A_OII_STEMS)})")

# Overall decision
closed_count = sum(1 for v in per_marker_verdicts.values() if v["verdict"] == "CLOSED")
open_count = sum(1 for v in per_marker_verdicts.values() if v["verdict"] == "OPEN")
print("\n" + "="*72)
print("  PRE-REGISTERED DECISION")
print("="*72)
print(f"  Markers CLOSED: {closed_count}/3")
print(f"  Markers OPEN:   {open_count}/3")

if closed_count == 3:
    overall = "CLOSED (all three)"
    print(f"  -> ALL THREE CLOSED")
    print(f"     Hand-B plant markers use closed-class vocabularies, like Hand A.")
elif closed_count >= 1 and open_count >= 1:
    overall = "MIXED"
    print(f"  -> MIXED")
    print(f"     {closed_count} closed, {open_count} open. Hand B's plant markers")
    print(f"     are structurally heterogeneous.")
elif open_count == 3:
    overall = "OPEN (all three)"
    print(f"  -> ALL THREE OPEN")
    print(f"     Hand B encodes something structurally different from Hand A.")
else:
    overall = "INDETERMINATE"

if overlap:
    print(f"\n  Cross-hand overlap: {len(overlap)} shared stems ({sorted(overlap)}).")
    print(f"  Hand B and Hand A share part of their closed-class vocabulary.")
else:
    print(f"\n  Cross-hand overlap: 0 shared stems.")
    print(f"  Scribe-specific closed-class vocabularies, same function.")

out = ROOT / "outputs" / "closed_class_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-CLOSED-CLASS-01",
    "locked_in_commit": "cb85f39",
    "hand_b_plant_folios": len(hand_b_plant_folios),
    "per_marker": per_marker_verdicts,
    "combined": {
        "total_tokens": len(all_entries),
        "unique_skeletons": len(all_sk_counts),
        "top_10": [{"skeleton": sk, "count": c,
                    "in_hand_a_oii_class": sk in HAND_A_OII_STEMS}
                   for sk, c in top10_all],
    },
    "cross_hand": {
        "hand_a_oii_stems": sorted(HAND_A_OII_STEMS),
        "hand_b_marker_stems": sorted(hand_b_stems),
        "overlap": sorted(overlap),
        "overlap_count": len(overlap),
    },
    "overall_verdict": overall,
    "closed_count": closed_count,
    "open_count": open_count,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
