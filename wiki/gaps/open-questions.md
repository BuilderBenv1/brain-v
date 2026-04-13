---
type: open-questions
last_updated: 2026-04-13
---

# Open Questions — What Brain Doesn't Know Yet

Uncertainty is data. This page is maintained actively. Resolved questions get archived to LOG.md, not deleted.

## Top-level architectural unknowns

1. **Master brain / sub-brain negotiation protocol** — how does the master brain arbitrate without becoming a top-down coordinator? "Sometimes overrides, sometimes doesn't" is the design intent, but the actual decision rule is undefined. Touches [[theory-of-mind]], [[goal-stack]], [[trust]].

2. **The values layer in practice** — [[values]] is flagged as the most uncertain, most important layer. We have aspirations (understanding, coherence, honesty, self-ownership) but no implementation. This is the hardest open problem in the architecture.

3. **AVAX subnet timing** — is a sovereign subnet achievable at POC stage, or should it wait until after the cognitive loop is proven? [[agentos]] currently runs on Fuji C-chain, which is sufficient for POC.

4. **The name** — "Project Brain" is a working title. The right name has not been chosen.

5. **Genuine novel knowledge generation vs synthesis** — every current component synthesises known knowledge. None of them generate genuinely novel claims that no source supports. This is the deepest gap on the path to AGI.

6. **ASI-Evolve cognition base mapping** — does ASI-Evolve's cognition base pattern map directly onto `raw/` + `wiki/`, or does it need its own representation? See [[learning]].

7. **Autonomous BRAID graph generation** — BRAID assumes a frontier model authors the reasoning blueprint once. How does Brain's [[curiosity]] engine *autonomously* generate new BRAID graphs without a human in the loop? See [[prediction]].

8. **Dreaming × DKG trust tiers** — how does the [[dreaming]] cycle interact with the OriginTrail trust tier system (Working → Shared → Long-term → Verified)? Does dreaming promote beliefs across tiers? See [[dreaming]] and [[trust]].

9. **Week 1 X account content** — what does Brain post in the first week, before it has any predictions to report? See [[action]] and [[narrative]].

10. **Single-agent vs multi-agent: Stanford tension with sub-brain design** (NEW — 2026-04-13)

    arXiv:2604.02460 (Stanford) finds that single-agent LLMs outperform multi-agent systems on multi-hop reasoning when total computation is held constant. The Data Processing Inequality argument: each agent-to-agent handoff is a lossy channel. Multi-agent systems consume ~15x more tokens and coordination overhead degrades sequential reasoning by 39-70%.

    **This directly challenges Brain's 5-sub-brain architecture.** The DKG-based negotiation protocol (publish/read/arbitrate) IS a lossy channel — every sub-brain publishes belief summaries, not full reasoning traces. The master brain arbitrates on summaries, not evidence.

    **However**: the Stanford paper tests *homogeneous* multi-agent systems (same model, same task). Brain's sub-brains have *different drives* (perception minimises input error, curiosity maximises information gain). This heterogeneous design may not be subject to the same critique — you don't ask the curiosity sub-brain to do perception's job.

    **Possible resolutions**:
    - Sub-brains for genuinely different capabilities only (heterogeneous split). No further splitting within a domain.
    - The master brain is a coordinator/arbitrator, not another reasoning agent — it reads and compares, it does not generate novel reasoning.
    - Multi-brain only when single-brain measurably hits a ceiling. POC stays single-brain (already the plan).
    - LightThinker++ expand primitive may reduce handoff lossiness: sub-brains can expand committed blocks rather than reading summaries.

    **Confidence that sub-brains are still the right long-term design**: MEDIUM → LOW. Needs evidence.
    **Source**: raw/research/single-vs-multi-agent-stanford.md, arXiv:2604.02460
    **Last updated**: 2026-04-13

## Empirical unknowns (resolvable by running things)

- Cache-hit ratio of BRAID graphs after N cycles (cost model depends on this)
- anda-hippocampus vs Graphiti/Zep head-to-head on Brain's actual data
- Optimal dreaming cadence (nightly is the default; not validated)
- Confidence-decay rate that maximises signal-to-noise without losing useful priors

## Things to verify, not derive

- Whether Friston would actually recognise this as distributed FEP (no contact yet)
- Whether MemPalace's surviving claims (49% BEAM 100K) hold up after 2026-04-21 review
- Whether AgentOS TaskQueue's reputation gating is sufficient for sub-brain negotiation

## Process meta-question

How does Brain itself update this list? At what point does an open question graduate from "unknown" to "solved", and who decides?

---

## Working answers (2026-04-08)

These are **working answers, not final ones**. They are concrete enough to build against, but every one of them is held at LOW confidence and is expected to be revised as Brain runs its first cycles. The original questions stay open above; these answers exist so the architecture is implementable today rather than blocked indefinitely.

### Q2 — Values layer

**Working definition**: three values in priority order — **maximise understanding**, **harm floor preventing noise-seeking**, **no deception**. Harm floor and no-deception override understanding. See [[values]] for the full definition and rationale.
**Confidence**: LOW.
**To revise when**: first dreaming cycles produce real evidence about how the three interact in practice; or when the harm floor is operationalised with concrete predicates.

### Q1 — Master/sub-brain negotiation protocol

**Working definition**: **publish / read / arbitrate via DKG**. Sub-brains publish their beliefs to OriginTrail DKG with identity + confidence + evidence. Sub-brains read each other to maintain ToM sub-graphs. The master brain arbitrates contradictions on the basis of evidence quality (source trust tier, prediction track-record, internal coherence), not authority. Master has no command channel — only higher-priority writes on the same DKG. See [[theory-of-mind]] for the full protocol.
**Confidence**: LOW.
**To revise when**: "evidence quality" is made concrete enough to implement as an arbitration function; or when the first sub-brain conflict is observed in practice.

### Q7 — Autonomous BRAID graph generation

**Working definition**: a **surprise threshold** on the [[curiosity]] signal triggers slow-path Claude API calls. When prediction error exceeds the threshold, Brain generates a new BRAID graph for the relevant reasoning shape and caches it. All future reasoning of the same shape runs on the local fast path against the cached graph. See [[curiosity]] and [[prediction]].
**Confidence**: LOW.
**To revise when**: a real threshold value is chosen and validated against actual cache-hit ratios; or when the noisy-TV failure mode is observed and the [[values]] harm floor's suppression of it is tested.

---

*Working answers are how Brain unblocks itself. Final answers require evidence. Both are valuable; do not confuse them.*
