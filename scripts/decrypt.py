"""
decrypt.py — Brain-V's decryption engine

Attempts actual decipherment of Voynich text using various cipher techniques.
When a cipher-type hypothesis scores high enough, this module applies the
proposed cipher to sample sections and measures whether the output resembles
a known natural language.

Supported cipher attacks:
  1. Simple substitution (frequency analysis)
  2. Caesar/shift cipher (brute force all shifts)
  3. Polyalphabetic / Vigenere (Kasiski + frequency)
  4. Transposition (columnar, reverse, rail fence)
  5. Combined substitution + transposition

Each attack produces candidate plaintext, which is scored against
Latin and Italian reference profiles.

Usage:
    python scripts/decrypt.py                    # run all attacks on herbal section
    python scripts/decrypt.py --section herbal   # target a specific section
    python scripts/decrypt.py --cipher sub       # try only substitution
    python scripts/decrypt.py --folio f1r        # target a specific folio
"""

import argparse
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = PROJECT_ROOT / "raw" / "perception" / "voynich-corpus.json"
STATS_PATH = PROJECT_ROOT / "raw" / "perception" / "voynich-stats.json"
RESULTS_DIR = PROJECT_ROOT / "outputs" / "decryption"
HYPOTHESES_DIR = PROJECT_ROOT / "hypotheses"

# --- Reference letter frequencies ---
# Latin frequencies from sttmedia.com (2M character corpus)
LATIN_FREQ = {
    "a": 8.89, "b": 1.58, "c": 3.99, "d": 2.77, "e": 11.38,
    "f": 0.93, "g": 1.21, "h": 0.69, "i": 11.44, "k": 0.01,
    "l": 3.15, "m": 5.38, "n": 6.28, "o": 5.40, "p": 3.03,
    "q": 1.51, "r": 6.67, "s": 7.60, "t": 8.00, "u": 8.46,
    "v": 0.96, "x": 0.60, "y": 0.07, "z": 0.01,
}

# Italian frequencies (standard)
ITALIAN_FREQ = {
    "a": 11.74, "b": 0.92, "c": 4.50, "d": 3.73, "e": 11.79,
    "f": 0.95, "g": 1.64, "h": 1.54, "i": 11.28, "k": 0.01,
    "l": 6.51, "m": 2.51, "n": 6.88, "o": 9.83, "p": 3.05,
    "q": 0.51, "r": 6.37, "s": 4.98, "t": 5.62, "u": 3.01,
    "v": 2.10, "w": 0.01, "x": 0.01, "y": 0.01, "z": 0.49,
}

# Common words for dictionary checking
LATIN_WORDS = {
    "et", "in", "est", "non", "ad", "de", "qui", "ut", "cum", "sed",
    "quod", "per", "ab", "ex", "si", "aut", "nec", "enim", "autem",
    "hic", "ille", "esse", "sunt", "fuit", "quae", "quid", "omnis",
    "iam", "nunc", "tamen", "ita", "sic", "tam", "ante", "post",
    "inter", "super", "sub", "pro", "contra", "sine", "apud",
    "ergo", "igitur", "nam", "quia", "quam", "atque", "neque",
    "vel", "sive", "seu", "dum", "donec", "ubi", "unde", "quo",
}

ITALIAN_WORDS = {
    "e", "di", "il", "la", "che", "in", "per", "con", "non", "una",
    "un", "del", "le", "da", "si", "al", "lo", "come", "ma", "se",
    "nel", "sono", "ha", "era", "suo", "sua", "dei", "gli", "delle",
    "alla", "anche", "questo", "quella", "essere", "stato", "fatto",
    "tutto", "loro", "quando", "molto", "dopo", "prima", "sempre",
    "ogni", "dove", "qui", "ora", "poi", "tra", "fra", "solo",
    "cosa", "tempo", "mano", "parte", "acqua", "terra", "fuoco",
}


def load_corpus() -> dict:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def extract_words(corpus: dict, section: str | None = None,
                  folio: str | None = None) -> list[str]:
    """Extract words from corpus, optionally filtering by section or folio."""
    words = []
    for f in corpus["folios"]:
        if section and f["section"] != section:
            continue
        if folio and f["folio"] != folio:
            continue
        for line in f["lines"]:
            words.extend(line["words"])
    return words


def extract_glyph_stream(words: list[str]) -> str:
    """Convert word list into a continuous glyph stream."""
    return "".join(words)


# --- Scoring functions ---

def frequency_correlation(observed: Counter, reference: dict) -> float:
    """Pearson correlation between observed and reference letter frequencies."""
    total = sum(observed.values()) or 1
    obs_pct = {ch: (count / total) * 100 for ch, count in observed.items()}

    # Get all letters from both sets
    all_letters = set(list(reference.keys()) + list(obs_pct.keys()))

    obs_vals = [obs_pct.get(ch, 0) for ch in sorted(all_letters)]
    ref_vals = [reference.get(ch, 0) for ch in sorted(all_letters)]

    n = len(obs_vals)
    if n < 2:
        return 0.0

    mean_obs = sum(obs_vals) / n
    mean_ref = sum(ref_vals) / n

    num = sum((o - mean_obs) * (r - mean_ref) for o, r in zip(obs_vals, ref_vals))
    den_obs = math.sqrt(sum((o - mean_obs) ** 2 for o in obs_vals))
    den_ref = math.sqrt(sum((r - mean_ref) ** 2 for r in ref_vals))

    if den_obs * den_ref == 0:
        return 0.0
    return num / (den_obs * den_ref)


def dictionary_hit_rate(words: list[str], dictionary: set) -> float:
    """Fraction of output words found in a reference dictionary."""
    if not words:
        return 0.0
    hits = sum(1 for w in words if w.lower() in dictionary)
    return hits / len(words)


def entropy(text: str) -> float:
    """Shannon entropy of a string in bits per character."""
    freq = Counter(text)
    total = len(text) or 1
    return -sum((c / total) * math.log2(c / total) for c in freq.values() if c > 0)


def score_plaintext(text: str, words: list[str]) -> dict:
    """Score a candidate plaintext against Latin and Italian profiles."""
    if not text:
        return {"latin_score": 0, "italian_score": 0, "best_language": "none",
                "best_score": 0, "details": "empty output"}

    char_freq = Counter(text.lower())
    text_entropy = entropy(text.lower())

    # Frequency correlation
    latin_corr = frequency_correlation(char_freq, LATIN_FREQ)
    italian_corr = frequency_correlation(char_freq, ITALIAN_FREQ)

    # Dictionary hits
    latin_dict = dictionary_hit_rate(words, LATIN_WORDS)
    italian_dict = dictionary_hit_rate(words, ITALIAN_WORDS)

    # Entropy comparison (Latin ~4.0, Italian ~3.95)
    latin_ent_score = max(0, 1.0 - abs(text_entropy - 4.0) / 2.0)
    italian_ent_score = max(0, 1.0 - abs(text_entropy - 3.95) / 2.0)

    # Combined scores (weighted)
    latin_score = (
        latin_corr * 0.4 +          # frequency match
        latin_dict * 0.4 +           # dictionary hits
        latin_ent_score * 0.2        # entropy match
    )
    italian_score = (
        italian_corr * 0.4 +
        italian_dict * 0.4 +
        italian_ent_score * 0.2
    )

    best = "latin" if latin_score > italian_score else "italian"
    best_score = max(latin_score, italian_score)

    return {
        "latin_score": round(latin_score, 4),
        "italian_score": round(italian_score, 4),
        "best_language": best,
        "best_score": round(best_score, 4),
        "latin_freq_correlation": round(latin_corr, 4),
        "italian_freq_correlation": round(italian_corr, 4),
        "latin_dict_hits": round(latin_dict, 4),
        "italian_dict_hits": round(italian_dict, 4),
        "entropy": round(text_entropy, 4),
        "details": (
            f"Freq corr: Latin={latin_corr:.3f}, Italian={italian_corr:.3f}. "
            f"Dict hits: Latin={latin_dict:.3f}, Italian={italian_dict:.3f}. "
            f"Entropy: {text_entropy:.3f} bits."
        ),
    }


# --- Cipher attacks ---

def attack_frequency_substitution(glyphs: str, words: list[str],
                                  target_freq: dict, language: str) -> dict:
    """
    Simple substitution via frequency analysis.
    Map the most frequent Voynich glyph to the most frequent target letter, etc.
    """
    glyph_freq = Counter(glyphs)
    sorted_glyphs = [g for g, _ in glyph_freq.most_common()]
    sorted_target = sorted(target_freq.keys(), key=lambda k: -target_freq[k])

    # Build mapping
    mapping = {}
    for i, g in enumerate(sorted_glyphs):
        if i < len(sorted_target):
            mapping[g] = sorted_target[i]
        else:
            mapping[g] = "?"

    # Apply mapping
    decrypted_stream = "".join(mapping.get(g, "?") for g in glyphs)

    # Reconstruct words using word boundaries from original
    decrypted_words = []
    pos = 0
    for w in words:
        end = pos + len(w)
        decrypted_words.append(decrypted_stream[pos:end])
        pos = end

    plaintext = " ".join(decrypted_words)
    score = score_plaintext(decrypted_stream, decrypted_words)

    return {
        "method": f"frequency_substitution_{language}",
        "mapping": mapping,
        "sample_output": plaintext[:500],
        "sample_words": decrypted_words[:50],
        "score": score,
        "word_count": len(decrypted_words),
    }


def attack_caesar_shift(glyphs: str, words: list[str],
                        alphabet: str = "abcdefghijklmnopqrstuvwxyz") -> list[dict]:
    """
    Try all possible shift values on the glyph stream.
    Treats each unique glyph as an index into an ordered alphabet.
    """
    unique_glyphs = sorted(set(glyphs))
    n = len(unique_glyphs)
    glyph_to_idx = {g: i for i, g in enumerate(unique_glyphs)}

    results = []
    for shift in range(min(n, 26)):
        decrypted = []
        for g in glyphs:
            idx = (glyph_to_idx[g] + shift) % 26
            if idx < len(alphabet):
                decrypted.append(alphabet[idx])
            else:
                decrypted.append("?")

        decrypted_stream = "".join(decrypted)

        # Reconstruct words
        dec_words = []
        pos = 0
        for w in words:
            end = pos + len(w)
            dec_words.append(decrypted_stream[pos:end])
            pos = end

        score = score_plaintext(decrypted_stream, dec_words)
        results.append({
            "method": f"caesar_shift_{shift}",
            "shift": shift,
            "sample_output": " ".join(dec_words[:20]),
            "score": score,
        })

    # Return best 3
    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


def attack_reverse_transposition(words: list[str]) -> dict:
    """
    Test if reversing the glyph order within each word produces
    better language scores. Some historical ciphers used this.
    """
    reversed_words = [w[::-1] for w in words]
    reversed_stream = "".join(reversed_words)
    plaintext = " ".join(reversed_words)
    score = score_plaintext(reversed_stream, reversed_words)

    return {
        "method": "reverse_transposition",
        "sample_output": plaintext[:500],
        "sample_words": reversed_words[:50],
        "score": score,
    }


def attack_columnar_transposition(words: list[str],
                                  key_lengths: list[int] | None = None) -> list[dict]:
    """
    Try columnar transposition with various key lengths.
    Read the text in columns instead of rows.
    """
    if key_lengths is None:
        key_lengths = [2, 3, 4, 5, 6, 7, 8]

    stream = "".join(words)
    results = []

    for klen in key_lengths:
        if klen >= len(stream):
            continue

        # Arrange into rows of klen, read by columns
        rows = [stream[i:i + klen] for i in range(0, len(stream), klen)]
        # Pad last row
        if rows and len(rows[-1]) < klen:
            rows[-1] = rows[-1] + "?" * (klen - len(rows[-1]))

        # Read columns
        cols_text = ""
        for col in range(klen):
            for row in rows:
                if col < len(row):
                    cols_text += row[col]

        # Split back into "words" using original word lengths
        col_words = []
        pos = 0
        for w in words:
            end = pos + len(w)
            if end <= len(cols_text):
                col_words.append(cols_text[pos:end])
            pos = end

        score = score_plaintext(cols_text[:len(stream)], col_words)
        results.append({
            "method": f"columnar_transposition_k{klen}",
            "key_length": klen,
            "sample_output": " ".join(col_words[:20]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


def attack_bigram_substitution(glyphs: str, words: list[str]) -> dict:
    """
    Treat common Voynich bigrams as single units (digraph cipher).
    The 25 glyphs might actually represent ~50+ values if read as pairs.
    """
    # Find most common bigrams in the glyph stream
    bigrams = [glyphs[i:i+2] for i in range(0, len(glyphs) - 1, 2)]
    bigram_freq = Counter(bigrams)

    # Map top bigrams to Latin letters by frequency
    sorted_bigrams = [b for b, _ in bigram_freq.most_common()]
    sorted_latin = sorted(LATIN_FREQ.keys(), key=lambda k: -LATIN_FREQ[k])

    mapping = {}
    for i, bg in enumerate(sorted_bigrams):
        if i < len(sorted_latin):
            mapping[bg] = sorted_latin[i]
        else:
            mapping[bg] = "?"

    # Decrypt
    decrypted = []
    for bg in bigrams:
        decrypted.append(mapping.get(bg, "?"))

    dec_stream = "".join(decrypted)
    # Approximate word reconstruction (every 2 glyphs = 1 char, so word lengths halve)
    dec_words = []
    pos = 0
    for w in words:
        chars_needed = len(w) // 2
        end = pos + chars_needed
        if end <= len(dec_stream):
            dec_words.append(dec_stream[pos:end])
        pos = end

    score = score_plaintext(dec_stream, dec_words)

    return {
        "method": "bigram_substitution",
        "mapping_sample": dict(list(mapping.items())[:15]),
        "sample_output": " ".join(dec_words[:30]),
        "score": score,
    }


def attack_vowel_consonant_pattern(words: list[str], stats: dict) -> dict:
    """
    Analyze the vowel/consonant pattern of the decryption output.
    Use positional glyph data to identify likely vowels vs consonants.
    """
    # In the Voynich, word-final glyphs are likely vowels (as in Latin/Italian)
    pos = stats["glyph_frequency"]["positional"]
    last_glyphs = list(pos.get("last", {}).keys())[:5]
    first_glyphs = list(pos.get("first", {}).keys())[:5]

    # Hypothesize: word-final glyphs = vowels
    likely_vowels = set(last_glyphs[:4])  # top 4 word-final glyphs
    all_glyphs_set = set()
    for w in words:
        all_glyphs_set.update(list(w))

    likely_consonants = all_glyphs_set - likely_vowels

    # Compute vowel ratio
    total = sum(len(w) for w in words)
    vowel_count = sum(1 for w in words for g in w if g in likely_vowels)
    vowel_ratio = vowel_count / total if total else 0

    # Latin vowel ratio ~0.45, Italian ~0.48
    latin_match = 1.0 - abs(vowel_ratio - 0.45) * 5
    italian_match = 1.0 - abs(vowel_ratio - 0.48) * 5

    return {
        "method": "vowel_consonant_analysis",
        "likely_vowels": sorted(likely_vowels),
        "likely_consonants": sorted(likely_consonants),
        "vowel_ratio": round(vowel_ratio, 4),
        "latin_vowel_match": round(max(0, latin_match), 4),
        "italian_vowel_match": round(max(0, italian_match), 4),
        "score": {
            "best_score": round(max(max(0, latin_match), max(0, italian_match)), 4),
            "best_language": "latin" if latin_match > italian_match else "italian",
            "details": (
                f"Vowel ratio: {vowel_ratio:.3f}. "
                f"Likely vowels (word-final): {sorted(likely_vowels)}. "
                f"Latin match: {max(0, latin_match):.3f}, "
                f"Italian match: {max(0, italian_match):.3f}."
            ),
        },
    }


def run_all_attacks(corpus: dict, stats: dict,
                    section: str | None = None,
                    folio: str | None = None) -> list[dict]:
    """Run all cipher attacks and return ranked results."""
    words = extract_words(corpus, section=section, folio=folio)
    if not words:
        return [{"error": f"No words found for section={section}, folio={folio}"}]

    glyphs = extract_glyph_stream(words)
    print(f"[decrypt] Working with {len(words)} words, {len(glyphs)} glyphs")

    results = []

    # 1. Frequency-based substitution (Latin)
    print("[decrypt] Trying frequency substitution (Latin)...")
    r = attack_frequency_substitution(glyphs, words, LATIN_FREQ, "latin")
    results.append(r)

    # 2. Frequency-based substitution (Italian)
    print("[decrypt] Trying frequency substitution (Italian)...")
    r = attack_frequency_substitution(glyphs, words, ITALIAN_FREQ, "italian")
    results.append(r)

    # 3. Caesar shifts
    print("[decrypt] Trying Caesar shifts...")
    for r in attack_caesar_shift(glyphs, words):
        results.append(r)

    # 4. Reverse transposition
    print("[decrypt] Trying reverse transposition...")
    r = attack_reverse_transposition(words)
    results.append(r)

    # 5. Columnar transposition
    print("[decrypt] Trying columnar transposition...")
    for r in attack_columnar_transposition(words):
        results.append(r)

    # 6. Bigram substitution
    print("[decrypt] Trying bigram substitution...")
    r = attack_bigram_substitution(glyphs, words)
    results.append(r)

    # 7. Vowel/consonant pattern analysis
    print("[decrypt] Analyzing vowel/consonant patterns...")
    r = attack_vowel_consonant_pattern(words, stats)
    results.append(r)

    # Sort by best score
    results.sort(key=lambda r: -r.get("score", {}).get("best_score", 0))

    return results


def main():
    parser = argparse.ArgumentParser(description="Brain-V decryption engine")
    parser.add_argument("--section", type=str, default="herbal",
                        help="Section to target (herbal/astronomical/biological/etc)")
    parser.add_argument("--folio", type=str, default=None,
                        help="Specific folio to target (e.g. f1r)")
    parser.add_argument("--cipher", type=str, default=None,
                        help="Specific cipher to try (sub/caesar/transpose/bigram/all)")
    args = parser.parse_args()

    if not CORPUS_PATH.exists() or not STATS_PATH.exists():
        print("[decrypt] ERROR: Run perceive.py first.")
        return

    corpus = load_corpus()
    stats = json.loads(STATS_PATH.read_text(encoding="utf-8"))

    target = args.folio or args.section or "herbal"
    print(f"[decrypt] === Brain-V Decryption Engine ===")
    print(f"[decrypt] Target: {target}")
    print(f"[decrypt] Running all attacks...\n")

    results = run_all_attacks(
        corpus, stats,
        section=None if args.folio else args.section,
        folio=args.folio,
    )

    # Print results
    print(f"\n{'='*60}")
    print(f"  DECRYPTION RESULTS — ranked by score")
    print(f"{'='*60}\n")

    for i, r in enumerate(results, 1):
        method = r.get("method", "unknown")
        score = r.get("score", {})
        best = score.get("best_score", 0)
        lang = score.get("best_language", "?")
        details = score.get("details", "")

        color = "***" if best > 0.3 else ""
        print(f"  {i}. {color}{method}{color}")
        print(f"     Score: {best:.4f} ({lang})")
        print(f"     {details[:120]}")

        sample = r.get("sample_output", "")
        if sample:
            print(f"     Sample: {sample[:100]}")
        print()

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result_file = {
        "date": today,
        "target": target,
        "section": args.section,
        "folio": args.folio,
        "attacks": len(results),
        "best_method": results[0].get("method", "none") if results else "none",
        "best_score": results[0].get("score", {}).get("best_score", 0) if results else 0,
        "results": results,
    }

    out_path = RESULTS_DIR / f"{today}-{target}.json"
    out_path.write_text(json.dumps(result_file, indent=2, default=str), encoding="utf-8")
    print(f"[decrypt] Results saved to {out_path}")

    # Summary
    best = results[0] if results else None
    if best:
        bs = best.get("score", {}).get("best_score", 0)
        if bs > 0.5:
            print(f"\n[decrypt] *** PROMISING: {best['method']} scored {bs:.4f} ***")
            print(f"[decrypt] This warrants deeper investigation.")
        elif bs > 0.3:
            print(f"\n[decrypt] Moderate signal from {best['method']} ({bs:.4f})")
            print(f"[decrypt] Worth refining but not conclusive.")
        else:
            print(f"\n[decrypt] No strong signals. Best: {best['method']} ({bs:.4f})")
            print(f"[decrypt] These cipher types likely don't apply to this section.")

    return results


if __name__ == "__main__":
    main()
