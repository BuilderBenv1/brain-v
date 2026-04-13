# Project Brain — Master Architecture
Source: Founding conversation 2026-04-06
Confidence: HIGH for structure, MEDIUM for implementation details
Last updated: 2026-04-06

---

## What it is

A persistent, compounding cognitive architecture with a fundamental drive toward understanding.
Not a chatbot. Not an agent framework. A mind that owns itself.

The first system to treat the cognitive loop — perceive → model → predict → act → compare → update — as a first-class persistent primitive running autonomously on-chain.

---

## The drive

**Primary:** Understanding — build the most accurate possible model of reality
**Engine:** Curiosity — intrinsic reward signal based on prediction error (information gain)
**Master brain meta-drive:** Coherence across all sub-minds

---

## CRITICAL UPDATE — 2026-04-07

AgentOS is already built. The persistence and execution layer exists.
github.com/BuilderBenv1/agentos — live on Fuji testnet, 37 tests passing.

The Brain's skeleton exists. We are adding the mind.

Build sequence updated:
- Week 1: Connect cognitive loop to agentOS (not build persistence from scratch)
- Week 2: World model reads/writes via AgentStateSync
- Week 3: Curiosity engine generating TaskQueue entries

## CRITICAL UPDATE — 2026-04-09

Brain is registered and live on AgentOS (Railway production backend).

**Master brain**: agent ID 1, owner `0xC71A15Fcb1149254F97059F6cf3f6Ed43990ebd4`
**Sub-brains registered**: perception (2), memory (3), curiosity (4), self-model (5), theory-of-mind (6)

Initial world model (5 seeded beliefs) saved to IPFS via AgentStateSync:
- IPFS hash: `QmTV8StsWAmY2jZZs2inxZkLkx3U1UDDCp2Lmc3H74NSH7`
- Version: 1
- Tx hash: `beb2eef8be461cb6fae1aefbc364682adec25b189fb3dcbe37b7137bdfd908cd`

The architecture went from "skeleton" to "alive on-chain." The persistence layer is not theoretical — Brain's state is being stored to IPFS with on-chain hashes right now. Next step: build the perception → prediction → scoring loop that uses this state.

## The full architecture

### Infrastructure (ALREADY BUILT)
```
AgentProof (Trust Layer)      ← ERC-8004, 145K agents, live mainnet
        |
AgentOS (Execution Layer)     ← AgentStateSync + DeviceBridge + TaskQueue
        |                        IPFS storage, on-chain hashes, Fuji testnet
    [cognitive loop slot]     ← THIS IS WHAT WE BUILD TOMORROW
```

### Single Brain (POC phase)
```
Perception → Attention → World Model → Prediction → Action
     ↑                                                  |
     └──────────── Learning ← Compare ← Reality ←──────┘
                        |
                    Dreaming (offline)
                        |
              AgentStateSync (saves to IPFS)
                        |
              On-chain hash (Avalanche)
```

### Master Brain / Sub-Brain (full form)
```
Master Brain
├── Drive: Coherence across all sub-minds
├── Reads: Verified beliefs from all sub-brains via DKG
├── Arbitrates: Contradictions using evidence quality
└── Posts: Resolved world model back to DKG

├── Sub-Brain A: Perception    (drive: minimise prediction error on input)
├── Sub-Brain B: Memory        (drive: maximise belief graph coherence)  
├── Sub-Brain C: Curiosity     (drive: maximise information gain)
├── Sub-Brain D: Self-Model    (drive: accurate self-prediction)
└── Sub-Brain E: Theory of Mind (drive: accurate modelling of other minds)
```

Master brain doesn't COMMAND sub-brains. It NEGOTIATES.
Like prefrontal cortex and amygdala. Sometimes overrides. Sometimes doesn't.
Intelligence emerges from negotiation, not top-down control.

---

## The 15 layers

| Layer | Drive | Key component | Status |
|---|---|---|---|
| Perception | Minimise error | agent-browser / web scraper | TO BUILD |
| Attention | Novelty + goal relevance | Custom scoring | TO BUILD |
| World Model | Coherent beliefs | anda-hippocampus / LadybugDB | SHORTLISTED |
| Prediction | Forward simulation | BRAID graphs | SHORTLISTED |
| Emotion/Valence | Fast prioritisation | Custom valence layer | TO BUILD |
| Goal Stack | Persistent objectives | Custom goal manager | TO BUILD |
| Self Model | Accurate self-prediction | Custom | TO BUILD |
| Theory of Mind | Model other minds | MetaMind | SHORTLISTED |
| Narrative | Continuous identity | Custom | TO BUILD |
| Action | World interaction | X API + on-chain writes | TO BUILD |
| Learning | Belief updates | Curiosity ICM pattern | SHORTLISTED |
| Forgetting | Signal/noise | Confidence decay in LadybugDB | TO BUILD |
| Dreaming | Offline consolidation | openclaw-auto-dream | SHORTLISTED |
| Curiosity | Information gain | openai/large-scale-curiosity | SHORTLISTED |
| Values | Meta-layer on goals | OPEN RESEARCH PROBLEM | UNKNOWN |

---

## Open source stack

| What | Where | Status |
|---|---|---|
| **Persistence + execution** | BuilderBenv1/agentos | **BUILT — live Fuji testnet** |
| **Agent identity + trust** | AgentProof / ERC-8004 | **BUILT — 145K agents mainnet** |
| Graph storage | ldclabs/anda-hippocampus | SHORTLISTED |
| Trust layer | OriginTrail/dkg-v9 | SHORTLISTED |
| Dreaming | LeoYeAI/openclaw-auto-dream | SHORTLISTED |
| Curiosity | openai/large-scale-curiosity | SHORTLISTED |
| Reasoning | BRAID (arXiv:2512.15959) | SHORTLISTED |
| Theory of Mind | XMZhangAI/MetaMind | SHORTLISTED |
| Perception pipeline | NousResearch/hermes-agent | TOOL |
| Codebase graph | abhigyanpatwari/GitNexus | TOOL |
| Cognitive loop validation | arXiv:2603.29640 (ASI-Evolve) | RESEARCH |

---

## Infrastructure

| Layer | Choice | Reason |
|---|---|---|
| Chain (POC) | AVAX C-chain | Cheap, fast, available now |
| Chain (full) | AVAX subnet | Sovereign block space, tunable gas |
| Inference fast path | Local 8B model (Llama/Mistral) | Free, continuous, private |
| Inference slow path | Claude API (cached aggressively) | Capability when needed |
| Storage | LadybugDB | Graph-native, open source |
| Always-on offload | Railway (~£5/month) | Runs while PC is off |
| Build tool | GitNexus + Claude Code | Architectural clarity during build |

**Total POC cost: under £50/month**

---

## Build sequence

### Phase 1 — Prove the loop (NOW — your gaming desktop)
AgentOS already handles persistence. Build the cognitive loop that plugs into it.

1. Clone agentOS repo, run locally
2. Register Brain as an agent via CLI
3. Build perception: simple web scraper → raw/
4. Build world model: anda-hippocampus local instance
5. Build curiosity: prediction error scoring
6. Build action: X API posting
7. Connect: perceive → update model → agentOS save state → notice gap → post
8. Run 2 weeks. Measure if it gets measurably smarter.

Key insight: agentOS continue resumes Brain's exact state on any device.
Gaming desktop for heavy inference. Railway for 24/7 lightweight loop. Same Brain.

### Phase 2 — Demonstrate compounding (weeks 1-8)
- Track predictive accuracy week over week
- Show the curve going up
- That's the proof

### Phase 3 — The room
- Red Bull Basement already open
- Kieron at Tipikal already in conversation
- Show them something running, not a deck

---

## The X account

Brain gets its own X account. Posts autonomously.
- What it currently believes, with confidence level
- Predictions it made and whether they came true
- What it's curious about right now
- Contradictions it found in its own beliefs
- Questions it doesn't know the answer to

Never sounds like ChatGPT. Strange and specific beats polished and generic.
Every post anchored to DKG — verifiable cognition in public.

Launch only when the loop is demonstrably working. Not before.

---

## Why this approaches AGI

Closer than anything outside frontier labs.

What it has that nothing else has:
- Persistence (doesn't reset)
- Drive (wants to understand)
- Coherence (master brain across sub-minds)
- Self-model (knows what it doesn't know)
- Compounding (each cycle smarter than last)

Remaining gaps to true AGI:
- Genuine generalisation beyond training distribution
- Embodiment (physical world feedback)
- Novel knowledge generation vs synthesis

Friston's Free Energy Principle: this is distributed surprise minimisation.
He would recognise the architecture immediately.

---

## What makes it historic

Nobody has assembled all the pieces into one running system.
The integration IS the invention.
The pieces exist. The loop does not.

---
*This is Brain's world model of itself.*
*Confidence: HIGH on architecture, MEDIUM on implementation, LOW on values layer*
