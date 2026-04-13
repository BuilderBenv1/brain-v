# Brain-V (VoynichMind) — Schema & Operating Instructions

## What This Is

Brain-V is a fork of Project Brain (`C:\Projects\project-brain\`) retargeted at
autonomous decipherment of the Voynich Manuscript (Beinecke MS 408).

Same cognitive loop — perceive, predict, score, learn, repeat.
The loop that predicted arXiv topics now generates and tests decipherment
hypotheses against the manuscript's statistical properties.

## Identity

- Name: Brain-V / VoynichMind
- Fork of: Project Brain (C:\Projects\project-brain)
- Purpose: Autonomous decipherment of the Voynich Manuscript
- Method: Cognitive loop — perceive corpus, generate hypotheses, test against
  statistical properties, update beliefs, repeat
- Drive: The manuscript has resisted 600 years of human analysis. Any AI
  progress is remarkable. On-chain provenance means the reasoning trail is
  verifiable from day 1.

## Folder Structure

```
brain-v/
  raw/                    → Source material. Immutable. Never modify.
    /corpus               → EVA transliteration, Currier data, section maps
    /corpus/reference-profiles → Latin/Italian statistical profiles for comparison
    /perception           → Computed statistical profiles (output of perceive.py)
    /research             → Published analyses, failed decipherment catalogue
  wiki/                   → LLM-maintained. Structured knowledge.
    /layers               → One file per cognitive architecture layer
    /components           → Open source components identified
    /concepts             → Core concepts with definitions and connections
    /gaps                 → What Brain-V doesn't know yet (important)
    INDEX.md              → Master index, updated on every ingest
    LOG.md                → Append-only change log
  outputs/                → Generated answers, analyses
    /reports              → Deep research outputs (baseline stats, etc.)
    /predictions          → Cycle predictions (hypotheses per cycle)
    /scores               → Cycle scoring results
  hypotheses/             → Active hypothesis files (one per hypothesis)
  scripts/                → The cognitive loop
    perceive.py           → Parse EVA corpus, compute statistical profile
    predict.py            → Generate/refine decipherment hypotheses
    score.py              → Test hypotheses against corpus statistics
    loop.py               → Orchestrate the cycle
    beliefs.json          → Current world model
```

## Wiki Rules

- Every topic gets its own .md file
- Every file starts with a one-paragraph summary
- Link related topics using [[topic-name]] format
- Maintain INDEX.md listing every topic with a one-line description
- Maintain LOG.md with every change: date, what changed, why
- Flag contradictions explicitly — don't silently overwrite

## Belief System

Every claim in the wiki carries:
- **Confidence**: 0.0–1.0 (numeric, not categorical)
- **Source**: what evidence supports this
- **Last verified**: date
- **Contradicts**: any conflicting beliefs

## Domain-Specific Scoring Criteria

These replace Brain's arXiv scoring:

1. **Language validity**: Does a proposed decryption produce valid Latin/Italian word frequencies?
2. **Positional constraints**: Does it respect EVA slot grammar (positional glyph constraints)?
3. **Currier split**: Does it explain the Currier A/B language split?
4. **Contextual coherence**: Does decrypted text match illustration context (herbal/astro/bio)?
5. **Historical plausibility**: Is the proposed cipher reproducible with 15th-century tools?
6. **Entropy match**: Does decrypted output entropy match natural language (~4.0-4.5 bits/char)?
7. **Zipf compliance**: Does the word frequency distribution follow Zipf's law?

## Hypothesis Format

Each hypothesis in `hypotheses/` must contain:
- **id**: Unique identifier (e.g., `H001`)
- **claim**: Plain English description
- **type**: cipher / language / structural / null
- **confidence**: 0.0–1.0
- **evidence_for**: List of supporting evidence
- **evidence_against**: List of contradicting evidence
- **tests_run**: List of statistical tests already performed
- **tests_remaining**: List of tests still to run
- **status**: active / parked / eliminated / confirmed
- **parent**: Parent hypothesis ID (if derived from another)
- **created**: Date created
- **last_tested**: Date of last test

## Cognitive Layers

Same layers as Brain, applied to Voynich decipherment:

1. Perception — parse and profile the EVA corpus
2. Attention — which folios/sections to focus on
3. World Model — beliefs about the manuscript's nature
4. Prediction — hypotheses about cipher, language, structure
5. Emotion/Valence — confidence signals, excitement at anomalies
6. Goal Stack — current decipherment strategy
7. Self Model — Brain-V's assessment of its own progress
8. Theory of Mind — modelling the manuscript's author
9. Narrative — Brain-V's story of the investigation
10. Action — tests to run, hypotheses to generate
11. Learning — how beliefs update from test results
12. Forgetting — pruning eliminated hypotheses
13. Dreaming — cross-referencing findings across sections
14. Curiosity — which statistical anomalies to investigate next
15. Values — preference for simple, historically plausible solutions

## Operations

### Perceive Cycle
1. Load EVA transliteration from raw/corpus/
2. Parse into folios → pages → lines → words → glyphs
3. Tag with section (herbal/astronomical/biological/pharmaceutical/recipes)
4. Tag with Currier language (A or B)
5. Compute statistical profile (frequencies, entropy, Zipf fit)
6. Save to raw/perception/voynich-corpus.json and voynich-stats.json
7. Push to AgentOS + IPFS

### Predict Cycle
1. Load beliefs and current hypotheses
2. Load statistical profile
3. Generate 3-5 new or refined hypotheses via LLM
4. Each hypothesis must specify testable statistical criteria
5. Save to hypotheses/ and outputs/predictions/

### Score Cycle
1. Load hypotheses
2. Run specified statistical tests against corpus
3. Score each hypothesis
4. Update confidence scores based on results
5. Update beliefs.json
6. Compute progress score (eliminations, narrowing, any >0.8 confidence)
7. Log to wiki/LOG.md, push to AgentOS + IPFS

### Auto Cycle
Brain-V can cycle continuously — the corpus is static, hypotheses are the
moving part. `python scripts/loop.py auto --cycles N` runs N consecutive
perceive-predict-score cycles.

## Infrastructure

- **AgentOS**: https://agentos-backend-production.up.railway.app
- **Agent launch**: https://agentproof.sh/launch (SKALE chain)
- **Inference**: llama3.1:8b via local Ollama (http://localhost:11434)
- **IPFS**: Belief anchoring via AgentOS save-context
- **Chain**: SKALE Base (zero gas fees) via AgentProof

## Brain-V Agents (SKALE)

| # | Agent | ID | Role |
|---|---|---|---|
| 1 | Brain-V Orchestrator | #471 | Main cycle runner, belief state owner |
| 2 | Brain-V Perceiver | #472 | Corpus parsing, statistical profiling |
| 3 | Brain-V Predictor | #473 | Hypothesis generation via llama3.1 |
| 4 | Brain-V Scorer | #474 | Statistical tests against corpus |
| 5 | Brain-V Scheduler | #475 | Auto cycling Mon-Fri |
| 6 | Brain-V Dreamer | #477 | Cross-section analysis, hypothesis synthesis |
| — | Brain-V Belief Engine | #476 | Registered but unused (ignore) |

## Architecture Decisions Log

| Decision | Rationale | Date | Confidence |
|---|---|---|---|
| Fork of Project Brain | Proven cognitive loop, same scripts/infra | 2026-04-13 | HIGH |
| Primary chain: SKALE | Zero gas fees for both Brain and Brain-V | 2026-04-13 | HIGH |
| Inference: local llama3.1:8b | Cost, latency, privacy | 2026-04-13 | HIGH |
| Scoring: statistical tests | Objective, reproducible, no LLM in scoring loop | 2026-04-13 | HIGH |
| Start with herbal section | Illustrations provide plaintext anchors | 2026-04-13 | MEDIUM |
| EVA transcription standard | Most widely used, enables comparison with literature | 2026-04-13 | HIGH |

## What Brain-V Doesn't Know Yet

- What cipher system was used (substitution, polyalphabetic, nomenclator, etc.)
- What language underlies the text (Latin, Italian, constructed, other)
- Whether the Currier A/B split reflects two ciphers or two scribes
- Whether the manuscript is a hoax (null hypothesis — must be tested)
- How to weight illustration context against statistical evidence
- Whether the Naibbe cipher hypothesis extends to the full manuscript

## Key References

| Source | What it provides |
|---|---|
| EVA transliteration | Standard glyph-to-Latin transcription of all folios |
| Currier classification | Language A vs B folio mapping |
| Naibbe cipher (2025) | Recent decipherment attempt, supplementary data |
| voynich.nu | Community resource hub, prior analysis |
| Beinecke MS 408 | Original high-res scans (Yale) |

## People Index

| Person | Why relevant | Key idea |
|---|---|---|
| William Friedman | NSA cryptanalyst, early systematic analysis | Concluded it was a constructed language |
| Prescott Currier | Navy cryptanalyst, identified A/B language split | Two statistical populations in the text |
| Jorge Stolfi | Computer scientist, extensive statistical analysis | Detailed glyph position constraints |
| Michael Greshko | Naibbe cipher author (2025) | Recent decipherment attempt |
| Wilfrid Voynich | Acquired the manuscript in 1912 | Provenance chain |

---

*This schema is a living document. Brain-V updates it as it learns about the manuscript.*
*Created: 2026-04-13 — Forked from Project Brain*
