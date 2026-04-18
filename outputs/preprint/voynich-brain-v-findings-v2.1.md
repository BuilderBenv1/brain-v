# Pre-Registered Autonomous Analysis of the Voynich Manuscript: Independent Verification of Bowern & Lindemann's Framework, Three Novel Observations, and Methodology Lessons from 150+ Hypothesis Tests

**Author:** Ben Horne, with the Brain-V cognitive architecture
**Affiliation:** Independent
**Date:** 2026-04-18
**Version:** 2.1
**Supersedes:** Brain-V v2 (2026-04-17, unreleased draft); Brain-V v1 (2026-04-16)

---

## Abstract

We report results from an autonomous pre-registered hypothesis-testing investigation of the Voynich Manuscript (Beinecke MS 408) conducted with the Brain-V cognitive architecture, in which every statistical claim was locked to a falsifiable threshold before its test was executed. After ~150 hypothesis executions and an internal literature audit that reclassified several initially-novel findings, we position Brain-V's contribution in relation to Bowern & Lindemann's (2021) statistical-linguistic framework, which is the established baseline for modern Voynich analysis. Brain-V's contribution comprises: (1) independent reproduction of four load-bearing B&L claims (per-hand conditional entropy h2 values, the -edy and qo- affix frequencies, the post-affix-removal h2 collapse to 2.23/2.24 reproduced within ±0.07, and the positional-constraint thesis), (2) four extensions within B&L's framework (within-section A/B convergence on TTR/length, per-token Cohen's d quantification for 8 section-concentrated markers, Layer-1/Layer-2 inventory closure rates, per-plant content refutation), and (3) three genuinely novel observations (a categorical n/consonant-inner gap 0/9643 across hands, the methodological disagreement between M1-M5 profile typology and MATTR for Hand A, and Hand A herbal's MATTR of 0.4544 matching Esperanto within 0.0004). We document twelve methodology lessons accumulated through pre-registered self-detected failures, presented as a parallel contribution. We report corrections to earlier overstatements: an apparent vowel-harmony finding dissolves into B&L's positional-constraint framework under cluster-diagnostic, an AGGLUTINATIVE-EXPANSION-01 "Basque uniquely best 6/6" result fails under direct UD_Basque-BDT corpus measurement and under MATTR, and Stolfi's 0.80 suffix-dealer-density reference reproduces only under Brain-V's narrow dealer set + strict-layer suffix definition. Negative results include refutations of twelve language-substitution mappings, Cardan-grille hoax hypotheses, species-level plant identification, and per-plant content encoding.

---

## 1. Introduction

The Voynich Manuscript is a 226-folio codex held in the Beinecke Rare Book and Manuscript Library (MS 408), radiocarbon-dated 1404-1438, written in an undeciphered script. A century of cryptanalytic and computational-linguistic effort beginning with William Friedman (D'Imperio 1978) has produced detailed structural observations without scholarly consensus on decipherment.

Modern statistical-linguistic analysis of the manuscript has consolidated around the framework established by Bowern and Lindemann (2021) in *The Linguistics of the Voynich Manuscript* (*Annual Review of Linguistics*) and Lindemann and Bowern (2020) in *Character Entropy in Modern and Historical Texts* (arXiv:2010.14697). This combined B&L framework establishes: (a) Voynichese exhibits anomalously low conditional character entropy (h2) relative to natural languages; (b) Hand A and Hand B differ quantitatively in h2 (A ≈ 2.17, B ≈ 2.01 per LV p.12); (c) the A/B h2 gap is driven primarily by two character sequences (-edy as a suffix and qo- as a prefix) that are respectively 86× and approximately 2× more common in Hand B; (d) removing these affixes collapses the A/B h2 gap to within 1% (post-removal values 2.23/2.24); (e) Voynichese's low h2 is largely attributable to positional constraints on character combinations within words; (f) on MATTR (Moving Average Type-Token Ratio, 2000-word window) comparisons across language families, Voynichese lies in the medium-morphological-complexity range closest to Germanic, Iranian, and Romance, least resembling Turkic, Dravidian, and Kartvelian.

This paper reports a pre-registered autonomous hypothesis-testing investigation conducted with the Brain-V cognitive architecture, positioned relative to B&L's framework. Brain-V's contribution is primarily *verification* of their established claims via an independent methodology, with three genuinely novel observations and a methodology-lessons trail derived from pre-registered self-detected failures.

We report an iteration-with-audit history. A v2 draft (2026-04-17, unreleased) initially framed Brain-V's Basque-typology finding and vowel-harmony finding as primary novel contributions. An internal audit against B&L's framework and a cluster-diagnostic test revealed these findings as either methodology-dependent (Basque match survives Brain-V's 5-metric profile but not MATTR) or re-detections of established results (the "harmony" finding is -edy concentration under k-means, consistent with B&L's positional-constraint framework). v2.1 reframes these explicitly.

The paper's scope: (2) methodology, (3) verification of B&L, (4) extensions within their framework, (5) novel contributions, (6) corrections, (7) published negatives, (8) open questions, (9) limitations, (10) acknowledgements, (11) repository and audit trail.

---

## 2. Methodology

### 2.1 Corpus

We use the Zandbergen-Landini ZL3b transliteration (`raw/corpus/ZL3b-n.txt`), parsed into 226 folios, 38,053 word tokens, 8,261 unique types, 191,562 EVA glyphs (25 distinct). Per-section breakdown is recorded in `raw/perception/voynich-stats.json`. Reference corpora for comparison (all from Universal Dependencies treebanks unless noted): UD_Basque-BDT, UD_Hungarian-Szeged, UD_Turkish-IMST, UD_English-EWT, UD_German-GSD, UD_Spanish-GSD, UD_French-GSD, UD_Persian-Seraji, UD_Arabic-PADT, UD_Hebrew-HTB, UD_Tamil-TTB, UD_Telugu-MTG, Esperanto Wikipedia plaintext.

### 2.2 Pre-registration discipline

For every non-trivial test, the hypothesis JSON (`hypotheses/H-BV-*.json`) is committed with `status: active`, an empty `tests_run` array, and a `test_threshold` field naming the exact numeric rule for verdict. The decision script is committed in the same lock commit. The execution commit then populates `tests_run` with the verdict per the locked rule. This produces a paired (`Pre-register …`, `<verdict>`) commit pattern visible in `git log`. Approximately 150 hypotheses have been executed; the full repository at `github.com/BuilderBenv1/brain-v` preserves each verdict as locked, unrevisable history.

### 2.3 Validation stack

Five validation patterns recur across the work:

- **Cross-validation.** 5-fold for marker enrichment claims.
- **Stress-testing.** For each "perfect" or "near-perfect" structural result, three stress tests are applied: alternative parameterisations, shuffle-null distribution, and reproduction on an external reference corpus.
- **External-benchmark reproduction.** When a claim aligns with prior published results, the independent verification is logged with explicit citation. For B&L specifically, the affix-removal h2 collapse (§3.1) serves as the pipeline sanity check for every entropy-related claim in this paper.
- **Self-applied novelty audit.** Before assembling this paper, each finding was audited against B&L's combined framework and classified as RE_DISCOVERY, EXTENDS_B&L, TRULY_NOVEL, or CONTRADICTS_B&L. Results are recorded in `outputs/reports/bowern-lindemann-framework-audit.md`.
- **Sample-composition parity.** When comparing two corpora (Hand A vs Hand B), the section composition of each is reported and considered as a possible confound.

### 2.4 Twelve methodology lessons

Each lesson is traced to the specific Brain-V hypothesis where the gap surfaced, documented in `findings_for_followup` of the relevant `hypotheses/H-BV-*.json` file.

1. **Pre-register exact numerator and denominator.** Detected in H-BV-EXTERNAL-PREDICTIONS-01 T3 where natural-language claim "of n occurrences, most are word-final" was locked as `tokens ending in n / all tokens` (15.46% FAIL) when Caveney's actual claim was `n occurrences word-final / total n occurrences` (94.61% PASS). Rule: every pre-registered metric must specify numerator and denominator with set-theoretic precision and a worked example.

2. **Lock tokenisation when referencing prior-hypothesis baselines.** Detected in H-BV-COMPOSITE-OUTER-01 M4 where the pre-reg imported a baseline value from a prior hypothesis but used a different tokenisation; ~95% of the apparent reduction was tokenisation change, not the hypothesised effect.

3. **Sanity-check external baselines on the original corpus.** Detected in H-BV-DENSITY-DIAGNOSIS-01 where Brain-V imported Stolfi's 0.80 suffix-dealer reference without verifying the pipeline reproduces it on Stolfi's own corpus. The "Hand A excess" over 0.80 turned out to be manuscript-wide pipeline drift, not a Hand-A-specific property.

4. **Pre-registered cumulative tests should include all variants with plausibly large effects.** Detected in H-BV-STOLFI-RECONCILIATION-01 where the S5 cumulative was locked before S3 ran and missed the critical S3c variant.

5. **Distinguish scale-invariant from scale-sensitive metrics in cross-corpus comparison.** Detected in H-BV-BASQUE-DIRECT-CORPUS-01 where Brain-V's glyph-level M2 inventory counts compared against UD_Basque morpheme-feature counts gave Hand-A-vs-Basque misses in opposite directions — characteristic of operational scale mismatch.

6. **Stress-test perfect alignments** via (a) alternative parameterisation, (b) shuffle null, (c) equivalent-methodology application to a reference corpus. Detected in H-BV-M5-RIGIDITY-DIAGNOSIS-01 where a 1.00 selectional-strictness value needed three stress tests to validate.

7. **Report both raw and normalised entropy in cross-language comparison.** Detected in H-BV-MARKOV-VALIDATION-01 S2 where alphabet-size normalisation attenuated a 1.3-unit raw-H_cond contrast to ~0.13.

8. **Shuffle nulls must respect sample-size dependence.** Detected in H-BV-EXTERNAL-CORRELATION-01 C8 where type-token ratio is sample-size dependent by construction; shuffle null that does not control for this produces spurious p<0.001 significance.

9. **Always run parallel tests on companion corpora.** Detected in H-BV-HAND-B-SECTION-INDEPENDENCE-01 where Hand A's section-independence did not extend to Hand B; without the parallel test the manuscript-wide narrative would have been wrong.

10. **Sample-composition parity.** Detected in H-BV-HAND-B-SECTION-BREAKDOWN-01 where Hand A's apparent section-independence was driven by 86%-herbal sampling. A corpus drawn from one condition cannot reveal condition-difference.

11. **Systematic locked tests over cherry-picked tokens.** Detected in H-BV-HAND-B-MARKER-CONCENTRATION-01 where a single-token test found one biological marker; the systematic top-20 locked test revealed 8 of 20 tokens section-concentrated.

12. **Audit the audit.** Detected in the Stolfi-crust-only literature audit where a research agent flagged a "critical correction" based on one passage of Stolfi's page; direct WebFetch verification revealed the page contains both 25% and 75% figures contradicting each other. Verification of the verification is the discipline.

### 2.5 Audit trail

Complete repository at `github.com/BuilderBenv1/brain-v`. Hypothesis files: `hypotheses/H-BV-*.json`. Scripts: `scripts/run_*.py`. Outputs: `outputs/reports/`. Methodology lessons: `wiki/methodology-lessons.md`. Framework audit: `outputs/reports/bowern-lindemann-framework-audit.md`. Every numeric claim in this paper carries a hypothesis ID and is reproducible from the stated script and corpus version.

---

## 3. Verification of Bowern & Lindemann 2021

### 3.1 Conditional character entropy (h2) — pipeline validated

B&L establish that Voynich A has higher h2 than Voynich B. Their published values are A=2.17, B=2.01 (LV p.12) and A=2.122, B=1.973 (CE §4.3.2 p.26). Brain-V's independent measurement under identical tokenisation (character-level over space-joined tokens, no ligature collapse): **A = 2.1906, B = 2.0191** (`H-BV-CONSTRUCTED-SIGNATURE-01`, `H-BV-HAND-B-MARKOV-01`). Brain-V reproduces B&L's LV numbers within 0.02 absolute on both hands; slightly higher than the CE numbers. Brain-V's pipeline aligns most closely with B&L's LV 2021 measurement.

### 3.2 The affix-driven A/B collapse

B&L's thesis-level claim (CE §4.3.2 p.27; LV p.12): removing -edy and qo- sequences from both texts collapses the A/B h2 gap to within 1%, with post-removal values 2.23/2.24. Brain-V's locked reproduction (`H-BV-BL-AFFIX-REMOVAL-01`, filter: tokens ending in 'edy' OR starting with 'qo' removed entirely):

| Measurement | Hand A | Hand B | A/B gap |
|---|---|---|---|
| Baseline h2 | 2.1906 | 2.0191 | 0.1715 |
| Post-removal h2 | **2.1758** | **2.1634** | **0.0125 (0.57%)** |
| B&L target | 2.23 | 2.24 | <1% |
| Brain-V deviation | 0.06 | 0.07 | within ±0.10 threshold |

**Both hands' post-removal h2 falls within 0.07 of B&L's target.** The A/B gap collapses from 0.17 to 0.01 (0.57%), well under B&L's "about 1%" qualitative claim. Removal rates (30.14% Hand B, 9.93% Hand A) are consistent with B&L's -edy-86×-more-common and qo-2×-more-common characterisation.

This reproduction validates Brain-V's pipeline for all entropy-related claims in this paper. Methodology lesson 3 (sanity-check external baselines on the original corpus) is applied retroactively; subsequent sections can cite B&L's published numbers with confidence.

### 3.3 Sensitivity refinement — the stems-without-affixes direction reversal

Brain-V's sensitivity diagnostics on the affix-removal test (V2 variant: remove the -edy and qo- substrings but *keep* the token stems) produce a direction-reversing result:

| Variant | Hand A h2 | Hand B h2 | Gap |
|---|---|---|---|
| V1 locked (remove tokens) | 2.1758 | 2.1634 | +0.01 |
| V2 remove substrings, keep stems | 2.1930 | **2.2450** | **−0.0521** |

Under V2, Hand B h2 *exceeds* Hand A by 0.05. This is a specific methodological refinement of B&L's characterisation: the entropy structure that drives the A/B gap is the affix substrings themselves, not stems that merely co-occur with affixes. Removing the affixes while keeping the stems exposes a residual reverse-direction A/B difference that B&L do not publish. Brain-V proposes this as a refinement of B&L's characterisation; the substantive conclusion (affixes drive the A/B gap) is unchanged.

### 3.4 Per-hand h2 values

B&L publish per-hand h2 values explicitly. Brain-V independently measures the same values from the same corpus using a different pipeline implementation. Reproduction within 0.02 absolute (LV) / 0.07 absolute (CE). This is reproduction of published results, not novel measurement.

### 3.5 The positional-constraint thesis

B&L's central characterisation (CE §4.7, §4.6.2; LV §3.2): Voynichese's low h2 is "largely the result of common characters which are heavily restricted to certain positions within the word." All Brain-V's Layer-1/Layer-2 morphological findings (§4.3) and n vowel-exclusive finding (§5.1) reproduce and refine this observation. Brain-V's "two-layer terminal morphology" is a quantitative refinement of the slot-grammar lineage (Tiltman 1950; Roe 1997; Stolfi 2005; Reddy & Knight 2011; Palmer 2014; Zattera 2022) that B&L adopt.

---

## 4. Extensions of Bowern & Lindemann's Framework

The following findings sit within B&L's framework and add specificity B&L did not publish.

### 4.1 Within-section A/B convergence on TTR and mean length

B&L's MATTR analysis operates at the whole-language level (Voynich A, Voynich B, Full). They do not slice by section × hand intersection. Brain-V's `H-BV-HAND-B-SECTION-BREAKDOWN-01` within-section controlled comparison:

- TTR: Hand A herbal 0.8284, Hand B herbal 0.8291 (Welch t = −0.052, p = 0.96)
- Mean length: Hand A herbal 4.991, Hand B herbal 5.072 glyph-units (t = −0.950, p = 0.34)

**Hand A herbal and Hand B herbal are statistically indistinguishable on these metrics.** This converges even though affix rates differ by a factor of 2.5× within herbal between the hands (Hand A herbal combined affix rate 9.29%, Hand B herbal 23.16%, per `outputs/per_section_affix_frequency.json`). The convergence on TTR/length is therefore distinct from B&L's affix-driven h2 collapse; both phenomena point to section as a key covariate in A/B comparisons, but the TTR/length convergence survives the 2.5× affix-rate disparity.

Framing: this is an extension of B&L's MATTR analysis to the section×hand intersection, documenting a specific within-section equivalence that sits alongside (not explained by) B&L's affix-removal collapse.

### 4.2 Section-specific marker concentration — Cohen's d quantification

B&L acknowledge section-vocabulary clustering and cite Montemurro et al. 2013 as the source. Their Table 2 (LV p.13) lists chedy, shedy, qokain as Voynich B's top words and daiin as Voynich A's top word. They do not partition by section, nor do they publish effect-size magnitudes. Brain-V's systematic top-20-locked test (`H-BV-HAND-B-MARKER-CONCENTRATION-01`, Welch t-test per token×section) identifies 8 of 20 Hand B tokens as section-concentrated at Bonferroni-corrected p < 0.0001:

| Token | Preferred section | Cohen's d | mean in section / mean out |
|---|---|---|---|
| shedy | biological | +2.09 | 0.035 / 0.011 |
| qokain | biological | +1.82 | 0.024 / 0.004 |
| ol | biological | +1.73 | 0.036 / 0.012 |
| qokedy | biological | +1.19 | 0.025 / 0.009 |
| shey | biological | +1.15 | 0.013 / 0.004 |
| chedy | biological | +1.08 | 0.030 / 0.018 |
| al | recipes | +1.68 | 0.013 / 0.004 |
| l | recipes | +1.60 | 0.009 / 0.002 |
| daiin | herbal | +0.73 | 0.019 / 0.012 |

Plus section-avoidance: aiin d=−1.15 in biological, ar d=−1.30 in biological. The phenomenon is B&L's (via Montemurro); the quantification per token-section pair is Brain-V's.

### 4.3 Layer-1 / Layer-2 inventory closure rates

B&L adopt the prefix/root-midfix/suffix three-field structure from the Tiltman-Roe-Stolfi-Zattera lineage and list "a few of the most common character combinations in each field" (LV pp.11-12) without publishing closure rate percentages. Brain-V's `H-BV-SUFFIX-SEQUENCE-01` (Hand A) and `H-BV-HAND-B-SUFFIX-SEQUENCE-01` (Hand B) compute inventory closure:

| Measure | Hand A | Hand B |
|---|---|---|
| Top-10 Layer-1 inner inventory coverage | 93% | 96% |
| Top-5 Layer-2 outer inventory coverage | 86% | 91% |
| Productive stems (≥3 occurrences) | 331 | 629 |
| Mean distinct inners per productive stem | 3.15 | 2.79 |
| Template coverage | 80.6% | 88.0% |

Both hands show closed Layer-1 / Layer-2 inventories and productive stems. The structural characterisation sits within B&L's slot-grammar acceptance; the closure rates are a quantitative extension.

### 4.4 Per-plant content encoding refutation

B&L cite Sterneck & Bowern 2020 for topic clustering aligned with hand and section (LV §4.3 pp.19-20). They do not test the specific prediction "one plant page = one plant-name encoding." Brain-V v1 (`H-BV-PLANT-CONTENT-01`) operationalises this prediction as token-count × entry-length correlation on Sherwood/Cohen plant-ID folios. Result: r = 0.58 on the null, not significant. The per-plant dictionary hypothesis is refuted as a specific test within B&L's established topic-clustering framework.

---

## 5. Novel Contributions

### 5.1 Categorical n / consonant-inner selectional gap

Slot grammars (Stolfi, Zattera, Palmer) constrain which glyphs co-occur but do not to our knowledge partition Layer-1 inner glyphs by phonological class and quantify Layer-2 selectional differentials by vowel-class.

Brain-V's `H-BV-SUFFIX-SUBCLASS-01` and `H-BV-HAND-B-SUFFIX-SUBCLASS-01` partition top-10 Layer-1 inners into VOWEL = {i, e, o, a} and CONSONANT = {ch, d, k, t, sh, l} for Hand A (and {d, k, ch, t, ckh, r} for Hand B — same 4 vowels, different consonants), then measure Layer-2 outer selectional asymmetry across the partition. Across both hands, **n is vowel-exclusive: 0 of 2,240 consonant-inner attachments in Hand A, 0 of 7,403 in Hand B, for a combined 0/9,643 across the manuscript.**

Stress-testing (`H-BV-M5-RIGIDITY-DIAGNOSIS-01`): (a) UD_Basque under identical methodology gives M5 = 0.00 — Basque does not exhibit this categorical gap. (b) Random 4/6 partitions of the top-10 inner set: V/C partition sits at the 95th percentile with 9% of random partitions also reaching the ceiling; V/C is not uniquely privileged but is above average. (c) Shuffle null: 100 shuffles of outer assignments produce mean M5 = 0.00 with zero shuffles reaching the observed value.

B&L discuss the Sukhotin-algorithm vowel/consonant split (LV §2.3.1) and note that "three characters that are almost exclusively word final are identified (g, n, y)" (p.8). They do not cross vowel-class with morpheme slot and do not report per-hand zero-count cells. The n / consonant-inner categorical gap is novel to Brain-V.

### 5.2 Methodological contrast — M1-M5 profile vs MATTR for Hand A

Brain-V's `H-BV-AGGLUTINATIVE-EXPANSION-01` tests Hand A's morphological profile against seven non-harmonic agglutinative candidates using five metrics (mean morphemes per word, Layer-1/Layer-2 inventory sizes, productivity ratio, categorical gap density, slot selectional strictness). Under this methodology Hand A matches Basque in 6 of 6 sub-metrics with profile distance 0.0. The result held as BASQUE_UNIQUELY_BEST with infinite margin to the second-ranked candidate.

B&L's published methodology is different: MATTR (Moving Average Type-Token Ratio, 2000-word window per Gheuens 2019, LV §3.4). Under MATTR B&L conclude Voynichese "most closely resembles the averages for Germanic and Iranian, and least resembles those for Turkic, Dravidian, and Kartvelian" (LV p.16).

Brain-V's `H-BV-BL-MATTR-REPRODUCTION-01` replicates B&L's MATTR methodology on hand-separated data:

| Corpus | MATTR |
|---|---|
| Hand A all | 0.4733 |
| Hand B all | 0.4216 |
| Hand A herbal | 0.4544 |
| Hand B herbal | 0.4612 |
| Basque (UD_Basque-BDT) | 0.5809 |
| Hungarian | 0.5253 |
| Turkish | 0.5339 |
| Spanish | 0.4579 |
| French | 0.4520 |
| German | 0.4980 |
| English | 0.3475 |
| Esperanto | 0.4548 |

Hand A MATTR (0.4733) is **0.108 below Basque (0.5809)** and closest (individual-language) to Spanish 0.4579 (0.015 away), Esperanto 0.4548 (0.019), French 0.4520 (0.021), German 0.4980 (0.025). Under MATTR, Hand A is not Basque-congruent; it clusters with Romance/Germanic/Esperanto at medium morphological complexity — consistent with B&L's conclusion.

**The two methodologies disagree for Hand A.** Brain-V's M1-M5 profile places Hand A in Basque's published range on every sub-metric. B&L's MATTR places Hand A 0.11 below Basque and adjacent to Romance/Germanic. The disagreement is the finding. v2.1 does not adjudicate — both methodologies are legitimate; they measure different aspects of morphological complexity; Hand A happens to profile differently under each. This is a methodology-level observation worth reporting, not a language identification.

This result also corrects v2's AGGLUTINATIVE-EXPANSION-01 "uniquely best with infinite margin" framing. The infinite margin was real within the 5-metric profile methodology; it dissolves under MATTR. The Basque candidate survives as a flagged possibility pending methodology-independent testing, not as a supported language identification.

### 5.3 Hand A herbal MATTR matches Esperanto within 0.0004

An unexpected by-product of the MATTR reproduction: Hand A herbal MATTR = 0.4544; Esperanto MATTR = 0.4548. **The difference is 0.0004.** This is the closest individual-corpus match anywhere in the MATTR comparison. The full manuscript MATTR (0.4547) is also closest to Esperanto (distance 0.0001).

We do not overclaim. This could be (a) coincidence, two MATTR values in the same narrow band; (b) evidence that Hand A herbal's vocabulary diversity profile specifically matches constructed-language-style regularity; (c) a signal that both Voynichese and Esperanto share a statistical profile consistent with medium morphological complexity plus regular affix systems. Distinguishing among these requires testing MATTR on multiple constructed languages (Lojban, Toki Pona, a priori languages) against Hand A herbal. Brain-V attempted to fetch additional constructed-language corpora but obtained only Esperanto at sufficient corpus size.

The finding is worth reporting because it creates a specific testable hypothesis for future work, not because it settles the constructed-language question.

---

## 6. Corrections and Reinterpretations

This section documents items that shifted between v1/v2 drafts and v2.1 based on internal audit.

### 6.1 Vowel-harmony finding dissolved into B&L's positional-constraint framework

v2 presented `H-BV-HAND-B-VOWEL-HARMONY-01` (Hand B silhouette 0.6495 with 77% prediction accuracy) as a novel typological divergence between hands (Hand A refuted at silhouette 0.33). The cluster diagnostic `H-BV-HAND-B-CLUSTER-DIAGNOSTIC-01` revealed:

- FRONT cluster (52 stems): mean -edy-family token fraction 32.75%, mean -aiin-family fraction 0.00%
- BACK cluster (26 stems): mean -edy-family 2.55%, mean -aiin-family 1.58%
- FRONT-EDY vs BACK-EDY Welch t=+5.84, p<10⁻⁵, d=+1.09

**The FRONT cluster is -edy-family suffix concentration, not phonological vowel harmony.** Stems with high inner 'e' are stems that preferentially take -edy; stems with high inner 'a' take a-vowel suffixes. The 77% prediction accuracy is phonotactic regularity consistent with B&L's positional-constraint thesis, not harmony in the technical sense.

We reclassify the harmony finding as a re-detection of B&L's -edy concentration observation via k-means methodology. The test methodology is novel; the result it returned is a re-discovery.

### 6.2 Stolfi 0.80 suffix-dealer density non-reproduction — unresolved

Brain-V initially interpreted Stolfi (2000) as reporting a suffix-dealer-density mean of 0.80 and observed Brain-V's pipeline measuring ~2.4 on both hands, interpreting this as a 3× "Hand A excess" over Stolfi's baseline. Methodology-lesson-3-motivated diagnosis (`H-BV-DENSITY-DIAGNOSIS-01`, `H-BV-STOLFI-RECONCILIATION-01`) revealed: (a) both hands show the same ~2.4-2.5 value under Brain-V's operationalisation, so the "Hand A excess" was manuscript-wide pipeline drift, not a Hand-A property; (b) Stolfi's 0.80 reproduces only under a reconciled configuration using his narrow 9-letter DEALER set and strict-layer suffix definition (stopping suffix count at first mantle glyph).

Additionally, Stolfi's grammar page contains an internal inconsistency on crust-only-token fraction: one passage states "almost exactly 75% of the normal tokens" are crust-only, another states "almost exactly 1/4 of the normal words have no core or mantle, only the crust layer." Brain-V measures 26-29% across all transcription variants, filter combinations, and sub-corpora — matching the 25% passage within 1-4 percentage points and not reaching the 75% figure under any tested configuration. We report the Stolfi-internal contradiction and Brain-V's Passage-B reproduction.

### 6.3 Basque finding — from unique language identification to methodology-dependent signal

v2 centred an "AGGLUTINATIVE-EXPANSION-01 6/6 Basque uniquely best with infinite margin" finding. Three methodological checks have pushed back on this framing:

| Test | Result |
|---|---|
| `H-BV-AGGLUTINATIVE-EXPANSION-01` (M1-M5 profile, approximate published ranges) | Basque uniquely best 6/6, distance 0.0 |
| `H-BV-BASQUE-DIRECT-CORPUS-01` (UD_Basque-BDT direct measurement) | CORPUS_WEAK 3/6 fit; M2 inventory scale-mismatched; M5 over-rigid |
| `H-BV-BL-MATTR-REPRODUCTION-01` (MATTR methodology) | Hand A 0.11 below Basque MATTR; closest to Romance/Esperanto/German |

v2.1 downgrades the Basque finding to methodology-dependent: Brain-V's 5-metric profile supports Basque-congruence; direct UD_Basque measurement does not fully support it; B&L's MATTR does not support it. As a language identification the claim is unsupported. As a flagged candidate pending further methodology-independent testing it remains.

### 6.4 Harmony-based cross-hand divergence framing

v2 reported `H-BV-HAND-B-FULL-BATTERY-01` as a "structurally different systems" finding based on 2-confirm / 3-diverge across five Hand-A-vs-Hand-B parallel sub-tests. With §6.1's reinterpretation of the harmony result (1c) and §6.3's downgrade of the agglutinative-expansion divergence (1d), the batch reclassifies as 2 CONFIRM + 1 RECLASSIFIED + 2 DIVERGE. The hands still diverge on the Basque-direct-corpus fit (1e) and on the candidate-language ranking (1d, with MATTR reinforcing B&L's medium-morphology cluster rather than Basque). The "structurally different systems" framing softens to "share basic morphological architecture; diverge on specific methodology outputs that are themselves methodology-dependent."

---

## 7. Published Negatives

Brain-V's pre-registered hypothesis-testing produces negative results of equal standing with positive findings. The following are refuted at locked thresholds:

- **Twelve language-substitution mappings** under shuffle-test or chi-square (`hypotheses/H-BV-BRADY-*`, `H-BV-PAGEL-*`, `H-BV-SCHECHTER-*`, various).
- **Random Cardan grille** under volvelle null (1,400+ runs across four architecture variants; `H-BV-VOLVELLE-*`).
- **Species-level plant identification** (three tests; `H-BV-PERUN-*`, `H-BV-RUGG-GRILLE-01`).
- **Per-plant content decoding** under 0.586-correlation null on token-count vs entry-length (`H-BV-PLANT-CONTENT-01`).
- **Vowel harmony** originally reported as CONFIRMED for Hand B under clustering; dissolved into B&L's positional-constraint framework per §6.1.
- **Nomenclator substrate** under positional and phonotactic tests (`H-BV-NOMENCLATOR-*`).
- **Esperanto-specific constructed-language hypothesis** on raw character-level metrics (`H-BV-CONSTRUCTED-SIGNATURE-01`, 0/6 metrics match Esperanto). Partially reversed under MATTR for Hand A herbal specifically (§5.3); otherwise refuted.

The full enumeration of refuted hypotheses is in `outputs/failures.log`.

---

## 8. Open Questions

### 8.1 The M1-M5 vs MATTR methodological disagreement itself

Brain-V's 5-metric profile and B&L's MATTR give different answers for Hand A. This is legitimately a research question: what does it mean that one typological methodology places Hand A in Basque's published range while another places it in the Germanic/Romance/Esperanto range? Both methodologies are principled. The disagreement may reflect (a) different aspects of morphological complexity being measured, (b) Hand A's profile genuinely sitting between typological clusters, (c) one or both methodologies having measurement artefacts Hand A reveals. Distinguishing requires running both methodologies on additional corpora and characterising where they agree and disagree.

### 8.2 Hand A herbal's Esperanto-like MATTR signature

Hand A herbal MATTR (0.4544) matches Esperanto (0.4548) within 0.0004. Whether this is coincidence or signal requires MATTR on additional constructed-language corpora and analysis of which features of Hand A herbal produce the match.

### 8.3 Section-level TTR/length convergence mechanism

Hand A herbal and Hand B herbal converge on TTR (0.83) and mean length (~5.0) despite a 2.5× difference in affix frequency. The convergence mechanism — what makes herbal content produce the same TTR and length across hands despite different affix rates — is unexplained.

### 8.4 qo-k- morphological amplification

`H-BV-QO-K-MORPHOLOGICAL-CLASS-01`: qo-k- token class biological-concentrated at Cohen's d = +2.05; qo-non-k- class at d = +1.00. Adding k- as core doubles qo-'s biological preference. Whether this is a genuine prefix-stem morphological compounding or distributional artefact requires further analysis.

---

## 9. Limitations

- **Autonomous LLM-orchestrated methodology**: findings from this framework should be independently verified before being treated as settled. The pre-registration audit trail preserves every verdict but does not replace human review.
- **Single corpus version**: all tests use the ZL3b-n.txt transliteration except where transcription version is explicitly compared (`H-BV-CRUST-ONLY-INVESTIGATION-01`, which finds max delta 0.023 across IT2a, RF1b, ZL3b).
- **Plant-ID labels heuristic**: v1's Sherwood + Cohen compilation inherits community-classification uncertainty.
- **Sample-size bounded findings**: some Hand B sub-corpus tests have small n (text-only n=5, cosmological n=3). The Dravidian family mean in `H-BV-BL-MATTR-REPRODUCTION-01` comes from Tamil (6,329 tokens) and Telugu (5,082 tokens), both marginal for 2000-word-window MATTR.
- **Kartvelian reference corpus missing** from the MATTR reproduction; Brain-V compares against 8 of B&L's 9 language families.
- **No independent verification against original manuscript imagery**: all findings are on the EVA transliteration. The EVA segmentation may not fully reflect the manuscript's underlying glyph structure.
- **Methodology lessons were self-detected**: each lesson came from a Brain-V test that initially returned a misleading result. The pre-registration audit trail records this honestly, but the self-detection pattern suggests additional undetected methodology issues may remain.

---

## 10. Acknowledgements

Prior researchers whose work Brain-V verifies or extends:

- **Claire Bowern and Luke Lindemann** (2020, 2021) — primary framework for modern Voynich statistical-linguistic analysis.
- **Prescott Currier** (1976) — A/B language distinction.
- **John Tiltman** (1967) — early grammar analysis, root + suffix model.
- **Jorge Stolfi** (2000) — crust-mantle-core grammar, dealer-rate quantification (with noted Stolfi-internal inconsistency on crust-only fraction).
- **Sravana Reddy and Kevin Knight** (2011) — character-level entropy analysis.
- **Marcelo Montemurro and Damián Zanette** (2013) — informative-token section-concentration.
- **Massimiliano Zattera** (2022) — 12-slot grammar extension.
- **Geoffrey Caveney** (2020) — word-final-n qualitative claim.
- **René Zandbergen** — voynich.nu corpus, transcription, illustration index.
- **Koen Gheuens** (2019) — 2000-word MATTR window recommendation.

Plant-ID compilations: **Sherwood** and **Cohen**. Corpus access: **Universal Dependencies** project, **Esperanto Wikipedia**, **Beinecke Library** for manuscript images.

Brain-V is a fork of the **Project Brain** cognitive architecture.

---

## 11. Code, Data, and Audit Trail

- **Repository**: `github.com/BuilderBenv1/brain-v`
- **Hypothesis files**: `hypotheses/H-BV-*.json` — every hypothesis cited
- **Decision scripts**: `scripts/run_*.py` — every numeric claim reproducible
- **Output reports**: `outputs/reports/` including `bowern-lindemann-framework-audit.md` and `v2-literature-audit.md`
- **Methodology lessons**: `wiki/methodology-lessons.md`
- **Failure log**: `outputs/failures.log`
- **Preceding versions**: `outputs/preprint/voynich-brain-v-findings-v1.{md,pdf}`, `voynich-brain-v-findings-v2.{md,pdf}` (v2 unreleased)

Every numeric claim in this paper carries a hypothesis ID and a script reference. The git log records the (`Pre-register …`, `<verdict>`) commit pattern for each test, providing a public audit trail.

---

## References

- Bowern, C. and Lindemann, L. (2021). The Linguistics of the Voynich Manuscript. *Annual Review of Linguistics* 7.
- Caveney, G. (2020). voynich.ninja thread 3354 (forum post on word-final n).
- Covington, M. A., and McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type-token ratio (MATTR). *Journal of Quantitative Linguistics* 17(2):94-100.
- Currier, P. (1976). Some important new statistical findings (reprinted at voynich.nu).
- D'Imperio, M. E. (1978). *The Voynich Manuscript: An Elegant Enigma*. National Security Agency.
- Davis, L. F. (2020). How many scribes wrote the Voynich Manuscript? *Manuscript Studies*.
- Fortescue, M. (1984). *West Greenlandic*. Routledge.
- Gheuens, K. (2019). Type-token ratio. herculeaf.wordpress.com/2019/05/04/type-token-ratio/.
- Havrankova, K. (2025). Analysis and Possible Translation of the Voynich Manuscript. OSF Preprints DOI 10.31235/osf.io/pdcna.
- Horne, B. (2026a). Brain-V v1 / v2 (preceding draft versions, this series).
- Hualde, J. I. and Ortiz de Urbina, J., eds. (2003). *A Grammar of Basque*. Mouton de Gruyter.
- Lindemann, L. and Bowern, C. (2020). Character Entropy in Modern and Historical Texts. arXiv:2010.14697.
- Montemurro, M. A. and Zanette, D. H. (2013). Keywords and Co-Occurrence Patterns in the Voynich Manuscript. *PLOS ONE* 8(6).
- Reddy, S. and Knight, K. (2011). What we know about the Voynich Manuscript. *ACL Workshop on Language Technology for Cultural Heritage*.
- Sterneck, J. M. and Bowern, C. (2020). Topic modeling the Voynich manuscript.
- Stolfi, J. (2000). A Grammar for Voynichese Words. voynich.nu/hist/stolfi/grammar.html.
- Tiltman, J. (1967). The Voynich Manuscript: The Most Mysterious Manuscript in the World.
- Zandbergen, R. (ongoing). voynich.nu.
- Zattera, M. (2022). A New Transliteration Alphabet Brings New Evidence of Word Structure in the Voynich Manuscript. *CEUR-WS* Vol-3313.

---

*End of v2.1 preprint. All findings reproducible from the stated repository state. Pre-registration audit trail visible in git log. Literature audits: `outputs/reports/v2-literature-audit.md`, `outputs/reports/bowern-lindemann-framework-audit.md`. Methodology lessons: `wiki/methodology-lessons.md`.*
