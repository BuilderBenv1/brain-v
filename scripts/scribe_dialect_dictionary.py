"""
Build a (hand, content-type) marker dictionary.

For each scribal hand (A, B) and each manuscript section, identify vowel
patterns that enrich within that section vs out-of-section folios (same
hand). Controls for hand-specific dialects: the "Hand A pharmaceutical
marker" is a pattern that fires more on Hand-A pharma folios than on
Hand-A non-pharma folios.

Produces a matrix:
  section × hand → list of enriched patterns
This gives the first content-type decoder without a language model.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

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
folio_section = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_hand[fid] = f.get("currier_language","?")
    folio_section[fid] = f["section"]
    for line in f["lines"]:
        folio_tokens[fid].extend(line["words"])

SECTIONS = ["pharmaceutical", "biological", "astronomical", "zodiac",
            "cosmological", "recipes", "text-only", "herbal"]

def section_hand_folios(section, hand):
    return [f for f,m in folio_hand.items()
            if folio_section.get(f) == section and m == hand
            and len(folio_tokens[f]) >= 20]

def other_same_hand(section, hand):
    return [f for f,m in folio_hand.items()
            if folio_section.get(f) != section and m == hand
            and folio_section.get(f) != "?"
            and len(folio_tokens[f]) >= 20]

def pattern_tally(folios):
    vp = Counter(); total = 0
    for f in folios:
        for w in folio_tokens[f]:
            _, p = split_skel_vowels(w)
            vp[p] += 1; total += 1
    return vp, total

def enriched_patterns(in_folios, out_folios, min_hits=10, min_enr=3.0):
    ivp, it = pattern_tally(in_folios)
    ovp, ot = pattern_tally(out_folios)
    rows = []
    for p, ih in ivp.items():
        if ih < min_hits or not p: continue
        oh = ovp.get(p, 0)
        i_rate = ih/it if it else 0
        o_rate = oh/ot if ot else 0
        if o_rate > 0:
            enr = i_rate / o_rate
        else:
            enr = float("inf")
        if enr >= min_enr or (enr == float("inf") and ih >= min_hits):
            rows.append({"pattern": p, "in_hits": ih, "out_hits": oh,
                         "in_rate": i_rate, "out_rate": o_rate, "enr": enr})
    rows.sort(key=lambda r: -r["enr"] if r["enr"] != float("inf") else -1e9)
    return rows

print("="*72)
print("  SCRIBE-SECTION DIALECT DICTIONARY")
print("="*72)
print("  For each (section, hand): vowel patterns that enrich in-section")
print("  vs same-hand out-of-section. Min 10 in-section hits, min 3x enr.")
print()

dictionary = {}

for section in SECTIONS:
    print(f"\n{'='*72}")
    print(f"  SECTION: {section}")
    print(f"{'='*72}")
    for hand in ("A", "B"):
        ins = section_hand_folios(section, hand)
        outs = other_same_hand(section, hand)
        if not ins or not outs:
            print(f"\n  Hand {hand}: n_in={len(ins)} n_out={len(outs)} — skipping")
            continue
        rows = enriched_patterns(ins, outs, min_hits=10, min_enr=3.0)
        print(f"\n  Hand {hand}: n_in={len(ins)} n_out={len(outs)}")
        print(f"  {'pattern':<14} {'in_hits':>8} {'out_hits':>8} "
              f"{'in_rate':>9} {'out_rate':>9} {'enr':>8}")
        if not rows:
            print(f"  (no patterns with >=10 hits and >=3x enrichment)")
        for r in rows[:12]:
            enr_str = f"{r['enr']:.2f}x" if r['enr'] != float("inf") else "inf"
            print(f"  {r['pattern']:<14} {r['in_hits']:>8} {r['out_hits']:>8} "
                  f"{r['in_rate']:>9.5f} {r['out_rate']:>9.5f} {enr_str:>8}")
        # Store only the top 8 markers
        dictionary.setdefault(section, {})[hand] = [
            {"pattern": r["pattern"], "in_hits": r["in_hits"],
             "out_hits": r["out_hits"],
             "in_rate": round(r["in_rate"], 5),
             "out_rate": round(r["out_rate"], 5),
             "enr": round(r["enr"], 2) if r["enr"] != float("inf") else 9999}
            for r in rows[:8]
        ]

# =========================================================================
# Cross-hand overlap summary per section
# =========================================================================
print("\n" + "="*72)
print("  CROSS-HAND OVERLAP PER SECTION  (does each hand have own dialect?)")
print("="*72)
for section in SECTIONS:
    a = {r["pattern"] for r in dictionary.get(section, {}).get("A", [])}
    b = {r["pattern"] for r in dictionary.get(section, {}).get("B", [])}
    if not a or not b:
        continue
    overlap = a & b
    a_only = a - b
    b_only = b - a
    print(f"\n  {section:<14} Hand A n={len(a)}  Hand B n={len(b)}  "
          f"overlap={len(overlap)}/{min(len(a),len(b))}")
    print(f"    A-only: {sorted(a_only)}")
    print(f"    B-only: {sorted(b_only)}")
    print(f"    shared: {sorted(overlap)}")

# =========================================================================
# Cross-section overlap per hand — dialect consistency
# =========================================================================
print("\n" + "="*72)
print("  CROSS-SECTION OVERLAP PER HAND  (does a hand reuse patterns?)")
print("="*72)
for hand in ("A", "B"):
    print(f"\n  Hand {hand}:")
    for section in SECTIONS:
        pats = {r["pattern"] for r in dictionary.get(section, {}).get(hand, [])}
        if pats:
            print(f"    {section:<14} {sorted(pats)}")
    # Compute pairwise overlap
    sec_sets = {s: {r["pattern"] for r in dictionary.get(s,{}).get(hand,[])}
                for s in SECTIONS}
    print(f"\n    Pattern uniqueness within Hand {hand}:")
    all_patterns = set()
    for s in SECTIONS: all_patterns |= sec_sets.get(s, set())
    for p in sorted(all_patterns):
        appears_in = [s for s in SECTIONS if p in sec_sets.get(s, set())]
        if len(appears_in) > 1:
            print(f"      {p} appears in: {appears_in}")

# =========================================================================
# Hand-A / Hand-B vowel dialect signature
# =========================================================================
print("\n" + "="*72)
print("  HAND DIALECT SIGNATURES")
print("="*72)
def count_vowel_chars(patterns):
    c = Counter()
    for p in patterns:
        for ch in p:
            if ch in "aoei": c[ch] += 1
    return c

a_all = set()
b_all = set()
for section in SECTIONS:
    a_all |= {r["pattern"] for r in dictionary.get(section,{}).get("A",[])}
    b_all |= {r["pattern"] for r in dictionary.get(section,{}).get("B",[])}
print(f"  Hand A unique markers across sections: {len(a_all)}")
print(f"  Hand B unique markers across sections: {len(b_all)}")
a_vc = count_vowel_chars(a_all); b_vc = count_vowel_chars(b_all)
print(f"  Hand A vowel char counts in markers: {dict(a_vc)}")
print(f"  Hand B vowel char counts in markers: {dict(b_vc)}")
print(f"  Ratio o/e Hand A: {a_vc['o']/a_vc['e'] if a_vc['e'] else float('inf'):.2f}")
print(f"  Ratio o/e Hand B: {b_vc['o']/b_vc['e'] if b_vc['e'] else float('inf'):.2f}")

# Save
out = ROOT / "outputs" / "scribe_dialect_dictionary.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "dictionary": dictionary,
    "cross_hand_overlap": {
        section: {
            "A": sorted({r["pattern"] for r in dictionary.get(section,{}).get("A",[])}),
            "B": sorted({r["pattern"] for r in dictionary.get(section,{}).get("B",[])}),
            "overlap": sorted({r["pattern"] for r in dictionary.get(section,{}).get("A",[])} &
                              {r["pattern"] for r in dictionary.get(section,{}).get("B",[])}),
        }
        for section in SECTIONS
        if dictionary.get(section,{}).get("A") and dictionary.get(section,{}).get("B")
    },
    "hand_dialect": {
        "A": {"n_markers": len(a_all), "vowel_chars": dict(a_vc)},
        "B": {"n_markers": len(b_all), "vowel_chars": dict(b_vc)},
    },
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
