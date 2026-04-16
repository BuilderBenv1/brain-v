"""
Execute pre-registered H-BV-HIGH-LOW-STRUCTURE-01.

Four-part structural test on Hand A's HIGH/LOW vocabulary split:
  (1) Line position clustering
  (2) Morphological state (bare stem vs inflected)
  (3) Paragraph role (initial / medial / final)
  (4) Adjacency cross-class rate (Hand A vs Latin/Italian references)

Decision (locked):
  STRUCTURAL if any of Tests 1-3 triggers clustering.
  FUNCTION/CONTENT if Test 4 cross-class in [0.60, 0.80] AND matches
    references within +/- 0.05.
  ORTHOGONAL if no clustering and Test 4 within 0.02 of random 0.50.
"""
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(r"C:\Projects\brain-v")
REF = ROOT / "raw/corpus/reference-corpora"
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
TARGET_TOKENS = 11022
SUFFIX_CHARS = set("ynrmg")

# =============================================================================
# Reproduce HIGH/LOW split (same R=146 from NOMENCLATOR-01)
# =============================================================================
hand_a_words_flat = []
hand_a_lines_all = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_lines_all.append(line["words"])
        hand_a_words_flat.extend(line["words"])

freq = Counter(hand_a_words_flat)
N_total = sum(freq.values())
sorted_types = freq.most_common()
cum = 0; R = 0
for i, (t, c) in enumerate(sorted_types, 1):
    cum += c
    if cum >= N_total / 2:
        R = i; break

HIGH_TYPES = {t for t, _ in sorted_types[:R]}
LOW_TYPES = {t for t, _ in sorted_types[R:]}
assert R == 146
print(f"HIGH: {R} types / {cum} tokens ({100*cum/N_total:.1f}%)")
print(f"LOW:  {len(LOW_TYPES)} types / {N_total - cum} tokens ({100*(N_total-cum)/N_total:.1f}%)")

def is_high(w): return w in HIGH_TYPES

# =============================================================================
# TEST 1 — LINE POSITION QUARTILES
# =============================================================================
print("\n" + "="*78)
print("  TEST 1 — LINE POSITION QUARTILES")
print("="*78)

quartile_high = Counter()
quartile_total = Counter()
for L in hand_a_lines_all:
    if len(L) < 4:
        continue
    n = len(L)
    for i, w in enumerate(L):
        # quartile 0..3
        q = min(3, int(4 * i / n))
        quartile_total[q] += 1
        if is_high(w):
            quartile_high[q] += 1

print(f"  Tokens per quartile (Q1..Q4): "
      f"{[quartile_total[q] for q in range(4)]}")
print(f"  HIGH tokens per quartile:      "
      f"{[quartile_high[q] for q in range(4)]}")
print(f"  HIGH share per quartile:")
q_shares = {}
for q in range(4):
    share = quartile_high[q] / quartile_total[q] if quartile_total[q] else 0
    q_shares[q] = share
    print(f"    Q{q+1}: {share*100:5.1f}%  ({quartile_high[q]}/{quartile_total[q]})")

# Distribution of HIGH tokens across quartiles (normalised so sum=1)
tot_h = sum(quartile_high.values())
q_dist = {q: (quartile_high[q] / tot_h if tot_h else 0) for q in range(4)}
print(f"  HIGH-token distribution across quartiles:")
for q in range(4):
    print(f"    Q{q+1}: {q_dist[q]*100:5.1f}%")
any_q_ge_60 = any(qd >= 0.60 for qd in q_dist.values())
edges_ge_70 = (q_dist[0] + q_dist[3]) >= 0.70
test1_positional = any_q_ge_60 or edges_ge_70
print(f"  Any quartile >=60%?  {any_q_ge_60}")
print(f"  Q1+Q4 >=70% (edges)? {edges_ge_70}  ({(q_dist[0]+q_dist[3])*100:.1f}%)")
print(f"  TEST 1 verdict: {'POSITIONAL' if test1_positional else 'not positional'}")

# =============================================================================
# TEST 2 — MORPHOLOGICAL STATE
# =============================================================================
print("\n" + "="*78)
print("  TEST 2 — MORPHOLOGICAL STATE (bare vs inflected)")
print("="*78)

def count_suffixes(word):
    n = 0
    w = word
    while w and w[-1] in SUFFIX_CHARS and len(w) > 1:
        n += 1
        w = w[:-1]
    return n

suffix_by_class = {"HIGH": Counter(), "LOW": Counter()}
tokens_by_class = {"HIGH": 0, "LOW": 0}
for w in hand_a_words_flat:
    cls = "HIGH" if is_high(w) else "LOW"
    suffix_by_class[cls][count_suffixes(w)] += 1
    tokens_by_class[cls] += 1

for cls in ("HIGH", "LOW"):
    print(f"  {cls}: {tokens_by_class[cls]} tokens")
    total = tokens_by_class[cls]
    for k in sorted(suffix_by_class[cls]):
        pct = suffix_by_class[cls][k] / total
        print(f"    {k} suffixes: {suffix_by_class[cls][k]:>5} ({pct*100:5.1f}%)")

high_0 = suffix_by_class["HIGH"][0] / tokens_by_class["HIGH"]
low_ge2 = sum(v for k, v in suffix_by_class["LOW"].items() if k >= 2) / tokens_by_class["LOW"]
print(f"\n  HIGH 0-suffix:  {high_0*100:5.1f}%  (threshold >=70%)")
print(f"  LOW  >=2-suffix:{low_ge2*100:5.1f}%  (threshold >=50%)")
test2_morph = (high_0 >= 0.70) and (low_ge2 >= 0.50)
print(f"  TEST 2 verdict: {'MORPHOLOGICAL' if test2_morph else 'not morphological'}")

# =============================================================================
# TEST 3 — PARAGRAPH ROLE
# =============================================================================
print("\n" + "="*78)
print("  TEST 3 — PARAGRAPH ROLE")
print("="*78)

def starts_with_plain_gallows(word):
    if not word: return False
    if word[0] not in "tp": return False
    if len(word) == 1: return True
    return word[1] != "h"

# Walk each folio's Hand-A lines in order; detect paragraphs
folio_to_lines = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    if f["lines"]:
        folio_to_lines.append(f["lines"])

paragraphs = []
for lines in folio_to_lines:
    current_para_tokens = []
    for line in lines:
        words = line["words"]
        if not words:
            continue
        if starts_with_plain_gallows(words[0]) and current_para_tokens:
            paragraphs.append(current_para_tokens)
            current_para_tokens = []
        current_para_tokens.extend(words)
    if current_para_tokens:
        paragraphs.append(current_para_tokens)

print(f"  Paragraphs detected: {len(paragraphs)}")

role_counts = {"initial": {"HIGH": 0, "LOW": 0},
               "medial": {"HIGH": 0, "LOW": 0},
               "final": {"HIGH": 0, "LOW": 0}}
for p in paragraphs:
    if not p: continue
    for i, w in enumerate(p):
        if i == 0:
            role = "initial"
        elif i == len(p) - 1:
            role = "final"
        else:
            role = "medial"
        cls = "HIGH" if is_high(w) else "LOW"
        role_counts[role][cls] += 1

print(f"  HIGH-share by role:")
shares = {}
for role in ("initial", "medial", "final"):
    h = role_counts[role]["HIGH"]; l = role_counts[role]["LOW"]
    share = h / (h + l) if (h + l) else 0
    shares[role] = share
    print(f"    {role:<8} HIGH={h:>5} LOW={l:>5}  HIGH-share={share*100:5.1f}%")

boundary_avg = (shares["initial"] + shares["final"]) / 2
medial = shares["medial"]
ratio = boundary_avg / medial if medial else 0
print(f"\n  Boundary HIGH-share (avg initial/final): {boundary_avg*100:5.1f}%")
print(f"  Medial   HIGH-share:                     {medial*100:5.1f}%")
print(f"  Ratio boundary/medial: {ratio:.2f}x (threshold >=1.5x)")
test3_paragraph = ratio >= 1.5
print(f"  TEST 3 verdict: {'PARAGRAPH-ROLE' if test3_paragraph else 'not paragraph-role'}")

# =============================================================================
# TEST 4 — ADJACENCY CROSS-CLASS RATE
# =============================================================================
print("\n" + "="*78)
print("  TEST 4 — ADJACENCY CROSS-CLASS RATE")
print("="*78)

def adjacency_stats(lines, is_high_fn):
    hh = hl = lh = ll = 0
    for L in lines:
        for a, b in zip(L, L[1:]):
            ah = is_high_fn(a); bh = is_high_fn(b)
            if ah and bh: hh += 1
            elif ah and not bh: hl += 1
            elif not ah and bh: lh += 1
            else: ll += 1
    total = hh + hl + lh + ll
    if total == 0: return None
    return {"HH": hh/total, "HL_or_LH": (hl+lh)/total, "LL": ll/total,
            "total_bigrams": total,
            "cross_class_rate": (hl+lh)/total}

adj_hand_a = adjacency_stats(hand_a_lines_all, is_high)
p_high = tokens_by_class["HIGH"] / N_total
expected_cross = 2 * p_high * (1 - p_high)
print(f"  Hand A: HH={adj_hand_a['HH']*100:5.1f}%  "
      f"HL+LH={adj_hand_a['HL_or_LH']*100:5.1f}%  LL={adj_hand_a['LL']*100:5.1f}%  "
      f"(n={adj_hand_a['total_bigrams']})")
print(f"  Random null with p_HIGH={p_high:.3f}: expected cross-class = "
      f"{expected_cross*100:.1f}%")

# =============================================================================
# References: Latin Vulgate and Italian Dante
# =============================================================================
class VulgateExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_li = False; self.text = []
    def handle_starttag(self, tag, attrs):
        if tag == "li": self.in_li = True
    def handle_endtag(self, tag):
        if tag == "li": self.in_li = False; self.text.append(" ")
    def handle_data(self, data):
        if self.in_li: self.text.append(data)

def load_ref_lines(path_html, is_html=True):
    """Return list of word-lists, mimicking 'lines' by splitting at periods."""
    if is_html:
        parts = []
        for book in ("Genesis", "Exodus", "Leviticus"):
            html = (REF / f"vulgate_{book}.html").read_text(encoding="latin-1")
            ex = VulgateExtractor(); ex.feed(html)
            parts.append("".join(ex.text))
        raw = " ".join(parts).lower()
    else:
        raw = (REF / path_html).read_text(encoding="utf-8")
        start = re.search(r"\*\*\* START OF.*?\*\*\*", raw)
        end = re.search(r"\*\*\* END OF.*?\*\*\*", raw)
        if start: raw = raw[start.end():]
        if end: raw = raw[:end.start()]
        raw = raw.lower()
        raw = re.sub(r"[\u2018\u2019\u201c\u201d\u2014\u2013]", " ", raw)
    # Preserve sentence boundaries as proxy for "lines"
    raw = re.sub(r"[;:!?]", ".", raw)
    # Strip non-letter except '.', keep whitespace and letters
    if is_html:
        raw = re.sub(r"[^a-zA-Z.\s]", " ", raw)
    else:
        raw = re.sub(r"[^a-zA-Z\u00c0-\u017f.\s]", " ", raw)
    # Split on '.', tokenize words
    sentences = [s.split() for s in raw.split(".")]
    return [s for s in sentences if s]

def truncate_to_tokens(sentences, n_target):
    out = []; total = 0
    for s in sentences:
        if total + len(s) <= n_target:
            out.append(s); total += len(s)
        else:
            remaining = n_target - total
            if remaining > 0: out.append(s[:remaining])
            break
    return out

def build_high_low_ref(lines, n_target):
    """Truncate to target, compute 50%-cumulative HIGH set, return lines
    + is_high_fn."""
    words = [w for L in lines for w in L]
    # Truncate
    if len(words) > n_target:
        words = words[:n_target]
        # rebuild lines truncated to match
        new_lines = []; total = 0
        for L in lines:
            if total + len(L) <= n_target:
                new_lines.append(L); total += len(L)
            else:
                new_lines.append(L[:n_target - total]); break
        lines = new_lines
    f = Counter(words); Nt = sum(f.values())
    st = f.most_common()
    c = 0; Rref = 0
    for i, (t, cn) in enumerate(st, 1):
        c += cn
        if c >= Nt/2: Rref = i; break
    HIGH_ref = {t for t, _ in st[:Rref]}
    return lines, (lambda w: w in HIGH_ref), Rref, Nt

print("\n  Reference corpora at matched 11,022 tokens:")
for label, sentences_fn in [("Vulgate Latin", lambda: load_ref_lines(None, is_html=True)),
                             ("Dante Italian", lambda: load_ref_lines("dante.txt", is_html=False))]:
    sents = sentences_fn()
    lines_ref, is_h, Rref, Nref = build_high_low_ref(sents, TARGET_TOKENS)
    adj = adjacency_stats(lines_ref, is_h)
    print(f"  {label}: R_split={Rref}, N={Nref}, "
          f"HH={adj['HH']*100:5.1f}%  HL+LH={adj['HL_or_LH']*100:5.1f}%  "
          f"LL={adj['LL']*100:5.1f}%  (n={adj['total_bigrams']})")
    if label == "Vulgate Latin":
        vulgate_cross = adj["HL_or_LH"]
    else:
        dante_cross = adj["HL_or_LH"]

hand_a_cross = adj_hand_a["HL_or_LH"]
ref_cross_avg = (vulgate_cross + dante_cross) / 2
print(f"\n  Hand A cross-class rate:        {hand_a_cross*100:5.1f}%")
print(f"  Vulgate Latin cross-class rate: {vulgate_cross*100:5.1f}%")
print(f"  Dante Italian cross-class rate: {dante_cross*100:5.1f}%")
print(f"  Reference mean:                 {ref_cross_avg*100:5.1f}%")
print(f"  Hand A - reference mean: {(hand_a_cross - ref_cross_avg)*100:+5.2f} pp")

test4_fc = (0.60 <= hand_a_cross <= 0.80 and
            abs(hand_a_cross - vulgate_cross) <= 0.05 and
            abs(hand_a_cross - dante_cross) <= 0.05)
test4_random = abs(hand_a_cross - 0.50) <= 0.02
print(f"  Function/content match? {test4_fc}")
print(f"  At random null (within 0.02 of 0.50)? {test4_random}")

# =============================================================================
# Overall decision
# =============================================================================
print("\n" + "="*78)
print("  PRE-REGISTERED DECISION")
print("="*78)
triggers = {
    "positional (Test 1)": test1_positional,
    "morphological (Test 2)": test2_morph,
    "paragraph-role (Test 3)": test3_paragraph,
}
n_triggers = sum(triggers.values())
print(f"  Structural triggers: {n_triggers}/3")
for name, ok in triggers.items():
    print(f"    {name}: {'TRIGGERED' if ok else 'no'}")

if n_triggers >= 1:
    verdict = "STRUCTURAL"
    which = [n for n, ok in triggers.items() if ok]
    print(f"  -> STRUCTURAL. HIGH/LOW split aligns with: {', '.join(which)}")
elif test4_fc:
    verdict = "FUNCTION_CONTENT"
    print(f"  -> FUNCTION/CONTENT. Cross-class rate matches natural-language")
    print(f"     reference within +/- 0.05. (Tension with HIGH-DECODE-01 refutation.)")
elif test4_random:
    verdict = "ORTHOGONAL"
    print(f"  -> ORTHOGONAL. No clustering on structure axes AND adjacency at")
    print(f"     random null. The HIGH/LOW split is not explained by any of")
    print(f"     the four axes tested.")
else:
    verdict = "PARTIAL_OR_UNRESOLVED"
    print(f"  -> PARTIAL/UNRESOLVED. No structural trigger, cross-class rate")
    print(f"     deviates from random but doesn't match natural-language band.")
    print(f"     Hand A cross-class {hand_a_cross*100:.1f}%.")

out_path = ROOT / "outputs" / "high_low_structure_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-HIGH-LOW-STRUCTURE-01",
    "R_split": R,
    "test_1_line_position": {
        "quartile_high_share": {f"Q{q+1}": round(q_shares[q], 4) for q in range(4)},
        "high_distribution_across_quartiles": {f"Q{q+1}": round(q_dist[q], 4) for q in range(4)},
        "any_quartile_ge_60pct": any_q_ge_60,
        "Q1_plus_Q4_ge_70pct": edges_ge_70,
        "triggered": test1_positional,
    },
    "test_2_morphological": {
        "high_0_suffix_pct": round(high_0, 4),
        "low_ge2_suffix_pct": round(low_ge2, 4),
        "high_suffix_distribution": dict(suffix_by_class["HIGH"]),
        "low_suffix_distribution": dict(suffix_by_class["LOW"]),
        "triggered": test2_morph,
    },
    "test_3_paragraph": {
        "n_paragraphs": len(paragraphs),
        "high_share_by_role": {k: round(v, 4) for k, v in shares.items()},
        "boundary_to_medial_ratio": round(ratio, 3),
        "triggered": test3_paragraph,
    },
    "test_4_adjacency": {
        "hand_a": {k: round(v, 4) if isinstance(v, float) else v for k, v in adj_hand_a.items()},
        "vulgate_cross_class_rate": round(vulgate_cross, 4),
        "dante_cross_class_rate": round(dante_cross, 4),
        "hand_a_cross_class_rate": round(hand_a_cross, 4),
        "random_null_expected": round(expected_cross, 4),
        "function_content_match": test4_fc,
        "at_random_null": test4_random,
    },
    "triggers": triggers,
    "verdict": verdict,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
