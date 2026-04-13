---
layer: 5
name: Emotion / Valence
status: TO BUILD
---

# Emotion / Valence

Fast heuristic prioritisation signal. Where [[attention]] does deliberate scoring, valence is the cheap reflex underneath it — a scalar (or low-dimensional vector) attached to every percept and belief that says "this matters" or "this is fine" before any reasoning runs. Valence is what lets [[curiosity]] react in microseconds and what biases the [[goal-stack]] without explicit deliberation.

## Drive
Pre-deliberative prioritisation. Provide a fast, lossy signal that the slower layers ([[attention]], [[goal-stack]], [[prediction]]) can either accept or override.

## Why this is a layer, not an aesthetic

Friston's Free Energy Principle treats valence as the gradient of expected free energy — it is *the* signal that drives action selection before any explicit prediction is computed. In Brain, valence plays the same role: when a [[perception]] arrives, valence fires immediately and either flags "ignore" or "look harder". Without it, every input has to go through full [[attention]] scoring, which is too expensive at scale.

## Signal sources
- **Surprise magnitude** from [[prediction]] — large prediction errors get high valence automatically
- **Source [[trust]] tier** — items from Verified DKG sources get a baseline valence boost
- **Goal proximity** — overlap with active items in the [[goal-stack]]
- **[[values]] floor** — items that touch the harm floor get strong negative valence regardless of other signals

## Interaction with [[curiosity]]

Curiosity is the slow, principled information-gain reward (layer 14). Valence is its fast cousin. They should agree most of the time; persistent disagreement is itself a signal that one of the two is miscalibrated and a flag for [[learning]].

## Open questions
- Scalar or vector? A scalar is cheap; a vector (e.g. surprise / threat / opportunity) carries more information but is harder to compose with [[attention]] scoring.
- How does valence get *learned* — is it hand-tuned, or does [[learning]] update it from outcome deltas?
- Where does it live computationally? Inside [[perception]]? As a separate pre-attention pass? As metadata on [[world-model]] nodes?

## Connections
[[perception]] · [[attention]] · [[curiosity]] · [[goal-stack]] · [[values]] · [[prediction]]
