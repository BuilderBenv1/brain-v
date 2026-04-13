"""
ingest_failed.py — Load the failed approaches catalogue into Brain-V's hypothesis system.

Reads raw/corpus/failed-approaches.json and creates eliminated hypothesis files
in hypotheses/ so Brain-V never wastes cycles retesting debunked approaches.

Usage:
    python scripts/ingest_failed.py
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FAILED_PATH = PROJECT_ROOT / "raw" / "corpus" / "failed-approaches.json"
HYPOTHESES_DIR = PROJECT_ROOT / "hypotheses"


def main():
    if not FAILED_PATH.exists():
        print("[ingest] ERROR: failed-approaches.json not found.")
        return

    failed = json.loads(FAILED_PATH.read_text(encoding="utf-8"))
    HYPOTHESES_DIR.mkdir(parents=True, exist_ok=True)

    ingested = 0
    skipped = 0

    for fa in failed:
        hid = fa["id"]  # e.g. "FA001"
        path = HYPOTHESES_DIR / f"{hid}.json"

        if path.exists():
            skipped += 1
            continue

        status = "eliminated" if fa["status"] in ("debunked", "debated") else "parked"

        hypothesis = {
            "id": hid,
            "claim": fa["claim"],
            "type": fa.get("type", "unknown"),
            "confidence": 0.0 if status == "eliminated" else 0.1,
            "evidence_for": [],
            "evidence_against": [fa["failure_reason"]],
            "test": f"Historical: {fa['researcher']} ({fa['year']})",
            "test_metric": "literature_review",
            "test_threshold": "peer review and independent verification",
            "tests_run": [{
                "date": str(fa["year"]),
                "test": f"Attempted by {fa['researcher']}",
                "score": 0.0 if status == "eliminated" else 0.2,
                "passed": False if status == "eliminated" else None,
                "details": fa["failure_reason"],
                "confidence_change": "N/A -> 0.0",
            }],
            "tests_remaining": [],
            "status": status,
            "parent": None,
            "created": f"{fa['year']}-01-01",
            "last_tested": f"{fa['year']}-01-01",
            "reasoning": f"Historical attempt by {fa['researcher']} ({fa['year']}). "
                         f"Cipher type: {fa.get('cipher_type', 'unknown')}. "
                         f"Proposed language: {fa.get('proposed_language', 'unknown')}.",
            "source": fa.get("source", ""),
            "researcher": fa["researcher"],
            "year": fa["year"],
        }

        path.write_text(json.dumps(hypothesis, indent=2), encoding="utf-8")
        ingested += 1
        print(f"  [{hid}] {status}: {fa['researcher']} ({fa['year']}) — {fa['claim'][:60]}...")

    print(f"\n[ingest] Done. {ingested} ingested, {skipped} skipped (already exist).")

    # Summary
    all_hyps = list(HYPOTHESES_DIR.glob("*.json"))
    active = sum(1 for p in all_hyps if json.loads(p.read_text())["status"] == "active")
    eliminated = sum(1 for p in all_hyps if json.loads(p.read_text())["status"] == "eliminated")
    parked = sum(1 for p in all_hyps if json.loads(p.read_text())["status"] == "parked")
    print(f"[ingest] Total hypotheses: {len(all_hyps)} "
          f"(active={active}, eliminated={eliminated}, parked={parked})")


if __name__ == "__main__":
    main()
