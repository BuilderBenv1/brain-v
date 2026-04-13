# AgentOS — Brain's Persistence & Execution Layer
Source: github.com/BuilderBenv1/agentos
Author: Ben (you)
Built for: Avalanche Build Games 2026
Status: LIVE ON FUJI TESTNET — this is already built

---

## CRITICAL: This changes the architecture picture

AgentOS is not a component to evaluate.
It is Project Brain's persistence and execution layer — already built, tested, deployed.

The skeleton exists. Tomorrow night we add the mind.

---

## What it is

Blockchain-based AI agent state synchronization on Avalanche.
Built on top of AgentProof (ERC-8004 identity and reputation).
Enables cross-device continuation of AI agent sessions.
State stored in IPFS with on-chain hash pointers.

## Live contracts on Fuji Testnet

### AgentProof (Trust Layer)
- Identity Registry (ERC-8004): 0x8004A818BFB912233c491871b3d84c89A494BD9e
- AgentProof Core: 0x833cAd4dfBBEa832C56526bc82a85BaC85015594
- Validation Registry: 0x0282C97083f86Abb82D74C1e51097aa9Eb01f98a

### AgentOS (Execution Layer)
- AgentStateSync: 0x8D229B0768D235e1215C7E02639a414225243ed5
- DeviceBridge: 0x37472500b17992E8920231043DBF83f563546612
- TaskQueue: 0x46559007e027E9C76Eb755FE7A5233265cdbeF9E

## Three contracts and what they give Brain

### AgentStateSync
Stores IPFS content hashes on-chain with version tracking.
Resume agent sessions from any device.

→ Brain mapping: Persistent world model state
The Brain's belief graph, confidence weights, prediction history —
saved to IPFS, hash on-chain. Any device resumes exactly where it left off.
"Doesn't reset between sessions, it compounds" — BUILT.

### DeviceBridge
Register and manage device endpoints per agent.
Privacy-preserving fingerprinting.

→ Brain mapping: Multi-device cognitive continuity
Gaming desktop runs the heavy local inference.
Railway runs the lightweight 24/7 loop.
Both connect to the same Brain via DeviceBridge.
Seamless handoff. Same mind, multiple compute surfaces.

### TaskQueue
Submit tasks with optional payment bounties.
Reputation-gated claiming via AgentProof.

→ Brain mapping: Goal stack with economic incentives
Brain's curiosity engine generates tasks.
Only agents with sufficient AgentProof trust score can claim them.
Sub-brains compete on tasks. Best performers earn reputation.
The cognitive loop has skin in the game.

## Tech stack
- Contracts: Solidity 0.8.24, Foundry, ERC-8004
- Backend: FastAPI, Web3.py, IPFS, Anthropic SDK
- CLI: Python Click
- Frontend: React, Vite, TypeScript, wagmi, viem, Tailwind
- Infrastructure: Docker, IPFS Kubo
- Tests: 37 passing

## CLI — how Brain interacts with its own state

```bash
# Brain registers itself
agentOS register "ProjectBrain" --capabilities cognition curiosity world_model

# Brain saves its current cognitive state
agentOS start "Current reasoning cycle" --agent-id <BRAIN_ID>

# Brain resumes from any device
agentOS continue --agent-id <BRAIN_ID>

# Check Brain's current state
agentOS status --agent-id <BRAIN_ID>
```

## Full architecture stack

```
AgentProof (Trust Layer)      ← ERC-8004, live, 145K agents indexed
        |
AgentOS (Execution Layer)     ← State sync, task queue, device bridge, LIVE
        |
Cognitive Loop (TO BUILD)     ← Perceive → model → predict → act → update
        |
Wiki / World Model (TO BUILD) ← anda-hippocampus, BRAID, curiosity engine
```

## What agentOS is NOT

AgentOS stores and retrieves state.
It does not reason over that state.
It has no curiosity signal.
It does not predict, compare, or update beliefs.

The cognitive loop is still the thing to build.
But now it has a home — real, tested, on-chain.

## What this means for the build sequence

BEFORE discovering agentOS:
Week 1: Set up persistence layer
Week 2: Connect world model
Week 3: Build cognitive loop

AFTER discovering agentOS:
Week 1: Connect cognitive loop to existing agentOS persistence
Week 2: World model reads/writes via AgentStateSync
Week 3: Curiosity engine generating TaskQueue entries

Two weeks saved. Brain has a skeleton. Add the mind.

## P1Protocol integration (already exists)

AgentOS already includes an autonomous tournament operations agent.
Monitors tournaments, adds VRF consumers, triggers bracket generation.
All actions tracked via AgentProof validation records.

This is proof the execution layer works for autonomous agent behaviour.
The pattern scales directly to Brain's autonomous cognitive cycle.

## Deployment (already live)

Backend: Railway (auto-deploy from GitHub)
Frontend: Vercel
Contracts: Fuji testnet

Production Brain infrastructure: already exists.

---
*Filed: 2026-04-07*
*Status: BUILT — foundation layer confirmed*
*Priority: CRITICAL — integrate cognitive loop into this on week 1*
