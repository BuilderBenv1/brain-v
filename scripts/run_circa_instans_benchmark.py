"""
Execute pre-registered H-BV-CIRCA-INSTANS-BENCHMARK-01.

Benchmark Hand A against a medieval Latin herbal-encyclopedic text.
Circa Instans unavailable in clean digital form; using Macer Floridus
(De viribus herbarum, Choulant 1832 edition from archive.org).

Pipeline identical to H-BV-RECIPE-STRUCTURE-01 but applied to Macer:
  - HIGH/LOW split at cumulative-50% rank
  - Paragraph detection via chapter headings
  - 5 comparison measures vs Hand A

Decision (locked):
  CONFIRMED if Macer: header-recur<10% AND disjunction>=0.70 AND
    top-20 medial reuse>=15/20 AND cross-class<0.52
  REFUTED if Macer: header-recur>=30% OR cross-class>=0.55
  MARGINAL otherwise
"""
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
REF = ROOT / "raw/corpus/reference-corpora"

# =============================================================================
# Load and clean Macer Floridus
# =============================================================================
raw = (REF / "macer_floridus_raw.txt").read_text(encoding="utf-8", errors="replace")
lines = raw.split("\n")

# Locate Macer content start and end
start_idx = end_idx = None
for i, L in enumerate(lines):
    if start_idx is None and re.search(r"^\s*II?l?\.?\s*ABSINTHIUM", L):
        start_idx = i
    if start_idx is not None and re.match(r"^\s*CONFECTBUCH", L):
        end_idx = i; break
if end_idx is None:
    end_idx = len(lines)
content = lines[start_idx:end_idx]
print(f"Macer content window: lines {start_idx}..{end_idx} ({len(content)} lines)")

# Per-chapter segmentation: detect chapter-heading lines
# Pattern: roman numeral + period + uppercase plant name (often ends with period)
CHAPTER_RE = re.compile(r"^\s*[IVXLCDM]+l?\.\s*[A-Z][A-Z]+")
GREEK_RE = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")

def is_apparatus(line):
    if GREEK_RE.search(line):
        return True
    # Lines starting with digit followed by space are apparatus
    if re.match(r"^\s*\d+\s", line):
        return True
    return False

# Step through content, group lines into chapter blocks
chapters = []  # list of list-of-lines (clean body of each chapter)
current = []
in_chapter = False
for L in content:
    if CHAPTER_RE.match(L):
        if in_chapter and current:
            chapters.append(current)
        current = []
        in_chapter = True
        continue
    if not in_chapter:
        continue
    if is_apparatus(L):
        continue
    current.append(L)
if current and in_chapter:
    chapters.append(current)

print(f"Chapters detected: {len(chapters)}")

# Tokenize: lowercase, strip non-alpha, Latin only
def tokenize_latin(lines_list):
    text = " ".join(lines_list).lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    return text.split()

chapter_tokens = [tokenize_latin(c) for c in chapters]
chapter_tokens = [ct for ct in chapter_tokens if len(ct) >= 3]
flat_tokens = [w for ct in chapter_tokens for w in ct]
print(f"Total Macer tokens (filtered): {len(flat_tokens)}")

# Truncate to 11022 tokens — preserving chapter structure
TARGET = 11022
used_chapters = []
total = 0
for ct in chapter_tokens:
    if total + len(ct) <= TARGET:
        used_chapters.append(ct)
        total += len(ct)
    elif TARGET - total >= 3:
        used_chapters.append(ct[:TARGET - total])
        total = TARGET
        break
    else:
        break
print(f"Used {len(used_chapters)} chapters totalling {total} tokens")

macer_flat = [w for c in used_chapters for w in c]

# =============================================================================
# HIGH/LOW split at cumulative-50% rank
# =============================================================================
freq = Counter(macer_flat)
Nt = sum(freq.values())
st = freq.most_common()
cum = 0; R = 0
for i, (t, c) in enumerate(st, 1):
    cum += c
    if cum >= Nt / 2:
        R = i; break
HIGH_TYPES = {t for t, _ in st[:R]}
print(f"\nMacer HIGH: {R} types covering {cum} tokens ({100*cum/Nt:.1f}%)")
print(f"Macer LOW:  {len(freq) - R} types ({Nt - cum} tokens)")

# =============================================================================
# Position bins per chapter (same as RECIPE-STRUCTURE-01)
# =============================================================================
def bin_of(pos, n):
    if pos == 0: return "INITIAL"
    third = math.ceil(n / 3)
    if pos < third: return "FIRST"
    if pos < math.ceil(2*n / 3): return "MIDDLE"
    return "FINAL"

bin_tokens = defaultdict(list)
bin_types = defaultdict(set)
initial_paragraph_count = Counter()  # token -> # chapters it initiates
token_chapters = defaultdict(set)    # token -> {chapter_idx}

for ci, tokens in enumerate(used_chapters):
    n = len(tokens)
    if n == 0: continue
    for pos, w in enumerate(tokens):
        b = bin_of(pos, n)
        bin_tokens[b].append(w)
        bin_types[b].add(w)
        token_chapters[w].add(ci)
    initial_paragraph_count[tokens[0]] += 1

for b in ("INITIAL","FIRST","MIDDLE","FINAL"):
    print(f"  {b:<8}: {len(bin_tokens[b]):>5} tokens, {len(bin_types[b]):>4} types")

# =============================================================================
# Measure 1 — vocabulary disjunction
# =============================================================================
I_types = bin_types["INITIAL"]
M_types = bin_types["MIDDLE"]
disjunct = I_types - M_types
disj_ratio = len(disjunct) / len(I_types) if I_types else 0

# =============================================================================
# Measure 2 — top-20 middle recipe-verb properties
# =============================================================================
def latin_skeleton(word):
    return re.sub(r"[aeiou]", "", word)

# Global skeleton index
skel_to_words = defaultdict(set)
for w in set(macer_flat):
    skel_to_words[latin_skeleton(w)].add(w)

middle_counts = Counter(bin_tokens["MIDDLE"])
top20 = middle_counts.most_common(20)
n_chapters = len(used_chapters)
crit2_passes = 0
top20_details = []
for tok, cnt in top20:
    sk = latin_skeleton(tok)
    variants = len(skel_to_words[sk])
    n_ch = len(token_chapters[tok])
    cov = n_ch / n_chapters if n_chapters else 0
    passed = variants >= 2 and cov >= 0.30
    if passed: crit2_passes += 1
    top20_details.append({
        "token": tok, "count": cnt, "skeleton": sk,
        "n_variants": variants, "n_chapters": n_ch,
        "coverage": round(cov, 3), "pass": passed,
    })

# =============================================================================
# Measure 3 — header recurrence rate
# =============================================================================
initial_types = set(bin_tokens["INITIAL"])
n_initial_types = len(initial_types)
recur_types = [t for t in initial_types if initial_paragraph_count[t] >= 3]
recur_ratio = len(recur_types) / n_initial_types if n_initial_types else 0
top_recur = sorted([(t, initial_paragraph_count[t]) for t in recur_types],
                    key=lambda x: -x[1])[:10]

# =============================================================================
# Measure 4 — cross-class adjacency
# =============================================================================
def is_high(w): return w in HIGH_TYPES

hh = hl = lh = ll = 0
for tokens in used_chapters:
    for a, b in zip(tokens, tokens[1:]):
        ah = is_high(a); bh = is_high(b)
        if ah and bh: hh += 1
        elif ah and not bh: hl += 1
        elif not ah and bh: lh += 1
        else: ll += 1
tot = hh + hl + lh + ll
cross_rate = (hl + lh) / tot if tot else 0
hh_rate = hh / tot if tot else 0
ll_rate = ll / tot if tot else 0

# =============================================================================
# Report
# =============================================================================
# Hand-A values from prior tests
HAND_A = {
    "R_split": 146,
    "high_pct": 0.501,
    "n_paragraphs": 271,
    "disjunction_ratio": 0.850,
    "top20_medial_passes": 19,
    "header_recurrence": 0.046,
    "cross_class_rate": 0.469,
}

print("\n" + "="*86)
print("  MACER FLORIDUS BENCHMARK vs HAND A")
print("="*86)
print(f"  {'measure':<36}{'Hand A':>14}{'Macer':>14}{'match?':>10}")

rows = [
    ("R (rank for cum 50%)", HAND_A["R_split"], R, None),
    ("HIGH class % tokens", HAND_A["high_pct"]*100, cum/Nt*100, None),
    ("n paragraphs/chapters", HAND_A["n_paragraphs"], len(used_chapters), None),
    ("vocab disjunction |I\\M|/|I|", HAND_A["disjunction_ratio"], disj_ratio,
      "PASS >=0.70"),
    ("top-20 medial recipe-verbs/20", HAND_A["top20_medial_passes"], crit2_passes,
      "PASS >=15"),
    ("header recurrence rate", HAND_A["header_recurrence"], recur_ratio,
      "match if <0.10"),
    ("cross-class rate HL+LH", HAND_A["cross_class_rate"], cross_rate,
      "match if <0.52"),
]
for lbl, ha, m, thr in rows:
    ha_s = f"{ha:.3f}" if isinstance(ha, float) and ha < 10 else f"{ha:.0f}" if isinstance(ha, (int, float)) and ha > 10 else f"{ha}"
    m_s = f"{m:.3f}" if isinstance(m, float) and m < 10 else f"{m:.0f}" if isinstance(m, (int, float)) and m > 10 else f"{m}"
    notes = thr if thr else ""
    print(f"  {lbl:<36}{ha_s:>14}{m_s:>14}  {notes}")

# =============================================================================
# Decision
# =============================================================================
print("\n" + "="*86)
print("  PRE-REGISTERED DECISION")
print("="*86)

criteria = {
    "header_recur_lt_10pct":    recur_ratio < 0.10,
    "disjunction_ge_70pct":     disj_ratio >= 0.70,
    "top20_medial_ge_15":       crit2_passes >= 15,
    "cross_class_lt_52pct":     cross_rate < 0.52,
}
n_pass = sum(criteria.values())
for k, v in criteria.items():
    print(f"    {k:<32} {'PASS' if v else 'FAIL'}")

recur_refute = recur_ratio >= 0.30
cross_refute = cross_rate >= 0.55

print(f"\n  All 4 signature features pass? {n_pass == 4}")
print(f"  Recipe-manual refute conditions: header-recur>=30%? {recur_refute}")
print(f"                                   cross-class>=55%?  {cross_refute}")

if n_pass == 4 and not (recur_refute or cross_refute):
    verdict = "CONFIRMED"
    print(f"  -> CONFIRMED. Macer Floridus reproduces all 4 Hand-A signature")
    print(f"     features. Herbal-encyclopedic framework is CORRECT for Hand A.")
elif recur_refute or cross_refute:
    verdict = "REFUTED"
    print(f"  -> REFUTED. Macer shows classical-recipe or natural-language pattern.")
    print(f"     The herbal-encyclopedic reframe of Hand A is wrong.")
else:
    verdict = "MARGINAL"
    print(f"  -> MARGINAL. {n_pass}/4 signature features match. Partial support")
    print(f"     for herbal-encyclopedic framework; additional comparison text needed.")

out_path = ROOT / "outputs" / "circa_instans_benchmark_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-CIRCA-INSTANS-BENCHMARK-01",
    "primary_corpus": "Macer Floridus, De viribus herbarum (Choulant 1832)",
    "circa_instans_status": "not available in clean digital plaintext; Macer Floridus substituted",
    "n_macer_tokens_used": total,
    "n_macer_chapters_used": len(used_chapters),
    "macer_R_split": R,
    "macer": {
        "disjunction_ratio": round(disj_ratio, 4),
        "top20_medial_passes_of_20": crit2_passes,
        "top20_details": top20_details,
        "header_recurrence_rate": round(recur_ratio, 4),
        "n_initial_types": n_initial_types,
        "n_recurring_types": len(recur_types),
        "top_recurring_headers": [{"token": t, "chapters": n} for t, n in top_recur],
        "cross_class_rate": round(cross_rate, 4),
        "HH_rate": round(hh_rate, 4),
        "LL_rate": round(ll_rate, 4),
    },
    "hand_a_priors": HAND_A,
    "criteria": criteria,
    "n_criteria_passing_of_4": n_pass,
    "recipe_manual_refute_triggered": (recur_refute or cross_refute),
    "verdict": verdict,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
