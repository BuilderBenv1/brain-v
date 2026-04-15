"""
Brain-V Dictionary v1 — honest first attempt.

Scope
-----
  - Biological section only (19 folios: f75r-f84v)
  - Currier B folios only
  - ~6,315 tokens before stemming

Pipeline
--------
  1. Strip leading plain gallows 't','p' per H-BRADY-02 (paragraph markers).
  2. Strip trailing single suffixes 'y','n','l','r' per H023.
     (Not multi-char suffixes like -aiin — those are contested.)
  3. Count stem frequencies.
  4. Take top candidates (>=3 occurrences in bio-B).
  5. For each stem, run three parallel hypotheses:
       (a) Syriac — apply Brady §2.2 char map, look up in Brady proxy lex.
       (b) Latin  — frequency-rank substitution against medieval Latin
                    pharmaceutical vocab (Dioscorides, Circa Instans).
       (c) Occitan — frequency-rank substitution against 14th-c. Occitan
                    medical vocab (Elucidari, Chirurgia).
  6. Compute confidence per language hit:
       +0.30 length match (|stem_len - word_len| <= 1)
       +0.30 frequency-rank proximity (same decile)
       +0.20 semantic category plausible for pharmaceutical text
       +0.20 starting-character class match (vowel vs consonant)
  7. Best of three wins. If top-language confidence < 0.30, mark unmatched.
  8. Shuffle test on the decoded stream.
"""
import csv
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "scripts")
import decrypt

ROOT = Path(r"C:\Projects\brain-v")
CORPUS_JSON = ROOT / "raw" / "perception" / "voynich-corpus.json"
OUT_CSV = ROOT / "outputs" / "brainv_dictionary_v1.csv"

corpus = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))

# =========================================================================
# 1. Filter bio-B
# =========================================================================
bio_b_lines = []
for folio in corpus["folios"]:
    if folio["section"] != "biological":
        continue
    if folio.get("currier_language") != "B":
        continue
    for line in folio["lines"]:
        bio_b_lines.append(line["words"])

all_tokens = [w for line in bio_b_lines for w in line]
print(f"Biological-B: {len(bio_b_lines)} lines, {len(all_tokens)} tokens")

# =========================================================================
# 2-3. Stem: strip leading t/p; strip one trailing y/n/l/r
# =========================================================================
def stem(word):
    if not word:
        return ""
    # Strip leading plain gallows UNLESS it's a bench gallows (t+h / p+h)
    if word[0] in "tp" and (len(word) == 1 or word[1] != "h"):
        word = word[1:]
    # Strip one trailing y/n/l/r suffix (single char only)
    if word and word[-1] in "ynlr" and len(word) > 2:
        word = word[:-1]
    return word

stems = [stem(w) for w in all_tokens]
stem_freq = Counter(stems)
# Drop empties and very short
stem_freq = Counter({k: v for k, v in stem_freq.items() if len(k) >= 2 and v >= 3})
top_stems = stem_freq.most_common()

print(f"Stems >= 3 occurrences: {len(top_stems)}")
total_stem_tokens = sum(v for _, v in top_stems)
print(f"Token coverage of these stems: {total_stem_tokens}/{len(all_tokens)} "
      f"= {total_stem_tokens/len(all_tokens):.1%}")

# =========================================================================
# 5a. Syriac — Brady's char map + proxy lex
# =========================================================================
EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
VOWELS = set("aoei")

def to_skeleton(word):
    out = []; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                out.append(sy); i += len(ev); matched = True; break
        if not matched:
            i += 1
    return "".join(out)

BRADY_LEX = {
    "w":"wa-","d":"d-","l":"l-","m":"min-","k":"ki-","km":"kamma",
    "kdy":"kaddin","kdn":"kedhen","yn":"ayna","kl":"kol/kuhla",
    "kr":"kriha","krh":"kriha","sm":"sam","smy":"samya",
    "tly":"tali","ls":"lasha","ss":"shasa","tr":"tara",
    "dl":"dala","kyn":"kyana","tks":"taksa","syy":"shayya",
    "kky":"akakiya","ks":"kasia","ksy":"kasia","tn":"tina",
    "ts":"tasa","sy":"asya","dr":"dara","bl":"bal","ml":"malla",
    "mpss":"mpwss","mys":"mybs","myl":"mhyl","kdd":"kadda",
    "mr":"mar","smn":"shmoneh","ak":"ak","bn":"bar",
}

def match_syriac(st):
    sk = to_skeleton(st)
    # Direct
    if sk in BRADY_LEX:
        return sk, BRADY_LEX[sk], 0.9
    # Prefix stripping
    for pre in ("w","d","l"):
        if sk.startswith(pre) and len(sk) > 1 and sk[1:] in BRADY_LEX:
            return sk, f"{pre}-{BRADY_LEX[sk[1:]]}", 0.7
    return sk, None, 0.0

# =========================================================================
# 5b. Medieval Latin pharmaceutical vocabulary (Dioscorides, Circa Instans)
#     Ranked by rough medieval-pharma frequency (common → rare).
# =========================================================================
LATIN_PHARMA = [
    # Connectors / prepositions (rank 1-20 in any Latin text)
    ("et","and","FUNC",1),("in","in","FUNC",2),("de","of","FUNC",3),
    ("ad","to","FUNC",4),("est","is","FUNC",5),("cum","with","FUNC",6),
    ("ex","from","FUNC",7),("aut","or","FUNC",8),("non","not","FUNC",9),
    ("sed","but","FUNC",10),("si","if","FUNC",11),("per","through","FUNC",12),
    ("vel","or","FUNC",13),("quod","which","FUNC",14),("sub","under","FUNC",15),
    # Parts / ingredients
    ("herba","herb","ING",16),("flos","flower","ING",17),("folium","leaf","ING",18),
    ("radix","root","ING",19),("semen","seed","ING",20),("fructus","fruit","ING",21),
    ("cortex","bark","ING",22),("succus","juice","ING",23),("pulvis","powder","ING",24),
    # Liquids
    ("oleum","oil","LIQ",25),("vinum","wine","LIQ",26),("aqua","water","LIQ",27),
    ("mel","honey","LIQ",28),("lac","milk","LIQ",29),("acetum","vinegar","LIQ",30),
    # Preparations
    ("unguentum","ointment","PREP",31),("pilula","pill","PREP",32),
    ("pasta","paste","PREP",33),("decoctio","decoction","PREP",34),
    # Anatomy
    ("corpus","body","ANAT",35),("caput","head","ANAT",36),("pectus","chest","ANAT",37),
    ("venter","belly","ANAT",38),("oculus","eye","ANAT",39),("stomachus","stomach","ANAT",40),
    ("matrix","womb","ANAT",41),("sanguis","blood","ANAT",42),("cor","heart","ANAT",43),
    ("hepar","liver","ANAT",44),("ren","kidney","ANAT",45),("os","bone","ANAT",46),
    ("pes","foot","ANAT",47),("manus","hand","ANAT",48),
    # Qualities
    ("calidus","warm","QUAL",49),("frigidus","cold","QUAL",50),
    ("humidus","moist","QUAL",51),("siccus","dry","QUAL",52),
    ("amarus","bitter","QUAL",53),("dulcis","sweet","QUAL",54),
    # Verbs
    ("sanat","heals","VERB",55),("curat","cures","VERB",56),
    ("dolet","hurts","VERB",57),("accipe","take","VERB",58),
    ("pone","place","VERB",59),("misce","mix","VERB",60),
    ("trahe","draw","VERB",61),("bibe","drink","VERB",62),
    ("apponit","applies","VERB",63),("purgat","purges","VERB",64),
    # Materia medica (Dioscorides/Circa Instans common)
    ("rosa","rose","PLANT",65),("viola","violet","PLANT",66),
    ("salvia","sage","PLANT",67),("ruta","rue","PLANT",68),
    ("menta","mint","PLANT",69),("thymus","thyme","PLANT",70),
    ("absinthium","wormwood","PLANT",71),("lilium","lily","PLANT",72),
    ("papaver","poppy","PLANT",73),("crocus","saffron","PLANT",74),
    ("cinnamomum","cinnamon","PLANT",75),("piper","pepper","PLANT",76),
    ("zingiber","ginger","PLANT",77),("cassia","cassia","PLANT",78),
    ("myrrha","myrrh","PLANT",79),("aloe","aloe","PLANT",80),
    ("mandragora","mandrake","PLANT",81),("hyoscyamus","henbane","PLANT",82),
    # Dosage / measure
    ("uncia","ounce","MEAS",83),("libra","pound","MEAS",84),
    ("drachma","drachm","MEAS",85),("scrupulus","scruple","MEAS",86),
    ("pars","part","MEAS",87),("una","one","MEAS",88),("duae","two","MEAS",89),
    ("tres","three","MEAS",90),
    # Time
    ("dies","day","TIME",91),("nox","night","TIME",92),
    ("mane","morning","TIME",93),("vesper","evening","TIME",94),
    ("hora","hour","TIME",95),
    # Common auxiliary
    ("fit","is made","VERB",96),("habet","has","VERB",97),
    ("facit","does","VERB",98),("dat","gives","VERB",99),
    ("ponitur","is placed","VERB",100),
]

# =========================================================================
# 5c. Medieval Occitan medical vocabulary (14th-15th c., Elucidari)
# =========================================================================
OCCITAN_MED = [
    ("e","and","FUNC",1),("en","in","FUNC",2),("de","of","FUNC",3),
    ("a","to","FUNC",4),("es","is","FUNC",5),("am","with","FUNC",6),
    ("non","not","FUNC",7),("per","through","FUNC",8),("si","if","FUNC",9),
    ("o","or","FUNC",10),("que","that","FUNC",11),("ni","nor","FUNC",12),
    ("lo","the-m","FUNC",13),("la","the-f","FUNC",14),("li","the-pl","FUNC",15),
    ("erba","herb","ING",16),("flor","flower","ING",17),("fuelha","leaf","ING",18),
    ("razitz","root","ING",19),("semens","seed","ING",20),("frucha","fruit","ING",21),
    ("cortic","bark","ING",22),("jus","juice","ING",23),
    ("oli","oil","LIQ",24),("vi","wine","LIQ",25),("aiga","water","LIQ",26),
    ("mel","honey","LIQ",27),("lach","milk","LIQ",28),
    ("enguent","ointment","PREP",29),("polvora","powder","PREP",30),
    ("cap","head","ANAT",31),("peitz","chest","ANAT",32),("ventre","belly","ANAT",33),
    ("uelh","eye","ANAT",34),("estomac","stomach","ANAT",35),("matritz","womb","ANAT",36),
    ("sang","blood","ANAT",37),("cor","heart","ANAT",38),("fege","liver","ANAT",39),
    ("ren","kidney","ANAT",40),("os","bone","ANAT",41),
    ("pe","foot","ANAT",42),("ma","hand","ANAT",43),
    ("calt","warm","QUAL",44),("freg","cold","QUAL",45),
    ("humid","moist","QUAL",46),("sec","dry","QUAL",47),
    ("amar","bitter","QUAL",48),("dous","sweet","QUAL",49),
    ("sana","heals","VERB",50),("cura","cures","VERB",51),
    ("pren","take","VERB",52),("pausa","place","VERB",53),
    ("mesca","mix","VERB",54),("beu","drink","VERB",55),
    ("aplica","apply","VERB",56),("purga","purges","VERB",57),
    ("rosa","rose","PLANT",58),("viola","violet","PLANT",59),
    ("sauvia","sage","PLANT",60),("rusca","bark","PLANT",61),
    ("menta","mint","PLANT",62),("timo","thyme","PLANT",63),
    ("encens","incense","PLANT",64),("pebre","pepper","PLANT",65),
    ("gingebre","ginger","PLANT",66),("canela","cinnamon","PLANT",67),
    ("safran","saffron","PLANT",68),("mirra","myrrh","PLANT",69),
    ("pars","part","MEAS",70),("una","one","MEAS",71),("doas","two","MEAS",72),
    ("tres","three","MEAS",73),("onsa","ounce","MEAS",74),
    ("jorn","day","TIME",75),("nuoch","night","TIME",76),
    ("matin","morning","TIME",77),("vespre","evening","TIME",78),
    ("ora","hour","TIME",79),
    ("fach","does","VERB",80),("es-fach","is made","VERB",81),
    ("a","has","VERB",82),("dona","gives","VERB",83),
    ("met","places","VERB",84),("val","is worth","VERB",85),
    ("dolor","pain","MED",86),("febre","fever","MED",87),
    ("malautia","illness","MED",88),("plagua","wound","MED",89),
    ("san","healthy","MED",90),
]

# =========================================================================
# 6. Matching — score each stem against Latin & Occitan by frequency rank
#    and structural features.
# =========================================================================
# Rank EVA stems by frequency (rank 1 = most common)
ranked_stems = [(s, c) for s, c in top_stems]
stem_rank = {s: i+1 for i, (s, _) in enumerate(ranked_stems)}

def rank_proximity(rank_a, rank_b, n_a, n_b):
    """Decile-aligned rank proximity. 1.0 if same decile, 0 if far."""
    pa = rank_a / n_a
    pb = rank_b / n_b
    return max(0.0, 1.0 - abs(pa - pb) * 3)  # within ~30% = decile-ish

def starts_vowel(w):
    return bool(w) and w[0] in "aeiouáéíóú"

PHARMA_CATEGORIES = {"ING","LIQ","PREP","ANAT","QUAL","VERB","PLANT",
                     "MEAS","TIME","MED"}

def pair_score(stem_str, stem_rank_in_bio, word, cat, rank, n_stems, n_vocab):
    """Strict scoring: max 1.00.

    Components (each must be earned):
      length_exact     : +0.25 if |stem-word| == 0, +0.10 if == 1
      rank_quintile    : +0.25 if same quintile of own list, +0.10 if ±1 quintile
      starts_class     : +0.15 same vowel/consonant onset
      category_bonus   : +0.10 if pharmaceutical category, +0.05 if function
      uniqueness_bonus : awarded later (+0.25) via winner-take-all assignment

    Cold score (before uniqueness bonus) thus maxes at 0.75 — threshold
    for inclusion is 0.65 AFTER uniqueness bonus. A stem that scores 0.45
    cold but wins its target uniquely clears at 0.70.
    """
    score = 0.0
    dl = abs(len(stem_str) - len(word))
    if dl == 0: score += 0.25
    elif dl == 1: score += 0.10
    sa = int(stem_rank_in_bio / n_stems * 5)
    sb = int((rank-1) / n_vocab * 5)
    if sa == sb: score += 0.25
    elif abs(sa - sb) == 1: score += 0.10
    if starts_vowel(stem_str) == starts_vowel(word):
        score += 0.15
    if cat in PHARMA_CATEGORIES: score += 0.10
    elif cat == "FUNC": score += 0.05
    return score

# =========================================================================
# 7. Build dictionary via one-to-one greedy assignment
# =========================================================================
# Step 1: score every (stem, target_word, language) triple.
# Step 2: sort triples by score desc, greedily assign, each stem and each
#         target word claimed at most once per language.
# Step 3: winner gets +0.25 uniqueness bonus. Threshold for commit: 0.65.
THRESHOLD = 0.65
n_stems = len(ranked_stems)

# Pre-score Syriac per stem (Syriac is deterministic lex lookup, no contention)
syriac_hit = {}  # stem -> (skel, reading, conf)
for st, _ in ranked_stems:
    sk, r, c = match_syriac(st)
    syriac_hit[st] = (sk, r, c)

# Score Latin and Occitan pairs
def all_pairs(vocab, lang):
    n_vocab = len(vocab)
    for i, (st, freq) in enumerate(ranked_stems):
        rank_b = i + 1
        for (word, gloss, cat, rank) in vocab:
            s = pair_score(st, rank_b, word, cat, rank, n_stems, n_vocab)
            if s >= 0.40:  # early filter
                yield (s, lang, st, word, gloss, cat)

all_cands = list(all_pairs(LATIN_PHARMA, "latin")) + list(all_pairs(OCCITAN_MED, "occitan"))
all_cands.sort(key=lambda x: -x[0])

claimed_stem = set()
claimed_word = set()   # (lang, word)
commit = {}            # stem -> dict
for s, lang, st, word, gloss, cat in all_cands:
    if st in claimed_stem:
        continue
    if (lang, word) in claimed_word:
        continue
    final_conf = s + 0.25  # uniqueness bonus
    if final_conf < THRESHOLD:
        continue
    commit[st] = dict(lang=lang, form=word, gloss=gloss, cat=cat,
                      conf=final_conf)
    claimed_stem.add(st)
    claimed_word.add((lang, word))

# Build entries: prefer Syriac high-conf over a weaker Latin/Occitan match
entries = []
for i, (st, freq) in enumerate(ranked_stems):
    rank_b = i + 1
    sk, syr_read, syr_conf = syriac_hit[st]
    lat_occ = commit.get(st)
    best = None
    if syr_conf >= 0.85:
        best = ("syriac", sk, syr_read or sk, "SYR", syr_conf)
    if lat_occ and (best is None or lat_occ["conf"] > best[4]):
        best = (lat_occ["lang"], lat_occ["form"], lat_occ["gloss"],
                lat_occ["cat"], lat_occ["conf"])
    if best is None:
        status = "unmatched"
        best_lang = best_form = best_gloss = best_cat = "-"
        best_conf = 0.0
    else:
        status = "matched"
        best_lang, best_form, best_gloss, best_cat, best_conf = best

    entries.append({
        "stem": st,
        "freq": freq,
        "rank": rank_b,
        "best_lang": best_lang,
        "best_form": best_form,
        "best_gloss": best_gloss,
        "best_cat": best_cat,
        "confidence": round(best_conf, 3),
        "syriac_skel": sk,
        "syriac_reading": syr_read or "-",
        "status": status,
    })

# Write CSV
OUT_CSV.parent.mkdir(exist_ok=True)
with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(entries[0].keys()))
    w.writeheader()
    w.writerows(entries)

# =========================================================================
# 8. Summary + honest scoring
# =========================================================================
matched = [e for e in entries if e["status"] == "matched"]
unmatched = [e for e in entries if e["status"] == "unmatched"]
by_lang = Counter(e["best_lang"] for e in matched)

print("\n" + "="*72)
print("  BRAIN-V DICTIONARY v1 — built")
print("="*72)
print(f"  Scope:           biological-B, 19 folios, 6,315 tokens")
print(f"  Pipeline:        t/p strip + y/n/l/r suffix strip (H-BRADY-02, H023)")
print(f"  Dictionary size: {len(entries)} stems (>=3 occurrences)")
print(f"  Matched:         {len(matched)} ({len(matched)/len(entries):.1%})")
print(f"  Unmatched:       {len(unmatched)} ({len(unmatched)/len(entries):.1%})")
print(f"  Matched by lang: {dict(by_lang)}")
# Token-level honest coverage
stem_lookup = {e["stem"]: e for e in entries}
tok_matched = sum(1 for s in stems if stem_lookup.get(s, {}).get("status") == "matched")
print(f"  Token coverage:  {tok_matched}/{len(stems)} = {tok_matched/len(stems):.2%}")
print(f"  Confidence mean: {statistics.mean(e['confidence'] for e in matched):.3f}")

# Show top 15
print("\n  Top 15 matched entries")
print(f"  {'stem':<10} {'freq':>5} {'conf':>5} {'lang':<8} "
      f"{'form':<12} {'gloss':<15}")
for e in sorted(matched, key=lambda x: -x["freq"])[:15]:
    print(f"  {e['stem']:<10} {e['freq']:>5} {e['confidence']:>5.2f} "
          f"{e['best_lang']:<8} {e['best_form']:<12} {e['best_gloss']:<15}")

print("\n  Top 10 UNMATCHED stems (freq >= 5)")
print(f"  {'stem':<10} {'freq':>5}  [would need new vocab]")
for e in sorted(unmatched, key=lambda x: -x["freq"])[:10]:
    if e["freq"] >= 5:
        print(f"  {e['stem']:<10} {e['freq']:>5}")

# =========================================================================
# 9. Shuffle test on the decoded stream
# =========================================================================
print("\n" + "="*72)
print("  SHUFFLE TEST on Brain-V dictionary v1 output")
print("="*72)

def decode_line(words):
    out = []
    for w in words:
        st = stem(w)
        e = stem_lookup.get(st)
        if e and e["status"] == "matched":
            out.append((e["best_form"], True, e["best_cat"] == "FUNC"))
        else:
            out.append((w, False, False))
    return out

line_streams = [decode_line(ws) for ws in bio_b_lines if len(ws) >= 3]

def coherence(tokens):
    n = len(tokens)
    if n < 3:
        return dict(match=0, conn_content=0, both_matched=0)
    m = sum(1 for _, ok, _ in tokens if ok)
    cc = conn_n = bm = 0
    for a, b in zip(tokens, tokens[1:]):
        if a[2]:  # a is a connector/function word
            conn_n += 1
            if b[1] and not b[2]:
                cc += 1
        if a[1] and b[1]:
            bm += 1
    return dict(
        match=m/n,
        conn_content=cc/conn_n if conn_n else 0,
        both_matched=bm/(n-1),
    )

in_order = defaultdict(list)
for s in line_streams:
    for k, v in coherence(s).items():
        in_order[k].append(v)

random.seed(1)
pool = [t for s in line_streams for t in s]
random.shuffle(pool)
idx = 0
shuffled = defaultdict(list)
for s in line_streams:
    samp = pool[idx:idx+len(s)]; idx += len(s)
    if len(samp) < 3: break
    for k, v in coherence(samp).items():
        shuffled[k].append(v)

print(f"  {'metric':<18} {'in-order':>10} {'shuffled':>10} {'delta':>10}")
for k in ("match", "conn_content", "both_matched"):
    io = statistics.mean(in_order[k]); sh = statistics.mean(shuffled[k])
    print(f"  {k:<18} {io:>10.4f} {sh:>10.4f} {io-sh:>+10.4f}")

print(f"\n  Saved to: {OUT_CSV}")
