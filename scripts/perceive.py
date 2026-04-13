"""
perceive.py — Brain-V's perception layer

Parses the Voynich Manuscript EVA transliteration (IVTFF format) into a
structured dataset and computes a comprehensive statistical profile.

Source: ZL3b-n.txt (Zandbergen transliteration, voynich.nu)

Usage:
    python scripts/perceive.py              # parse and compute stats locally
    python scripts/perceive.py --push       # also push to AgentOS
    python scripts/perceive.py --report     # also write baseline-statistics.md
"""

import argparse
import hashlib
import json
import math
import re
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "raw" / "corpus"
OUTPUT_DIR = PROJECT_ROOT / "raw" / "perception"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
AGENTOS_URL = "https://agentos-backend-production.up.railway.app"
# Brain-V agents on SKALE (registered via agentproof.sh)
ORCHESTRATOR_ID = 471
PERCEIVER_ID = 472
PREDICTOR_ID = 473
SCORER_ID = 474
SCHEDULER_ID = 475
DREAMER_ID = 477
PERCEPTION_AGENT_ID = PERCEIVER_ID

# IVTFF source file (Zandbergen transliteration — most complete)
IVTFF_FILE = CORPUS_DIR / "ZL3b-n.txt"

# Illustration type codes from IVTFF $I= field
SECTION_NAMES = {
    "H": "herbal",
    "A": "astronomical",
    "B": "biological",
    "C": "cosmological",
    "P": "pharmaceutical",
    "S": "recipes",
    "T": "text-only",
    "Z": "zodiac",
}


def parse_ivtff(filepath: Path) -> dict:
    """Parse IVTFF format file into structured corpus data."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    folios = []
    current_folio = None
    current_lines = []
    current_meta = {}

    for line in lines:
        line = line.rstrip()

        # Skip comments
        if line.startswith("#"):
            continue

        # Folio header: <f1r> <! $Q=A $P=A ...>
        header_match = re.match(r"<(f\d+[rv]\d*)>\s+<!\s+(.*?)>", line)
        if header_match:
            # Save previous folio
            if current_folio and current_lines:
                folios.append({
                    "folio": current_folio,
                    "meta": current_meta,
                    "lines": current_lines,
                })
            current_folio = header_match.group(1)
            meta_str = header_match.group(2)
            current_meta = {}
            for m in re.finditer(r"\$(\w+)=(\S+)", meta_str):
                current_meta[m.group(1)] = m.group(2)
            current_lines = []
            continue

        # Text line: <f1r.1,@P0> fachys.ykal.ar...
        text_match = re.match(r"<([^>]+)>\s+(.*)", line)
        if text_match and current_folio:
            locus = text_match.group(1)
            raw_text = text_match.group(2).strip()

            # Clean the text: remove inline comments, special markers
            clean = raw_text
            clean = re.sub(r"<!.*?>", "", clean)      # inline comments
            clean = re.sub(r"<%>", "", clean)          # paragraph marks
            clean = re.sub(r"<\$>", "", clean)         # end marks
            clean = re.sub(r"<->", "", clean)          # deletion marks
            clean = re.sub(r"@\d+;", "", clean)        # special glyph refs
            clean = re.sub(r"\{[^}]*\}", "", clean)    # uncertain readings
            clean = re.sub(r"\[[^\]]*\]", "", clean)   # alternative readings
            clean = re.sub(r"[{}()\[\]]", "", clean)   # stray brackets
            clean = clean.strip()

            if not clean:
                continue

            # Split into words (. is word separator in EVA, , is sub-word)
            words = []
            for token in clean.replace(",", ".").split("."):
                token = token.strip()
                if token and re.match(r"^[a-z]+$", token):
                    words.append(token)

            if words:
                current_lines.append({
                    "locus": locus,
                    "raw": raw_text,
                    "words": words,
                })

    # Don't forget last folio
    if current_folio and current_lines:
        folios.append({
            "folio": current_folio,
            "meta": current_meta,
            "lines": current_lines,
        })

    # Build structured corpus
    corpus = {
        "source": filepath.name,
        "parse_date": datetime.now(timezone.utc).isoformat(),
        "folio_count": len(folios),
        "folios": [],
    }

    for f in folios:
        lang = f["meta"].get("L", "?")
        section_code = f["meta"].get("I", "?")
        section = SECTION_NAMES.get(section_code, "unknown")
        quire = f["meta"].get("Q", "?")

        all_words = []
        line_data = []
        for ln in f["lines"]:
            all_words.extend(ln["words"])
            line_data.append({
                "locus": ln["locus"],
                "words": ln["words"],
                "word_count": len(ln["words"]),
            })

        corpus["folios"].append({
            "folio": f["folio"],
            "quire": quire,
            "currier_language": lang,
            "section": section,
            "section_code": section_code,
            "line_count": len(line_data),
            "word_count": len(all_words),
            "lines": line_data,
        })

    return corpus


def compute_stats(corpus: dict) -> dict:
    """Compute comprehensive statistical profile of the corpus."""
    all_words = []
    all_glyphs = []
    words_by_section = {}
    words_by_language = {}
    glyphs_by_position = {"first": [], "middle": [], "last": []}

    for folio in corpus["folios"]:
        section = folio["section"]
        lang = folio["currier_language"]

        for line in folio["lines"]:
            for word in line["words"]:
                all_words.append(word)
                words_by_section.setdefault(section, []).append(word)
                words_by_language.setdefault(lang, []).append(word)

                glyphs = list(word)
                all_glyphs.extend(glyphs)

                if len(glyphs) >= 1:
                    glyphs_by_position["first"].append(glyphs[0])
                if len(glyphs) >= 2:
                    glyphs_by_position["last"].append(glyphs[-1])
                if len(glyphs) >= 3:
                    for g in glyphs[1:-1]:
                        glyphs_by_position["middle"].append(g)

    # --- Word statistics ---
    word_freq = Counter(all_words)
    total_words = len(all_words)
    unique_words = len(word_freq)
    word_lengths = [len(w) for w in all_words]
    avg_word_length = sum(word_lengths) / total_words if total_words else 0

    # Word length distribution
    length_dist = Counter(word_lengths)

    # --- Glyph statistics ---
    glyph_freq = Counter(all_glyphs)
    total_glyphs = len(all_glyphs)
    unique_glyphs = len(glyph_freq)

    # Positional glyph frequencies
    pos_freq = {
        pos: dict(Counter(gs).most_common())
        for pos, gs in glyphs_by_position.items()
    }

    # --- Shannon entropy ---
    def shannon_entropy(freq_counter: Counter) -> float:
        total = sum(freq_counter.values())
        if total == 0:
            return 0.0
        entropy = 0.0
        for count in freq_counter.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    overall_entropy = shannon_entropy(glyph_freq)
    word_entropy = shannon_entropy(word_freq)

    # Per-section entropy
    section_entropy = {}
    for section, words in words_by_section.items():
        sec_glyphs = []
        for w in words:
            sec_glyphs.extend(list(w))
        section_entropy[section] = {
            "glyph_entropy": shannon_entropy(Counter(sec_glyphs)),
            "word_entropy": shannon_entropy(Counter(words)),
            "word_count": len(words),
            "unique_words": len(set(words)),
        }

    # Per-language entropy
    language_entropy = {}
    for lang, words in words_by_language.items():
        lang_glyphs = []
        for w in words:
            lang_glyphs.extend(list(w))
        language_entropy[lang] = {
            "glyph_entropy": shannon_entropy(Counter(lang_glyphs)),
            "word_entropy": shannon_entropy(Counter(words)),
            "word_count": len(words),
            "unique_words": len(set(words)),
        }

    # --- Bigram and trigram glyph frequencies ---
    bigrams = []
    trigrams = []
    for word in all_words:
        glyphs = list(word)
        for i in range(len(glyphs) - 1):
            bigrams.append(glyphs[i] + glyphs[i + 1])
        for i in range(len(glyphs) - 2):
            trigrams.append(glyphs[i] + glyphs[i + 1] + glyphs[i + 2])

    bigram_freq = Counter(bigrams)
    trigram_freq = Counter(trigrams)

    # --- Zipf's law fit ---
    ranked_freqs = sorted(word_freq.values(), reverse=True)
    if len(ranked_freqs) >= 10:
        log_ranks = [math.log(i + 1) for i in range(len(ranked_freqs))]
        log_freqs = [math.log(f) for f in ranked_freqs]
        n = len(log_ranks)
        sum_x = sum(log_ranks)
        sum_y = sum(log_freqs)
        sum_xy = sum(x * y for x, y in zip(log_ranks, log_freqs))
        sum_xx = sum(x * x for x in log_ranks)
        denom = n * sum_xx - sum_x * sum_x
        if denom != 0:
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in log_freqs)
            ss_res = sum(
                (y - (slope * x + intercept)) ** 2
                for x, y in zip(log_ranks, log_freqs)
            )
            r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else 0
            zipf_exponent = -slope
        else:
            zipf_exponent = 0
            r_squared = 0
    else:
        zipf_exponent = 0
        r_squared = 0

    # --- Hapax legomena ---
    hapax = sum(1 for w, c in word_freq.items() if c == 1)
    dis_legomena = sum(1 for w, c in word_freq.items() if c == 2)

    stats = {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "source": corpus["source"],
        "summary": {
            "total_folios": corpus["folio_count"],
            "total_words": total_words,
            "unique_words": unique_words,
            "total_glyphs": total_glyphs,
            "unique_glyphs": unique_glyphs,
            "avg_word_length": round(avg_word_length, 2),
            "hapax_legomena": hapax,
            "dis_legomena": dis_legomena,
            "hapax_ratio": round(hapax / unique_words, 3) if unique_words else 0,
        },
        "entropy": {
            "glyph_entropy_overall": round(overall_entropy, 4),
            "word_entropy_overall": round(word_entropy, 4),
            "by_section": {
                k: {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()}
                for k, v in section_entropy.items()
            },
            "by_language": {
                k: {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()}
                for k, v in language_entropy.items()
            },
        },
        "zipf": {
            "exponent": round(zipf_exponent, 4),
            "r_squared": round(r_squared, 4),
            "interpretation": (
                "strong Zipf fit" if r_squared > 0.95 else
                "moderate Zipf fit" if r_squared > 0.90 else
                "weak Zipf fit"
            ),
        },
        "word_frequency": {
            "top_50": dict(word_freq.most_common(50)),
            "length_distribution": {str(k): v for k, v in sorted(length_dist.items())},
        },
        "glyph_frequency": {
            "overall": dict(glyph_freq.most_common()),
            "positional": {
                pos: dict(Counter(gs).most_common(15))
                for pos, gs in glyphs_by_position.items()
            },
        },
        "ngrams": {
            "top_30_bigrams": dict(bigram_freq.most_common(30)),
            "top_30_trigrams": dict(trigram_freq.most_common(30)),
        },
        "sections": {
            section: {
                "folio_count": sum(
                    1 for f in corpus["folios"] if f["section"] == section
                ),
                "word_count": len(words),
                "unique_words": len(set(words)),
                "avg_word_length": round(
                    sum(len(w) for w in words) / len(words), 2
                ) if words else 0,
            }
            for section, words in words_by_section.items()
        },
        "languages": {
            lang: {
                "folio_count": sum(
                    1 for f in corpus["folios"] if f["currier_language"] == lang
                ),
                "word_count": len(words),
                "unique_words": len(set(words)),
            }
            for lang, words in words_by_language.items()
        },
    }

    return stats


def generate_report(stats: dict) -> str:
    """Generate a human-readable baseline statistics report."""
    s = stats["summary"]
    e = stats["entropy"]
    z = stats["zipf"]

    lines = [
        "# Brain-V Baseline Statistics Report",
        "",
        f"*Generated: {stats['computed_at']}*",
        f"*Source: {stats['source']}*",
        "",
        "## Corpus Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total folios | {s['total_folios']} |",
        f"| Total words | {s['total_words']:,} |",
        f"| Unique words | {s['unique_words']:,} |",
        f"| Total glyphs | {s['total_glyphs']:,} |",
        f"| Unique glyphs | {s['unique_glyphs']} |",
        f"| Avg word length | {s['avg_word_length']} |",
        f"| Hapax legomena | {s['hapax_legomena']:,} ({s['hapax_ratio']:.1%} of vocabulary) |",
        f"| Dis legomena | {s['dis_legomena']:,} |",
        "",
        "## Entropy",
        "",
        "| Scope | Glyph entropy | Word entropy |",
        "|---|---|---|",
        f"| Overall | {e['glyph_entropy_overall']} bits | {e['word_entropy_overall']} bits |",
    ]

    for section, se in sorted(e["by_section"].items()):
        lines.append(
            f"| Section: {section} | {se['glyph_entropy']} bits | {se['word_entropy']} bits |"
        )
    for lang, le in sorted(e["by_language"].items()):
        lines.append(
            f"| Language {lang} | {le['glyph_entropy']} bits | {le['word_entropy']} bits |"
        )

    lines.extend([
        "",
        "*Natural language comparison: English ~4.11 bits/char, Latin ~4.0 bits/char, "
        "Italian ~3.95 bits/char*",
        "",
        "## Zipf's Law",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Zipf exponent | {z['exponent']} |",
        f"| R-squared | {z['r_squared']} |",
        f"| Interpretation | {z['interpretation']} |",
        "",
        "*Natural language typically has Zipf exponent ~1.0 and R^2 > 0.95*",
        "",
        "## Top 20 Words",
        "",
        "| Rank | Word | Count | Frequency |",
        "|---|---|---|---|",
    ])

    total = s["total_words"]
    for i, (word, count) in enumerate(
        sorted(stats["word_frequency"]["top_50"].items(), key=lambda x: -x[1])[:20],
        1,
    ):
        lines.append(f"| {i} | {word} | {count:,} | {count/total:.3%} |")

    lines.extend([
        "",
        "## Section Breakdown",
        "",
        "| Section | Folios | Words | Unique | Avg len |",
        "|---|---|---|---|---|",
    ])
    for section, data in sorted(stats["sections"].items()):
        lines.append(
            f"| {section} | {data['folio_count']} | {data['word_count']:,} | "
            f"{data['unique_words']:,} | {data['avg_word_length']} |"
        )

    lines.extend([
        "",
        "## Currier Language Split",
        "",
        "| Language | Folios | Words | Unique |",
        "|---|---|---|---|",
    ])
    for lang, data in sorted(stats["languages"].items()):
        lines.append(
            f"| {lang} | {data['folio_count']} | {data['word_count']:,} | "
            f"{data['unique_words']:,} |"
        )

    lines.extend([
        "",
        "## Glyph Frequency (top 15)",
        "",
        "| Glyph | Count | Position preference |",
        "|---|---|---|",
    ])
    pos_data = stats["glyph_frequency"]["positional"]
    for glyph, count in sorted(
        stats["glyph_frequency"]["overall"].items(), key=lambda x: -x[1]
    )[:15]:
        pos_counts = {}
        for pos in ["first", "middle", "last"]:
            pos_counts[pos] = pos_data.get(pos, {}).get(glyph, 0)
        total_pos = sum(pos_counts.values()) or 1
        pref = max(pos_counts, key=pos_counts.get)
        pref_pct = pos_counts[pref] / total_pos
        lines.append(f"| {glyph} | {count:,} | {pref} ({pref_pct:.0%}) |")

    lines.extend([
        "",
        "---",
        "",
        "*This is Brain-V's first perception of the Voynich Manuscript.*",
        f"*Cycle 0 — baseline established {stats['computed_at'][:10]}*",
    ])

    return "\n".join(lines)


def file_hash(filepath: Path) -> str:
    """SHA-256 hash of a file for change detection."""
    return hashlib.sha256(filepath.read_bytes()).hexdigest()


def push_to_agentos(data: dict, description: str):
    """Push perception data to AgentOS."""
    context = {
        "context": data,
        "description": description,
    }
    body = json.dumps(context).encode("utf-8")
    req = urllib.request.Request(
        f"{AGENTOS_URL}/api/agents/{PERCEPTION_AGENT_ID}/save-context",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result


def main():
    parser = argparse.ArgumentParser(description="Brain-V perception: Voynich corpus parser")
    parser.add_argument("--push", action="store_true", help="Push to AgentOS")
    parser.add_argument("--report", action="store_true", help="Generate baseline report")
    args = parser.parse_args()

    if not IVTFF_FILE.exists():
        print(f"[perceive] ERROR: IVTFF file not found: {IVTFF_FILE}")
        print(f"[perceive] Download from voynich.nu/data/ZL3b-n.txt")
        return

    # Check if corpus has changed since last parse
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    corpus_path = OUTPUT_DIR / "voynich-corpus.json"
    stats_path = OUTPUT_DIR / "voynich-stats.json"
    hash_path = OUTPUT_DIR / ".corpus-hash"

    current_hash = file_hash(IVTFF_FILE)
    if hash_path.exists() and corpus_path.exists() and stats_path.exists():
        cached_hash = hash_path.read_text(encoding="utf-8").strip()
        if cached_hash == current_hash:
            print("[perceive] Corpus unchanged since last parse. Loading cached data.")
            stats = json.loads(stats_path.read_text(encoding="utf-8"))
            print(f"[perceive] {stats['summary']['total_words']:,} words, "
                  f"{stats['summary']['unique_words']:,} unique across "
                  f"{stats['summary']['total_folios']} folios.")
            if args.push:
                result = push_to_agentos(
                    {"corpus_hash": current_hash, "stats": stats},
                    f"Perception (cached) — {stats['summary']['total_words']} words",
                )
                print(f"[perceive] Pushed to AgentOS: IPFS={result.get('ipfs_hash')}")
            return stats

    print(f"[perceive] Parsing {IVTFF_FILE.name}...")

    # Parse corpus
    corpus = parse_ivtff(IVTFF_FILE)
    print(f"[perceive] Parsed {corpus['folio_count']} folios.")

    # Save corpus
    corpus_path.write_text(json.dumps(corpus, indent=2), encoding="utf-8")
    print(f"[perceive] Saved corpus to {corpus_path}")

    # Compute statistics
    print("[perceive] Computing statistical profile...")
    stats = compute_stats(corpus)

    stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"[perceive] Saved stats to {stats_path}")

    # Save hash for change detection
    hash_path.write_text(current_hash, encoding="utf-8")

    # Print summary
    s = stats["summary"]
    e = stats["entropy"]
    z = stats["zipf"]
    print(f"\n[perceive] === Voynich Corpus Profile ===")
    print(f"  Words: {s['total_words']:,} total, {s['unique_words']:,} unique")
    print(f"  Glyphs: {s['total_glyphs']:,} total, {s['unique_glyphs']} unique")
    print(f"  Avg word length: {s['avg_word_length']}")
    print(f"  Glyph entropy: {e['glyph_entropy_overall']} bits")
    print(f"  Word entropy: {e['word_entropy_overall']} bits")
    print(f"  Zipf exponent: {z['exponent']} (R²={z['r_squared']})")
    print(f"  Hapax legomena: {s['hapax_legomena']:,} ({s['hapax_ratio']:.1%})")

    # Generate report
    if args.report:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report = generate_report(stats)
        report_path = REPORTS_DIR / "baseline-statistics.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"[perceive] Report saved to {report_path}")

    # Push to AgentOS
    if args.push:
        result = push_to_agentos(
            {"corpus_hash": current_hash, "stats": stats},
            f"Perception cycle — {s['total_words']} words, {s['unique_words']} unique",
        )
        print(f"[perceive] Pushed to AgentOS: IPFS={result.get('ipfs_hash')}, v={result.get('version')}")

    return stats


if __name__ == "__main__":
    main()
