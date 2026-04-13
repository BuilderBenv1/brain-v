"""
loop.py — Brain-V's cognitive loop

Runs the perceive → predict → score → update cycle for Voynich decipherment.
Unlike Brain (which waits for daily arXiv data), Brain-V can cycle continuously
because the corpus is static — hypotheses are the moving part.

Usage:
    python scripts/loop.py perceive-predict    # perceive corpus + generate hypotheses
    python scripts/loop.py score               # test hypotheses + update beliefs
    python scripts/loop.py full                # perceive + predict + score in one shot
    python scripts/loop.py auto --cycles 10    # run N consecutive full cycles
    python scripts/loop.py status              # show current state
"""

import json
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BELIEFS_PATH = PROJECT_ROOT / "scripts" / "beliefs.json"
SCORES_DIR = PROJECT_ROOT / "outputs" / "scores"
PREDICTIONS_DIR = PROJECT_ROOT / "outputs" / "predictions"
HYPOTHESES_DIR = PROJECT_ROOT / "hypotheses"
WIKI_LOG = PROJECT_ROOT / "wiki" / "LOG.md"
FAIL_LOG = PROJECT_ROOT / "outputs" / "failures.log"


# --- Circuit breaker ---

def log_failure(step: str, error: str):
    """Write a structured failure entry to both LOG.md and outputs/failures.log."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S UTC")

    FAIL_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(FAIL_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "date": date_str, "time": time_str,
            "step": step, "error": error[:500],
        }) + "\n")

    log_entry = f"""## {date_str} — FAILED: {step} ({time_str})

**Step**: `{step}`
**Error**: {error[:300]}
**Action**: Brain-V's loop broke. Check `outputs/failures.log` for details."""

    append_to_wiki_log(log_entry)
    print(f"\n[loop] CIRCUIT BREAKER: {step} failed at {time_str}.")


def run_script(name: str, extra_args: list[str] | None = None) -> bool:
    """Run a script. Returns True on success."""
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / name)]
    if extra_args:
        cmd.extend(extra_args)
    print(f"\n{'='*60}")
    print(f"  Running: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    try:
        result = subprocess.run(
            cmd, cwd=str(PROJECT_ROOT),
            capture_output=True, text=True, timeout=300,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip() or f"Exit code {result.returncode}"
            log_failure(name, error_msg)
            return False
        return True
    except subprocess.TimeoutExpired:
        log_failure(name, "Script timed out after 300 seconds")
        return False
    except Exception as e:
        log_failure(name, f"{type(e).__name__}: {e}")
        return False


# --- Wiki log ---

def append_to_wiki_log(entry: str):
    if WIKI_LOG.exists():
        current = WIKI_LOG.read_text(encoding="utf-8")
        marker = "---\n\n## "
        idx = current.find(marker)
        if idx >= 0:
            new_content = current[:idx] + "---\n\n" + entry + "\n\n## " + current[idx + len(marker):]
            WIKI_LOG.write_text(new_content, encoding="utf-8")
            return
    # Fallback: just append
    with open(WIKI_LOG, "a", encoding="utf-8") as f:
        f.write("\n\n" + entry)


# --- Commands ---

def cmd_perceive_predict():
    if not run_script("perceive.py", ["--report"]):
        print("[loop] Perceive failed.")
        return False

    if not run_script("predict.py"):
        print("[loop] Predict failed. No hypotheses generated.")
        return False

    # Summary
    hypotheses = []
    for path in sorted(HYPOTHESES_DIR.glob("*.json")):
        try:
            hypotheses.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    active = [h for h in hypotheses if h.get("status") == "active"]
    print(f"\n[loop] Perceive-predict complete. {len(active)} active hypotheses.")
    return True


def cmd_score():
    if not run_script("score.py"):
        print("[loop] Score failed. Beliefs not updated.")
        return False

    # Log to wiki
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Find latest score file
    score_files = sorted(SCORES_DIR.glob(f"{today}*.json"))
    if score_files:
        score = json.loads(score_files[-1].read_text(encoding="utf-8"))
        progress = score.get("progress", {})

        log_entry = f"""## {today} — Brain-V cognitive cycle (automated)

**Hypotheses scored**: {score.get('hypotheses_scored', '?')}
**Progress**: {progress.get('progress_summary', '?')}
**Surprise**: {progress.get('surprise', '?')}
**Beliefs**: {score.get('belief_count_before', '?')} → {score.get('belief_count_after', '?')}
**High confidence**: {progress.get('high_confidence_ids', [])}"""

        append_to_wiki_log(log_entry)
        print(f"\n[loop] Score logged to wiki/LOG.md")
        print(f"[loop] Surprise={progress.get('surprise', '?')}")

    return True


def cmd_decrypt():
    """Run decryption attacks on sections with high-confidence cipher hypotheses."""
    # Check if any cipher hypothesis is above threshold
    if not HYPOTHESES_DIR.exists():
        return False

    cipher_hyps = []
    for path in sorted(HYPOTHESES_DIR.glob("H*.json")):
        try:
            h = json.loads(path.read_text(encoding="utf-8"))
            if h.get("status") == "active" and h.get("type") == "cipher" and h.get("confidence", 0) > 0.4:
                cipher_hyps.append(h)
        except json.JSONDecodeError:
            continue

    if not cipher_hyps:
        print("[loop] No cipher hypotheses above 0.4 confidence. Skipping decrypt.")
        return True

    print(f"[loop] {len(cipher_hyps)} cipher hypotheses above threshold. Running decryption...")
    # Run decrypt on text-only section (H027: closest to natural language — Rosetta stone)
    if not run_script("decrypt.py", ["--section", "text-only"]):
        print("[loop] Decrypt failed on herbal section.")
        return False

    return True


def cmd_full():
    """Run a full perceive → predict → score → decrypt cycle."""
    if not cmd_perceive_predict():
        return False
    if not cmd_score():
        return False
    # Attempt decryption after scoring
    cmd_decrypt()
    return True


def cmd_auto(cycles: int):
    """Run multiple consecutive cycles."""
    print(f"\n[loop] Starting auto mode: {cycles} cycles")
    print(f"{'='*60}\n")

    for i in range(1, cycles + 1):
        print(f"\n{'#'*60}")
        print(f"  CYCLE {i}/{cycles}")
        print(f"{'#'*60}\n")

        success = cmd_full()
        if not success:
            print(f"\n[loop] Cycle {i} failed. Stopping auto mode.")
            break

        # Brief pause between cycles to let Ollama cool down
        if i < cycles:
            print(f"\n[loop] Cycle {i} complete. Pausing 5 seconds before next cycle...")
            time.sleep(5)

    # Final status
    cmd_status()


def cmd_status():
    print("\n=== BRAIN-V STATUS ===\n")

    # Beliefs
    if BELIEFS_PATH.exists():
        beliefs = json.loads(BELIEFS_PATH.read_text(encoding="utf-8"))
        print(f"Beliefs: {len(beliefs)}")
        for b in beliefs:
            conf = b.get("confidence", "?")
            if isinstance(conf, float):
                conf = f"{conf:.2f}"
            print(f"  [{conf}] {b.get('belief', '?')[:80]}")
    else:
        print("No local beliefs.json found.")

    # Hypotheses
    print(f"\nHypotheses:")
    if HYPOTHESES_DIR.exists():
        all_hyps = []
        for path in sorted(HYPOTHESES_DIR.glob("*.json")):
            try:
                all_hyps.append(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue

        active = [h for h in all_hyps if h.get("status") == "active"]
        eliminated = [h for h in all_hyps if h.get("status") == "eliminated"]
        print(f"  Total: {len(all_hyps)} | Active: {len(active)} | Eliminated: {len(eliminated)}")

        if active:
            print(f"\n  Active (sorted by confidence):")
            for h in sorted(active, key=lambda x: -x.get("confidence", 0)):
                print(f"    [{h['id']}] [{h.get('confidence', '?'):.2f}] ({h.get('type', '?')}) "
                      f"{h.get('claim', '?')[:70]}")

        high = [h for h in active if h.get("confidence", 0) > 0.8]
        if high:
            print(f"\n  *** HIGH CONFIDENCE (>0.8): ***")
            for h in high:
                print(f"    [{h['id']}] [{h['confidence']:.2f}] {h['claim']}")
    else:
        print("  No hypotheses directory yet.")

    # Score history
    print(f"\nScore history:")
    if SCORES_DIR.exists():
        score_files = sorted(SCORES_DIR.glob("*.json"))
        if score_files:
            for sf in score_files[-10:]:  # last 10
                s = json.loads(sf.read_text(encoding="utf-8"))
                p = s.get("progress", {})
                print(f"  {s.get('date', '?')} — surprise={p.get('surprise', '?')}, "
                      f"{p.get('progress_summary', '?')}")
        else:
            print("  No scores yet.")
    else:
        print("  No scores directory yet.")

    # Failure history
    print(f"\nRecent failures:")
    if FAIL_LOG.exists():
        lines = FAIL_LOG.read_text(encoding="utf-8").strip().split("\n")
        recent = lines[-5:] if len(lines) > 5 else lines
        for line in recent:
            try:
                f = json.loads(line)
                print(f"  {f.get('date', '?')} {f.get('time', '?')} — "
                      f"{f.get('step', '?')}: {f.get('error', '?')[:80]}")
            except json.JSONDecodeError:
                print(f"  {line[:80]}")
    else:
        print("  No failures recorded.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/loop.py [perceive-predict|score|decrypt|full|auto|status]")
        print("  auto: python scripts/loop.py auto --cycles 10")
        sys.exit(1)

    cmd = sys.argv[1]
    try:
        if cmd == "perceive-predict":
            cmd_perceive_predict()
        elif cmd == "score":
            cmd_score()
        elif cmd == "decrypt":
            cmd_decrypt()
        elif cmd == "full":
            cmd_full()
        elif cmd == "auto":
            cycles = 5  # default
            if "--cycles" in sys.argv:
                idx = sys.argv.index("--cycles")
                if idx + 1 < len(sys.argv):
                    cycles = int(sys.argv[idx + 1])
            cmd_auto(cycles)
        elif cmd == "status":
            cmd_status()
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    except Exception as e:
        log_failure(f"loop.py {cmd}", f"Unhandled: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
