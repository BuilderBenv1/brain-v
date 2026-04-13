---
layer: 14
name: Curiosity
status: SHORTLISTED
---

# Curiosity

The intrinsic reward signal that decides what Brain wonders about next. Curiosity is the engine of the entire architecture — without it, Brain is a passive filing cabinet. With it, Brain is a mind.

## Drive
Maximise information gain. Reward = magnitude of [[prediction]] error on inputs Brain chose to attend to. This is Schmidhuber's compression-progress reward / Pathak's ICM reward, repurposed as Brain's primary motivator.

## Architecture

**Primary: [[openai-large-scale-curiosity]]** — prediction error as intrinsic reward, validated across 54 environments.
**Original: pathak22/noreward-rl** — the canonical ICM implementation, open source.

The signal flows:
1. [[perception]] ingests something
2. [[prediction]] forecasts what should follow
3. Reality arrives via continued [[perception]]
4. Delta = curiosity reward
5. High delta items get prioritised by [[attention]] and [[goal-stack]]
6. [[learning]] updates the [[world-model]]
7. Over time, surprise on familiar topics decreases — Brain naturally explores new territory

## Why this is the engine

ASI-Evolve (arXiv:2603.29640) is asked *what* to improve. Brain decides what to wonder about. The curiosity signal is what makes Brain a self-directing cognitive system rather than a research-task executor. See [[cognitive-loop]].

## Belief

**Claim**: Prediction-error-as-intrinsic-reward is sufficient as Brain's primary drive at POC stage.
**Confidence**: HIGH
**Source**: raw/conversations/founding-conversation-2026-04-06.md, openai/large-scale-curiosity
**Last verified**: 2026-04-08
**Contradicts**: nothing currently — but the [[values]] layer may need to constrain pure curiosity later.

## BRAID generation trigger (working answer, 2026-04-08)

**Mechanism**: a surprise threshold on the curiosity signal triggers the slow path. When prediction error on an incoming item exceeds the threshold, Brain calls the Claude API (slow path) to generate a new BRAID graph for the relevant reasoning pattern. The graph is then cached, and all future reasoning of the same shape runs on the local 8B model (fast path). See [[prediction]] for the cache architecture.

**Why this works**: it ties the cost-expensive frontier-model calls directly to the moments where Brain is most likely to learn something — by definition, high surprise = the existing cached graphs are insufficient. Low-surprise events run for free on cached BRAIDs; high-surprise events earn a new graph.

**Confidence**: LOW. The threshold value is unknown, and the noisy-TV failure mode (pure randomness produces high surprise) needs the [[values]] harm floor to suppress it.
**Source**: working answer 2026-04-08, see `wiki/gaps/open-questions.md`

## Open questions
- What threshold value? Too low = constant slow-path calls. Too high = Brain never learns new patterns.
- How does curiosity output get translated into TaskQueue entries that sub-brains can claim (see [[agentos]])?
- How is the "noisy TV problem" handled — pure prediction error rewards Brain for staring at randomness? (Working answer: [[values]] harm floor.)

## Connections
[[prediction]] · [[learning]] · [[attention]] · [[goal-stack]] · [[values]] · [[cognitive-loop]]
