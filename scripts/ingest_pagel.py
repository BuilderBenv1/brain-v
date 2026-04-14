"""Ingest kpagel's trilingual pharmaceutical hypotheses and run initial tests."""
import json
import sys
sys.path.insert(0, "scripts")
import decrypt
from collections import Counter

corpus = decrypt.load_corpus()

# === CREATE HYPOTHESES ===

hypotheses = [
    {
        "id": "H106",
        "claim": "The Voynich Manuscript is a trilingual pharmaceutical compendium encoding plant-based medicine in a mixed Latin/Greek/Arabic scribal system, with a 168-term dictionary covering ~80% of the text.",
        "type": "language",
        "confidence": 0.35,
        "evidence_for": [
            "Pagel (2025): 168-term dictionary on Zenodo (DOI 10.5281/zenodo.18478526)",
            "Claims 80% text coverage — far exceeds Brain-V best codebook (50.8%)",
            "Pharmaceutical context aligns with Brain-V biological section findings",
            "Brain-V independently identified medical context from statistics"
        ],
        "evidence_against": [
            "80% coverage needs independent verification against EVA corpus",
            "Brain-V universal cipher transfer shows ONE table — trilingual would show variation",
            "IC 0.077 consistent with single-language monoalphabetic, not multilingual",
            "168 terms covering 80% implies extremely repetitive text"
        ],
        "test": "Verify 80% coverage: count tokens matching 168-term dictionary across corpus",
        "test_metric": "dictionary_coverage",
        "test_threshold": ">70% tokens: strong support. <50%: overclaimed.",
        "tests_run": [],
        "tests_remaining": ["dictionary_coverage_verification", "section_uniformity"],
        "status": "active",
        "parent": None,
        "created": "2026-04-14",
        "last_tested": None,
        "reasoning": "Most concrete decipherment claim received — 168 specific mappings with DOI. If 80% coverage verifies, major lead.",
        "source": "Pagel, K. (2025) Zenodo DOI 10.5281/zenodo.18478526; voynich.net",
        "researcher": "kpagel"
    },
    {
        "id": "H107",
        "claim": "74.4% of Voynich plant illustrations match Mediterranean species at >=80% confidence: 100% Mediterranean flora, 0% New World. Plant families: Lamiaceae 33%, Asteraceae 22%, Solanaceae 21%, consistent with Dioscorides pharmaceutical tradition.",
        "type": "structural",
        "confidence": 0.40,
        "evidence_for": [
            "Pagel: systematic botanical ID with confidence scores",
            "100% Mediterranean eliminates New World hypotheses (FA013)",
            "Lamiaceae/Asteraceae/Solanaceae dominate medieval Mediterranean herbals",
            "Compatible with Brain-V dating (c.1404-1438) and European provenance"
        ],
        "evidence_against": [
            "Plant ID from stylised medieval illustrations is inherently subjective",
            "Previous IDs (Tucker & Talbert 2013) reached different conclusions",
            "26% unidentified — large uncertainty margin"
        ],
        "test": "Cross-reference plant IDs with independent botanical analyses",
        "test_metric": "botanical_cross_reference",
        "test_threshold": ">60% agreement with independent analyses",
        "tests_run": [],
        "tests_remaining": ["botanical_cross_reference"],
        "status": "active",
        "parent": None,
        "created": "2026-04-14",
        "last_tested": None,
        "reasoning": "Botanical claim is partially independent of decipherment — verifiable visually. If confirmed, strongly constrains provenance.",
        "source": "Pagel, K. (2025) Zenodo DOI 10.5281/zenodo.18478526",
        "researcher": "kpagel"
    },
    {
        "id": "H108",
        "claim": "The word 'daiin' (799 occurrences, rank 1) decomposes as 'da' (give) + 'in' (in water), a pharmaceutical instruction appearing after plant-part descriptions. This morphological decomposition is systematic across the corpus.",
        "type": "cipher",
        "confidence": 0.30,
        "evidence_for": [
            "Pagel: daiin = da + in pharmaceutical instruction",
            "daiin is most frequent word (799x) — frequent instruction expected",
            "Brain-V found 'aiin'/'ain' as systematic suffixes — compatible",
            "Brain-V found da-stem family (dal, dar, dain, daiin)",
            "Latin 'da in aqua' is standard medieval pharmaceutical format"
        ],
        "evidence_against": [
            "da+in decomposition is post-hoc — many decompositions possible",
            "Brain-V suffix analysis treats 'aiin' as suffix, making stem 'd' not 'da'",
            "If daiin = 'give in water', should cluster in pharma sections",
            "'aiin' alone (506x, rank 3) needs separate explanation"
        ],
        "test": "Test daiin section distribution: is it more frequent in pharmaceutical/recipe vs zodiac?",
        "test_metric": "positional_distribution",
        "test_threshold": "daiin >2x more frequent in pharma vs zodiac supports",
        "tests_run": [],
        "tests_remaining": ["daiin_section_distribution", "daiin_positional_context"],
        "status": "active",
        "parent": None,
        "created": "2026-04-14",
        "last_tested": None,
        "reasoning": "Most testable claim. daiin distribution across sections measurable immediately.",
        "source": "Pagel, K. (2025) Zenodo DOI 10.5281/zenodo.18478526",
        "researcher": "kpagel"
    },
    {
        "id": "H109",
        "claim": "Jaccard Index between Voynich vocabulary and proposed decipherment vocabulary is J~0.08, independently confirmed. Low but non-zero overlap indicates partial but real linguistic correspondence.",
        "type": "structural",
        "confidence": 0.30,
        "evidence_for": [
            "Pagel: J~0.08, independently confirmed",
            "Non-zero Jaccard exceeds random expectation",
            "J=0.08 is honest — not overclaiming"
        ],
        "evidence_against": [
            "J=0.08 is very low (92% non-overlap)",
            "Need random baseline comparison",
            "Independent confirmation details unspecified"
        ],
        "test": "Compute Jaccard against Pagel dictionary and random baselines",
        "test_metric": "jaccard_index",
        "test_threshold": "J(Pagel) > 2x J(random) supports",
        "tests_run": [],
        "tests_remaining": ["jaccard_verification"],
        "status": "active",
        "parent": None,
        "created": "2026-04-14",
        "last_tested": None,
        "reasoning": "Directly verifiable if 168-term dictionary is available.",
        "source": "Pagel, K. (2025) Zenodo DOI 10.5281/zenodo.18478526",
        "researcher": "kpagel"
    },
]

for h in hypotheses:
    path = f"hypotheses/{h['id']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(h, f, indent=2)
    print(f"Saved {h['id']}: {h['claim'][:80]}...")

# === RUN TESTABLE CLAIMS ===

print("\n" + "=" * 80)
print("  TESTING H108: daiin section distribution")
print("=" * 80)

sections = ["text-only", "herbal", "recipes", "biological",
            "pharmaceutical", "cosmological", "zodiac", "astronomical"]

print(f"\n  {'Section':<20} {'Words':>8} {'daiin':>8} {'Rate':>10} {'aiin':>8} {'Rate':>10}")
print(f"  {'-'*66}")

daiin_rates = {}
for sec in sections:
    sw = decrypt.extract_words(corpus, section=sec)
    if not sw:
        continue
    total = len(sw)
    daiin_count = sum(1 for w in sw if w == "daiin")
    aiin_count = sum(1 for w in sw if w == "aiin")
    rate = daiin_count / total * 1000  # per 1000 words
    aiin_rate = aiin_count / total * 1000
    daiin_rates[sec] = rate
    print(f"  {sec:<20} {total:>8} {daiin_count:>8} {rate:>9.2f}x {aiin_count:>8} {aiin_rate:>9.2f}x")

# Check if pharmaceutical sections have higher daiin rates
pharma_secs = ["pharmaceutical", "recipes", "herbal"]
non_pharma = ["zodiac", "astronomical", "cosmological"]

pharma_rate = sum(daiin_rates.get(s, 0) for s in pharma_secs) / len(pharma_secs)
non_pharma_rate = sum(daiin_rates.get(s, 0) for s in non_pharma if s in daiin_rates) / max(1, sum(1 for s in non_pharma if s in daiin_rates))

print(f"\n  Pharma-adjacent sections avg rate:   {pharma_rate:.2f} per 1000 words")
print(f"  Non-pharma sections avg rate:         {non_pharma_rate:.2f} per 1000 words")
ratio = pharma_rate / non_pharma_rate if non_pharma_rate > 0 else float('inf')
print(f"  Ratio:                                {ratio:.2f}x")
print(f"  Threshold (>2x):                      {'PASS' if ratio > 2 else 'FAIL'}")

# Update H108
h108 = json.load(open("hypotheses/H108.json"))
passed = ratio > 2.0
h108["confidence"] = round(0.45 if passed else 0.25, 3)
h108["last_tested"] = "2026-04-14"
h108["tests_run"].append({
    "date": "2026-04-14",
    "test": "daiin section distribution analysis",
    "score": round(min(1.0, ratio / 4), 4),
    "passed": passed,
    "details": f"Pharma sections: {pharma_rate:.2f}/1000, non-pharma: {non_pharma_rate:.2f}/1000, ratio: {ratio:.2f}x. Threshold >2x: {'PASS' if passed else 'FAIL'}.",
    "confidence_change": f"0.30 -> {h108['confidence']}",
})
h108["tests_remaining"] = [t for t in h108["tests_remaining"] if t != "daiin_section_distribution"]
json.dump(h108, open("hypotheses/H108.json", "w"), indent=2)
print(f"\n  H108 updated: confidence -> {h108['confidence']}")

# === Test da- stem family ===
print("\n" + "=" * 80)
print("  TESTING: da- stem family analysis")
print("=" * 80)

all_words_flat = []
for fo in corpus["folios"]:
    for line in fo["lines"]:
        all_words_flat.extend(line["words"])

wf = Counter(all_words_flat)
da_family = {w: c for w, c in wf.items() if w.startswith("da")}
da_sorted = sorted(da_family.items(), key=lambda x: -x[1])

print(f"\n  da- stem family ({len(da_family)} members, {sum(da_family.values())} total tokens):")
for w, c in da_sorted[:20]:
    print(f"    {w:<15} x{c}")

# Check if Brain-V's suffix model explains the da- family
print(f"\n  Suffix decomposition of da- family:")
suffixes_found = Counter()
for w, c in da_sorted[:20]:
    stem = w
    if len(w) > 2:
        for suf in ["aiin", "ain", "air", "iin", "in", "dy", "ey", "ar", "or", "al", "an", "y", "n", "l", "r"]:
            if w.endswith(suf) and len(w) > len(suf) + 1:
                stem = w[:-len(suf)]
                suffixes_found[suf] += c
                print(f"    {w:<15} = {stem} + {suf} (x{c})")
                break
        else:
            print(f"    {w:<15} = {w} [no suffix match] (x{c})")

print(f"\n  Most common suffixes in da- family:")
for suf, c in suffixes_found.most_common(10):
    print(f"    -{suf:<10} x{c}")

print(f"\n  Pagel's decomposition: daiin = da + iin (give + in water)")
print(f"  Brain-V decomposition: daiin = d + aiin (stem d + suffix aiin)")
print(f"  Both are structurally valid. The question is whether 'da' or 'd' is the root.")
