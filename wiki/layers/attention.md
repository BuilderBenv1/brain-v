---
layer: 2
name: Attention
status: TO BUILD
---

# Attention

Decides what matters out of everything [[perception]] ingests. Attention is the gatekeeper between raw input and the [[world-model]] — it scores each incoming item on novelty, relevance, and goal alignment, and only the high-scoring items get committed to belief.

## Drive
Maximise expected information gain per unit of [[world-model]] update cost. Attention is the bottleneck that prevents Brain from drowning in low-value input.

## Scoring (initial design)
- **Novelty** — distance from existing beliefs in the [[world-model]]
- **Relevance** — overlap with active items in the [[goal-stack]]
- **Source quality** — weighted by [[trust]] tier of the originating source
- **Surprise** — magnitude of [[prediction]] error if the item is true

## Candidate components
None shortlisted yet — likely a custom scoring layer on top of [[world-model]] embeddings. ASI-Evolve's "cognition base" pattern (see [[learning]]) is a related prior-injection mechanism worth studying.

## Open questions
- Does attention run synchronously inside the perceive→update step, or as a separate filter pass?
- How does it interact with the [[dreaming]] cycle, which gets a second pass at things attention initially rejected?

## Connections
[[perception]] · [[world-model]] · [[curiosity]] · [[goal-stack]] · [[dreaming]]
