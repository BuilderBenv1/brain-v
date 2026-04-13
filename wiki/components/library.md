---
type: components-library
last_updated: 2026-04-08
---

# Components Library

Every open-source component identified as cherry-pickable for Brain. Status legend:

- **BUILT** — already live and integrated (AgentOS, AgentProof)
- **SHORTLISTED** — chosen as primary candidate for a layer; not yet integrated
- **TOOL** — used during development but not part of the runtime cognitive loop
- **RESEARCH** — interesting prior work, not yet a candidate for integration
- **WATCH** — credible but unverified; revisit on schedule

## Table

| Component | Layer | Repo / Source | Status | Notes |
|---|---|---|---|---|
| **AgentOS** | Persistence + Execution | github.com/BuilderBenv1/agentos | **BUILT — LIVE** | Railway production backend. Brain registered as agent 1. Sub-brains 2–6 registered. State persisting to IPFS via AgentStateSync. See [[master-architecture]] 2026-04-09 update. |
| **AgentProof** | Trust (infrastructure) | ERC-8004 | **BUILT** | Live on mainnet, 145K agents indexed. Identity + reputation. **Trust is infrastructure, not a cognitive layer — see schema fix 2026-04-08 in LOG.md.** |
| LadybugDB | [[world-model]] | ldclabs/anda-hippocampus | SHORTLISTED | Underlying graph store for anda-hippocampus. |
| anda-hippocampus | [[world-model]] | ldclabs/anda-hippocampus | SHORTLISTED | Graph-native, sleep consolidation, contradiction detection, state evolution. |
| OriginTrail DKG V9 | Trust (infrastructure) | OriginTrail/dkg-v9 | SHORTLISTED | 4-tier trust system: Working → Shared → Long-term → Verified. Substrate for sub-brain negotiation protocol — see [[theory-of-mind]]. |
| openclaw-auto-dream | [[dreaming]] | LeoYeAI/openclaw-auto-dream | SHORTLISTED | Scheduled consolidation, health scoring. |
| BRAID | [[prediction]] | arXiv:2512.15959 (OpenServ) | SHORTLISTED | Mermaid graph bounded reasoning. Frontier model draws blueprint, cheap model executes, blueprint cached forever. |
| OpenAI large-scale-curiosity | [[curiosity]] | openai/large-scale-curiosity | SHORTLISTED | Prediction error as intrinsic reward, validated across 54 environments. |
| pathak22/noreward-rl | [[curiosity]] | pathak22/noreward-rl | SHORTLISTED | Original ICM implementation. |
| MetaMind | [[theory-of-mind]] | XMZhangAI/MetaMind | SHORTLISTED | NeurIPS 2025 Spotlight. ToM agent + Domain agent. |
| Hermes Agent | [[perception]] | NousResearch/hermes-agent | TOOL / SHORTLISTED | 28.5K stars. Native `/llm-wiki` skill (Karpathy pattern). Brain's candidate ingestion pipeline. |
| GitNexus | Structural Graph | abhigyanpatwari/GitNexus | TOOL | Codebase knowledge graph. Use during development for architectural clarity. |
| MAGMA | [[world-model]] | arXiv Jan 2026 | RESEARCH | 4-graph architecture: semantic, temporal, causal, entity. |
| ASI-Evolve | [[cognitive-loop]] | arXiv:2603.29640 | RESEARCH | Learn → design → experiment → analyze cycle. Cognition base + analyzer pattern. Closest published validation of Brain's loop. |
| Graphiti / Zep | [[world-model]] | zep-inc/graphiti | RESEARCH | Temporal KG, 94.8% DMR accuracy, bitemporal versioning. Head-to-head vs anda-hippocampus. |
| MemPalace | [[world-model]] / [[forgetting]] | github.com/milla-jovovich/mempalace | WATCH — SUPERSEDED by Memento for compression | Method-of-loci hierarchy. AAAK compression claims debunked. Contradiction detection module survives scrutiny. Review 2026-04-21. |
| **Memento** | Context compression | github.com/microsoft/memento, HF microsoft/OpenMementos | **SHORTLISTED** | Microsoft. Trained context compression: 6x trace-level, 2-3x KV cache reduction, throughput nearly doubles. 228K open training traces. Replaces MemPalace AAAK as compression candidate. |
| LightThinker++ | [[dreaming]] / [[forgetting]] / [[learning]] | arXiv:2604.03679 | RESEARCH | Commit/expand/fold memory primitives. 69.9% token reduction, +2.42% accuracy. Stable past 80 rounds in agentic tasks. Primitives map directly to dreaming/learning/forgetting interface. |
| Neural Computers | Long-term vision | arXiv:2604.06425 | RESEARCH | Meta AI + KAUST + Schmidhuber. Unifies computation, memory, I/O in a single learned latent state. Paradigm-level — not near-term actionable but defines Brain's long-term architectural horizon. |
| Letta sleep-time compute | [[dreaming]] | (Letta) | RESEARCH | Anticipatory pre-computation while idle. |
| Google Always-On Memory Agent | [[dreaming]] | (Google) | RESEARCH | LLM-native consolidation, no vector DB. |
| ToM-agent | [[theory-of-mind]] | (paper) | RESEARCH | BDI tracking with confidence. |
| Opal Intelligence | (reference) | @opalbotgg | WATCH | Persistent gaming brain, 1.5M behavioural signals. Closest existing analogue. |

## Beliefs about the stack

**Claim**: AgentOS provides the persistence and execution layer such that Brain does not need to build a state-sync layer from scratch.
**Confidence**: HIGH → **VERIFIED**
**Source**: raw/research/agentos-built.md, live registration 2026-04-09
**Last verified**: 2026-04-09
**Contradicts**: any older plan that allocated Week 1 to building persistence
**Evidence**: Brain master agent registered (ID 1), 5 sub-brains registered (IDs 2–6), initial belief set persisted to IPFS hash `QmTV8StsWAmY2jZZs2inxZkLkx3U1UDDCp2Lmc3H74NSH7`, on-chain tx `beb2eef8...fd908cd`. This is no longer a claim — it is an observed fact.

**Claim**: Hermes Agent's `/llm-wiki` skill is the right perception pipeline at POC stage.
**Confidence**: MEDIUM
**Source**: raw/research/hermes-agent-llm-wiki.md
**Last verified**: 2026-04-08
**Contradicts**: nothing currently

**Claim**: MemPalace cannot replace anda-hippocampus as the world-model substrate.
**Confidence**: HIGH
**Source**: raw/research/mempalace.md (community-debunked benchmarks)
**Last verified**: 2026-04-08
**Contradicts**: any earlier "MemPalace as candidate" framing

**Claim**: Memento is the right context compression primitive for Brain's dreaming/forgetting layers, superseding MemPalace's AAAK.
**Confidence**: MEDIUM
**Source**: raw/research/memento-microsoft.md
**Last verified**: 2026-04-13
**Contradicts**: any residual reliance on MemPalace AAAK for compression

**Claim**: LightThinker++'s commit/expand/fold primitives map directly to Brain's dreaming (commit), learning (expand), and forgetting (fold) interface.
**Confidence**: MEDIUM
**Source**: raw/research/lightthinker-plus.md
**Last verified**: 2026-04-13
**Contradicts**: nothing currently — complementary to Memento (Memento = how to compress, LT++ = when to compress/expand/re-compress)

**Claim**: Neural Computers (Meta/KAUST/Schmidhuber) represent Brain's long-term architectural horizon — computation, memory, and I/O unified in a single learned state — but are not near-term actionable.
**Confidence**: SPECULATIVE (paradigm-level claim)
**Source**: raw/research/neural-computers-meta.md, arXiv:2604.06425
**Last verified**: 2026-04-13
**Contradicts**: nothing currently — Brain's current agent-shaped design is transitional, NC is the direction
