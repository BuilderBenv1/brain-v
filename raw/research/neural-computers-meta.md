# Neural Computers — A New Machine Form
Source: arXiv:2604.06425
Published: 2026-04-07
Authors: Mingchen Zhuge, Changsheng Zhao, Haozhe Liu, et al. (19 authors), including Jürgen Schmidhuber
Institutions: Meta AI, KAUST
Status: RAW — to be compiled into wiki

---

## Core claim

Neural Computers (NCs) are a new architectural paradigm that unifies computation, memory, and I/O into a single learned latent runtime state. The model IS the computer — not a program running on a computer, not an agent acting over an environment, not a world model simulating dynamics.

## What it replaces

| Paradigm | Limitation | NC answer |
|---|---|---|
| Conventional computer | Explicit programs, Von Neumann bottleneck | Differentiably configured, not coded |
| Agent | Acts over external execution environment | Instantiates the environment within weights |
| World model | Learns environment dynamics | Merges dynamics with computation and memory |

## Key insight

The shift from the modular Von Neumann hardware/software stack to a unified "neural latent stack." If this holds, future systems are not explicitly coded but differentiably configured.

## Prototypes

Two working demos built on a diffusion transformer (Wan2.1):
- **NCCLIGen** — terminal environments
- **NCGUIWorld** — desktop graphical interfaces

## Why this is a paradigm shift

This is not an incremental improvement. It proposes replacing the fundamental abstraction of computing (program + data + I/O as separate concerns) with a single learned object. If Neural Computers work at scale, the concept of "software" changes.

Schmidhuber co-authored this. The man who invented LSTM and formalized curiosity as compression progress is now arguing the model should BE the computer. That's not a random claim.

## Relevance to Project Brain

### Long-term vision alignment

Brain's current design is agent-shaped: it acts over an environment (arXiv RSS, DKG, X), maintains a separate world model (anda-hippocampus), and stores state externally (AgentOS/IPFS). The NC paradigm suggests this is transitional — the endgame is Brain's world model, reasoning, memory, and I/O unified in a single learned latent state.

Brain is not ready for this. But the architecture should not paint itself into a corner that prevents evolving toward it.

### Near-term implications

- The cognitive loop (perceive → model → predict → act → update) maps onto the NC framing: what if the loop isn't a pipeline but a single differentiable object?
- BRAID graphs (cached reasoning blueprints) are a step toward "differentiably configured" computation — not code, but learned reasoning shapes.
- The dreaming cycle (offline consolidation) could be the NC's self-reconfiguration phase.

### What it does NOT change

- Week 1-8 build plan: still the right path. NC is a 2-5 year horizon.
- AgentOS as persistence layer: still needed regardless of paradigm.
- The cognitive layer decomposition: useful as a design tool even if the runtime is unified.

## For the wiki
- Update wiki/concepts/master-architecture.md — add NC as long-term architectural horizon
- Update wiki/layers/world-model.md — note NC convergence direction
- Add to wiki/components/library.md as RESEARCH
- Update wiki/people/index.md — Schmidhuber is now co-authoring work directly relevant to Brain's trajectory

---
*Filed: 2026-04-13*
*Status: RESEARCH — paradigm-level, not near-term actionable*
*Review date: ongoing — track NC prototype progress*
