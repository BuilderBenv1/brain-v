"""
First contact: Brain-V's structural model applied to Schechter's decipherment.

Four tests:
  1. Suffix stripping on DECODED Latin (not on EVA).
  2. Transposition attacks on decoded word sequences per line/page.
  3. Biological section vs others — Brain-V predicts biological reads cleanest.
  4. Currier A vs B under Schechter's glossary — Brain-V predicts equal fit.

Coherence score for decoded Latin (line-level features):
  - ending_score:   fraction of words ending in canonical Latin inflections
                    (us/um/is/em/ae/am/os/as/es/et/ibus/orum/i/o/e/a)
  - common_score:   fraction of words that are common Latin function words
                    (et, in, est, non, ad, de, qui, ut, cum, sed, ex, per,
                     sine, ac, sic, sed, quod, quia, vel, si)
  - bigram_score:   fraction of adjacent pairs whose first word is a prep/conj
                    and second word carries a noun/adj ending (simple proxy
                    for preposition-object placement)

  coherence = mean(ending, common, bigram)

Not a real grammar check. A grammar check needs a parser. But it is
reproducible, unbiased, and lets us compare interventions against a baseline.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "scripts")

GLOSS_CSV = Path(r"C:\Projects\brain-v\raw\schechter_glossary.csv")
CORPUS_JSON = Path(r"C:\Projects\brain-v\raw\perception\voynich-corpus.json")

# --- Load glossary ---
GLOSS = {}
with GLOSS_CSV.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        GLOSS[row["eva"]] = row["decoded"].upper()

# --- Load corpus ---
corpus = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))

# Decode a line: return list of (decoded_or_None, eva) tuples
def decode_line(words):
    return [(GLOSS.get(w), w) for w in words]

# --- Latin coherence scoring ---
ENDINGS = ("IBUS", "ORUM", "ARUM", "US", "UM", "IS", "EM", "AE", "AM",
           "OS", "AS", "ES", "ET", "ITE", "AT", "ANT", "ENT")
FUNCTIONS = {"ET", "IN", "EST", "NON", "AD", "DE", "QUI", "UT", "CUM", "SED",
             "EX", "PER", "SINE", "AC", "SIC", "QUOD", "QUIA", "VEL", "SI",
             "OR", "AN", "AL", "AM", "AUT", "NEC", "QUE", "SUB", "SUPER"}
PREPS_CONJS = {"IN", "AD", "DE", "CUM", "EX", "PER", "SINE", "SUB", "SUPER",
               "ET", "SED", "VEL", "AC", "AUT", "NEC", "SI", "UT", "QUIA"}

def word_ending_score(words):
    if not words:
        return 0.0
    return sum(1 for w in words if w.endswith(ENDINGS)) / len(words)

def function_word_score(words):
    if not words:
        return 0.0
    return sum(1 for w in words if w in FUNCTIONS) / len(words)

def prep_object_score(words):
    if len(words) < 2:
        return 0.0
    hits = 0
    pairs = 0
    for a, b in zip(words, words[1:]):
        pairs += 1
        if a in PREPS_CONJS and b.endswith(ENDINGS):
            hits += 1
    return hits / pairs if pairs else 0.0

def coherence(words):
    """words = list of decoded uppercase Latin (None dropped)."""
    words = [w for w in words if w]
    if not words:
        return 0.0, 0.0, 0.0, 0.0
    e = word_ending_score(words)
    f = function_word_score(words)
    p = prep_object_score(words)
    return (e + f + p) / 3, e, f, p

# --- Suffix stripping on DECODED Latin ---
# Strip trailing inflections if word length > 3 after strip
SUFFIXES_SORTED = sorted(ENDINGS, key=len, reverse=True)
def strip_suffix(word):
    for s in SUFFIXES_SORTED:
        if word.endswith(s) and len(word) - len(s) >= 3:
            return word[:-len(s)]
    return word

# --- Transposition operators on a SEQUENCE OF WORDS ---
def t_identity(seq):      return list(seq)
def t_reverse(seq):       return list(reversed(seq))
def t_boustro(seq):       # flip every second half
    n = len(seq); mid = n // 2
    return list(seq[:mid]) + list(reversed(seq[mid:]))
def t_columnar(seq, k=4):
    cols = [[] for _ in range(k)]
    for i, w in enumerate(seq):
        cols[i % k].append(w)
    out = []
    for c in cols:
        out.extend(c)
    return out
def t_spiral(seq):
    # read outside-in: first, last, second, second-to-last, ...
    out = []
    i, j = 0, len(seq) - 1
    while i <= j:
        out.append(seq[i]); i += 1
        if i <= j:
            out.append(seq[j]); j -= 1
    return out

TRANSPOSITIONS = {
    "identity":    t_identity,
    "reverse":     t_reverse,
    "boustro":     t_boustro,
    "columnar4":   lambda s: t_columnar(s, 4),
    "columnar5":   lambda s: t_columnar(s, 5),
    "spiral":      t_spiral,
}

# =========================================================================
# Collect per-line decoded sequences, tagged by section and currier.
# =========================================================================
line_records = []  # (section, currier, decoded_words_with_none, eva_words)
page_records = defaultdict(list)  # (folio_id) -> flat decoded list
for folio in corpus["folios"]:
    sec = folio["section"]
    cur = folio.get("currier_language", "?")
    fid = folio["folio"]
    for line in folio["lines"]:
        dec = [GLOSS.get(w) for w in line["words"]]
        line_records.append({
            "section": sec, "currier": cur, "folio": fid,
            "decoded": dec, "eva": line["words"],
        })
        page_records[fid].extend(dec)

total_lines = len(line_records)
print("=" * 80)
print("  SCHECHTER × BRAIN-V — first-contact analysis")
print(f"  {total_lines:,} lines across {len(page_records)} folios")
print("=" * 80)

# =========================================================================
# TEST 1: Suffix stripping on DECODED Latin
# =========================================================================
print("\n  TEST 1 — Suffix stripping on decoded Latin")
print("  " + "-" * 70)
raw_scores = []
stripped_scores = []
for rec in line_records:
    dec = [w for w in rec["decoded"] if w]
    if len(dec) < 3:
        continue
    raw_scores.append(coherence(dec)[0])
    stripped = [strip_suffix(w) for w in dec]
    # scoring stripped text still uses ending detection — so we expect
    # ending_score to DROP and function_word_score to stay similar.
    stripped_scores.append(coherence(stripped)[0])
raw_mean = sum(raw_scores) / len(raw_scores)
strip_mean = sum(stripped_scores) / len(stripped_scores)
print(f"  Lines scored: {len(raw_scores):,}")
print(f"  Coherence — raw decoded:      {raw_mean:.4f}")
print(f"  Coherence — suffix stripped:  {strip_mean:.4f}")
print(f"  Delta:                        {strip_mean - raw_mean:+.4f}")
if strip_mean > raw_mean + 0.01:
    print("  -> Suffix stripping IMPROVES decoded coherence (supports Brain-V)")
elif strip_mean < raw_mean - 0.01:
    print("  -> Suffix stripping DEGRADES coherence (suffix signal is real Latin inflection)")
else:
    print("  -> No meaningful change")

# =========================================================================
# TEST 2: Transposition attacks on decoded word sequences
# =========================================================================
print("\n  TEST 2 — Transposition attacks on DECODED word sequences")
print("  " + "-" * 70)
print("  Per-line coherence under each transposition:")
print(f"  {'transform':<14} {'line-mean':>12} {'page-mean':>12}")
for name, fn in TRANSPOSITIONS.items():
    line_scores = []
    for rec in line_records:
        dec = [w for w in rec["decoded"] if w]
        if len(dec) < 3:
            continue
        permuted = fn(dec)
        line_scores.append(coherence(permuted)[0])
    page_scores = []
    for fid, flat in page_records.items():
        dec = [w for w in flat if w]
        if len(dec) < 10:
            continue
        permuted = fn(dec)
        page_scores.append(coherence(permuted)[0])
    ls = sum(line_scores) / len(line_scores)
    ps = sum(page_scores) / len(page_scores)
    print(f"  {name:<14} {ls:>12.4f} {ps:>12.4f}")

# =========================================================================
# TEST 3: Section-by-section coherence
# =========================================================================
print("\n  TEST 3 — Biological vs other sections (raw decoded)")
print("  " + "-" * 70)
print(f"  {'section':<16} {'lines':>6} {'coverage':>9} {'coherence':>10} "
      f"{'ending':>8} {'func':>7} {'prep-obj':>9}")
by_section = defaultdict(list)
cov_by_section = defaultdict(lambda: [0, 0])
for rec in line_records:
    dec = [w for w in rec["decoded"] if w]
    if len(dec) < 3:
        continue
    by_section[rec["section"]].append(coherence(dec))
    cov_by_section[rec["section"]][0] += len(dec)
    cov_by_section[rec["section"]][1] += len(rec["eva"])

for sec in sorted(by_section):
    rows = by_section[sec]
    n = len(rows)
    c = sum(r[0] for r in rows) / n
    e = sum(r[1] for r in rows) / n
    f_ = sum(r[2] for r in rows) / n
    p = sum(r[3] for r in rows) / n
    m, tot = cov_by_section[sec]
    cov = m / tot if tot else 0
    print(f"  {sec:<16} {n:>6} {cov:>8.1%} {c:>10.4f} {e:>8.4f} {f_:>7.4f} {p:>9.4f}")
bio = by_section.get("biological", [])
if bio:
    bio_c = sum(r[0] for r in bio) / len(bio)
    others = [r for s, rows in by_section.items() if s != "biological" for r in rows]
    oth_c = sum(r[0] for r in others) / len(others)
    print(f"\n  Biological coherence: {bio_c:.4f}")
    print(f"  Other sections:       {oth_c:.4f}")
    print(f"  Delta:                {bio_c - oth_c:+.4f}")
    if bio_c > oth_c + 0.01:
        print("  -> Biological reads cleaner (supports Brain-V prediction)")
    elif bio_c < oth_c - 0.01:
        print("  -> Biological reads WORSE than others (refutes Brain-V prediction)")
    else:
        print("  -> No meaningful difference")

# =========================================================================
# TEST 4: Currier A vs B under Schechter's glossary
# =========================================================================
print("\n  TEST 4 — Currier A vs B fit to Schechter's glossary")
print("  " + "-" * 70)
by_cur = defaultdict(list)
cov_by_cur = defaultdict(lambda: [0, 0])
for rec in line_records:
    cur = rec["currier"]
    if cur not in ("A", "B"):
        continue
    dec = [w for w in rec["decoded"] if w]
    cov_by_cur[cur][0] += len(dec)
    cov_by_cur[cur][1] += len(rec["eva"])
    if len(dec) < 3:
        continue
    by_cur[cur].append(coherence(dec))

for cur in ("A", "B"):
    rows = by_cur[cur]
    n = len(rows)
    c = sum(r[0] for r in rows) / n
    e = sum(r[1] for r in rows) / n
    f_ = sum(r[2] for r in rows) / n
    p = sum(r[3] for r in rows) / n
    m, tot = cov_by_cur[cur]
    print(f"  Currier {cur}: {n:>5} lines, coverage {m/tot:.1%}, "
          f"coherence {c:.4f} (ending {e:.4f}, func {f_:.4f}, prep-obj {p:.4f})")

if by_cur["A"] and by_cur["B"]:
    a_c = sum(r[0] for r in by_cur["A"]) / len(by_cur["A"])
    b_c = sum(r[0] for r in by_cur["B"]) / len(by_cur["B"])
    a_cov = cov_by_cur["A"][0] / cov_by_cur["A"][1]
    b_cov = cov_by_cur["B"][0] / cov_by_cur["B"][1]
    print(f"\n  Coverage delta (A-B): {a_cov - b_cov:+.4f}")
    print(f"  Coherence delta (A-B): {a_c - b_c:+.4f}")
    if abs(a_cov - b_cov) < 0.03 and abs(a_c - b_c) < 0.02:
        print("  -> Glossary fits A and B comparably (supports Brain-V: same language)")
    else:
        print("  -> Glossary fits A and B UNEQUALLY (challenges Brain-V's same-language claim)")

print("\n" + "=" * 80)
print("  Baseline sanity: coherence of random latin-looking strings")
print("=" * 80)
# Shuffle decoded words across the corpus: a destroyed-order baseline.
import random
random.seed(0)
all_decoded = [w for rec in line_records for w in rec["decoded"] if w]
random.shuffle(all_decoded)
scores = []
i = 0
for rec in line_records:
    dec = [w for w in rec["decoded"] if w]
    if len(dec) < 3:
        continue
    sample = all_decoded[i:i+len(dec)]
    i += len(dec)
    if len(sample) < 3:
        break
    scores.append(coherence(sample)[0])
shuf_mean = sum(scores) / len(scores)
print(f"  Shuffled-across-corpus coherence: {shuf_mean:.4f}")
print(f"  Identity (in-order):              {raw_mean:.4f}")
print(f"  Delta vs shuffle:                 {raw_mean - shuf_mean:+.4f}")
if raw_mean - shuf_mean < 0.005:
    print("  -> In-order decoded text is NOT more coherent than random-order decoded text")
    print("     i.e. Schechter's glossary produces 'Latin-looking words' but not Latin sentences")
else:
    print("  -> In-order decoded text IS more coherent than shuffled — syntax survives the mapping")
