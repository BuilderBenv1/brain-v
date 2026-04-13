---
layer: 12
name: Forgetting
status: TO BUILD — operational model now defined (commit/expand/fold)
---

# Forgetting

Confidence decay and pruning rules. Forgetting is not a bug — it is signal-to-noise maintenance. Without it, the [[world-model]] silts up with stale, low-evidence, and contradicted beliefs that drag down [[prediction]] quality.

## Drive
Maximise signal-to-noise in the [[world-model]]. Drop beliefs whose marginal contribution to prediction is negative.

## Operational model: commit / expand / fold

LightThinker++ (arXiv:2604.03679) provides the three memory primitives that define how forgetting actually works in Brain:

**Commit** (→ [[dreaming]]): archive a reasoning step or cycle as a compact summary. The full trace is replaced by the summary. This is what the [[dreaming]] cycle does when it compresses episodic entries into semantic beliefs.

**Expand** (→ [[learning]]): retrieve raw evidence behind a committed summary when a belief is challenged. If Brain needs to re-evaluate a compressed belief, it expands back to the original reasoning. This is the reversibility mechanism — forgetting is not permanent destruction, it is compression with a retrieval escape hatch.

**Fold** (→ forgetting): re-compress an expanded block back to its summary after use. Expand → use → fold is the "look, learn, re-forget" pattern. Context hygiene: don't leave expanded blocks lying around consuming the window.

Results from LightThinker++: 69.9% peak token reduction, +2.42% accuracy gain, stable performance past 80 rounds in agentic tasks (+14.8% average gain). This is evidence the pattern works at the cycle counts Brain targets.

### Compression mechanism: Memento

Memento (Microsoft) provides the HOW inside commit and fold — trained context compression, ~6x ratio, 228K open training traces. LightThinker++ provides the WHEN (commit/expand/fold decisions). Brain may use both: Memento as the compressor inside LightThinker++'s memory management primitives.

## Other mechanisms

- **Confidence decay** — beliefs with no recent supporting evidence drop one tier per N cycles (HIGH → MEDIUM → LOW → SPECULATIVE → pruned)
- **Contradiction resolution** — when two beliefs conflict and one has decisively better evidence, the loser is demoted, not silently overwritten (CLAUDE.md rule)
- **Pre-output validation** — contradiction detection (catches wrong names, ages, confidence before [[action]])
- **Orphan pruning** — concepts mentioned but never explained, beliefs with no inbound links (surfaced by the weekly health check)

## Beliefs

**Claim**: LightThinker++'s commit/expand/fold primitives are the right operational model for Brain's forgetting layer.
**Confidence**: MEDIUM
**Source**: raw/research/lightthinker-plus.md, arXiv:2604.03679
**Last verified**: 2026-04-13
**Contradicts**: nothing currently

**Claim**: Memento is the right compression mechanism inside the commit/fold primitives, superseding MemPalace AAAK.
**Confidence**: MEDIUM
**Source**: raw/research/memento-microsoft.md
**Last verified**: 2026-04-13
**Contradicts**: any residual reliance on MemPalace AAAK

## Open questions
- What is the right decay rate? Too fast = Brain forgets useful priors; too slow = noise accumulates.
- Should forgetting respect [[trust]] tier? (Verified DKG beliefs probably should not decay on the same schedule as Working Memory.)
- How deep is the expand retrieval? Can Brain recover raw evidence from N cycles ago, or only the most recent committed block?
- The "erased but still retained" effect from Memento (KV cache traces survive masking) — does this mean true forgetting is impossible, and if so, what are the implications for the [[self-model]]?

## Connections
[[world-model]] · [[dreaming]] · [[learning]] · [[trust]] · [[self-model]]
