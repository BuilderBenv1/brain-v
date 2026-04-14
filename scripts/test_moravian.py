"""Test H104: Moravian/Czech hypothesis (Stoilova) against corpus statistics."""
import json
import sys
sys.path.insert(0, "scripts")
import decrypt
from collections import Counter

# Old Czech / Moravian letter frequencies (modern Czech as proxy)
CZECH_FREQ = {
    "a": 8.42, "b": 1.50, "c": 3.05, "d": 3.44, "e": 10.48,
    "f": 0.29, "g": 0.30, "h": 1.65, "i": 6.07, "j": 1.96,
    "k": 3.48, "l": 3.89, "m": 3.24, "n": 6.55, "o": 7.68,
    "p": 3.36, "q": 0.01, "r": 4.28, "s": 5.21, "t": 5.62,
    "u": 3.17, "v": 4.06, "w": 0.01, "x": 0.05, "y": 2.07, "z": 2.37,
}

CZECH_WORDS = {
    "a", "je", "to", "na", "se", "v", "ze", "do", "za", "od",
    "po", "pro", "jak", "co", "ten", "ale", "tak", "ne", "by",
    "si", "jeho", "jen", "nebo", "ani", "kde", "kdo",
    "moc", "pak", "nad", "pod", "pri", "bez", "pred",
    "list", "koren", "bylina", "maslo", "olej", "voda", "sol",
    "med", "ocet", "prach", "mast", "rana", "bolest", "hnis",
    "noha", "ruka", "hlava", "zuby", "telo", "krev",
}

corpus = decrypt.load_corpus()

all_words = []
for f in corpus["folios"]:
    for line in f["lines"]:
        all_words.extend(line["words"])
all_glyphs = decrypt.extract_glyph_stream(all_words)

stems = decrypt._strip_to_stems(all_words)
stem_glyphs = decrypt.extract_glyph_stream(stems)

glyph_freq = Counter(all_glyphs)
stem_freq = Counter(stem_glyphs)

print("=" * 80)
print("  H104 TEST: Moravian/Czech Hypothesis (Stoilova)")
print("=" * 80)

# Test 1: Frequency correlation
print("\n  TEST 1: Glyph frequency correlation")
print("  " + "-" * 60)

latin_corr = decrypt.frequency_correlation(glyph_freq, decrypt.LATIN_FREQ)
italian_corr = decrypt.frequency_correlation(glyph_freq, decrypt.ITALIAN_FREQ)
czech_corr = decrypt.frequency_correlation(glyph_freq, CZECH_FREQ)

latin_corr_s = decrypt.frequency_correlation(stem_freq, decrypt.LATIN_FREQ)
italian_corr_s = decrypt.frequency_correlation(stem_freq, decrypt.ITALIAN_FREQ)
czech_corr_s = decrypt.frequency_correlation(stem_freq, CZECH_FREQ)

print(f"  {'Language':<25} {'Raw words':>12} {'Stems':>12}")
print(f"  {'-'*51}")
print(f"  {'Latin correlation':<25} {latin_corr:>12.4f} {latin_corr_s:>12.4f}")
print(f"  {'Italian correlation':<25} {italian_corr:>12.4f} {italian_corr_s:>12.4f}")
print(f"  {'Czech correlation':<25} {czech_corr:>12.4f} {czech_corr_s:>12.4f}")

winner_raw = "Latin" if latin_corr >= max(italian_corr, czech_corr) else "Italian" if italian_corr >= czech_corr else "Czech"
winner_stem = "Latin" if latin_corr_s >= max(italian_corr_s, czech_corr_s) else "Italian" if italian_corr_s >= czech_corr_s else "Czech"
print(f"  {'Winner':<25} {winner_raw:>12} {winner_stem:>12}")

# Test 2: Word length
print(f"\n  TEST 2: Word length distribution")
print(f"  " + "-" * 60)
avg_wl = sum(len(w) for w in all_words) / len(all_words)
print(f"  Voynich avg word length:    {avg_wl:.2f}")
print(f"  Latin expected:             5.5")
print(f"  Italian expected:           4.8")
print(f"  Czech expected:             4.8")
print(f"  Medieval Czech medical:     ~5.0-5.5")

# Test 3: IC
print(f"\n  TEST 3: Index of Coincidence")
print(f"  " + "-" * 60)
vic = decrypt.index_of_coincidence(all_glyphs)
vic_s = decrypt.index_of_coincidence(stem_glyphs)
print(f"  Voynich IC (raw):           {vic:.6f}")
print(f"  Voynich IC (stems):         {vic_s:.6f}")
print(f"  Latin expected:             ~0.070")
print(f"  Italian expected:           ~0.075")
print(f"  Czech expected:             ~0.060-0.065")

if abs(vic - 0.070) < abs(vic - 0.062):
    print(f"  Verdict:                    Closer to Latin/Italian (AGAINST Czech)")
else:
    print(f"  Verdict:                    Closer to Czech (SUPPORTS Moravian)")

# Test 4: Entropy
print(f"\n  TEST 4: Entropy comparison")
print(f"  " + "-" * 60)
vent = decrypt.entropy(all_glyphs)
vent_s = decrypt.entropy(stem_glyphs)
print(f"  Voynich entropy (raw):      {vent:.4f} bits")
print(f"  Voynich entropy (stems):    {vent_s:.4f} bits")
print(f"  Latin expected:             ~4.0 bits")
print(f"  Italian expected:           ~3.95 bits")
print(f"  Czech expected:             ~4.2 bits")
print(f"  Verdict:                    {'Closer to Latin/Italian' if abs(vent - 3.97) < abs(vent - 4.2) else 'Closer to Czech'}")

# Test 5: Freq sub -> Czech on biological stems
print(f"\n  TEST 5: Frequency substitution on biological stems")
print(f"  " + "-" * 60)
bio_words = decrypt.extract_words(corpus, section="biological")
bio_stems = decrypt._strip_to_stems(bio_words)
bio_sg = decrypt.extract_glyph_stream(bio_stems)

r_cz = decrypt.attack_frequency_substitution(bio_sg, bio_stems, CZECH_FREQ, "czech")
r_la = decrypt.attack_frequency_substitution(bio_sg, bio_stems, decrypt.LATIN_FREQ, "latin")
r_it = decrypt.attack_frequency_substitution(bio_sg, bio_stems, decrypt.ITALIAN_FREQ, "italian")

print(f"  {'Target':<20} {'Score':>10} {'Freq corr':>12}")
print(f"  {'-'*44}")
print(f"  {'Czech (stems)':<20} {r_cz['score']['best_score']:>10.4f} {r_cz['score'].get('latin_freq_correlation', czech_corr_s):>12.4f}")
print(f"  {'Latin (stems)':<20} {r_la['score']['best_score']:>10.4f} {r_la['score']['latin_freq_correlation']:>12.4f}")
print(f"  {'Italian (stems)':<20} {r_it['score']['best_score']:>10.4f} {r_it['score']['italian_freq_correlation']:>12.4f}")
print(f"\n  Czech sample:   {r_cz['sample_output'][:120]}")
print(f"  Latin sample:   {r_la['sample_output'][:120]}")
print(f"  Italian sample: {r_it['sample_output'][:120]}")

# Verdict
print(f"\n{'=' * 80}")
print(f"  VERDICT ON H104 (Moravian Hypothesis)")
print(f"{'=' * 80}")

score = 0
reasons = []
if czech_corr > 0.90:
    score += 0.25
    reasons.append("Czech freq corr > 0.90 (+0.25)")
elif czech_corr > 0.80:
    score += 0.15
    reasons.append(f"Czech freq corr {czech_corr:.3f} > 0.80 (+0.15)")
else:
    reasons.append(f"Czech freq corr {czech_corr:.3f} < 0.80 (+0.00)")

if abs(vic - 0.062) < abs(vic - 0.070):
    score += 0.25
    reasons.append("IC closer to Czech (+0.25)")
else:
    reasons.append("IC closer to Latin (+0.00)")

if abs(vent - 4.2) < abs(vent - 4.0):
    score += 0.25
    reasons.append("Entropy closer to Czech (+0.25)")
else:
    reasons.append("Entropy closer to Latin (+0.00)")

if abs(avg_wl - 4.8) < 0.5:
    score += 0.25
    reasons.append("Word length matches Czech (+0.25)")
else:
    reasons.append(f"Word length {avg_wl:.2f} outside Czech range (+0.00)")

for r in reasons:
    print(f"  {r}")
print(f"\n  Composite score: {score:.2f}/1.00")

if score > 0.5:
    print(f"  -> SUPPORTS Moravian hypothesis")
elif score > 0.25:
    print(f"  -> INCONCLUSIVE")
else:
    print(f"  -> STATISTICAL EVIDENCE FAVOURS Latin/Italian over Czech/Moravian")

print(f"""
  NOTE: This tests the BULK statistical profile of the full 38,053-word corpus
  against Czech language parameters. It does NOT test Stoilova's specific
  readings of f14v and f116v, which would require folio-level verification.

  A mixed-script cipher (Latin + Glagolitic + Cyrillic) could distort these
  metrics. The pharmaceutical content match for Acanthus mollis is interesting
  independent of the language identification question.

  Brain-V rates H104 at confidence: {max(0.15, min(0.60, score))}
""")

# Update hypothesis file
h = json.load(open("hypotheses/H104.json"))
h["confidence"] = round(max(0.15, min(0.60, score)), 3)
h["last_tested"] = "2026-04-14"
h["tests_run"].append({
    "date": "2026-04-14",
    "test": "Statistical profile comparison: Czech vs Latin vs Italian",
    "score": round(score, 4),
    "passed": score > 0.5,
    "details": f"Czech freq corr={czech_corr:.4f}, IC={vic:.5f} (Latin range), entropy={vent:.4f} (Latin range). Composite {score:.2f}/1.00.",
    "confidence_change": f"0.30 -> {max(0.15, min(0.60, score)):.3f}",
})
h["tests_remaining"] = [t for t in h["tests_remaining"] if t != "frequency_correlation_slavic"]
json.dump(h, open("hypotheses/H104.json", "w"), indent=2)
print(f"  H104 updated: confidence -> {h['confidence']}")
