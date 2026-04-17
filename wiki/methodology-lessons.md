---
type: methodology
last_updated: 2026-04-17
source: pre-registered-failures
status: canonical
---

# Methodology Lessons

Three methodology lessons accumulated through pre-registered hypothesis failures, 2026-04-17. Each lesson is traceable to a specific Brain-V hypothesis where the methodology gap was first detected. These are the canonical methodology notes for v2's methodology section.

A methodology section listing lessons learned through pre-registered failures is more credible than one claiming the framework worked perfectly throughout. Brain-V's pre-registration audit trail is the evidence.

## Lesson 1 — Pre-register exact numerator and denominator

**Detected in:** H-BV-EXTERNAL-PREDICTIONS-01 Test 3 (Caveney word-final n)

**The failure:** The natural-language claim ("of all n occurrences, most are word-final") was translated into a pre-registered metric as `tokens ending in n / all Hand A tokens`. That metric measures how common final-n is in the vocabulary, not whether n is word-final when it appears. The two are fundamentally different.

**Concrete numbers:** Locked (incorrect) metric yielded 15.46%, FAIL. Correct metric (of all n occurrences, word-final fraction) yielded 94.61%, PASS. A refute-vs-confirm reversal on the same underlying linguistic claim.

**The rule:** Every pre-registered metric must specify its numerator and denominator with set-theoretic precision. Natural-language claims like "most X are Y" are ambiguous — they can be converted to `|{X with property Y}| / |X|` OR `|{tokens containing X at position Y}| / |tokens containing X anywhere|` OR something else again. The conversion must be stated in the pre-registration, not left to the reader.

**How to apply:** For every metric in a pre-registration, include:
1. The numerator as a set definition (what counts)
2. The denominator as a set definition (what is the reference universe)
3. At least one worked example on a concrete token, showing the computation step by step

**Corrective hypothesis:** H-BV-CAVENEY-FINAL-N-01 (pre-registered cleanly, CONFIRMED at 0.9461).

## Lesson 2 — Lock tokenisation when referencing prior-hypothesis baselines

**Detected in:** H-BV-COMPOSITE-OUTER-01 M4 (dealer density anomaly reduction)

**The failure:** The pre-registration locked `observed_glyph_mean = 2.4182`, a number imported from H-BV-EXTERNAL-PREDICTIONS-01 T2. T2 was measured under a tokenisation that did NOT treat `ol` as a ligature. COMPOSITE-OUTER-01's own tokenisation DID treat `ol` as a ligature (inherited from H-BV-SUFFIX-SUBCLASS-01 conventions). The reduction metric therefore compared a value measured under one tokenisation against a value measured under another.

**Concrete numbers:** Under COMPOSITE-OUTER-01's own tokenisation, the baseline Hand A suffix crust-glyph mean is 2.0414, not 2.4182. About 95% of the apparent reduction (from 2.4182 to 2.0233) is attributable to the tokenisation choice, not to composite decomposition. The "real" composite-decomposition contribution is ~0.02.

**The rule:** Pre-registrations that import values from earlier hypotheses must ALSO lock the tokenisation under which those values were measured. If the current hypothesis uses a different tokenisation, the baseline value must be recomputed under the current tokenisation, not imported wholesale.

**How to apply:** When pre-registering a test that references a prior-hypothesis baseline:
1. State the tokenisation locked in the prior hypothesis explicitly
2. State the tokenisation locked in the current hypothesis explicitly
3. If they differ, recompute the baseline under the current tokenisation before using it
4. If they match, cite both and proceed

**Followup:** Use a consistent tokenisation across a test family, or accept the cost of recomputing baselines each time a tokenisation changes. Brain-V currently has at least three tokenisations in use across hypotheses (no-ol-ligature; ol-ligature; ol+qo-ligature) — this proliferation itself is a risk.

## Lesson 3 — Sanity-check external baselines on the original corpus before applying to new data

**Detected in:** H-BV-DENSITY-DIAGNOSIS-01 (diagnosis of the 3x suffix dealer gap)

**The failure:** H-BV-EXTERNAL-PREDICTIONS-01 T2 imported Stolfi's published 0.80 suffix dealer mean as an external pass band reference. Brain-V's measurement on Hand A yielded 2.4182 — a 3x drift — which was interpreted as "Hand A has substantially denser crust glyphs than Stolfi's B baseline." DENSITY-DIAGNOSIS-01 later ran the identical Brain-V operationalisation on Hand B (= Currier B, Stolfi's primary corpus) and measured 2.5168. Both hands land near 2.4-2.5; the drift is between Brain-V's pipeline and Stolfi's published numbers, not between hands.

**Concrete numbers:** Fraction of the Hand A excess attributable to pipeline drift ≥ 106%. Hand B shows the drift equally. The "Hand A is unusually dense" framing was an artefact of comparing Brain-V's code to Stolfi's published statistics without first verifying that Brain-V's code reproduces those statistics on Stolfi's own corpus.

**The rule:** Pre-registrations referencing external published baselines must include a PREREQUISITE sanity check: Brain-V's pipeline must reproduce the external number on the corpus where the external author originally measured it, WITHIN A TOLERANCE, BEFORE the baseline can be applied to new data. If the sanity check fails, the comparison is between pipelines, not between corpora — and the pipeline drift must be diagnosed (see H-BV-STOLFI-RECONCILIATION-01) before any substantive claim is made.

**How to apply:** When pre-registering a test against an external baseline:
1. Identify the corpus the external author measured on
2. Run Brain-V's planned measurement on that same corpus
3. Check whether the Brain-V result reproduces the external number within ~5% tolerance
4. If yes: proceed, baseline is methodologically sound
5. If no: the drift must be diagnosed (tokenisation, categorisation, filtering, definition) before the baseline can be trusted. The original external-prediction test is suspended until drift is resolved, or its interpretation is reframed as 'pipeline-vs-external' rather than 'corpus-property'.

**Why it matters most:** Lessons 1 and 2 can be caught by careful pre-registration review. Lesson 3 requires actually running the test on the original author's corpus, which is an extra step and easy to skip. But if Brain-V wants to compare its findings against 25 years of prior Voynich structural analysis — as v2 intends to — this sanity check is the load-bearing prerequisite. Without it, every "Brain-V finds X where prior author reported Y" claim is potentially an implementation artefact.

## Cross-cutting principle

All three lessons share a common shape: **operational precision beats natural-language precision**. Pre-registration is not just "write down the hypothesis before running the test" — it is "write down the exact computation, the exact inputs, the exact tokenisation, the exact comparator, with sufficient precision that an independent replication can reproduce the test within ~1% agreement." Brain-V's framework learned this one precision at a time.

## Related

- [[H-BV-EXTERNAL-PREDICTIONS-01]] — source of Lesson 1
- [[H-BV-COMPOSITE-OUTER-01]] — source of Lesson 2
- [[H-BV-DENSITY-DIAGNOSIS-01]] — source of Lesson 3
- [[H-BV-CAVENEY-FINAL-N-01]] — Lesson 1's corrective pre-registration
- [[H-BV-STOLFI-RECONCILIATION-01]] — Lesson 3's diagnostic follow-up (pending)
