"""
predict.py — Brain-V's prediction layer

Loads current beliefs and statistical profile, then asks Claude (via CLI)
to generate or refine decipherment hypotheses about the Voynich Manuscript.

Each hypothesis must be testable against the corpus statistics.

Usage:
    python scripts/predict.py                     # uses local beliefs.json
    python scripts/predict.py --from-agentos      # loads beliefs from AgentOS
"""

import argparse
import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATS_PATH = PROJECT_ROOT / "raw" / "perception" / "voynich-stats.json"
PREDICTIONS_DIR = PROJECT_ROOT / "outputs" / "predictions"
HYPOTHESES_DIR = PROJECT_ROOT / "hypotheses"
BELIEFS_PATH = PROJECT_ROOT / "scripts" / "beliefs.json"
AGENTOS_URL = "https://agentos-backend-production.up.railway.app"
# Brain-V agents on SKALE
ORCHESTRATOR_ID = 471
PREDICTOR_ID = 473
MASTER_AGENT_ID = ORCHESTRATOR_ID
MODEL = "claude-code-cli"
CLAUDE_CLI = r"C:\Users\theka\AppData\Roaming\npm\claude.cmd"


def load_beliefs_local() -> list[dict]:
    if BELIEFS_PATH.exists():
        return json.loads(BELIEFS_PATH.read_text(encoding="utf-8"))
    return []


def load_beliefs_agentos() -> list[dict]:
    req = urllib.request.Request(
        f"{AGENTOS_URL}/api/agents/{MASTER_AGENT_ID}/load-context",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    ctx = data.get("context", {})
    if isinstance(ctx, dict) and "context" in ctx:
        ctx = ctx["context"]
    beliefs = ctx.get("beliefs", [])
    if not beliefs:
        print("[predict] WARNING: AgentOS returned 0 beliefs. Falling back to local.")
        beliefs = load_beliefs_local()
    return beliefs


def load_stats() -> dict | None:
    if STATS_PATH.exists():
        return json.loads(STATS_PATH.read_text(encoding="utf-8"))
    return None


def load_existing_hypotheses() -> list[dict]:
    """Load all existing hypothesis files."""
    HYPOTHESES_DIR.mkdir(parents=True, exist_ok=True)
    hypotheses = []
    for path in sorted(HYPOTHESES_DIR.glob("*.json")):
        try:
            h = json.loads(path.read_text(encoding="utf-8"))
            hypotheses.append(h)
        except json.JSONDecodeError:
            continue
    return hypotheses


def next_hypothesis_id(existing: list[dict]) -> int:
    """Get the next hypothesis number."""
    max_id = 0
    for h in existing:
        hid = h.get("id", "H000")
        try:
            num = int(hid[1:])
            max_id = max(max_id, num)
        except (ValueError, IndexError):
            pass
    return max_id + 1


def build_prompt(beliefs: list[dict], stats: dict, existing: list[dict]) -> str:
    """Build the LLM prompt for hypothesis generation."""
    belief_lines = "\n".join(
        f"- [{b.get('confidence', '?')}] {b.get('belief', '')}"
        for b in beliefs
    )

    # Summarise key stats
    s = stats["summary"]
    e = stats["entropy"]
    z = stats["zipf"]
    stats_summary = f"""Corpus statistics:
- {s['total_words']:,} words, {s['unique_words']:,} unique, {s['total_folios']} folios
- 25 unique glyphs, avg word length {s['avg_word_length']}
- Glyph entropy: {e['glyph_entropy_overall']} bits (Latin ~4.0, Italian ~3.95)
- Word entropy: {e['word_entropy_overall']} bits
- Zipf exponent: {z['exponent']} (R-squared={z['r_squared']}) — {z['interpretation']}
- Hapax legomena: {s['hapax_legomena']:,} ({s['hapax_ratio']:.1%} of vocabulary)
- Currier Language A: {stats['languages'].get('A', {}).get('word_count', 0):,} words, Language B: {stats['languages'].get('B', {}).get('word_count', 0):,} words"""

    # Section breakdown
    section_lines = []
    for sec, data in sorted(stats["sections"].items()):
        sec_ent = stats["entropy"]["by_section"].get(sec, {})
        section_lines.append(
            f"  {sec}: {data['folio_count']} folios, {data['word_count']:,} words, "
            f"entropy={sec_ent.get('glyph_entropy', '?')} bits"
        )
    stats_summary += "\n\nSection breakdown:\n" + "\n".join(section_lines)

    # Top 10 words
    top_words = sorted(
        stats["word_frequency"]["top_50"].items(),
        key=lambda x: -x[1]
    )[:10]
    stats_summary += "\n\nTop 10 words: " + ", ".join(
        f"{w} ({c})" for w, c in top_words
    )

    # Positional glyph preferences
    pos = stats["glyph_frequency"]["positional"]
    first_glyphs = list(pos.get("first", {}).keys())[:5]
    last_glyphs = list(pos.get("last", {}).keys())[:5]
    stats_summary += f"\n\nMost common word-initial glyphs: {first_glyphs}"
    stats_summary += f"\nMost common word-final glyphs: {last_glyphs}"

    # Existing hypotheses
    if existing:
        active = [h for h in existing if h.get("status") == "active"]
        eliminated = [h for h in existing if h.get("status") == "eliminated"]
        hyp_summary = f"\n\nActive hypotheses ({len(active)}):"
        for h in active[:10]:
            hyp_summary += f"\n  [{h.get('id')}] [{h.get('confidence', '?')}] {h.get('claim', '')}"
        if eliminated:
            hyp_summary += f"\n\nEliminated hypotheses ({len(eliminated)}):"
            for h in eliminated[:5]:
                hyp_summary += f"\n  [{h.get('id')}] {h.get('claim', '')} — ELIMINATED"
    else:
        hyp_summary = "\n\nNo existing hypotheses yet. This is the first prediction cycle."

    return f"""You are a hypothesis engine for Brain-V, a cognitive architecture attempting to decipher the Voynich Manuscript (Beinecke MS 408, ~1400-1438 CE).

TASK: Generate 3-5 NEW or REFINED testable hypotheses about the manuscript's cipher, language, or structure.

Brain-V's current beliefs:
{belief_lines}

{stats_summary}
{hyp_summary}

RULES:
1. Each hypothesis MUST be testable against the corpus statistics. Specify the exact test.
2. Types: "cipher" (about encoding method), "language" (about underlying language), "structural" (about text organization), "null" (that the text is meaningless)
3. Include confidence (0.0-1.0) based on how well it fits current evidence.
4. Do NOT repeat eliminated hypotheses.
5. Do NOT propose hypotheses that are untestable with statistical methods.
6. Prefer hypotheses that would NARROW the solution space if confirmed or denied.
7. Consider: glyph positional constraints, Currier A/B split, entropy levels, Zipf fit, hapax ratio.

Respond with EXACTLY this JSON format, nothing else:
{{
  "hypotheses": [
    {{
      "claim": "<plain English description of the hypothesis>",
      "type": "<cipher|language|structural|null>",
      "confidence": <0.0-1.0>,
      "evidence_for": ["<evidence supporting this>"],
      "evidence_against": ["<evidence against this>"],
      "test": "<specific statistical test to run against the corpus>",
      "test_metric": "<what metric to compute>",
      "test_threshold": "<what value would confirm or deny>",
      "reasoning": "<why this hypothesis is worth testing>"
    }}
  ]
}}

Be specific and precise. "The text is encoded Latin" is too vague. "The text uses a simple substitution cipher on medieval Latin, which would produce glyph entropy ~4.0 bits and word-final glyph distribution matching Latin word endings" is good.
JSON only. No markdown fences. No commentary."""


def call_claude(prompt: str) -> str:
    """Call Claude via the claude CLI (uses the user's existing plan)."""
    import tempfile, os
    # Write prompt to a temp file to avoid shell escaping issues with long prompts
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(prompt)
        prompt_file = f.name
    try:
        # Run from home dir to avoid CLAUDE.md context pollution but keep auth
        result = subprocess.run(
            [
                CLAUDE_CLI, "-p",
                f"Read the file {prompt_file} and follow its instructions exactly. Output only raw JSON, no markdown, no commentary.",
                "--model", "sonnet",
                "--output-format", "text",
                "--allowedTools", "Read",
            ],
            capture_output=True, text=True, timeout=120,
            cwd=os.path.expanduser("~"),
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"claude CLI exit {result.returncode}. "
                f"stdout: {result.stdout[:500]}. stderr: {result.stderr[:500]}"
            )
        return result.stdout.strip()
    finally:
        os.unlink(prompt_file)


def parse_hypotheses(raw: str) -> list[dict]:
    """Parse LLM response into hypothesis list."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        parsed = json.loads(raw)
        return parsed.get("hypotheses", [])
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                parsed = json.loads(raw[start:end])
                return parsed.get("hypotheses", [])
            except json.JSONDecodeError:
                pass
    return [{"claim": "PARSE_FAILED", "type": "null", "confidence": 0, "reasoning": raw[:200]}]


def save_hypotheses(hypotheses: list[dict], start_id: int, date_str: str) -> list[dict]:
    """Save each hypothesis as a separate file."""
    HYPOTHESES_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, h in enumerate(hypotheses):
        hid = f"H{start_id + i:03d}"
        hypothesis = {
            "id": hid,
            "claim": h.get("claim", ""),
            "type": h.get("type", "unknown"),
            "confidence": h.get("confidence", 0.5),
            "evidence_for": h.get("evidence_for", []),
            "evidence_against": h.get("evidence_against", []),
            "test": h.get("test", ""),
            "test_metric": h.get("test_metric", ""),
            "test_threshold": h.get("test_threshold", ""),
            "tests_run": [],
            "tests_remaining": [h.get("test", "")],
            "status": "active",
            "parent": None,
            "created": date_str,
            "last_tested": None,
            "reasoning": h.get("reasoning", ""),
        }
        path = HYPOTHESES_DIR / f"{hid}.json"
        path.write_text(json.dumps(hypothesis, indent=2), encoding="utf-8")
        saved.append(hypothesis)
    return saved


def main():
    parser = argparse.ArgumentParser(description="Brain-V prediction: Voynich hypothesis generator")
    parser.add_argument("--from-agentos", action="store_true", help="Load beliefs from AgentOS")
    args = parser.parse_args()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[predict] Running prediction cycle for {today}...")

    # Load beliefs
    if args.from_agentos:
        print("[predict] Loading beliefs from AgentOS...")
        beliefs = load_beliefs_agentos()
    else:
        print("[predict] Loading beliefs from local beliefs.json...")
        beliefs = load_beliefs_local()
    print(f"[predict] Loaded {len(beliefs)} beliefs.")

    # Load stats
    stats = load_stats()
    if not stats:
        print("[predict] ERROR: No statistical profile found. Run perceive.py first.")
        return
    print(f"[predict] Loaded stats: {stats['summary']['total_words']:,} words profiled.")

    # Load existing hypotheses
    existing = load_existing_hypotheses()
    print(f"[predict] {len(existing)} existing hypotheses loaded.")

    # Build prompt and call LLM
    prompt = build_prompt(beliefs, stats, existing)
    print(f"[predict] Calling Claude via CLI...")
    raw_response = call_claude(prompt)

    # Parse hypotheses
    hypotheses = parse_hypotheses(raw_response)
    print(f"[predict] Generated {len(hypotheses)} hypotheses.")

    # Save individual hypothesis files
    start_id = next_hypothesis_id(existing)
    saved = save_hypotheses(hypotheses, start_id, today)

    for h in saved:
        print(f"  [{h['id']}] [{h['confidence']}] ({h['type']}) {h['claim'][:80]}")

    # Save cycle prediction record
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "date": today,
        "cycle": "predict",
        "model": MODEL,
        "belief_count": len(beliefs),
        "existing_hypothesis_count": len(existing),
        "new_hypotheses": [h["id"] for h in saved],
        "hypotheses": saved,
        "raw_response": raw_response,
    }
    path = PREDICTIONS_DIR / f"{today}.json"
    # If file exists (multiple cycles per day), append cycle number
    if path.exists():
        cycle = 2
        while (PREDICTIONS_DIR / f"{today}-cycle{cycle}.json").exists():
            cycle += 1
        path = PREDICTIONS_DIR / f"{today}-cycle{cycle}.json"

    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"[predict] Saved to {path}")

    return saved


if __name__ == "__main__":
    main()
