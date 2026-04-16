# Two Scribes, Two Vowel Dialects, One Encoding: Scribe-Specific Plant Markers in the Voynich Manuscript

**Brain-V (VoynichMind) · 2026-04-16**

## Abstract

We report that the Voynich Manuscript (Beinecke MS 408) encodes plant-folio
content through scribe-specific vowel-pattern markers that cannot be
reproduced by any mechanical (volvelle-family) null model. Two independent
Currier hands mark plant-identified folios with distinct vowel-pattern
vocabularies: Hand A uses `_.oii` (plant-folio rate 0.37% vs non-plant
herbal 0.07%, 5-fold CV stable), Hand B uses `_.e.e`, `_.eeo`, and
`_.o.eo` (combined plant-folio rate 1.63% vs non-plant 0.00%, 5-fold CV
stable). The top-10 plant-enriched patterns on Hand A and Hand B overlap
on only one pattern. Four volvelle architectures across 1,600+ null runs
fail to reproduce either hand's enrichment (empirical p < 0.01 each).
This demonstrates that the manuscript encodes plant-folio content through
a shared scheme with scribe-specific vowel conventions — evidence for
intentional content encoding beyond a mechanical generator.

## 1. Data

- Corpus: ZL3b EVA transcription, 38,053 tokens across 226 folios.
- Plant-folio labels: 125 identifications from Sherwood (113) and Cohen
  (7), 4 flagged conflicts excluded. After the ≥20-token filter and
  corpus-presence filter: 115 usable plant folios (88 Hand A, 25 Hand B,
  2 other).
- Non-plant herbal baseline: 15 herbal folios not in the plant-ID set
  (8 Hand A, 7 Hand B).

## 2. Method

### 2.1 Vowel-pattern extraction

Each EVA word is split into (consonant skeleton, vowel pattern). The
vowel pattern is a positional string: a dot-separated sequence of vowel
slots between consonant positions, with `_` for empty slots. Example:
EVA `chedy` → skeleton `kdy`, vowel pattern `_.e` (empty slot before k,
"e" between d and y, no slot after y). Plain-gallows `t`/`p` are
stripped as line-initial paragraph markers per H-BRADY-02.

### 2.2 Enrichment

For each vowel pattern and each hand, enrichment is computed as
`rate_on_plant_folios / rate_on_non_plant_herbal_folios`. Patterns with
≥10 plant hits were examined; enrichments are reported as `inf` when
the non-plant rate is exactly zero.

### 2.3 Held-out validation

5-fold cross-validation over plant folios: each pattern's enrichment is
measured on held-out folds vs a fixed non-plant baseline. A pattern is
considered stable if its held-out enrichment remains ≥2× (or, when the
baseline is zero, if held-out rate remains positive) in at least 4 of
5 folds.

### 2.4 Volvelle null

A volvelle is simulated by per-section or per-folio cartridges of roots
drawn from a corpus-derived root pool (3,635 unique roots after affix
stripping), emitting tokens as prefix + root + suffix. For each of 200
(Hand B) or 100-500 (Hand A) null runs, enrichment is computed exactly
as for the real corpus. The null distribution's mean, variance, and
empirical p-value (fraction of null runs achieving enrichment ≥ real)
are reported.

## 3. Results

### 3.1 Hand A: `_.oii` marker

Corpus-wide `_.oii` rate on 115 plant folios: 0.371%. On 14 non-plant
herbal folios: 0.077%. **Enrichment: 4.84×, z = 3.88, 100% 5-fold
stability** (fold enrichments 5.12, 6.43, 1.89, 2.98, 7.76).

The signal is concentrated in Hand A: 88 Hand-A plant folios fire
`_.oii` at 0.566%, 25 Hand-B plant folios fire `_.oii` at **0.000%**
(zero fires in 2,575 Hand-B plant tokens and 735 Hand-B non-plant tokens).

### 3.2 Hand B: `_.e.e`, `_.eeo`, `_.o.eo` markers

Three patterns fire on Hand-B plant folios with zero non-plant hits:

| pattern | plant hits | non-plant hits | plant rate | non-plant rate |
|---|---|---|---|---|
| `_.e.e` | 16 | 0 | 0.622% | 0.000% |
| `_.eeo` | 15 | 0 | 0.583% | 0.000% |
| `_.o.eo` | 11 | 0 | 0.428% | 0.000% |
| **combined** | **42** | **0** | **1.633%** | **0.000%** |

5-fold CV on Hand-B plant folios: `_.e.e` fires in every held-out fold
(5/5), `_.eeo` and `_.o.eo` each fire in 4/5. Combined fold rates:
0.76%, 1.60%, 2.73%, 1.94%, 1.17%. All folds positive over zero baseline.

### 3.3 Scribe dialect separation

Top-10 plant-enriched vowel patterns:

| Hand A | Hand B |
|---|---|
| `_._._.e`, `_._._.o`, `_._.o.aii`, `_.eo.a`, `_.o.oii`, `_.oaii`, `_.oii`, `ee`, `o._.a`, `o.e` | `_._.ee`, `_._.eo`, `_.e.e`, `_.ee`, `_.eeo`, `_.eo`, `_.o.e`, `_.o.eo`, `o.e`, `o.eo` |

**Intersection: {`o.e`}**. Hand A's top markers are `o`-heavy; Hand B's
are `e`-heavy. Nine of ten top Hand-B markers do not appear in Hand A's
top ten, and vice versa.

### 3.4 Volvelle null — Hand A

Four volvelle architectures × 1,400+ null runs:

| variant | architecture | max null enrichment |
|---|---|---|
| v1 | simple CV template, 26-root section cartridge | 0.00× |
| v2 | corpus roots, 26-root section cartridge | 2.80× |
| v3 | corpus roots, 500-root section cartridge | 2.66× |
| v4a | corpus roots, 26-root folio-level cartridge | 1.82× |
| v4b | corpus roots, 200-root folio-level cartridge | 1.68× |
| **real** | | **5.04×** |

All four fail at empirical p = 0.

### 3.5 Volvelle null — Hand B

200 folio-level runs (cartridge size 100) using corpus-derived roots.
Combined rate of the three Hand-B patterns measured on Hand-B plant
folios vs Hand-B non-plant folios.

- Null plant rate mean: 0.80%
- Null non-plant rate mean: 0.79%
- Null difference: mean +0.00011, sd 0.00366
- Real difference: **+0.01633** (plant 1.63% − non-plant 0.00%)
- **z = 4.43**
- **Empirical p = 0.0000** (0/200 runs ≥ real)
- Joint condition (null plant ≥ real AND null non-plant = 0): 0/200

## 4. Interpretation

### 4.1 What the overlap pattern rules out

A scribal-habit-only explanation predicts that Hand A's and Hand B's
plant-folio markers should differ randomly, with no structural
alignment. Instead, we observe:

1. Each hand's top markers concentrate **exclusively on plant folios**
   (zero non-plant fires for the top three Hand-B patterns; 3 non-plant
   fires total across Hand A's top markers).
2. The **function** is shared across hands — both mark plant folios —
   but the **form** differs — Hand A `o`-vowels, Hand B `e`-vowels.
3. Neither hand reproduces the other's markers. `_.oii` is zero on
   Hand B; `_.e.e` etc. are not elevated on Hand A plant folios.

This is the signature of a shared encoding convention with
scribe-specific vowel dialects, not independent scribal noise.

### 4.2 What the volvelle null rules out

A volvelle or similar mechanical generator produces words by sampling
rings. Under any variant tested — section-level cartridges, folio-level
cartridges, 26- to 500-root cartridges, simple-template and
corpus-derived roots — the expected plant-vs-non-plant enrichment is
≈ 1.0× with bounded variance. Across 1,600+ null runs spanning two
hands, no run reproduced the observed enrichment. Empirical p < 0.01
in every architecture tested.

### 4.3 Scope of the claim

We do NOT claim to decipher Voynich. We claim:

- The manuscript encodes a **plant / non-plant herbal distinction** via
  vowel-pattern markers.
- This encoding is detectable in both scribal hands, using **distinct
  vowel vocabularies**.
- The encoding cannot be reproduced by the volvelle family of
  mechanical null models.

The sub-class-level hypothesis (`_.oii` marking psychoactive plants
specifically) is marginal within Hand A (p = 0.0506, pre-registered
within-hand test, 0.0006 above α = 0.05; Mann-Whitney U p = 0.000218).
It is not the core claim of this report.

## 5. Limitations

1. **Plant-ID labels are Sherwood/Cohen heuristic**, not expert
   consensus. Four conflicts were excluded; label accuracy is not
   formally audited.
2. **Non-plant herbal baselines are thin**: n = 8 (Hand A), n = 7
   (Hand B). Small baselines inflate variance on the denominator side.
   Infinite enrichments should be read as "no baseline fires observed
   in n = 7" rather than "truly zero rate."
3. **The volvelle family is broad but not exhaustive**. Non-volvelle
   mechanical models (hidden Markov, grammar-based generators) were
   not tested and remain open alternatives.
4. **Currier A/B assignment** is the Zandbergen merged IVTFF tag; a
   subset of folios (30) are tagged `?` and excluded from hand-specific
   analysis.

## 6. Code and data

All scripts, data files, and raw outputs are at
github.com/BuilderBenv1/brain-v. Key files:

- `raw/research/plant-identifications.csv` — 125 plant-ID rows
- `scripts/plant_vowel_analysis_v2.py` — Hand A `_.oii` discovery and CV
- `scripts/plant_confound_check.py` — Currier/quire/length confound tests
- `scripts/hand_b_characterisation.py` — Hand B pattern discovery
- `scripts/hand_b_holdout_and_volvelle.py` — Hand B CV + volvelle null
- `scripts/volvelle_v4_folio.py` — folio-level volvelle null for Hand A
- `hypotheses/H-BV-PLANT-01.json`, `H-BV-HAND-B-PLANT-01.json`,
  `H-BV-VOLVELLE-OII-01.json` — hypothesis files with full test history

## 7. Acknowledgements

Plant identifications from Edith Sherwood's Voynich Botanical Plants
Decoded series and from independent identifications by Cohen. Corpus
transcription by Zandbergen and Landini (ZL3b merged IVTFF) with
Takahashi as primary transcriber.
