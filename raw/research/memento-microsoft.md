# Memento — Teaching LLMs to Manage Their Own Context
Source: Microsoft Research, github.com/microsoft/memento, HuggingFace microsoft/OpenMementos
Authors: Vasilis Kontonis, Yuchen Zeng, et al. (Microsoft)
Published: 2026 (exact arXiv date TBD)
Status: RAW — to be compiled into wiki

---

## What it is

A framework that teaches LLMs to segment their own chain-of-thought into blocks, compress each into a dense summary (a "memento"), and reason forward from mementos alone. The model learns to manage its own context window — deciding what to keep and what to compress — as a trained skill, not an external post-hoc process.

## How it works

1. **Block segmentation** — model divides its reasoning trace into blocks
2. **Compression** — a compressor LLM produces a memento for each block (state compression: produce something compact enough that the model can continue reasoning from the memento alone)
3. **Judge evaluation** — a judge LLM evaluates each memento across 6 dimensions, provides feedback
4. **Iterative refinement** — crucial: the compressor revises based on feedback
5. **Masking** — after each memento, the preceding thinking block is fully masked from subsequent attention, forcing mementos to carry everything future reasoning needs

## Results

- **~6x trace-level compression**: ~10,900 block tokens → ~1,850 memento tokens per trace
- **Peak KV cache: 2-3x reduction**
- **Throughput: nearly doubles**
- Accuracy gaps shrink with scale and close with RL
- Erased reasoning blocks leave traces in KV cache that the model still uses (interesting — implies latent retention even after masking)

## Dataset: OpenMementos

228K annotated traces:
- 54% math
- 19% code
- 27% science problems

Open dataset on HuggingFace. Open implementation on GitHub.

## Why this replaces MemPalace AAAK

MemPalace's AAAK claimed "30x lossless compression" which community tore apart as lossy summarisation (see raw/research/mempalace.md). Memento is the real version:

| Property | MemPalace AAAK | Memento |
|---|---|---|
| Compression | Claimed 30x lossless, actual lossy | 6x with measured accuracy |
| Validation | Self-reported, debunked | Judge LLM + iterative refinement |
| Training | None (prompting trick) | Trained skill with masking |
| Open data | None | 228K traces (OpenMementos) |
| Residual retention | Unknown | Confirmed (KV cache traces) |
| Source credibility | Indie project (6 commits) | Microsoft Research |

Memento is what AAAK pretended to be: trained, measured, open context compression.

## Relevance to Project Brain

### Context compression layer (new concept)

Brain's cognitive loop generates tokens every cycle. Over 100+ cycles, the context history becomes enormous. Memento provides the compression primitive:
- Each cycle's reasoning gets compressed into a memento
- Future cycles reason from mementos, not raw traces
- The forgetting layer can work WITH compression rather than just pruning

### Dreaming integration

The dreaming cycle currently compresses episodic entries into semantic beliefs. Memento is the mechanism for HOW that compression happens — trained, not hand-ruled.

### Self-model calibration

The erased-but-still-retained effect (KV cache traces) is interesting for the self-model: Brain may "know" things it has technically "forgotten," which has implications for confidence calibration.

## For the wiki
- Update wiki/components/library.md — add Memento as SHORTLISTED for context compression
- Update wiki/layers/forgetting.md — Memento as compression primitive
- Update wiki/layers/dreaming.md — Memento as trained consolidation mechanism
- Update wiki/concepts/master-architecture.md — note context compression as infrastructure need
- Downgrade MemPalace AAAK references — Memento supersedes it

---
*Filed: 2026-04-13*
*Status: SHORTLISTED — context compression layer*
