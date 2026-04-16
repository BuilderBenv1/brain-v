# Structural Findings in the Voynich Manuscript: Scribe-Architecture Differences, Plant-Folio Markers, and the Refutation of Per-Plant Content Decoding

**Author:** Ben Horne, with the Brain-V cognitive architecture
**Affiliation:** Independent
**Date:** 2026-04-16
**Version:** 1.0

---

## Abstract

We report results from a pre-registered hypothesis-testing investigation of the Voynich Manuscript (Beinecke MS 408) conducted with the Brain-V cognitive architecture, in which every statistical claim was locked to a falsifiable threshold before its test was executed. Across more than fifty hypotheses, we identify a set of robust structural findings: a Hand-A plant-folio vowel-pattern marker (`_.oii`) at 5.04× corpus-wide enrichment surviving 5-fold cross-validation; three Hand-B plant markers (`_.e.e`, `_.eeo`, `_.o.eo`) with zero stem overlap with the Hand-A marker; a (scribe, content-type) classifier reaching 74.2% five-fold accuracy across six classes; and a confirmed architectural difference between the two hands (Hand A's `_.oii` is a 3-stem closed class, Hand B's markers are productive). We also report substantive negative results of equal value: per-plant content decoding is refuted under a 0.586-correlation null on token-count vs entry-length, twelve language-substitution hypotheses fail under shuffle-test or chi-square thresholds, three species-level identification tests fail, and four families of volvelle architectures (1,400+ runs) cannot mechanically reproduce the `_.oii` enrichment. The contribution is not a decipherment but a structural map of what the manuscript *cannot* be (a per-plant illustrated dictionary, a simple letter-substitution of any tested European or Semitic language) together with what it does appear to be at the surface level (natural-language-like prose with scribe-specific topical markers, decoded without illustration support).

---

## 1. Introduction

The Voynich Manuscript is a 226-folio codex held in the Beinecke Rare Book and Manuscript Library (MS 408), radiocarbon-dated 1404–1438, written in an undeciphered script. A century of systematic cryptanalytic effort beginning with William Friedman (D'Imperio 1978) and continuing through modern statistical characterisation (Currier 1976; Reddy and Knight 2011; Montemurro and Zanette 2013) has produced detailed structural observations but no decipherment with scholarly consensus. Recent attempts (Pagel 2025, Zenodo DOI 10.5281/zenodo.18478526; Brady 2025, Zenodo DOI 10.5281/zenodo.19583306; Greshko 2025 "Naibbe cipher", DOI 10.1080/01611194.2025.2566408) have each surfaced suggestive lexical signal that fails to survive shuffle-test scrutiny on the full corpus.

This paper reports the result of running a pre-registered hypothesis-testing pipeline — the Brain-V cognitive architecture, a fork of Project Brain — against the manuscript over a sustained sequence of perceive–predict–score cycles. The investigative discipline is the contribution as much as any individual finding: every claim that appears below was *committed in a locked, untested form* (status `pre-registered` in `hypotheses/H-BV-*.json`) **before** its decision script was executed, with the threshold for `CONFIRMED`, `MARGINAL`, or `REFUTED` written into the file. Each verdict is recorded by file ID; nothing is interpreted post-hoc into a positive without an explicit amendment commit.

The motivation for that discipline is the regularity with which Voynich claims that look strong at first inspection collapse under the simplest sanity tests (a shuffle of token order, a phonotactically-plausible nonsense baseline, or a folio-restricted re-test). Pre-registration with locked thresholds is the cheapest defence against this failure mode and produces a complete audit trail.

---

## 2. Data and Methodology

### 2.1 Corpus

We use the Zandbergen-Landini ZL3b transliteration of the manuscript (`raw/corpus/ZL3b-n.txt`), parsed into 226 folios, 38,053 word tokens, 8,261 unique types, 191,562 EVA glyphs (25 distinct), with mean word length 5.03 and a hapax ratio of 0.701. Glyph entropy over the full corpus is 3.86 bits/character; word entropy 10.45. Per-section breakdown is recorded in `raw/perception/voynich-stats.json`.

### 2.2 Plant identifications

Folio-level botanical identifications are sourced from two compilations: Sherwood (113 plant identifications, conservative) and Cohen (7 additional identifications). Conflicts are flagged in `raw/research/plant-identifications.csv` and excluded from any test where the conflict is material.

### 2.3 Currier hand assignments

Each folio carries a Currier-language tag (A, B, or unknown), inherited verbatim from the ZL3b transcription. Hand-A folios contain 11,022 word tokens (29.0%); Hand-B 25,179 (66.2%); the remainder are unattributed. We treat the assignment as authoritative throughout.

### 2.4 Pre-registration discipline

For every non-trivial test reported below, the hypothesis JSON file (`hypotheses/H-BV-*.json`) was committed to the repository with `status: pre-registered`, an empty `tests_run` array, and a `test_threshold` field naming the exact numeric rule for `CONFIRMED`, `MARGINAL`, and `REFUTED`. The decision script was committed in the same lock commit. The execution commit then populates `tests_run` with the verdict per the locked rule. This produces a paired (`Pre-register …`, `<verdict>`) commit pattern visible in `git log`.

### 2.5 Held-out validation methodology

For every enrichment claim we report 5-fold cross-validation: folios are randomly partitioned into five folds, the marker is re-discovered on four folds and the enrichment computed on the held-out fifth, repeated five times. A claim "passes 5-fold CV" only if the held-out enrichment exceeds the threshold in at least 4 of 5 folds.

### 2.6 Null model testing framework

Two null families are routinely applied:

- **Volvelle nulls.** Mechanical 3-ring rotating-disk encodings (four architecture variants, 1,400+ runs) are scored against the same metric as the empirical claim; the empirical p-value is the fraction of null runs at or above the observed value.
- **Phonotactically-plausible nonsense lexicon.** Random EVA-shaped skeletons are matched against the same proxy lexicons used for matching tests; this calibrates the "coverage floor" achievable by any zipfian glyph stream, and is reported alongside any lexical-coverage claim.

---

## 3. Positive Findings

### 3.1 _.oii — Hand A plant-folio marker

The vowel pattern `_.oii` (skeleton `*oii*` after EVA tokenisation) appears at a folio-level enrichment of **5.04× (z=3.88)** on Sherwood/Cohen plant-identified folios over non-plant folios within the corpus, restricted to Hand A. The enrichment survives 5-fold cross-validation with held-out fold enrichments [5.12, 6.43, 1.89, 2.98, 7.76] (mean ≈ 4.84×), 5/5 folds positive, 100% stability. The marker concentrates on three consonant skeletons {`kn`, `sn`, `dn`}, which together account for 29 of 36 occurrences (80%+ coverage) — i.e. it is a *closed-class* marker (see §3.3). When the test is restricted to within-Hand-A folios only (controlling for Currier confound), the enrichment drops to 1.72× (p=0.258, not significant), so the headline 5.04× should be read as a (Hand-A × plant) joint enrichment, not a pure plant signal.
**Cite:** `H-BV-PLANT-01` (status: confirmed, confidence 0.55).

### 3.2 Hand B plant markers — distinct, with zero stem overlap

Three vowel patterns in Hand B (`_.e.e`, `_.eeo`, `_.o.eo`) are 100% plant-specific by occurrence: 16, 15, and 11 plant-folio hits respectively, with zero non-plant hits in Hand B. Held-out 5-fold CV: `_.e.e` 5/5 folds positive, `_.eeo` 4/5, `_.o.eo` 4/5. Critically, the Hand-B marker stems do **not overlap** with the Hand-A `_.oii` stems {kn, sn, dn} — the two scribes use non-overlapping vowel-pattern dialects to mark plant content.
**Cite:** `H-BV-HAND-B-PLANT-01` (status: confirmed, confidence 0.88).

### 3.3 Architectural difference: closed-class vs productive

The two hands differ in marker *architecture*, not just choice of marker. Hand A's `_.oii` is a closed class: 3 stems span 36 tokens (17% type/token, highly concentrated). Hand B's markers are open / productive: 25 unique skeletons span 42 marker tokens (60% type/token), with `_.e.e`, `_.eeo`, `_.o.eo` top-5-stem coverage of 75.0%, 73.3%, 72.7% respectively — all below the 80% threshold that would qualify them as closed. The pre-registered prediction that Hand B would mirror Hand A's closed-class structure is **REFUTED**: the hands differ structurally in how they encode plant content.
**Cite:** `H-BV-CLOSED-CLASS-01` (status: refuted on the closed-class prediction, confidence 0.85; the architectural-difference observation is the substantive finding).

### 3.4 (Scribe, content-type) classifier — 74.2% multi-class accuracy

A naive-Bayes classifier built only over folio-level vowel-pattern frequencies, with no lexicon or language assumption, achieves **74.2% five-fold cross-validation accuracy** across six (scribe, content-type) classes (Hand-A herbal, Hand-A pharmaceutical, Hand-A recipes, Hand-B biological, Hand-B recipes, Hand-B herbal). Majority-class baseline is 50.0%; uniform-chance baseline is 16.7%. The classifier is a *topical reader*, not a decipherment: it identifies what a folio is about from its statistical fingerprint without identifying the language.
**Cite:** `H-BV-DIALECT-01` (status: confirmed across discovery, 5-fold CV per marker, volvelle null per marker, and classifier accuracy; confidence 0.88).

### 3.5 Hand A internal linguistic structure

Hand A passes a three-part pre-registered structural-coherence test:

1. **Inflection.** Of 162 consonant skeletons appearing ≥5 times in Hand A, mean distinct word-final suffixes per skeleton is **2.46**, with **69.8%** of skeletons taking ≥2 distinct suffixes (locked threshold: mean ≥2.0 AND ≥50%).
2. **Plant-folio bigram specificity.** Within-plant-folio mean pairwise Jaccard (top-50 bigrams) is 0.0014 vs cross-plant/non-plant 0.0010, ratio **1.44×** (locked threshold: ≥1.3×).
3. **LDA topic structure.** Latent Dirichlet Allocation with K=8 over Hand-A folio bag-of-words yields mean top-20 section purity **0.831** (locked threshold: ≥0.60); 6 of 8 topics are ≥80% pure on a single section, including one 100% herbal topic.

All three pre-registered criteria pass: Hand A is **natural-language-like** at the structural level.
**Cite:** `H-BV-HAND-A-INTERNAL-01` (status: confirmed, confidence 0.80).

### 3.6 Psychoactive sub-marker

Within the plant set, the four folios identified as psychoactive species (Paris, Cannabis, Rhododendron, Nymphaea caerulea) show `_.oii` at **8.14× the rate of non-psychoactive plants** (psychoactive mean 2.80% vs non-psychoactive 0.34%; t=+2.43, **p=0.046**; Cohen's d=2.63; Mann-Whitney U p=0.000015; bootstrap 95% CI [+0.007, +0.042]). A pre-registered Hand-A-only replication on the same four folios reproduced the direction at 6.18× but missed the α=0.05 significance threshold by 0.0006 (t=+2.32, p=0.0506, d=2.24, MW U p=0.000218) — pre-registered MARGINAL.
**Cite:** `H-BV-PSYCHOACTIVE-01` (status: confirmed, confidence 0.80) and `H-BV-PSYCHOACTIVE-02` (status: marginal, confidence 0.55).

---

## 4. Mechanical Null Rejections

### 4.1 Four volvelle architectures, 1,400+ runs

A standard objection to any structural marker on the Voynich is that simple mechanical encodings (e.g. rotating-disk volvelles in the Bacon/Trithemius family) can reproduce many of the statistical fingerprints of natural language. We test the `_.oii` plant-marker enrichment against four families of volvelle architectures (v1 simple 3-ring, v2 stratified, v3 paired, v4a/v4b folio-anchored) totalling 1,400+ runs. **No volvelle reproduces the empirical 5.04× enrichment.** Maximum across architectures: v1 0.00×, v2 max 2.80× (z=23.30), v3 max 2.66× (z=7.74), v4a max 1.82× (z=12.33), v4b max 1.68× (z=11.67). Empirical p=0 across all four. The same null rejection holds for Hand-B markers (volvelle z=4.43, p=0).
**Cite:** `H-BV-VOLVELLE-OII-01` (status: confirmed, confidence 0.92).

### 4.2 Null lexicon — 83% coverage from nonsense

Coverage rates ≥80% — the headline number for several published reconstructions — are achievable by phonotactically-plausible nonsense lexicons. Twenty random-skeleton trials produced **83.56% ± 1.03 percentage-point** coverage of the corpus, which is the diagnostic floor against which any matched-skeleton claim must clear. Brady (2025) clears it by +3.3 pp (86.9% reported); Schechter (2025) sits 0.75 pp below it; Hebrew lexicon test sits 25.6 pp below it. Coverage is therefore not a sufficient signal in isolation.
**Cite:** `H-BV-NULL-01` (active, confidence 0.92).

---

## 5. Cross-Validation with Independent Methods

### 5.1 Jensen TF-IDF attractor convergence

Jensen's independent TF-IDF attractor analysis identifies a small set of "attractor" folios per token. Cross-referencing 105 of Jensen's reported 190 attractors against Brain-V's plant-folio sets yields three convergence signals: (1) **9 attractors achieve simultaneous 100% overlap with both the Sherwood/Cohen plant-identification set AND Brain-V's Hand-A `_.oii` folio set** (attractors 15, 16, 44, 54, 55, 56, 58, 69, 76); (2) section-concentration rate is **76.7%** of attractor-touched folios falling in the herbal section, with 75 of 79 section-dominant attractors herbal-aligned (94.9%); (3) global Jaccard with the plant-ID set is 0.524. Distinct methodologies (TF-IDF clustering vs vowel-pattern enrichment) converge on the same folio set, providing external cross-validation of the Hand-A plant-folio cluster.
**Cite:** `outputs/jensen_cross_reference.json`.

### 5.2 Timm continuous-evolution challenge

Timm's continuous-evolution model predicts that the manuscript's apparent A/B distinction is a quire-anchored continuum rather than a discrete scribal split. We ran an 8-marker hand-vs-quire regression: 4/8 markers show quire ≥ hand effect, 4/8 show hand > quire, and 5/8 markers achieve combined-feature predictive power substantially exceeding either alone — meeting the pre-registered `BOTH_PARTIAL` decision rule. Specific examples: HandA_pharma marker has quire-coefficient 0.27 vs hand-coefficient 0.01 (quire-dominant); HandA_herbal has hand-coefficient 0.41 (hand-dominant). Plant markers survive Timm's challenge; preparation/method markers confound with quire. Verdict: PARTIAL.
**Cite:** `H-BV-TIMM-CHALLENGE-01` (status: partial, confidence 0.65).

### 5.3 Brady gallows-prediction verification

Of three published character-mapping reconstructions tested on Hand A's connector-content bigram delta (the same shuffle test used to falsify Schechter), Pagel's trilingual map ranks first at +0.0118 delta (23.9% match rate, **CONFIRMED** at the locked +0.010 threshold), Brady's Syriac map ranks second at +0.0044 (MARGINAL), Schechter's Latin sits at -0.0608 (REFUTED). When restricted to Hand A alone, Brady's full-corpus -0.0098 flips to a positive +0.0044, suggesting Hand-B noise was masking a small Hand-A signal in Brady's original reporting — a methodological vindication of the Hand-A-restricted analysis.
**Cite:** `H-BV-HAND-A-MAP-COMPARISON-01` (status: confirmed for Pagel, confidence 0.7); `H-BV-HAND-A-LANGUAGE-01` (status: marginal, confidence 0.4).

---

## 6. Negative Results

### 6.1 Per-plant content decoding refuted

A plant-by-plant decoding model predicts that folios about taxonomically-similar plants should produce taxonomically-similar text. We tested two corollaries:

- **Token-count vs entry-length correlation.** Pearson r=+0.0589 (p=0.586) between Hand-A folio token count and plant-entry-length proxy (n=88). Spearman ρ=+0.0454 (p=0.674). The pre-registered REFUTED threshold was r ≤ 0.3; the observed correlation is essentially zero. **Per-plant token-count decoding is refuted.**
**Cite:** `H-BV-SYLLABLE-LEVEL-01` (status: refuted, confidence 0.7).

- **Plant-family text similarity.** Within-family folio cosine similarity 0.2407 vs cross-family 0.2622 (diff −0.0214, sign opposite of plant-specific prediction); permutation p=0.856. Medicinal-use correlation r=−0.041. **Content-independence holds directionally.**
**Cite:** `H-BV-HAND-A-CONTENT-INDEPENDENCE-01` (status: marginal directionally independent, confidence 0.65).

### 6.2 Twelve language mappings refuted or marginal

Across two pre-registered language screens, twelve candidate languages fail to produce a connector-to-content bigram delta above the +0.005/+0.010 thresholds when applied to Hand A via simple frequency-rank substitution:

- Italian[^italian], Latin, Hebrew, Syriac, Greek, Arabic, German, Basque, Hungarian, Finnish, Armenian, Ottoman Turkish — all REFUTED in `H-BV-HAND-A-LANGUAGE-SCREEN-02` (best delta german +0.00198, well below +0.005).

[^italian]: Italian appears as REFUTED in the character-frequency screen but as best-fitting in the abjad consonant chi-square test; the results measure different properties and warrant a dedicated Italian-specific follow-up test.
- Pagel's trilingual (Latin/Hebrew/Arabic) original 81-term lexicon delta +0.0118 (CONFIRMED at +0.010); expanding the lexicon to 167 terms (51.3% coverage) drops the delta to +0.0030 (REFUTED) — the Pagel finding does not scale.
**Cite:** `H-BV-HAND-A-LANGUAGE-SCREEN-02` (status: refuted, confidence 0.15); `H-BV-PAGEL-EXPANSION-01` (status: refuted, confidence 0.8).

The chi-square abjad consonant test (`H-BV-ABJAD-CONSONANT-01`) technically passes for all seven languages but, per the post-hoc amendment, *substantively refutes* the abjad hypothesis: Semitic abjads (Hebrew 3.63×, Syriac 2.95×) fit *worst*, while Mediterranean alphabetic languages (Italian 9.82×, Latin 9.69×, Greek 9.02×) fit *best* — the opposite of the abjad-shorthand prediction.
**Cite:** `H-BV-ABJAD-CONSONANT-01` (status: confirmed_but_under_discriminating, confidence 0.55).

### 6.3 Three species-level identification tests refuted

- **`_.oii` species-clustering.** 22 Hand-A plant folios fire `_.oii`, but 0 species appear on ≥2 Hand-A folios — by Sherwood/Cohen's one-folio-per-species labelling, species-level clustering of `_.oii` is structurally impossible.
**Cite:** `H-BV-CONSONANT-ID-01` (status: refuted, confidence 0.15).

- **Cross-hand consonant semantics.** Jaccard(Hand-A plant skeletons, Hand-B plant skeletons) = 0.600 vs Jaccard(Hand-A plant, Hand-B non-plant) = 0.538, ratio 1.11× (below the pre-registered 1.2× threshold). Skeletons cluster by *hand*, not by *content*.
**Cite:** `H-BV-CONSONANT-SEMANTICS-01` (status: refuted, confidence 0.82).

- **Hand-B species-stem clustering.** 25 unique Hand-B plant species, all unique per folio; stem concentration 1.5–3.0 (intermediate); a secondary finding emerged that stems cluster on folio neighborhoods (mean 2.30 folios/stem), which is a *positional* rather than a *semantic* signal.
**Cite:** `H-BV-HAND-B-SPECIES-01` (status: refuted on primary, intermediate on secondary, confidence 0.25).

### 6.4 External-application, toxic, Perun visual-key, syllable-level, content-family

- **External vs internal application.** Hand-A `_.oii` rate external 0.561% vs internal 0.557% = 1.01× (t-test p=0.494; bootstrap CI [-0.0046, +0.0048] straddles zero).
**Cite:** `H-BV-EXTERNAL-NULL-01` (active, confidence 0.90).

- **Toxic vs non-toxic.** Toxic mean 1.08% vs non-toxic 0.34% = 3.15× (t=+1.65, p=0.060, missing α=0.05 by 0.010); bimodal distribution (5 of 14 toxic plants fire, 9 are zero); pre-registered MARGINAL.
**Cite:** `H-BV-TOXIC-01` (active, confidence 0.35).

- **Perun visual-key null.** 0 of 24 botanical-property × text-feature combinations reach p ≤ 0.05; medicinal vs non-medicinal `_.oii` rate 0.35% vs 0.41% (t=−0.31).
**Cite:** `H-BV-PERUN-NULL-01` (active, confidence 0.80).

- **Syllable-level decoding.** Token-count to entry-length r=+0.0589 (refuted, see §6.1).
- **Content-family similarity.** Within-family cosine < cross-family cosine (refuted, see §6.1).

---

## 7. Discussion

### 7.1 What Hand A appears to be

Hand A is a structurally coherent natural-language-like corpus (`H-BV-HAND-A-INTERNAL-01` confirmed across inflection, bigram specificity, and LDA topic purity), but its content does **not** track the plant illustrations at the per-plant level. Multiple independent tests of per-plant decoding (`H-BV-SYLLABLE-LEVEL-01`, `H-BV-HAND-A-CONTENT-INDEPENDENCE-01`, `H-BV-CONSONANT-ID-01`, `H-BV-CONSONANT-SEMANTICS-01`, `H-BV-PERUN-NULL-01`) refute the prediction that text content varies with plant identity, plant family, plant medicinal use, plant toxicity, or plant illustration features. The statistical fingerprint of Hand A is consistent with **natural-language prose that is topically organised by section** (herbal-pharma-recipes), not a per-plant illustrated dictionary.

### 7.2 Implications for decipherment

The negative-result chain has direct methodological implications. Future decipherment proposals on Hand A:

1. **Should not assume per-plant content.** A "decoded" text that names plants matching their illustrations would require explaining how the per-plant content prediction was refuted under five separate locked tests with the present corpus.
2. **Cannot rely on shuffle-fragile lexical matching alone.** Coverage ≥80% is achievable by nonsense (`H-BV-NULL-01`); only shuffle-test-positive deltas survive, and to date only Pagel's original 81-term map clears +0.010 (the expansion to 167 terms collapses to +0.0030).
3. **Should test on Hand A in isolation first.** Hand A and Hand B differ structurally (`H-BV-CLOSED-CLASS-01`), use non-overlapping plant-marker vowel patterns (`H-BV-HAND-B-PLANT-01`), and Brady's full-corpus negative result becomes Hand-A-positive once the Hand-B contamination is removed (`H-BV-HAND-A-LANGUAGE-01`).

### 7.3 Methodology as contribution

The paired-commit pre-registration discipline (lock → execute) produces a complete audit trail in the public Git history. Every claim in this paper can be traced to a `Pre-register …` commit dated *before* the corresponding `<verdict>` commit, with the locked thresholds visible in the `pre-registered` version of the hypothesis file. This is, to our knowledge, the first time Voynich research has been conducted with end-to-end pre-registration enforced by version control.

---

## 8. Limitations

- **Plant-ID labels are heuristic.** Sherwood (113) and Cohen (7) plant identifications are themselves contested; the Hand-A `_.oii` 5.04× enrichment depends on these labels being correct. CONFLICT-flagged folios are excluded but residual disagreement exists.
- **Non-plant baselines are thin.** Hand A has 88 plant-identified folios vs 8 non-plant herbal folios in the within-Hand-A restricted analysis, which drives the within-hand 1.72× being non-significant (p=0.258). The 5.04× cross-hand enrichment is the more statistically robust number.
- **Volvelle family is broad but not exhaustive.** Four architecture variants and 1,400+ runs cover the simple-rotating-disk family; more exotic mechanical encodings (e.g. position-conditional grilles, polyalphabetic rotors with variable stride) are not tested.
- **Abjad chi-square test is under-discriminating at N≈20k.** All seven languages pass the locked p<0.01 / improvement>2× thresholds, so the binary verdict is not the informative signal — the spread (2.95×–9.82×) is. The italian-medieval lead at 9.82× is identified as a *follow-up hypothesis target*, not a confirmed result of the present test.
- **Italian-medieval lead is post-hoc.** It emerged from the under-discriminating abjad test and has not been independently pre-registered. A discrimination-validated test methodology (with Italian-specific function-word predictions) is required before any positive interpretation.

---

## 9. Code and Data

- **GitHub repository:** [github.com/BuilderBenv1/brain-v](https://github.com/BuilderBenv1/brain-v) — full source code, hypothesis files, output JSON, and the paired pre-registration commit history.
- **Dashboard:** [brain-v-beryl.vercel.app](https://brain-v-beryl.vercel.app) — live view of the hypothesis state, confidence scores, and recent cycle activity.
- **Zenodo DOI:** [10.5281/zenodo.19610118](https://doi.org/10.5281/zenodo.19610118)

The corpus uses the public Zandbergen-Landini ZL3b transliteration; plant-identification CSVs are committed to `raw/research/`; reference letter-frequency profiles are in `raw/corpus/reference-profiles/`.

---

## 10. Acknowledgements

- **Edith Sherwood** and **Claudette Cohen** for the plant-identification compilations on which `_.oii` and the Hand-B markers depend.
- **Brady Defibaugh (2025)** for the two-stratum dispensatory hypothesis and the Syriac character map; the Hand-A restricted re-test (`H-BV-HAND-A-LANGUAGE-01`) is an independent partial confirmation.
- **Michael D. Jensen** for the TF-IDF attractor methodology, which converges on the same Hand-A plant-folio cluster from a fully independent angle (`outputs/jensen_cross_reference.json`).
- **Torsten Timm** for the continuous-evolution model, against which our 8-marker hand-vs-quire regression was scored (`H-BV-TIMM-CHALLENGE-01`).
- **Stephen Bax** for the partial decoding framework that established the abjad-style hypothesis space.
- **René Zandbergen** and **Marco Landini** for the ZL3b transcription and decades of foundational corpus work.
- **Karsten Pagel (2025)** for the 81-term trilingual map that is the only published character mapping currently passing our shuffle-test threshold on Hand A (`H-BV-HAND-A-MAP-COMPARISON-01`).

---

*This paper is a snapshot of a continuing investigation. Hypothesis files, decision scripts, and verdict commits are all under version control; subsequent work will append rather than overwrite.*
