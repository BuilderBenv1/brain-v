---
type: master-index
last_updated: 2026-04-08
---

# Wiki Index

Master index of every file in `wiki/`. One line per file.

## Concepts

- [master-architecture](concepts/master-architecture.md) — full architecture: drives, layers, infrastructure stack, build sequence
- [trust](concepts/trust.md) — infrastructure (not a cognitive layer): AgentProof + OriginTrail DKG. Canonical target for `[[trust]]` wikilinks.
- [verification-layer](concepts/verification-layer.md) — Brain's RLVR equivalent: binary signal generator that makes learning trainable. Required before week 3.
- [economic-layer](concepts/economic-layer.md) — incentive structure: how outputs accrue value and feed back into priority. Required before week 3.
- [curation-moat](concepts/curation-moat.md) — Brain's core competitive position: verified curation compounding over time, not data volume.

## Cognitive Layers (15)

- [1. perception](layers/perception.md) — how Brain ingests the world (Hermes Agent candidate)
- [2. attention](layers/attention.md) — what gets through to the world model (custom scoring)
- [3. world-model](layers/world-model.md) — belief graph substrate (anda-hippocampus shortlisted)
- [4. prediction](layers/prediction.md) — forward simulation via BRAID graphs
- [5. emotion-valence](layers/emotion-valence.md) — fast pre-deliberative prioritisation signal
- [6. goal-stack](layers/goal-stack.md) — persistent objectives, on-chain via TaskQueue
- [7. self-model](layers/self-model.md) — Brain's beliefs about its own capabilities
- [8. theory-of-mind](layers/theory-of-mind.md) — modelling other minds (MetaMind shortlisted)
- [9. narrative](layers/narrative.md) — continuous identity across sessions
- [10. action](layers/action.md) — X posts, DKG writes, TaskQueue submissions
- [11. learning](layers/learning.md) — belief updates from prediction-vs-reality delta (ASI-Evolve analyzer)
- [12. forgetting](layers/forgetting.md) — confidence decay and pruning
- [13. dreaming](layers/dreaming.md) — offline consolidation (openclaw-auto-dream)
- [14. curiosity](layers/curiosity.md) — prediction-error intrinsic reward (the engine)
- [15. values](layers/values.md) — meta-layer on goals (working definition, confidence LOW)

Note: Trust is no longer a cognitive layer. See [trust](concepts/trust.md) under Concepts (and `components/library.md` for the implementation rows).

## Components

- [components/library](components/library.md) — full table of cherry-pickable components, statuses, and beliefs

## People

- [people/index](people/index.md) — key figures in Brain's intellectual + build orbit

## Gaps

- [gaps/open-questions](gaps/open-questions.md) — what Brain doesn't know yet

## Logs

- [LOG](LOG.md) — append-only change log
