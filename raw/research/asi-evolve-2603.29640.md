# ASI-Evolve: AI Accelerates AI
Source: arXiv:2603.29640
Published: March 31, 2026
Authors: Weixian Xu, Tiantian Mi, Yixiu Liu, Yang Nan, Zhimeng Zhou, Lyumanshan Ye, Lin Zhang, Yu Qiao, Pengfei Liu
Status: RAW — to be compiled into wiki

---

## Core question
Can AI accelerate the development of AI itself?

## What it is
An agentic framework for AI-for-AI research that closes the loop through a
learn → design → experiment → analyze cycle.

First unified framework to demonstrate AI-driven discovery across three
central components of AI development: data, architectures, and learning algorithms.

## Two key components added to standard evolutionary agents

### 1. Cognition Base
Injects accumulated human priors into each round of exploration.
Prevents agents from rediscovering known dead ends.
The accumulated knowledge of previous cycles shapes what gets explored next.

### 2. Dedicated Analyzer
Distills complex experimental outcomes into reusable insights for future iterations.
Turns raw results into structured knowledge that compounds.
Separates "what happened" from "what it means."

## Relevance to Project Brain

### Direct mappings
ASI-Evolve cycle → Brain cognitive loop:
- Learn → Perceive + World Model update
- Design → Prediction + Goal Stack
- Experiment → Action
- Analyze → Learning + Dreaming

Cognition Base → Brain's raw/ + wiki/ combined
The accumulated prior knowledge injected into each cycle.

Dedicated Analyzer → Brain's dreaming cycle
Offline consolidation that turns episodic outcomes into semantic beliefs.

### The critical difference
ASI-Evolve: applied to AI research specifically (architectures, data, algorithms)
Project Brain: applied to understanding in general — curiosity signal decides what to research

ASI-Evolve is asked what to improve. Brain decides what to wonder about.

### Why this matters
Empirical proof that the learn-design-experiment-analyze cycle works at scale
for genuinely hard, long-horizon, weakly-supervised problems.

This is the closest published validation of the cognitive loop architecture.

## For the wiki
- Update wiki/layers/learning.md — reference ASI-Evolve's analyzer pattern
- Update wiki/layers/dreaming.md — cognition base as prior injection mechanism  
- Update wiki/components/library.md — add ASI-Evolve as RESEARCH reference
- Create wiki/concepts/cognitive-loop.md — synthesise Brain loop vs ASI-Evolve loop

---
*Filed: 2026-04-06*
