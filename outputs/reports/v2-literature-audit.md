# Brain-V v2 — Literature Audit of 20 Findings

**Date:** 2026-04-17
**Purpose:** Classify each Brain-V finding against prior Voynich literature, so v2 headlines genuine novelty, cites re-discoveries, and frames independent verifications honestly.
**Method:** Checked each finding against named primary sources (Currier 1976, Tiltman 1967, Stolfi 2000, Reddy & Knight 2011, Montemurro & Zanette 2013, Lindemann & Bowern 2020, Bowern & Lindemann 2021, Zattera 2022, Caveney 2020, Havrankova 2025) plus voynich.nu analysis pages, voynich.ninja, and the computational-attacks blog network. "UNKNOWN" is preferred to guessing.

---

## Audit table

| # | Finding (one line) | Classification | Citation(s) | Confidence | Notes |
|---|---|---|---|---|---|
| 1 | Character-level Markov-1 flatness (H_cond ~2.0-2.2 vs natural ~3.5) | INDEPENDENT_VERIFICATION | Reddy & Knight 2011; Lindemann & Bowern 2020 | HIGH | Both established Voynichese's anomalously low h2 relative to natural languages; Brain-V reproduces with reconciled methodology and separates Hand A/B numerically. |
| 2 | Alphabet-size-normalised H_cond gap (0.45 vs 0.60) | QUANTITATIVE_REFINEMENT | Lindemann & Bowern 2020 | MEDIUM | L&B discuss the caveat that small alphabets inflate entropy gap and correct for it; Brain-V's specific normalised number is a numeric restatement, not a new concept. |
| 3 | Higher-order conditional entropy ratio H_cond(k=3)/H_cond(k=1) ~0.84 vs natural 0.58-0.70 | QUANTITATIVE_REFINEMENT | Reddy & Knight 2011 (trigram redundancy); Lindemann & Bowern 2020 | MEDIUM | Reddy & Knight note "exceptionally low bigram and trigram redundancy"; the *ratio* framing and cross-language comparison numbers (Basque/Hungarian/Esperanto) are Brain-V's specific operationalisation of a well-known qualitative observation. |
| 4 | Esperanto 0/6 closest to Hand A on character-level metrics | TRULY_NOVEL | — | MEDIUM | Lindemann & Bowern 2020 included Esperanto and other conlangs as corpus samples but did not report a cross-metric "closest" tally against Hand A specifically; framing as rebuttal to an explicit conlang-match hypothesis appears original. |
| 5 | Stolfi prefix/suffix dealer asymmetry reproduced (0.14/0.80, ratio 0.175) | INDEPENDENT_VERIFICATION | Stolfi 2000 | HIGH | Stolfi grammar.html explicitly reports "prefix averages 0.14 dealers, suffix averages 0.80 dealers" — Brain-V's numbers match to two decimals. Classify as verification not refinement because numbers are identical. |
| 6 | Stolfi crust-only 75% fails to reproduce (Brain-V measures 26-29%) | UNKNOWN (likely SPURIOUS CLAIM) | Stolfi 2000 | HIGH | **Critical:** Stolfi actually wrote "almost exactly 1/4 of the normal words have no core or mantle, only the crust layer" — i.e. 25%, not 75%. Brain-V's 26-29% measurement *reproduces* Stolfi, it does not fail to. The "75%" in Brain-V's prior-work doc (hypotheses/H-BV-BASQUE-HEADER-MAP-01 era) is a misreading. v2 must correct this: finding 6 should be re-labelled "Stolfi 25% crust-only rate reproduced at 26-29%" and moved to INDEPENDENT_VERIFICATION. |
| 7 | Two-layer terminal morphology (closed Layer-1 inner, Layer-2 outer inventories) | QUANTITATIVE_REFINEMENT | Stolfi 2000 (prefix-midfix-suffix); Zattera 2022 (12-slot grammar) | MEDIUM | Zattera's 12-slot grammar already partitions slots into type-1 (0-5) and type-2 (6-11) groups, with Naibbe cipher (Greshko 2025) adopting this bipartite structure. Brain-V's specific top-10/top-5 coverage numbers (93%/86%) are quantitative refinements within an established two-layer frame. |
| 8 | Vowel/consonant sub-slot selectional asymmetry; n vowel-exclusive | TRULY_NOVEL | — | MEDIUM | Slot grammars (Stolfi, Zattera) constrain which glyphs co-occur but do not to my knowledge report a V/C partition of Layer-1 glyphs or quantify Layer-2 selectional differentials by vowel-class. The specific claim "n is vowel-exclusive (0/2240)" appears original. Havrankova 2025 has no such test. |
| 9 | Caveney word-final n at 94.6% in Hand A | QUANTITATIVE_REFINEMENT | Caveney 2020 (voynich.ninja thread 3354); Stolfi 2000 (positional constraints) | HIGH | Caveney's original forum post is qualitative ("n restricted to word-final/syllable-coda, striking correspondence with Basque"); provides no percentage. Stolfi lists n as constrained positionally. Zandbergen a2_char.html notes final-n behaviour without the specific rate. Brain-V's 94.6% is the first quantitative realisation of Caveney's qualitative claim on Hand A. |
| 10 | y-terminal Layer-2 ordering (r→y, ol→y, l→y at 97-99%) | QUANTITATIVE_REFINEMENT | Stolfi 2000; Zandbergen voynich.nu | MEDIUM | y as "final" or "terminal" in slot grammars is standard (Stolfi: y "almost exclusively word-initial or word-final"; voynich.nu notes -dy final dominance in Currier B). Brain-V's r/ol/l → y specific pairwise orderings at 97-99% look like novel quantitative refinement of a known positional constraint; classification could flip to TRULY_NOVEL for the specific pairs if no prior count exists. |
| 11 | Folio-level clustering of composite outer pairs, Cramer's V=0.61 | UNKNOWN | — | LOW | I could not find prior work measuring folio-level non-uniformity of composite suffix pairs with a Cramer's V statistic. Montemurro & Zanette 2013 operate at word level, not morpheme-pair level. Very likely novel but confidence is LOW because absence-of-evidence in a 100-year literature is hard to certify in 10 minutes. |
| 12 | Hand A matches Basque 6/6 on 5-metric typology (M1-M5) | TRULY_NOVEL | — (Havrankova 2025 proposes Basque qualitatively; Caveney 2020 proposes Basque qualitatively) | HIGH | No prior Basque-Voynich work operationalises a five-metric morphological typology test. Havrankova's paper is explicitly philological-qualitative with no null model. Brain-V's 6/6 pass is a genuinely new structural-typological result. This is the headline novelty candidate. |
| 13 | Hand B section-sensitive vocabulary (TTR, chedy by section) | INDEPENDENT_VERIFICATION | Montemurro & Zanette 2013 | HIGH | M&Z demonstrate "strongly non-uniform distribution" of top informative words across thematic sections, explicitly including shedy and qokeedy as top informative tokens. Brain-V verifies via TTR-on-folio methodology which is independent of M&Z's information-theoretic approach. |
| 14 | Chedy as biological marker (70% higher, d=+1.08) | QUANTITATIVE_REFINEMENT | Montemurro & Zanette 2013 | HIGH | M&Z list chedy among top-30 informative tokens with non-uniform section distribution; do not publish per-section effect sizes. Brain-V's specific effect size and biological-sole-driver claim is a quantitative refinement of M&Z's qualitative non-uniformity finding. |
| 15 | 8 of 20 top Hand B tokens section-concentrated | QUANTITATIVE_REFINEMENT | Montemurro & Zanette 2013 | HIGH | M&Z report this qualitatively across the top-30; Brain-V reframes as a per-token count on a different ranked list (top-20 Hand B). Same underlying phenomenon, specific cuts are Brain-V's. |
| 16 | Hand A's 86% herbal composition explains its apparent section-independence | TRULY_NOVEL | — | MEDIUM | This is a methodological correction: the "Hand A has no section-content coupling" non-finding is explained by sampling composition. I found no prior work that flags Hand A's herbal dominance as the reason for null section results on Hand A. Havrankova does not discuss. Likely original. |
| 17 | qo-k- morphological class amplifies biological preference (d=+2.05 vs +1.00) | TRULY_NOVEL | — | MEDIUM | M&Z identify qo-k- tokens as individually section-concentrated but don't decompose the qo- prefix by presence/absence of k-core. voynichattacks.wordpress.com notes qok- concentration in Currier B broadly. The specific compositional-decomposition finding (k-core roughly doubles qo's biological tilt) appears novel. |
| 18 | Q-initial tokens broadly biological-preferring (24% vs 13%) | INDEPENDENT_VERIFICATION | Montemurro & Zanette 2013; voynich.nu (Currier B / Bio-B discussion) | HIGH | Qualitatively known that q-initial tokens dominate Currier B and cluster in biological/balneological folios. Brain-V's specific 24% vs 13% cut on folio composition is a numeric packaging of the known Currier-language/section correspondence. |
| 19 | Hand A mean-length drift with folio position (Spearman rho=+0.36, p<0.001) | UNKNOWN (likely TRULY_NOVEL) | — | LOW-MEDIUM | Known in the literature: mean word length varies by *section* (herbal 4.0, recipes 4.7 — Zandbergen, voynich.nu). Unknown to me: whether anyone reports a monotonic *folio-position* correlation within Hand A specifically. voynichattacks.wordpress.com analyses word positions within lines, not across folio sequence. Likely original structural observation but could be subsumed by section-variation if herbal occupies earlier folios. Flag for closer-look at sampling. |
| 20 | Hand A vs Hand B converge on herbal statistics (TTR 0.83=0.83, mean length 4.99 vs 5.07) | TRULY_NOVEL | — | HIGH | This is the "controlled comparison" result. Prior literature (Currier 1976, Zandbergen) emphasises A/B *differences*; Brain-V's contribution is showing that when you condition on section (herbal), the differences attenuate to non-significance. I have found no prior paper performing this within-section controlled comparison. Strong novelty candidate. |

---

## Summary

### Counts per category

| Category | Count |
|---|---|
| TRULY_NOVEL | 5 (#4, #8, #12, #16, #20) |
| QUANTITATIVE_REFINEMENT | 6 (#2, #3, #7, #9, #14, #15) |
| INDEPENDENT_VERIFICATION | 5 (#1, #5, #13, #18 — plus #6 after correction) |
| RE-DISCOVERY | 0 (no pure re-discoveries identified; Brain-V's methodology consistently adds something) |
| UNKNOWN | 3 (#10 — likely QR, #11 — likely novel, #17 — likely novel, #19 — likely novel) — net after resolution, most collapse toward QR or TRULY_NOVEL |

Note on #6: per Stolfi grammar.html, the crust-only rate is 25%, not 75%. Brain-V's 26-29% measurement therefore *reproduces* Stolfi and should be re-classified as INDEPENDENT_VERIFICATION with a correction note. The "fails to reproduce" framing currently in `hypotheses/H-BV-BASQUE-HEADER-MAP-01` and `outputs/reports/prior-work-basque-voynich.md` is based on a misreading of Stolfi (§2.1 claim 1 of the prior-work doc says "~75% of tokens are crust-only", which is the inverse). **This is the single most important correction v2 must make before submission.**

### Key novelty candidates (headline these)

- **#12 — Hand A Basque typology match (6/6 on M1-M5).** First falsifiable structural test of the Basque hypothesis. Havrankova (2025) proposes Basque philologically with zero statistical predictions; Caveney (2020) makes one qualitative claim. Brain-V's five-metric pass is the first structural-typological Basque test in the literature. This is the strongest TRULY_NOVEL item — make it the lead.

- **#20 — Hand A/B within-section convergence.** Controlled-comparison framing. The classical A/B literature (Currier 1976 onwards) emphasises *differences*; Brain-V shows that when section is held constant, the differences attenuate. This is methodologically distinctive and directly actionable: it reframes the Currier split as partly a sampling artefact of which section each hand dominates.

- **#16 — Hand A herbal-composition explains its section-independence.** Complements #20. Together they form a clean narrative: "Apparent A/B differences are partly section-confounded; when you control for section, they shrink." This is a structural finding about the corpus's own sampling, not about Voynichese per se, but it matters for every prior comparison.

- **#8 — vowel/consonant sub-slot selectional asymmetry (n vowel-exclusive).** Extends Stolfi/Zattera slot grammar with a phonologically-typed partition. Novel if nobody in the slot-grammar lineage has published V/C-typed Layer-1/Layer-2 co-occurrence. Worth a full section.

- **#4 — Esperanto 0/6 rebuttal.** Narrow but publishable as a rebuttal-to-Friedman footnote. Friedman's constructed-language hypothesis is standard background; Esperanto being the most-studied conlang makes it the natural test case. Brain-V's 0/6 is a clean negative result.

### Key re-discoveries to cite explicitly

- **#1 (H_cond flatness)** must cite Reddy & Knight 2011 and Lindemann & Bowern 2020 as the origin of the observation. Brain-V's contribution is the Hand-A/Hand-B split numbers, not the flatness itself.
- **#5 (Stolfi 0.14/0.80 dealer rates)** must cite Stolfi 2000 — Brain-V's numbers are *identical* to Stolfi's. This is reproduction-of-a-numeric-claim.
- **#6 (crust-only rate)** must cite Stolfi 2000 — and correct the direction of the prediction from 75% to 25%. Without this correction, v2's reproduction of Stolfi reads as a contradiction when it is in fact a confirmation.
- **#13, #14, #15 (Hand B section-sensitivity, chedy, top-token concentration)** must cite Montemurro & Zanette 2013, whose top-30 informative-word table already names chedy, shedy, qokeedy, qokedy, qokain as section-concentrated. Brain-V's effect sizes and controlled-methodology framing are the contribution.
- **#18 (q-initial biological-preferring)** must cite voynich.nu (Currier A/B) and Zandbergen's language-extension pages; this is well-known.

### Key verifications (Brain-V's confirmation is the contribution)

- **#5** and the corrected **#6** together constitute a faithful reproduction of Stolfi's 2000 grammar on a modern reconciled-methodology pipeline. This is a reasonable secondary headline: "First independent quantitative reproduction of Stolfi's prefix-midfix-suffix dealer rates on both Hand A and Hand B." Stolfi's paper is now 26 years old and has been *cited* in almost every subsequent Voynich-computational paper, but I could not locate a prior independent re-measurement that reports his 0.14/0.80 numbers back to him. Brain-V's reproduction therefore has documentary value.

- **#1** — independent verification of Lindemann & Bowern h2 gap with separated Hand A/Hand B. L&B's headline is the gap; Brain-V confirms and quantifies the hands separately (2.19/2.02). The per-hand numbers are new; the gap is theirs.

- **#13** — Montemurro & Zanette's section non-uniformity re-confirmed via an independent information-channel (TTR-and-concentration, not mutual-information). Different statistic, same phenomenon, same direction. This is textbook IV.

### Items to resolve before v2 submission

1. **Correct the Stolfi crust-only direction in finding #6 and in `outputs/reports/prior-work-basque-voynich.md` §2.1 claim 1.** Stolfi says ~25%, not ~75%. Brain-V's 26-29% confirms.
2. **Resolve #19 (mean-length drift)** — check whether the monotonic folio-position trend survives conditioning on section. If herbal is front-loaded, the raw rho=+0.36 could collapse. This matters for TRULY_NOVEL classification.
3. **Resolve #11 (composite outer pair Cramer's V)** — find or confirm absence of prior folio-level morpheme-pair clustering work. Likely novel, currently LOW confidence.
4. **Resolve #10 (y-terminal specific orderings)** — confirm whether Stolfi, Zattera, or voynich.nu give specific pairwise r→y / ol→y / l→y rates, or only the general "y is final" rule.

### Bottom line for v2

Of 20 findings, **5 are strong novelty candidates** (items 4, 8, 12, 16, 20), **6 are quantitative refinements** that should be pitched as "we give the numbers behind previously qualitative claims" (items 2, 3, 7, 9, 14, 15), and **5 are independent verifications** that should be pitched as "we confirm prior work via an orthogonal method" (items 1, 5, 13, 18, and corrected 6). The remaining 4 are UNKNOWN pending one round of targeted literature checks (items 10, 11, 17, 19). None of the 20 findings are pure RE-DISCOVERIES requiring Brain-V to retract the claim of contribution; every item either adds numbers, adds methodology, or extends the finding to a new partition (hand, section, morpheme-class).

The paper should lead with **#12 (Basque typology 6/6)** because it is the only finding that materially advances a specific language hypothesis with a falsifiable structural test. The corrected **#6 (Stolfi reproduction)** and **#5 (dealer rates)** should be framed together as "Brain-V is the first independent quantitative reproduction of Stolfi (2000)." **#20 + #16** should be framed together as "A/B differences are partly section-confounded; within-section they converge." **#1, #3, #4** should appear together as an entropy-profile section that confirms L&B and rules out Esperanto.

---

*End of audit. ~1,900 words. All citations are to sources explicitly checked during this pass; UNKNOWN verdicts reflect inability to certify absence in a 10-minute window, not confidence that a finding is novel.*

---

## Addendum: Verification of finding #6 (crust-only rate) — 2026-04-17

The audit table above classified #6 as a "critical correction: Stolfi reports ~25%, not 75%." Direct WebFetch verification of Stolfi's grammar.html (https://www.voynich.nu/hist/stolfi/grammar.html) on 2026-04-17 revealed that the page contains **BOTH** passages, and they **contradict each other within Stolfi's own text**:

**Passage A (supports 75% crust-only):**
> "In normal words, the crust comprises either the whole word (almost exactly 75% of the normal tokens), or a prefix and a suffix thereof (25%)."

**Passage B (supports 25% crust-only):**
> "Almost exactly 1/4 of the normal words have no core or mantle, only the crust layer."

Both statements appear in the same "The crust layer" section, describing the same structural category (tokens with no core and no mantle). They give opposite percentages (75% vs 25%) and cannot both be correct.

**Implication for v2:**

1. Brain-V's 26-29% measurement matches Passage B (~25%) almost exactly.
2. Brain-V's 26-29% measurement does NOT match Passage A (75%).
3. H-BV-EXTERNAL-PREDICTIONS-01 T1 used `[0.70, 0.80]` as the pass band (based on Passage A). Under that band, Brain-V FAILS. Under a Passage B-based band `[0.20, 0.30]`, Brain-V PASSES.
4. H-BV-CRUST-ONLY-INVESTIGATION-01 concluded UNRESOLVED_OPEN_QUESTION because Brain-V's number couldn't reach 75% under any configuration. If Passage B (25%) is the correct Stolfi claim, Brain-V's finding is actually a clean INDEPENDENT_VERIFICATION of Stolfi.
5. The audit agent's original "critical correction" (claiming Stolfi reports 25%) was partially correct — Passage B does say 25% — but it missed that Passage A also exists and says 75%. The full picture is: Stolfi's page is internally inconsistent on this figure.

**Classification after verification:**

Finding #6 should be classified as **UNRESOLVED (Stolfi-internal-contradiction)** rather than "verification" or "failure to reproduce." v2 must explicitly note:
- Brain-V measures 26-29% crust-only (consistent across three IVTFF transcriptions, multiple filter variants, and multiple sub-corpora).
- Stolfi's grammar page asserts both 25% and 75% in different paragraphs.
- Brain-V's number matches the 25% claim.
- Resolving which Stolfi claim is correct requires either (a) Stolfi's source data (unavailable) or (b) a third-party reproduction.

This is a case where an audit requires the *audit itself to be audited*. The verification pass above is the canonical reading going forward.
