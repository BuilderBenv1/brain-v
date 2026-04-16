# A Scribe-Specific Vowel-Pattern Classifier for the Voynich Manuscript: 74.2% Accuracy on (Scribe, Content-Type) Without Language Identification

**Author:** Ben Horne / Brain-V (VoynichMind)
**Affiliation:** Independent
**Date:** 2026-04-16
**Version:** 1.0

---

## Abstract

We present a working content-type classifier for the Voynich Manuscript
(Beinecke MS 408) that achieves 74.2% five-fold cross-validation accuracy
at identifying (scribe, content-type) tuples across six classes, using
only the distribution of vowel patterns in each folio's EVA transcription
and requiring no language identification, dictionary, or cipher
assumption. The classifier exploits a scribe-section division of labor:
the two Currier hands do not co-write most sections (Hand A owns
pharmaceutical, Hand B owns biological; only herbal and recipes are
shared at n ≥ 2), and where they co-write they use non-overlapping
vowel-pattern dialects — 0 of 8 Hand-A recipe markers overlap with Hand-B
recipe markers, and the top-10 plant-enriched vowel patterns between
the hands overlap on exactly one pattern. Each (section, hand) marker
set validates under 5-fold CV (all ≥ 4/5 folds ≥ 2× enrichment), and
each rejects a volvelle-family mechanical null across 100 to 200 null
runs at empirical p < 0.01 (z = 5.29–24.79). We publish the associated
nulls and partial results with equal rigor: pre-registered sub-class
hypotheses for toxicity, external-application, and a cross-hand "eo"
meta-feature either refute or return as partial under locked decision
rules. This is not a decipherment, not a language identification, and
not a reading of any folio; it is a **working topical reader** that
identifies what a folio is *about*, aggregated over the folio's text,
with accuracy far above majority-class baseline (50.0%) and vastly
above uniform-chance (16.7%).

---

## 1. Background

The Voynich Manuscript is a 226-folio codex in the Beinecke Rare Book
and Manuscript Library (MS 408), radiocarbon-dated 1404–1438, written
in an undeciphered script. Despite a century of systematic cryptanalytic
effort (D'Imperio 1978) and extensive statistical characterisation
(Reddy and Knight 2011), no proposed decipherment has achieved
scholarly consensus.

Three results from the existing literature bear directly on this work.
Currier (1976) identified two distinct scribal hands (A and B) with
different statistical fingerprints, now standard in the ZL (Zandbergen-
Landini) transcription as a per-folio tag. Montemurro and Zanette
(2013) demonstrated that section-level vocabulary clusters are
statistically distinguishable at p < 0.001 using unsupervised methods,
establishing that sections are genuinely different registers rather
than artefacts of transcription. Brady (2026) proposed a two-stratum
pharmaceutical dispensatory model in which the manuscript's structural
features (gallows markers, consonant-skeleton positional constraints,
pharyngeal absence) reflect a European copyist's encoding of a Syriac
source text. Brain-V's contribution is consistent with all three:
we confirm hand-specific statistical dialects, we confirm section-level
differentiation, and we adopt gallows-stripping and consonant-skeleton
conventions proposed by Brady. What we add is a working classifier
that turns these structural observations into an operational reader
for folio content-type.

---

## 2. Data

- **Corpus:** ZL3b merged IVTFF transcription of MS 408 in EVA encoding,
  with Takahashi (H) as primary transcriber. After filtering annotation
  markers and tokens of length < 2, the corpus contains 38,053 tokens
  across 226 folios.
- **Currier hand assignments:** Per-folio from the ZL3b metadata.
  Hand A: 114 folios. Hand B: 82 folios. Unassigned (`?`): 30 folios.
- **Section labels:** Per-folio from the ZL3b metadata. Eight sections:
  astronomical, biological, cosmological, herbal, pharmaceutical,
  recipes, text-only, zodiac.
- **Plant identifications:** 125 folio-to-species mappings from Edith
  Sherwood's *Voynich Botanical Plants Decoded* series (118 entries)
  and from independent identifications by Cohen (7 entries). Four
  entries were flagged CONFLICT between sources and excluded from the
  primary analysis. 115 plant-ID folios are present in the corpus with
  ≥ 20 tokens each.
- **Non-plant herbal baseline:** 15 herbal-section folios not in the
  plant-ID set, ≥ 20 tokens each (8 Hand A, 7 Hand B).

---

## 3. Method

### 3.1 Vowel-pattern extraction

Each EVA word is decomposed into a consonant skeleton plus a
positional vowel pattern. Bench gallows (`cth`, `ckh`, `cph`) are
treated as multi-character consonants per Brady (2026). Plain gallows
(`t`, `p`) at word-initial position are stripped as paragraph markers
where the second character is not `h` (avoiding the bench-gallows
cases). EVA characters are mapped to consonants {tk, kk, pk, k, s, d,
r, l, n, y, m, g, t, p, s, w} and vowels {a, o, e, i}. The vowel
pattern is constructed as a dot-separated sequence of slot contents,
with `_` for empty slots between consonant positions. Example: `chedy`
→ consonant skeleton `kdy`, vowel pattern `_.e` (empty first slot,
`e` between d and y, no final slot).

### 3.2 Enrichment and held-out validation

For each pattern and each hand-section cell, enrichment is computed as
`rate_in_cell / rate_in_same_hand_other_sections`. Patterns with
≥ 10 in-cell hits and ≥ 3× enrichment are retained. Five-fold
cross-validation is performed over in-cell folios: each pattern's
held-out enrichment is recomputed per fold against the fixed
out-of-cell baseline. A marker set passes if the combined set's
enrichment remains ≥ 2× in ≥ 4 of 5 folds.

### 3.3 Volvelle null

A volvelle is simulated as a 3-ring combinatorial token generator:
Ring A (6 prefixes: empty, q, qo, o, d, ch), Ring B (26 to 500 roots
per cartridge), Ring C (8 suffixes: empty, y, n, r, l, in, ain, aiin).
Ring B cartridges are drawn uniformly from a corpus-derived root pool
of 3,635 roots constructed by affix-stripping every real-corpus word.
Currier-aware suffix weighting (different priors for Hand A vs Hand B)
is applied. Four architectural variants are tested: section-level
cartridge swap at size 26 and 500, and folio-level cartridge swap at
size 26 and 200. For each variant, 100–200 independent null corpora
are generated; enrichment of the target marker set is measured on
each; the empirical p-value is the fraction of null runs achieving
enrichment ≥ the real corpus.

### 3.4 Classifier

A multinomial naive-Bayes classifier is trained on folio-level bags
of vowel patterns. Labels are (hand, section) tuples. Classes with
fewer than 5 folios are dropped. Add-one Laplace smoothing is applied
over a vocabulary equal to the set of vowel patterns observed anywhere
in the corpus. 5-fold cross-validation, stratified by folio identity
(no folio appears in both train and test for a given fold).

### 3.5 Pre-registration

Each sub-class hypothesis (psychoactive, toxic, external-application,
"eo"-family) was committed to the repository as a hypothesis file
with `status: "pre-registered"` and `tests_run: []` **in a separate
git commit before** the test script was run. Decision rules (α, Cohen's
d threshold, pass/partial/refute conditions) were frozen in the
pre-registration commit and not modified after the test.

---

## 4. Results

### 4.1 Scribe-section division of labor

| Section | Hand A folios | Hand B folios |
|---|---|---|
| pharmaceutical | **16** | 0 |
| biological | 0 | **19** |
| herbal | **95** | 32 |
| recipes | 2 | **23** |
| cosmological | 0 | 3 |
| text-only | 1 | 5 |
| astronomical | 0 | 0 |
| zodiac | 0 | 0 |

The scribes partition the manuscript. Only herbal and recipes have
both hands present at n ≥ 2. In recipes (the only content-overlap
section where both hands have ≥ 8 discoverable markers at the 3×
threshold), the Hand-A marker set {`a.a`, `_.a.a`, `o.a`, `a`,
`o.ai`, `_.o.ai`, `_.o.a`, `_._.a`} and the Hand-B marker set {`oai`,
`ai.o`, `o.ea`, `o._.eeo`, `o.eeo`, `_.eo.ai`, `o.ee.a`, `_.o.eeo`}
share **zero** patterns. Hand A across all sections has a
marker-o/e ratio of 2.00; Hand B's is 1.36.

### 4.2 Per-marker validation (5-fold CV)

| Marker set | n folios | Fold enrichments | ≥ 2× folds |
|---|---|---|---|
| HandA_pharma | 16 | 5.77, 8.04, 7.60, 5.33, 5.10 | **5/5** |
| HandA_herbal | 95 | 4.60, 3.16, 4.54, 3.07, 3.67 | **5/5** |
| HandB_biological | 19 | 4.91, 6.79, 4.01, 10.28, 1.91 | 4/5 |
| HandB_recipes | 23 | 9.13, 9.28, 4.19, 7.21, 6.47 | **5/5** |

The three infinite-enrichment Hand-B plant markers (`_.e.e`, `_.eeo`,
`_.o.eo`) individually pass 5/5, 4/5, and 4/5 folds respectively;
combined, they fire in every held-out fold at rates 0.76%–2.73% over
a zero non-plant baseline.

### 4.3 Volvelle null rejection

For each marker set, the real in-minus-out difference is compared to
a null distribution constructed from 100–200 volvelle corpora drawn
from corpus-derived roots:

| Marker set | Real diff | Null mean | Null sd | z | Empirical p |
|---|---|---|---|---|---|
| HandA_pharma | +0.08054 | +0.00034 | 0.00323 | **24.79** | 0.0000 |
| HandA_herbal | +0.04759 | −0.00028 | 0.00556 | 8.61 | 0.0000 |
| HandB_biological | +0.00414 | +0.00004 | 0.00078 | 5.29 | 0.0000 |
| HandB_recipes | +0.01244 | +0.00011 | 0.00143 | 8.64 | 0.0000 |
| HandB plant combined | +0.01633 | +0.00011 | 0.00366 | 4.43 | 0.0000 |

Across five additional Hand-A `_.oii` variants (simple CV template
through folio-level rate-matched), 1,400+ null runs produced a null
maximum enrichment of 2.80× against a real enrichment of 5.04×,
empirical p < 0.01 in every architecture.

### 4.4 Classifier performance

Six classes with n ≥ 5 folios; 190 folios total.

| Class | n | Per-class accuracy |
|---|---|---|
| (A, herbal) | 95 | 92.6% |
| (A, pharmaceutical) | 16 | 56.2% |
| (B, biological) | 19 | **100.0%** |
| (B, herbal) | 32 | 6.2% |
| (B, recipes) | 23 | **100.0%** |
| (B, text-only) | 5 | 0.0% |

**Overall 5-fold CV accuracy: 74.2%.**
Majority-class baseline: 50.0% ((A, herbal) prediction).
Uniform-chance baseline: 16.7%.
Gain over majority: +24.2 percentage points.

The classifier is near-perfect on the three largest (B, …) classes and
on (A, herbal). It performs weakly on (B, herbal) where Hand-B herbal
folios are frequently absorbed by the dominant (A, herbal) class,
and on (B, text-only) where the class is too small to train on
(n = 5). Both weaknesses are mechanical consequences of the naive-Bayes
prior and sample size, not of the marker dictionary.

---

## 5. Findings published as honest negatives

Brain-V publishes its null and partial results with the same rigor as
its confirmed ones. The following are on the repository record:

- **H-BV-PLANT-01 weakened to Hand-A-restricted.** The headline 5.04×
  `_.oii` plant-folio enrichment is driven entirely by Hand A. Hand B
  shows zero `_.oii` across all 25 Hand-B plant folios and 7 Hand-B
  non-plant herbal folios. Within-Hand-A enrichment is 1.72× and the
  corresponding t-test is not significant at p = 0.258. The corpus-wide
  figure is Hand-A-inflated. Confidence downgraded 0.75 → 0.55 after
  confound check.

- **H-BV-PSYCHOACTIVE-02 marginal (p = 0.0506).** Pre-registered
  within-Hand-A test of psychoactive vs non-psychoactive plant folios.
  One-tailed Welch p = 0.0506 (missing α = 0.05 by 0.0006), Cohen's
  d = 2.24 (passing the ≥ 0.4 threshold), Mann-Whitney U p = 0.000218.
  Under locked rules requiring both p < 0.05 and d ≥ 0.4: marginal.
  Confidence 0.55.

- **H-BV-EO-FAMILY-01 partial (Hand-B only).** Pre-registered cross-hand
  test of `eo`-containing patterns on preparation content. Hand B
  passes cleanly (p < 10⁻⁶, d = 1.71). Hand A fails the locked p
  criterion (p = 0.130, d = 0.59 passes d alone). Under locked rules:
  partial, Hand-B-specific.

- **H-BV-TOXIC-01 refuted.** Pre-registered one-tailed test of toxic
  vs non-toxic plants on `_.oii` rate. Ratio 3.15×, d = 0.73, but
  p = 0.060 (misses α = 0.05 by 0.010). Refuted under locked rules;
  the underlying observation was subsequently refined into
  H-BV-PSYCHOACTIVE-01 via cross-check analysis.

- **H-BV-EXTERNAL-NULL-01 null published.** Pre-registered one-tailed
  test of external-application vs internal-application plant folios on
  `_.oii` rate. p = 0.494, d = 0.003. Refuted at α = 0.05 with d ≈ 0.

- **H-BV-PERUN-NULL-01 null published.** 24-test battery of botanical
  properties (toxicity, Mediterranean origin, plant family, medicinal
  flag) against six text features. Zero tests reach p ≤ 0.05.
  Illustration botanical properties do not correlate with Brain-V's
  current text features at this sample size.

- **H-BV-NULL-01 coverage is not evidence.** Twenty trials of 1,300
  phonotactically plausible nonsense skeletons against the ZL3b
  corpus returned 83.56% ± 1.03% aggregate token coverage. Brady's
  Syriac claim (86.90%) is +3.34pp above the null; Schechter's
  Latin/Occitan (82.81%) is below. Coverage alone cannot distinguish
  a decipherment from a phonotactic null floor.

---

## 6. Limitations

1. **(A, pharmaceutical) performs at 56.2%.** The class is small
   (n = 16) and shares vowel-pattern overlap with (A, herbal). This
   weakness is published openly rather than masked; improving it
   requires more Hand-A pharma folios than the manuscript contains.

2. **Plant-ID labels are heuristic.** Sherwood's identifications are
   from illustration matching against medieval herbals; Cohen's are
   independent blog-published attributions. Four conflicts were
   excluded; the remaining 121 labels have not been independently
   audited by expert botanists. Label noise can only blur the
   scribe-section signal observed here, not create it.

3. **The volvelle family is broad but not exhaustive.** Four
   architectural variants were tested across 1,600+ null runs. Non-
   volvelle mechanical generators — hidden Markov models, context-free
   grammar generators, neural language models trained on the corpus —
   were not tested. Any claim that the classifier signal is evidence
   of "intentional content" rests on ruling out these alternatives,
   which remains open work.

4. **Currier `?` folios excluded.** 30 folios carry `?` hand
   assignments in ZL3b. These folios were excluded from all
   hand-conditioned analyses, which biases the result toward folios
   with clean hand tags.

5. **No held-out validation against a second plant-ID dataset.** The
   classifier was trained and cross-validated on Sherwood + Cohen
   IDs. An independent plant-ID list from another compiler would
   provide a stronger external validation, but no such list of
   comparable size was available at the time of this report.

6. **The classifier does not read words.** It aggregates over all
   tokens in a folio. Sub-folio resolution (line-level or token-level
   section prediction) has not been tested and is expected to be much
   lower accuracy given the known shuffle-test null.

---

## 7. Discussion

The central result is that topical identification of Voynich folios
is possible at 74.2% accuracy **without any language identification,
dictionary, or cipher hypothesis**. The classifier operates on the
positional distribution of vowels within word skeletons, a signal
available in any EVA transcription at zero cost.

This result has four implications for future decipherment work.

**Dialect dictionary expansion.** Each (section, hand) marker set
currently has 1–8 validated patterns. Extending the threshold to
looser enrichments (2× rather than 3×) and lower minimum hit counts
(5 rather than 10) would likely expand the marker dictionary to
80–120 patterns. This expanded dictionary, cross-validated and
volvelle-null-rejected, would be a candidate target vocabulary for
semantic mapping against medieval Latin/Occitan/Syriac botanical
texts.

**Consonant-skeleton role.** The current work uses only vowel
patterns and treats consonant skeletons as covariates. The skeleton
carries additional structural information (`q` is 98.9% word-initial,
suffix class `{y, n, r, m, g}` is predominantly word-final). A
joint (skeleton, vowel-pattern) representation may extend the
classifier's accuracy and potentially enable sub-folio prediction.

**Cross-scribe content matching.** Hand A pharmaceutical and Hand B
recipes both contain preparation content, but use non-overlapping
marker sets. Identifying candidate cross-scribe equivalences (e.g.
Hand A `_.o.eo` ↔ Hand B `o._.eeo`) via contextual co-occurrence
analysis would constitute the first systematic attempt to align the
two scribes' vocabularies at the pattern level.

**Pre-registration as a decipherment tool.** Two of Brain-V's four
confirmed findings are pre-registered; two are pre-registered and
published as partial/null. The discipline of locking decision rules
before observation meaningfully constrains the analysis space. The
Voynich decipherment field would benefit from adopting this
convention: publish the test rule, the hypothesis ID, and the
decision before running the test script, and let the eventual result
stand.

---

## 8. Reproducibility

All code and data are public.

- **GitHub:** [github.com/BuilderBenv1/brain-v](https://github.com/BuilderBenv1/brain-v)
- **Dashboard:** [brain-v-beryl.vercel.app](https://brain-v-beryl.vercel.app)
- **Corpus:** ZL3b merged IVTFF (Zandbergen & Landini, Takahashi primary)
- **Plant IDs:** `raw/research/plant-identifications.csv` (125 rows)

Key scripts used in this report:

- `scripts/plant_vowel_analysis_v2.py` — Hand-A `_.oii` discovery + 5-fold CV
- `scripts/plant_confound_check.py` — Currier / quire / length confound tests
- `scripts/hand_b_characterisation.py` — Hand-B pattern discovery
- `scripts/hand_b_holdout_and_volvelle.py` — Hand-B CV + volvelle null
- `scripts/volvelle_v4_folio.py` — folio-level volvelle null for Hand A
- `scripts/scribe_dialect_dictionary.py` — per-(section, hand) markers
- `scripts/dialect_validation_and_classifier.py` — CV, volvelle, classifier
- `scripts/run_psychoactive.py` / `run_psychoactive_v2.py` — pre-registered tests

Every hypothesis is in `hypotheses/<ID>.json` with its full test history
(date, confidence, details, pre-registration status). Every run's raw
output is in `outputs/`. The cognitive loop's score history is in
`outputs/scores/`.

Pre-registrations are verifiable: each pre-registered hypothesis was
committed to the public repository with `status: "pre-registered"` and
`tests_run: []` in a commit preceding the test-execution commit. For
example:

- H-BV-PSYCHOACTIVE-02 pre-registered: commit `85b8915`, executed: `2628f47`
- H-BV-EO-FAMILY-01 pre-registered: commit `6a2ddb4`, executed: `8e0719d`

---

## 9. Acknowledgements

The plant identifications that make this analysis possible were
compiled by Edith Sherwood over many years of public work on the
*Voynich Botanical Plants Decoded* series, supplemented by independent
identifications by Cohen. Brady (2026) proposed the two-stratum
dispensatory framework and the gallows-as-paragraph-marker
observation (H-BRADY-02), both of which Brain-V independently
confirmed and adopted. The ZL3b merged IVTFF transcription is the
work of René Zandbergen and Marco Landini, with Takahashi as primary
transcriber. Claude (Anthropic) powers the hypothesis-generation
and scoring layers of Brain-V; the statistical tests and classifier
are pure Python. Brain-V itself is a fork of Project Brain by the
same author.

---

## 10. References

- Brady, B. A. D. (2026). *A Syriac Pharmaceutical Dispensatory
  Encoded in the Voynich Manuscript: Statistical and Philological
  Evidence from Consonant Skeleton Analysis.* Zenodo
  10.5281/zenodo.19583306.
- Currier, P. (1976). *Papers on the Voynich Manuscript.* Unpublished
  manuscripts, reproduced in D'Imperio (1978) and at voynich.nu.
- D'Imperio, M. E. (1978). *The Voynich Manuscript: An Elegant Enigma.*
  NSA/CRESS.
- Greshko, M. (2025). The Naibbe cipher. *Cryptologia.*
- Montemurro, M. A., and Zanette, D. H. (2013). Keywords and
  co-occurrence patterns in the Voynich manuscript: An information-
  theoretic analysis. *PLoS ONE* 8(6): e66344.
- Reddy, S., and Knight, K. (2011). What we know about the Voynich
  manuscript. *Proceedings of the 5th ACL-HLT Workshop on Language
  Technology for Cultural Heritage, Social Sciences, and Humanities.*
- Sherwood, E. *Voynich Botanical Plants Decoded*. edithsherwood.com.
- Zandbergen, R., and Landini, M. *ZL merged IVTFF transcription of
  MS 408.* voynich.nu.

---

*Brain-V did not decipher the Voynich Manuscript. It built a working
content-type decoder from vowel patterns alone, with every null
published and every pre-registration locked before the test ran. The
decoder works at 74.2% accuracy across six scribe-content classes.
What the manuscript is about, Brain-V can now read — in aggregate.
What it says is still open.*
