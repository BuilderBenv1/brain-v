"""
decrypt.py — Brain-V's decryption engine

Attempts actual decipherment of Voynich text using every viable cipher technique.
When a cipher-type hypothesis scores high enough, this module applies the
proposed cipher to sample sections and measures whether the output resembles
a known natural language.

Supported cipher attacks (22 total):
  === Substitution family ===
  1.  Simple substitution (frequency analysis, Latin + Italian)
  2.  Caesar/shift cipher (brute force all 26 shifts)
  3.  Bigram substitution (digraph cipher)
  4.  Homophonic substitution (many-to-one glyph mapping)
  5.  Affine cipher (ax+b mod 26)

  === Polyalphabetic family ===
  6.  Vigenere / polyalphabetic (Kasiski + IC key-length detection)
  7.  Beaufort cipher (reverse Vigenere)
  8.  Autokey cipher (plaintext-seeded key)

  === Transposition family ===
  9.  Columnar transposition (multiple key lengths)
  10. Reverse transposition (word-level reversal)
  11. Rail fence cipher (zigzag read)
  12. Scytale / strip cipher (cylinder wrap)
  13. Route cipher (spiral/diagonal read through grid)

  === Combined / layered ===
  14. Substitution + transposition combined
  15. Substitution + reverse (sub then flip words)

  === Structural / encoding ===
  16. Null cipher extraction (every Nth glyph)
  17. Steganographic extraction (first/last glyph of each word)
  18. Syllabic encoding (glyph pairs/triples as syllables)
  19. Verbose cipher (multiple glyphs per plaintext letter)
  20. Word-level codebook (each Voynich word = code entry)

  === Analytical ===
  21. Index of Coincidence analysis (mono vs poly determination)
  22. Vowel/consonant pattern analysis (positional inference)

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
from itertools import combinations
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
    "aqua", "herba", "terra", "ignis", "aer", "lux", "nox",
    "radix", "flos", "folium", "semen", "cortex", "succus",
    "medicina", "morbus", "febris", "dolor", "corpus", "sanguis",
    "caput", "manus", "oculus", "luna", "sol", "stella", "caelum",
}

ITALIAN_WORDS = {
    "e", "di", "il", "la", "che", "in", "per", "con", "non", "una",
    "un", "del", "le", "da", "si", "al", "lo", "come", "ma", "se",
    "nel", "sono", "ha", "era", "suo", "sua", "dei", "gli", "delle",
    "alla", "anche", "questo", "quella", "essere", "stato", "fatto",
    "tutto", "loro", "quando", "molto", "dopo", "prima", "sempre",
    "ogni", "dove", "qui", "ora", "poi", "tra", "fra", "solo",
    "cosa", "tempo", "mano", "parte", "acqua", "terra", "fuoco",
    "erba", "radice", "fiore", "foglia", "seme", "corteccia",
    "medicina", "malattia", "febbre", "dolore", "corpo", "sangue",
    "testa", "occhio", "luna", "sole", "stella", "cielo",
}

# Latin bigrams for bigram frequency comparison
LATIN_COMMON_BIGRAMS = [
    "is", "us", "um", "er", "in", "es", "et", "en", "ti", "re",
    "an", "nt", "at", "it", "te", "on", "or", "tu", "am", "ar",
]

ITALIAN_COMMON_BIGRAMS = [
    "re", "er", "on", "di", "in", "an", "en", "to", "la", "co",
    "no", "al", "ti", "le", "ne", "io", "ra", "el", "ta", "te",
]


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


def reconstruct_words(stream: str, words: list[str]) -> list[str]:
    """Split a decrypted stream back into words using original word lengths."""
    result = []
    pos = 0
    for w in words:
        end = pos + len(w)
        if end <= len(stream):
            result.append(stream[pos:end])
        pos = end
    return result


# --- Scoring functions ---

def frequency_correlation(observed: Counter, reference: dict) -> float:
    """Pearson correlation between observed and reference letter frequencies."""
    total = sum(observed.values()) or 1
    obs_pct = {ch: (count / total) * 100 for ch, count in observed.items()}

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


def index_of_coincidence(text: str) -> float:
    """Index of Coincidence — measures how far from random the text is."""
    freq = Counter(text)
    n = len(text)
    if n < 2:
        return 0.0
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))


def bigram_frequency_correlation(text: str, reference_bigrams: list[str]) -> float:
    """Score how well the top bigrams in text match a reference language's top bigrams."""
    if len(text) < 4:
        return 0.0
    bigrams = [text[i:i+2] for i in range(len(text) - 1)]
    bg_freq = Counter(bigrams)
    top_observed = [b for b, _ in bg_freq.most_common(20)]
    hits = sum(1 for b in top_observed if b in reference_bigrams)
    return hits / 20


def score_plaintext(text: str, words: list[str]) -> dict:
    """Score a candidate plaintext against Latin and Italian profiles."""
    if not text:
        return {"latin_score": 0, "italian_score": 0, "best_language": "none",
                "best_score": 0, "details": "empty output"}

    char_freq = Counter(text.lower())
    text_entropy = entropy(text.lower())
    text_ic = index_of_coincidence(text.lower())

    # Frequency correlation
    latin_corr = frequency_correlation(char_freq, LATIN_FREQ)
    italian_corr = frequency_correlation(char_freq, ITALIAN_FREQ)

    # Dictionary hits
    latin_dict = dictionary_hit_rate(words, LATIN_WORDS)
    italian_dict = dictionary_hit_rate(words, ITALIAN_WORDS)

    # Entropy comparison (Latin ~4.0, Italian ~3.95)
    latin_ent_score = max(0, 1.0 - abs(text_entropy - 4.0) / 2.0)
    italian_ent_score = max(0, 1.0 - abs(text_entropy - 3.95) / 2.0)

    # IC comparison (English ~0.065, Latin ~0.07, Italian ~0.075, random ~0.038)
    latin_ic_score = max(0, 1.0 - abs(text_ic - 0.07) / 0.03)
    italian_ic_score = max(0, 1.0 - abs(text_ic - 0.075) / 0.03)

    # Bigram match
    latin_bg = bigram_frequency_correlation(text.lower(), LATIN_COMMON_BIGRAMS)
    italian_bg = bigram_frequency_correlation(text.lower(), ITALIAN_COMMON_BIGRAMS)

    # Combined scores (weighted)
    latin_score = (
        latin_corr * 0.30 +          # frequency match
        latin_dict * 0.30 +           # dictionary hits
        latin_ent_score * 0.15 +      # entropy match
        latin_ic_score * 0.10 +       # IC match
        latin_bg * 0.15              # bigram match
    )
    italian_score = (
        italian_corr * 0.30 +
        italian_dict * 0.30 +
        italian_ent_score * 0.15 +
        italian_ic_score * 0.10 +
        italian_bg * 0.15
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
        "ic": round(text_ic, 6),
        "latin_bigram_match": round(latin_bg, 4),
        "italian_bigram_match": round(italian_bg, 4),
        "details": (
            f"Freq corr: Latin={latin_corr:.3f}, Italian={italian_corr:.3f}. "
            f"Dict hits: Latin={latin_dict:.3f}, Italian={italian_dict:.3f}. "
            f"Entropy: {text_entropy:.3f} bits. IC: {text_ic:.5f}."
        ),
    }


# =====================================================================
#  SUBSTITUTION FAMILY
# =====================================================================

def attack_frequency_substitution(glyphs: str, words: list[str],
                                  target_freq: dict, language: str) -> dict:
    """
    Simple substitution via frequency analysis.
    Map most frequent Voynich glyph to most frequent target letter, etc.
    """
    glyph_freq = Counter(glyphs)
    sorted_glyphs = [g for g, _ in glyph_freq.most_common()]
    sorted_target = sorted(target_freq.keys(), key=lambda k: -target_freq[k])

    mapping = {}
    for i, g in enumerate(sorted_glyphs):
        if i < len(sorted_target):
            mapping[g] = sorted_target[i]
        else:
            mapping[g] = "?"

    decrypted_stream = "".join(mapping.get(g, "?") for g in glyphs)
    decrypted_words = reconstruct_words(decrypted_stream, words)
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
    """Try all possible shift values on the glyph stream."""
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
        dec_words = reconstruct_words(decrypted_stream, words)
        score = score_plaintext(decrypted_stream, dec_words)
        results.append({
            "method": f"caesar_shift_{shift}",
            "shift": shift,
            "sample_output": " ".join(dec_words[:20]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


def attack_bigram_substitution(glyphs: str, words: list[str]) -> dict:
    """
    Treat common Voynich bigrams as single units (digraph cipher).
    The 25 glyphs might actually represent ~50+ values if read as pairs.
    """
    bigrams = [glyphs[i:i+2] for i in range(0, len(glyphs) - 1, 2)]
    bigram_freq = Counter(bigrams)

    sorted_bigrams = [b for b, _ in bigram_freq.most_common()]
    sorted_latin = sorted(LATIN_FREQ.keys(), key=lambda k: -LATIN_FREQ[k])

    mapping = {}
    for i, bg in enumerate(sorted_bigrams):
        if i < len(sorted_latin):
            mapping[bg] = sorted_latin[i]
        else:
            mapping[bg] = "?"

    decrypted = [mapping.get(bg, "?") for bg in bigrams]
    dec_stream = "".join(decrypted)

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


def attack_homophonic_substitution(glyphs: str, words: list[str]) -> dict:
    """
    Homophonic substitution: multiple Voynich glyphs map to the same plaintext letter.
    In the Voynich, common glyphs like o/a/e/y might all encode the same few vowels.
    Try clustering the 25 glyphs into ~15 groups based on positional similarity,
    then map groups to letters.
    """
    # Group glyphs by positional behavior
    # Use a simple approach: cluster by frequency rank
    glyph_freq = Counter(glyphs)
    ranked = [g for g, _ in glyph_freq.most_common()]

    # Target: Italian has 21 letters effectively. Map 25 glyphs to 21.
    # The top 4 extra glyphs get merged with their nearest frequency neighbor.
    target_letters = sorted(ITALIAN_FREQ.keys(), key=lambda k: -ITALIAN_FREQ[k])

    # Build mapping: first 21 glyphs map 1:1, remaining get merged
    mapping = {}
    for i, g in enumerate(ranked):
        if i < len(target_letters):
            mapping[g] = target_letters[i]
        else:
            # Map to the letter at position i mod len(target)
            mapping[g] = target_letters[i % len(target_letters)]

    dec_stream = "".join(mapping.get(g, "?") for g in glyphs)
    dec_words = reconstruct_words(dec_stream, words)
    score = score_plaintext(dec_stream, dec_words)

    return {
        "method": "homophonic_substitution_italian",
        "mapping": mapping,
        "sample_output": " ".join(dec_words[:40]),
        "sample_words": dec_words[:50],
        "score": score,
    }


def attack_affine_cipher(glyphs: str, words: list[str]) -> list[dict]:
    """
    Affine cipher: E(x) = (ax + b) mod 26.
    Try all valid 'a' values (coprime with 26) and all 'b' shifts.
    """
    unique_glyphs = sorted(set(glyphs))
    glyph_to_idx = {g: i for i, g in enumerate(unique_glyphs)}
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    # Values of 'a' coprime with 26: 1,3,5,7,9,11,15,17,19,21,23,25
    valid_a = [a for a in range(1, 26) if math.gcd(a, 26) == 1]

    results = []
    for a in valid_a:
        for b in range(0, 26, 2):  # Sample b values to keep runtime sane
            decrypted = []
            for g in glyphs:
                idx = glyph_to_idx.get(g, 0)
                mapped = (a * idx + b) % 26
                decrypted.append(alphabet[mapped])

            dec_stream = "".join(decrypted)
            dec_words = reconstruct_words(dec_stream, words)
            score = score_plaintext(dec_stream, dec_words)
            results.append({
                "method": f"affine_a{a}_b{b}",
                "a": a, "b": b,
                "sample_output": " ".join(dec_words[:20]),
                "score": score,
            })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


# =====================================================================
#  POLYALPHABETIC FAMILY
# =====================================================================

def kasiski_examination(glyphs: str, min_len: int = 3, max_len: int = 6) -> list[int]:
    """
    Kasiski examination: find repeated sequences in the ciphertext and
    compute GCDs of distances between repetitions to estimate key length.
    """
    distances = []
    for seq_len in range(min_len, max_len + 1):
        seen = {}
        for i in range(len(glyphs) - seq_len + 1):
            seq = glyphs[i:i + seq_len]
            if seq in seen:
                dist = i - seen[seq]
                if dist > 0:
                    distances.append(dist)
            seen[seq] = i

    if not distances:
        return [3, 4, 5, 6, 7]

    # Find most common factors (2-20)
    factor_counts = Counter()
    for d in distances:
        for f in range(2, min(21, d + 1)):
            if d % f == 0:
                factor_counts[f] += 1

    return [f for f, _ in factor_counts.most_common(5)]


def ic_key_length_detection(glyphs: str, max_key: int = 15) -> list[int]:
    """
    Use Index of Coincidence to estimate Vigenere key length.
    Split text into 'k' interleaved streams; the correct key length
    will show IC close to natural language (~0.065-0.075).
    """
    target_ic = 0.068  # midpoint of Latin/Italian
    results = []

    for k in range(2, max_key + 1):
        streams = [[] for _ in range(k)]
        for i, g in enumerate(glyphs):
            streams[i % k].append(g)

        ics = []
        for stream in streams:
            if len(stream) > 1:
                ic_val = index_of_coincidence("".join(stream))
                ics.append(ic_val)

        if ics:
            avg_ic = sum(ics) / len(ics)
            results.append((k, avg_ic, abs(avg_ic - target_ic)))

    results.sort(key=lambda x: x[2])
    return [k for k, _, _ in results[:5]]


def attack_vigenere(glyphs: str, words: list[str]) -> list[dict]:
    """
    Vigenere/polyalphabetic cipher attack.
    1. Use Kasiski + IC to determine likely key lengths
    2. For each key length, solve each column as a simple substitution
    3. Score the combined output
    """
    unique_glyphs = sorted(set(glyphs))
    n_glyphs = len(unique_glyphs)
    glyph_to_idx = {g: i for i, g in enumerate(unique_glyphs)}
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    # Determine likely key lengths
    kasiski_keys = kasiski_examination(glyphs)
    ic_keys = ic_key_length_detection(glyphs)
    # Merge, preferring keys that appear in both
    all_keys = list(dict.fromkeys(kasiski_keys + ic_keys))[:8]

    # Target frequency (use Italian as primary, it scored higher)
    target = sorted(ITALIAN_FREQ.keys(), key=lambda k: -ITALIAN_FREQ[k])

    results = []
    for key_len in all_keys:
        # Split into columns
        columns = [[] for _ in range(key_len)]
        for i, g in enumerate(glyphs):
            columns[i % key_len].append(g)

        # Solve each column by frequency analysis
        key = []
        for col in columns:
            col_freq = Counter(col)
            if not col_freq:
                key.append(0)
                continue
            most_common_glyph = col_freq.most_common(1)[0][0]
            # Assume most common maps to 'e' (most common in Italian/Latin)
            mc_idx = glyph_to_idx.get(most_common_glyph, 0)
            e_idx = 4  # 'e' is index 4 in alphabet
            shift = (mc_idx - e_idx) % min(n_glyphs, 26)
            key.append(shift)

        # Decrypt
        decrypted = []
        for i, g in enumerate(glyphs):
            idx = glyph_to_idx.get(g, 0)
            shift = key[i % key_len]
            plain_idx = (idx - shift) % 26
            decrypted.append(alphabet[plain_idx])

        dec_stream = "".join(decrypted)
        dec_words = reconstruct_words(dec_stream, words)
        score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"vigenere_k{key_len}",
            "key_length": key_len,
            "key_shifts": key,
            "kasiski_detected": key_len in kasiski_keys,
            "ic_detected": key_len in ic_keys,
            "sample_output": " ".join(dec_words[:25]),
            "sample_words": dec_words[:50],
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


def attack_beaufort(glyphs: str, words: list[str]) -> list[dict]:
    """
    Beaufort cipher: D(c) = (key - c) mod 26, instead of Vigenere's (c - key).
    Historically plausible for 15th century. Uses same key detection as Vigenere.
    """
    unique_glyphs = sorted(set(glyphs))
    n_glyphs = len(unique_glyphs)
    glyph_to_idx = {g: i for i, g in enumerate(unique_glyphs)}
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    key_lengths = ic_key_length_detection(glyphs)[:4]

    results = []
    for key_len in key_lengths:
        columns = [[] for _ in range(key_len)]
        for i, g in enumerate(glyphs):
            columns[i % key_len].append(g)

        key = []
        for col in columns:
            col_freq = Counter(col)
            if not col_freq:
                key.append(0)
                continue
            mc = col_freq.most_common(1)[0][0]
            mc_idx = glyph_to_idx.get(mc, 0)
            key.append((4 + mc_idx) % min(n_glyphs, 26))  # key = e + cipher

        decrypted = []
        for i, g in enumerate(glyphs):
            idx = glyph_to_idx.get(g, 0)
            k = key[i % key_len]
            plain_idx = (k - idx) % 26  # Beaufort: key - cipher
            decrypted.append(alphabet[plain_idx])

        dec_stream = "".join(decrypted)
        dec_words = reconstruct_words(dec_stream, words)
        score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"beaufort_k{key_len}",
            "key_length": key_len,
            "sample_output": " ".join(dec_words[:25]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:2]


def attack_autokey(glyphs: str, words: list[str]) -> list[dict]:
    """
    Autokey cipher: key = primer + plaintext. Each decrypted char becomes
    the next key character. Try multiple primer values.
    """
    unique_glyphs = sorted(set(glyphs))
    glyph_to_idx = {g: i for i, g in enumerate(unique_glyphs)}
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    results = []
    # Try primers based on common starting letters
    for primer_idx in range(min(len(unique_glyphs), 26)):
        decrypted = []
        key_val = primer_idx

        for g in glyphs[:5000]:  # Limit for speed
            idx = glyph_to_idx.get(g, 0)
            plain_idx = (idx - key_val) % 26
            decrypted.append(alphabet[plain_idx])
            key_val = plain_idx  # Next key = this plaintext char

        dec_stream = "".join(decrypted)
        dec_words = reconstruct_words(dec_stream, words)
        score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"autokey_primer{primer_idx}",
            "primer": primer_idx,
            "sample_output": " ".join(dec_words[:20]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


# =====================================================================
#  TRANSPOSITION FAMILY
# =====================================================================

def attack_reverse_transposition(words: list[str]) -> dict:
    """Reverse the glyph order within each word."""
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
    """Columnar transposition with various key lengths."""
    if key_lengths is None:
        key_lengths = [2, 3, 4, 5, 6, 7, 8]

    stream = "".join(words)
    results = []

    for klen in key_lengths:
        if klen >= len(stream):
            continue

        rows = [stream[i:i + klen] for i in range(0, len(stream), klen)]
        if rows and len(rows[-1]) < klen:
            rows[-1] = rows[-1] + "?" * (klen - len(rows[-1]))

        cols_text = ""
        for col in range(klen):
            for row in rows:
                if col < len(row):
                    cols_text += row[col]

        col_words = reconstruct_words(cols_text, words)
        score = score_plaintext(cols_text[:len(stream)], col_words)
        results.append({
            "method": f"columnar_transposition_k{klen}",
            "key_length": klen,
            "sample_output": " ".join(col_words[:20]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


def attack_rail_fence(glyphs: str, words: list[str]) -> list[dict]:
    """
    Rail fence cipher: write text in zigzag across N rails, read off rows.
    Try decryption by reversing the process.
    """
    results = []
    for n_rails in range(2, 8):
        if n_rails >= len(glyphs):
            continue

        # Calculate the length of each rail
        cycle = 2 * (n_rails - 1) or 1
        rail_lens = [0] * n_rails
        for i in range(len(glyphs)):
            pos_in_cycle = i % cycle
            rail = pos_in_cycle if pos_in_cycle < n_rails else cycle - pos_in_cycle
            rail_lens[rail] += 1

        # Split ciphertext into rails
        rails = []
        pos = 0
        for rlen in rail_lens:
            rails.append(list(glyphs[pos:pos + rlen]))
            pos += rlen

        # Read off in zigzag order
        rail_indices = [0] * n_rails
        decrypted = []
        for i in range(len(glyphs)):
            pos_in_cycle = i % cycle
            rail = pos_in_cycle if pos_in_cycle < n_rails else cycle - pos_in_cycle
            if rail_indices[rail] < len(rails[rail]):
                decrypted.append(rails[rail][rail_indices[rail]])
                rail_indices[rail] += 1
            else:
                decrypted.append("?")

        dec_stream = "".join(decrypted)
        dec_words = reconstruct_words(dec_stream, words)
        score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"rail_fence_{n_rails}rails",
            "rails": n_rails,
            "sample_output": " ".join(dec_words[:20]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:2]


def attack_scytale(glyphs: str, words: list[str]) -> list[dict]:
    """
    Scytale/strip cipher: text written in a spiral around a cylinder.
    Equivalent to columnar transposition where the key is just column width.
    Try unwrapping with various circumferences.
    """
    results = []
    for circ in range(3, 20):
        n_rows = math.ceil(len(glyphs) / circ)
        # Pad
        padded = glyphs + "?" * (n_rows * circ - len(glyphs))

        # Read column by column (unwrap the cylinder)
        decrypted = []
        for col in range(circ):
            for row in range(n_rows):
                idx = row * circ + col
                if idx < len(padded):
                    decrypted.append(padded[idx])

        dec_stream = "".join(decrypted)[:len(glyphs)]
        dec_words = reconstruct_words(dec_stream, words)
        score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"scytale_circ{circ}",
            "circumference": circ,
            "sample_output": " ".join(dec_words[:20]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:2]


def attack_route_cipher(glyphs: str, words: list[str]) -> list[dict]:
    """
    Route cipher: text arranged in a grid, read in a spiral or diagonal pattern.
    Try spiral read-out on various grid dimensions.
    """
    results = []

    for n_cols in [5, 6, 7, 8, 9, 10, 12, 15]:
        n_rows = math.ceil(len(glyphs) / n_cols)
        padded = glyphs + "?" * (n_rows * n_cols - len(glyphs))

        # Build grid
        grid = []
        for r in range(n_rows):
            grid.append(list(padded[r * n_cols:(r + 1) * n_cols]))

        # Spiral read
        decrypted = []
        top, bottom, left, right = 0, n_rows - 1, 0, n_cols - 1
        while top <= bottom and left <= right:
            for c in range(left, right + 1):
                if top < len(grid) and c < len(grid[top]):
                    decrypted.append(grid[top][c])
            top += 1
            for r in range(top, bottom + 1):
                if r < len(grid) and right < len(grid[r]):
                    decrypted.append(grid[r][right])
            right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    if bottom < len(grid) and c < len(grid[bottom]):
                        decrypted.append(grid[bottom][c])
                bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    if r < len(grid) and left < len(grid[r]):
                        decrypted.append(grid[r][left])
                left += 1

        dec_stream = "".join(decrypted)[:len(glyphs)]
        dec_words = reconstruct_words(dec_stream, words)
        score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"route_spiral_{n_cols}cols",
            "columns": n_cols,
            "sample_output": " ".join(dec_words[:20]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:2]


# =====================================================================
#  COMBINED / LAYERED ATTACKS
# =====================================================================

def attack_sub_then_transpose(glyphs: str, words: list[str]) -> list[dict]:
    """
    Apply frequency substitution first, then try transposition on the result.
    This tests the H001 hypothesis (combination cipher) directly.
    """
    results = []

    for target_freq, language in [(ITALIAN_FREQ, "italian"), (LATIN_FREQ, "latin")]:
        # Step 1: frequency substitution
        glyph_freq = Counter(glyphs)
        sorted_glyphs = [g for g, _ in glyph_freq.most_common()]
        sorted_target = sorted(target_freq.keys(), key=lambda k: -target_freq[k])
        mapping = {}
        for i, g in enumerate(sorted_glyphs):
            mapping[g] = sorted_target[i] if i < len(sorted_target) else "?"

        sub_stream = "".join(mapping.get(g, "?") for g in glyphs)

        # Step 2: try columnar transposition on the substituted text
        for klen in [3, 4, 5, 6, 7]:
            rows = [sub_stream[i:i + klen] for i in range(0, len(sub_stream), klen)]
            if rows and len(rows[-1]) < klen:
                rows[-1] = rows[-1] + "?" * (klen - len(rows[-1]))
            cols_text = ""
            for col in range(klen):
                for row in rows:
                    if col < len(row):
                        cols_text += row[col]

            dec_words = reconstruct_words(cols_text[:len(glyphs)], words)
            score = score_plaintext(cols_text[:len(glyphs)], dec_words)

            results.append({
                "method": f"sub_{language}_then_columnar_k{klen}",
                "substitution": language,
                "transposition_key": klen,
                "sample_output": " ".join(dec_words[:25]),
                "score": score,
            })

        # Step 2b: try reverse within words after substitution
        sub_words = reconstruct_words(sub_stream, words)
        rev_words = [w[::-1] for w in sub_words]
        rev_stream = "".join(rev_words)
        score = score_plaintext(rev_stream, rev_words)

        results.append({
            "method": f"sub_{language}_then_reverse",
            "substitution": language,
            "sample_output": " ".join(rev_words[:30]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


# =====================================================================
#  STRUCTURAL / ENCODING ATTACKS
# =====================================================================

def attack_null_cipher(glyphs: str, words: list[str]) -> list[dict]:
    """
    Null cipher: only every Nth glyph carries the real message.
    The rest is padding/noise.
    """
    results = []
    for n in [2, 3, 4, 5]:
        # Extract every Nth glyph
        extracted = glyphs[::n]
        if len(extracted) < 10:
            continue

        # Try to split into ~5-char "words"
        avg_len = 5
        ext_words = [extracted[i:i+avg_len] for i in range(0, len(extracted), avg_len)]
        score = score_plaintext(extracted, ext_words)

        results.append({
            "method": f"null_cipher_every{n}th",
            "interval": n,
            "extracted_length": len(extracted),
            "sample_output": " ".join(ext_words[:20]),
            "score": score,
        })

    # Also try: first glyph after space (word-initial)
    initials = "".join(w[0] for w in words if w)
    init_words = [initials[i:i+5] for i in range(0, len(initials), 5)]
    score = score_plaintext(initials, init_words)
    results.append({
        "method": "null_cipher_word_initials",
        "extracted_length": len(initials),
        "sample_output": " ".join(init_words[:20]),
        "score": score,
    })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


def attack_steganographic(words: list[str]) -> list[dict]:
    """
    Steganographic extraction: the real message is hidden in specific positions.
    Try: first letter, last letter, first+last, middle letter of each word.
    """
    results = []

    extractions = {
        "first_letter": "".join(w[0] for w in words if w),
        "last_letter": "".join(w[-1] for w in words if w),
        "first_last": "".join(w[0] + w[-1] for w in words if len(w) >= 2),
        "middle_letter": "".join(w[len(w)//2] for w in words if w),
        "second_letter": "".join(w[1] for w in words if len(w) >= 2),
    }

    for name, extracted in extractions.items():
        if len(extracted) < 10:
            continue
        ext_words = [extracted[i:i+5] for i in range(0, len(extracted), 5)]
        score = score_plaintext(extracted, ext_words)

        results.append({
            "method": f"stego_{name}",
            "extracted_length": len(extracted),
            "sample_output": " ".join(ext_words[:20]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:3]


def attack_syllabic_encoding(glyphs: str, words: list[str]) -> dict:
    """
    Syllabic encoding: groups of 2-3 Voynich glyphs represent single syllables.
    Common in East Asian scripts and some historical codes.
    Map the most common trigrams to common Latin/Italian syllables.
    """
    # Find most common trigrams
    trigrams = [glyphs[i:i+3] for i in range(0, len(glyphs) - 2, 3)]
    tri_freq = Counter(trigrams)

    # Common Latin syllables (medical/herbal context)
    latin_syllables = [
        "us", "um", "is", "em", "ae", "am", "er", "en",
        "in", "es", "et", "re", "ti", "an", "at", "or",
        "al", "ar", "on", "it", "te", "ta", "ra", "de",
        "la", "co", "si", "na", "ma", "me", "mi", "no",
    ]

    mapping = {}
    for i, (tri, _) in enumerate(tri_freq.most_common(len(latin_syllables))):
        if i < len(latin_syllables):
            mapping[tri] = latin_syllables[i]

    decrypted = [mapping.get(t, "??") for t in trigrams]
    dec_stream = "".join(decrypted)

    # Split into word-sized chunks (~5 chars)
    dec_words = [dec_stream[i:i+6] for i in range(0, len(dec_stream), 6)]

    score = score_plaintext(dec_stream, dec_words)

    return {
        "method": "syllabic_trigram_latin",
        "mapping_sample": dict(list(mapping.items())[:10]),
        "sample_output": " ".join(dec_words[:20]),
        "score": score,
    }


def attack_verbose_cipher(glyphs: str, words: list[str]) -> list[dict]:
    """
    Verbose cipher: 2+ Voynich glyphs encode each plaintext letter.
    This would explain the Voynich's unusually long words.
    Test by mapping fixed-length glyph groups to letters.
    """
    results = []

    for group_size in [2, 3]:
        groups = [glyphs[i:i+group_size] for i in range(0, len(glyphs) - group_size + 1, group_size)]
        group_freq = Counter(groups)

        # Map by frequency to Italian letters
        sorted_groups = [g for g, _ in group_freq.most_common()]
        sorted_italian = sorted(ITALIAN_FREQ.keys(), key=lambda k: -ITALIAN_FREQ[k])

        mapping = {}
        for i, grp in enumerate(sorted_groups):
            mapping[grp] = sorted_italian[i] if i < len(sorted_italian) else "?"

        dec_stream = "".join(mapping.get(g, "?") for g in groups)

        # Reconstruct approximate words (original words shrink by group_size)
        dec_words = []
        pos = 0
        for w in words:
            n_chars = len(w) // group_size
            end = pos + n_chars
            if end <= len(dec_stream):
                dec_words.append(dec_stream[pos:end])
            pos = end

        score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"verbose_cipher_{group_size}to1",
            "group_size": group_size,
            "unique_groups": len(set(groups)),
            "sample_output": " ".join(dec_words[:30]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results[:2]


def attack_word_codebook(words: list[str]) -> dict:
    """
    Word-level codebook: each Voynich word maps to a plaintext word.
    HONEST SCORING: score includes unmapped words as failures, not excluded.
    """
    word_freq = Counter(words)
    sorted_voynich = [w for w, _ in word_freq.most_common()]

    latin_common = [
        "et", "in", "est", "non", "ad", "de", "qui", "ut", "cum", "sed",
        "quod", "per", "ab", "ex", "si", "aut", "nec", "enim", "autem",
        "hic", "ille", "esse", "sunt", "fuit", "quae", "quid", "omnis",
        "iam", "nunc", "tamen", "herba", "aqua", "radix", "flos", "folium",
        "semen", "terra", "ignis", "medicina", "morbus", "febris", "dolor",
        "sanguis", "corpus", "caput", "manus", "luna", "sol", "stella",
    ]

    mapping = {}
    for i, vw in enumerate(sorted_voynich):
        if i < len(latin_common):
            mapping[vw] = latin_common[i]
        else:
            mapping[vw] = f"[{vw}]"

    dec_words = [mapping.get(w, f"[{w}]") for w in words]

    # HONEST scoring: unmapped words count as misses
    mapped_count = sum(1 for w in dec_words if not w.startswith("["))
    mapped_ratio = mapped_count / len(dec_words) if dec_words else 0

    # Score on ALL words — unmapped ones treated as gibberish
    all_plain = []
    for w in dec_words:
        all_plain.append(w.strip("[]"))
    full_stream = "".join(all_plain)
    score = score_plaintext(full_stream, all_plain)

    # Override dict hits with honest numbers
    score["latin_dict_hits_honest"] = round(
        sum(1 for w in all_plain if w.lower() in LATIN_WORDS) / len(all_plain), 4
    )
    score["italian_dict_hits_honest"] = round(
        sum(1 for w in all_plain if w.lower() in ITALIAN_WORDS) / len(all_plain), 4
    )
    score["coverage"] = round(mapped_ratio, 4)
    # Penalize score by unmapped fraction
    score["best_score"] = round(score["best_score"] * mapped_ratio, 4)
    score["details"] = (
        f"Coverage: {mapped_ratio:.1%} tokens mapped. "
        f"Honest dict hits: Latin={score['latin_dict_hits_honest']}, "
        f"Italian={score['italian_dict_hits_honest']}. "
        f"{score['details']}"
    )

    return {
        "method": "word_codebook_latin",
        "mapping_sample": dict(list(mapping.items())[:20]),
        "sample_output": " ".join(dec_words[:30]),
        "mapped_ratio": round(mapped_ratio, 4),
        "mapped_tokens": mapped_count,
        "total_tokens": len(dec_words),
        "unmapped_top20": [w for w in sorted_voynich[len(latin_common):len(latin_common)+20]],
        "score": score,
    }


def attack_medical_codebook(words: list[str]) -> dict:
    """
    Refined word codebook using medieval medical Latin vocabulary.
    Based on H027 (text-only = least enciphered) and the pharmaceutical context
    suggested by the manuscript's illustrations.

    Strategy:
    1. Map top-49 words by frequency (same as basic codebook)
    2. Extend mapping for next ~100 words using medical Latin vocabulary
    3. Use word-length and positional glyph hints to constrain mapping
    4. Score honestly against full text
    """
    word_freq = Counter(words)
    sorted_voynich = [w for w, _ in word_freq.most_common()]

    # Tier 1: Function words (most frequent Latin words, matched by rank)
    tier1 = [
        "et", "in", "est", "non", "ad", "de", "qui", "ut", "cum", "sed",
        "quod", "per", "ab", "ex", "si", "aut", "nec", "enim", "autem",
        "hic", "ille", "esse", "sunt", "fuit", "quae", "quid", "omnis",
        "iam", "nunc", "tamen", "vel", "tam", "sic", "ita", "ergo",
    ]

    # Tier 2: Medical/herbal vocabulary (matched by word length to Voynich words)
    medical_vocab_by_length = {
        2: ["os", "re", "vi"],
        3: ["sal", "mel", "lac", "ius", "vis", "ova", "cor", "vas", "pus"],
        4: ["aqua", "dico", "vero", "fiat", "cera", "rosa", "dose", "olim",
            "aloe", "item", "idem", "modo", "inde", "sola", "nota", "alia"],
        5: ["herba", "radix", "folii", "succi", "morbi", "folia", "semen",
            "calor", "dolor", "febri", "ignis", "album", "nigra", "piper",
            "ungue", "misce", "ponit", "facit", "curat", "sanat", "terra"],
        6: ["recipe", "pulvis", "florem", "herbam", "potius", "calida",
            "frigid", "humida", "siccum", "contra", "medica", "corpus",
            "capiti", "sangui", "vulnus", "morbus"],
        7: ["ungento", "medicus", "virtute", "potione", "herbari", "materia",
            "calculi", "infirmi", "stomaco", "venenum"],
        8: ["medicina", "ungentum", "cataplas", "electuar", "decoctio",
            "emplasta", "infirmis"],
    }

    # Build mapping
    mapping = {}
    # Tier 1: top words by frequency -> function words
    for i, vw in enumerate(sorted_voynich):
        if i < len(tier1):
            mapping[vw] = tier1[i]
        else:
            break

    # Tier 2: next words matched by word length to medical vocab
    used_medical = set()
    for vw in sorted_voynich[len(tier1):]:
        vlen = len(vw)
        candidates = medical_vocab_by_length.get(vlen, [])
        for candidate in candidates:
            if candidate not in used_medical:
                mapping[vw] = candidate
                used_medical.add(candidate)
                break

    # Apply mapping
    dec_words = []
    for w in words:
        if w in mapping:
            dec_words.append(mapping[w])
        else:
            dec_words.append(f"[{w}]")

    # Honest scoring
    mapped_count = sum(1 for w in dec_words if not w.startswith("["))
    mapped_ratio = mapped_count / len(dec_words) if dec_words else 0

    all_plain = [w.strip("[]") for w in dec_words]
    full_stream = "".join(all_plain)
    score = score_plaintext(full_stream, all_plain)

    # Honest dict hits
    all_dict = LATIN_WORDS | set(tier1) | used_medical
    score["dict_hits_honest"] = round(
        sum(1 for w in all_plain if w.lower() in all_dict) / len(all_plain), 4
    )
    score["coverage"] = round(mapped_ratio, 4)
    score["best_score"] = round(score["best_score"] * mapped_ratio, 4)
    score["details"] = (
        f"Medical codebook: {len(mapping)} mappings, {mapped_ratio:.1%} coverage. "
        f"Dict hits (honest): {score['dict_hits_honest']}. "
        f"{score['details']}"
    )

    # Analyze unmapped words for patterns
    unmapped = [w for w in sorted_voynich if w not in mapping]
    unmapped_freq = [(w, word_freq[w]) for w in unmapped[:30]]

    # Check if unmapped words share stems with mapped words
    stem_matches = {}
    for uw in unmapped[:50]:
        for mw, lw in mapping.items():
            # Check if unmapped word is a suffix variant of a mapped word
            if len(uw) > len(mw) and uw.startswith(mw):
                suffix = uw[len(mw):]
                stem_matches[uw] = {"stem": mw, "maps_to": lw, "suffix": suffix}
                break
            if len(uw) > 2 and len(mw) > 2 and uw[:3] == mw[:3]:
                stem_matches[uw] = {"shared_prefix": mw, "maps_to": lw}
                break

    return {
        "method": "medical_codebook_latin",
        "tier1_count": len(tier1),
        "tier2_medical_count": len(used_medical),
        "total_mappings": len(mapping),
        "mapped_ratio": round(mapped_ratio, 4),
        "mapped_tokens": mapped_count,
        "total_tokens": len(dec_words),
        "unmapped_top30": unmapped_freq,
        "stem_matches": dict(list(stem_matches.items())[:15]),
        "mapping_sample": dict(list(mapping.items())[:30]),
        "sample_output": " ".join(dec_words[:40]),
        "score": score,
    }


# =====================================================================
#  ANALYTICAL ATTACKS
# =====================================================================

def attack_ic_analysis(glyphs: str, words: list[str], stats: dict) -> dict:
    """
    Index of Coincidence analysis — determine whether the cipher is
    monoalphabetic or polyalphabetic, and estimate key length.
    """
    overall_ic = index_of_coincidence(glyphs)

    # Expected IC values
    # Random: 1/N where N=alphabet size. For 25 glyphs: 0.04
    # Natural language: ~0.065-0.075
    # Voynich with 25 glyphs random: 1/25 = 0.04

    # IC by section
    section_ics = {}
    for section_name, section_data in stats["entropy"]["by_section"].items():
        sec_words = extract_words(
            json.loads(CORPUS_PATH.read_text(encoding="utf-8")),
            section=section_name
        )
        sec_glyphs = extract_glyph_stream(sec_words)
        if len(sec_glyphs) > 100:
            section_ics[section_name] = round(index_of_coincidence(sec_glyphs), 6)

    # IC per key length (Vigenere detection)
    key_length_ics = {}
    for k in range(1, 16):
        streams = [[] for _ in range(k)]
        for i, g in enumerate(glyphs):
            streams[i % k].append(g)
        ics = [index_of_coincidence("".join(s)) for s in streams if len(s) > 10]
        if ics:
            key_length_ics[k] = round(sum(ics) / len(ics), 6)

    # Find the key length where IC is highest (closest to natural language)
    best_key = max(key_length_ics.items(), key=lambda x: x[1]) if key_length_ics else (1, 0)

    # Determine cipher type
    if overall_ic > 0.060:
        cipher_type = "monoalphabetic (IC consistent with single alphabet)"
    elif overall_ic > 0.045:
        cipher_type = "possibly polyalphabetic or structured encoding"
    else:
        cipher_type = "polyalphabetic or random (IC near chance level)"

    return {
        "method": "ic_analysis",
        "overall_ic": round(overall_ic, 6),
        "expected_random_25": round(1/25, 6),
        "expected_natural_language": "0.065-0.075",
        "cipher_type_estimate": cipher_type,
        "best_key_length": best_key[0],
        "best_key_ic": best_key[1],
        "key_length_ics": key_length_ics,
        "section_ics": section_ics,
        "score": {
            "best_score": round(overall_ic * 10, 4),  # Normalize to 0-1 range
            "best_language": "analytical",
            "details": (
                f"Overall IC: {overall_ic:.5f}. "
                f"Random (25 glyphs): {1/25:.5f}. "
                f"Best key length: {best_key[0]} (IC={best_key[1]:.5f}). "
                f"{cipher_type}."
            ),
        },
    }


def attack_vowel_consonant_pattern(words: list[str], stats: dict) -> dict:
    """Analyze vowel/consonant patterns using positional glyph data."""
    pos = stats["glyph_frequency"]["positional"]
    last_glyphs = list(pos.get("last", {}).keys())[:5]

    likely_vowels = set(last_glyphs[:4])
    all_glyphs_set = set()
    for w in words:
        all_glyphs_set.update(list(w))

    likely_consonants = all_glyphs_set - likely_vowels

    total = sum(len(w) for w in words)
    vowel_count = sum(1 for w in words for g in w if g in likely_vowels)
    vowel_ratio = vowel_count / total if total else 0

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


def attack_currier_split(corpus: dict, stats: dict) -> dict:
    """
    Analyze Currier A vs B as potentially different cipher systems.
    Run frequency analysis on each separately and compare.
    """
    a_words = []
    b_words = []
    for f in corpus["folios"]:
        for line in f["lines"]:
            lang = f.get("language", "?")
            if lang == "A":
                a_words.extend(line["words"])
            elif lang == "B":
                b_words.extend(line["words"])

    results = {}
    for label, w_list in [("A", a_words), ("B", b_words)]:
        if not w_list:
            continue
        glyphs = extract_glyph_stream(w_list)
        ic = index_of_coincidence(glyphs)
        ent = entropy(glyphs)
        freq = Counter(glyphs)
        total = sum(freq.values())
        top5 = [(g, round(c/total*100, 2)) for g, c in freq.most_common(5)]
        avg_wl = sum(len(w) for w in w_list) / len(w_list)
        hapax = sum(1 for w, c in Counter(w_list).items() if c == 1) / len(set(w_list))

        results[label] = {
            "word_count": len(w_list),
            "unique_words": len(set(w_list)),
            "ic": round(ic, 6),
            "entropy": round(ent, 4),
            "top5_glyphs": top5,
            "avg_word_length": round(avg_wl, 2),
            "hapax_ratio": round(hapax, 3),
        }

    # Compare
    if "A" in results and "B" in results:
        ic_diff = abs(results["A"]["ic"] - results["B"]["ic"])
        ent_diff = abs(results["A"]["entropy"] - results["B"]["entropy"])
        wl_diff = abs(results["A"]["avg_word_length"] - results["B"]["avg_word_length"])

        divergence = ic_diff * 100 + ent_diff + wl_diff * 0.2
        interpretation = (
            "two_ciphers" if divergence > 0.5 else
            "two_scribes_same_cipher" if divergence > 0.1 else
            "single_system"
        )
    else:
        divergence = 0
        interpretation = "insufficient_data"

    return {
        "method": "currier_split_analysis",
        "language_a": results.get("A", {}),
        "language_b": results.get("B", {}),
        "divergence_score": round(divergence, 4),
        "interpretation": interpretation,
        "score": {
            "best_score": round(min(1.0, divergence), 4),
            "best_language": "analytical",
            "details": (
                f"A/B divergence: {divergence:.4f}. "
                f"IC diff: {ic_diff:.5f}. "
                f"Entropy diff: {ent_diff:.4f}. "
                f"Interpretation: {interpretation}."
            ) if "A" in results and "B" in results else "Insufficient data",
        },
    }


def attack_word_grammar(words: list[str], stats: dict) -> dict:
    """
    Test for word-internal grammar / slot structure (Stolfi's glyph position constraints).
    If the Voynich has strict positional rules, it suggests a structured encoding
    rather than a natural language cipher.
    """
    pos_data = stats["glyph_frequency"]["positional"]
    first = set(pos_data.get("first", {}).keys())
    middle = set(pos_data.get("middle", {}).keys())
    last = set(pos_data.get("last", {}).keys())

    # Compute transition matrix for bigrams within words
    transitions = Counter()
    for w in words:
        for i in range(len(w) - 1):
            transitions[(w[i], w[i+1])] += 1

    total_trans = sum(transitions.values())
    unique_trans = len(transitions)
    all_glyphs = first | middle | last
    possible_trans = len(all_glyphs) ** 2

    # Transition density: what fraction of possible bigrams actually occur
    density = unique_trans / possible_trans if possible_trans else 0

    # Positional exclusivity
    first_only = first - middle - last
    last_only = last - middle - first
    middle_only = middle - first - last

    # Check for forbidden transitions (common in structured encodings)
    forbidden_count = possible_trans - unique_trans
    forbidden_ratio = forbidden_count / possible_trans if possible_trans else 0

    # Natural languages have ~60-70% density, structured encodings much lower
    structure_score = 1.0 - density  # Higher = more structured
    if density < 0.3:
        interpretation = "highly_structured (strong slot grammar, suggests encoding)"
    elif density < 0.5:
        interpretation = "moderately_structured (some positional constraints)"
    else:
        interpretation = "loosely_structured (consistent with natural language)"

    return {
        "method": "word_grammar_analysis",
        "transition_density": round(density, 4),
        "unique_transitions": unique_trans,
        "possible_transitions": possible_trans,
        "forbidden_ratio": round(forbidden_ratio, 4),
        "first_only_glyphs": sorted(first_only),
        "last_only_glyphs": sorted(last_only),
        "middle_only_glyphs": sorted(middle_only),
        "interpretation": interpretation,
        "score": {
            "best_score": round(structure_score, 4),
            "best_language": "analytical",
            "details": (
                f"Transition density: {density:.3f} ({unique_trans}/{possible_trans}). "
                f"Forbidden: {forbidden_ratio:.1%}. "
                f"First-only: {sorted(first_only)}. Last-only: {sorted(last_only)}. "
                f"{interpretation}."
            ),
        },
    }


def attack_entropy_layers(corpus: dict) -> dict:
    """
    Multi-scale entropy analysis: character, word, line, page level.
    Compare entropy profile against known languages and known hoaxes.
    """
    all_words = []
    lines_per_page = []
    for f in corpus["folios"]:
        page_lines = []
        for line in f["lines"]:
            all_words.extend(line["words"])
            page_lines.append(" ".join(line["words"]))
        if page_lines:
            lines_per_page.append(page_lines)

    glyphs = extract_glyph_stream(all_words)

    # Character-level entropy
    char_ent = entropy(glyphs)

    # Word-level entropy
    word_ent = entropy(" ".join(all_words))

    # IC at character level
    char_ic = index_of_coincidence(glyphs)

    # Conditional entropy: H(char | previous char)
    bigrams = Counter()
    unigrams = Counter()
    for i in range(len(glyphs) - 1):
        bigrams[(glyphs[i], glyphs[i+1])] += 1
        unigrams[glyphs[i]] += 1
    unigrams[glyphs[-1]] = unigrams.get(glyphs[-1], 0) + 1

    cond_ent = 0
    total_bi = sum(bigrams.values())
    for (g1, g2), count in bigrams.items():
        p_bi = count / total_bi
        p_uni = unigrams[g1] / sum(unigrams.values())
        if p_bi > 0 and p_uni > 0:
            cond_ent -= p_bi * math.log2(p_bi / p_uni)

    # Second-order entropy (how predictable is the next character?)
    predictability = 1.0 - (cond_ent / char_ent) if char_ent > 0 else 0

    # Compare with known values
    # Latin: char_ent ~4.0, cond_ent ~3.2, predictability ~0.20
    # Random: char_ent ~4.6 (25 chars), cond_ent ~4.6, predictability ~0.0
    # Hoax (Rugg): char_ent ~3.5, cond_ent ~2.0, predictability ~0.43

    if predictability > 0.35:
        profile = "high_predictability (consistent with table/grille generation — cf. Rugg)"
    elif predictability > 0.15:
        profile = "moderate_predictability (consistent with natural language)"
    else:
        profile = "low_predictability (consistent with strong cipher or random)"

    return {
        "method": "entropy_layers_analysis",
        "char_entropy": round(char_ent, 4),
        "conditional_entropy": round(cond_ent, 4),
        "predictability": round(predictability, 4),
        "char_ic": round(char_ic, 6),
        "profile": profile,
        "reference": {
            "latin": {"char_ent": 4.0, "predictability": 0.20},
            "random_25": {"char_ent": 4.64, "predictability": 0.0},
            "hoax_rugg": {"char_ent": 3.5, "predictability": 0.43},
        },
        "score": {
            "best_score": round(max(0, 1.0 - abs(predictability - 0.20) * 3), 4),
            "best_language": "analytical",
            "details": (
                f"Char entropy: {char_ent:.3f}. Cond entropy: {cond_ent:.3f}. "
                f"Predictability: {predictability:.3f}. IC: {char_ic:.5f}. "
                f"{profile}."
            ),
        },
    }


# =====================================================================
#  HYPOTHESIS-DRIVEN TARGETED ATTACKS
#  Based on high-confidence findings from Brain-V's cognitive loop
# =====================================================================

def attack_morphological_strip(words: list[str]) -> list[dict]:
    """
    H023 (0.97): Word-final glyphs y, n, l, r function as detachable
    morphological markers. Strip them and re-analyze the resulting stems.
    If hapax ratio drops significantly, the suffixes are real morphology.
    """
    SUFFIXES = {"y", "n", "l", "r"}
    # Also try common multi-char suffixes seen in EVA
    MULTI_SUFFIXES = ["dy", "ey", "in", "ol", "ar", "or", "al", "an"]

    results = []

    # Single-char suffix strip
    stripped_1 = []
    for w in words:
        if len(w) > 2 and w[-1] in SUFFIXES:
            stripped_1.append(w[:-1])
        else:
            stripped_1.append(w)

    orig_unique = len(set(words))
    strip1_unique = len(set(stripped_1))
    reduction_1 = 1.0 - (strip1_unique / orig_unique) if orig_unique else 0

    strip1_glyphs = extract_glyph_stream(stripped_1)
    score_1 = score_plaintext(strip1_glyphs, stripped_1)

    results.append({
        "method": "morpho_strip_single_suffix",
        "suffixes_stripped": sorted(SUFFIXES),
        "original_unique": orig_unique,
        "stripped_unique": strip1_unique,
        "vocabulary_reduction": round(reduction_1, 4),
        "hapax_before": round(sum(1 for w, c in Counter(words).items() if c == 1) / orig_unique, 4),
        "hapax_after": round(sum(1 for w, c in Counter(stripped_1).items() if c == 1) / strip1_unique, 4) if strip1_unique else 0,
        "sample_words": stripped_1[:50],
        "score": score_1,
    })

    # Multi-char suffix strip
    stripped_m = []
    for w in words:
        done = False
        for suf in sorted(MULTI_SUFFIXES, key=len, reverse=True):
            if len(w) > len(suf) + 1 and w.endswith(suf):
                stripped_m.append(w[:-len(suf)])
                done = True
                break
        if not done:
            stripped_m.append(w)

    stripm_unique = len(set(stripped_m))
    reduction_m = 1.0 - (stripm_unique / orig_unique) if orig_unique else 0

    stripm_glyphs = extract_glyph_stream(stripped_m)
    score_m = score_plaintext(stripm_glyphs, stripped_m)

    results.append({
        "method": "morpho_strip_multi_suffix",
        "suffixes_stripped": MULTI_SUFFIXES,
        "original_unique": orig_unique,
        "stripped_unique": stripm_unique,
        "vocabulary_reduction": round(reduction_m, 4),
        "hapax_before": round(sum(1 for w, c in Counter(words).items() if c == 1) / orig_unique, 4),
        "hapax_after": round(sum(1 for w, c in Counter(stripped_m).items() if c == 1) / stripm_unique, 4) if stripm_unique else 0,
        "sample_words": stripped_m[:50],
        "score": score_m,
    })

    # Substitution AFTER suffix strip (H001 + H023 combo)
    for target_freq, language in [(ITALIAN_FREQ, "italian"), (LATIN_FREQ, "latin")]:
        glyph_freq = Counter(strip1_glyphs)
        sorted_glyphs = [g for g, _ in glyph_freq.most_common()]
        sorted_target = sorted(target_freq.keys(), key=lambda k: -target_freq[k])
        mapping = {g: sorted_target[i] if i < len(sorted_target) else "?"
                   for i, g in enumerate(sorted_glyphs)}

        dec_stream = "".join(mapping.get(g, "?") for g in strip1_glyphs)
        dec_words = reconstruct_words(dec_stream, stripped_1)
        score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"morpho_strip_then_sub_{language}",
            "vocab_reduction": round(reduction_1, 4),
            "sample_output": " ".join(dec_words[:30]),
            "sample_words": dec_words[:50],
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results


def attack_homophonic_reduction(glyphs: str, words: list[str]) -> list[dict]:
    """
    H020 (0.99): Multiple Voynich glyphs map to the same plaintext letter.
    Identify glyph clusters that behave similarly (same positional distribution)
    and merge them before attempting substitution.
    """
    # Compute positional profiles for each glyph
    glyph_profiles = {}
    for w in words:
        for i, g in enumerate(w):
            if g not in glyph_profiles:
                glyph_profiles[g] = {"first": 0, "middle": 0, "last": 0, "total": 0}
            glyph_profiles[g]["total"] += 1
            if i == 0:
                glyph_profiles[g]["first"] += 1
            elif i == len(w) - 1:
                glyph_profiles[g]["last"] += 1
            else:
                glyph_profiles[g]["middle"] += 1

    # Normalize profiles
    for g in glyph_profiles:
        t = glyph_profiles[g]["total"] or 1
        for pos in ["first", "middle", "last"]:
            glyph_profiles[g][pos] /= t

    # Cluster glyphs by positional similarity (cosine-like distance)
    all_g = sorted(glyph_profiles.keys())
    def profile_dist(a, b):
        pa, pb = glyph_profiles[a], glyph_profiles[b]
        return sum((pa[k] - pb[k]) ** 2 for k in ["first", "middle", "last"]) ** 0.5

    # Greedy clustering: merge pairs within distance threshold
    results = []
    for threshold in [0.15, 0.25, 0.35]:
        merged = {}  # glyph -> representative
        reps = list(all_g)
        for i, g1 in enumerate(all_g):
            if g1 in merged:
                continue
            for g2 in all_g[i+1:]:
                if g2 in merged:
                    continue
                if profile_dist(g1, g2) < threshold:
                    merged[g2] = g1

        # Build reduced alphabet
        def reduce(g):
            return merged.get(g, g)

        reduced_glyphs = "".join(reduce(g) for g in glyphs)
        reduced_words = ["".join(reduce(g) for g in w) for w in words]
        n_clusters = len(set(reduce(g) for g in all_g))

        # Now do frequency substitution on reduced alphabet
        rf = Counter(reduced_glyphs)
        sorted_rg = [g for g, _ in rf.most_common()]
        sorted_it = sorted(ITALIAN_FREQ.keys(), key=lambda k: -ITALIAN_FREQ[k])
        mapping = {g: sorted_it[i] if i < len(sorted_it) else "?"
                   for i, g in enumerate(sorted_rg)}

        dec_stream = "".join(mapping.get(g, "?") for g in reduced_glyphs)
        dec_words = reconstruct_words(dec_stream, reduced_words)
        score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"homophonic_reduce_t{threshold}_sub_italian",
            "threshold": threshold,
            "original_alphabet": len(all_g),
            "reduced_alphabet": n_clusters,
            "merges": {v: k for k, v in merged.items()},
            "sample_output": " ".join(dec_words[:30]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results


def attack_section_comparative(corpus: dict, stats: dict) -> list[dict]:
    """
    H027 (0.99) + H029 (0.99): Text-only section is closest to natural language.
    Compare frequency substitution results across all sections to find which
    section produces the most language-like output.
    """
    sections = ["text-only", "herbal", "recipes", "biological",
                "pharmaceutical", "cosmological", "zodiac", "astronomical"]

    results = []
    for section in sections:
        sec_words = extract_words(corpus, section=section)
        if len(sec_words) < 50:
            continue
        sec_glyphs = extract_glyph_stream(sec_words)

        # Run freq sub against Italian
        gf = Counter(sec_glyphs)
        sorted_g = [g for g, _ in gf.most_common()]
        sorted_it = sorted(ITALIAN_FREQ.keys(), key=lambda k: -ITALIAN_FREQ[k])
        mapping = {g: sorted_it[i] if i < len(sorted_it) else "?"
                   for i, g in enumerate(sorted_g)}

        dec_stream = "".join(mapping.get(g, "?") for g in sec_glyphs)
        dec_words = reconstruct_words(dec_stream, sec_words)
        score = score_plaintext(dec_stream, dec_words)

        # Section-specific stats
        sec_ic = index_of_coincidence(sec_glyphs)
        sec_ent = entropy(sec_glyphs)
        sec_hapax = sum(1 for w, c in Counter(sec_words).items() if c == 1) / len(set(sec_words))

        results.append({
            "method": f"section_compare_{section}",
            "section": section,
            "word_count": len(sec_words),
            "unique_words": len(set(sec_words)),
            "ic": round(sec_ic, 6),
            "entropy": round(sec_ent, 4),
            "hapax_ratio": round(sec_hapax, 4),
            "sample_output": " ".join(dec_words[:20]),
            "score": score,
        })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results


def attack_currier_parallel(corpus: dict) -> list[dict]:
    """
    H021/H025 (0.99): Currier A and B use different cipher alphabets for
    the same language. Solve them independently and compare.
    """
    a_words = []
    b_words = []
    for f in corpus["folios"]:
        lang = f.get("language", "?")
        for line in f["lines"]:
            if lang == "A":
                a_words.extend(line["words"])
            elif lang == "B":
                b_words.extend(line["words"])

    results = []
    for label, w_list in [("A", a_words), ("B", b_words)]:
        if len(w_list) < 50:
            continue
        glyphs = extract_glyph_stream(w_list)

        for target_freq, lang_name in [(ITALIAN_FREQ, "italian"), (LATIN_FREQ, "latin")]:
            gf = Counter(glyphs)
            sorted_g = [g for g, _ in gf.most_common()]
            sorted_t = sorted(target_freq.keys(), key=lambda k: -target_freq[k])
            mapping = {g: sorted_t[i] if i < len(sorted_t) else "?"
                       for i, g in enumerate(sorted_g)}

            dec_stream = "".join(mapping.get(g, "?") for g in glyphs)
            dec_words = reconstruct_words(dec_stream, w_list)
            score = score_plaintext(dec_stream, dec_words)

            results.append({
                "method": f"currier_{label}_sub_{lang_name}",
                "currier_language": label,
                "target_language": lang_name,
                "word_count": len(w_list),
                "mapping": mapping,
                "sample_output": " ".join(dec_words[:25]),
                "sample_words": dec_words[:50],
                "score": score,
            })

    # Check if A and B mappings converge (same glyph -> same letter)
    a_maps = {r["mapping"] for r in results if "currier_A" in r["method"] and "italian" in r["method"]}
    b_maps = {r["mapping"] for r in results if "currier_B" in r["method"] and "italian" in r["method"]}

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results


def attack_text_only_rosetta(corpus: dict, stats: dict) -> list[dict]:
    """
    H027 (0.99): Text-only section is the Rosetta stone.
    Build a mapping from text-only section, then apply it to herbal.
    If text-only is less enciphered, its mapping should transfer better.
    """
    textonly_words = extract_words(corpus, section="text-only")
    herbal_words = extract_words(corpus, section="herbal")

    if not textonly_words or not herbal_words:
        return []

    results = []

    for target_freq, lang_name in [(ITALIAN_FREQ, "italian"), (LATIN_FREQ, "latin")]:
        # Build mapping from text-only
        to_glyphs = extract_glyph_stream(textonly_words)
        gf = Counter(to_glyphs)
        sorted_g = [g for g, _ in gf.most_common()]
        sorted_t = sorted(target_freq.keys(), key=lambda k: -target_freq[k])
        mapping = {g: sorted_t[i] if i < len(sorted_t) else "?"
                   for i, g in enumerate(sorted_g)}

        # Score on text-only itself
        dec_to = "".join(mapping.get(g, "?") for g in to_glyphs)
        dec_to_words = reconstruct_words(dec_to, textonly_words)
        score_to = score_plaintext(dec_to, dec_to_words)

        results.append({
            "method": f"rosetta_textonly_self_{lang_name}",
            "source_section": "text-only",
            "target_section": "text-only",
            "target_language": lang_name,
            "mapping": mapping,
            "sample_output": " ".join(dec_to_words[:25]),
            "score": score_to,
        })

        # Apply text-only mapping to herbal section
        h_glyphs = extract_glyph_stream(herbal_words)
        dec_h = "".join(mapping.get(g, "?") for g in h_glyphs)
        dec_h_words = reconstruct_words(dec_h, herbal_words)
        score_h = score_plaintext(dec_h, dec_h_words)

        results.append({
            "method": f"rosetta_textonly_to_herbal_{lang_name}",
            "source_section": "text-only",
            "target_section": "herbal",
            "target_language": lang_name,
            "mapping": mapping,
            "sample_output": " ".join(dec_h_words[:25]),
            "score": score_h,
        })

        # Apply text-only mapping to recipes
        rec_words = extract_words(corpus, section="recipes")
        if rec_words:
            r_glyphs = extract_glyph_stream(rec_words)
            dec_r = "".join(mapping.get(g, "?") for g in r_glyphs)
            dec_r_words = reconstruct_words(dec_r, rec_words)
            score_r = score_plaintext(dec_r, dec_r_words)

            results.append({
                "method": f"rosetta_textonly_to_recipes_{lang_name}",
                "source_section": "text-only",
                "target_section": "recipes",
                "target_language": lang_name,
                "sample_output": " ".join(dec_r_words[:25]),
                "score": score_r,
            })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results


def attack_morpho_then_vigenere(glyphs: str, words: list[str]) -> list[dict]:
    """
    Combine H023 (suffix stripping) with H001 (layered cipher).
    Strip suffixes, then try Vigenere on the stems.
    """
    SUFFIXES = {"y", "n", "l", "r"}
    stripped = []
    for w in words:
        if len(w) > 2 and w[-1] in SUFFIXES:
            stripped.append(w[:-1])
        else:
            stripped.append(w)

    strip_glyphs = extract_glyph_stream(stripped)

    # Run Vigenere on stripped text
    return attack_vigenere(strip_glyphs, stripped)


def _strip_to_stems(words: list[str]) -> list[str]:
    """Aggressive morphological suffix strip."""
    SUFFIXES_1 = {"y", "n", "l", "r"}
    SUFFIXES_M = ["aiin", "ain", "air", "dy", "ey", "in", "ol", "ar", "or", "al", "an"]
    stems = []
    for w in words:
        s = w
        for suf in sorted(SUFFIXES_M, key=len, reverse=True):
            if len(s) > len(suf) + 1 and s.endswith(suf):
                s = s[:-len(suf)]
                break
        if len(s) > 2 and s[-1] in SUFFIXES_1:
            s = s[:-1]
        stems.append(s)
    return stems


def attack_stem_crack(corpus: dict, section: str = "biological") -> list[dict]:
    """
    Core stem-cracking attack. Builds a substitution table from stripped stems
    in one section, then tests whether it generalises to other sections.

    The biological section has IC=0.100 after stripping (above natural language),
    suggesting a simple monoalphabetic substitution on stems. Crack it there,
    then validate on text-only and herbal.
    """
    source_words = extract_words(corpus, section=section)
    if not source_words:
        return []

    source_stems = _strip_to_stems(source_words)
    source_glyphs = extract_glyph_stream(source_stems)

    results = []

    for target_freq, lang in [(LATIN_FREQ, "latin"), (ITALIAN_FREQ, "italian")]:
        # Build mapping from source section stems
        gf = Counter(source_glyphs)
        sorted_g = [g for g, _ in gf.most_common()]
        sorted_t = sorted(target_freq.keys(), key=lambda k: -target_freq[k])
        mapping = {g: sorted_t[i] if i < len(sorted_t) else "?"
                   for i, g in enumerate(sorted_g)}

        # Score on source section
        dec_stream = "".join(mapping.get(g, "?") for g in source_glyphs)
        dec_words = reconstruct_words(dec_stream, source_stems)
        source_score = score_plaintext(dec_stream, dec_words)

        results.append({
            "method": f"stem_crack_{section}_self_{lang}",
            "source": section,
            "target": section,
            "mapping": mapping,
            "sample_output": " ".join(dec_words[:30]),
            "sample_words": dec_words[:50],
            "score": source_score,
        })

        # Test generalisation to other sections
        for test_section in ["text-only", "herbal", "recipes", "pharmaceutical"]:
            if test_section == section:
                continue
            test_words = extract_words(corpus, section=test_section)
            if not test_words:
                continue

            test_stems = _strip_to_stems(test_words)
            test_glyphs = extract_glyph_stream(test_stems)

            # Apply SAME mapping from source section
            dec_test = "".join(mapping.get(g, "?") for g in test_glyphs)
            dec_test_words = reconstruct_words(dec_test, test_stems)
            test_score = score_plaintext(dec_test, dec_test_words)

            # Also build a LOCAL mapping for comparison
            local_gf = Counter(test_glyphs)
            local_sorted = [g for g, _ in local_gf.most_common()]
            local_mapping = {g: sorted_t[i] if i < len(sorted_t) else "?"
                            for i, g in enumerate(local_sorted)}
            dec_local = "".join(local_mapping.get(g, "?") for g in test_glyphs)
            dec_local_words = reconstruct_words(dec_local, test_stems)
            local_score = score_plaintext(dec_local, dec_local_words)

            # How much does the transferred mapping lose vs local?
            transfer_loss = local_score["best_score"] - test_score["best_score"]

            results.append({
                "method": f"stem_crack_{section}_to_{test_section}_{lang}",
                "source": section,
                "target": test_section,
                "transfer_score": test_score["best_score"],
                "local_score": local_score["best_score"],
                "transfer_loss": round(transfer_loss, 4),
                "generalises": transfer_loss < 0.05,
                "sample_output": " ".join(dec_test_words[:25]),
                "score": test_score,
            })

    results.sort(key=lambda r: -r["score"]["best_score"])
    return results


def attack_stem_bigram_chain(corpus: dict, section: str = "biological") -> dict:
    """
    Analyse bigram transition probabilities in stripped stems.
    High IC after stripping suggests ordered structure in stems.
    Map the most probable stem bigrams to Latin's most common bigrams.
    """
    words = extract_words(corpus, section=section)
    if not words:
        return {"method": "stem_bigram_chain", "score": {"best_score": 0}}

    stems = _strip_to_stems(words)
    stem_glyphs = extract_glyph_stream(stems)

    # Build bigram frequency table
    bigrams = Counter()
    for i in range(len(stem_glyphs) - 1):
        bigrams[(stem_glyphs[i], stem_glyphs[i+1])] += 1

    total_bi = sum(bigrams.values())
    top_bi = bigrams.most_common(30)

    # Compare with Latin bigrams
    latin_top_bi = [
        ("e", "t"), ("i", "n"), ("u", "s"), ("e", "s"), ("i", "s"),
        ("u", "m"), ("e", "r"), ("a", "t"), ("e", "n"), ("t", "i"),
        ("r", "e"), ("a", "n"), ("n", "t"), ("o", "r"), ("t", "e"),
        ("i", "t"), ("a", "r"), ("e", "m"), ("o", "n"), ("a", "m"),
    ]

    # Build mapping from top Voynich stem bigrams to Latin bigrams
    bi_mapping = {}
    char_votes = {}  # Track which Latin chars each glyph votes for
    for i, ((g1, g2), count) in enumerate(top_bi):
        if i < len(latin_top_bi):
            l1, l2 = latin_top_bi[i]
            # Vote for glyph->letter mappings
            for glyph, letter in [(g1, l1), (g2, l2)]:
                if glyph not in char_votes:
                    char_votes[glyph] = Counter()
                char_votes[glyph][letter] += count

    # Resolve votes: each glyph maps to its most-voted letter
    bigram_derived_mapping = {}
    used_letters = set()
    for glyph in sorted(char_votes.keys(), key=lambda g: -sum(char_votes[g].values())):
        for letter, votes in char_votes[glyph].most_common():
            if letter not in used_letters:
                bigram_derived_mapping[glyph] = letter
                used_letters.add(letter)
                break

    # Apply bigram-derived mapping
    dec_stream = "".join(bigram_derived_mapping.get(g, "?") for g in stem_glyphs)
    dec_words = reconstruct_words(dec_stream, stems)
    score = score_plaintext(dec_stream, dec_words)

    return {
        "method": f"stem_bigram_chain_{section}",
        "section": section,
        "mapping": bigram_derived_mapping,
        "top_voynich_bigrams": [(f"{g1}{g2}", count) for (g1, g2), count in top_bi[:15]],
        "latin_bigram_targets": ["".join(b) for b in latin_top_bi[:15]],
        "sample_output": " ".join(dec_words[:30]),
        "sample_words": dec_words[:50],
        "score": score,
    }


# =====================================================================
#  RUN ALL ATTACKS
# =====================================================================

def run_all_attacks(corpus: dict, stats: dict,
                    section: str | None = None,
                    folio: str | None = None) -> list[dict]:
    """Run all 22 cipher attacks and return ranked results."""
    words = extract_words(corpus, section=section, folio=folio)
    if not words:
        return [{"error": f"No words found for section={section}, folio={folio}"}]

    glyphs = extract_glyph_stream(words)
    print(f"[decrypt] Working with {len(words)} words, {len(glyphs)} glyphs")
    print(f"[decrypt] Unique glyphs: {len(set(glyphs))}")

    results = []

    # === SUBSTITUTION FAMILY ===
    print("[decrypt] [1/22] Frequency substitution (Latin)...")
    results.append(attack_frequency_substitution(glyphs, words, LATIN_FREQ, "latin"))

    print("[decrypt] [2/22] Frequency substitution (Italian)...")
    results.append(attack_frequency_substitution(glyphs, words, ITALIAN_FREQ, "italian"))

    print("[decrypt] [3/22] Caesar shifts...")
    results.extend(attack_caesar_shift(glyphs, words))

    print("[decrypt] [4/22] Bigram substitution...")
    results.append(attack_bigram_substitution(glyphs, words))

    print("[decrypt] [5/22] Homophonic substitution...")
    results.append(attack_homophonic_substitution(glyphs, words))

    print("[decrypt] [6/22] Affine cipher...")
    results.extend(attack_affine_cipher(glyphs, words))

    # === POLYALPHABETIC FAMILY ===
    print("[decrypt] [7/22] Vigenere (Kasiski + IC detection)...")
    results.extend(attack_vigenere(glyphs, words))

    print("[decrypt] [8/22] Beaufort cipher...")
    results.extend(attack_beaufort(glyphs, words))

    print("[decrypt] [9/22] Autokey cipher...")
    results.extend(attack_autokey(glyphs, words))

    # === TRANSPOSITION FAMILY ===
    print("[decrypt] [10/22] Reverse transposition...")
    results.append(attack_reverse_transposition(words))

    print("[decrypt] [11/22] Columnar transposition...")
    results.extend(attack_columnar_transposition(words))

    print("[decrypt] [12/22] Rail fence cipher...")
    results.extend(attack_rail_fence(glyphs, words))

    print("[decrypt] [13/22] Scytale / strip cipher...")
    results.extend(attack_scytale(glyphs, words))

    print("[decrypt] [14/22] Route cipher (spiral)...")
    results.extend(attack_route_cipher(glyphs, words))

    # === COMBINED / LAYERED ===
    print("[decrypt] [15/22] Substitution + transposition combined...")
    results.extend(attack_sub_then_transpose(glyphs, words))

    # === STRUCTURAL / ENCODING ===
    print("[decrypt] [16/22] Null cipher extraction...")
    results.extend(attack_null_cipher(glyphs, words))

    print("[decrypt] [17/22] Steganographic extraction...")
    results.extend(attack_steganographic(words))

    print("[decrypt] [18/22] Syllabic encoding...")
    results.append(attack_syllabic_encoding(glyphs, words))

    print("[decrypt] [19/22] Verbose cipher (multi-glyph per letter)...")
    results.extend(attack_verbose_cipher(glyphs, words))

    print("[decrypt] [20/22] Word-level codebook (honest scoring)...")
    results.append(attack_word_codebook(words))

    print("[decrypt] [20b/22] Medical Latin codebook...")
    results.append(attack_medical_codebook(words))

    # === ANALYTICAL ===
    print("[decrypt] [21/22] Index of Coincidence analysis...")
    results.append(attack_ic_analysis(glyphs, words, stats))

    print("[decrypt] [22/22] Vowel/consonant pattern analysis...")
    results.append(attack_vowel_consonant_pattern(words, stats))

    # === BONUS ANALYTICAL (full corpus) ===
    print("[decrypt] [+1] Currier A/B split analysis...")
    results.append(attack_currier_split(corpus, stats))

    print("[decrypt] [+2] Word grammar / slot structure analysis...")
    results.append(attack_word_grammar(words, stats))

    print("[decrypt] [+3] Multi-scale entropy layers...")
    results.append(attack_entropy_layers(corpus))

    # === HYPOTHESIS-DRIVEN TARGETED ATTACKS ===
    print("[decrypt] [H023] Morphological suffix stripping...")
    results.extend(attack_morphological_strip(words))

    print("[decrypt] [H020] Homophonic glyph reduction...")
    results.extend(attack_homophonic_reduction(glyphs, words))

    print("[decrypt] [H027] Section-comparative substitution...")
    results.extend(attack_section_comparative(corpus, stats))

    print("[decrypt] [H021] Currier A/B parallel attack...")
    results.extend(attack_currier_parallel(corpus))

    print("[decrypt] [H027] Text-only Rosetta stone transfer...")
    results.extend(attack_text_only_rosetta(corpus, stats))

    print("[decrypt] [H023+H001] Morpho-strip then Vigenere...")
    results.extend(attack_morpho_then_vigenere(glyphs, words))

    # === STEM CRACK (biological section focus) ===
    print("[decrypt] [STEM] Stem-crack: biological -> generalise...")
    results.extend(attack_stem_crack(corpus, section="biological"))

    print("[decrypt] [STEM] Stem bigram chain analysis...")
    results.append(attack_stem_bigram_chain(corpus, section="biological"))

    # Also crack from text-only for comparison
    print("[decrypt] [STEM] Stem-crack: text-only -> generalise...")
    results.extend(attack_stem_crack(corpus, section="text-only"))

    # Sort by best score
    results.sort(key=lambda r: -r.get("score", {}).get("best_score", 0))

    return results


def main():
    parser = argparse.ArgumentParser(description="Brain-V decryption engine")
    parser.add_argument("--section", type=str, default="biological",
                        help="Section to target (biological/text-only/herbal/astronomical/etc)")
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
    print(f"[decrypt] === Brain-V Decryption Engine v3 ===")
    print(f"[decrypt] Target: {target}")
    print(f"[decrypt] Attack suite: 22 cipher + 3 analytical + 6 hypothesis-driven\n")

    results = run_all_attacks(
        corpus, stats,
        section=None if args.folio else args.section,
        folio=args.folio,
    )

    # Print results
    print(f"\n{'='*60}")
    print(f"  DECRYPTION RESULTS — ranked by score ({len(results)} attacks)")
    print(f"{'='*60}\n")

    for i, r in enumerate(results, 1):
        method = r.get("method", "unknown")
        score = r.get("score", {})
        best = score.get("best_score", 0)
        lang = score.get("best_language", "?")
        details = score.get("details", "")

        marker = "***" if best > 0.5 else "**" if best > 0.3 else ""
        print(f"  {i:2d}. {marker}{method}{marker}")
        print(f"      Score: {best:.4f} ({lang})")
        print(f"      {details[:140]}")

        sample = r.get("sample_output", "")
        if sample:
            print(f"      Sample: {sample[:100]}")
        print()

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result_file = {
        "date": today,
        "target": target,
        "section": args.section,
        "folio": args.folio,
        "engine_version": 3,
        "attacks": len(results),
        "best_method": results[0].get("method", "none") if results else "none",
        "best_score": results[0].get("score", {}).get("best_score", 0) if results else 0,
        "results": results,
    }

    out_path = RESULTS_DIR / f"{today}-{target}.json"
    out_path.write_text(json.dumps(result_file, indent=2, default=str), encoding="utf-8")
    print(f"[decrypt] Results saved to {out_path}")

    # Summary
    top3 = results[:3]
    print(f"\n[decrypt] === TOP 3 ===")
    for i, r in enumerate(top3, 1):
        s = r.get("score", {})
        print(f"  {i}. {r.get('method', '?')}: {s.get('best_score', 0):.4f} ({s.get('best_language', '?')})")

    best = results[0] if results else None
    if best:
        bs = best.get("score", {}).get("best_score", 0)
        if bs > 0.6:
            print(f"\n[decrypt] *** STRONG SIGNAL: {best['method']} scored {bs:.4f} ***")
            print(f"[decrypt] This warrants focused investigation and refinement.")
        elif bs > 0.4:
            print(f"\n[decrypt] ** MODERATE SIGNAL from {best['method']} ({bs:.4f})")
        else:
            print(f"\n[decrypt] No strong signals. Best: {best['method']} ({bs:.4f})")

    return results


if __name__ == "__main__":
    main()
