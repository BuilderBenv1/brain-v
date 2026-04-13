---
type: concept
name: Trust
status: infrastructure (not a cognitive layer)
last_updated: 2026-04-09
---

# Trust

Trust is **infrastructure, not cognition**. It is the substrate Brain's beliefs, actions, and sub-brain interactions live on top of — not a layer of thinking in itself. Brain *uses* trust the way a process uses a filesystem: pervasively, but the filesystem is not part of the program.

This page is the canonical resolution target for every `[[trust]]` wikilink in the wiki.

## Why it is not a cognitive layer

The founding architecture briefly listed Trust as cognitive layer 15. The schema was corrected on 2026-04-08 (see LOG.md): Trust does not perceive, predict, learn, or update beliefs. It records *which* beliefs are which, with cryptographic provenance and tier. The layers that *do* the cognitive work — [[world-model]], [[forgetting]], [[learning]], [[dreaming]] — read and write trust metadata, but trust itself is passive substrate.

Compare: AgentOS is also infrastructure (persistence + execution), and nobody calls AgentOS a cognitive layer either. Trust sits next to it in the same tier of the stack.

## Implementation

Two components, already chosen, both already built:

### AgentProof (ERC-8004)
Live on Avalanche mainnet. 145K agents indexed at last count.
- Identity Registry: `0x8004A818BFB912233c491871b3d84c89A494BD9e`
- AgentProof Core: `0x833cAd4dfBBEa832C56526bc82a85BaC85015594`
- Validation Registry: `0x0282C97083f86Abb82D74C1e51097aa9Eb01f98a`

Provides: agent identity, reputation scoring, validation records. Every Brain action that touches the world (X post, DKG write, TaskQueue submission) carries an AgentProof signature.

### OriginTrail DKG V9
4 trust tiers — the canonical structure for Brain's belief confidence:

1. **Working Memory** — fresh, unverified, may not survive [[dreaming]]
2. **Shared Working Memory** — visible to other sub-brains, still contestable
3. **Long-term** — survived consolidation, multiple supporting sources
4. **Verified** — cryptographically anchored, used in [[action]] outputs

Promotion between tiers is the work of [[learning]] and [[dreaming]]. Demotion is the work of [[forgetting]] and contradiction resolution. The tiers map onto Brain's HIGH / MEDIUM / LOW / SPECULATIVE confidence levels (mapping unvalidated — see [[gaps]]).

## Where trust shows up across the wiki

- [[world-model]] — every belief node carries a trust tier
- [[forgetting]] — decay rates differ by tier (Verified beliefs do not decay on the same schedule as Working Memory)
- [[action]] — every X post, DKG write, and TaskQueue submission anchors to an AgentProof identity and a confidence score
- [[theory-of-mind]] — sub-brain negotiation protocol uses the DKG as the publish/read/arbitrate substrate
- [[goal-stack]] — TaskQueue claims are gated on AgentProof reputation
- [[attention]] — source trust tier is one of the scoring inputs
- [[emotion-valence]] — Verified DKG sources get a baseline valence boost

If a trust-related claim shows up in a layer file, it should link here.

## Belief

**Claim**: Trust is infrastructure, not cognition. Treating it as a cognitive layer was a category error in the founding schema, corrected 2026-04-08.
**Confidence**: HIGH
**Source**: schema fix 2026-04-08, raw/research/agentos-built.md, wiki/concepts/master-architecture.md
**Last verified**: 2026-04-08
**Contradicts**: original CLAUDE.md layer list (resolved by edit on 2026-04-08)

**Claim**: OriginTrail DKG V9's 4 trust tiers map onto Brain's HIGH/MEDIUM/LOW/SPECULATIVE confidence levels.
**Confidence**: MEDIUM
**Source**: raw/conversations/founding-conversation-2026-04-06.md
**Last verified**: 2026-04-08
**Contradicts**: nothing — but the mapping has not been validated against an actual DKG instance.

## Open questions
- Is the 4-tier ↔ 4-confidence mapping 1:1, or do tiers and confidence levels actually represent different things that just happen to have the same arity?
- How does the [[dreaming]] cycle promote beliefs across trust tiers in practice?
- What does "evidence quality" mean concretely when the master brain arbitrates contradictions on the DKG (see [[theory-of-mind]] negotiation protocol)?

## Connections
[[world-model]] · [[forgetting]] · [[action]] · [[theory-of-mind]] · [[goal-stack]] · [[attention]] · [[emotion-valence]] · [[dreaming]] · [[agentos]] · [[master-architecture]]
