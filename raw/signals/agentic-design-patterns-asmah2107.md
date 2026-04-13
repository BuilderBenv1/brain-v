# Agentic System Design Patterns — Production Checklist
Source: @asmah2107 (Ashutosh Maheshwari), X post, April 2026
Status: RAW — scanned against Brain architecture

---

## The 15 patterns

1. Agent Circuit Breaker
2. Blast Radius Limiter
3. Orchestrator vs Choreography
4. Tool Invocation Timeout
5. Confidence Threshold Gate
6. Context Window Checkpointing
7. Idempotent Tool Calls
8. Dead Letter Queue for Agents
9. LLM Gateway Pattern
10. Semantic Caching
11. Human Escalation Protocol
12. Multi-Agent State Sync
13. Replanning Loop
14. Canary Agent Deployment
15. Agentic Observability Tracing

## Scan against Brain

### Already in Brain

| Pattern | Brain implementation | Status |
|---|---|---|
| Confidence Threshold Gate | Belief confidence system (HIGH/MEDIUM/LOW/SPECULATIVE) gates prediction weighting | BUILT |
| Context Window Checkpointing | AgentOS saves state to IPFS at every cycle, resume from any device | BUILT |
| Multi-Agent State Sync | AgentOS DeviceBridge + AgentStateSync, live on Fuji | BUILT |
| Replanning Loop | score.py updates beliefs and replans predictions each cycle | BUILT |
| Dead Letter Queue | Failed predictions logged to outputs/scores/ for analysis | BUILT (partial) |

### Gaps

| Pattern | Brain status | Priority |
|---|---|---|
| Agent Circuit Breaker | No graceful degradation — loop.py errors silently if Ollama or network fails | **HIGH — this week** |
| Blast Radius Limiter | No isolation between sub-brains. Failure in one could corrupt master world model | MEDIUM — needed before sub-brain parallelism |
| Agentic Observability Tracing | LOG.md is manual. No structured trace of belief → prediction → update chain | **HIGH — this week** |
| Human Escalation Protocol | No mechanism to flag "I'm uncertain, human should check." Values layer should trigger this | MEDIUM — needed before X account launch |
| Canary Agent Deployment | No way to test new belief update rules on one sub-brain before rolling to all | LOW — needed at multi-brain stage |
| Tool Invocation Timeout | Ollama calls have a 120s timeout but no retry/fallback | LOW |
| Semantic Caching | BRAID graph caching is the architectural answer but not yet built | LOW — week 2-3 |
| LLM Gateway Pattern | Direct Ollama calls, no gateway. Fine for POC | LOW |
| Idempotent Tool Calls | perceive.py overwrites same file if run twice — effectively idempotent | BUILT (incidental) |
| Orchestrator vs Choreography | Brain uses orchestration (loop.py drives everything). Choreography relevant at multi-brain stage | DEFERRED |

## Most urgent

Circuit breaker and observability tracing. The loop runs autonomously at 7am — silent failures are invisible until manually checked.

---
*Filed: 2026-04-13*
