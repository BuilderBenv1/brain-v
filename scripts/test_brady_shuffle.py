"""
Shuffle test on Brady's decoded output.

Zenodo 10.5281/zenodo.19583306 does NOT host supplementary files; the
lexicon_v31_session31_final.json and pipeline_v31.py are not downloadable.

Reconstruction:
  - EVA->Syriac character mapping: from Brady §2.2 (verbatim table).
  - Lexicon: ~90-term proxy extracted from skeletons and Syriac words
    explicitly mentioned in the paper body (§1, §3.4-3.12, §4.2).
  - The proxy covers the paper's explicit vocabulary (kaddin/kedhen/aynā/kol/
    kuhlā/kriha/āsyā/rappā/akākiyā/kasiā/tinā/taksā/kyānā/lāšā/šāsā/talī etc.)
    plus connectors (wa-/d-/l-/m-) and common Syriac function morphology.

The test MIRRORS the one that killed Schechter's syntactic claim:
  - Decode every token; produce a stream of (skeleton, match?, is_connector?).
  - Define a Syriac-flavoured coherence score on the stream.
  - Compare in-order vs. across-corpus-shuffled coherence.
  - If shuffled scores ≥ in-order, the decoded stream carries no Syriac
    syntactic signal beyond the token-level lexical match.
"""
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "scripts")
import decrypt

CORPUS_JSON = Path(r"C:\Projects\brain-v\raw\perception\voynich-corpus.json")
corpus = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))

# =========================================================================
# 1. Brady's character mapping (§2.2) — verbatim
# =========================================================================
EVA_MAP = [
    ("cth", "tk"),    # bench gallows
    ("ckh", "kk"),
    ("cph", "pk"),
    ("ch",  "k"),     # kaph (kaph/qoph merged)
    ("sh",  "s"),     # shin
    ("k",   "k"),
    ("d",   "d"),
    ("r",   "r"),
    ("s",   "s"),
    ("l",   "l"),
    ("n",   "n"),
    ("y",   "y"),
    ("m",   "m"),
    ("g",   "g"),
    ("t",   "t"),     # plain gallows — see strip_plain_gallows
    ("p",   "p"),
    ("f",   "s"),     # tsade -> s
    ("q",   "w"),     # waw, gives wa- conjunction
]
VOWELS = set("aoei")

def to_skeleton(word):
    """Apply Brady's EVA->Syriac map + plain-gallows strip per §2.4 step (4)."""
    if word and word[0] in "tp" and (len(word) == 1 or word[1] != "h"):
        word = word[1:]
    out = []
    i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                out.append(sy)
                i += len(ev)
                matched = True
                break
        if not matched:
            if word[i] not in VOWELS:
                pass  # skip unknowns silently
            i += 1
    return "".join(out)

# =========================================================================
# 2. Proxy lexicon reconstructed from Brady paper body
# =========================================================================
# Format: skeleton -> (reading, category)
# Categories: PHARMA, MED, BOT, FUNCTION, GENERAL
BRADY_LEX = {
    # === Connectors / function words (paper §2.2, §3.13) ===
    "w":    ("wa-",       "FUNCTION"),
    "d":    ("d-",        "FUNCTION"),
    "l":    ("l-",        "FUNCTION"),
    "m":    ("min-",      "FUNCTION"),
    "wd":   ("wa-d-",     "FUNCTION"),
    "wl":   ("wa-l-",     "FUNCTION"),
    "wdl":  ("wa-d-l-",   "FUNCTION"),
    "k":    ("kī/like",   "FUNCTION"),
    "kl":   ("kol/kuḥlā", "FUNCTION"),   # all / collyrium — homograph
    "lm":   ("lām",       "FUNCTION"),
    "bn":   ("bar",       "FUNCTION"),
    # === Temporal adverbs (§3.7) ===
    "kdy":  ("kaddīn",     "FUNCTION"),
    "kdn":  ("kəḏēn",      "FUNCTION"),
    # === Anatomy / disease (§3.9, §3.12) ===
    "yn":   ("ʿaynā",      "MED"),
    "krh":  ("krīhā",      "MED"),
    "kr":   ("krīhā/kārā", "MED"),
    "sm":   ("šemʿ",       "MED"),
    "smy":  ("samyā",      "MED"),
    # === Pharmaceutical procedure verbs (§abstract) ===
    "tly":  ("ṭalī",       "PHARMA"),
    "tl":   ("ṭalī",       "PHARMA"),
    "ls":   ("lāšā",       "PHARMA"),
    "ss":   ("šāsā",       "PHARMA"),
    "tdy":  ("ṭādyā",      "PHARMA"),
    "tr":   ("ṭārā/ṭōrā",  "PHARMA"),
    "dl":   ("dālā",       "PHARMA"),
    "ak":   ("ak",         "PHARMA"),
    # === Galenic classification terms ===
    "kyn":  ("kyānā",      "PHARMA"),
    "tks":  ("ṭaksā",      "PHARMA"),
    "syy":  ("šayyā",      "PHARMA"),
    "kdd":  ("kaddā",      "PHARMA"),
    # === Materia medica ===
    "kky":  ("akākīyā",    "BOT"),
    "ks":   ("kasīā",      "BOT"),
    "ksy":  ("kasīā",      "BOT"),
    "tyn":  ("tīnā",       "BOT"),
    "tn":   ("tīnā",       "BOT"),
    # === Dosage ===
    "ts":   ("ṭāsā",       "PHARMA"),
    "km":   ("kammā",      "FUNCTION"),
    # === Physician / agents ===
    "sy":   ("āsyā",       "GENERAL"),
    "syw":  ("āsyā",       "GENERAL"),
    "rp":   ("rappā",      "GENERAL"),
    # === Galenic active-participle verbs (§4.2) ===
    "mpss": ("mpwšš",      "PHARMA"),
    "mys":  ("mybš",       "PHARMA"),
    "myl":  ("mḥyl",       "PHARMA"),
    # === Other Syriac pharma-text vocabulary cited ===
    "dr":   ("dārā/dōrā",  "GENERAL"),
    "bl":   ("bāl",        "GENERAL"),
    "ml":   ("malla",      "GENERAL"),
    "mlk":  ("malkā",      "GENERAL"),
    "sr":   ("sar",        "GENERAL"),
    "sry":  ("saryā",      "GENERAL"),
    "drm":  ("darma",      "GENERAL"),
    # === Numbers / quantifiers plausible in recipes ===
    "ky":   ("kī",         "FUNCTION"),
    "dy":   ("dē",         "FUNCTION"),
    "sn":   ("sān",        "GENERAL"),
    "ny":   ("nē",         "FUNCTION"),
    "ry":   ("rē",         "FUNCTION"),
    # === Paper explicitly confirms these skeletons exist ===
    "kss":  ("kassā",      "BOT"),
    "krd":  ("kardā",      "BOT"),
    "sdr":  ("sidrā",      "BOT"),
    "ydy":  ("yadayā",     "MED"),
    "yd":   ("yadā",       "MED"),
    "sl":   ("šlām",       "GENERAL"),
    "mr":   ("mar",        "GENERAL"),
    "skr":  ("sakrā",      "PHARMA"),
    "ndr":  ("nedrā",      "MED"),
    "ssr":  ("sāṣar",      "GENERAL"),
    "kkr":  ("kakkar",     "GENERAL"),
    "sym":  ("sīmā",       "GENERAL"),
    "rsm":  ("rāsem",      "PHARMA"),
    "nsy":  ("nāsī",       "GENERAL"),
    "lks":  ("lksā",       "PHARMA"),
    "tks":  ("ṭaksā",      "PHARMA"),
    "dkr":  ("dkar",       "GENERAL"),
}

CONNECTORS = {"w", "d", "l", "m", "wd", "wl", "wdl", "k", "kl", "km", "dy", "ky"}
PREFIXES = ("w", "d", "l", "m")

def match(skel):
    """Return (matched_bool, reading_or_none)."""
    if not skel:
        return False, None
    if skel in BRADY_LEX:
        return True, BRADY_LEX[skel][0]
    # Prefix stripping (Brady pipeline step 5): w-, d-, l-
    for pre in ("w", "d", "l"):
        if skel.startswith(pre) and len(skel) > 1:
            rest = skel[len(pre):]
            if rest in BRADY_LEX:
                return True, f"{pre}-{BRADY_LEX[rest][0]}"
    # Suffix -yn (step 6)
    if skel.endswith("yn") and skel[:-2] in BRADY_LEX:
        return True, f"{BRADY_LEX[skel[:-2]][0]}-yn"
    return False, None

# =========================================================================
# 3. Decode the corpus
# =========================================================================
line_streams = []   # list of lists of (skel, matched, reading)
for folio in corpus["folios"]:
    cur = folio.get("currier_language", "?")
    for line in folio["lines"]:
        stream = []
        for w in line["words"]:
            skel = to_skeleton(w)
            ok, rd = match(skel)
            stream.append((skel, ok, rd))
        line_streams.append({"currier": cur, "stream": stream})

# Flatten
all_tokens = [t for L in line_streams for t in L["stream"]]
total = len(all_tokens)
matched = sum(1 for t in all_tokens if t[1])
print("=" * 72)
print("  BRADY DANI RECONSTRUCTION — Brain-V proxy")
print("=" * 72)
print(f"  Corpus tokens:     {total:,}")
print(f"  Proxy lexicon:     {len(BRADY_LEX)} skeletons")
print(f"  Matched:           {matched:,}  ({matched/total:.2%})")
print(f"  (Brady reports 86.9% with full 1,334-entry lexicon)")

# =========================================================================
# 4. Syriac-flavoured coherence metrics
# =========================================================================
# (a) match_rate: fraction of tokens matched (same as above)
# (b) connector->content bigrams: fraction of connector tokens followed
#     immediately by a matched non-connector (expected in Syriac prose:
#     wa-NOUN, d-NOUN, l-NOUN)
# (c) match_adjacency: fraction of adjacent token pairs where BOTH are
#     matched (coherence islands; should be >> chance if syntax is present)
# (d) conn_fraction_among_matched: prevalence of function words among
#     matched tokens (should be high and stable)
#
# In-order vs shuffled-across-corpus:
#   If shuffled ≈ in-order, no syntactic signal beyond token-level matching.

def coherence(tokens):
    n = len(tokens)
    if n < 3:
        return dict(match=0, conn_content=0, both_matched=0, conn_frac=0)
    m = sum(1 for _, ok, _ in tokens if ok)
    # bigram metrics
    conn_content = 0
    conn_count = 0
    both_matched = 0
    pairs = 0
    for a, b in zip(tokens, tokens[1:]):
        pairs += 1
        a_skel, a_ok, _ = a
        b_skel, b_ok, _ = b
        if a_skel in CONNECTORS:
            conn_count += 1
            if b_ok and b_skel not in CONNECTORS:
                conn_content += 1
        if a_ok and b_ok:
            both_matched += 1
    conn_content_rate = conn_content / conn_count if conn_count else 0
    both_matched_rate = both_matched / pairs if pairs else 0
    matched_toks = [t for t in tokens if t[1]]
    conn_frac = (sum(1 for t in matched_toks if t[0] in CONNECTORS)
                 / len(matched_toks)) if matched_toks else 0
    return dict(
        match=m/n,
        conn_content=conn_content_rate,
        both_matched=both_matched_rate,
        conn_frac=conn_frac,
    )

# Per-line in-order scoring
in_order_scores = defaultdict(list)
for L in line_streams:
    s = L["stream"]
    if len(s) < 3:
        continue
    c = coherence(s)
    for k, v in c.items():
        in_order_scores[k].append(v)

# Shuffled: pool all tokens across corpus, shuffle, redistribute by line length
random.seed(0)
pool = list(all_tokens)
random.shuffle(pool)
idx = 0
shuffled_scores = defaultdict(list)
for L in line_streams:
    s = L["stream"]
    if len(s) < 3:
        continue
    sample = pool[idx:idx+len(s)]
    idx += len(s)
    if len(sample) < 3:
        break
    c = coherence(sample)
    for k, v in c.items():
        shuffled_scores[k].append(v)

print("\n  SHUFFLE TEST — in-order vs across-corpus shuffled")
print("  " + "-" * 66)
print(f"  {'metric':<22} {'in-order':>10} {'shuffled':>10} {'delta':>10}")
deltas = {}
for k in ("match", "conn_content", "both_matched", "conn_frac"):
    io = statistics.mean(in_order_scores[k])
    sh = statistics.mean(shuffled_scores[k])
    d = io - sh
    deltas[k] = d
    print(f"  {k:<22} {io:>10.4f} {sh:>10.4f} {d:>+10.4f}")

# =========================================================================
# 5. Verdict
# =========================================================================
print("\n  VERDICT")
print("  " + "-" * 66)
cc = deltas["conn_content"]
bm = deltas["both_matched"]
print(f"  connector→content delta (in-order − shuffled): {cc:+.4f}")
print(f"    In-order Syriac prose should have HIGHER conn→content bigrams")
print(f"    than random, because wa-/d-/l- prefix nouns deliberately.")
print(f"  both-matched-adjacent delta:                     {bm:+.4f}")
print(f"    In-order text should form coherence islands more than random.")

if cc > 0.015 and bm > 0.005:
    print("\n  -> Shuffle-test RESULT: Brady's decoded stream carries a MODEST")
    print("     syntactic signal beyond token-level matching. Survives shuffle.")
elif cc > 0.005 or bm > 0.005:
    print("\n  -> Shuffle-test RESULT: WEAK signal — barely distinguishable from")
    print("     shuffled decoded text. Parallel to Schechter's failure.")
else:
    print("\n  -> Shuffle-test RESULT: NO syntactic signal. Brady's decoded")
    print("     output is no more Syriac-like in-order than shuffled.")
    print("     Same failure mode as Schechter's Latin.")

# =========================================================================
# 6. A/B replication sanity check with expanded lexicon
# =========================================================================
print("\n  A/B REPLICATION (expanded proxy, n=~75 terms)")
print("  " + "-" * 66)
cov_by_cur = defaultdict(lambda: [0, 0])
for L in line_streams:
    cur = L["currier"]
    if cur not in ("A", "B"):
        continue
    for _, ok, _ in L["stream"]:
        cov_by_cur[cur][1] += 1
        if ok:
            cov_by_cur[cur][0] += 1
for cur in ("A", "B"):
    m, t = cov_by_cur[cur]
    print(f"  Currier {cur}: {m:,}/{t:,} = {m/t:.2%}")
mA, tA = cov_by_cur["A"]
mB, tB = cov_by_cur["B"]
gap = mB/tB - mA/tA
print(f"  B-A gap: {gap:+.2%}  (prior run with 35-term proxy: +3.92%)")
