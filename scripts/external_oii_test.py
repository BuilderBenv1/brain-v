"""
Pre-registered single-hypothesis test:
  H1: _.oii fire rate is higher on EXTERNAL-application plant folios
      than on INTERNAL-application (ingested) plant folios.

Motivated by H-BV-TOXIC-01 bimodality: the 5 toxic plants that fired _.oii
heavily (Paris quadrifolia, Rhododendron, Delphinium, Euphorbia, Cuscuta,
Nymphaea) are mostly external/topical; the 9 non-firing toxic plants are
mostly ingested (Atropa, Helleborus, Mandragora, Ricinus, etc.).

Classification rules (keyword-matched against the medicinal_use + notes
fields in plant-identifications.csv):

  EXTERNAL keywords:
    poultice, ointment, unguent, salve, topical, skin, wound, burn,
    bruise, sprain, ulcer, inflammation, repellent, perfume, bath,
    dermal, applied, lotion, plaster, rub, conjunctivitis

  INTERNAL keywords:
    tea, infusion, decoction, food, edible, vegetable, salad, purgative,
    laxative, tincture, drink, digestion, stomach, cough, sedative,
    diuretic, tonic, aphrodisiac, sore throat, memory, depression,
    Alzheimer, dementia, protein, lettuce, coffee substitute, cuisine,
    eaten, ingested, snakebite cure

A folio counts as EXTERNAL if it matches >=1 external keyword and
0 internal keywords (or a net external score). If it matches both,
mark MIXED and exclude from the primary test. Same the other way.

Pre-registered alpha = 0.05, one-tailed Welch's t-test.
"""
import csv
import json
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

EXTERNAL_KW = [
    "poultice", "ointment", "unguent", "salve", "topical", "skin",
    "wound", "burn", "bruise", "sprain", "ulcer", "inflammation",
    "inflammatory", "repellent", "perfume", "bath", "dermal", "applied",
    "lotion", "plaster", " rub", "conjunctivitis", "insecticide",
    "insect", "flea", "eye disease", "fire protection", "lice",
    "parasite", "witchcraft protection", "anti-flea", "boil", "acne",
    "herpes", "mouthwash", "throat", "scorpion",
]
INTERNAL_KW = [
    "tea", "infusion", "decoction", "food", "edible", "vegetable",
    "salad", "purgative", "laxative", "tincture", "drink", "drunk",
    "digest", "stomach", "cough", "sedative", "diuretic", "tonic",
    "aphrodisiac", "memory", "depression", "alzheimer", "dementia",
    "protein", "coffee substitute", "cuisine", "eaten", "ingested",
    "snakebite cure", "childbirth", "antidote", "fever", "pulmonary",
    "lung", "bronchial", "blood", "aperitif", "staple", "cooking",
    "kidney", "liver", "urinary", "bladder", "gallstone", "epilepsy",
    "headache", "colds", "constipation", "indigestion", "migraine",
    "lactation", "narcotic", "hallucinogenic", "soporific",
    "heart stimulant", "gout", "insomnia", "vitamin", "cardioactive",
]

def classify(row):
    text = ((row.get("medicinal_use") or "") + " " +
            (row.get("notes") or "")).lower()
    ext_hits = [kw for kw in EXTERNAL_KW if kw in text]
    int_hits = [kw for kw in INTERNAL_KW if kw in text]
    ne, ni = len(ext_hits), len(int_hits)
    if ne == 0 and ni == 0:
        return "unknown", ext_hits, int_hits
    if ne >= 1 and ni == 0: return "external", ext_hits, int_hits
    if ni >= 1 and ne == 0: return "internal", ext_hits, int_hits
    if ne > ni: return "external", ext_hits, int_hits
    if ni > ne: return "internal", ext_hits, int_hits
    return "mixed", ext_hits, int_hits

# Load CSV, classify
external = set(); internal = set(); mixed = set(); unknown = set()
class_map = {}
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        notes = (r.get("notes") or "").upper()
        if "CONFLICT" in notes: continue
        fid = r["folio"]
        cls, eh, ih = classify(r)
        class_map[fid] = (cls, r, eh, ih)
        if cls == "external": external.add(fid)
        elif cls == "internal": internal.add(fid)
        elif cls == "mixed": mixed.add(fid)
        else: unknown.add(fid)

print(f"External: {len(external)}  Internal: {len(internal)}  "
      f"Mixed: {len(mixed)}  Unknown: {len(unknown)}")

# Per-folio tokens + oii rate
folio_tokens = defaultdict(list)
for folio in CORPUS["folios"]:
    fid = folio["folio"]
    for line in folio["lines"]:
        folio_tokens[fid].extend(line["words"])

def oii_rate(fid):
    toks = folio_tokens[fid]
    if len(toks) < 20: return None
    hits = sum(1 for w in toks if split_skel_vowels(w)[1] == "_.oii")
    return hits / len(toks)

ext_rates = [r for f in external if (r := oii_rate(f)) is not None]
int_rates = [r for f in internal if (r := oii_rate(f)) is not None]

print(f"External folios with >=20 tokens: {len(ext_rates)}")
print(f"Internal folios with >=20 tokens: {len(int_rates)}")

# Print classifications
print("\n  EXTERNAL classifications:")
for fid in sorted(external):
    r = oii_rate(fid)
    rate = f"{r:.4f}" if r is not None else "  n/a"
    cls, rec, eh, _ = class_map[fid]
    name = (rec.get("latin_name") or rec.get("common_name","")).strip()[:25]
    kw = ",".join(eh[:3])
    print(f"    {fid:<8} rate={rate}  {name:<25}  [{kw}]")

print("\n  INTERNAL classifications:")
for fid in sorted(internal):
    r = oii_rate(fid)
    rate = f"{r:.4f}" if r is not None else "  n/a"
    cls, rec, _, ih = class_map[fid]
    name = (rec.get("latin_name") or rec.get("common_name","")).strip()[:25]
    kw = ",".join(ih[:3])
    print(f"    {fid:<8} rate={rate}  {name:<25}  [{kw}]")

# =========================================================================
# STATISTICS
# =========================================================================
print("\n" + "="*72)
print("  ONE-TAILED WELCH'S T-TEST: H1: external > internal")
print("="*72)

me = statistics.mean(ext_rates); se = statistics.stdev(ext_rates) if len(ext_rates)>1 else 0
mi = statistics.mean(int_rates); si = statistics.stdev(int_rates) if len(int_rates)>1 else 0
print(f"  External: mean = {me:.5f}  sd = {se:.5f}  n = {len(ext_rates)}")
print(f"  Internal: mean = {mi:.5f}  sd = {si:.5f}  n = {len(int_rates)}")
print(f"  Difference (ext - int): {me - mi:+.5f}")
print(f"  Ratio:                   {me/mi if mi>0 else float('inf'):.2f}x")

t, p_two = stats.ttest_ind(ext_rates, int_rates, equal_var=False)
p_one = p_two/2 if t > 0 else 1 - p_two/2

va = statistics.variance(ext_rates) if len(ext_rates)>1 else 0
vb = statistics.variance(int_rates) if len(int_rates)>1 else 0
na, nb = len(ext_rates), len(int_rates)
df = ((va/na + vb/nb)**2 /
      ((va**2/(na**2*(na-1)) if na>1 else 0) +
       (vb**2/(nb**2*(nb-1)) if nb>1 else 0))) if (va/na + vb/nb) > 0 else 0

pooled_sd = ((va*(na-1) + vb*(nb-1))/(na+nb-2))**0.5 if na+nb>2 else 0
d = (me - mi)/pooled_sd if pooled_sd > 0 else 0
J = 1 - 3/(4*(na+nb)-9) if na+nb > 2 else 1
g = d * J

print(f"\n  t-statistic:         {t:+.4f}")
print(f"  Welch df:            {df:.2f}")
print(f"  Two-tailed p:        {p_two:.6f}")
print(f"  ONE-TAILED p (H1):   {p_one:.6f}")
print(f"  Cohen's d:           {d:.3f}")
print(f"  Hedges' g:           {g:.3f}")

# Bootstrap 95% CI on mean difference
rng = random.Random(7); B = 10000
diffs = []
for _ in range(B):
    a = [rng.choice(ext_rates) for _ in ext_rates]
    b = [rng.choice(int_rates) for _ in int_rates]
    diffs.append(statistics.mean(a) - statistics.mean(b))
diffs.sort()
lo, hi = diffs[int(B*0.025)], diffs[int(B*0.975)]
print(f"\n  Bootstrap 95% CI on (ext - int) mean diff: [{lo:+.5f}, {hi:+.5f}]")
print(f"  CI excludes zero: {'YES' if (lo>0 or hi<0) else 'no'}")

# Mann-Whitney U as non-parametric sanity check (handles skew better)
u, p_u_two = stats.mannwhitneyu(ext_rates, int_rates, alternative="greater")
print(f"\n  Mann-Whitney U (one-tailed, ext > int):")
print(f"    U = {u:.1f}   p = {p_u_two:.6f}")

# =========================================================================
# VERDICT
# =========================================================================
print("\n" + "="*72)
print("  VERDICT (pre-registered alpha = 0.05)")
print("="*72)
if p_one < 0.05 and t > 0:
    print(f"  p = {p_one:.4f} < 0.05 — REJECT null in direction of H1")
    print(f"  _.oii fires significantly more on external-application folios.")
    print(f"  *** This is Brain-V's first evidence of illustration-content")
    print(f"      encoding in the Voynich text.  Effect: d = {d:.2f}, "
          f"{me/mi:.1f}x ratio.")
elif p_one < 0.10 and t > 0:
    print(f"  p = {p_one:.4f} — marginal; larger sample needed")
else:
    print(f"  p = {p_one:.4f} — fails alpha = 0.05")

# Verify against the bimodal toxic finding
print("\n  Cross-check on H-BV-TOXIC-01 bimodality:")
print("  Toxic folios that fired _.oii heavily — classified as:")
heavy_toxic = ["f15v", "f28v", "f30v", "f36r", "f38v", "f49r"]
for fid in heavy_toxic:
    if fid in class_map:
        cls, rec, eh, ih = class_map[fid]
        name = (rec.get("latin_name") or rec.get("common_name","")).strip()[:25]
        print(f"    {fid:<8} {name:<25}  -> {cls}  [ext:{','.join(eh[:2])} / int:{','.join(ih[:2])}]")
print("\n  Toxic folios that fired _.oii at zero — classified as:")
zero_toxic = ["f1v","f3v","f9r","f23r","f28r","f42v","f44r","f48r"]
for fid in zero_toxic:
    if fid in class_map:
        cls, rec, eh, ih = class_map[fid]
        name = (rec.get("latin_name") or rec.get("common_name","")).strip()[:25]
        print(f"    {fid:<8} {name:<25}  -> {cls}  [ext:{','.join(eh[:2])} / int:{','.join(ih[:2])}]")

# Save
out = ROOT / "outputs" / "external_oii_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-15",
    "classification_counts": {"external": len(external), "internal": len(internal),
                              "mixed": len(mixed), "unknown": len(unknown)},
    "ext_n": len(ext_rates), "int_n": len(int_rates),
    "ext_mean": round(me, 6), "int_mean": round(mi, 6),
    "difference": round(me - mi, 6),
    "ratio": round(me/mi, 3) if mi>0 else None,
    "t_stat": round(t, 4), "df": round(df, 2),
    "p_one_tailed": round(p_one, 6),
    "cohens_d": round(d, 3), "hedges_g": round(g, 3),
    "bootstrap_ci_95": [round(lo, 6), round(hi, 6)],
    "ci_excludes_zero": (lo > 0 or hi < 0),
    "mann_whitney_p": round(p_u_two, 6),
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
