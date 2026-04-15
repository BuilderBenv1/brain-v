"""
Volvelle hypothesis simulator (Stevendistinto / Quevedo).

Design
------
  Ring A (6):  prefix positions — fixed set of prefix glyph strings
  Ring B (26): root positions   — cartridge swapped per section
  Ring C (8):  suffix positions — fixed set of suffix strings

  Each token := prefix + root + suffix, rings selected independently
  at uniform random. Section boundary -> Ring B cartridge swap: each
  section draws a fresh 26-root cartridge generated from the EVA
  consonant/vowel inventory with matched length distribution.

  Currier A/B simulated as two scribes with different SUFFIX preferences
  (Ring C biased sampling).

The simulator is NOT fitted to Voynich — rings and cartridges are
procedurally generated. This is the steelman test of "could a volvelle
produce Voynich-like statistics?"

Test battery (5)
---------------
  1. Zipf exponent + R^2
  2. Hapax ratio + glyph entropy + IC
  3. Currier A/B split (divergence of glyph frequencies)
  4. Vowel-pattern section coupling — chi-square on skeleton groups
  5. Shuffle test (connector-content bigram proxy) — whether simulated
     text has word-order signal above/below random shuffle

Volvelle survives if synthetic reproduces real Voynich statistics
including the chi-square vowel coupling. Otherwise, contradicted.
"""
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "scripts")

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
VOWELS = set("aoei")
CONSONANTS = list("kdrslnymg") + ["ch", "sh", "cth", "ckh", "cph", "f", "t", "p"]
SECTIONS = ["astronomical","biological","cosmological","herbal",
            "pharmaceutical","recipes","text-only","zodiac"]

# =========================================================================
# Extract real-corpus targets
# =========================================================================
real_tokens = []
real_section_tokens = defaultdict(list)
real_currier_tokens = defaultdict(list)
section_word_counts = Counter()
for folio in CORPUS["folios"]:
    sec = folio["section"]; cur = folio.get("currier_language","?")
    for line in folio["lines"]:
        for w in line["words"]:
            real_tokens.append(w)
            real_section_tokens[sec].append(w)
            if cur in ("A","B"):
                real_currier_tokens[cur].append(w)
    section_word_counts[sec] += folio["word_count"]

TARGET_TOTAL = len(real_tokens)
print(f"Real Voynich: {TARGET_TOTAL:,} tokens")
print(f"Section token counts: {dict(section_word_counts)}")

# Word length distribution we want to approximate
real_len_dist = Counter(len(w) for w in real_tokens)

# =========================================================================
# Volvelle rings
# =========================================================================
# Ring A — 6 prefixes (drawn from empirical common word starts)
RING_A_PREFIXES = ["", "q", "qo", "o", "d", "ch"]

# Ring C — 8 suffixes (drawn from empirical common word endings)
RING_C_SUFFIXES = ["", "y", "n", "r", "l", "in", "ain", "aiin"]

# Currier suffix bias: A favors some, B favors others
RING_C_WEIGHTS_A = [3, 4, 3, 2, 2, 2, 2, 3]  # scribe A
RING_C_WEIGHTS_B = [2, 6, 2, 3, 1, 3, 3, 1]  # scribe B (different mix)

# Ring B generator — produce a 26-root cartridge
def generate_cartridge(rng, mean_len=3):
    """Generate 26 root strings, each length 2-4, via random C-V-C patterns.
    Each cartridge uses a uniform sampling across consonants/vowels — NO
    section-specific vowel bias is injected. This is the key test: any
    section-coupled vowel pattern in the output must come from the
    volvelle structure itself, not from content-differentiated vowels."""
    roots = []
    while len(roots) < 26:
        L = rng.choices([2,3,4], weights=[1,3,2], k=1)[0]
        out = []
        # Pattern: start with consonant OR vowel, alternate with some jitter
        start_vowel = rng.random() < 0.3
        for i in range(L):
            if (i + (1 if start_vowel else 0)) % 2 == 0:
                out.append(rng.choice(CONSONANTS))
            else:
                out.append(rng.choice("aoei"))
        root = "".join(out)
        if 2 <= len(root) <= 5:
            roots.append(root)
    return roots

# =========================================================================
# Generate synthetic corpus
# =========================================================================
SEED = 17
rng = random.Random(SEED)

synth_tokens_by_section = {}
synth_lines = []  # list of (section, list_of_words) preserving ordering
synth_folio_currier = {}  # fake folio -> currier

# Assign sections/currier to simulated folios following real distribution
# Use real folio structure as a scaffold
for folio in CORPUS["folios"]:
    sec = folio["section"]; cur = folio.get("currier_language","?")
    fid = folio["folio"]
    synth_folio_currier[fid] = cur

# One cartridge per section (the cartridge swap)
section_cartridges = {s: generate_cartridge(rng) for s in SECTIONS}

# Generate synthetic tokens preserving section and currier structure
synth_lines = []
for folio in CORPUS["folios"]:
    sec = folio["section"]; cur = folio.get("currier_language","?")
    cartridge = section_cartridges[sec]
    suf_weights = RING_C_WEIGHTS_B if cur == "B" else RING_C_WEIGHTS_A
    for line in folio["lines"]:
        new_words = []
        for _ in line["words"]:
            prefix = rng.choice(RING_A_PREFIXES)
            root   = rng.choice(cartridge)
            suffix = rng.choices(RING_C_SUFFIXES, weights=suf_weights, k=1)[0]
            new_words.append(prefix + root + suffix)
        synth_lines.append({"section": sec, "currier": cur, "words": new_words})

synth_tokens = [w for L in synth_lines for w in L["words"]]
print(f"Synthetic corpus: {len(synth_tokens):,} tokens")

# =========================================================================
# Shared statistics functions
# =========================================================================
MULTICHAR = ["cth", "ckh", "cph", "ch", "sh"]
def tokenize(word):
    out = []; i = 0
    while i < len(word):
        m = next((m for m in MULTICHAR if word.startswith(m, i)), None)
        if m: out.append(m); i += len(m)
        else: out.append(word[i]); i += 1
    return out

def glyph_entropy(words):
    stream = []
    for w in words: stream.extend(tokenize(w))
    c = Counter(stream); n = sum(c.values())
    return -sum((v/n)*math.log2(v/n) for v in c.values() if v>0)

def ic(words):
    stream = []
    for w in words: stream.extend(tokenize(w))
    c = Counter(stream); n = sum(c.values())
    if n < 2: return 0.0
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

def zipf(words):
    c = Counter(words)
    freqs = sorted(c.values(), reverse=True)
    n = min(100, len(freqs))
    xs = [math.log(r+1) for r in range(n)]
    ys = [math.log(freqs[r]) for r in range(n)]
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    den = sum((xs[i]-mx)**2 for i in range(n))
    slope = num/den if den else 0
    ss_res = sum((ys[i]-(my+slope*(xs[i]-mx)))**2 for i in range(n))
    ss_tot = sum((ys[i]-my)**2 for i in range(n))
    r2 = 1 - ss_res/ss_tot if ss_tot else 0
    return -slope, r2

def hapax(words):
    c = Counter(words)
    return sum(1 for v in c.values() if v==1)/len(c)

# =========================================================================
# Vowel-pattern + skeleton extractor (shared with v1/v2)
# =========================================================================
def split_skel_vowels(word):
    if word and word[0] in "tp" and (len(word) == 1 or word[1] != "h"):
        word = word[1:]
    cons = []; vs = []; pos = 0; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                cons.append(sy); pos += 1; i += len(ev); matched = True; break
        if not matched:
            if word[i] in VOWELS: vs.append((pos, word[i]))
            i += 1
    if not vs:
        return "".join(cons), ""
    by_pos = defaultdict(list)
    for p, v in vs: by_pos[p].append(v)
    return "".join(cons), ".".join("".join(by_pos.get(p, [])) or "_"
                                    for p in range(max(by_pos) + 1))

def chisq(observed):
    secs = sorted({s for r in observed for s in r.keys()})
    mat = [[r.get(s,0) for s in secs] for r in observed]
    tr = [sum(r) for r in mat]; tc = [sum(c) for c in zip(*mat)]
    N = sum(tr)
    if N == 0: return 0, 0
    chi = 0.0
    for i in range(len(mat)):
        for j in range(len(secs)):
            e = tr[i]*tc[j]/N
            if e>0: chi += (mat[i][j]-e)**2/e
    return chi, (len(mat)-1)*(len(secs)-1)

CRIT_01 = {1:6.63,2:9.21,3:11.34,4:13.28,5:15.09,6:16.81,7:18.48,8:20.09,
           9:21.67,10:23.21,12:26.22,15:30.58,20:37.57,25:44.31,30:50.89,
           40:63.69,50:76.15}
def crit(df):
    for k in sorted(CRIT_01):
        if df <= k: return CRIT_01[k]
    return df + 2*math.sqrt(2*df)

# Count vowel-section coupling on any corpus-structured data
def vowel_coupling(lines):
    """lines: list of dict(section=..., words=[...]). Return (skeletons_tested, significant_at_p01)."""
    word_section = defaultdict(Counter)
    for L in lines:
        for w in L["words"]:
            word_section[w][L["section"]] += 1
    by_skel = defaultdict(list)
    for w, counts in word_section.items():
        sk, vp = split_skel_vowels(w)
        if not sk: continue
        by_skel[sk].append((w, vp, sum(counts.values()), dict(counts)))
    sig = 0; tested = 0
    for sk, vs in by_skel.items():
        if len(vs) < 3 or sum(v[2] for v in vs) < 100: continue
        top = sorted(vs, key=lambda x: -x[2])[:5]
        chi, df = chisq([v[3] for v in top])
        if df > 0:
            tested += 1
            if chi > crit(df): sig += 1
    return tested, sig

# Shuffle test
SUFFIX_CHARS = set("ynrmg")
def conn_content_delta(lines, connector_set):
    """In-order vs shuffled conn_content bigram delta."""
    # Build stream of (word, is_connector)
    def score(stream):
        pairs = 0; hits = 0; conn_n = 0
        for a, b in zip(stream, stream[1:]):
            if a in connector_set:
                conn_n += 1
                if b not in connector_set:
                    hits += 1
        return hits / conn_n if conn_n else 0
    all_tokens = [w for L in lines for w in L["words"]]
    in_order = statistics.mean(
        score(L["words"]) for L in lines if len(L["words"]) >= 3
    )
    shuffled = all_tokens[:]
    random.Random(0).shuffle(shuffled)
    chunked = []
    i = 0
    for L in lines:
        n = len(L["words"])
        chunked.append(shuffled[i:i+n]); i += n
    shuffle_score = statistics.mean(
        score(c) for c in chunked if len(c) >= 3
    )
    return in_order, shuffle_score, in_order - shuffle_score

# =========================================================================
# Build comparable lines structure for real corpus
# =========================================================================
real_lines = []
for folio in CORPUS["folios"]:
    sec = folio["section"]; cur = folio.get("currier_language","?")
    for line in folio["lines"]:
        real_lines.append({"section": sec, "currier": cur, "words": line["words"]})

# Connector sets: top 10 most frequent short tokens in each corpus
real_top = [w for w, _ in Counter(real_tokens).most_common(10)]
synth_top = [w for w, _ in Counter(synth_tokens).most_common(10)]
real_conn = set(real_top)
synth_conn = set(synth_top)

# =========================================================================
# RUN TESTS
# =========================================================================
print("\n" + "="*72)
print("  TEST BATTERY — REAL vs VOLVELLE SYNTHETIC")
print("="*72)

def row(label, real, synth):
    print(f"  {label:<28} {real:>12} {synth:>12}")

# 1. Zipf
r_zipf, r_r2 = zipf(real_tokens)
s_zipf, s_r2 = zipf(synth_tokens)
print(f"\n  {'Metric':<28} {'Real':>12} {'Synthetic':>12}")
print(f"  {'-'*56}")
row("Zipf exponent", f"{r_zipf:.4f}", f"{s_zipf:.4f}")
row("Zipf R^2", f"{r_r2:.4f}", f"{s_r2:.4f}")

# 2. Hapax / entropy / IC
row("Hapax ratio", f"{hapax(real_tokens):.4f}", f"{hapax(synth_tokens):.4f}")
row("Glyph entropy (bits)", f"{glyph_entropy(real_tokens):.4f}",
    f"{glyph_entropy(synth_tokens):.4f}")
row("Index of Coincidence", f"{ic(real_tokens):.4f}", f"{ic(synth_tokens):.4f}")
row("Unique types", f"{len(set(real_tokens)):,}",
    f"{len(set(synth_tokens)):,}")

# 3. Currier A/B divergence
def currier_divergence(lines):
    ca = Counter(); cb = Counter()
    for L in lines:
        if L["currier"] == "A":
            for w in L["words"]:
                for g in tokenize(w): ca[g] += 1
        elif L["currier"] == "B":
            for w in L["words"]:
                for g in tokenize(w): cb[g] += 1
    Na = sum(ca.values()); Nb = sum(cb.values())
    if Na == 0 or Nb == 0: return 0.0
    all_g = set(ca.keys()) | set(cb.keys())
    # Jensen-Shannon divergence
    pa = {g: ca[g]/Na for g in all_g}
    pb = {g: cb[g]/Nb for g in all_g}
    m = {g: (pa[g]+pb[g])/2 for g in all_g}
    def kl(p, q):
        return sum(p[g]*math.log2(p[g]/q[g]) for g in all_g
                   if p[g] > 0 and q[g] > 0)
    return 0.5*kl(pa, m) + 0.5*kl(pb, m)

row("Currier A/B JS-divergence",
    f"{currier_divergence(real_lines):.5f}",
    f"{currier_divergence(synth_lines):.5f}")

# 4. Vowel-section coupling
rt, rs = vowel_coupling(real_lines)
st, ss_ = vowel_coupling(synth_lines)
row("Vowel chi-sq groups (>=100 tok, >=3 variants)",
    f"{rt}", f"{st}")
row("Significant at p<0.01",
    f"{rs} ({rs/rt:.0%})" if rt else "n/a",
    f"{ss_} ({ss_/st:.0%})" if st else "n/a")

# 5. Shuffle test
r_in, r_sh, r_d = conn_content_delta(real_lines, real_conn)
s_in, s_sh, s_d = conn_content_delta(synth_lines, synth_conn)
row("Conn-content in-order", f"{r_in:.4f}", f"{s_in:.4f}")
row("Conn-content shuffled",  f"{r_sh:.4f}", f"{s_sh:.4f}")
row("Delta (in-order minus shuffled)",
    f"{r_d:+.4f}", f"{s_d:+.4f}")

# =========================================================================
# VERDICT
# =========================================================================
print("\n" + "="*72)
print("  VERDICT")
print("="*72)

def ok(real, synth, tol):
    return abs(real - synth) <= tol

# Match scorecard
matches = []
matches.append(("Zipf exponent within 0.15", ok(r_zipf, s_zipf, 0.15)))
matches.append(("Hapax ratio within 0.10",
                 ok(hapax(real_tokens), hapax(synth_tokens), 0.10)))
matches.append(("Glyph entropy within 0.3 bits",
                 ok(glyph_entropy(real_tokens), glyph_entropy(synth_tokens), 0.3)))
matches.append(("IC within 0.02",
                 ok(ic(real_tokens), ic(synth_tokens), 0.02)))
matches.append(("Currier divergence same order of magnitude",
                 currier_divergence(synth_lines) >= 0.1 * currier_divergence(real_lines)
                 and currier_divergence(synth_lines) <= 10 * currier_divergence(real_lines)))
real_coupling_rate = rs/rt if rt else 0
synth_coupling_rate = ss_/st if st else 0
matches.append((f"Vowel coupling p<0.01 rate within 10pp "
                f"(real {real_coupling_rate:.0%} vs synth {synth_coupling_rate:.0%})",
                 abs(real_coupling_rate - synth_coupling_rate) <= 0.10))
matches.append((f"Shuffle-test delta sign matches",
                 (r_d >= 0) == (s_d >= 0)))

passed = sum(1 for _, ok in matches if ok)
print(f"\n  Match scorecard: {passed}/{len(matches)}")
for name, res in matches:
    print(f"    [{('PASS' if res else 'FAIL')}] {name}")

print(f"\n  Critical test — vowel-section coupling:")
print(f"    Real:      {rs}/{rt} skeleton groups significant at p<0.01 "
      f"({real_coupling_rate:.0%})")
print(f"    Volvelle:  {ss_}/{st} skeleton groups significant at p<0.01 "
      f"({synth_coupling_rate:.0%})")
if synth_coupling_rate < 0.5 * real_coupling_rate:
    print(f"    -> Volvelle UNDER-PRODUCES vowel coupling — contradicted")
elif synth_coupling_rate > 1.5 * real_coupling_rate:
    print(f"    -> Volvelle OVER-PRODUCES vowel coupling — may indicate too-strong cartridges")
else:
    print(f"    -> Volvelle reproduces coupling within same range — SURVIVES this test")

# Save
out = ROOT / "outputs" / "volvelle_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-15",
    "seed": SEED,
    "real": {
        "tokens": len(real_tokens),
        "zipf": round(r_zipf, 4), "r2": round(r_r2, 4),
        "hapax": round(hapax(real_tokens), 4),
        "entropy": round(glyph_entropy(real_tokens), 4),
        "ic": round(ic(real_tokens), 4),
        "currier_js": round(currier_divergence(real_lines), 5),
        "vowel_coupling": {"tested": rt, "significant": rs,
                           "rate": round(real_coupling_rate, 3)},
        "shuffle_delta": round(r_d, 4),
    },
    "synthetic": {
        "tokens": len(synth_tokens),
        "zipf": round(s_zipf, 4), "r2": round(s_r2, 4),
        "hapax": round(hapax(synth_tokens), 4),
        "entropy": round(glyph_entropy(synth_tokens), 4),
        "ic": round(ic(synth_tokens), 4),
        "currier_js": round(currier_divergence(synth_lines), 5),
        "vowel_coupling": {"tested": st, "significant": ss_,
                           "rate": round(synth_coupling_rate, 3)},
        "shuffle_delta": round(s_d, 4),
    },
    "scorecard": {"passed": passed, "total": len(matches),
                  "items": [{"name": n, "pass": ok} for n, ok in matches]},
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
