---
layer: 8
name: Theory of Mind
status: SHORTLISTED
---

# Theory of Mind

Brain's models of other minds — humans, other agents, sub-brains. Required for any social [[action]] (X posts, conversations, sub-brain negotiation), and required for the master brain to arbitrate between sub-minds without collapsing into a top-down command system.

## Drive
Accurate modelling of other minds — predict what they believe, want, and will do.

## Architecture

**Primary: [[metamind]] (XMZhangAI, NeurIPS 2025 Spotlight)** — splits into a ToM agent and a Domain agent that work together.
**Secondary: ToM-agent** — BDI (Belief / Desire / Intention) tracking with confidence levels.

Both fit naturally inside Brain's belief graph: each modelled mind is a sub-graph in the [[world-model]] with its own confidence-weighted beliefs.

## Master/Sub-brain relevance

The master brain "negotiates with genuine sub-minds" rather than commanding them (see [[master-architecture]]). That negotiation requires the master brain to *model* each sub-brain's drive and current state — which is theory of mind applied internally. Theory of mind is therefore not optional for the full architecture; it is the substrate for inter-brain coherence.

## Negotiation protocol (working answer, 2026-04-08)

**Mechanism**: publish / read / arbitrate via DKG.

1. Each sub-brain **publishes** its current beliefs to the OriginTrail DKG (see components library — Trust). Each published belief carries its sub-brain's identity, confidence, source, and supporting evidence.
2. Sub-brains **read** each other's published beliefs to maintain their own world-model sub-graphs (this is where ToM lives — each sub-brain models the others by reading their DKG output).
3. The master brain **arbitrates** contradictions on the basis of *evidence quality*, not authority. When two sub-brains publish conflicting claims, the master compares supporting evidence (source trust tier, prediction-track-record, internal coherence with the rest of the graph) and writes the resolution back to the DKG with its own master-brain identity.

The master brain has no command channel. It only has higher-priority writes on the same DKG everyone else uses. Sub-brains may continue holding losing beliefs locally, but the DKG-verified tier reflects the master's arbitration.

**Confidence**: LOW. The arbitration rule ("evidence quality") is itself underspecified — it has to be made concrete before the protocol is implementable.
**Source**: working answer 2026-04-08, see `wiki/gaps/open-questions.md`

## Open questions
- Does the same ToM machinery work for modelling humans on X and modelling sub-brains internally, or do they need different representations?
- How does ToM interact with [[trust]] scoring from AgentProof?

## Connections
[[world-model]] · [[self-model]] · [[trust]] · [[action]] · [[metamind]]
