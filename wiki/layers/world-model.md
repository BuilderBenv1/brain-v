---
layer: 3
name: World Model
status: SHORTLISTED (component selected, not yet integrated)
---

# World Model

Brain's belief graph — every claim it currently holds about reality, with confidence weights, sources, and contradictions. This is the substrate everything else operates on. [[perception]] writes to it, [[prediction]] reads from it, [[learning]] updates it, [[dreaming]] consolidates it, [[forgetting]] prunes it.

## Drive
Coherent beliefs. Maximise internal consistency and minimise contradiction across the graph.

## Architecture choice

**Primary candidate: [[anda-hippocampus]] (ldclabs)** — graph-native, sleep consolidation, contradiction detection, state evolution. Independent benchmark: 94.8% DMR.

**Alternative considered: MemPalace (method-of-loci hierarchy)** — wings → halls → rooms. Worth understanding as a retrieval primitive but compression claims (AAAK 30x lossless) were debunked by community review; it is lossy summarisation. Currently WATCH only. See raw/research/mempalace.md.

**Alternative considered: Graphiti / Zep** — bitemporal temporal knowledge graph, 94.8% DMR accuracy. RESEARCH.

**Alternative considered: MAGMA (arXiv Jan 2026)** — 4-graph architecture (semantic, temporal, causal, entity). RESEARCH.

## Belief

**Claim**: anda-hippocampus is the right world-model substrate for Brain.
**Confidence**: MEDIUM
**Source**: raw/conversations/founding-conversation-2026-04-06.md, CLAUDE.md
**Last verified**: 2026-04-08
**Contradicts**: nothing currently — but Graphiti/Zep matches the same independent benchmark and deserves head-to-head evaluation before commit.

## Belief format
Every node carries:
- **Confidence**: HIGH / MEDIUM / LOW / SPECULATIVE
- **Source**: pointer into `raw/`
- **Last verified**: date
- **Contradicts**: list of conflicting node IDs

## Persistence
Serialised to IPFS via [[agentos]] AgentStateSync. On-chain hash on Avalanche Fuji testnet. Brain resumes its full belief graph on any device via `agentOS continue`.

## Open questions
- Flat graph (anda-hippocampus) vs hierarchical palace (MemPalace) — which retrieves better for Brain's mix of episodic + semantic memory?
- How does the world model represent its own uncertainty about itself (boundary with [[self-model]])?

## Connections
[[perception]] · [[attention]] · [[prediction]] · [[learning]] · [[forgetting]] · [[dreaming]] · [[trust]] · [[agentos]] · [[anda-hippocampus]]
