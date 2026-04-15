"""
Two tests in one cycle:

(1) H-BRADY-02 — gallows positional enrichment.
    Plain gallows 't','p' predicted at 42.3% / 70.9% line-initial vs 13.1% baseline.
    Bench gallows 'cth','ckh','cph' predicted at 0-4% line-initial (normal mid-word).

(2) Currier A vs B under BOTH decipherments:
    - Schechter already tested: A coverage 78.1%, B 86.3%.
    - Brady's Syriac DANI mapping: apply his char map, produce skeletons,
      match against a reduced proxy of his lexicon (we don't have the
      1,334-entry JSON, so we use the high-frequency skeletons documented
      in the paper: kdy/kdn/yn/kl/kr/dr/tr/kol/krihā/akakiya/kadda/kyana/
      shayya + 30 more from Brady's paper). This is a proxy, not the full
      test; we'll flag it as such.

If both glossaries show the same A-worse-than-B asymmetry, that is a
structural property of the manuscript, not an artefact of either hypothesis.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "scripts")
import decrypt

CORPUS_JSON = Path(r"C:\Projects\brain-v\raw\perception\voynich-corpus.json")
GLOSS_CSV = Path(r"C:\Projects\brain-v\raw\schechter_glossary.csv")

corpus = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))

# ===========================================================================
# TEST 1 — Gallows positional enrichment (H-BRADY-02)
# ===========================================================================
# First-word-of-line rate for each gallows character sequence.
# Brady's 13.1% baseline is for "token in the EVA corpus"; i.e. the probability
# a random token starts with the char. His line-initial % means: given a line,
# what fraction of those lines have their first EVA word starting with the char.
print("=" * 72)
print("  TEST 1 — H-BRADY-02 gallows positional enrichment")
print("=" * 72)

# Correct parsing: Brady says "Line-initial %" is the share of LINES where the
# first token starts with this character. "Baseline %" is the share of ALL
# tokens starting with this character. Enrichment = initial / baseline.
CHARS = ["t", "p", "cth", "ckh", "cph"]

# Count over the corpus
total_tokens = 0
start_counts = Counter()
total_lines = 0
line_initial_counts = Counter()

for folio in corpus["folios"]:
    for line in folio["lines"]:
        words = line["words"]
        if not words:
            continue
        total_lines += 1
        first = words[0]
        for ch in CHARS:
            if first.startswith(ch):
                line_initial_counts[ch] += 1
        for w in words:
            total_tokens += 1
            for ch in CHARS:
                if w.startswith(ch):
                    start_counts[ch] += 1

print(f"  Corpus: {total_tokens:,} tokens, {total_lines:,} lines")
print(f"  {'char':<6} {'line-init%':>11} {'baseline%':>11} {'enrichment':>12} "
      f"{'Brady pred':>12}")

BRADY_PRED = {
    "t":   (42.3, 13.1, 3.2),
    "p":   (70.9, 13.1, 5.4),
    "cth": (None, 13.1, "normal"),
    "ckh": (None, 13.1, "normal"),
    "cph": (None, 13.1, "normal"),
}
# Handle prefix overlap: "cth"/"ckh"/"cph" all start with 'c', not 't'/'p'.
# But our counter uses startswith so 'cth' won't be double-counted as 't'.
# Good — 't' and 'cth' are disjoint prefix tests.

for ch in CHARS:
    li = line_initial_counts[ch] / total_lines * 100
    bl = start_counts[ch] / total_tokens * 100
    enr = li / bl if bl > 0 else float("inf")
    pred = BRADY_PRED[ch]
    pred_str = f"{pred[2]}" if isinstance(pred[2], str) else f"{pred[2]:.1f}x"
    print(f"  {ch:<6} {li:>10.1f}% {bl:>10.1f}% {enr:>11.1f}x {pred_str:>12}")

# Verdict
t_enr = (line_initial_counts["t"]/total_lines) / (start_counts["t"]/total_tokens)
p_enr = (line_initial_counts["p"]/total_lines) / (start_counts["p"]/total_tokens)
cth_enr = ((line_initial_counts["cth"]/total_lines) /
           (start_counts["cth"]/total_tokens)) if start_counts["cth"] else 0
ckh_enr = ((line_initial_counts["ckh"]/total_lines) /
           (start_counts["ckh"]/total_tokens)) if start_counts["ckh"] else 0
print()
print(f"  Brady prediction: plain-gallows ENR >> bench-gallows ENR (~1.0x)")
if t_enr > 2.0 and p_enr > 3.5 and cth_enr < 1.5 and ckh_enr < 1.5:
    print(f"  -> H-BRADY-02 CONFIRMED: plain gallows heavily line-initial, bench gallows flat")
elif t_enr > 1.5 and p_enr > 2.5:
    print(f"  -> H-BRADY-02 PARTIALLY SUPPORTED: directional match, magnitudes differ")
else:
    print(f"  -> H-BRADY-02 CHALLENGED: predicted asymmetry not reproduced")

# ===========================================================================
# TEST 2 — Currier A vs B under Schechter + Brady
# ===========================================================================
print()
print("=" * 72)
print("  TEST 2 — Currier A vs B across BOTH decipherments")
print("=" * 72)

# --- Schechter side: reuse existing glossary
GLOSS = {}
with GLOSS_CSV.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        GLOSS[row["eva"]] = row["decoded"]

# --- Brady side: character map + proxy lexicon of documented skeletons ---
# EVA -> Syriac consonant map from Brady §2.2
EVA_MAP = [
    # Order matters: longer sequences first
    ("cth", "tk"),    # bench gallows mid-word
    ("ckh", "kk"),
    ("cph", "pk"),
    ("ch",  "k"),     # kaph/qoph merged
    ("sh",  "s"),     # š -> s  (we treat sheen as s for matching)
    ("k",   "k"),
    ("d",   "d"),
    ("r",   "r"),
    ("s",   "s"),
    ("l",   "l"),
    ("n",   "n"),
    ("y",   "y"),
    ("m",   "m"),
    ("g",   "g"),
    ("t",   "t"),     # gallows but we include; optional strip below
    ("p",   "p"),
    ("f",   "s"),     # tsade -> s (approx)
    ("q",   "w"),
    # vowels dropped
]
VOWELS = set("aoei")

def to_skeleton(word, strip_plain_gallows=True):
    """Apply Brady's EVA->Syriac char map with vowel stripping."""
    # Optionally strip a leading plain gallows if present (paragraph marker rule)
    if strip_plain_gallows and word and word[0] in "tp":
        # Only strip if NOT followed by a bench gallows sequence start
        # (crude: if next char is not 'h' or end)
        if len(word) == 1 or word[1] not in "h":
            word = word[1:]
    out = []
    i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                if sy:
                    out.append(sy)
                i += len(ev)
                matched = True
                break
        if not matched:
            if word[i] in VOWELS:
                i += 1
            else:
                # unknown char -> skip
                i += 1
    return "".join(out)

# Brady proxy lexicon: skeletons explicitly cited in the paper.
# This is a MINIMAL subset (~30 terms) of his 1,334-entry lexicon, so coverage
# will be far below his reported 86.9%. But the A/B DELTA is what we care about —
# does the same-language claim reproduce Schechter's B>A gap or invert it?
BRADY_LEX = {
    "kdy": "kaddīn",          # temporal adverb (Syriac)
    "kdn": "kəḏēn",           # JBA
    "yn":  "ʿaynā",           # eye
    "kl":  "kol/kuḥlā",
    "kr":  "krīhā/kārā",
    "dr":  "dārā/dōrā",
    "tr":  "ṭārā/ṭōrā",
    "sy":  "āsyā",
    "rp":  "rappā",
    "kky": "akākīyā",          # acacia gum — skeleton after kk
    "ks":  "kasīā",           # cassia
    "tn":  "tīnā",            # fig
    "ts":  "ṭaksā",           # dynamis
    "ky":  "kyānā",           # nature
    "sl":  "lāšā",            # to compound (metathesis-aware would go further)
    "ss":  "šāsā",            # to grind
    "tl":  "ṭalī",            # to anoint
    "sm":  "šemʿ",
    "klm": "kallāmā",
    "smy": "samyā",
    "drm": "darma",
    "sry": "sarya",
    "ksy": "kasīā",
    "ml":  "malla",
    "sr":  "sar",
    "kdd": "kaddā",
    "sy>": "āsyā",
    "syy": "šayyā",
    "krh": "krīhā",
    "dl":  "dālā",
    "bl":  "bāl",
    "bn":  "bar",
    # connectors / preps
    "w":   "wa-",
    "d":   "d-",
    "l":   "l-",
    "m":   "m(in)-",
}

# Apply Brady mapping to corpus tokens, track per-currier
line_records = []
for folio in corpus["folios"]:
    sec = folio["section"]
    cur = folio.get("currier_language", "?")
    for line in folio["lines"]:
        skels = [to_skeleton(w) for w in line["words"]]
        line_records.append({"section": sec, "currier": cur,
                             "eva": line["words"], "skels": skels})

def brady_match(skel):
    if skel in BRADY_LEX:
        return True
    # Brady allows stripping waw/lamed/dalet prefix
    if len(skel) >= 2 and skel[0] in "wdl" and skel[1:] in BRADY_LEX:
        return True
    # suffix -yn
    if skel.endswith("yn") and skel[:-2] in BRADY_LEX:
        return True
    return False

# Per-currier coverage, both systems
print()
print(f"  {'side':<10} {'currier':<8} {'lines':>6} {'tokens':>8} "
      f"{'matched':>9} {'coverage':>10}")
print(f"  {'-'*58}")
by_side_cur = defaultdict(lambda: [0, 0])
for rec in line_records:
    cur = rec["currier"]
    if cur not in ("A", "B"):
        continue
    # Schechter
    for w in rec["eva"]:
        by_side_cur[("Schechter", cur)][1] += 1
        if w in GLOSS:
            by_side_cur[("Schechter", cur)][0] += 1
    # Brady proxy
    for s in rec["skels"]:
        by_side_cur[("Brady-proxy", cur)][1] += 1
        if brady_match(s):
            by_side_cur[("Brady-proxy", cur)][0] += 1

for side in ("Schechter", "Brady-proxy"):
    for cur in ("A", "B"):
        m, t = by_side_cur[(side, cur)]
        cov = m / t if t else 0
        print(f"  {side:<10} {cur:<8} {'':>6} {t:>8,} {m:>9,} {cov:>9.2%}")

print()
print(f"  {'side':<15} {'A cov':>8} {'B cov':>8} {'B-A':>8}")
for side in ("Schechter", "Brady-proxy"):
    ma, ta = by_side_cur[(side, "A")]
    mb, tb = by_side_cur[(side, "B")]
    cvA = ma/ta if ta else 0
    cvB = mb/tb if tb else 0
    print(f"  {side:<15} {cvA:>7.2%} {cvB:>7.2%} {cvB-cvA:>+8.2%}")

# Verdict
s_gap = (by_side_cur[("Schechter","B")][0] / by_side_cur[("Schechter","B")][1]
        - by_side_cur[("Schechter","A")][0] / by_side_cur[("Schechter","A")][1])
b_gap = (by_side_cur[("Brady-proxy","B")][0] / by_side_cur[("Brady-proxy","B")][1]
        - by_side_cur[("Brady-proxy","A")][0] / by_side_cur[("Brady-proxy","A")][1])
print()
print(f"  Schechter B-A gap:   {s_gap:+.2%}   (B fits better if >0)")
print(f"  Brady-proxy B-A gap: {b_gap:+.2%}")
if (s_gap > 0.01 and b_gap > 0.01) or (s_gap < -0.01 and b_gap < -0.01):
    direction = "B>A" if s_gap > 0 else "A>B"
    print(f"  -> BOTH glossaries favour {direction} — structural property of MS, not")
    print(f"     of the hypothesis. Currier A/B asymmetry is real.")
elif abs(s_gap) > 0.02 and abs(b_gap) > 0.02:
    print(f"  -> OPPOSITE directions: discriminating. The two hypotheses")
    print(f"     cannot both be simultaneously true — at most one matches the")
    print(f"     dominant dialect.")
else:
    print(f"  -> Mixed/weak signal; larger Brady proxy lexicon needed to confirm.")

print()
print("  Caveat on Brady side: this uses a ~35-term PROXY lexicon derived from")
print("  skeletons mentioned in Brady's paper, not his full 1,334-entry JSON.")
print("  Raw coverage is therefore much lower than Brady's reported 86.9%;")
print("  only the A/B DELTA is interpretable, and only if the proxy is")
print("  representative.")
