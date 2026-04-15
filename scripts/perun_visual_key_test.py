"""
Perun visual-key hypothesis: do plant illustration properties correlate
with measurable text properties on the same folio?

If a volvelle or any mechanical process wrote the text independent of
content, no correlation should exist between what the plant IS and what
the text looks like. Any robust text<->image correlation is evidence that
the illustrations constrained the text (i.e. the manuscript has content).
"""
import csv
import json
import math
import statistics
import sys
import re
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
MULTICHAR = ["cth", "ckh", "cph", "ch", "sh"]

def tokenize(word):
    out=[]; i=0
    while i<len(word):
        m=next((m for m in MULTICHAR if word.startswith(m,i)), None)
        if m: out.append(m); i+=len(m)
        else: out.append(word[i]); i+=1
    return out

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

def glyph_entropy(stream):
    c = Counter(stream); n = sum(c.values())
    if n == 0: return 0
    return -sum((v/n)*math.log2(v/n) for v in c.values() if v>0)

# =========================================================================
# Index corpus by folio
# =========================================================================
folio_tokens = defaultdict(list)
folio_lines = defaultdict(list)
for folio in CORPUS["folios"]:
    fid = folio["folio"]
    for line in folio["lines"]:
        folio_tokens[fid].extend(line["words"])
        folio_lines[fid].append(line["words"])

def folio_text_features(fid):
    toks = folio_tokens[fid]
    lines = folio_lines[fid]
    if not toks: return None
    lens = [len(w) for w in toks]
    stream = []
    for w in toks: stream.extend(tokenize(w))
    # q-initial fraction
    q_init = sum(1 for w in toks if w.startswith("q")) / len(toks)
    # gallows-initial lines (first word starts with t/p non-bench)
    gli = 0
    for L in lines:
        if L and L[0] and L[0][0] in "tp" and (len(L[0])==1 or L[0][1]!="h"):
            gli += 1
    gli_rate = gli / len(lines) if lines else 0
    # top vowel pattern frequency
    vps = Counter()
    oii_hits = 0
    for w in toks:
        _, vp = split_skel_vowels(w)
        vps[vp] += 1
        if vp == "_.oii": oii_hits += 1
    top_vp_freq = vps.most_common(1)[0][1] / len(toks) if vps else 0
    oii_rate = oii_hits / len(toks)
    return {
        "n_tokens": len(toks),
        "mean_len": statistics.mean(lens),
        "glyph_entropy": glyph_entropy(stream),
        "q_init": q_init,
        "gallows_line_init": gli_rate,
        "top_vp_freq": top_vp_freq,
        "oii_rate": oii_rate,
    }

# =========================================================================
# Botanical categorisation
# =========================================================================
TOXIC_WORDS = ["poison", "toxic", "narcotic", "hallucin", "sedative", "lethal"]
FOOD_WORDS = ["edible", "vegetable", "food", "protein", "leafy", "staple",
              "cuisine", "cooking", "salad", "aperitif", "salsify", "tuber",
              "cucumber", "lettuce", "chickpea", "spinach"]
MEDICINAL_MARKERS = ["treatment", "cure", "antidote", "disease", "infection",
                     "wound", "ointment", "inflammation", "digestion",
                     "cough", "pain", "antibiotic", "antiseptic", "tonic",
                     "antioxidant", "anti-inflammatory", "anti-", "diuretic",
                     "sedative", "emollient", "purgative", "stimulant",
                     "fever", "ulcer"]

MED_GENUS_FAMILY = {
    # Some common genus -> family
    "rosmarinus": "lamiaceae", "mentha": "lamiaceae", "salvia": "lamiaceae",
    "thymus": "lamiaceae", "lavandula": "lamiaceae", "origanum": "lamiaceae",
    "stachys": "lamiaceae", "prunella": "lamiaceae", "lamium": "lamiaceae",
    "helleborus": "ranunculaceae", "delphinium": "ranunculaceae",
    "aquilegia": "ranunculaceae", "anemone": "ranunculaceae",
    "eranthis": "ranunculaceae", "pulsatilla": "ranunculaceae",
    "adonis": "ranunculaceae", "ranunculus": "ranunculaceae",
    "atropa": "solanaceae", "mandragora": "solanaceae",
    "nicotiana": "solanaceae",
    "leucanthemum": "asteraceae", "tanacetum": "asteraceae",
    "inula": "asteraceae", "erigeron": "asteraceae", "emilia": "asteraceae",
    "aster": "asteraceae", "catananche": "asteraceae",
    "cichorium": "asteraceae", "sonchus": "asteraceae",
    "hieracium": "asteraceae", "scorzonera": "asteraceae",
    "lactuca": "asteraceae", "cynara": "asteraceae",
    "chrysanthemum": "asteraceae", "astrantia": "apiaceae",
    "apium": "apiaceae", "coriandrum": "apiaceae", "eryngium": "apiaceae",
    "astragalus": "fabaceae", "pisum": "fabaceae", "lens": "fabaceae",
    "nymphaea": "nymphaeaceae", "nymphoides": "menyanthaceae",
    "crocus": "iridaceae", "tulipa": "liliaceae", "paris": "melanthiaceae",
    "dianthus": "caryophyllaceae", "silene": "caryophyllaceae",
    "stellaria": "caryophyllaceae",
    "viola": "violaceae",
    "ruta": "rutaceae", "dictamnus": "rutaceae",
    "papaver": "papaveraceae",
    "saxifraga": "saxifragaceae", "ribes": "grossulariaceae",
    "borago": "boraginaceae", "pulmonaria": "boraginaceae",
    "rhus": "anacardiaceae",
    "cakile": "brassicaceae", "draba": "brassicaceae", "isatis": "brassicaceae",
    "lunaria": "brassicaceae",
    "verbena": "verbenaceae",
    "euphorbia": "euphorbiaceae", "ricinus": "euphorbiaceae",
    "sempervivum": "crassulaceae",
    "campanula": "campanulaceae",
    "drosera": "droseraceae",
    "acanthus": "acanthaceae", "thunbergia": "acanthaceae",
    "valeriana": "caprifoliaceae", "lonicera": "caprifoliaceae",
    "linnaea": "caprifoliaceae",
    "polemonium": "polemoniaceae",
    "veronica": "plantaginaceae",
    "centaurea": "asteraceae",
    "symphytum": "boraginaceae",
    "arnica": "asteraceae",
    "curcuma": "zingiberaceae",
    "malva": "malvaceae",
    "myrica": "myricaceae",
    "trientalis": "primulaceae", "anagallis": "primulaceae",
    "cucumis": "cucurbitaceae", "telfairia": "cucurbitaceae",
    "ficus": "moraceae", "cannabis": "cannabaceae",
    "musa": "musaceae", "dioscorea": "dioscoreaceae",
    "aristolochia": "aristolochiaceae",
    "gentiana": "gentianaceae",
    "cuscuta": "convolvulaceae",
    "nigella": "ranunculaceae",
    "erodium": "geraniaceae",
    "spinacia": "amaranthaceae", "atriplex": "amaranthaceae",
    "celosia": "amaranthaceae",
    "sanguisorba": "rosaceae", "elytrigia": "poaceae",
    "polygonum": "polygonaceae",
    "rhododendron": "ericaceae",
}

MED_NATIVES = {
    "mediterranean", "tuscany", "italian native", "greek", "coastal europe",
    "southern europe", "se european", "iberian", "spain",
}

def botany(row):
    med = (row.get("medicinal_use") or "").lower()
    notes = (row.get("notes") or "").lower()
    combined = f"{med} {notes}"
    # Toxicity / use class
    is_toxic = any(w in combined for w in TOXIC_WORDS)
    is_food = any(w in combined for w in FOOD_WORDS)
    is_medicinal = any(w in combined for w in MEDICINAL_MARKERS) and not is_food
    if is_toxic:
        use_class = "toxic"
    elif is_food:
        use_class = "food"
    elif is_medicinal:
        use_class = "medicinal"
    elif med.strip():
        use_class = "medicinal"
    else:
        use_class = "unknown"
    # Family
    lat = (row.get("latin_name") or "").strip().lower()
    genus = lat.split()[0] if lat else ""
    family = MED_GENUS_FAMILY.get(genus, "unknown")
    # Med / non-Med
    is_med_native = any(m in combined for m in MED_NATIVES)
    # Africa / Asia explicit non-Med
    non_med = any(x in combined for x in
                  ["african", "west african", "se asian", "asian",
                   "central asian", "arab", "indian", "chinese"])
    if is_med_native:
        origin = "mediterranean"
    elif non_med:
        origin = "non-mediterranean"
    else:
        origin = "unknown"
    return dict(use=use_class, family=family, origin=origin, genus=genus)

# =========================================================================
# Build combined dataset
# =========================================================================
rows = []
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        notes = (r.get("notes") or "").upper()
        if "CONFLICT" in notes:
            continue
        fid = r["folio"]
        ft = folio_text_features(fid)
        if ft is None: continue
        bot = botany(r)
        rows.append({
            "folio": fid, **ft, **bot,
            "latin": r.get("latin_name",""), "common": r.get("common_name",""),
        })

print(f"Plant folios with text features + botany: {len(rows)}")

# =========================================================================
# Statistical tests
# =========================================================================
def welch_t(a, b):
    """Welch's t-test (assumes unequal variances). Returns (t, df, p approx)."""
    if len(a) < 2 or len(b) < 2: return 0, 0, 1.0
    ma, mb = statistics.mean(a), statistics.mean(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    if va == 0 and vb == 0:
        return 0, 0, 1.0
    se = math.sqrt(va/len(a) + vb/len(b))
    if se == 0: return 0, 0, 1.0
    t = (ma - mb) / se
    # Welch-Satterthwaite df
    num = (va/len(a) + vb/len(b))**2
    den = (va**2/(len(a)**2*(len(a)-1)) if len(a)>1 else 0) + \
          (vb**2/(len(b)**2*(len(b)-1)) if len(b)>1 else 0)
    df = num/den if den else 0
    # Crude two-tailed p via normal approx (df large) or t approx
    # Use a rough lookup for small df
    abs_t = abs(t)
    if abs_t > 3.5: p = 0.001
    elif abs_t > 2.6: p = 0.01
    elif abs_t > 2.0: p = 0.05
    elif abs_t > 1.65: p = 0.10
    else: p = 0.20
    return t, df, p

TEXT_FEATURES = ["mean_len", "glyph_entropy", "q_init", "gallows_line_init",
                 "top_vp_freq", "oii_rate"]

def compare_groups(label_a, group_a, label_b, group_b):
    print(f"\n  {label_a} (n={len(group_a)}) vs {label_b} (n={len(group_b)})")
    print(f"  {'feature':<22} {label_a[:10]:>10} {label_b[:10]:>10} "
          f"{'t':>7} {'p<=':>6}")
    for feat in TEXT_FEATURES:
        a = [r[feat] for r in group_a]
        b = [r[feat] for r in group_b]
        if not a or not b: continue
        ma = statistics.mean(a); mb = statistics.mean(b)
        t, df, p = welch_t(a, b)
        marker = " *" if p <= 0.05 else ""
        print(f"  {feat:<22} {ma:>10.4f} {mb:>10.4f} {t:>+7.2f} {p:>6.3f}{marker}")

# =========================================================================
# Q1: toxic vs food
# =========================================================================
print("\n" + "="*72)
print("  Q1. Toxic vs Food plants — text-feature comparison")
print("="*72)
toxic = [r for r in rows if r["use"] == "toxic"]
food  = [r for r in rows if r["use"] == "food"]
print(f"  Toxic folios: {len(toxic)}  |  Food folios: {len(food)}")
if toxic and food:
    compare_groups("toxic", toxic, "food", food)

# =========================================================================
# Q2: Mediterranean vs non-Mediterranean
# =========================================================================
print("\n" + "="*72)
print("  Q2. Mediterranean native vs non-Mediterranean")
print("="*72)
med = [r for r in rows if r["origin"] == "mediterranean"]
nm  = [r for r in rows if r["origin"] == "non-mediterranean"]
print(f"  Mediterranean: {len(med)}  |  Non-Mediterranean: {len(nm)}")
if med and nm:
    compare_groups("med", med, "non-med", nm)

# =========================================================================
# Q3: plant family predicts any text property?
# =========================================================================
print("\n" + "="*72)
print("  Q3. Plant family vs text features (ANOVA-style F-ratio)")
print("="*72)
fam_groups = defaultdict(list)
for r in rows:
    if r["family"] != "unknown":
        fam_groups[r["family"]].append(r)
# Keep families with n>=4
big_fams = {f: g for f, g in fam_groups.items() if len(g) >= 4}
print(f"  Families with n>=4: {len(big_fams)}")
for f, g in sorted(big_fams.items(), key=lambda x: -len(x[1])):
    print(f"    {f:<20} n={len(g)}")

def f_ratio(groups, feat):
    """One-way ANOVA F ratio. groups: list of lists of values."""
    vals = [v for g in groups for v in g]
    if len(vals) < 3: return 0
    grand = statistics.mean(vals)
    N = len(vals); k = len(groups)
    if k < 2: return 0
    ssb = sum(len(g)*(statistics.mean(g)-grand)**2 for g in groups if g)
    ssw = sum((v - statistics.mean(g))**2 for g in groups for v in g if g)
    dfb = k - 1; dfw = N - k
    if dfw == 0 or ssw == 0: return 0
    return (ssb/dfb) / (ssw/dfw)

if len(big_fams) >= 2:
    print(f"\n  {'feature':<22} {'F-ratio':>8} {'signif (F>=2.5)':>18}")
    for feat in TEXT_FEATURES:
        groups = [[r[feat] for r in g] for g in big_fams.values()]
        F = f_ratio(groups, feat)
        marker = " *" if F >= 2.5 else ""
        print(f"  {feat:<22} {F:>8.2f} {('YES' if F>=2.5 else 'no'):>18}{marker}")

# =========================================================================
# Q4: _.oii fire rate vs medicinal use
# =========================================================================
print("\n" + "="*72)
print("  Q4. _.oii fire rate: medicinal vs non-medicinal plants")
print("="*72)
med_plants = [r for r in rows if r["use"] == "medicinal"]
nonmed_plants = [r for r in rows if r["use"] in ("food", "unknown")]
print(f"  Medicinal: {len(med_plants)}  |  Non-medicinal (food/unknown): "
      f"{len(nonmed_plants)}")
if med_plants and nonmed_plants:
    a = [r["oii_rate"] for r in med_plants]
    b = [r["oii_rate"] for r in nonmed_plants]
    ma, mb = statistics.mean(a), statistics.mean(b)
    t, df, p = welch_t(a, b)
    print(f"  _.oii rate  medicinal: {ma:.4f}  non-medicinal: {mb:.4f}")
    print(f"  t = {t:+.2f}, p <= {p:.3f}")
    if p <= 0.05:
        print(f"  -> SIGNIFICANT: _.oii rate differs between medicinal and non-medicinal")
    else:
        print(f"  -> no significant difference")
    # Also check against TOXIC
    tox = [r["oii_rate"] for r in rows if r["use"] == "toxic"]
    if tox:
        mt = statistics.mean(tox)
        print(f"  _.oii rate  toxic: {mt:.4f} (n={len(tox)})")

# =========================================================================
# SUMMARY
# =========================================================================
print("\n" + "="*72)
print("  SUMMARY — Perun visual-key test")
print("="*72)
use_counts = Counter(r["use"] for r in rows)
origin_counts = Counter(r["origin"] for r in rows)
print(f"  Use classification:    {dict(use_counts)}")
print(f"  Origin classification: {dict(origin_counts)}")
print(f"  Families identified:   {len(big_fams)} with n>=4")

out = ROOT / "outputs" / "perun_visual_key.json"
# Save features + botany per folio + summary
records = [{k: r[k] for k in ("folio","latin","common","use","family",
                              "origin","mean_len","glyph_entropy","q_init",
                              "gallows_line_init","top_vp_freq","oii_rate",
                              "n_tokens")} for r in rows]
out.write_text(json.dumps({
    "generated": "2026-04-15",
    "n_folios": len(rows),
    "use_counts": dict(use_counts),
    "origin_counts": dict(origin_counts),
    "families_ge4": {f: len(g) for f, g in big_fams.items()},
    "records": records,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
