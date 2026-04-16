"""
Execute pre-registered H-BV-NOMENCLATOR-NLREF-01.

Compare Hand A's head/tail vocabulary gaps against natural-language
reference corpora (Latin Vulgate Genesis+Exodus+Leviticus, Italian
Dante Divina Commedia), each truncated to 11,022 tokens.

Decision (locked):
  >=3 of 5 Hand-A gaps more extreme (predicted direction) than BOTH
    references -> NOMENCLATOR-SUPPORTED
  1-2 of 5 -> AMBIGUOUS
  0 of 5 -> NOT-NOMENCLATOR (NOMENCLATOR-01 reinterpreted as ordinary
    natural-language function-vs-content stratification)
"""
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(r"C:\Projects\brain-v")
REF = ROOT / "raw/corpus/reference-corpora"
TARGET_TOKENS = 11022

# =============================================================================
# Hand A — same EVA tokenisation as NOMENCLATOR-01
# =============================================================================
MULTI_GLYPHS = ["ckh", "cth", "cph", "ch", "sh"]

def eva_tokenize(word):
    out = []; i = 0
    while i < len(word):
        matched = False
        for t in MULTI_GLYPHS:
            if word.startswith(t, i):
                out.append(t); i += len(t); matched = True; break
        if not matched:
            out.append(word[i]); i += 1
    return out

def latin_tokenize(word):
    return list(word)

# =============================================================================
# Corpus loaders
# =============================================================================
class VulgateExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_li = False
        self.text = []
    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self.in_li = True
    def handle_endtag(self, tag):
        if tag == "li":
            self.in_li = False
            self.text.append(" ")
    def handle_data(self, data):
        if self.in_li:
            self.text.append(data)

def load_vulgate():
    """Concatenate Genesis + Exodus + Leviticus, strip HTML, lowercase, strip
    punctuation, return word list."""
    all_text = []
    for book in ("Genesis", "Exodus", "Leviticus"):
        html_path = REF / f"vulgate_{book}.html"
        html = html_path.read_text(encoding="latin-1")
        ex = VulgateExtractor()
        ex.feed(html)
        all_text.append("".join(ex.text))
    raw = " ".join(all_text).lower()
    # strip punctuation, keep ASCII letters and spaces
    raw = re.sub(r"[^a-zA-Z\s]", " ", raw)
    words = raw.split()
    return words

def load_dante():
    """Strip Project Gutenberg header/footer, lowercase, strip punctuation."""
    text = (REF / "dante.txt").read_text(encoding="utf-8")
    # Find Gutenberg start/end markers
    start = re.search(r"\*\*\* START OF.*?\*\*\*", text)
    end = re.search(r"\*\*\* END OF.*?\*\*\*", text)
    if start: text = text[start.end():]
    if end: text = text[:end.start()]
    text = text.lower()
    # Italian: keep accented letters; strip punctuation only
    # Replace fancy quotes/dashes
    text = re.sub(r"[\u2018\u2019\u201c\u201d\u2014\u2013]", " ", text)
    # Strip everything except letters (incl accented) and whitespace
    text = re.sub(r"[^a-zA-Z\u00c0-\u017f\s]", " ", text)
    words = text.split()
    return words

def load_hand_a():
    corpus = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
    words = []
    for f in corpus["folios"]:
        if f.get("currier_language") != "A":
            continue
        for line in f["lines"]:
            words.extend(line["words"])
    return words

# =============================================================================
# Measures (identical to NOMENCLATOR-01)
# =============================================================================
def zipf_exponent(items):
    n = len(items)
    if n < 3: return 0.0
    log_rank = [math.log(i+1) for i in range(n)]
    log_freq = [math.log(c) for _, c in items]
    mr = sum(log_rank)/n
    mf = sum(log_freq)/n
    num = sum((log_rank[i]-mr)*(log_freq[i]-mf) for i in range(n))
    den = sum((log_rank[i]-mr)**2 for i in range(n))
    return -(num/den) if den else 0.0

def glyph_entropy_weighted(items, tokenize):
    counts = Counter()
    for t, c in items:
        for g in tokenize(t):
            counts[g] += c
    total = sum(counts.values())
    if total == 0: return 0.0
    H = 0.0
    for c in counts.values():
        p = c/total
        if p > 0: H -= p * math.log2(p)
    return H

def type_glyph_entropy(items, tokenize):
    counts = Counter()
    for t, _ in items:
        for g in tokenize(t):
            counts[g] += 1
    total = sum(counts.values())
    if total == 0: return 0.0
    H = 0.0
    for c in counts.values():
        p = c/total
        if p > 0: H -= p * math.log2(p)
    return H

def mean_length_stddev(items, tokenize):
    lengths = []
    for t, c in items:
        L = len(tokenize(t))
        lengths.extend([L] * c)
    if len(lengths) < 2: return 0.0, 0.0
    return statistics.mean(lengths), statistics.stdev(lengths)

def measure(items, tokenize):
    z = zipf_exponent(items)
    H_w = glyph_entropy_weighted(items, tokenize)
    H_t = type_glyph_entropy(items, tokenize)
    mL, sL = mean_length_stddev(items, tokenize)
    return {"zipf": z, "glyph_entropy_weighted": H_w,
            "type_glyph_entropy": H_t, "mean_length": mL,
            "length_stddev": sL}

def analyze(words, tokenize, label):
    """Run head/tail split + 5 measures on a token list. Truncate to TARGET_TOKENS."""
    if len(words) < TARGET_TOKENS:
        print(f"  WARNING: {label} has only {len(words)} tokens, less than target {TARGET_TOKENS}")
    words = words[:TARGET_TOKENS]
    freq = Counter(words)
    N_total = sum(freq.values())
    N_types = len(freq)
    sorted_types = freq.most_common()
    cum = 0; R = 0
    for i, (t, c) in enumerate(sorted_types, 1):
        cum += c
        if cum >= N_total / 2:
            R = i; break
    high = sorted_types[:R]
    low = sorted_types[R:]
    m_high = measure(high, tokenize)
    m_low = measure(low, tokenize)
    gaps = {k: m_high[k] - m_low[k] for k in m_high}
    return {
        "label": label,
        "n_tokens": N_total,
        "n_types": N_types,
        "split_R": R,
        "cumulative_high_pct": round(100*cum/N_total, 2),
        "high": {k: round(v, 4) for k, v in m_high.items()},
        "low": {k: round(v, 4) for k, v in m_low.items()},
        "gaps": {k: round(v, 4) for k, v in gaps.items()},
    }

# =============================================================================
# Run analyses
# =============================================================================
print("Loading corpora...")
hand_a_words = load_hand_a()
print(f"  Hand A: {len(hand_a_words)} tokens (will use first {TARGET_TOKENS})")

vulgate_words = load_vulgate()
print(f"  Vulgate (Gen+Exod+Lev): {len(vulgate_words)} tokens (will use first {TARGET_TOKENS})")

dante_words = load_dante()
print(f"  Dante Divina Commedia:  {len(dante_words)} tokens (will use first {TARGET_TOKENS})")

hand_a = analyze(hand_a_words, eva_tokenize, "hand_a")
vulgate = analyze(vulgate_words, latin_tokenize, "vulgate_latin")
dante = analyze(dante_words, latin_tokenize, "dante_italian")

# =============================================================================
# Comparison
# =============================================================================
PREDICTED = {
    "zipf": +1,
    "glyph_entropy_weighted": -1,
    "type_glyph_entropy": -1,
    "mean_length": -1,
    "length_stddev": +1,
}

def is_more_extreme(a_gap, ref_gap, predicted_sign):
    """True if a_gap is more extreme than ref_gap in predicted_sign direction."""
    if predicted_sign > 0:
        return a_gap > ref_gap
    else:
        return a_gap < ref_gap

print("\n" + "="*86)
print("  HEAD/TAIL GAPS — Hand A vs natural-language references")
print("="*86)
print(f"  {'measure':<26}{'Hand A':>12}{'Vulgate':>12}{'Dante':>12}{'pred':>6}{'A>both?':>10}")

n_more_extreme = 0
results = []
for k, sign in PREDICTED.items():
    ag = hand_a["gaps"][k]
    vg = vulgate["gaps"][k]
    dg = dante["gaps"][k]
    more_v = is_more_extreme(ag, vg, sign)
    more_d = is_more_extreme(ag, dg, sign)
    both = more_v and more_d
    if both: n_more_extreme += 1
    sign_str = "+" if sign > 0 else "-"
    yn = "YES" if both else "no"
    print(f"  {k:<26}{ag:>+12.4f}{vg:>+12.4f}{dg:>+12.4f}{sign_str:>6}{yn:>10}")
    results.append({
        "measure": k, "predicted_direction": sign,
        "hand_a_gap": round(ag, 4),
        "vulgate_gap": round(vg, 4),
        "dante_gap": round(dg, 4),
        "more_extreme_than_vulgate": more_v,
        "more_extreme_than_dante": more_d,
        "more_extreme_than_both": both,
    })

# =============================================================================
# Decision
# =============================================================================
print("\n" + "="*86)
print("  PRE-REGISTERED DECISION")
print("="*86)
print(f"  Hand A more extreme than BOTH references: {n_more_extreme}/5 measures")

if n_more_extreme >= 3:
    verdict = "NOMENCLATOR-SUPPORTED"
    print(f"  -> NOMENCLATOR-SUPPORTED. Hand A's two-population structure")
    print(f"     significantly exceeds natural-language reference baselines.")
elif n_more_extreme >= 1:
    verdict = "AMBIGUOUS"
    print(f"  -> AMBIGUOUS. Hand A is partially distinct from references but")
    print(f"     not decisively. The cipher-specific reading is weakened.")
else:
    verdict = "NOT-NOMENCLATOR"
    print(f"  -> NOT-NOMENCLATOR. Hand A's head/tail gaps fall within the")
    print(f"     natural-language reference range. The H-BV-NOMENCLATOR-01")
    print(f"     confirmation is reinterpreted as ordinary function-vs-content")
    print(f"     stratification, NOT a cipher signature.")

# Save
out_path = ROOT / "outputs" / "nomenclator_nlref_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-NOMENCLATOR-NLREF-01",
    "target_tokens": TARGET_TOKENS,
    "hand_a": hand_a,
    "vulgate_latin": vulgate,
    "dante_italian": dante,
    "comparison": results,
    "n_hand_a_more_extreme_than_both_refs": n_more_extreme,
    "verdict": verdict,
    "thresholds": {
        "supported": ">=3 of 5",
        "ambiguous": "1-2 of 5",
        "not_nomenclator": "0 of 5",
    },
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
