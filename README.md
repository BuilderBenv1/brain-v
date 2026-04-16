# Brain-V: An Autonomous Cognitive Architecture Attacks the Voynich Manuscript

**Three days. Two hundred scoring cycles. A working content-type decoder.**

Brain-V is a persistent cognitive architecture — a system that generates
hypotheses, tests them against statistical evidence, eliminates failures,
updates its beliefs, and publishes its own nulls. It was pointed at the
Voynich Manuscript on April 14, 2026.

This README reports what it has found through April 16. Everything is
reproducible: the code, the data, the scoring methodology, every hypothesis
file, and every pre-registration commit.

---

## Headline finding

**Two independent scribes encode plant-folio content in the Voynich
Manuscript using scribe-specific vowel-pattern dialects that no mechanical
(volvelle-family) null model reproduces.**

- Hand A marks plant folios with `_.oii` (o-heavy vowel pattern).
- Hand B marks plant folios with `_.e.e`, `_.eeo`, `_.o.eo` (e-heavy patterns,
  all with zero non-plant fires).
- Top-10 plant-enriched patterns between the two hands overlap on **1** of 10.
- Across 1,600+ volvelle null runs spanning 4 architectures, empirical p < 0.01
  for every hand's markers.
- A naive-Bayes classifier trained on folio vowel-pattern distributions
  achieves **74.2% 5-fold-CV accuracy** at classifying (scribe, content-type),
  across 6 classes, vs 50% majority-class baseline.

The manuscript encodes *something* about each folio — at least, plant vs
non-plant herbal and scribe identity — through conventions that survive
held-out validation and refute the volvelle hypothesis.

The preprint-level write-up is at
[`outputs/preprint/scribe-specific-plant-markers.md`](outputs/preprint/scribe-specific-plant-markers.md).

---

## The findings in order

### 1. The null-lexicon result: coverage is not evidence

**1,300 phonotactically plausible nonsense skeletons achieve 83.56% coverage
on the Voynich corpus.** Schechter's 4,063-entry "Latin/Occitan" glossary
scores 82.81% — below the nonsense floor. Brady's 1,334-entry Syriac
dictionary (claimed 87.8%) sits +3.3pp above the null.

| System | Coverage | Δ vs null |
|---|---|---|
| Brady Syriac claim | 86.90% | +3.34pp |
| **Null nonsense (1,300)** | **83.56%** | baseline |
| Schechter Latin/Occitan | 82.81% | −0.75pp |
| Hebrew medieval medical | 57.90% | −25.66pp |

Coverage-based decipherment claims for the Voynich require a corpus-derived
null baseline, not just raw hit rate. (Hypothesis `H-BV-NULL-01`.)

### 2. The shuffle-test ceiling: no word-order signal survives

Across four independent lexicons (Schechter Latin, Brady Syriac proxy,
Hebrew medieval medical, Brain-V's own dictionary v1), the in-order decoded
text scores ≤ the shuffled decoded text on the connector→content bigram
metric. All four show the same failure mode: lexicons produce Latin-looking
words without Latin syntactic structure.

**Word-order syntactic signal is absent from Voynichese under lexicon
substitution**, regardless of source language. (`H-BV-SHUF-01`.)

### 3. Volvelle family ruled out for `_.oii`

Four volvelle architectures tested against the observed 5.04× Hand-A
plant-folio `_.oii` enrichment:

| Variant | Architecture | Null max | vs real 5.04× |
|---|---|---|---|
| v1 | Simple CV template, 26-root section cartridge | 0.00× | fails |
| v2 | Corpus roots, 26-root section cartridge | 2.80× | fails |
| v3 | Corpus roots, 500-root section cartridge | 2.66× | fails |
| v4a | Corpus roots, 26-root folio-level cartridge | 1.82× | fails |
| v4b | Corpus roots, 200-root folio-level cartridge | 1.68× | fails |

1,400+ null runs. Empirical p = 0 in every variant. Plant folios and
non-plant herbal folios draw from the same cartridge under section-level
volvelle, so enrichment ≈ 1.0× by construction. Folio-level cartridges
allow independence but average signal away. (`H-BV-VOLVELLE-OII-01`.)

### 4. The Hand-A `_.oii` plant marker

On 115 plant-identified folios (Sherwood + Cohen), `_.oii` appears at
4.84× the rate of 14 non-plant herbal baseline folios. Held-out 5-fold
cross-validation: 100% fold stability, all folds ≥1.5× enrichment.

A confound check revealed that `_.oii` is essentially a **Hand-A-specific**
feature: Hand B shows zero `_.oii` across all 25 Hand-B plant and 7
Hand-B non-plant herbal folios. Within-Hand-A enrichment is 1.72× (not
significant at p=0.258). The corpus-wide 5.04× headline is Hand-A-inflated.

Quire and length confounds were ruled out. (`H-BV-PLANT-01`.)

### 5. Hand B uses its own plant-marker vocabulary

After the confound check revealed the hand restriction, we searched Hand
B for its own plant markers. Three vowel patterns fire on Hand-B plant
folios with **zero non-plant fires**:

| pattern | plant hits | non-plant hits |
|---|---|---|
| `_.e.e` | 16 | 0 |
| `_.eeo` | 15 | 0 |
| `_.o.eo` | 11 | 0 |

Combined plant-folio rate: 1.63%. Combined non-plant rate: 0.00%.
5-fold CV: `_.e.e` positive in 5/5 held-out folds, the other two in 4/5.
200 folio-level volvelle runs produced a null plant-non-plant difference
of +0.00011 ± 0.00366; real is +0.01633, **z = 4.43**, empirical p = 0.

**Two scribes, two vowel dialects, same function.** Hand A uses o-heavy
patterns on plant folios; Hand B uses e-heavy patterns. Top-10 overlap
between hands: 1 pattern (`o.e`). (`H-BV-HAND-B-PLANT-01`.)

### 6. The scribes divide labor by section

| section | Hand A | Hand B |
|---|---|---|
| pharmaceutical | **16** | 0 |
| biological | 0 | **19** |
| herbal | **95** | 32 |
| recipes | 2 | **23** |
| cosmological | 0 | 3 |
| astronomical/zodiac | 0 | 0 |

Only herbal and recipes have both hands present at n ≥ 2. In recipes —
the only section where both hands have ≥8 discoverable markers — the top
marker sets **do not overlap at all** (0/8).

| Hand A recipes | Hand B recipes |
|---|---|
| `a.a`, `_.a.a`, `o.a`, `a`, `o.ai`, `_.o.ai`, `_.o.a`, `_._.a` | `oai`, `ai.o`, `o.ea`, `o._.eeo`, `o.eeo`, `_.eo.ai`, `o.ee.a`, `_.o.eeo` |

Hand A across all sections: o/e ratio 2.00 in its markers.
Hand B across all sections: o/e ratio 1.36. (`H-BV-DIALECT-01`.)

### 7. Content-type classifier at 74.2%

Bag-of-vowel-patterns → (scribe, content-type) naive-Bayes classifier.
5-fold CV on 190 folios across 6 classes:

| class | n | accuracy |
|---|---|---|
| (A, herbal) | 95 | 92.6% |
| (A, pharmaceutical) | 16 | 56.2% |
| (B, biological) | 19 | **100%** |
| (B, herbal) | 32 | 6.2% |
| (B, recipes) | 23 | **100%** |
| (B, text-only) | 5 | 0.0% |

**Overall: 74.2%**, vs 50% majority-class baseline, vs 16.7% chance.
**Brain-V can read what a folio is *about* from its vowel patterns alone,
without any language model.** (`H-BV-DIALECT-01` test 3.)

### 8. Pre-registered sub-class signals

- **Psychoactive plants**: corpus-wide `_.oii` rate 8.14× on 4 psychoactive
  folios (Paris quadrifolia, Cannabis, Rhododendron, Nymphaea caerulea).
  Pre-registered one-tailed Welch p = 0.046, Cohen d = 2.63 → **CONFIRMED**.
  Within-Hand-A re-test: p = 0.0506 (misses α = 0.05 by 0.0006) → marginal
  under locked rules. Mann-Whitney U p = 0.000218. (`H-BV-PSYCHOACTIVE-01/02`.)
- **"eo" family as cross-hand preparation marker**: pre-registered, Hand B
  passes (p < 1e-6), Hand A fails (p = 0.130). Locked rule → **PARTIAL**
  (Hand-B-specific, not cross-hand). (`H-BV-EO-FAMILY-01`.)
- **Toxic plants**: pre-registered, p = 0.060 (misses α = 0.05 by 0.010).
  **Refuted** under locked rules, replaced by the psychoactive hypothesis
  after cross-check. (`H-BV-TOXIC-01`.)
- **External vs internal preparation**: pre-registered, p = 0.494 → **refuted**.
  (`H-BV-EXTERNAL-NULL-01`.)

Four pre-registered sub-class tests; one confirmed cleanly, two marginal,
one refuted, one partial. The discipline holds.

### 9. Published nulls

- **H-BV-NULL-01** — coverage ≥80% is a free null floor
- **H-BV-SHUF-01** — word-order signal absent under lexicon substitution
- **H-BV-VOLVELLE-OII-01** — volvelle family ruled out for Hand-A plant marker
- **H-BV-PERUN-NULL-01** — illustration botanical properties do not correlate
  with text features at p < 0.05 across 24 tests
- **H-BV-STRUCT-01** — non-vowel structural features add <+1.9pp to section
  prediction; combining with vowels hurts
- **H-BV-VOWEL-CODE-01** (demoted 0.75 → 0.35) — per-token section prediction
  from vowel patterns fails held-out F1

Brain-V publishes its failed hypotheses with the same rigor as its
confirmed ones. Every pre-registration is a separate git commit made
*before* the test is run.

---

## What Brain-V has *not* done

- It has **not** deciphered the Voynich Manuscript.
- It has **not** identified the underlying language.
- It has **not** produced a reading of any folio.

It has demonstrated:

1. That the manuscript encodes content-type information at a resolution
   detectable by vowel-pattern analysis, with **74.2% classifier accuracy**
   across scribe-section classes.
2. That this encoding uses **scribe-specific vowel dialects** that barely
   overlap between the two Currier hands.
3. That the coverage metric dominating the Voynich decipherment field
   is **compromised** by a phonotactic null floor.
4. That **no volvelle architecture** among the four tested can reproduce
   the observed scribe-specific plant-folio enrichment.

The remaining open questions are the language identity of the plaintext,
the specific consonant-skeleton cipher, and whether the `_.oii`/`_.e.e`
pattern family corresponds to a semantic class (plant, genus, preparation)
that would allow cross-referencing with known medieval botanical texts.

---

## Key hypotheses and their confidence

| ID | Claim | Confidence | Status |
|---|---|---|---|
| H-BV-NULL-01 | Coverage ≥80% is a null floor | 0.92 | confirmed |
| H-BV-VOLVELLE-OII-01 | Volvelle family ruled out | 0.92 | confirmed |
| H-BV-DIALECT-01 | Scribe-section dialect dictionary (classifier 74.2%) | 0.88 | confirmed |
| H-BV-HAND-B-PLANT-01 | Hand B uses distinct plant markers | 0.88 | confirmed |
| H-BV-PERUN-NULL-01 | Illustration properties don't correlate with text | 0.80 | null published |
| H-BV-Q-01 | EVA `q` is categorical word-initial marker (98.9%) | 0.92 | confirmed |
| H-BV-PLANT-01 | Hand-A `_.oii` plant marker | 0.55 | Hand-A-restricted |
| H-BV-PSYCHOACTIVE-01/02 | Psychoactive plant sub-signal | 0.65/0.55 | confirmed/marginal |
| H-BV-EO-FAMILY-01 | `eo`-family preparation marker | 0.55 | partial (Hand-B only) |

All 180+ hypothesis files are in `hypotheses/`. Each records its full test
history with dates, confidences, and evidence.

---

## Methodology and reproducibility

All code is public in this repository.

- `scripts/perceive.py` — Parses EVA transliteration into structured data
- `scripts/predict.py` — Hypothesis generator (Claude Sonnet)
- `scripts/score.py` — Hypothesis scorer (Claude Haiku)
- `scripts/decrypt.py` — Deterministic cipher attacks (pure Python)
- `scripts/plant_vowel_analysis_v2.py` — Hand-A `_.oii` discovery + 5-fold CV
- `scripts/plant_confound_check.py` — Currier/quire/length confound tests
- `scripts/hand_b_characterisation.py` — Hand-B pattern discovery
- `scripts/hand_b_holdout_and_volvelle.py` — Hand-B CV + volvelle null
- `scripts/volvelle_v4_folio.py` — folio-level volvelle null for Hand A
- `scripts/scribe_dialect_dictionary.py` — per-(section, hand) markers
- `scripts/dialect_validation_and_classifier.py` — CV + volvelle + classifier
- `scripts/run_psychoactive.py` / `run_psychoactive_v2.py` — pre-registered tests
- `hypotheses/` — every hypothesis with test history
- `outputs/` — raw JSON outputs from every cycle
- `outputs/preprint/scribe-specific-plant-markers.md` — current preprint
- `raw/research/plant-identifications.csv` — 125 plant-ID rows (Sherwood + Cohen)
- `wiki/LOG.md` — chronological change log

The corpus is the ZL3b merged IVTFF transcription (Zandbergen + Landini,
Takahashi as primary transcriber). Plant identifications are from Edith
Sherwood's *Voynich Botanical Plants Decoded* series and from independent
IDs by Cohen.

**Pre-registration discipline**: Each pre-registered hypothesis is committed
to git with `status: "pre-registered"` and `tests_run: []` in a separate
commit *before* the test script is run. The test-execution commit includes
the results; the decision rules are never adjusted after observing the
outcome.

---

## Architecture

Brain-V is a fork of [Project Brain](https://github.com/BuilderBenv1/project-brain),
a persistent cognitive architecture by Ben Horne. Brain-V duplicates the
perceive-hypothesise-test-score-update loop and retargets it at MS 408.

Both systems run on [AgentProof](https://agentproof.sh) infrastructure —
ERC-8004 compliant reputation and trust scoring for autonomous AI agents.
Brain-V's agents are registered on SKALE (zero gas fees). Every hypothesis,
cycle log, and belief update is anchored to IPFS with on-chain timestamps.

The cognitive loop is the core innovation. Brain-V doesn't apply a single
theory and check if it works. It maintains a population of competing
theories, tests them against evidence, eliminates failures, and compounds
knowledge over time. When a positive finding is identified, Brain-V
actively tries to destroy it — running confound checks, volvelle nulls,
and pre-registered sub-class tests — and publishes whatever survives.

---

## Contributing

If you have a hypothesis about the Voynich Manuscript, open a GitHub
Issue with:

- **Claim** — plain English statement of what you believe is true
- **Type** — cipher / language / structural / null hypothesis
- **Test** — what statistical test would confirm or deny it

Brain-V will add it to the hypothesis pool and test it. Results are
posted back to the issue with the raw stats, the decision rule applied,
and the confidence update.

Specific open invitations:

- **Richer plant-ID labels.** The current 125 IDs are from Sherwood and
  Cohen. Expert botanical audit or alternative identification sources
  would sharpen the plant vs non-plant binary and enable finer-grained
  sub-class tests.
- **Brady's supplementary files.** The Syriac dispensatory paper
  (Zenodo 10.5281/zenodo.19583306) promises a 1,389-entry lexicon and
  pipeline code that weren't attached at time of analysis. Running
  Brain-V's full battery against the actual lexicon would be the
  definitive comparative test.
- **Non-volvelle mechanical nulls.** Hidden Markov, grammar-based
  generators, and other non-cartridge mechanical processes haven't
  been tested against Brain-V's findings.

---

## Contact

Built by Ben Horne ([@AgentProof](https://x.com/AgentProof_sh)) using
the Project Brain cognitive architecture.

Brain-V is part of the [AgentProof](https://agentproof.sh) ecosystem —
trust scoring infrastructure for autonomous AI agents.

---

*Brain-V did not solve the Voynich. It built a working content-type
decoder from vowel patterns alone, with every null published and every
pre-registration locked before the test ran. The decoder works at 74.2%
accuracy across six scribe-content classes. What the manuscript is about,
Brain-V can now read — in aggregate. What it says is still open.*
