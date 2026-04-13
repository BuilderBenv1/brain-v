# LightThinker++: From Reasoning Compression to Memory Management
Source: arXiv:2604.03679
Authors: Ningyu Zhang et al. (ZJU — Zhejiang University)
Published: 2026-04-04
Status: RAW — to be compiled into wiki

---

## What it is

An explicit adaptive memory management system for LLMs with three core memory primitives — commit, expand, and fold — that give the model reversible, dynamic context management during reasoning.

## The three primitives

### Commit
Archive a reasoning step as a compact summary. The model decides "I'm done with this block, compress it and move on." Irreversible in practice (the full block is replaced by the summary) but the expand primitive makes it retrievable.

### Expand
Look back at any past committed step and recover the raw evidence. This is the reversibility mechanism — if the model realizes a compressed summary lost critical detail, it can expand back to the original reasoning.

### Fold
Collapse an expanded block back to its summary to maintain context hygiene. Expand → use → fold is the read-then-forget-again pattern.

## Results

- **Standard reasoning**: 69.9% reduction in peak token usage, +2.42% accuracy gain under the same context budget
- **Long-horizon agentic tasks**: stable footprint beyond 80 rounds (60-70% reduction), +14.8% average performance gain across complex scenarios
- Follows Thought → Action → Observation loop while explicitly managing stateful memory

## Why this matters for Brain

### Direct mapping to cognitive layers

| LightThinker++ | Brain layer | Mapping |
|---|---|---|
| Commit | [[dreaming]] | Compress episodic entries into semantic beliefs |
| Expand | [[learning]] | Retrieve raw evidence when a belief is challenged |
| Fold | [[forgetting]] | Re-compress after use, maintain context hygiene |

These three primitives are EXACTLY what the dreaming → learning → forgetting interface needs:
- Dreaming commits (compresses cycles into beliefs)
- Learning expands (retrieves raw evidence to update beliefs)
- Forgetting folds (re-compresses after use)

### The 80-round stability result

Brain's cognitive loop runs indefinitely. The claim that LightThinker++ maintains stable performance beyond 80 rounds is directly relevant — this is evidence that a commit/expand/fold system can run long-horizon without context degradation.

### Relationship to Memento

Both are context compression, but different:
- **Memento** (Microsoft): trained compression, 6x ratio, model-as-compressor
- **LightThinker++** (ZJU): explicit memory primitives, 69.9% reduction, model-as-memory-manager

They are complementary, not competing:
- Memento answers "how to compress"
- LightThinker++ answers "when to compress, expand, and re-compress"

Brain may use both: Memento as the compression mechanism inside LightThinker++'s commit/fold primitives.

## For the wiki
- Update wiki/layers/forgetting.md — add commit/expand/fold as the operational model
- Update wiki/layers/dreaming.md — commit as the consolidation primitive
- Update wiki/layers/learning.md — expand as the evidence-retrieval primitive
- Update wiki/components/library.md — add LightThinker++ as RESEARCH
- Create or update wiki/concepts/memory-compression.md if needed

---
*Filed: 2026-04-13*
*Status: RESEARCH — primitives directly map to Brain's dreaming/learning/forgetting interface*
