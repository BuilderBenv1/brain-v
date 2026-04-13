# Hermes Agent — LLM-Wiki Skill
Source: github.com/NousResearch/hermes-agent/pull/5100
Author: teknium1 (NousResearch founder)
Published: April 4, 2026
Status: RAW — to be compiled into wiki

---

## What it is

NousResearch's Hermes Agent (28.5K stars, serious AI lab) has merged
Karpathy's LLM-Wiki pattern as a native built-in skill.

One command: `/llm-wiki <research topic>`

Agent autonomously:
- Studies the web, code, and papers on the topic
- Builds a persistent interlinked markdown knowledge base
- Outputs an Obsidian vault
- Keeps it current as new sources arrive

Update with: `hermes update`

## Why this matters

Traditional RAG rediscovers knowledge from scratch per query.
LLM-Wiki compiles once, keeps current. Cross-references and synthesis compound.

This is the Karpathy wiki pattern implemented by a credible lab
as production-grade agent infrastructure. Not a weekend project.

## Relevance to Project Brain

### What Hermes gives you for free
- Autonomous web ingestion pipeline
- Wiki compilation from code + papers + web
- Obsidian vault output with backlinks
- Proven, maintained codebase (28.5K stars)

### What Hermes cannot do
- Genuine curiosity signal (it doesn't decide what to research)
- Prediction engine (no forward simulation)
- Dreaming cycle (no offline consolidation)
- Self-model (no beliefs about its own capabilities)
- On-chain sovereignty (no identity, no trust layer)
- The cognitive loop (perceive → model → predict → act → update)

Hermes = the perception + world model pipeline
Project Brain = the mind that directs it

### Strategic decision

**Option A: Build wiki layer from scratch**
Use Claude Code + CLAUDE.md schema already set up.
Full control. More setup. Already partially done.

**Option B: Use Hermes as the wiki engine**
Let Hermes handle ingestion + compilation.
Build cognitive loop on top.
Faster to get to the interesting parts.
Dependency on NousResearch roadmap.

**Recommendation: Hybrid**
Run both in parallel initially.
Hermes for broad research ingestion (web + papers).
Claude Code + CLAUDE.md for Brain's own self-knowledge base.
Compare outputs. Merge the best of both.

### Practical use tomorrow night
After desktop setup:
1. Install Hermes: `hermes update`
2. Run: `/llm-wiki cognitive architecture AGI world models`
3. Let it build overnight
4. Morning: compare to Brain's own wiki
5. Ingest Hermes output into raw/research/ if useful

## For the wiki
- Update wiki/components/library.md — add Hermes as TOOL (perception pipeline)
- Update wiki/layers/perception.md — Hermes as candidate ingestion engine
- Update wiki/concepts/wiki-pattern.md — Karpathy → Nick Spisak → Hermes evolution

---
*Filed: 2026-04-07*
*Status: SHORTLISTED as perception pipeline tool*
