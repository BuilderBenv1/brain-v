"""
Reproduce Jensen's attractor detection and cross-reference with Brain-V.

Method (matches Jensen paper §2.2-2.4):
  1. Parse Currier/FSG transcription interln16e6.txt to (folio, line_text).
  2. TF-IDF vectorise lines: word-level, ngram 1-2, min_df=2,
     max_features=10000, sublinear_tf=True.
  3. L2-normalise embeddings.
  4. DBSCAN with eps=0.5, min_samples=2, metric=cosine.
  5. Non-noise clusters = semantic attractors. Noise = -1 cluster.

Cross-reference:
  For each attractor, collect the set of folios its lines touch.
  Compare to Brain-V's _.oii-firing folios (Hand A plant marker) and
  _.e.e/_.eeo/_.o.eo-firing folios (Hand B plant markers). Measure
  folio-level overlap and test whether Jensen's method independently
  identifies the same plant-folio subset.
"""
import json
import re
import sys
import csv
import math
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize

ROOT = Path(r"C:\Projects\brain-v")
JENSEN_TRX = ROOT / "raw/research/jensen-interln16e6.txt"
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
PLANT_CSV = ROOT / "raw/research/plant-identifications.csv"

# ----------------------------------------------------------------------
# 1. Parse Currier/FSG transcription
# ----------------------------------------------------------------------
line_re = re.compile(r"<(f?\d+[rv]?\d*)\.(\d+)>(.*?)(?:[=\-]?)$")
raw_lines = []
with JENSEN_TRX.open(encoding="utf-8", errors="ignore") as f:
    for raw in f:
        raw = raw.rstrip("\n")
        m = line_re.match(raw)
        if not m: continue
        folio_raw, line_no, content = m.group(1), m.group(2), m.group(3)
        # Normalise folio to Brain-V convention (f1r, f2r etc.)
        if not folio_raw.startswith("f"):
            folio_raw = "f" + folio_raw
        # Replace Currier punctuation: period = word separator, remove
        # line-continuation = and - at end already consumed by regex
        content = content.replace(",", " ").replace(".", " ")
        content = re.sub(r"[=\-]+$", "", content).strip()
        if not content: continue
        raw_lines.append({"folio": folio_raw, "line": int(line_no),
                          "text": content})

print(f"Parsed {len(raw_lines)} lines from {len({r['folio'] for r in raw_lines})} folios")

# ----------------------------------------------------------------------
# 2-4. TF-IDF + DBSCAN matching Jensen's parameters
# ----------------------------------------------------------------------
texts = [r["text"] for r in raw_lines]
vec = TfidfVectorizer(analyzer="word",
                      ngram_range=(1, 2),
                      min_df=2,
                      max_features=10000,
                      sublinear_tf=True,
                      token_pattern=r"\S+")
X = vec.fit_transform(texts)
X = normalize(X, norm="l2")

print(f"TF-IDF matrix: {X.shape[0]} lines, {X.shape[1]} features")

db = DBSCAN(eps=0.5, min_samples=2, metric="cosine")
labels = db.fit_predict(X)

n_attractors = len({l for l in labels if l >= 0})
n_noise = int((labels == -1).sum())
print(f"Attractors: {n_attractors}   noise: {n_noise} "
      f"({n_noise/len(labels):.1%})")
print(f"(Jensen reported 190 attractors, 87.1% noise over 4,486 lines)")

# ----------------------------------------------------------------------
# 5. Map attractors to folios
# ----------------------------------------------------------------------
attractor_folios = defaultdict(set)
attractor_lines = defaultdict(list)
for i, lbl in enumerate(labels):
    if lbl < 0: continue
    attractor_folios[int(lbl)].add(raw_lines[i]["folio"])
    attractor_lines[int(lbl)].append(i)

# Attractor size distribution
sizes = [len(attractor_lines[a]) for a in attractor_folios]
print(f"\nAttractor sizes — min {min(sizes)}, median {sorted(sizes)[len(sizes)//2]}, "
      f"max {max(sizes)}")

# Top attractors by folio coverage
top_attractors = sorted(attractor_folios.items(), key=lambda x: -len(x[1]))[:10]
print(f"\nTop 10 attractors by folio coverage:")
for aid, folios in top_attractors:
    print(f"  attractor {aid:>4}: {len(folios)} folios, {len(attractor_lines[aid])} lines")

# ----------------------------------------------------------------------
# 6. Identify Brain-V's plant-marker folios (Hand A _.oii firing;
#    Hand B _.e.e / _.eeo / _.o.eo firing)
# ----------------------------------------------------------------------
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

folio_tokens = defaultdict(list)
folio_hand = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_hand[fid] = f.get("currier_language", "?")
    for line in f["lines"]:
        folio_tokens[fid].extend(line["words"])

def has_marker(fid, patterns):
    for w in folio_tokens[fid]:
        _, vp = split_skel_vowels(w)
        if vp in patterns:
            return True
    return False

hand_a_oii_folios = {f for f in folio_tokens
                     if folio_hand.get(f) == "A" and has_marker(f, {"_.oii"})}
hand_b_plant_folios = {f for f in folio_tokens
                       if folio_hand.get(f) == "B"
                       and has_marker(f, {"_.e.e", "_.eeo", "_.o.eo"})}
plant_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        plant_folios.add(r["folio"])

print(f"\nBrain-V marker folios:")
print(f"  Hand-A _.oii firing: {len(hand_a_oii_folios)} folios")
print(f"  Hand-B plant-marker firing: {len(hand_b_plant_folios)} folios")
print(f"  Sherwood+Cohen plant-ID folios: {len(plant_folios)}")

# ----------------------------------------------------------------------
# 7. Cross-reference
# ----------------------------------------------------------------------
# For each Jensen attractor, compute overlap with each Brain-V set.
# A "plant attractor" candidate = attractor whose folios overlap
# strongly with plant-ID folios.

def jaccard(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

def overlap_pct(a_folios, target):
    if not a_folios: return 0.0
    return len(a_folios & target) / len(a_folios)

# Find attractors with high plant-ID overlap
plant_aligned = []
for aid, folios in attractor_folios.items():
    if len(folios) < 2: continue  # need at least 2 folios to be meaningful
    ov_plant = overlap_pct(folios, plant_folios)
    ov_a_oii = overlap_pct(folios, hand_a_oii_folios)
    ov_b_plant = overlap_pct(folios, hand_b_plant_folios)
    plant_aligned.append({
        "attractor": aid, "n_folios": len(folios),
        "n_lines": len(attractor_lines[aid]),
        "overlap_plant": ov_plant,
        "overlap_hand_a_oii": ov_a_oii,
        "overlap_hand_b_plant": ov_b_plant,
        "folios": sorted(folios),
    })

# Top attractors aligned with plant folios
print(f"\n{'='*72}")
print(f"  Top attractors by overlap with Brain-V plant-ID set")
print(f"{'='*72}")
print(f"  {'attr':<5} {'n_fol':>5} {'n_ln':>5} {'%plant':>8} {'%A_oii':>8} {'%B_pl':>7}")
plant_aligned.sort(key=lambda r: -r["overlap_plant"])
for r in plant_aligned[:15]:
    print(f"  {r['attractor']:<5} {r['n_folios']:>5} {r['n_lines']:>5} "
          f"{r['overlap_plant']*100:>7.1f}% {r['overlap_hand_a_oii']*100:>7.1f}% "
          f"{r['overlap_hand_b_plant']*100:>6.1f}%")

# Top aligned with Hand-A _.oii set
print(f"\n{'='*72}")
print(f"  Top attractors by overlap with Brain-V Hand-A _.oii-firing folios")
print(f"{'='*72}")
plant_aligned.sort(key=lambda r: -r["overlap_hand_a_oii"])
for r in plant_aligned[:15]:
    print(f"  {r['attractor']:<5} {r['n_folios']:>5} {r['n_lines']:>5} "
          f"{r['overlap_plant']*100:>7.1f}% {r['overlap_hand_a_oii']*100:>7.1f}% "
          f"{r['overlap_hand_b_plant']*100:>6.1f}%")

# Top aligned with Hand-B plant-marker set
print(f"\n{'='*72}")
print(f"  Top attractors by overlap with Brain-V Hand-B plant-marker folios")
print(f"{'='*72}")
plant_aligned.sort(key=lambda r: -r["overlap_hand_b_plant"])
for r in plant_aligned[:15]:
    print(f"  {r['attractor']:<5} {r['n_folios']:>5} {r['n_lines']:>5} "
          f"{r['overlap_plant']*100:>7.1f}% {r['overlap_hand_a_oii']*100:>7.1f}% "
          f"{r['overlap_hand_b_plant']*100:>6.1f}%")

# ----------------------------------------------------------------------
# Section-level overlap: do Jensen's section separations match
# Brain-V's scribe-section division?
# ----------------------------------------------------------------------
folio_section = {f["folio"]: f["section"] for f in CORPUS["folios"]}
section_folios = defaultdict(set)
for fid, sec in folio_section.items():
    section_folios[sec].add(fid)

# For each attractor, which section dominates its folio set?
print(f"\n{'='*72}")
print(f"  Attractor section dominance (attractor folio set's majority section)")
print(f"{'='*72}")
sec_dominant = Counter()
total_attr = 0
for aid, folios in attractor_folios.items():
    if len(folios) < 2: continue
    total_attr += 1
    sec_counts = Counter(folio_section.get(f, "?") for f in folios)
    top_sec, top_n = sec_counts.most_common(1)[0]
    # Only count if strict majority in a single section
    if top_n / len(folios) >= 0.75:
        sec_dominant[top_sec] += 1
print(f"  Total attractors with >=2 folios: {total_attr}")
print(f"  Attractors with >=75% of folios in a single section:")
for sec, n in sec_dominant.most_common():
    print(f"    {sec:<18} {n:>4}")
section_concentration_rate = sum(sec_dominant.values()) / total_attr if total_attr else 0
print(f"  Section-concentration rate: {section_concentration_rate:.1%}")

# ----------------------------------------------------------------------
# Global folio-level overlap stats
# ----------------------------------------------------------------------
# All folios touched by any attractor with >=2 folios
attractor_touched = set()
for aid, folios in attractor_folios.items():
    if len(folios) >= 2:
        attractor_touched |= folios

print(f"\n{'='*72}")
print(f"  GLOBAL OVERLAP — folios touched by attractors >=2-fol vs Brain-V sets")
print(f"{'='*72}")
print(f"  Touched by attractors (size>=2):  {len(attractor_touched)}")
print(f"  Brain-V _.oii Hand-A:              {len(hand_a_oii_folios)}")
print(f"  Brain-V Hand-B plant markers:      {len(hand_b_plant_folios)}")
print(f"  Sherwood+Cohen plant-ID:           {len(plant_folios)}")
print()
print(f"  Jaccard(attractor-touched, _.oii A)   = {jaccard(attractor_touched, hand_a_oii_folios):.3f}")
print(f"  Jaccard(attractor-touched, HandB pl)  = {jaccard(attractor_touched, hand_b_plant_folios):.3f}")
print(f"  Jaccard(attractor-touched, plant-ID)  = {jaccard(attractor_touched, plant_folios):.3f}")
print()
print(f"  |_.oii A  intersect attractor-touched|  = {len(hand_a_oii_folios & attractor_touched)} / "
      f"{len(hand_a_oii_folios)}")
print(f"  |HandB pl intersect attractor-touched|  = {len(hand_b_plant_folios & attractor_touched)} / "
      f"{len(hand_b_plant_folios)}")
print(f"  |plant-ID intersect attractor-touched|  = {len(plant_folios & attractor_touched)} / "
      f"{len(plant_folios)}")

# Save
out = ROOT / "outputs" / "jensen_cross_reference.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "jensen_attractors_count": n_attractors,
    "jensen_reported": 190,
    "noise_pct": n_noise/len(labels),
    "brainv_sets": {
        "hand_a_oii": sorted(hand_a_oii_folios),
        "hand_b_plant": sorted(hand_b_plant_folios),
        "sherwood_cohen_plant": sorted(plant_folios),
    },
    "section_concentration_rate": section_concentration_rate,
    "section_dominance_counts": dict(sec_dominant),
    "global_overlap": {
        "attractor_touched_n": len(attractor_touched),
        "jaccard_with_hand_a_oii": jaccard(attractor_touched, hand_a_oii_folios),
        "jaccard_with_hand_b_plant": jaccard(attractor_touched, hand_b_plant_folios),
        "jaccard_with_plant_id": jaccard(attractor_touched, plant_folios),
    },
    "top_plant_aligned_attractors": [
        {k: v for k, v in r.items() if k != "folios"} for r in
        sorted(plant_aligned, key=lambda r: -r["overlap_plant"])[:30]
    ],
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
