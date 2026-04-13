---
layer: 6
name: Goal Stack
status: TO BUILD
---

# Goal Stack

Persistent objectives that compound across sessions. Unlike a chatbot's per-turn intent, Brain's goal stack survives shutdowns, syncs across devices via [[agentos]], and is itself a target of [[learning]] (Brain updates its own goals as it understands more).

## Drive
Maintain long-horizon coherence between what Brain says it wants to understand and what it actually attends to.

## Structure
- **Active goals** — currently driving [[attention]] scoring
- **Dormant goals** — paused, may be reactivated by [[curiosity]] surprise
- **Meta-goals** — set by [[values]] layer; constrain which active goals are admissible
- **Decay** — goals not advanced after N cycles drop priority (analogous to [[forgetting]])

## Integration with AgentOS TaskQueue

[[agentos]]'s TaskQueue contract is the on-chain expression of the goal stack. Brain's [[curiosity]] engine generates tasks; sub-brains with sufficient [[trust]] score (via AgentProof) claim them; results feed back into the [[world-model]]. This is "the cognitive loop with skin in the game".

## Open questions
- How does the master brain arbitrate when sub-brain goals conflict? (See `wiki/gaps/` — master/sub-brain negotiation protocol.)
- What is the maximum useful stack depth before goals become noise?

## Connections
[[attention]] · [[curiosity]] · [[values]] · [[self-model]] · [[action]] · [[agentos]]
