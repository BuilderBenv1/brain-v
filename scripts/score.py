"""
score.py — Brain-V's scoring/learning layer

Tests each active hypothesis against the Voynich corpus statistics.
Updates hypothesis confidence, beliefs, and computes progress metrics.

Unlike Brain (which compares predictions vs new data), Brain-V scores
immediately — the corpus is static, the tests are against existing stats.

Usage:
    python scripts/score.py                        # score and update locally
    python scripts/score.py --push                 # also push to AgentOS
"""

import argparse
import json
import math
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATS_PATH = PROJECT_ROOT / "raw" / "perception" / "voynich-stats.json"
CORPUS_PATH = PROJECT_ROOT / "raw" / "perception" / "voynich-corpus.json"
HYPOTHESES_DIR = PROJECT_ROOT / "hypotheses"
BELIEFS_PATH = PROJECT_ROOT / "scripts" / "beliefs.json"
SCORES_DIR = PROJECT_ROOT / "outputs" / "scores"
OLLAMA_URL = "http://localhost:11434/api/generate"
AGENTOS_URL = "https://agentos-backend-production.up.railway.app"
# Brain-V agents on SKALE
ORCHESTRATOR_ID = 471
SCORER_ID = 474
MASTER_AGENT_ID = ORCHESTRATOR_ID
MODEL = "llama3.1:8b"

# --- Reference language profiles (medieval Latin and 15th-century Italian) ---
# These are approximate values from published linguistic studies.
REFERENCE_PROFILES = {
    "latin": {
        "glyph_entropy": 4.0,
        "avg_word_length": 5.5,
        "zipf_exponent": 1.0,
        "common_endings": ["us", "um", "is", "em", "ae", "am", "os", "as", "es", "et"],
        "common_initials": ["a", "c", "d", "e", "i", "p", "q", "s"],
        "hapax_ratio": 0.50,
        "vowel_ratio": 0.45,
    },
    "italian": {
        "glyph_entropy": 3.95,
        "avg_word_length": 4.8,
        "zipf_exponent": 1.05,
        "common_endings": ["a", "e", "i", "o", "re", "to", "te", "no", "le", "ne"],
        "common_initials": ["a", "c", "d", "e", "i", "l", "p", "s"],
        "hapax_ratio": 0.45,
        "vowel_ratio": 0.48,
    },
}


def load_stats() -> dict:
    return json.loads(STATS_PATH.read_text(encoding="utf-8"))


def load_corpus() -> dict:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def load_hypotheses() -> list[dict]:
    """Load all active hypothesis files."""
    hypotheses = []
    for path in sorted(HYPOTHESES_DIR.glob("*.json")):
        try:
            h = json.loads(path.read_text(encoding="utf-8"))
            if h.get("status") == "active":
                hypotheses.append(h)
        except json.JSONDecodeError:
            continue
    return hypotheses


def load_beliefs() -> list[dict]:
    if BELIEFS_PATH.exists():
        return json.loads(BELIEFS_PATH.read_text(encoding="utf-8"))
    return []


def save_hypothesis(hypothesis: dict):
    """Save updated hypothesis back to file."""
    path = HYPOTHESES_DIR / f"{hypothesis['id']}.json"
    path.write_text(json.dumps(hypothesis, indent=2), encoding="utf-8")


def run_statistical_test(hypothesis: dict, stats: dict, corpus: dict) -> dict:
    """
    Run the appropriate statistical test for a hypothesis.
    Returns a test result dict with score, details, and pass/fail.
    """
    htype = hypothesis.get("type", "unknown")
    test = hypothesis.get("test", "").lower()
    test_metric = hypothesis.get("test_metric", "").lower()

    result = {
        "test_name": test[:100],
        "score": 0.5,  # neutral default
        "details": "",
        "passed": None,  # True/False/None
    }

    s = stats["summary"]
    e = stats["entropy"]
    z = stats["zipf"]

    # --- Entropy-based tests ---
    if "entropy" in test or "entropy" in test_metric:
        observed = e["glyph_entropy_overall"]
        if "latin" in test.lower() or "latin" in hypothesis.get("claim", "").lower():
            expected = REFERENCE_PROFILES["latin"]["glyph_entropy"]
        elif "italian" in test.lower() or "italian" in hypothesis.get("claim", "").lower():
            expected = REFERENCE_PROFILES["italian"]["glyph_entropy"]
        else:
            expected = 4.0  # generic natural language

        diff = abs(observed - expected)
        # Score: 1.0 if perfect match, decreasing with distance
        result["score"] = max(0, 1.0 - diff / 2.0)
        result["details"] = (
            f"Observed glyph entropy: {observed:.4f} bits. "
            f"Expected for hypothesis: ~{expected:.1f} bits. "
            f"Difference: {diff:.4f} bits."
        )
        result["passed"] = diff < 0.3

    # --- Zipf's law tests ---
    elif "zipf" in test or "zipf" in test_metric:
        observed_exp = z["exponent"]
        observed_r2 = z["r_squared"]
        expected_exp = 1.0  # natural language

        diff = abs(observed_exp - expected_exp)
        result["score"] = observed_r2 * max(0, 1.0 - diff / 0.5)
        result["details"] = (
            f"Observed Zipf exponent: {observed_exp:.4f} (R²={observed_r2:.4f}). "
            f"Natural language expected: ~1.0. "
            f"Fit quality: {'good' if observed_r2 > 0.95 else 'moderate' if observed_r2 > 0.90 else 'weak'}."
        )
        result["passed"] = observed_r2 > 0.90 and diff < 0.2

    # --- Positional glyph constraint tests ---
    elif "position" in test or "slot" in test or "positional" in test_metric:
        pos = stats["glyph_frequency"]["positional"]
        first_set = set(list(pos.get("first", {}).keys())[:10])
        middle_set = set(list(pos.get("middle", {}).keys())[:10])
        last_set = set(list(pos.get("last", {}).keys())[:10])

        # Measure how distinct positional distributions are
        first_only = first_set - middle_set - last_set
        last_only = last_set - middle_set - first_set
        overlap = first_set & middle_set & last_set

        distinctness = (len(first_only) + len(last_only)) / max(1, len(first_set | middle_set | last_set))
        result["score"] = distinctness
        result["details"] = (
            f"Positional distinctness: {distinctness:.2f}. "
            f"First-only glyphs: {first_only}. "
            f"Last-only glyphs: {last_only}. "
            f"Universal glyphs: {overlap}. "
            f"Strong positional constraints suggest cipher structure over grammar."
        )
        result["passed"] = distinctness > 0.2

    # --- Currier A/B split tests ---
    elif "currier" in test or "language a" in test or "language b" in test:
        lang_stats = stats["entropy"]["by_language"]
        a_stats = lang_stats.get("A", {})
        b_stats = lang_stats.get("B", {})

        if a_stats and b_stats:
            entropy_diff = abs(a_stats.get("glyph_entropy", 0) - b_stats.get("glyph_entropy", 0))
            a_unique = a_stats.get("unique_words", 0)
            b_unique = b_stats.get("unique_words", 0)
            a_total = a_stats.get("word_count", 1)
            b_total = b_stats.get("word_count", 1)

            # Vocabulary overlap
            # (we'd need the actual word lists for precise overlap — use proxy)
            vocab_density_a = a_unique / a_total if a_total else 0
            vocab_density_b = b_unique / b_total if b_total else 0
            density_diff = abs(vocab_density_a - vocab_density_b)

            result["score"] = min(1.0, entropy_diff * 5 + density_diff * 10)
            result["details"] = (
                f"Language A: entropy={a_stats.get('glyph_entropy', '?')}, "
                f"{a_unique} unique/{a_total} total words. "
                f"Language B: entropy={b_stats.get('glyph_entropy', '?')}, "
                f"{b_unique} unique/{b_total} total words. "
                f"Entropy difference: {entropy_diff:.4f}. "
                f"Vocabulary density difference: {density_diff:.4f}."
            )
            result["passed"] = entropy_diff > 0.05 or density_diff > 0.02
        else:
            result["details"] = "Insufficient language data for A/B comparison."
            result["score"] = 0.5

    # --- Hapax ratio tests ---
    elif "hapax" in test or "hapax" in test_metric:
        observed = s["hapax_ratio"]
        if "latin" in hypothesis.get("claim", "").lower():
            expected = REFERENCE_PROFILES["latin"]["hapax_ratio"]
        elif "italian" in hypothesis.get("claim", "").lower():
            expected = REFERENCE_PROFILES["italian"]["hapax_ratio"]
        else:
            expected = 0.50

        diff = abs(observed - expected)
        result["score"] = max(0, 1.0 - diff * 3)
        result["details"] = (
            f"Observed hapax ratio: {observed:.3f}. "
            f"Expected: ~{expected:.2f}. "
            f"Voynich has unusually high hapax ratio ({observed:.1%}), "
            f"suggesting either large vocabulary, verbose encoding, or noise."
        )
        result["passed"] = diff < 0.15

    # --- Word length distribution tests ---
    elif "word length" in test or "word_length" in test_metric:
        observed_avg = s["avg_word_length"]
        if "latin" in hypothesis.get("claim", "").lower():
            expected = REFERENCE_PROFILES["latin"]["avg_word_length"]
        elif "italian" in hypothesis.get("claim", "").lower():
            expected = REFERENCE_PROFILES["italian"]["avg_word_length"]
        else:
            expected = 5.0

        diff = abs(observed_avg - expected)
        result["score"] = max(0, 1.0 - diff / 2.0)
        result["details"] = (
            f"Observed avg word length: {observed_avg:.2f}. "
            f"Expected: ~{expected:.1f}. Difference: {diff:.2f}."
        )
        result["passed"] = diff < 0.5

    # --- Section consistency tests ---
    elif "section" in test or "illustration" in test:
        section_stats = stats["entropy"]["by_section"]
        entropies = [v.get("glyph_entropy", 0) for v in section_stats.values()]
        if entropies:
            mean_ent = sum(entropies) / len(entropies)
            variance = sum((e - mean_ent) ** 2 for e in entropies) / len(entropies)
            std_dev = math.sqrt(variance)
            result["score"] = 1.0 - min(1.0, std_dev * 10)
            result["details"] = (
                f"Section entropy std dev: {std_dev:.4f}. "
                f"Range: {min(entropies):.4f} - {max(entropies):.4f}. "
                f"{'Consistent' if std_dev < 0.05 else 'Variable'} across sections."
            )
            result["passed"] = std_dev < 0.1
        else:
            result["details"] = "No section data available."
            result["score"] = 0.5

    # --- Substitution cipher test (with actual decryption attempt) ---
    elif "substitution" in test or "cipher" in test_metric:
        n_glyphs = s["unique_glyphs"]
        ent = e["glyph_entropy_overall"]
        plausible = 20 <= n_glyphs <= 30
        entropy_match = 3.5 < ent < 4.5

        # Try actual decryption via decrypt.py
        decrypt_score = 0.0
        decrypt_details = ""
        try:
            from decrypt import run_all_attacks, load_corpus
            import json as _json
            stats_data = _json.loads(
                (PROJECT_ROOT / "raw" / "perception" / "voynich-stats.json").read_text()
            )
            corpus_data = load_corpus()
            attacks = run_all_attacks(corpus_data, stats_data, section="herbal")
            if attacks:
                best = attacks[0]
                decrypt_score = best.get("score", {}).get("best_score", 0)
                best_lang = best.get("score", {}).get("best_language", "?")
                freq_corr = best.get("score", {}).get(
                    f"{best_lang}_freq_correlation",
                    best.get("score", {}).get("latin_freq_correlation", 0)
                )
                decrypt_details = (
                    f"Best attack: {best.get('method', '?')} "
                    f"(score={decrypt_score:.4f}, lang={best_lang}, "
                    f"freq_corr={freq_corr:.3f}). "
                )
        except Exception as ex:
            decrypt_details = f"Decrypt attempt failed: {ex}. "

        # Combined score: structural compatibility + actual decryption result
        struct_score = (0.3 if plausible else 0.0) + (0.3 if entropy_match else 0.0)
        combined = struct_score + decrypt_score * 0.4

        result["score"] = min(1.0, combined)
        result["details"] = (
            f"Unique glyphs: {n_glyphs} (Latin ~23). "
            f"Entropy: {ent:.4f} bits. "
            f"Alphabet {'compatible' if plausible else 'incompatible'}. "
            f"{decrypt_details}"
        )
        result["passed"] = combined > 0.5

    # --- Fallback: use LLM to evaluate ---
    else:
        result = score_with_llm(hypothesis, stats)

    return result


def score_with_llm(hypothesis: dict, stats: dict) -> dict:
    """Fallback: ask the LLM to evaluate a hypothesis against the stats."""
    s = stats["summary"]
    e = stats["entropy"]
    z = stats["zipf"]

    prompt = f"""You are scoring a hypothesis about the Voynich Manuscript against its statistical profile.

Hypothesis: {hypothesis.get('claim', '')}
Type: {hypothesis.get('type', '')}
Test specified: {hypothesis.get('test', '')}

Key corpus statistics:
- {s['total_words']:,} words, {s['unique_words']:,} unique, 25 glyphs
- Glyph entropy: {e['glyph_entropy_overall']} bits
- Zipf exponent: {z['exponent']} (R²={z['r_squared']})
- Hapax ratio: {s['hapax_ratio']}
- Avg word length: {s['avg_word_length']}

Score this hypothesis:
- score: 0.0 (completely contradicted by stats) to 1.0 (strongly supported)
- passed: true if evidence supports it, false if contradicts, null if inconclusive
- details: one sentence explaining why

Respond with EXACTLY this JSON, nothing else:
{{"score": <0.0-1.0>, "passed": <true|false|null>, "details": "<explanation>"}}
JSON only."""

    try:
        body = json.dumps({
            "model": MODEL, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.1, "num_predict": 256},
        }).encode("utf-8")
        req = urllib.request.Request(
            OLLAMA_URL, data=body,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode("utf-8")).get("response", "")

        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(raw[start:end])
            return {
                "test_name": "llm_evaluation",
                "score": parsed.get("score", 0.5),
                "details": parsed.get("details", ""),
                "passed": parsed.get("passed"),
            }
    except Exception as ex:
        pass

    return {
        "test_name": "llm_evaluation_failed",
        "score": 0.5,
        "details": f"Could not evaluate: {hypothesis.get('test', 'no test specified')}",
        "passed": None,
    }


def update_hypothesis_confidence(hypothesis: dict, test_result: dict, date_str: str) -> dict:
    """Update hypothesis confidence based on test result."""
    old_conf = hypothesis["confidence"]
    score = test_result["score"]

    # Bayesian-ish update: move confidence toward score
    # Stronger moves when test clearly passes or fails
    if test_result["passed"] is True:
        new_conf = old_conf + (1.0 - old_conf) * 0.15 * score
    elif test_result["passed"] is False:
        new_conf = old_conf * (1.0 - 0.3 * (1.0 - score))
    else:
        # Inconclusive — small move toward score
        new_conf = old_conf + (score - old_conf) * 0.05

    new_conf = round(max(0.01, min(0.99, new_conf)), 3)

    hypothesis["confidence"] = new_conf
    hypothesis["last_tested"] = date_str
    hypothesis["tests_run"].append({
        "date": date_str,
        "test": test_result["test_name"],
        "score": test_result["score"],
        "passed": test_result["passed"],
        "details": test_result["details"],
        "confidence_change": f"{old_conf:.3f} -> {new_conf:.3f}",
    })

    # Move test from remaining to run
    if hypothesis["tests_remaining"]:
        hypothesis["tests_remaining"] = hypothesis["tests_remaining"][1:]

    # Eliminate if confidence drops below 0.05
    if new_conf < 0.05:
        hypothesis["status"] = "eliminated"

    return hypothesis


def update_beliefs(beliefs: list[dict], scored_hypotheses: list[dict], date_str: str) -> list[dict]:
    """Update beliefs based on hypothesis test results."""
    updated = list(beliefs)

    for h in scored_hypotheses:
        if not h.get("tests_run"):
            continue
        latest_test = h["tests_run"][-1]

        # Promote beliefs related to confirmed hypotheses
        if latest_test.get("passed") is True and h["confidence"] > 0.6:
            # Check if a related belief already exists
            claim = h.get("claim", "")
            already_exists = any(
                claim[:30].lower() in b.get("belief", "").lower()
                for b in updated
            )
            if not already_exists:
                updated.append({
                    "belief": f"Evidence supports: {claim[:100]}",
                    "confidence": h["confidence"],
                    "source": f"hypothesis-{h['id']}-{date_str}",
                    "date": date_str,
                })

        # Demote beliefs contradicted by failed hypotheses
        if latest_test.get("passed") is False:
            for b in updated:
                belief_text = b.get("belief", "").lower()
                claim_words = [w for w in h.get("claim", "").lower().split() if len(w) >= 5]
                if any(w in belief_text for w in claim_words[:3]):
                    old_conf = b.get("confidence", 0.5)
                    if isinstance(old_conf, (int, float)):
                        b["confidence"] = round(max(0.05, old_conf * 0.85), 3)
                        b["last_scored"] = date_str

    return updated


def compute_progress(scored: list[dict], all_hypotheses: list[dict]) -> dict:
    """Compute overall progress metrics."""
    active = [h for h in all_hypotheses if h.get("status") == "active"]
    eliminated = [h for h in all_hypotheses if h.get("status") == "eliminated"]
    high_confidence = [h for h in active if h.get("confidence", 0) > 0.8]

    # How much did the world model change this cycle?
    confidence_changes = []
    for h in scored:
        if h.get("tests_run"):
            latest = h["tests_run"][-1]
            change_str = latest.get("confidence_change", "0.5 -> 0.5")
            parts = change_str.split(" -> ")
            if len(parts) == 2:
                try:
                    old = float(parts[0])
                    new = float(parts[1])
                    confidence_changes.append(abs(new - old))
                except ValueError:
                    pass

    surprise = sum(confidence_changes) / max(1, len(confidence_changes))

    return {
        "total_hypotheses": len(all_hypotheses),
        "active": len(active),
        "eliminated": len(eliminated),
        "high_confidence": len(high_confidence),
        "high_confidence_ids": [h["id"] for h in high_confidence],
        "eliminated_this_cycle": sum(
            1 for h in scored if h.get("status") == "eliminated"
        ),
        "surprise": round(surprise, 4),
        "progress_summary": (
            f"{len(eliminated)} eliminated, {len(active)} active, "
            f"{len(high_confidence)} above 0.8 confidence"
        ),
    }


def push_to_agentos(beliefs: list[dict], cycle: int, date_str: str):
    context = {
        "context": {
            "beliefs": beliefs,
            "cycle": cycle,
            "domain": "voynich",
            "last_scored": date_str,
        },
        "description": f"Brain-V cycle {cycle} — post-score belief update {date_str}",
    }
    body = json.dumps(context).encode("utf-8")
    req = urllib.request.Request(
        f"{AGENTOS_URL}/api/agents/{MASTER_AGENT_ID}/save-context",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Brain-V scoring: test hypotheses against corpus")
    parser.add_argument("--push", action="store_true", help="Push updated beliefs to AgentOS")
    args = parser.parse_args()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[score] Scoring hypotheses for {today}...")

    # Load data
    if not STATS_PATH.exists():
        print("[score] ERROR: No stats file. Run perceive.py first.")
        return
    stats = load_stats()

    if not CORPUS_PATH.exists():
        print("[score] ERROR: No corpus file. Run perceive.py first.")
        return
    corpus = load_corpus()

    hypotheses = load_hypotheses()
    if not hypotheses:
        print("[score] No active hypotheses to score. Run predict.py first.")
        return
    print(f"[score] Scoring {len(hypotheses)} active hypotheses...")

    # Score each hypothesis
    scored = []
    for h in hypotheses:
        print(f"\n[score] Testing {h['id']}: {h['claim'][:60]}...")
        test_result = run_statistical_test(h, stats, corpus)
        print(f"  Score: {test_result['score']:.2f} | Passed: {test_result['passed']}")
        print(f"  {test_result['details'][:120]}")

        h = update_hypothesis_confidence(h, test_result, today)
        save_hypothesis(h)
        scored.append(h)
        print(f"  Confidence: {h['confidence']:.3f} | Status: {h['status']}")

    # Load all hypotheses (including eliminated) for progress
    all_hyps = []
    for path in sorted(HYPOTHESES_DIR.glob("*.json")):
        try:
            all_hyps.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue

    progress = compute_progress(scored, all_hyps)
    print(f"\n[score] === Progress ===")
    print(f"  {progress['progress_summary']}")
    print(f"  Surprise: {progress['surprise']:.4f}")

    # Update beliefs
    beliefs = load_beliefs()
    updated_beliefs = update_beliefs(beliefs, scored, today)
    BELIEFS_PATH.write_text(json.dumps(updated_beliefs, indent=2), encoding="utf-8")
    print(f"[score] Beliefs: {len(beliefs)} -> {len(updated_beliefs)}")

    # Save score record
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    score_record = {
        "date": today,
        "hypotheses_scored": len(scored),
        "progress": progress,
        "scored_hypotheses": [
            {
                "id": h["id"],
                "claim": h["claim"][:100],
                "confidence": h["confidence"],
                "status": h["status"],
                "test_result": h["tests_run"][-1] if h.get("tests_run") else None,
            }
            for h in scored
        ],
        "belief_count_before": len(beliefs),
        "belief_count_after": len(updated_beliefs),
    }

    score_path = SCORES_DIR / f"{today}.json"
    if score_path.exists():
        cycle = 2
        while (SCORES_DIR / f"{today}-cycle{cycle}.json").exists():
            cycle += 1
        score_path = SCORES_DIR / f"{today}-cycle{cycle}.json"

    score_path.write_text(json.dumps(score_record, indent=2), encoding="utf-8")
    print(f"[score] Score record saved to {score_path}")

    # Push to AgentOS
    if args.push:
        agentos_result = push_to_agentos(updated_beliefs, len(all_hyps), today)
        print(f"[score] Pushed to AgentOS: IPFS={agentos_result.get('ipfs_hash')}")

    return score_record


if __name__ == "__main__":
    main()
