# Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets
Source: arXiv:2604.02460
Authors: Stanford-affiliated researchers
Published: 2026-04-03
Status: RAW — to be compiled into wiki

---

## Core finding

When you control for total computation (thinking tokens), single-agent LLMs outperform multi-agent systems on multi-hop reasoning tasks. The reported advantages of multi-agent systems are largely explained by unaccounted computation and context effects, not inherent architectural benefits.

## Key results

- **Single-agent systems are more information-efficient** when reasoning tokens are held constant
- **Significant artifacts in API-based budget control** — standard benchmarks inflate apparent multi-agent gains by not accounting for total tokens consumed
- **Data Processing Inequality argument**: under a fixed reasoning-token budget and with perfect context utilization, a single-agent pipeline loses less information than a multi-agent one (each handoff between agents is a lossy channel)
- Tested across three model families: Qwen3, DeepSeek-R1-Distill-Llama, and Gemini 2.5
- Multi-agent systems consume ~15x more tokens than single-agent
- Coordination overhead degrades sequential reasoning performance by 39-70%

## The information-theoretic argument

Multi-agent handoffs are lossy channels. Each time Agent A passes context to Agent B, information is lost (the full reasoning trace is summarised or truncated). A single agent with the same total token budget retains the full reasoning chain. Therefore, under fixed computation, single > multi.

## The nuance

The paper does NOT say multi-agent is always worse. It says:
1. Most benchmarks don't control for total computation → inflated multi-agent scores
2. When you DO control, single-agent wins on multi-hop reasoning
3. Multi-agent may still win on parallelisable tasks, diverse expertise, or adversarial robustness

## CRITICAL — Relevance to Project Brain

### This directly challenges the sub-brain architecture

Brain's master-architecture designs 5 sub-brains (perception, memory, curiosity, self-model, theory-of-mind) communicating via DKG. The Stanford paper says this is information-lossy by construction — every sub-brain handoff loses context.

### The tension

**Pro sub-brain**: Brain's sub-brains have DIFFERENT drives (perception minimises input error, curiosity maximises information gain, etc.). They are not copies of the same agent doing the same task — they are genuinely different minds. The Stanford paper tests homogeneous multi-agent systems (same model, same task). Brain's heterogeneous design may not be subject to the same critique.

**Anti sub-brain**: The DKG-based negotiation protocol (publish/read/arbitrate) IS a lossy channel. Every time sub-brain A publishes a belief summary to the DKG, the full reasoning trace behind that belief is lost. The master brain arbitrates on summaries, not evidence.

**Possible resolution**: Sub-brains for genuinely different capabilities (heterogeneous), but within each sub-brain's domain, use a single-agent architecture (no further splitting). The master brain is a coordinator, not another reasoning agent. This is already close to what Brain designs, but the Stanford paper says it needs to be explicit: minimize handoffs, maximize within-agent reasoning depth.

### Build sequence implication

POC phase already uses a single-brain design (correct per Stanford). The multi-brain architecture should ONLY be introduced when there is measurable evidence that a single brain is hitting capability ceilings in specific domains — not as a default design choice.

## For the wiki
- Update wiki/gaps/open-questions.md — flag the single-vs-multi tension
- Update wiki/concepts/master-architecture.md — add Stanford caveat to sub-brain design
- Update wiki/layers/theory-of-mind.md — negotiation protocol needs the lossy-channel risk noted

---
*Filed: 2026-04-13*
*Status: CRITICAL — directly challenges a core architectural assumption*
