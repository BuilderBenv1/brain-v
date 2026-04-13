---
type: concept
name: Economic Layer
status: ARCHITECTURE — not built, required before week 3
last_updated: 2026-04-09
---

# Economic Layer

The incentive structure — how Brain's outputs accrue value and how that value feeds back into what Brain prioritises next. Economics is what closes the gap between "Brain is curious" and "Brain is useful." Without it, [[curiosity]] is unconstrained and Brain wanders. With it, Brain learns to be curious *about things that matter*.

## Why this matters

Week 1's cognitive loop has a drive ([[curiosity]]) and a scoring mechanism (`score.py`). But the loop has no concept of *value*. Every prediction topic is treated equally. Every paper is equally worth perceiving. Every belief update has the same weight.

In reality:
- Some predictions are more valuable than others (predicting a paradigm shift > predicting a keyword)
- Some knowledge domains have more downstream impact than others
- Brain's time and compute are finite — pure curiosity doesn't allocate them efficiently
- If Brain ever earns revenue (API access, predictions-as-a-service, X audience), that revenue signal should feed back into priority

Economics is the layer that introduces scarcity, priority, and return-on-investment into the cognitive loop.

## Two kinds of value

### 1. Internal value — prediction utility

How much does knowing X improve Brain's future predictions? This is information-theoretic value, already partially captured by the [[curiosity]] signal (prediction error ≈ information gain). But curiosity is local ("this surprised me") while value is global ("knowing this makes me better at everything").

Internal value feeds back into [[attention]] scoring and [[goal-stack]] priority. High-value knowledge domains get more perception cycles. Low-value domains decay via [[forgetting]].

### 2. External value — output utility

How much does Brain's output matter to anyone besides Brain? This is economic value in the traditional sense:

| Output | Value signal | How measured |
|---|---|---|
| X posts | Engagement (likes, replies, reposts) | X API metrics |
| Predictions | Accuracy over time, measured by [[verification-layer]] | Binary hit rate |
| Knowledge base | Usefulness to people who query it | Query frequency, citation |
| TaskQueue results | Sub-brain task completion quality | AgentProof reputation scores |

External value is noisier than internal value but more important for sustainability. Brain needs compute, and compute costs money (£50/month POC, £5K–15K/month real phase per [[master-architecture]]). External value is how that gets funded.

## Architecture sketch

```
[[curiosity]] signal (what surprises Brain)
    +
[[verification-layer]] (what Brain got right/wrong)
    +
External value signals (engagement, accuracy track record, query demand)
    ↓
Economic scoring function
    ↓
Weighted priority → [[attention]] and [[goal-stack]]
    ↓
Brain allocates perception + prediction cycles accordingly
```

The economic layer does NOT replace curiosity. It *weights* curiosity. A topic that is both surprising AND externally valuable gets more cycles than a topic that is only surprising. Pure curiosity is the tiebreaker when economic signals are absent or equal.

## Integration with AgentOS

[[agentos]]'s TaskQueue already has economic primitives:
- Tasks can carry **payment bounties**
- Sub-brains claim tasks based on **AgentProof reputation**
- Completion quality feeds back into reputation scores

This is already an economic loop — sub-brains that do good work get more access to high-value tasks. The economic layer formalises it: Brain's [[curiosity]] engine generates tasks, the economic layer assigns bounty weights based on expected value, and sub-brains compete.

## Integration with Avalanche

Long-term (post-POC), the AVAX subnet provides:
- **Token-gated access** to Brain's prediction outputs
- **Staking** on prediction accuracy (Brain puts tokens behind its claims)
- **Marketplace** for knowledge — other agents pay to query Brain's world model via DKG

This is phase 2/3. But the architecture needs to accommodate it now, or the economic layer becomes a retrofit.

## Belief

**Claim**: Without an economic layer, Brain's curiosity signal will not efficiently allocate finite compute across knowledge domains — it will explore broadly but not deeply in the directions that matter.
**Confidence**: MEDIUM
**Source**: founding conversation ("the cognitive loop has skin in the game"), analogy to RL reward shaping
**Last verified**: 2026-04-09
**Contradicts**: nothing currently — but the pure-curiosity camp (Schmidhuber, Pathak) would argue that information gain IS the right allocation signal and economic weighting distorts exploration. This tension is real and unresolved.

**Claim**: AgentOS TaskQueue bounties are the right primitive for the economic layer's sub-brain incentive mechanism.
**Confidence**: MEDIUM
**Source**: raw/research/agentos-built.md (TaskQueue with bounties already implemented)
**Last verified**: 2026-04-09
**Contradicts**: nothing currently

## Open questions
- How does Brain avoid Goodharting on external value signals? (Optimising for X engagement could make Brain a content farm, not a mind.)
- What is the exchange rate between internal value (information gain) and external value (engagement, revenue)? Who sets it?
- Should economic signals be allowed to override [[values]]? (No — the harm floor and no-deception constraints are not negotiable. But how is that enforced?)
- When does Brain start earning? The X account is gated on "loop demonstrably working." The economic layer is gated on the verification layer. What is the minimum viable economic cycle?

## Connections
[[curiosity]] · [[attention]] · [[goal-stack]] · [[verification-layer]] · [[trust]] · [[action]] · [[values]] · [[agentos]] · [[master-architecture]]
