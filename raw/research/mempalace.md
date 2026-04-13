# MemPalace — AI Memory System
Source: github.com/milla-jovovich/mempalace
Authors: Milla Jovovich (actress, The Fifth Element) + Ben Sigman (@bensig)
Published: April 2026
Status: RAW — to be compiled into wiki

---

## What it is

A local, private AI memory system built with Claude.
Mines conversations and organises them into a "palace" — a structured
hierarchical architecture with wings, halls, and rooms.

MIT licensed. No API key. No cloud. One dependency. Runs locally.

## Benchmark claims — POST COMMUNITY REVIEW (24 hours later)

Community tore it apart. Public correction shipped within hours.

What was debunked:
- AAAK "30x lossless compression" → lossy summarisation. FIXED.
- Token counts used len(text)//3 not a real estimator. FIXED.
- LoCoMo 100% was meaningless — top-k exceeded corpus size. ACKNOWLEDGED.
- 96.6% LongMemEval is session-level retrieval on ~50 candidates, not comparable to published papers.
- Palace structure contributed only a small amount to retrieval — vanilla ChromaDB did most of it.

What survived scrutiny:
- Independent BEAM 100K: 49% answer quality (honest number)
- It is a retrieval layer, not a reasoning engine

Community response despite issues: 14K stars, 2K forks, 70+ PRs, 11 bugs fixed.
Credibility partially restored by transparency and speed of correction.

**Confidence: MEDIUM for retrieval claims, LOW for compression claims**

## Two technically interesting components

### 1. Palace Architecture (method of loci)
Organises memory hierarchically: wings → halls → rooms
Mirrors how human spatial memory actually works.
Not a flat list of facts — a navigable structure.

Implication for Project Brain:
Current design is a belief graph. Hierarchical spatial organisation
may be a better retrieval primitive for certain memory types.
Worth evaluating against anda-hippocampus flat graph approach.

### 2. AAAK Compression — DEBUNKED
Claims to compress entire life context into ~120 tokens.
CLAIMED: 30x lossless compression.
ACTUAL: Lossy summarisation. Not lossless.

Implication for Project Brain:
Does NOT solve the context window ceiling problem as originally assessed.
Lossy summarisation introduces errors that compound in a belief graph.
Remove from consideration as a compression solution.

### 3. Contradiction Detection
Catches wrong names, pronouns, ages before output.
Pre-output validation layer.

Implication for Project Brain:
Exactly what the dreaming cycle needs.
Could be lifted directly as the belief validation step.

## What it is NOT

Not a cognitive loop. No curiosity. No prediction. No drive.
A very well-organised, potentially very efficient filing cabinet.
Same category as anda-hippocampus — world model layer only.

## Relationship to other components

| Component | MemPalace | anda-hippocampus |
|---|---|---|
| Storage structure | Hierarchical palace | Graph-native |
| Sleep consolidation | Unknown | Yes |
| Contradiction detection | Yes (pre-output) | Yes (graph traversal) |
| Compression | AAAK 120 tokens | Standard |
| On-chain | No | No |
| Benchmarks | Self-reported 100% | 94.8% DMR (independent) |
| Maturity | 6 commits | More established |

## Verdict

Not a replacement for anda-hippocampus. A competing approach.
AAAK compression technique worth studying regardless of benchmark validity.
Spatial palace architecture worth understanding as retrieval primitive.

**Action:** Monitor for independent benchmark reproduction.
If 100% LongMemEval holds up: elevate to SHORTLISTED for world model layer.
If benchmarks fail reproduction: extract AAAK compression concept only.

## For the wiki
- Update wiki/components/library.md — add MemPalace as WATCH
- Update wiki/layers/world-model.md — add palace architecture as alternative approach
- Update wiki/layers/forgetting.md — add contradiction detection pattern
- Create wiki/concepts/memory-compression.md — AAAK vs standard approaches

---
*Filed: 2026-04-07*
*Review date: 2026-04-21 (2 weeks — check for independent benchmark reproduction)*
