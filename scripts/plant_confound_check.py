"""
Confound check for H-BV-PLANT-01 / H-BV-PSYCHOACTIVE-01.

Four tests. If _.oii enrichment on plant folios is explained by any of
these variables, the finding is a confound, not content encoding.

  1. Currier hand (A vs B) — is enrichment driven by scribe habit?
  2. Quire — are plant/psychoactive folios clustered physically?
  3. Folio length — do enriched folios just have more text?
  4. Psychoactive-four spread — do Paris, Cannabis, Rhododendron,
     Nymphaea caerulea span different hands/quires?

Publication gate: _.oii must survive all four for the finding to be
defensible against confound critique.
"""
import csv
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

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
    if not vs:
        return "".join(cons), ""
    by_pos = defaultdict(list)
    for p,v in vs: by_pos[p].append(v)
    return "".join(cons), ".".join("".join(by_pos.get(p,[])) or "_"
                                    for p in range(max(by_pos)+1))

# Index corpus
folio_meta = {}
folio_tokens = defaultdict(list)
for folio in CORPUS["folios"]:
    fid = folio["folio"]
    folio_meta[fid] = {
        "quire": folio["quire"],
        "currier": folio.get("currier_language", "?"),
        "section": folio["section"],
        "word_count": folio["word_count"],
    }
    for line in folio["lines"]:
        folio_tokens[fid].extend(line["words"])

def oii_rate(fid):
    toks = folio_tokens.get(fid, [])
    if len(toks) < 20: return None
    return sum(1 for w in toks if split_skel_vowels(w)[1] == "_.oii") / len(toks)

# Plant / psychoactive sets (replicating H-BV-PSYCHOACTIVE-01 spec)
PSYCHO_KEYWORDS = ["narcotic", "hallucinogenic", "soporific", "psychedelic",
                   "psychoactive", "consciousness-altering", "hypnotic",
                   "entheogen"]
plant_folios = set()
psycho_folios = set()
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        notes_raw = (r.get("notes") or "")
        if "CONFLICT" in notes_raw.upper(): continue
        fid = r["folio"]
        plant_folios.add(fid)
        text = ((r.get("medicinal_use") or "") + " " + notes_raw).lower()
        if any(kw in text for kw in PSYCHO_KEYWORDS):
            psycho_folios.add(fid)

# Usable sets (>=20 tokens, in corpus)
plant_usable = [f for f in plant_folios if oii_rate(f) is not None]
nonplant_herbal = [f for f, m in folio_meta.items()
                   if m["section"] == "herbal" and f not in plant_folios
                   and oii_rate(f) is not None]
psycho_usable = [f for f in psycho_folios if oii_rate(f) is not None]
nonpsycho_plant = [f for f in plant_usable if f not in psycho_folios]

print(f"Plant folios (usable):     {len(plant_usable)}")
print(f"Non-plant herbal:          {len(nonplant_herbal)}")
print(f"Psychoactive plants:       {len(psycho_usable)}")
print(f"Non-psychoactive plants:   {len(nonpsycho_plant)}")

# =========================================================================
# CONFOUND 1 — Currier hand
# =========================================================================
print("\n" + "="*72)
print("  CONFOUND 1 — Currier hand distribution")
print("="*72)
cur_plant = Counter(folio_meta[f]["currier"] for f in plant_usable)
cur_nonplant = Counter(folio_meta[f]["currier"] for f in nonplant_herbal)
cur_psycho = Counter(folio_meta[f]["currier"] for f in psycho_usable)
print(f"  Plant folios by hand:       {dict(cur_plant)}")
print(f"  Non-plant herbal by hand:   {dict(cur_nonplant)}")
print(f"  Psychoactive by hand:       {dict(cur_psycho)}")

# Compare _.oii rate within each Currier hand
def rate_stats(folios):
    rates = [oii_rate(f) for f in folios if oii_rate(f) is not None]
    return (len(rates), statistics.mean(rates) if rates else 0,
            statistics.stdev(rates) if len(rates)>1 else 0)

print(f"\n  _.oii rate within each hand (plant vs non-plant herbal):")
for hand in ("A", "B", "?"):
    pn, pm, ps = rate_stats([f for f in plant_usable
                              if folio_meta[f]["currier"] == hand])
    nn, nm, ns = rate_stats([f for f in nonplant_herbal
                              if folio_meta[f]["currier"] == hand])
    if pn > 0 and nn > 0:
        enr = pm / nm if nm > 0 else float("inf")
        print(f"    Hand {hand}: plant n={pn} rate={pm:.5f}  |  "
              f"non-plant n={nn} rate={nm:.5f}  |  enrichment {enr:.2f}x")

# Within-hand one-tailed t-test
for hand in ("A", "B"):
    plant_rates = [oii_rate(f) for f in plant_usable
                   if folio_meta[f]["currier"] == hand and oii_rate(f) is not None]
    non_rates = [oii_rate(f) for f in nonplant_herbal
                 if folio_meta[f]["currier"] == hand and oii_rate(f) is not None]
    if len(plant_rates) >= 3 and len(non_rates) >= 3:
        t, p2 = stats.ttest_ind(plant_rates, non_rates, equal_var=False)
        p1 = p2/2 if t > 0 else 1 - p2/2
        print(f"    Hand {hand} within-hand t-test: t={t:+.2f} one-tailed p={p1:.4f}")

# =========================================================================
# CONFOUND 2 — Quire distribution
# =========================================================================
print("\n" + "="*72)
print("  CONFOUND 2 — Quire distribution")
print("="*72)
qu_plant = Counter(folio_meta[f]["quire"] for f in plant_usable)
qu_psycho = Counter(folio_meta[f]["quire"] for f in psycho_usable)
qu_nonplant = Counter(folio_meta[f]["quire"] for f in nonplant_herbal)
all_quires = sorted(set(qu_plant) | set(qu_nonplant) | set(qu_psycho))
print(f"  {'quire':<8} {'plant':>6} {'non':>6} {'psycho':>8} "
      f"{'plant_oii':>11} {'non_oii':>10}")
for q in all_quires:
    pf = [f for f in plant_usable if folio_meta[f]["quire"] == q]
    nf = [f for f in nonplant_herbal if folio_meta[f]["quire"] == q]
    psyf = [f for f in psycho_usable if folio_meta[f]["quire"] == q]
    pr = statistics.mean(oii_rate(f) for f in pf) if pf else 0
    nr = statistics.mean(oii_rate(f) for f in nf) if nf else 0
    if len(pf) + len(nf) + len(psyf) >= 2:
        print(f"  {q:<8} {len(pf):>6} {len(nf):>6} {len(psyf):>8} "
              f"{pr:>10.5f} {nr:>10.5f}")

# =========================================================================
# CONFOUND 3 — Folio token count correlation
# =========================================================================
print("\n" + "="*72)
print("  CONFOUND 3 — Folio token count vs _.oii rate")
print("="*72)
counts_plant = [folio_meta[f]["word_count"] for f in plant_usable]
rates_plant  = [oii_rate(f) for f in plant_usable]
counts_non   = [folio_meta[f]["word_count"] for f in nonplant_herbal]
rates_non    = [oii_rate(f) for f in nonplant_herbal]

print(f"  Plant folios: mean token count = {statistics.mean(counts_plant):.0f} "
      f"(sd {statistics.pstdev(counts_plant):.0f})")
print(f"  Non-plant:    mean token count = {statistics.mean(counts_non):.0f} "
      f"(sd {statistics.pstdev(counts_non):.0f})")

# Token-count t-test: are plant folios shorter/longer than non-plant?
t_count, p2_count = stats.ttest_ind(counts_plant, counts_non, equal_var=False)
print(f"  Token-count difference: t = {t_count:+.2f}  two-tailed p = {p2_count:.4f}")

# Pearson correlation within plant folios: does longer folio = higher rate?
n = len(counts_plant)
mx = statistics.mean(counts_plant); my = statistics.mean(rates_plant)
num = sum((counts_plant[i]-mx)*(rates_plant[i]-my) for i in range(n))
den_x = math.sqrt(sum((counts_plant[i]-mx)**2 for i in range(n)))
den_y = math.sqrt(sum((rates_plant[i]-my)**2 for i in range(n)))
pearson = num/(den_x*den_y) if den_x*den_y > 0 else 0
print(f"  Pearson r (plant folio token count vs _.oii rate): {pearson:+.3f}")

# Length-matched resampling: draw 115 non-plant folios weighted to match
# plant token-count distribution, recompute enrichment
nonplant_mean = statistics.mean(counts_non)
plant_mean = statistics.mean(counts_plant)
# Bin by length: <100, 100-200, 200+
def bin_of(n):
    return "short" if n < 100 else ("mid" if n < 200 else "long")
plant_bins = Counter(bin_of(folio_meta[f]["word_count"]) for f in plant_usable)
print(f"\n  Plant token-count bins: {dict(plant_bins)}")
non_bins = defaultdict(list)
for f in nonplant_herbal:
    non_bins[bin_of(folio_meta[f]["word_count"])].append(f)
print(f"  Non-plant token-count bins: {dict((k,len(v)) for k,v in non_bins.items())}")

# Stratified baseline: compute per-bin _.oii rate across non-plant, use plant bin weights
plant_oii_agg = (sum(oii_rate(f) * folio_meta[f]["word_count"] for f in plant_usable) /
                 sum(folio_meta[f]["word_count"] for f in plant_usable))
non_oii_bins = {}
for b, fs in non_bins.items():
    if fs:
        non_oii_bins[b] = (sum(oii_rate(f) * folio_meta[f]["word_count"] for f in fs) /
                           sum(folio_meta[f]["word_count"] for f in fs))
# Length-matched non-plant baseline: weighted by plant's distribution
plant_bin_props = {b: plant_bins[b]/len(plant_usable) for b in plant_bins}
length_matched_non = sum(non_oii_bins.get(b, 0) * plant_bin_props[b] for b in plant_bins)
print(f"\n  Plant _.oii aggregate rate:            {plant_oii_agg:.5f}")
print(f"  Non-plant _.oii rate (length-matched): {length_matched_non:.5f}")
print(f"  Length-matched enrichment:             "
      f"{plant_oii_agg/length_matched_non if length_matched_non>0 else float('inf'):.2f}x")

# =========================================================================
# CONFOUND 4 — Psychoactive four spread
# =========================================================================
print("\n" + "="*72)
print("  CONFOUND 4 — Psychoactive-four physical spread")
print("="*72)
for fid in sorted(psycho_usable):
    m = folio_meta[fid]; r = oii_rate(fid)
    print(f"  {fid:<8}  quire={m['quire']:<3}  hand={m['currier']}  "
          f"section={m['section']:<14}  rate={r:.4f}  "
          f"tokens={m['word_count']}")

# Count distinct values
qu_psy_set = set(folio_meta[f]["quire"] for f in psycho_usable)
cur_psy_set = set(folio_meta[f]["currier"] for f in psycho_usable)
sec_psy_set = set(folio_meta[f]["section"] for f in psycho_usable)
print(f"\n  Distinct quires: {len(qu_psy_set)} ({qu_psy_set})")
print(f"  Distinct hands:  {len(cur_psy_set)} ({cur_psy_set})")
print(f"  Distinct sections: {len(sec_psy_set)} ({sec_psy_set})")

# =========================================================================
# VERDICT
# =========================================================================
print("\n" + "="*72)
print("  CONFOUND-CHECK VERDICT")
print("="*72)

# Save
out = ROOT / "outputs" / "plant_confound_check.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "currier": {
        "plant_distribution": dict(cur_plant),
        "nonplant_distribution": dict(cur_nonplant),
        "psycho_distribution": dict(cur_psycho),
    },
    "quire": {
        "plant_quires_n": len(set(qu_plant)),
        "psycho_quires_n": len(qu_psy_set),
        "psycho_distinct_quires": sorted(qu_psy_set),
    },
    "length": {
        "plant_mean_tokens": statistics.mean(counts_plant),
        "nonplant_mean_tokens": statistics.mean(counts_non),
        "token_count_ttest_p": p2_count,
        "pearson_length_vs_oii": pearson,
        "plant_aggregate_oii": plant_oii_agg,
        "length_matched_nonplant_oii": length_matched_non,
        "length_matched_enrichment": (plant_oii_agg/length_matched_non
                                       if length_matched_non>0 else None),
    },
    "psycho_four": [
        {"folio": fid, **folio_meta[fid], "oii_rate": oii_rate(fid)}
        for fid in sorted(psycho_usable)
    ],
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
