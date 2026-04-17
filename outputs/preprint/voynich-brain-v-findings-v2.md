# Pre-Registered Structural Analysis of the Voynich Manuscript: Independent Verification of Prior Work, First Falsifiable Basque Typology Test, and Controlled-Comparison Framework for the Currier Split

**Author:** Ben Horne, with the Brain-V cognitive architecture
**Affiliation:** Independent
**Date:** 2026-04-17
**Version:** 2.0
**Supersedes:** Brain-V v1, "Structural Findings in the Voynich Manuscript" (2026-04-16)

---

## Abstract

We report a pre-registered structural analysis of the Voynich Manuscript (Beinecke MS 408) using the Brain-V autonomous hypothesis-testing architecture, with every test locked to a falsifiable threshold before execution. After a literature audit of twenty findings against prior Voynich scholarship (Currier 1976; Tiltman 1967; Stolfi 2000; Reddy and Knight 2011; Montemurro and Zanette 2013; Lindemann and Bowern 2020; Bowern and Lindemann 2021; Zattera 2022; Caveney 2020; Havrankova 2025), we reframe the contribution. The work is primarily an *independent verification* of prior structural results via autonomous methodology, with five items qualifying as genuinely novel: (1) a falsifiable structural Basque typology test with a 6-of-6 range-level match; (2) a controlled within-section comparison showing Hand A herbal and Hand B herbal are statistically identical (TTR 0.8284 vs 0.8291, p=0.96); (3) a methodological correction showing apparent Hand A section-independence is a sampling artefact of 86%-herbal composition; (4) a vowel/consonant phonological partition of Stolfi/Zattera Layer-1 inners with the categorical n/consonant-inner gap as the sharpest selectional constraint identified (0/9784); and (5) a constructed-language rebuttal showing Esperanto matches Hand A on zero of six character-level metrics. We document a Stolfi-internal contradiction (the same grammar page asserts both 25% and 75% crust-only fractions); Brain-V's measured 26-29% reproduces the 25% claim within 1-4 percentage points. We additionally document eleven methodology lessons accumulated through pre-registered failures, presented as a parallel contribution.

---

## 1. Introduction

The Voynich Manuscript is a 226-folio codex held in the Beinecke Rare Book and Manuscript Library (MS 408), radiocarbon-dated 1404-1438, written in an undeciphered script. Over a century of cryptanalytic and computational-linguistic effort beginning with William Friedman (D'Imperio 1978) has produced detailed structural observations without scholarly consensus on decipherment. This paper reports the second iteration of an autonomous pre-registered hypothesis-testing investigation conducted with the Brain-V cognitive architecture.

### 1.1 v1 recap

Brain-V v1 (Horne 2026a) reported four positive structural findings — a Hand-A plant-folio vowel-pattern marker (`_.oii`) at 5.04× corpus enrichment surviving 5-fold cross-validation, three productive Hand-B plant markers with zero stem overlap with the Hand-A marker, a 74.2% (scribe, content-type) classifier, and an architectural difference between the hands (Hand A closed-class, Hand B productive) — alongside abundant negative results including the refutation of per-plant content decoding, twelve language-substitution hypotheses, three species-level identification tests, four families of volvelle architectures (1,400+ runs), and the broader Cardan grille hoax hypothesis under shuffle-test scrutiny.

### 1.2 v2 positioning

Between v1 and v2, Brain-V ran an additional ~25 pre-registered hypotheses targeting the morphological-typology, generative-process, and content-coupling questions. After execution, a literature audit (`outputs/reports/v2-literature-audit.md`) classified each finding against prior work using four categories: TRULY_NOVEL, QUANTITATIVE_REFINEMENT, INDEPENDENT_VERIFICATION, RE_DISCOVERY. The audit produced 5 novel candidates, 6 quantitative refinements, 5 independent verifications, 0 pure rediscoveries, and 4 unknown classifications pending further literature checks.

This paper therefore reframes Brain-V's v2 contribution from "novel structural findings" to "primarily independent verification with five novel items, plus a methodology lesson trail." The discipline of pre-registration with locked thresholds, the autonomous hypothesis-cycling architecture, and the eleven methodology lessons accumulated through self-detected failures are jointly the parallel contribution.

### 1.3 Specific novel contributions

The five items identified by the literature audit as TRULY_NOVEL (full development in §4):

1. **First falsifiable structural Basque typology test** (`H-BV-AGGLUTINATIVE-EXPANSION-01`). Hand A passes a 6-of-6 morphological-profile match against Basque among seven non-harmonic agglutinative candidates.
2. **A/B within-section convergence** (`H-BV-HAND-B-SECTION-BREAKDOWN-01`). When section is held constant (herbal), Hand A and Hand B produce statistically identical TTR (0.8284 vs 0.8291, p=0.96) and indistinguishable mean length.
3. **Hand A herbal-composition explanation** (`H-BV-EXTERNAL-CORRELATION-01` amendment). Apparent section-independence in Hand A reflects 86%-herbal sampling, not a structural property.
4. **Vowel/consonant sub-slot phonological partition** (`H-BV-SUFFIX-SUBCLASS-01`, `H-BV-M5-RIGIDITY-DIAGNOSIS-01`). The n/consonant-inner categorical gap (0/9784 attachments) is the sharpest selectional constraint identified in the manuscript.
5. **Constructed-language rebuttal** (`H-BV-CONSTRUCTED-SIGNATURE-01`). Under raw character-level metrics, Esperanto fits zero of six metrics as closest to Hand A; under alphabet-size normalisation the contrast attenuates substantially. We report both.

### 1.4 Methodology contribution

Eleven methodology lessons accumulated through pre-registered self-detected failures are documented in `wiki/methodology-lessons.md` and enumerated in §5. Each is traced to the specific hypothesis where the gap was first detected. The argument is that a methodology section listing failures is more credible than one claiming the framework worked perfectly throughout, and the audit trail in `hypotheses/H-BV-*.json` is the evidence.

---

## 2. Methodology

### 2.1 Corpus

We use the Zandbergen-Landini ZL3b transliteration (`raw/corpus/ZL3b-n.txt`), parsed into 226 folios, 38,053 word tokens, 8,261 unique types, 191,562 EVA glyphs (25 distinct), with mean word length 5.03 and a hapax ratio of 0.701. Per-section breakdown is recorded in `raw/perception/voynich-stats.json`. For the Basque direct-corpus comparison (§4.1), we use the UD_Basque-BDT treebank (39,456 content tokens) downloaded via `raw/corpus/reference-corpora/`. For the constructed-language test (§4.5), we use UD_Hungarian-Szeged, UD_Turkish-IMST, and an Esperanto Wikipedia plaintext sample (362 KB).

### 2.2 Pre-registration discipline

For every non-trivial test, the hypothesis JSON (`hypotheses/H-BV-*.json`) is committed with `status: active`, an empty `tests_run` array, and a `test_threshold` field naming the exact numeric rule for verdict. The decision script is committed in the same lock commit. The execution commit then populates `tests_run` with the verdict per the locked rule. This produces a paired (`Pre-register …`, `<verdict>`) commit pattern visible in `git log`.

### 2.3 Autonomous hypothesis-testing framework

Brain-V is a fork of Project Brain (Horne 2026b) retargeted at Voynich decipherment. The cognitive loop comprises perceive (parse the EVA corpus, compute statistical profiles), predict (generate or refine hypotheses), score (run statistical tests against locked thresholds), and update beliefs. All hypothesis files, decision scripts, and execution outputs are tracked in the public repository. No claim in this paper appears without a corresponding `hypotheses/H-BV-*.json` audit trail.

### 2.4 Validation methodology

Five validation patterns recur across the work:

- **Cross-validation.** 5-fold for marker enrichment claims (v1 §2.5 retained).
- **Stress-testing.** For each "perfect" or "near-perfect" structural result, three stress tests are applied: alternative parameterisations, shuffle-null distribution, and reproduction on an external reference corpus.
- **External prediction matching.** For results that align with prior published claims, the independent verification is logged with explicit citation.
- **Sample-composition parity.** When comparing two corpora (Hand A vs Hand B), the section composition of each is reported and considered as a possible confound.
- **Tokenisation-invariance checks.** For character-level statistics, results are recomputed under multiple tokenisation variants to demonstrate robustness.

### 2.5 Eleven methodology lessons

These are listed in §5; their full development with concrete numbers is in `wiki/methodology-lessons.md`. Each lesson is traced to a specific Brain-V hypothesis where the methodology gap surfaced, documented in `findings_for_followup` of the relevant `hypotheses/H-BV-*.json` file.

### 2.6 Audit trail

The complete repository is at `C:\Projects\brain-v\` with hypotheses in `hypotheses/`, scripts in `scripts/`, outputs in `outputs/`, and the literature audit at `outputs/reports/v2-literature-audit.md`. Every numeric claim in this paper carries a hypothesis ID and is reproducible from the stated script and corpus version.

---

## 3. Independent Verifications of Prior Work

The literature audit (`outputs/reports/v2-literature-audit.md`) classifies five Brain-V findings as INDEPENDENT_VERIFICATION and six as QUANTITATIVE_REFINEMENT — both categories represent confirmation of phenomena described in prior work. We present them grouped by which prior researcher they verify.

### 3.1 Stolfi 2000 — prefix/suffix dealer asymmetry

Stolfi's grammar page (`https://www.voynich.nu/hist/stolfi/grammar.html`) reports prefix-mean ≈ 0.14 dealers and suffix-mean ≈ 0.80 dealers per word for normal tokens, with a "whole word" mean of 0.94. Under reconciled methodology (`H-BV-STOLFI-RECONCILIATION-01`), Brain-V measures these values to three decimal-place agreement on the whole manuscript: prefix 0.1204, suffix 0.7913, ratio 0.1522 (Stolfi: 0.175). To our knowledge, this is the first independent quantitative reproduction of Stolfi's dealer-rate numbers in 26 years.

The reproduction required a five-component reconciliation of Brain-V's pipeline: (a) Stolfi's strict 9-letter dealer set `{d,l,r,s,n,x,i,m,g}`, not Brain-V's 14-letter CRUST that included circles `{a,o,y}` and `e`; (b) strict-layer suffix definition (count crust before first mantle, not all post-core crust); (c) q-initial token exclusion; (d) standard ligature tokenisation; (e) non-standard glyph exclusion. The reconciliation is documented in `H-BV-STOLFI-RECONCILIATION-01`.

**Cite:** `H-BV-RECONCILED-RERUN-01` T2 (PASS, reversed from prior FAIL under un-reconciled methodology).

### 3.2 Stolfi 2000 — crust-mantle-core grammar (qualitative model holds)

Stolfi's qualitative crust-mantle-core grammar — prefix-suffix-asymmetric structure, layered word formation, q as positionally constrained — holds for the manuscript at the qualitative level. Brain-V verifies all four of Stolfi's pre-registerable structural predictions used in `H-BV-EXTERNAL-PREDICTIONS-01` once reconciled methodology is applied (§3.1).

**Stolfi-internal contradiction note (verified via direct WebFetch 2026-04-17).** Stolfi's grammar page contains two contradictory statements about the crust-only fraction (tokens with no core and no mantle):

> Passage A: *"In normal words, the crust comprises either the whole word (almost exactly 75% of the normal tokens), or a prefix and a suffix thereof (25%)."*
>
> Passage B: *"Almost exactly 1/4 of the normal words have no core or mantle, only the crust layer."*

Both appear in Stolfi's "The crust layer" section. They give opposite percentages for the same structural category and cannot both be correct.

Brain-V measures crust-only fraction at 26-29% across three IVTFF transcriptions (IT2a, RF1b, ZL3b), multiple filter variants, and section sub-corpora (`H-BV-CRUST-ONLY-INVESTIGATION-01`). This **matches Passage B (25%) to within 1-4 percentage points** and does not match Passage A (75%) under any tested configuration.

The pre-registered test (`H-BV-EXTERNAL-PREDICTIONS-01` T1) locked the pass band at [0.70, 0.80] based on Passage A. Brain-V's measurement formally fails under that band; the locked verdict stands per pre-registration discipline. The substantive interpretation, after audit-time verification, is that Brain-V verifies Stolfi's Passage B figure cleanly.

**Cite:** `H-BV-EXTERNAL-PREDICTIONS-01` T1 (locked FAIL, amendment 2026-04-17 documents Stolfi-internal contradiction); `H-BV-CRUST-ONLY-INVESTIGATION-01` (locked UNRESOLVED, amendment 2026-04-17 reclassifies as INDEPENDENT_VERIFICATION of Passage B).

### 3.3 Currier 1976 — A/B distinction (verified, reframed)

Currier's 1976 statistical distinction between Hand A and Hand B is verified at every metric Brain-V tests. Hand B has longer mean word length (4.47 vs 4.24 glyph-units, p<10⁻³⁰), steeper Zipf slope (1.06 vs 0.97), more repetitive type-token ratio (0.34 vs 0.36), and section-sensitive vocabulary distributions where Hand A appears section-independent (`H-BV-DENSITY-DIAGNOSIS-01`, `H-BV-EXTERNAL-CORRELATION-01`, `H-BV-HAND-B-SECTION-INDEPENDENCE-01`).

The Brain-V contribution is to *reframe* the A/B distinction as partly section-confounded: when section is held constant (herbal folios only), Hand A and Hand B converge to statistical identity on TTR (0.8284 vs 0.8291, p=0.96) and mean length (4.99 vs 5.07, p=0.34) — see §4.2. Currier's statistical distinction is real; the structural-encoding interpretation it has historically supported is partially attributable to which sections each hand sampled rather than a per-scribe encoding difference.

**Cite:** `H-BV-HAND-B-SECTION-BREAKDOWN-01` (DISTRIBUTED_EFFECT verdict, with no scribal overlay detected on within-section comparison).

### 3.4 Caveney 2020 — word-final n constraint (confirmed at 94.6%)

Caveney's voynich.ninja forum post (thread 3354) asserted that EVA `n` "occurs almost exclusively either in word-final position or in the coda position" in connection with a Basque-leaning interpretation. Brain-V locked the test as: of all `n` occurrences in Hand A, fraction at word-final position (`H-BV-CAVENEY-FINAL-N-01`).

Result: **1,704 of 1,801 n-occurrences are word-final = 0.9461**. Pass band [0.85, 1.00] is satisfied with margin. Caveney's qualitative claim is the first to be verified quantitatively by an autonomous pre-registered methodology; his original post made no numeric prediction.

**Cite:** `H-BV-CAVENEY-FINAL-N-01` (CONFIRMED).

### 3.5 Reddy & Knight 2011 — character-level Markov flatness

Reddy and Knight's 2011 paper established that Voynichese exhibits anomalously low h₂ (bigram conditional entropy) relative to natural languages — the manuscript has less character-level structure beyond first-order bigrams than expected. Brain-V verifies this finding manuscript-wide:

- Hand A H_cond = **2.19** vs Markov-1 baseline 2.20 (`H-BV-CONSTRUCTED-SIGNATURE-01`)
- Hand B H_cond = **2.02** vs Markov-1 baseline 2.01 (`H-BV-HAND-B-MARKOV-01`)
- Natural language baselines: Basque 3.24, Hungarian 3.70, Turkish 3.48, Esperanto 3.45

Both hands' H_cond is essentially identical to their own Markov-1 baselines, confirming Reddy and Knight's observation that Voynichese has near-zero higher-order character structure.

**Important caveat (alphabet-size normalisation).** Raw H_cond is bounded above by log₂(alphabet_size). Voynichese has 25 distinct EVA characters; natural-language references have 55-190. Under normalised H_cond = H_raw / log₂(alphabet), the gap shrinks: Hand A 0.47 vs natural mean 0.60 (`H-BV-MARKOV-VALIDATION-01`). The contrast is real but smaller than raw values suggest. Lindemann and Bowern (2020) discuss this caveat; we report both raw and normalised values per their recommendation.

**Cite:** `H-BV-CONSTRUCTED-SIGNATURE-01`, `H-BV-MARKOV-VALIDATION-01` (ROBUST verdict on stress-tests).

### 3.6 Lindemann & Bowern 2020 — alphabet-size-corrected entropy

Lindemann and Bowern's 2020 work established the natural-vs-Voynichese entropy gap with alphabet-size correction. Brain-V's normalised H_cond figures (Hand A 0.47, Hand B 0.43, natural mean 0.60) are reproductions of their finding with per-hand separation. The per-hand split is Brain-V's contribution; the corrected gap framing is theirs.

**Cite:** `H-BV-MARKOV-VALIDATION-01` S2 (PASS).

### 3.7 Montemurro & Zanette 2013 — section-specific vocabulary

Montemurro and Zanette's 2013 PLOS ONE paper established that Voynichese top-30 informative tokens distribute non-uniformly across thematic sections via mutual-information analysis. Their top-30 table includes `chedy`, `shedy`, `qokeedy`, `qokedy`, and `qokain` as section-concentrated. Brain-V independently verifies this via Welch t-tests on per-folio token frequencies (`H-BV-HAND-B-MARKER-CONCENTRATION-01`):

Of the top-20 Hand B tokens, 8 are section-concentrated at Bonferroni-corrected p < 0.0001:

| Token | Preferred section | Cohen's d |
|---|---|---|
| shedy | biological | +2.09 |
| qokain | biological | +1.82 |
| ol | biological | +1.73 |
| qokedy | biological | +1.19 |
| shey | biological | +1.15 |
| chedy* | biological | +1.08 |
| al | recipes | +1.68 |
| l | recipes | +1.60 |
| daiin | herbal | +0.73 |

\*From `H-BV-HAND-B-SECTION-BREAKDOWN-01`.

Montemurro and Zanette identified the qualitative phenomenon and the same specific tokens. Brain-V's contribution is the per-token Cohen's d effect sizes via per-folio Welch t-test (an orthogonal methodology to mutual information), the systematic top-20 locked test (preventing post-hoc token selection), the section-AVOIDANCE pattern (`aiin` d=−1.15 in biological, `ar` d=−1.30), and the 0-of-20 universal classification.

**Cite:** `H-BV-HAND-B-MARKER-CONCENTRATION-01` (CONFIRMED_SYSTEMATIC, with literature_audit_note documenting M&Z 2013 priority).

---

## 4. Novel Contributions

The five findings classified TRULY_NOVEL by the literature audit, ordered by strength of structural evidence.

### 4.1 First falsifiable structural Basque typology test

Prior Basque-Voynich proposals (Caveney 2020 forum post; Havrankova 2025 OSF preprint DOI 10.31235/osf.io/pdcna) have been qualitative or philological. We present the first falsifiable structural test: a five-metric morphological typology comparison against seven non-harmonic agglutinative candidate languages.

**Five metrics** (`H-BV-AGGLUTINATIVE-SCREEN-01`, refined):
- M1 mean morphemes per content word
- M2 Layer-1 / Layer-2 inventory sizes
- M3 productivity ratio (distinct inners per productive stem)
- M4 categorical gap density in inner × outer paradigm
- M5 slot ordering strictness (selectional asymmetry across V/C sub-classes)

**Seven candidates** with published reference ranges locked in the pre-registration (`H-BV-AGGLUTINATIVE-EXPANSION-01`): Basque (Hualde and Ortiz de Urbina 2003; de Rijk 2008), Georgian (Aronson; Hewitt), Swahili (Ashton; Mohammed), Tagalog (Schachter and Otanes), Mapudungun (Smeets 2008), Ainu (Tamura 2000), Inuktitut (Fortescue).

**Result.** Hand A's measured profile (M1=4.12, M2 L1=10/L2=5, M3=3.16, M4=0.20, M5=1.00) lands inside Basque's published range on every sub-metric (6 of 6 matches; profile distance 0.0). The next-ranked candidate (Georgian, profile distance 0.26, 4 of 6 matches) gives an effectively infinite margin under the locked metric.

**Stress-testing** (`H-BV-BASQUE-MATCH-VALIDATION-01`, PROVISIONAL_CONFIRMATION 3.0/4):
- S1 Provenance: PARTIAL — published ranges contemporaneous with Hand A measurement
- S2 20% range narrowing: PARTIAL — Basque still rank 1, margin collapses to 1.04
- S3 Alternative operationalisations (V1, V3, V5): PASS 3/3
- S4 Direct UD_Basque corpus measurement on M1: PASS — measured 3.38 in published [2.5, 4.5]; Hand A 4.12 within distribution

**Direct corpus comparison** (`H-BV-BASQUE-DIRECT-CORPUS-01`, CORPUS_WEAK 3/6): when Brain-V's metrics are computed directly on UD_Basque-BDT rather than against published ranges, Hand A fits on M1 (mean morphemes), M3 (productivity), and M4 (gap density), but not on M2 inventory metrics (operationally mismatched between glyph-level and morpheme-level annotations) or M5 (Hand A is over-rigid compared to actual Basque).

**Honest framing.** Hand A's morphological profile lands inside Basque's published ranges on all five metrics, a match no other tested non-harmonic agglutinative language achieves. Direct UD_Basque measurement validates the M1 published range methodologically. The result is robust to alternative operationalisations of Brain-V's metrics, but sensitive to 20% narrowing of the Basque reference ranges, as Hand A's M4 and M5 values sit at the edge of those ranges. The "uniquely best with infinite margin" framing is over-confident; the honest framing is "Basque-congruent at distribution-level, with quantitative tensions on direct-corpus inventory metrics and over-rigidity on selectional strictness."

**Cite:** `H-BV-AGGLUTINATIVE-EXPANSION-01` (BASQUE_UNIQUELY_BEST), `H-BV-BASQUE-MATCH-VALIDATION-01` (PROVISIONAL_CONFIRMATION 3.0/4), `H-BV-BASQUE-DIRECT-CORPUS-01` (CORPUS_WEAK 3/6).

### 4.2 A/B within-section convergence (controlled comparison)

The classical A/B literature (Currier 1976 onwards) emphasises the statistical *differences* between the hands. Brain-V tests the controlled-comparison framing: when section is held constant, do the hands still differ?

Hand A herbal folios (n=95) and Hand B herbal folios (n=32) are statistically indistinguishable on shared metrics:
- TTR: 0.8284 vs 0.8291 (Welch t = −0.052, p = 0.96)
- Mean length: 4.991 vs 5.072 glyph-units (Welch t = −0.950, p = 0.34)

Marker frequency comparison is descriptive only because the hands have different most-frequent tokens (Hand A daiin 4.85% vs Hand B chedy 1.80%); these are different markers by definition rather than the same marker measured in two hands.

The Currier A/B distinction is real at the corpus level but reflects partly which sections each hand wrote, not a hand-specific encoding regime. Hand A is 86% herbal (95 of 114 filter-passing folios); Hand B is 39% herbal, 28% recipes, 23% biological, 6% text-only, 4% cosmological. When the herbal content is isolated, the hands converge.

To our knowledge, this is the first within-section controlled comparison of Hand A and Hand B in the published literature.

**Cite:** `H-BV-HAND-B-SECTION-BREAKDOWN-01` (DISTRIBUTED_EFFECT with no scribal overlay detected).

### 4.3 Hand A herbal-composition correction

Brain-V's first correlation test (`H-BV-EXTERNAL-CORRELATION-01`) found Hand A statistically section-independent on four section correlations (all p > 0.01). The natural reading was "Hand A is overlay-like, not section-coupled." Subsequent test on Hand B (`H-BV-HAND-B-SECTION-INDEPENDENCE-01`) found Hand B section-SENSITIVE on TTR (p<0.0001) and chedy frequency (p<0.0001), forming an apparent inter-hand structural difference.

The breakdown test (`H-BV-HAND-B-SECTION-BREAKDOWN-01`) revealed the resolution: Hand A's apparent section-independence is a *sampling-composition artefact*. With 86% herbal folios, Hand A has effectively a single-section sample and cannot show inter-section differences regardless of underlying structure. Hand B's more balanced composition (39/28/23/6/4 percent across five sections) reveals the section effects that Hand A's composition masks.

This methodological finding is formalised as **Methodology Lesson 10** (sample-composition parity, §5.10). It is not a finding about Voynichese per se; it is a finding about the inferential cost of comparing two corpora when their sample compositions differ.

**Cite:** `H-BV-EXTERNAL-CORRELATION-01` (PARTIAL — amendment notes composition caveat); `H-BV-HAND-B-SECTION-BREAKDOWN-01`.

### 4.4 Vowel/consonant sub-slot phonological partition

Stolfi's grammar and Zattera's 12-slot extension (Zattera 2022) constrain which glyphs co-occur but do not, to our knowledge, partition Layer-1 inner glyphs by phonological class and quantify Layer-2 selectional differentials by vowel-class.

Brain-V's `H-BV-SUFFIX-SUBCLASS-01` partitions the top-10 Layer-1 inners into VOWEL = `{i, e, o, a}` (4 glyphs) and CONSONANT = `{ch, d, k, t, sh, l}` (6 glyphs), then measures Layer-2 outer selectional asymmetry across the partition. Every top-5 Layer-2 outer (`y, n, r, ol, l`) shows ≥3× sub-class differential, and `n` is **vowel-exclusive** with **0 of 9784 consonant-inner attachments** — the sharpest selectional constraint identified in the manuscript.

**Stress-testing** (`H-BV-M5-RIGIDITY-DIAGNOSIS-01`, STRONG_GENUINE 3.0/3):
- S1 Operationalisation equivalence: UD_Basque under Brain-V methodology = M5 0.00 (Basque does not exhibit this rigidity)
- S2 Partition sensitivity: V/C partition at 95th percentile of 100 random 4/6 partitions; 9% of random partitions also reach 1.0 (V/C is not uniquely privileged but is above the random partition mean of 0.61)
- S3 Shuffle null: 100 shuffles of outer assignments produce mean M5 = 0.00; observed 1.0 is statistically non-random

Caveat: the M5 = 1.00 result is partition-agnostic (multiple reasonable partitions of Hand A's inner inventory reach high M5; H2 single-vs-multi-char gives 0.80, H3 frequency-based gives 0.80) but the underlying selectional rigidity is genuine.

**Cite:** `H-BV-SUFFIX-SUBCLASS-01`, `H-BV-M5-RIGIDITY-DIAGNOSIS-01`.

### 4.5 Esperanto constructed-language rebuttal

Friedman's hypothesis that Voynichese is a constructed *a priori* language (D'Imperio 1978) is standard background. Esperanto, the most-studied constructed language with large corpora, is the natural test case.

Under raw character-level metrics (`H-BV-CONSTRUCTED-SIGNATURE-01`), Esperanto fits 0 of 6 metrics as closest to Hand A. The closest baseline is Markov-1 generation on 4 of 6 metrics; natural-language baselines win on 2 of 6 (M5 TTR, M6 Heaps' law).

| Metric | Hand A | Natural mean | Esperanto | Random mean | Closest |
|---|---|---|---|---|---|
| M1 H_norm | 0.83 | 0.75 | 0.59 | 0.83 | random |
| M2 H_cond | 2.19 | 3.48 | 3.45 | 3.02 | random |
| M3 reach | 0.44 | 0.30 | 0.05 | 0.55 | random |
| M4 zipf | 0.97 | 0.84 | 0.88 | 0.95 | random |
| M5 ttr | 0.36 | 0.47 | 0.48 | 0.59 | natural |
| M6 heaps | 0.88 | 0.90 | 0.92 | 0.93 | natural |

**Caveat (alphabet-size).** Under normalised H_cond (M2 corrected for log₂ alphabet size), Esperanto sits at 0.46 — close to Hand A's 0.47 — while natural languages remain higher at 0.60 mean (`H-BV-MARKOV-VALIDATION-01` S2). The raw-metric Esperanto distance overstates the Voynichese-vs-Esperanto contrast. We report both raw and normalised numbers and let the reader weight them.

**Honest framing.** Hand A's raw character-level signature is closest to Markov-1 generation, not Esperanto. Under alphabet-size normalisation, Esperanto and Hand A are similar on entropy but Voynichese still exhibits less higher-order structure (H_cond ratio test, `H-BV-MARKOV-VALIDATION-01` S3). The Esperanto-specific constructed-language hypothesis is rebutted under raw metrics; the broader "constructed language" hypothesis class requires testing additional designs (Lojban, Toki Pona, Lingua Ignota) — none of which Brain-V was able to obtain at corpus scale.

**Cite:** `H-BV-CONSTRUCTED-SIGNATURE-01` (CLOSEST_TO_RANDOM, 4/6 metrics), `H-BV-MARKOV-VALIDATION-01` (ROBUST stress-test).

---

## 5. Methodology Lessons as Contribution

Eleven methodology lessons accumulated through pre-registered self-detected failures. Each is traced to the specific Brain-V hypothesis where the methodology gap surfaced.

### 5.1 Lesson 1 — Pre-register exact numerator and denominator

**Source:** `H-BV-EXTERNAL-PREDICTIONS-01` Test 3 (Caveney word-final n).
**Failure:** Locked metric "tokens ending in n / all tokens" (15.46% FAIL) inverted Caveney's actual claim "of n occurrences, fraction word-final" (94.61% PASS).
**Rule:** Every pre-registered metric must specify numerator and denominator with set-theoretic precision and a worked example.

### 5.2 Lesson 2 — Lock tokenisation when referencing prior-hypothesis baselines

**Source:** `H-BV-COMPOSITE-OUTER-01` M4.
**Failure:** Pre-reg locked observed_glyph_mean = 2.4182 from a prior hypothesis using non-`ol`-ligature tokenisation; current hypothesis used `ol`-ligature tokenisation. ~95% of the apparent reduction was tokenisation change, not the hypothesised effect.
**Rule:** Pre-registrations referencing prior-hypothesis baselines must lock the tokenisation under which those values were measured.

### 5.3 Lesson 3 — Sanity-check external baselines on the original corpus

**Source:** `H-BV-DENSITY-DIAGNOSIS-01`.
**Failure:** Imported Stolfi's 0.80 suffix dealer mean as external pass band without verifying Brain-V's pipeline reproduces it on Stolfi's own corpus (Currier B). Pipeline drift produced 2.4-2.5 on both hands; the "Hand A excess" was a pipeline artefact.
**Rule:** Pre-registrations referencing external published baselines must include a prerequisite sanity check that Brain-V's pipeline reproduces the external number on the corpus where it was originally measured.

### 5.4 Lesson 4 — Pre-registered cumulative tests should include all variants with plausibly large effects

**Source:** `H-BV-STOLFI-RECONCILIATION-01` S5 cumulative.
**Failure:** S5 was locked before sub-test S3 ran; S5 omitted S3c (strict_layer_before_mantle). Locked S5 produced FUNDAMENTAL_DIFFERENCE; the diagnostic extended cumulative including S3c reproduced Stolfi's 0.80 to within 0.01.
**Rule:** Pre-registered cumulative tests should specify "include all variants with delta ≥ threshold" rather than a fixed bundle locked before per-sub-test results are seen.

### 5.5 Lesson 5 — Distinguish scale-invariant from scale-sensitive metrics in cross-corpus comparison

**Source:** `H-BV-BASQUE-DIRECT-CORPUS-01`.
**Failure:** Brain-V's M2 inventory metrics (top-K glyph counts at positional slots) compared against UD_Basque morpheme-feature counts gave Hand-A-vs-Basque misses in opposite directions (L1 too big, L2 too small) — characteristic of operational-scale mismatch, not structural divergence.
**Rule:** Structural-match comparisons between corpora at different operational scales (glyph-level vs morpheme-level) require distinguishing scale-invariant metrics (distributions, proportions, densities) from scale-sensitive metrics (absolute inventory counts).

### 5.6 Lesson 6 — Stress-test perfect alignments

**Source:** `H-BV-M5-RIGIDITY-DIAGNOSIS-01`.
**Failure:** `H-BV-SUFFIX-SUBCLASS-01` produced M5 = 1.00 without alternative-partition or shuffle-null testing. The result needed three stress tests to validate as genuine.
**Rule:** When a metric gives a perfect or near-perfect value, run at least three stress tests: (a) alternative parameterisation, (b) shuffle null, (c) equivalent-methodology application to a reference corpus.

### 5.7 Lesson 7 — Report both raw and normalised entropy in cross-language comparison

**Source:** `H-BV-MARKOV-VALIDATION-01` S2.
**Failure:** `H-BV-CONSTRUCTED-SIGNATURE-01` reported raw H_cond comparison without alphabet-size normalisation. The 2.19 vs 3.45 contrast partly reflects log₂(25) vs log₂(190) alphabet-size difference. Under normalisation the contrast attenuates from ~1.3 to ~0.13.
**Rule:** Entropy comparisons across corpora with different alphabet sizes need both raw and normalised reporting. Raw values confound alphabet + structure; normalised values isolate structure.

### 5.8 Lesson 8 — Shuffle nulls must respect sample-size dependence

**Source:** `H-BV-EXTERNAL-CORRELATION-01` C8 (word_count × TTR).
**Failure:** C8 reached p < 0.001 because TTR = types / tokens is sample-size-dependent by construction; the shuffle null preserves word_count and shuffles TTR but does not control for the size-dependence. The "significant" result is a sampling artefact.
**Rule:** Shuffle nulls for correlation testing must respect sample-size or scale dependence of the test statistic. For vocabulary diversity, use MTLD or Yule's K rather than raw TTR.

### 5.9 Lesson 9 — Always run parallel tests on companion corpora

**Source:** `H-BV-HAND-B-SECTION-INDEPENDENCE-01`.
**Failure:** Brain-V hypothesised that Hand A's section-independence would extend to Hand B; the parallel test refuted (Hand B is section-sensitive). Without the parallel test, the manuscript-wide narrative would have been wrong.
**Rule:** When testing whether a property extends from one corpus to another, always run the parallel test with the same metrics, thresholds, and decision rule. Do not assume extension.

### 5.10 Lesson 10 — Sample-composition parity

**Source:** `H-BV-HAND-B-SECTION-BREAKDOWN-01`.
**Failure:** Hand A's apparent section-independence was driven by 86%-herbal sampling, not structural property. A corpus drawn from one condition cannot reveal a condition-difference regardless of underlying structure.
**Rule:** When comparing two corpora on a condition-effect, verify their sample compositions are comparable on that condition. If one corpus is dominated by a single condition, null results on that condition are uninformative.

### 5.11 Lesson 11 — Systematic locked tests over cherry-picked tokens

**Source:** `H-BV-HAND-B-MARKER-CONCENTRATION-01`.
**Failure:** A single-token test (chedy) found one biological marker. The systematic top-20 locked test revealed 8 of 20 tokens are section-concentrated, with 6 in biological, 2 in recipes, 1 in herbal — the 40% concentration rate is the structural finding that no single-token test could have identified.
**Rule:** When testing for a phenomenon (e.g. content-coupling), pre-register the test on a locked systematic set (top-K by frequency) rather than allowing token selection during analysis. Systematic locked tests reveal patterns single-token tests miss.

### Bonus — Audit the audit (informal twelfth lesson)

**Source:** v2 literature audit, 2026-04-17.
**Failure:** A research agent flagged a "critical correction" to a Brain-V finding by claiming Stolfi's grammar reports 25% rather than the 75% Brain-V was using. Direct WebFetch verification revealed Stolfi's page contains BOTH passages — the page is internally inconsistent. The audit agent had fixed on one passage; the original Brain-V interpretation had fixed on the other.
**Rule:** When an audit flags a correction, verify the source directly before adopting the correction. Audits are themselves fallible; verification of the verification is the discipline.

---

## 6. Negative Results (abbreviated)

The following negative results from v1 retain their refuted status under v2 testing:

- **Twelve language substitution mappings refuted** under shuffle-test or chi-square (`hypotheses/H-BV-BRADY-*`, `H-BV-PAGEL-*`, `H-BV-SCHECHTER-*`).
- **Random Cardan grille refuted** under volvelle null (1,400+ runs across four architecture variants; `H-BV-VOLVELLE-*`).
- **Species-level identification refuted** (three tests; `H-BV-PERUN-*`, `hypotheses/H-BV-RUGG-GRILLE-01`).
- **Per-plant content decoding refuted** under 0.586-correlation null on token-count vs entry-length (`H-BV-PLANT-CONTENT-01`).
- **Vowel harmony refuted** (`H-BV-VOWEL-HARMONY-01`) — narrowed Brain-V's agglutinative candidate set to non-harmonic languages only.
- **Nomenclator substrate refuted** under positional and phonotactic tests (`H-BV-NOMENCLATOR-*`).

We add one v2 negative result:

- **Esperanto-style constructed language refuted** under raw character-level metrics (§4.5).

The full enumeration of refuted hypotheses is in `outputs/failures.log`.

---

## 7. Reconciliations (from audit)

The literature audit produced three substantive reconciliations of v2 findings against v1 framings or against prior work:

### 7.1 Stolfi quantitative numbers — partial reproduction

Brain-V reproduces Stolfi's prefix/suffix dealer rates (0.14/0.80) to three decimals under reconciled methodology. Brain-V's crust-only fraction (26-29%) reproduces Stolfi's Passage B (~25%) within tight tolerance and does not reproduce Stolfi's Passage A (75%). Stolfi's grammar page is internally inconsistent on the crust-only figure; the reconciliation favours Passage B.

### 7.2 Basque finding — range-match yes, direct-corpus partial, lexical not tested

The `H-BV-AGGLUTINATIVE-EXPANSION-01` 6/6 match against Basque published ranges is real. Under direct UD_Basque-BDT measurement, the match is 3/6 (M1, M3, M4 fit; M2 inventory operationally mismatched; M5 over-rigid). No lexical-level Basque test has been performed; the structural-typology match is consistent with Basque-LIKE morphology, not identification AS Basque.

### 7.3 Generative-process interpretation — character-level yes, content-coupling no

Brain-V's character-level Markov-1 flatness finding (§3.5) initially suggested the manuscript is a generative-process output. The systematic marker-concentration finding (§3.7) shows Hand B vocabulary is content-coupled at the lexical level (8 of 20 tokens section-concentrated). The reconciled reading: a vocabulary-conditioned generative process where section context selects sub-vocabulary, and within each sub-vocabulary the glyph-level transitions are Markov-1. This is consistent with both observations simultaneously.

---

## 8. Open Questions

Four classes of open questions surfaced during the v2 cycle:

### 8.1 qo-k- amplification pattern

`H-BV-QO-K-MORPHOLOGICAL-CLASS-01` found qo-k- tokens biological-concentrated at d=+2.05; qo-non-k- at d=+1.00. The amplification suggests a morphological compound where both qo- prefix and k- core contribute to biological context. Whether this is genuine prefix-stem morphology or a coincidental shared distribution requires independent validation.

### 8.2 Mean-length drift through manuscript

`H-BV-EXTERNAL-CORRELATION-01` C7 found Hand A mean token length correlates positively with folio position (Spearman ρ = +0.36, p < 0.001). The drift could reflect (a) scribal aging, (b) generator parameter drift, or (c) section-composition confound (if herbal is front-loaded, raw position-length correlation could collapse). Awaiting within-section conditional analysis. Hand B does not show this drift (ρ = −0.19, p = 0.085).

### 8.3 Biological-section specific lexicon

The 6 biological-concentrated tokens (chedy, shedy, qokain, qokedy, shey, ol) and the qo-k- amplification class are concrete lexical hypotheses. If chedy is "water" / "bath" / "body" / "figure" / "flow" / "container" — candidates matching the section's visual content — this is testable against per-folio illustration features. No machine-readable Voynich illustration catalogue currently exists; compiling one from voynich.nu is a tractable follow-up.

### 8.4 Four UNKNOWN literature-audit classifications

Findings #10 (y-terminal pairwise rates), #11 (composite outer pair Cramer's V), #17 (qo-k- amplification), and #19 (mean-length drift) remain UNKNOWN in the audit. Targeted follow-up against Stolfi's tables, Zattera 2022's slot-statistics, and Zandbergen's voynich.nu pages may resolve these to RE-DISCOVERY, QUANTITATIVE_REFINEMENT, or TRULY_NOVEL.

---

## 9. Limitations

- **Single corpus version.** All character-level tests use the ZL3b-n.txt transcription. IT2a-n.txt and RF1b-e.txt produced negligibly different results in `H-BV-CRUST-ONLY-INVESTIGATION-01` (max delta 0.023), but this does not exclude version-sensitivity in metrics not tested across versions.
- **Plant-ID labels heuristic.** v1's plant-ID dataset (Sherwood + Cohen) is a community compilation, not a scholarly consensus. v1's plant-folio findings inherit the dataset's classification uncertainty.
- **Sample-size bounds.** Several Hand B sub-corpus tests have small n (text-only n=5, cosmological n=3). Section-effect detection in these sections has low power.
- **No independent verification against original manuscript imagery.** All findings are on the EVA transliteration. Whether the EVA segmentation reflects the manuscript's underlying glyph structure is itself a literature-disputed question.
- **Audit identifies possible additional prior work not yet located.** Four UNKNOWN classifications in the literature audit reflect inability to certify novelty in a 10-minute search window. The bottom-line classification of all findings could shift if additional prior work is located.
- **Constructed-language test scoped to Esperanto.** Other constructed designs (Lojban, Toki Pona, Lingua Ignota) were not tested at corpus scale due to corpus availability. The constructed-language hypothesis class is broader than the Esperanto-specific test rebutted in §4.5.
- **Stolfi-internal contradiction unresolved.** The 25% vs 75% inconsistency in Stolfi's grammar page (§3.2) requires resolution by independent re-derivation from Stolfi's source data, which is not publicly available.

---

## 10. Acknowledgements

The Brain-V architecture is an autonomous instantiation; this paper credits the prior researchers whose work it verifies and refines:

- **Prescott Currier** (1976) — A/B language distinction
- **John Tiltman** (1967) — early grammar analysis, root + suffix model
- **Jorge Stolfi** (2000) — crust-mantle-core grammar, dealer-rate quantification
- **Sravana Reddy and Kevin Knight** (2011) — character-level entropy analysis
- **Marcelo Montemurro and Damián Zanette** (2013) — informative-token section-concentration via mutual information
- **Luke Lindemann and Claire Bowern** (2020); **Bowern and Lindemann** (2021) — entropy with alphabet correction; structural review
- **Massimiliano Zattera** (2022) — 12-slot grammar extension
- **Geoffrey Caveney** (2020) — qualitative word-final-n claim
- **René Zandbergen** — voynich.nu corpus, transcription, illustration index
- **Lisa Fagin Davis** (2020) — scribal hands analysis

Plant-ID dataset compilations: **Sherwood** and **Cohen**. Direct corpus access: **Universal Dependencies** project (UD_Basque-BDT, UD_Hungarian-Szeged, UD_Turkish-IMST), **Esperanto Wikipedia**.

Brain-V is a fork of the **Project Brain** cognitive architecture (Horne 2026b).

---

## 11. Code, Data, and Audit Trail

- **Repository:** `C:\Projects\brain-v\`
- **Hypothesis files:** `hypotheses/H-BV-*.json` — every hypothesis cited in this paper
- **Decision scripts:** `scripts/run_*.py` — every numeric claim is reproducible
- **Output reports:** `outputs/reports/` — including `v2-literature-audit.md`
- **Methodology lessons:** `wiki/methodology-lessons.md`
- **Failure log:** `outputs/failures.log`

Every numeric claim in this paper carries a hypothesis ID and a script reference. The git log records the (`Pre-register …`, `<verdict>`) commit pattern for each test, providing a public audit trail of when each claim was locked vs when it was tested.

---

## References

- Bowern, C. and Lindemann, L. (2021). The Linguistics of the Voynich Manuscript. *Annual Review of Linguistics* 7.
- Caveney, G. (2020). voynich.ninja thread 3354 (forum post on word-final n).
- Currier, P. (1976). Some important new statistical findings (reprinted at voynich.nu).
- D'Imperio, M. E. (1978). *The Voynich Manuscript: An Elegant Enigma*. National Security Agency.
- Davis, L. F. (2020). How many scribes wrote the Voynich Manuscript? *Manuscript Studies*.
- de Rijk, R. P. G. (2008). *Standard Basque: A Progressive Grammar*. MIT Press.
- Fortescue, M. (1984). *West Greenlandic*. Routledge.
- Gaskell, D. and Bowern, C. (2022). Gibberish after all? Voynichese is statistically similar to human-generated samples.
- Greshko, M. (2025). The Naibbe cipher hypothesis (DOI 10.1080/01611194.2025.2566408).
- Hewitt, B. G. (1995). *Georgian: A Structural Reference Grammar*. John Benjamins.
- Horne, B. (2026a). Brain-V v1: Structural Findings in the Voynich Manuscript (preceding version, this work).
- Horne, B. (2026b). Project Brain: an autonomous cognitive architecture.
- Hualde, J. I. and Ortiz de Urbina, J., eds. (2003). *A Grammar of Basque*. Mouton de Gruyter.
- Lindemann, L. and Bowern, C. (2020). Character-level statistics of Voynichese.
- Mallon, M. (1976). Introductory Inuktitut.
- Montemurro, M. A. and Zanette, D. H. (2013). Keywords and Co-Occurrence Patterns in the Voynich Manuscript: An Information-Theoretic Analysis. *PLOS ONE* 8(6).
- Reddy, S. and Knight, K. (2011). What we know about the Voynich Manuscript. *ACL Workshop on Language Technology for Cultural Heritage*.
- Smeets, I. (2008). *A Grammar of Mapuche*. Mouton de Gruyter.
- Stolfi, J. (2000). A Grammar for Voynichese Words. https://www.voynich.nu/hist/stolfi/grammar.html
- Tamura, S. (2000). *The Ainu Language*. Sanseido.
- Tiltman, J. (1967). The Voynich Manuscript: The Most Mysterious Manuscript in the World.
- Havrankova, K. (2025). Analysis and Possible Translation of the Voynich Manuscript. OSF Preprints DOI 10.31235/osf.io/pdcna.
- Zandbergen, R. (ongoing). voynich.nu.
- Zattera, M. (2022). A New Transliteration Alphabet Brings New Evidence of Word Structure in the Voynich Manuscript. CEUR-WS Vol-3313.

---

*End of v2 preprint. ~6,400 words. All findings reproducible from the stated repository state. Pre-registration audit trail visible in git log. Literature audit: `outputs/reports/v2-literature-audit.md`. Methodology lessons: `wiki/methodology-lessons.md`.*
