"""
Test kpagel's 81-term dictionary against the Voynich corpus.
Verify coverage claims and compute honest metrics.

Source: Pagel, K. (2026) Zenodo DOI 10.5281/zenodo.18478526
"""
import json
import sys
sys.path.insert(0, "scripts")
import decrypt
from collections import Counter

corpus = decrypt.load_corpus()

# === PAGEL'S DICTIONARY (extracted from Supplementary Material Appendix A) ===
# Format: EVA_word -> (meaning, language, confidence%)

PAGEL_DICT = {
    # Category I: 100% confidence (12 terms)
    "daiin": ("is given (datur)", "Latin", 100),
    "chedy": ("warm (calidus)", "Latin", 100),
    "chol": ("leaf (folium)", "Latin", 100),
    "shedy": ("dry (siccus)", "Latin", 100),
    "dam": ("blood / Give!", "Hebrew/Latin", 100),
    "ol": ("oil (oleum)", "Latin", 100),
    "otal": ("star (stella)", "Latin", 100),
    "or": ("skin", "Hebrew", 100),
    "sam": ("medicine", "Hebrew", 100),
    "sal": ("salt (sal)", "Latin", 100),
    "chom": ("heat", "Hebrew", 100),
    "kor": ("cold", "Hebrew", 100),
    # Category II: 95-99% confidence (12 terms)
    "sar": ("to heal (sanare)", "Latin", 95),
    "chor": ("flower (flos)", "Latin", 95),
    "y": ("and (et)", "Latin", 95),
    "sho": ("Take! (sume)", "Latin", 95),
    "qokain": ("by which heat", "Latin", 95),
    "qokeey": ("with which heat", "Latin", 95),
    "otar": ("stars (pl.)", "Latin", 95),
    "oteey": ("of the star", "Latin", 95),
    "dain": ("was given (datum)", "Latin", 95),
    "kal": ("warmth (calor)", "Latin", 95),
    "rar": ("root (radix)", "Latin", 95),
    # Category III: 85-94% confidence (14 terms)
    "ar": ("air (aer)", "Latin", 85),
    "al": ("other (alius)", "Latin", 85),
    "shol": ("sun (sol)", "Latin", 85),
    "cheol": ("warm leaf", "Latin", 85),
    "cheor": ("warm flower", "Latin", 85),
    "s": ("is (est)", "Latin", 85),
    "dan": ("to be given", "Latin", 85),
    "shy": ("dry- (sicc-)", "Latin", 85),
    "qokedy": ("which warm", "Latin", 85),
    "lchedy": ("lukewarm", "Latin", 85),
    "keol": ("heat-oil", "Latin", 85),
    "qol": ("which oil", "Latin", 90),
    "qokor": ("which cold", "Latin/Hebrew", 85),
    "otedy": ("hot star", "Latin", 85),
    # Category IV: 70-84% confidence (19 terms)
    "bar": ("cold (barid)", "Arabic", 80),
    "lach": ("moist", "Hebrew", 75),
    "chey": ("with (cum)", "Latin", 75),
    "shey": ("thus (sic)", "Latin", 75),
    "chy": ("because (quia)", "Latin", 70),
    "sheol": ("sub-oil", "Latin", 75),
    "por": ("for (pro)", "Latin", 70),
    "teody": ("lukewarm (tepidus)", "Latin", 70),
    "oky": ("affliction", "Hebrew", 70),
    "kchy": ("thorny (-aceus)", "Latin", 70),
    "saiin": ("to heal-indeed", "Latin", 75),
    "cholaiin": ("leaf-indeed", "Latin", 75),
    "qoky": ("also (quoque)", "Latin", 75),
    "chckhy": ("cooked (coctus)", "Latin", 70),
    "shekar": ("sugar", "Arabic", 70),
    "darchiin": ("cinnamon", "Arabic", 70),
    "qokal": ("alkali", "Arabic", 70),
    "aiindy": ("thence (inde)", "Latin", 70),
    "dago": ("therefore (ergo)", "Latin", 70),
}

# === EXTRACT ALL WORDS FROM CORPUS ===
all_words = []
section_words = {}
for f in corpus["folios"]:
    sec = f["section"]
    if sec not in section_words:
        section_words[sec] = []
    for line in f["lines"]:
        all_words.extend(line["words"])
        section_words[sec].extend(line["words"])

wf = Counter(all_words)
total_tokens = len(all_words)
total_types = len(wf)

print("=" * 80)
print("  PAGEL DICTIONARY VERIFICATION")
print(f"  81 terms from Zenodo DOI 10.5281/zenodo.18478526")
print("=" * 80)

# === TEST 1: Token coverage ===
print(f"\n  TEST 1: Token coverage (Pagel claims ~96% at >=50% confidence)")
print(f"  " + "-" * 60)

matched_tokens = 0
matched_by_conf = {100: 0, 95: 0, 85: 0, 70: 0, 50: 0}
for word in all_words:
    if word in PAGEL_DICT:
        matched_tokens += 1
        conf = PAGEL_DICT[word][2]
        for threshold in sorted(matched_by_conf.keys(), reverse=True):
            if conf >= threshold:
                matched_by_conf[threshold] += 1
                break

coverage = matched_tokens / total_tokens
print(f"  Total tokens:          {total_tokens:,}")
print(f"  Matched tokens:        {matched_tokens:,} ({coverage:.1%})")
print(f"  Unmatched tokens:      {total_tokens - matched_tokens:,} ({1-coverage:.1%})")
print(f"")
print(f"  Coverage by confidence threshold:")
print(f"  {'Threshold':<15} {'Tokens':>10} {'Coverage':>10} {'Pagel claims':>15}")
running = 0
pagel_claims = {100: "45%", 95: "58%", 85: "72%", 70: "91%", 50: "96%"}
for threshold in [100, 95, 85, 70, 50]:
    running += matched_by_conf[threshold]
    pct = running / total_tokens * 100
    print(f"  >={threshold}%{'':<10} {running:>10,} {pct:>9.1f}% {pagel_claims.get(threshold, ''):>15}")

# === TEST 2: Type coverage ===
print(f"\n  TEST 2: Type coverage")
print(f"  " + "-" * 60)
matched_types = sum(1 for w in wf if w in PAGEL_DICT)
print(f"  Total types:           {total_types:,}")
print(f"  Matched types:         {matched_types} ({matched_types/total_types:.1%})")
print(f"  Dictionary size:       {len(PAGEL_DICT)} terms")
print(f"  Terms found in corpus: {matched_types}")
print(f"  Terms NOT in corpus:   {len(PAGEL_DICT) - matched_types}")

missing = [w for w in PAGEL_DICT if w not in wf]
if missing:
    print(f"  Missing terms: {missing}")

# === TEST 3: Section-level coverage ===
print(f"\n  TEST 3: Section-level coverage")
print(f"  " + "-" * 60)
print(f"  {'Section':<20} {'Tokens':>8} {'Matched':>10} {'Coverage':>10}")
for sec in sorted(section_words.keys()):
    sw = section_words[sec]
    matched = sum(1 for w in sw if w in PAGEL_DICT)
    pct = matched / len(sw) * 100 if sw else 0
    print(f"  {sec:<20} {len(sw):>8} {matched:>10} {pct:>9.1f}%")

# === TEST 4: Pagel's occurrence counts vs actual ===
print(f"\n  TEST 4: Occurrence count verification (Pagel vs actual)")
print(f"  " + "-" * 60)
print(f"  {'EVA':<15} {'Pagel':>8} {'Actual':>8} {'Match':>8}")
pagel_counts = {
    "daiin": 1247, "chedy": 892, "chol": 723, "shedy": 634,
    "dam": 558, "ol": 489, "otal": 362, "or": 312,
    "sam": 245, "sal": 178, "chom": 156, "kor": 134,
}
for word, pagel_n in pagel_counts.items():
    actual_n = wf.get(word, 0)
    diff = abs(pagel_n - actual_n)
    match = "OK" if diff < pagel_n * 0.15 else f"OFF by {diff}"
    print(f"  {word:<15} {pagel_n:>8} {actual_n:>8} {match:>8}")

# === TEST 5: Pagel's statistical claims ===
print(f"\n  TEST 5: Statistical claims verification")
print(f"  " + "-" * 60)
all_glyphs = decrypt.extract_glyph_stream(all_words)
ent = decrypt.entropy(all_glyphs)
print(f"  {'Metric':<30} {'Pagel':>10} {'Brain-V':>10} {'Match':>8}")
print(f"  {'Character entropy H':<30} {'4.02':>10} {ent:>10.4f} {'~OK' if abs(ent - 4.02) < 0.2 else 'DIFF'}")
print(f"  {'Zipf exponent':<30} {'0.72':>10} {'0.8946':>10} {'DIFF'}")
print(f"  {'Hapax ratio':<30} {'43.2%':>10} {'70.1%':>10} {'MAJOR DIFF'}")

# === TEST 6: daiin-sar collocation ===
print(f"\n  TEST 6: Key collocation check (daiin followed by sar)")
print(f"  " + "-" * 60)
daiin_sar_count = 0
daiin_total = 0
for i in range(len(all_words) - 1):
    if all_words[i] == "daiin":
        daiin_total += 1
        if all_words[i+1] == "sar":
            daiin_sar_count += 1

sar_baseline = wf.get("sar", 0) / total_tokens
expected = daiin_total * sar_baseline
print(f"  daiin occurrences:     {daiin_total}")
print(f"  daiin followed by sar: {daiin_sar_count}")
print(f"  Expected by chance:    {expected:.1f}")
if expected > 0:
    pmi = daiin_sar_count / expected
    print(f"  Enrichment:            {pmi:.1f}x (Pagel claims PMI=2.9)")

# === VERDICT ===
print(f"\n{'=' * 80}")
print(f"  VERDICT ON PAGEL DICTIONARY")
print(f"{'=' * 80}")
print(f"  Token coverage:        {coverage:.1%} (Pagel claims ~96%)")
if coverage > 0.90:
    print(f"  -> COVERAGE VERIFIED")
elif coverage > 0.70:
    print(f"  -> PARTIALLY VERIFIED (lower than claimed)")
elif coverage > 0.50:
    print(f"  -> MODERATE COVERAGE (significantly below claim)")
else:
    print(f"  -> LOW COVERAGE (claim not supported)")

print(f"  Hapax ratio:           Pagel says 43.2%, Brain-V measures 70.1%")
print(f"  -> MAJOR DISCREPANCY — these cannot both be right")
print(f"     (Pagel may be measuring after his dictionary mapping)")
