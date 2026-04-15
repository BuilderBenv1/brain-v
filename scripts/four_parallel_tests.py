"""
Four parallel tests, one cycle:
  1. Null lexicon   — 1,300 phonotactically plausible nonsense skeletons.
  2. Glyph positions — systematic positional analysis of every glyph.
  3. Vowel layer    — do same-consonant-frame EVA words distribute by section?
  4. Gallows-stripped rebaseline — entropy/IC/Zipf with plain gallows removed.

Each is independent. Results consolidated at the end.
"""
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "scripts")
import decrypt

ROOT = Path(r"C:\Projects\brain-v")
corpus = json.loads((ROOT / "raw" / "perception" / "voynich-corpus.json").read_text(encoding="utf-8"))

# Flatten tokens
all_tokens = []
section_of = {}
for folio in corpus["folios"]:
    sec = folio["section"]
    for line in folio["lines"]:
        for w in line["words"]:
            all_tokens.append(w)
            section_of.setdefault(w, Counter())[sec] += 1

total = len(all_tokens)
wf = Counter(all_tokens)
print(f"Corpus: {total:,} tokens, {len(wf):,} types")

# =========================================================================
# Brady char mapping (reused)
# =========================================================================
EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
VOWELS = set("aoei")

def to_skeleton(word):
    if word and word[0] in "tp" and (len(word) == 1 or word[1] != "h"):
        word = word[1:]
    out = []; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                out.append(sy); i += len(ev); matched = True; break
        if not matched:
            i += 1
    return "".join(out)

corpus_skeletons = [to_skeleton(w) for w in all_tokens]
skel_set = set(corpus_skeletons)

# =========================================================================
# TEST 1 — NULL LEXICON
# =========================================================================
print("\n" + "="*72); print("  TEST 1 — NULL LEXICON"); print("="*72)

# Phonotactically plausible nonsense: draw consonants with realistic
# unigram/bigram frequencies from CORPUS SKELETONS themselves (that's the
# worst case — we can't be more plausible than the corpus, so this gives
# the random baseline the best shot).
skel_chars = Counter()
skel_bigrams = Counter()
for s in corpus_skeletons:
    for c in s: skel_chars[c] += 1
    for a, b in zip(s, s[1:]): skel_bigrams[(a,b)] += 1

chars = list(skel_chars.keys())
char_weights = [skel_chars[c] for c in chars]
# bigram Markov: next_char_given[prev] -> Counter
next_given = defaultdict(Counter)
for (a, b), n in skel_bigrams.items():
    next_given[a][b] += n

def random_skeleton(length):
    if length == 0:
        return ""
    first = random.choices(chars, weights=char_weights, k=1)[0]
    out = [first]
    for _ in range(length - 1):
        pool = next_given[out[-1]]
        if not pool:
            out.append(random.choices(chars, weights=char_weights, k=1)[0])
        else:
            ks = list(pool.keys()); ws = [pool[k] for k in ks]
            out.append(random.choices(ks, weights=ws, k=1)[0])
    return "".join(out)

# Length distribution: match corpus skeleton lengths
len_dist = Counter(len(s) for s in corpus_skeletons if s)
lens = list(len_dist.keys()); lw = [len_dist[L] for L in lens]

random.seed(17)
N_TRIALS = 20
null_coverages = []
for trial in range(N_TRIALS):
    nonsense = set()
    while len(nonsense) < 1300:
        L = random.choices(lens, weights=lw, k=1)[0]
        nonsense.add(random_skeleton(L))
    matched = sum(1 for s in corpus_skeletons if s in nonsense)
    null_coverages.append(matched / len(corpus_skeletons))

mu = statistics.mean(null_coverages)
sd = statistics.pstdev(null_coverages)
hi = max(null_coverages); lo = min(null_coverages)
print(f"  Trials:                {N_TRIALS}")
print(f"  Null lexicon size:     1,300 phonotactically plausible skeletons")
print(f"  Null coverage mean:    {mu:.2%}")
print(f"  Null coverage stdev:   {sd:.2%}")
print(f"  Null coverage range:   [{lo:.2%}, {hi:.2%}]")
print()
print(f"  Compare:")
print(f"    Brady Syriac (1,334): 86.9% (claimed)")
print(f"    Schechter Latin (4,063): 82.8%")
print(f"    Hebrew medieval (1,300): 57.9%")
print(f"    Null nonsense (1,300): {mu:.1%}")
if mu >= 0.50:
    print(f"  -> Coverage metric COMPROMISED: 1,300 random-but-plausible")
    print(f"     skeletons alone reach {mu:.0%}. Coverage is an upper bound,")
    print(f"     not evidence of meaning.")
elif mu >= 0.30:
    print(f"  -> Coverage metric PARTIALLY COMPROMISED: ~{mu:.0%} is the")
    print(f"     floor any credible lexicon must clear.")
else:
    print(f"  -> Coverage metric PRESERVED: genuine lexicons score well above")
    print(f"     the {mu:.0%} nonsense floor.")

# =========================================================================
# TEST 2 — GLYPH POSITIONAL ANALYSIS
# =========================================================================
print("\n" + "="*72); print("  TEST 2 — GLYPH POSITIONAL ANALYSIS"); print("="*72)

# EVA multichar sequences to treat as single glyphs
MULTICHAR = ["cth", "ckh", "cph", "ch", "sh"]
def tokenize(word):
    out = []; i = 0
    while i < len(word):
        matched = False
        for m in MULTICHAR:
            if word.startswith(m, i):
                out.append(m); i += len(m); matched = True; break
        if not matched:
            out.append(word[i]); i += 1
    return out

# Positional counts: for each glyph, how often at [initial, medial, final]
pos = defaultdict(lambda: Counter())  # glyph -> {"init","mid","fin","only"}
for w in all_tokens:
    g = tokenize(w)
    n = len(g)
    for i, ch in enumerate(g):
        if n == 1: pos[ch]["only"] += 1
        elif i == 0: pos[ch]["init"] += 1
        elif i == n-1: pos[ch]["fin"] += 1
        else: pos[ch]["mid"] += 1

# Normalize + report top 20 glyphs by total occurrences
all_glyphs = sorted(pos.keys(), key=lambda g: -sum(pos[g].values()))
print(f"  {'glyph':<6} {'total':>8} {'init%':>7} {'mid%':>7} {'fin%':>7} {'only%':>7} "
      f"{'role':<28}")
classifications = {}
for g in all_glyphs:
    tot = sum(pos[g].values())
    if tot < 50:
        continue
    ip = pos[g]["init"] / tot * 100
    mp = pos[g]["mid"] / tot * 100
    fp = pos[g]["fin"] / tot * 100
    op = pos[g]["only"] / tot * 100
    # Classify
    role = "balanced"
    if ip > 70: role = "INITIAL-dominant (prefix/marker)"
    elif fp > 70: role = "FINAL-dominant (suffix/marker)"
    elif mp > 80: role = "MID-only (internal consonant)"
    elif op > 40: role = "STANDALONE-dominant (word unit)"
    elif ip + op > 80: role = "word-initial tendency"
    elif fp + op > 80: role = "word-final tendency"
    classifications[g] = role
    print(f"  {g:<6} {tot:>8,} {ip:>6.1f}% {mp:>6.1f}% {fp:>6.1f}% {op:>6.1f}% {role:<28}")

# Count roles
role_counts = Counter(classifications.values())
print(f"\n  Role distribution:")
for role, n in role_counts.most_common():
    print(f"    {role:<38} {n}")

# Specifically flag already-known + newly-discovered roles
print(f"\n  Knowns confirmed:")
for g in ("t", "p"):
    if g in classifications:
        print(f"    '{g}' -> {classifications[g]} (H-BRADY-02)")
for g in ("y", "n", "l", "r"):
    if g in classifications:
        print(f"    '{g}' -> {classifications[g]} (H023 suffix class)")
print(f"\n  New candidates for structural-role testing:")
for g, r in classifications.items():
    if g in ("t","p","y","n","l","r"): continue
    if "dominant" in r or "tendency" in r:
        print(f"    '{g}' -> {r}")

# =========================================================================
# TEST 3 — VOWEL LAYER (Brady §3.10)
# =========================================================================
print("\n" + "="*72); print("  TEST 3 — VOWEL LAYER (chedy/chody case study)"); print("="*72)

# For each consonant skeleton, collect its realisations (words that map to
# it via Brady's char map, retaining vowels) and their section distribution.
# Then for high-volume skeletons, chi-square the section distribution across
# vowel variants.

# Map each word to (skeleton, vowel_pattern). Vowel pattern = sequence of
# a/o/e/i characters that would be stripped.
def split_skel_vowels(word):
    # Apply same prefix strip as to_skeleton for consistency
    if word and word[0] in "tp" and (len(word) == 1 or word[1] != "h"):
        word = word[1:]
    consonants = []
    vowels = []
    i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                consonants.append(sy); i += len(ev); matched = True; break
        if not matched:
            if word[i] in VOWELS:
                vowels.append(word[i])
            i += 1
    return "".join(consonants), "".join(vowels)

# Per-word section occurrences
word_section = defaultdict(Counter)
for folio in corpus["folios"]:
    sec = folio["section"]
    for line in folio["lines"]:
        for w in line["words"]:
            word_section[w][sec] += 1

# Group words by skeleton
by_skel = defaultdict(list)  # skel -> [(word, total_count, {section->count})]
for w, counts in word_section.items():
    sk, _ = split_skel_vowels(w)
    if not sk:
        continue
    by_skel[sk].append((w, sum(counts.values()), dict(counts)))

# Chi-square test for independence: are vowel variants distributed uniformly
# across sections, or section-linked?
# Focus on skeletons with >=3 variants and >=100 total tokens.

def chisq(observed):
    """observed: list of dicts {section: count}. Returns (chi2, df)."""
    sections = set()
    for row in observed:
        sections |= set(row.keys())
    sections = sorted(sections)
    rows = len(observed)
    if rows < 2 or len(sections) < 2:
        return 0, 0
    mat = [[row.get(s, 0) for s in sections] for row in observed]
    totals_row = [sum(r) for r in mat]
    totals_col = [sum(c) for c in zip(*mat)]
    N = sum(totals_row)
    if N == 0: return 0, 0
    chi2 = 0.0
    for i in range(rows):
        for j in range(len(sections)):
            exp = totals_row[i] * totals_col[j] / N
            if exp > 0:
                chi2 += (mat[i][j] - exp) ** 2 / exp
    df = (rows - 1) * (len(sections) - 1)
    return chi2, df

# Critical values for common df (p=0.01)
CRIT_01 = {1:6.63, 2:9.21, 3:11.34, 4:13.28, 5:15.09, 6:16.81, 7:18.48,
           8:20.09, 9:21.67, 10:23.21, 12:26.22, 15:30.58, 20:37.57,
           25:44.31, 30:50.89, 40:63.69, 50:76.15}

def crit(df):
    keys = sorted(CRIT_01.keys())
    for k in keys:
        if df <= k: return CRIT_01[k]
    return df + 2 * math.sqrt(2 * df)  # approximate

candidates = []
for sk, variants in by_skel.items():
    if len(variants) < 3: continue
    if sum(v[1] for v in variants) < 100: continue
    # Keep only top-5 variants by count
    variants = sorted(variants, key=lambda x: -x[1])[:5]
    chi, df = chisq([v[2] for v in variants])
    if df > 0:
        candidates.append((sk, variants, chi, df, chi / max(crit(df), 0.001)))

candidates.sort(key=lambda x: -x[4])
print(f"  Skeletons with >=3 vowel variants and >=100 total tokens: {len(candidates)}")
print(f"  Significant at p<0.01 (chi2 > critical): "
      f"{sum(1 for c in candidates if c[4] >= 1.0)}")

# Focus case: chedy/chody (skel 'kdy')
kdy = [c for c in candidates if c[0] == "kdy"]
print(f"\n  Case: skeleton 'kdy' (Brady's chedy/chody)")
if kdy:
    sk, variants, chi, df, ratio = kdy[0]
    print(f"    chi2 = {chi:.2f}, df = {df}, crit(p=0.01) = {crit(df):.2f}, "
          f"ratio = {ratio:.2f}x")
    print(f"    -> {'section-coupled vowels' if ratio >= 1.0 else 'NOT section-coupled'}")
    print(f"    Top variants and section distribution:")
    all_secs = sorted(set(s for _, _, d in variants for s in d))
    header = "      variant      total  " + "  ".join(f"{s[:6]:>6}" for s in all_secs)
    print(header)
    for w, tot, secs in variants:
        row = "  ".join(f"{secs.get(s,0):>6}" for s in all_secs)
        print(f"      {w:<12} {tot:>5}  {row}")
else:
    print("    skeleton 'kdy' has fewer than 3 variants or <100 tokens")

# Top 5 overall section-coupled skeletons
print(f"\n  Top 5 skeletons with strongest section-vowel coupling:")
for sk, variants, chi, df, ratio in candidates[:5]:
    vnames = ",".join(v[0] for v in variants[:3])
    print(f"    {sk:<6} variants[{vnames}]  chi2={chi:.1f}/df={df}  ratio={ratio:.2f}x")

# =========================================================================
# TEST 4 — GALLOWS-STRIPPED REBASELINE
# =========================================================================
print("\n" + "="*72); print("  TEST 4 — GALLOWS-STRIPPED REBASELINE"); print("="*72)

def strip_plain_gallows(w):
    if w and w[0] in "tp" and (len(w) == 1 or w[1] != "h"):
        return w[1:]
    return w

orig_words = all_tokens
stripped_words = [strip_plain_gallows(w) for w in all_tokens if strip_plain_gallows(w)]

# Entropy — glyph-level over the glyph stream
def glyph_entropy(words):
    # Use EVA multichar tokenisation
    stream = []
    for w in words:
        stream.extend(tokenize(w))
    c = Counter(stream); n = sum(c.values())
    return -sum((v/n) * math.log2(v/n) for v in c.values() if v > 0)

def ic(words):
    stream = []
    for w in words:
        stream.extend(tokenize(w))
    c = Counter(stream); n = sum(c.values())
    if n < 2: return 0.0
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

def zipf_exponent(words):
    c = Counter(words)
    freqs = sorted(c.values(), reverse=True)
    # Log-log regression on top 100 ranks
    xs = [math.log(r+1) for r in range(min(100, len(freqs)))]
    ys = [math.log(freqs[r]) for r in range(min(100, len(freqs)))]
    n = len(xs)
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    den = sum((xs[i]-mx)**2 for i in range(n))
    slope = num/den if den else 0
    # R^2
    ss_res = sum((ys[i] - (my + slope*(xs[i]-mx)))**2 for i in range(n))
    ss_tot = sum((ys[i]-my)**2 for i in range(n))
    r2 = 1 - ss_res/ss_tot if ss_tot else 0
    return -slope, r2

def hapax_ratio(words):
    c = Counter(words)
    return sum(1 for v in c.values() if v == 1) / len(c)

o_ent = glyph_entropy(orig_words)
s_ent = glyph_entropy(stripped_words)
o_ic = ic(orig_words); s_ic = ic(stripped_words)
o_zipf, o_r2 = zipf_exponent(orig_words)
s_zipf, s_r2 = zipf_exponent(stripped_words)
o_hap = hapax_ratio(orig_words); s_hap = hapax_ratio(stripped_words)

stripped_tokens_removed = len(orig_words) - len(stripped_words)
# Actually we kept all words but stripped prefix; token count same.
stripped_words_actual = [strip_plain_gallows(w) for w in all_tokens]
assert len(stripped_words_actual) == len(orig_words)
# But some words became empty — count them
empties = sum(1 for w in stripped_words_actual if not w)
print(f"  Tokens total:           {len(orig_words):,}")
print(f"  Tokens reduced to empty after gallows strip: {empties}")

# Recompute with empties dropped for hapax/zipf but keep in glyph stream
real_stripped = [w for w in stripped_words_actual if w]
r_ent = glyph_entropy(real_stripped)
r_ic = ic(real_stripped)
r_zipf, r_r2 = zipf_exponent(real_stripped)
r_hap = hapax_ratio(real_stripped)

print(f"\n  {'Metric':<22} {'Original':>12} {'Stripped':>12} {'Delta':>12}")
print(f"  {'-'*60}")
print(f"  {'Glyph entropy (bits)':<22} {o_ent:>12.4f} {r_ent:>12.4f} {r_ent-o_ent:>+12.4f}")
print(f"  {'Index of Coincidence':<22} {o_ic:>12.4f} {r_ic:>12.4f} {r_ic-o_ic:>+12.4f}")
print(f"  {'Zipf exponent':<22} {o_zipf:>12.4f} {r_zipf:>12.4f} {r_zipf-o_zipf:>+12.4f}")
print(f"  {'Zipf R2':<22} {o_r2:>12.4f} {r_r2:>12.4f} {r_r2-o_r2:>+12.4f}")
print(f"  {'Hapax ratio':<22} {o_hap:>12.4f} {r_hap:>12.4f} {r_hap-o_hap:>+12.4f}")
print(f"  {'Unique types':<22} {len(Counter(orig_words)):>12,} {len(Counter(real_stripped)):>12,}")

print(f"\n  Interpretation:")
if abs(r_ent - o_ent) > 0.05:
    print(f"    Entropy shifts by >0.05 bits — gallows carry independent info.")
else:
    print(f"    Entropy nearly unchanged ({abs(r_ent-o_ent):.3f}b) — gallows behave")
    print(f"    as auxiliary markers, not core phonetic content.")
if abs(r_zipf - o_zipf) > 0.03:
    print(f"    Zipf exponent shifts by {r_zipf-o_zipf:+.3f} — word-length/frequency")
    print(f"    distribution changes; the stripped corpus may fit natural language")
    print(f"    expectations better.")
else:
    print(f"    Zipf exponent essentially unchanged.")
if r_hap < o_hap - 0.02:
    print(f"    Hapax ratio drops {o_hap-r_hap:.3f} — fewer uniques after strip.")
elif r_hap > o_hap + 0.02:
    print(f"    Hapax ratio rises {r_hap-o_hap:.3f} — uniqueness slightly enriched.")
else:
    print(f"    Hapax ratio essentially unchanged.")

# =========================================================================
# SUMMARY
# =========================================================================
print("\n" + "="*72); print("  CONSOLIDATED SUMMARY — 4 tests"); print("="*72)
print(f"  1. Null lexicon:       {mu:.1%} coverage (1,300 nonsense skeletons)")
print(f"     Genuine lexicons    58-87%. Delta over null: "
      f"{(0.58 - mu)*100:+.1f}pp (Hebrew floor)")
print(f"  2. Glyph positions:    {len(classifications)} glyphs classified; "
      f"{sum(1 for r in classifications.values() if 'dominant' in r)} positionally dominant")
print(f"  3. Vowel layer:        {sum(1 for c in candidates if c[4] >= 1.0)}/"
      f"{len(candidates)} skeleton groups show section-coupled vowels at p<0.01")
print(f"  4. Gallows rebaseline: entropy {o_ent:.3f} -> {r_ent:.3f} "
      f"(d {r_ent-o_ent:+.3f} b), Zipf {o_zipf:.3f} -> {r_zipf:.3f}")
