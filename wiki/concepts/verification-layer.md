---
type: concept
name: Verification Layer
status: ARCHITECTURE — not built, required before week 3
last_updated: 2026-04-09
---

# Verification Layer

Brain's RLVR equivalent — the binary signal generator that makes the [[learning]] loop trainable. Without it, Brain's surprise scores are LLM-judged vibes, not ground truth. The loop can close on vibes for week 1, but it cannot *compound* on them. Verification is what turns Brain from "a system that runs" into "a system that provably improves."

## Why this matters

Right now (week 1), `score.py` asks the local 8B model: "how well did these predictions match these papers?" The model returns a number. That number is:

- **Not grounded** — it's the 8B's opinion about match quality, not a measured fact
- **Not binary** — it's a float, which means the [[learning]] update rule (surprise > 0.6 → demote beliefs) is thresholding a soft signal with a hard cutoff, losing information
- **Not verifiable** — nobody can check the score except by re-running the same LLM call, which may give a different answer

RLVF (Reinforcement Learning from Verifiable Feedback) works because the reward signal is *binary and checkable*: the code compiles or it doesn't, the proof is valid or it isn't, the prediction matches or it doesn't. Brain needs the same kind of signal.

## What verification looks like for Brain

The prediction domain is cs.AI paper topics. Verifiable signals available:

| Signal | Binary? | Checkable? | Automated? |
|---|---|---|---|
| "Did a paper with keyword X appear?" | Yes | Yes — grep the RSS | Yes |
| "Did Brain's predicted topic rank in top-N by count?" | Yes | Yes — count titles | Yes |
| "Did the surprise score decrease from last cycle?" | Yes | Yes — compare JSONs | Yes |
| "Was Brain's confidence calibrated?" (stated 0.85, hit rate ~85%) | No (needs N cycles) | Yes (eventually) | Yes |

The first three are available *now*. The scoring loop should be producing binary pass/fail per prediction alongside the LLM-judged surprise score, so that Brain has a hard signal to learn from and a soft signal for nuance.

## Architecture sketch

```
Prediction (5 topic themes with confidence)
    ↓
Reality (tomorrow's arXiv RSS)
    ↓
Verification layer:
  1. Keyword match — did each predicted topic appear? (binary per prediction)
  2. Rank match — was each topic in the top N by frequency? (binary)
  3. Calibration — over rolling window, does stated confidence ≈ hit rate? (continuous, delayed)
    ↓
Binary reward signal → [[learning]] (hard update: promote/demote beliefs)
LLM-judged surprise → [[curiosity]] (soft signal: what was *interesting* about the miss?)
```

The binary signal trains the model. The soft signal directs exploration. Both are needed; neither is sufficient alone.

## Relationship to other components

- **[[trust]]** — verification results get written to the DKG. Verified predictions that hit promote the underlying beliefs to higher trust tiers. Verified misses demote them.
- **[[self-model]]** — calibration data (stated confidence vs hit rate) is the primary input to Brain's self-model. Without verification, the self-model is guessing about its own accuracy.
- **[[action]]** — Brain should not post predictions on X until the verification layer can score them. Otherwise Brain is posting unverifiable claims, which violates the no-deception value (see [[values]]).
- **[[economic-layer]]** — verification is upstream of economics. The economic layer needs to know *which outputs are valuable*, and verification is how value gets measured.

## Belief

**Claim**: Without a verification layer producing binary reward signals, Brain's learning loop will plateau after the initial novelty of LLM-judged surprise scores wears off — the soft signal is too noisy to compound over many cycles.
**Confidence**: MEDIUM
**Source**: RLVR literature (DeepSeek-R1 pattern), analogy to Brain's score.py architecture
**Last verified**: 2026-04-09
**Contradicts**: nothing currently

**Claim**: Keyword-match and rank-match verification are implementable in week 2 with no new dependencies — just string matching against the existing perception output.
**Confidence**: HIGH
**Source**: architecture analysis of perceive.py + score.py
**Last verified**: 2026-04-09
**Contradicts**: nothing currently

## Open questions
- Is keyword match too crude? "Chain-of-thought reasoning" as a prediction vs "CoT" in a paper title — these are semantic matches, not string matches. May need embedding similarity with a hard threshold to stay binary.
- How many cycles does Brain need before calibration data is meaningful? (Probably 20+ — not available until week 3.)
- Should verification scores be stored separately from LLM-judged scores, or should they replace them?

## Connections
[[learning]] · [[prediction]] · [[curiosity]] · [[self-model]] · [[trust]] · [[action]] · [[values]] · [[economic-layer]]
