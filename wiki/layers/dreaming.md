---
layer: 13
name: Dreaming
status: SHORTLISTED
---

# Dreaming

Offline consolidation. While Brain is not actively perceiving, it re-runs the day: episodic entries get compressed into semantic beliefs, contradictions get resolved, expired confidences get pruned, and hypotheses are generated for the next active session. Dreaming is where compounding actually happens.

## Drive
Convert episodic [[perception]] into durable [[world-model]] beliefs. Maximise structure per unit of stored data.

## Architecture

**Primary: [[openclaw-auto-dream]] (LeoYeAI)** — scheduled consolidation with health scoring.
**Reference: Letta sleep-time compute** — anticipatory pre-computation while the agent is idle.
**Reference: Google Always-On Memory Agent** — LLM-native consolidation, no vector DB.
**Validation: ASI-Evolve dedicated analyzer** — distills experimental outcomes into reusable insights (see [[learning]] and raw/research/asi-evolve-2603.29640.md).

## Cognition base / prior injection

ASI-Evolve's "cognition base" injects accumulated prior knowledge into each new cycle to prevent rediscovering known dead ends. In Brain, this maps to dreaming generating BRAID graphs (see [[prediction]]) and writing them into the cache so the fast path can reuse them on the next cycle.

## Per CLAUDE.md — nightly Dream Cycle

- Compress episodic entries into semantic beliefs
- Prune beliefs with expired confidence (handoff to [[forgetting]])
- Strengthen beliefs confirmed by multiple sources
- Generate hypotheses for next active session
- Output a Dream Report to `outputs/`

## Belief

**Claim**: openclaw-auto-dream provides a usable scheduling and health-scoring substrate for Brain's nightly cycle.
**Confidence**: MEDIUM
**Source**: raw/conversations/founding-conversation-2026-04-06.md
**Last verified**: 2026-04-08
**Contradicts**: nothing currently

## Open questions
- How does the dreaming cycle interact with the DKG [[trust]] tier system? (Listed in `wiki/gaps/`.)
- How often should dreaming run? Nightly is the default but the optimal cadence is unknown.

## Connections
[[world-model]] · [[learning]] · [[forgetting]] · [[prediction]] · [[curiosity]] · [[openclaw-auto-dream]]
