---
layer: 1
name: Perception
status: TO BUILD
---

# Perception

How Brain ingests the world. Converts raw external signals (web pages, papers, tweets, code, conversations) into structured episodic entries that can flow into [[attention]] and [[world-model]].

## Drive
Minimise prediction error on incoming input. Perception is "good" when what arrives matches what was expected — surprise is the signal that the [[world-model]] is wrong.

## Candidate components

**[[hermes-agent]] (NousResearch)** — SHORTLISTED as the primary ingestion engine.
- One command (`/llm-wiki <topic>`) autonomously studies web + code + papers and outputs an Obsidian-style interlinked markdown vault.
- Gives Brain a credible, maintained perception pipeline for free (28.5K stars).
- Does NOT decide *what* to research — that is Brain's [[curiosity]] layer.

**Custom web scraper → `raw/`** — fallback for sources Hermes does not cover (X timeline, specific repos).

## Belief

**Claim**: Hermes Agent is the right perception pipeline for Brain's web/paper/code ingestion.
**Confidence**: MEDIUM
**Source**: raw/research/hermes-agent-llm-wiki.md
**Last verified**: 2026-04-08
**Contradicts**: nothing currently

## Open questions
- Does Hermes' Obsidian-vault output format play nicely with Brain's `wiki/` structure or do we need a translator?
- How does Brain's [[curiosity]] signal feed back into Hermes' topic selection?

## Connections
[[attention]] · [[world-model]] · [[curiosity]] · [[hermes-agent]]
