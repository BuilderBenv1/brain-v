---
layer: 11
name: Learning
status: SHORTLISTED
---

# Learning

How beliefs update from outcomes. Learning closes the loop: [[prediction]] is made, [[action]] is taken (or [[perception]] arrives), reality is compared against expectation, and the [[world-model]] is revised. The delta is also the reward signal for [[curiosity]].

## Drive
Reduce future [[prediction]] error.

## Pattern

**ICM (Intrinsic Curiosity Module) loop** — from openai/large-scale-curiosity and pathak22/noreward-rl. Prediction error becomes the gradient signal, regardless of whether any external task reward exists.

**ASI-Evolve Analyzer pattern** — from arXiv:2603.29640. After each cycle, a dedicated analyzer distills "what happened" into structured "what it means" insights that get fed back as priors for the next cycle. This separates raw outcomes from reusable knowledge.

ASI-Evolve cycle → Brain layers:
- Learn → [[perception]] + [[world-model]] update
- Design → [[prediction]] + [[goal-stack]]
- Experiment → [[action]]
- Analyze → **this layer** + [[dreaming]]

See [[cognitive-loop]] for the full mapping.

## Belief

**Claim**: ASI-Evolve is the closest published validation of Brain's loop architecture, and its analyzer pattern is directly liftable into Brain's learning layer.
**Confidence**: HIGH
**Source**: raw/research/asi-evolve-2603.29640.md
**Last verified**: 2026-04-08
**Contradicts**: nothing currently

## Open questions
- Whether ASI-Evolve's "cognition base" maps directly onto Brain's `raw/` + `wiki/` combination, or needs its own representation. (Listed in `wiki/gaps/`.)
- Online vs offline updates: which belief revisions happen immediately, and which wait for [[dreaming]]?

## Connections
[[prediction]] · [[world-model]] · [[curiosity]] · [[dreaming]] · [[forgetting]] · [[self-model]]
