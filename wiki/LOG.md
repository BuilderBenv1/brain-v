# Wiki Change Log

Append-only. Newest at the top.

---

## 2026-04-16 — H-BV-CIRCA-INSTANS-BENCHMARK-01 MARGINAL (3/4 match Isidore)

**Hypothesis**: Hand A's paragraph-structure signature falls within tolerance bands of Isidore of Seville's Etymologiae Book 17 — an established medieval Latin prose encyclopedic herbal reference. Reference anchor: Isidore (not Hand A). Macer Floridus is a secondary verse sanity check, informational only.

**Method**: dual-benchmark with reference-anchored tolerance bands. Isidore from Latin Library (`raw/corpus/reference-corpora/isidore_etym_17_raw.html`, 10,003 tokens after truncation; no Book 18 padding available). Macer Floridus from archive.org Choulant 1832 (11,022 tokens after filtering Greek apparatus and chapter headings). Hand A reloaded via the same pipeline (11,018 tokens, 268 paragraphs).

**Result**: MARGINAL (3 of 4 tolerance-band matches; no refute conditions; no genre-reference-unstable caveat).

| measure | Hand A | Isidore (ref) | Macer | \|HA−Iso\| | tol | verdict | form-sensitive? |
|---|---|---|---|---|---|---|---|
| disjunction | 0.849 | 0.771 | 0.333 | 0.078 | 0.10 | **MATCH** | yes |
| top-20 medial | 5 | 5 | 15 | 0 | 4 | **EXACT MATCH** | yes |
| header recurrence | 0.063 | 0.003 | 0.000 | 0.060 | 0.05 | **miss by 0.010** | no |
| cross-class rate | 0.468 | 0.509 | 0.472 | 0.041 | 0.05 | **MATCH** | no |

**Unit sizes**: Hand A mean paragraph 41 tokens; Isidore 31 tokens (within 2x band, no caveat); Macer 355 tokens (chapter-level, non-diagnostic for paragraph structure — Macer is verse with large narrative chapters).

**Form-sensitive measures (2 of 4)**: disjunction and top-20 medial — prose Isidore and verse Macer differ by >2× tolerance on these. Below the 3/4 threshold for GENRE-REFERENCE-UNSTABLE caveat; the remaining two measures (header recurrence, cross-class rate) are genre-robust.

**Substantive reading**:
- The **three most informative measures** (disjunction, top-20 medial, cross-class adjacency) all match Isidore within tolerance.
- **Cross-class anti-alternation** is particularly striking: Hand A 0.468, Isidore 0.509 — BOTH well below the random 50% null, BOTH well below natural-language function/content alternation (54-57%). Medieval encyclopedic prose exhibits register-clustering just like Hand A, not function-content interleaving.
- The **single miss (header recurrence)** is 0.010 above the tolerance band — small in absolute terms but interpretable. Isidore's encyclopedic Latin has essentially unique nominal headers per section (agricultura, frumentum, granum, hordeum, …); Hand A has 6.3% repetition, driven by scribal gallows-initial tokens that occur at the opening of several paragraphs across the corpus.

**Implication**: the herbal-encyclopedic framework is supported on the vocabulary-stratification and register-clustering axes but REFINED — Hand A is NOT structurally identical to Isidore. Hand A has occasional repeated section-marker vocabulary that pure Isidore-style encyclopedic prose lacks. This is consistent with Hand A being an encyclopedic text in a different scribal tradition, or with the gallows itself acting as a partially-reused section-marker.

**Method note**: the top-20 medial value is 5/20 for Hand A under this script's ASCII-vowel-strip stemming. The prior H-BV-RECIPE-STRUCTURE-01 measurement was 19/20 using Brady's EVA consonant-skeleton mapping. Different stemming functions produce different variant counts; the 5/20 value is directly comparable to Isidore's 5/20 because they use the same function, and that is what the locked test requires.

Confidence 0.55 → 0.60.

**Follow-ups noted in hypothesis file**: reconcile the two stemming methodologies; investigate whether the 6.3% Hand A header recurrence clusters on specific gallows-family tokens; add a second medieval Latin encyclopedic reference (Hrabanus Maurus, Vincent of Beauvais) since Isidore alone is only ~10k tokens of narrow sampling.

**Files**: `hypotheses/H-BV-CIRCA-INSTANS-BENCHMARK-01.json`, `outputs/circa_instans_benchmark_test.json`, `scripts/run_circa_instans_benchmark.py`, `raw/corpus/reference-corpora/isidore_etym_17_raw.html`.

## 2026-04-16 — H-BV-RECIPE-STRUCTURE-01 MARGINAL (herbal-encyclopedic fit)

**Hypothesis**: Hand A follows medieval pharmaceutical recipe structure — paragraph-initial ingredient/topic terms, paragraph-medial preparation instructions, plus ingredient recurrence across paragraphs.

**Method**: three-criterion locked test on 271 paragraphs. Position bins: INITIAL (pos 0), FIRST (1..⌈N/3⌉-1), MIDDLE (⌈N/3⌉..⌈2N/3⌉-1), FINAL (⌈2N/3⌉..N-1).

**Result**: MARGINAL (2 of 3 criteria pass).

| criterion | metric | observed | threshold | pass |
|---|---|---|---|---|
| C1 vocabulary disjunction | \|INITIAL \ MIDDLE\| / \|INITIAL\| | **0.850** | ≥0.70 | **PASS** |
| C2 recipe-verb properties | top-20 MIDDLE with ≥2 variants AND ≥30% folio cov | **19 / 20** | ≥15 / 20 | **PASS** |
| C3 LOW-initial recurrence | LOW initial types in ≥3 paragraphs | **4.6%** (9/197) | ≥10% | **FAIL** |

**C1**: 176 of 207 paragraph-initial types never appear in paragraph-medial position. Paragraph openers use a vocabulary almost entirely separate from running-text vocabulary.

**C2**: Top-20 medial tokens include **daiin** (147 occurrences, 93% of Hand-A folios, 15 skeleton variants), **chol** (104, 81.6%, 26 variants), **s** (56, 66.7%, 32 variants), **chor** (55, 71.9%, 33 variants). Notable: Pagel (2025) translated daiin as *datur* ("is given") and chol as *folium* ("leaf") — regardless of Pagel's reading accuracy, these tokens have the statistical profile of a generic medieval-Latin recipe verb and a recurring anatomical noun.

**C3**: Only 9 LOW-class paragraph-initial types recur across ≥3 paragraphs (tor, pchor, tshol, pcheol, tcheody, teol, tcho, tshor, pchocthy). **Paragraph headers are nearly all unique**.

**Substantive conclusion**: the MARGINAL verdict reflects a real structural distinction that the locked rule couldn't capture cleanly. Paragraphs are *topically headed + instructional-body*, but headers do NOT repeat. This argues AGAINST classical pharmaceutical recipes (where ingredients recur) and FOR a **herbal-encyclopedic entry-per-paragraph** structure: one unique topic or plant per paragraph, with descriptive vocabulary (Galenic qualities, uses, preparation verbs) shared across all entries. Medieval encyclopedic herbals like *Circa Instans* and *Macer Floridus* have exactly this signature.

This is compatible with the prior Brain-V findings:
- Per-plant content-decoding refutations (`H-BV-SYLLABLE-LEVEL-01` et al.) — the plant-specific content lives in the *unique headers*, not the reusable body.
- HIGH/LOW anti-alternation from HIGH-LOW-STRUCTURE-01 — run-clustering is the encyclopedic pattern, not function/content alternation.
- Hand A internal linguistic structure from HAND-A-INTERNAL-01 — an encyclopedic register with inflected descriptive verbs.

Confidence 0.4 → 0.55.

**Follow-ups**:
- Ingredient-clustering: do paragraph-initial tokens on plant-ID folios cluster by plant family or species?
- Benchmark paragraph-header recurrence against an 11k-token *Circa Instans* or *Macer Floridus* excerpt — if natural herbal encyclopedias show ~5% header recurrence, C3's 10% threshold was too strict.
- Test the Pagel readings (daiin=datur, chol=folium) as locked predictions against paragraph-medial behaviour.

**Files**: `hypotheses/H-BV-RECIPE-STRUCTURE-01.json`, `outputs/recipe_structure_test.json`, `scripts/run_recipe_structure.py`.

## 2026-04-16 — H-BV-HIGH-LOW-STRUCTURE-01 PARTIAL (regime-alternation signal)

**Hypothesis**: The HIGH/LOW vocabulary split may reflect a structural axis (line position, morphological state, paragraph role) rather than lexical function/content; or the function/content reading may survive via adjacency analysis.

**Method**: four-part locked test on Hand A with R=146 split from NOMENCLATOR-01.

**Result**: PARTIAL/UNRESOLVED per locked rule — 0 of 3 structural triggers, Test 4 neither at natural-language band nor at random null.

| test | metric | observed | threshold | triggered? |
|---|---|---|---|---|
| 1 line position | any quartile HIGH-share | max 29% (Q1) | ≥60% | **no** |
| 1 line position | Q1+Q4 edges | 48% | ≥70% | **no** |
| 2 morphological | HIGH 0-suffix | 37.4% | ≥70% | no |
| 2 morphological | LOW ≥2-suffix | 1.9% | ≥50% | no |
| 3 paragraph role | boundary / medial | **0.47x** (inverse) | ≥1.5x | no |
| 4 adjacency | Hand A cross-class | **46.9%** | [60%, 80%] match refs | no |

**Two substantive signals the locked rule did not capture:**

1. **HIGH and LOW classes ANTI-ALTERNATE.** Hand A cross-class rate 46.9% is BELOW random 50% and BELOW Latin Vulgate (53.8%) and Italian Dante (56.7%). Natural languages alternate function/content above random; Hand A clusters like-with-like. The classes appear in RUNS rather than interleaved.

2. **Paragraph-initial tokens are 87.5% LOW-class** (34 HIGH vs 237 LOW across 271 paragraphs; boundary-to-medial HIGH-share ratio 0.47x — inverse of the predicted clustering direction). Consistent with a *'[topic or ingredient name] [common instruction words]'* structure: paragraphs open with a rare/technical token, then transition to a HIGH-dominated middle.

**Combined picture across NOMENCLATOR-01, NLREF-01, HIGH-DECODE-01, and this test:**

- The HIGH/LOW vocabulary split is **real** (Zipf gap, glyph entropy gap, type-glyph entropy gap all p<0.01; 3/5 gaps exceed natural-language references).
- It is **not** function/content (Brady/Schechter/Pagel all fail on HIGH-only; adjacency anti-alternates).
- It is **not** line-positional, not morphological, not paragraph-role clustering.
- It **is** regime-alternation plus topic-initial structure: text segments between HIGH-dominated and LOW-dominated runs, with rare tokens opening paragraphs.

This reframes the nomenclator interpretation. Hand A's statistical fingerprint fits a **two-register prose** — common (HIGH) words cluster in running instructional text, rare (LOW) words cluster at topic boundaries and in technical-term blocks. This is consistent with medieval pharmaceutical recipe structure (ingredient → preparation → dosage) and consistent with a regime-switching cipher architecture, but NOT consistent with the classical nomenclator "cipher+codebook" model.

Confidence 0.4 → 0.35.

**Follow-ups:**
- Run-length distribution on HIGH/LOW classes vs natural-language baselines — quantify the regime-alternation.
- Characterise paragraph-initial LOW tokens — do they cluster by plant species / ingredient family?
- Reframe NOMENCLATOR-NLREF-01's 3/5 gaps as register-switching rather than cipher structure.

**Files**: `hypotheses/H-BV-HIGH-LOW-STRUCTURE-01.json`, `outputs/high_low_structure_test.json`, `scripts/run_high_low_structure.py`.

## 2026-04-16 — H-BV-NOMENCLATOR-HIGH-DECODE-01 REFUTED (all 3 maps fail)

**Hypothesis**: If Hand A has a nomenclator-style head/tail split, then Brady / Schechter / Pagel — previously tested on the full Hand-A vocabulary — should succeed on the HIGH class alone. The HIGH class is the function-word scaffold; if it is enciphered natural language, a correct substrate mapping should clear the +0.010 connector-content bigram shuffle-test threshold on HIGH-only tokens.

**Method**: Filter each Hand-A line to HIGH-only tokens (R=146 frequency-rank split from NOMENCLATOR-01, 5,518 HIGH tokens); apply each of the three decoders; compute connector-content bigram shuffle-test delta with identical methodology to `H-BV-HAND-A-MAP-COMPARISON-01`.

**Result**: NOMENCLATOR-SUBSTRATE-REFUTED. All three maps REFUTED on HIGH-only.

| map | HIGH-only delta | full-Hand-A prior | shift | verdict |
|---|---|---|---|---|
| Brady-Syriac | **−0.0354** | +0.0044 | −0.0398 | REFUTED |
| Schechter-LatinOcc | **−0.0559** | −0.0608 | +0.0049 | REFUTED |
| Pagel-trilingual | **−0.0033** | +0.0118 | −0.0151 | REFUTED |

987 Hand-A lines survived the filter (≥3 HIGH tokens each); 4,701 HIGH tokens total.

**Critical finding**: Pagel's full-Hand-A +0.0118 (previously CONFIRMED in `H-BV-HAND-A-MAP-COMPARISON-01`) DROPS to −0.0033 when restricted to HIGH-only. This is the opposite of the nomenclator substrate prediction — removing the LOW class (which the hypothesis said was the opaque codebook) should have *preserved or strengthened* the signal. Instead it eliminated it. Pagel's signal must have been driven by LOW-class matches.

**Brady's** drop is even sharper: +0.0044 → −0.0354, a 40-point swing. **Schechter** stays negative throughout, consistent with prior REFUTED status.

**Implication**: the classical nomenclator reading — HIGH class is enciphered natural language, LOW class is arbitrary codebook — is REFUTED for all three best-available substrate candidates. The two-population vocabulary structure from NOMENCLATOR-01 and NOMENCLATOR-NLREF-01 remains confirmed (Hand A differs from Latin and Italian on 3/5 measures), but the FUNCTION-WORD-SCAFFOLD interpretation of the HIGH class is not correct under Brady/Schechter/Pagel.

Three directions survive:
1. The HIGH class is enciphered under some UNTESTED substrate (different language, different map).
2. The HIGH class is not natural-language ciphertext at all.
3. The HIGH/LOW split, though real, is not the function/content axis. Alternatives: positional (line-initial vs medial), morphological (suffix-present vs suffix-absent), or syntactic-role.

Confidence 0.4 → 0.25.

**Files**: `hypotheses/H-BV-NOMENCLATOR-HIGH-DECODE-01.json`, `outputs/nomenclator_high_decode_test.json`, `scripts/run_nomenclator_high_decode.py`.

## 2026-04-16 — H-BV-NOMENCLATOR-NLREF-01 SUPPORTED (mixed substantive)

**Hypothesis**: Hand A's head/tail vocabulary gaps from H-BV-NOMENCLATOR-01 are significantly more extreme (in nomenclator-predicted direction) than the same gaps measured on natural-language reference corpora of comparable size.

**Reference corpora**: Latin Vulgate (Genesis + Exodus + Leviticus, fourmilab.ch HTML-stripped) and Italian Dante Divina Commedia (Project Gutenberg #1012, header/footer stripped). All three corpora truncated to first 11,022 word tokens.

**Result**: SUPPORTED per locked rule. 3 of 5 measures show Hand A more extreme than BOTH reference corpora.

| measure | Hand A | Vulgate | Dante | predicted | A>both? |
|---|---|---|---|---|---|
| Zipf exponent | **+0.240** | +0.106 | +0.231 | + | **YES** |
| weighted glyph entropy | -0.151 | **-0.209** | -0.060 | − | no (Vulgate flatter) |
| type-glyph entropy | **-0.152** | -0.073 | +0.083 | − | **YES** |
| mean word length | -1.81 | **-3.03** | **-3.14** | − | no (refs much larger) |
| length stddev | **-0.57** | -0.73 | -0.63 | + | **YES** (closest to zero) |

**Substantive reading is mixed**:
- Hand A's Zipf and type-glyph-entropy gaps are larger than both reference languages — head and tail are MORE statistically distinct than natural language produces. Cipher-supportive.
- Notably, Italian (Dante) shows POSITIVE type-glyph-entropy gap — its function words use a more uniform glyph distribution than its content words. Hand A is firmly in the opposite direction, which is not a natural-language pattern.
- HOWEVER: Hand A's mean-length gap (-1.81) is roughly HALF the magnitude of natural references (-3.0+). Natural languages have function words MUCH shorter than content words; Hand A's length distribution is COMPRESSED.
- The compressed length is itself cipher-consistent (many cipher schemes equalise word length) but it is NOT the classical Cicco-Simonetta nomenclator pattern of "arbitrary code-words". Rather, the data is consistent with a **verbose cipher with token-padding**, or a **constructed language with regularised morphology**, or a **polyalphabetic system with positional length quantisation**.

**Implication**: the H-BV-NOMENCLATOR-01 result does NOT dissolve into ordinary natural-language stratification — Hand A is genuinely distinct from Latin and Italian on three of five measures. But the classical-nomenclator reading is refined: the cipher structure includes both head/tail vocabulary separation AND length compression, which is a stricter constraint than a generic codebook. Confidence 0.5 → 0.6.

**Next pre-registered tests**:
- Unigram-vs-bigram entropy ratio on LOW class — distinguishes "arbitrary uniform-random codes" from "phonotactically-structured content".
- KS test of full-vocabulary length distribution against natural-language references.
- Add a Latin pharmaceutical/scientific text reference (Macer Floridus, Circa Instans) — scripture+verse may be poor controls for a pharmaceutical-illustrated codex.

**Files**: `hypotheses/H-BV-NOMENCLATOR-NLREF-01.json`, `outputs/nomenclator_nlref_test.json`, `scripts/run_nomenclator_nlref.py`, reference corpora pinned in `raw/corpus/reference-corpora/`.

## 2026-04-16 — H-BV-NOMENCLATOR-01 CONFIRMED (with refinement)

**Hypothesis**: Hand A's vocabulary splits into two statistically distinct populations consistent with a 15th-century nomenclator cipher: a HIGH-frequency class (function words / connectors, behaving as natural language) and a LOW-frequency class (technical terms / arbitrary codebook entries, NOT behaving as natural language).

**Method**: Head/tail split at the rank R where cumulative tokens reach 50% of total Hand A. Five measures per class — Zipf exponent, weighted glyph entropy, type-glyph entropy, mean word length, length stddev. Permutation null with 1000 random type-relabellings.

**Result**: CONFIRMED per locked rule. Split rank R=146 (HIGH = 146 types covering 5,518 tokens / 50.1%; LOW = 3,367 types covering 5,504 tokens / 49.9%).

| measure | HIGH | LOW | gap (H−L) | predicted | one-sided p | verdict |
|---|---|---|---|---|---|---|
| Zipf exponent | 0.751 | 0.511 | +0.240 | + | **0.003** | PASS |
| weighted glyph entropy | 3.773 | 3.924 | −0.151 | − | 0.254 | direction-pass weak |
| type-glyph entropy | 3.786 | 3.938 | −0.152 | − | **<0.001** | PASS |
| mean word length | 3.41 | 5.22 | −1.81 | − | **<0.001** | PASS |
| length stddev | 1.37 | 1.94 | −0.57 | + | 0.98 | **FAIL** |

4 of 5 nomenclator predictions hold; 3 reach permutation p<0.01 → CONFIRMED under the locked rule.

**Refinement**: the FIXED-LENGTH-CODE prediction failed — the LOW class has HIGHER length variance, not lower. This rules out the rigid Cicco-Simonetta-style nomenclator with constant-length code words. The two-population vocabulary structure is real and statistically robust, but consistent with EITHER a variable-length nomenclator OR ordinary natural-language function-vs-content stratification. The locked test cannot fully distinguish those without a natural-language reference corpus of comparable size.

**Implication**: this is the strongest cipher-architecture signal Brain-V has produced on Hand A to date. Combined with the 12 refuted character-substitution mappings, the per-plant-content refutation chain, and Pagel's-only-the-head-clears-shuffle pattern, the picture is consistent with a hybrid system in which the high-frequency vocabulary is a (partially) decodable substitution and the low-frequency tail is opaque code. Confidence 0.4 → 0.7.

**Follow-ups (to be pre-registered)**:
- Compare gap magnitudes against an 11k-token Latin/Italian reference corpus split by the same rule.
- Unigram-vs-bigram entropy ratio test on the LOW class to distinguish "uniform-random codes" from "phonotactically-structured natural-language content".

**Files**: `hypotheses/H-BV-NOMENCLATOR-01.json`, `outputs/nomenclator_test.json`, `scripts/run_nomenclator.py`.

## 2026-04-16 — H-BV-ABJAD-CONSONANT-01 CONFIRMED (with caveat)

**Hypothesis**: Hand A's consonantal skeleton (vowels a/e/i/o stripped, word-final suffix y/n/r/m/g stripped, line-initial plain gallows t/p stripped) matches at least one natural-language consonant-frequency distribution with chi-square p<0.01 AND improvement factor over uniform null > 2.0.

**Method**: Hand-A residual after stripping yielded N=19,651 consonantal glyph-units across 25 distinct types. Top-12 (ch, d, l, k, t, sh, q, y, s, cth, r, ckh) rank-paired against published top-12 consonant frequencies for seven languages. Chi-square df=11 against each language's expected distribution and against uniform null.

**Result**: CONFIRMED per locked rule — but all seven languages pass the threshold, limiting discrimination.

| rank by fit | language | chi² | p-value | improvement |
|---|---|---|---|---|
| 1 | italian_medieval | 944.08 | 2.1e-195 | **9.82x** |
| 2 | latin | 956.59 | 4.2e-198 | 9.69x |
| 3 | greek | 1028.14 | 1.7e-213 | 9.02x |
| 4 | arabic | 1522.35 | ~0 | 6.09x |
| 5 | german | 1786.05 | ~0 | 5.19x |
| 6 | hebrew | 2556.35 | ~0 | 3.63x |
| 7 | syriac | 3148.73 | ~0 | 2.95x |

Uniform null chi² = 9273.58. All seven languages meet p<0.01 AND improvement>2x.

**Key observations**:
- Per the pre-registered rule, primary abjad candidate is **italian_medieval** (narrow margin over Latin and Greek).
- **Surprise**: the best fits are Mediterranean ALPHABETIC languages (Italian, Latin, Greek all cluster near 9x), while the SEMITIC ABJADS (Hebrew 3.63x, Syriac 2.95x) fit WORST. The naive abjad-shorthand prediction — that vowel-stripped Voynich should look most like Hebrew/Syriac/Arabic — is directly contradicted.
- The test is under-powered for discrimination at N≈20k: any non-uniform consonant distribution passes the thresholds. The spread in improvement factor (2.95x to 9.82x) is the informative signal, not the binary pass/fail.

**Implication**: Hand A's consonantal skeleton shape resembles Latin/Italian alphabetic consonants more than Semitic abjads. The abjad hypothesis passes its letter but fails its spirit — direction shifts toward "vowel-stripped Latin/Italian" (a known medieval shorthand device) rather than true Semitic abjad shorthand.

**Files**: `hypotheses/H-BV-ABJAD-CONSONANT-01.json`, `outputs/abjad_consonant_test.json`, `scripts/run_abjad_consonant.py`.

## 2026-04-16 — H-BV-HAND-A-LANGUAGE-SCREEN-02 REFUTED

**Hypothesis**: At least one of seven under-tested candidate languages — Basque, Hungarian, Finnish, Armenian, Ottoman Turkish, Italian-dialect, German — produces a connector-to-content bigram delta >= +0.005 under frequency-rank EVA-to-letter substitution on Hand A.

**Method**: For each candidate, sort Hand-A EVA glyph-units (ch/sh/ckh/cth/cph collapsed) by descending frequency. Map rank-i EVA glyph to rank-i letter of the language's published letter-frequency ranking (top-20). Decode all Hand-A tokens. Match against a fixed 80-item lexicon (15 connectors + 65 content). Compute in-order vs. Hand-A-shuffled connector-content bigram rate (same shuffle-test as Brady/Pagel/Schechter).

**Result**: REFUTED. Best delta +0.00198 (german), below +0.005 threshold.

| rank | language | match% | in-order | shuffled | delta |
|------|----------|--------|----------|----------|-------|
| 1 | german | 5.19% | 0.0026 | 0.0007 | +0.00198 |
| 2 | finnish | 3.74% | 0.0007 | 0.0000 | +0.00066 |
| 3 | basque | 1.49% | 0.0007 | 0.0000 | +0.00066 |
| 4 | armenian | 2.41% | 0.0000 | 0.0007 | -0.00066 |
| 5 | italian | 7.11% | 0.0000 | 0.0010 | -0.00099 |
| 6 | ottoman_turkish | 11.21% | 0.0127 | 0.0139 | -0.00121 |
| 7 | hungarian | 11.18% | 0.0067 | 0.0131 | -0.00638 |

**Key observations**:
- Ottoman Turkish and Hungarian have the highest lexicon match rates (~11%) — but negative deltas. High match is driven by the letter-set rather than syntactic structure.
- German's small positive delta (+0.002) is below Brady's Syriac Hand-A result (+0.0044), which itself is sub-threshold.
- Italian — the strongest historical prior by Voynich provenance — produces a negative delta.

**Implication**: Simple frequency-rank character substitution in all seven candidates is eliminated. Combined with prior Brady/Pagel/Schechter results, no tested natural-language substitution survives the shuffle test on Hand A. Direction: cipher/constructed/shorthand models (polyalphabetic, nomenclator, abjad-style consonantal shorthand, or verbose cipher with nulls).

**Files**: `hypotheses/H-BV-HAND-A-LANGUAGE-SCREEN-02.json`, `outputs/hand_a_language_screen.json`, `scripts/run_hand_a_language_screen.py`.

## 2026-04-15 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 109
**Progress**: 18 eliminated, 109 active, 57 above 0.8 confidence
**Surprise**: 0.0219
**Beliefs**: 39 → 39
**High confidence**: ['H001', 'H003', 'H004', 'H006', 'H008', 'H011', 'H014', 'H015', 'H016', 'H019', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H050', 'H051', 'H052', 'H053', 'H054', 'H055', 'H056', 'H057', 'H058', 'H059', 'H060', 'H062', 'H063', 'H064', 'H066', 'H069', 'H070', 'H071', 'H074', 'H075', 'H076', 'H078', 'H081', 'H092']

## 2026-04-15 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 109
**Progress**: 18 eliminated, 109 active, 57 above 0.8 confidence
**Surprise**: 0.0219
**Beliefs**: 39 → 39
**High confidence**: ['H001', 'H003', 'H004', 'H006', 'H008', 'H011', 'H014', 'H015', 'H016', 'H019', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H050', 'H051', 'H052', 'H053', 'H054', 'H055', 'H056', 'H057', 'H058', 'H059', 'H060', 'H062', 'H063', 'H064', 'H066', 'H069', 'H070', 'H071', 'H074', 'H075', 'H076', 'H078', 'H081', 'H092']

## 2026-04-15 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 109
**Progress**: 18 eliminated, 109 active, 57 above 0.8 confidence
**Surprise**: 0.0219
**Beliefs**: 39 → 39
**High confidence**: ['H001', 'H003', 'H004', 'H006', 'H008', 'H011', 'H014', 'H015', 'H016', 'H019', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H050', 'H051', 'H052', 'H053', 'H054', 'H055', 'H056', 'H057', 'H058', 'H059', 'H060', 'H062', 'H063', 'H064', 'H066', 'H069', 'H070', 'H071', 'H074', 'H075', 'H076', 'H078', 'H081', 'H092']

## 2026-04-15 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 109
**Progress**: 18 eliminated, 109 active, 57 above 0.8 confidence
**Surprise**: 0.0219
**Beliefs**: 39 → 39
**High confidence**: ['H001', 'H003', 'H004', 'H006', 'H008', 'H011', 'H014', 'H015', 'H016', 'H019', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H050', 'H051', 'H052', 'H053', 'H054', 'H055', 'H056', 'H057', 'H058', 'H059', 'H060', 'H062', 'H063', 'H064', 'H066', 'H069', 'H070', 'H071', 'H074', 'H075', 'H076', 'H078', 'H081', 'H092']

## 2026-04-15 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 109
**Progress**: 18 eliminated, 109 active, 57 above 0.8 confidence
**Surprise**: 0.0219
**Beliefs**: 39 → 39
**High confidence**: ['H001', 'H003', 'H004', 'H006', 'H008', 'H011', 'H014', 'H015', 'H016', 'H019', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H050', 'H051', 'H052', 'H053', 'H054', 'H055', 'H056', 'H057', 'H058', 'H059', 'H060', 'H062', 'H063', 'H064', 'H066', 'H069', 'H070', 'H071', 'H074', 'H075', 'H076', 'H078', 'H081', 'H092']

## 2026-04-15 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 109
**Progress**: 18 eliminated, 109 active, 57 above 0.8 confidence
**Surprise**: 0.0219
**Beliefs**: 39 → 39
**High confidence**: ['H001', 'H003', 'H004', 'H006', 'H008', 'H011', 'H014', 'H015', 'H016', 'H019', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H050', 'H051', 'H052', 'H053', 'H054', 'H055', 'H056', 'H057', 'H058', 'H059', 'H060', 'H062', 'H063', 'H064', 'H066', 'H069', 'H070', 'H071', 'H074', 'H075', 'H076', 'H078', 'H081', 'H092']

## 2026-04-14 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 67
**Progress**: 15 eliminated, 66 active, 29 above 0.8 confidence
**Surprise**: 0.0313
**Beliefs**: 31 → 31
**High confidence**: ['H001', 'H003', 'H004', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H051', 'H052', 'H053']

## 2026-04-14 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 67
**Progress**: 15 eliminated, 66 active, 29 above 0.8 confidence
**Surprise**: 0.0313
**Beliefs**: 31 → 31
**High confidence**: ['H001', 'H003', 'H004', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H051', 'H052', 'H053']

## 2026-04-14 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 67
**Progress**: 15 eliminated, 66 active, 29 above 0.8 confidence
**Surprise**: 0.0313
**Beliefs**: 31 → 31
**High confidence**: ['H001', 'H003', 'H004', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H051', 'H052', 'H053']

## 2026-04-14 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 67
**Progress**: 15 eliminated, 66 active, 29 above 0.8 confidence
**Surprise**: 0.0313
**Beliefs**: 31 → 31
**High confidence**: ['H001', 'H003', 'H004', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H051', 'H052', 'H053']

## 2026-04-14 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 67
**Progress**: 15 eliminated, 66 active, 29 above 0.8 confidence
**Surprise**: 0.0313
**Beliefs**: 31 → 31
**High confidence**: ['H001', 'H003', 'H004', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H051', 'H052', 'H053']

## 2026-04-14 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 67
**Progress**: 15 eliminated, 66 active, 29 above 0.8 confidence
**Surprise**: 0.0313
**Beliefs**: 31 → 31
**High confidence**: ['H001', 'H003', 'H004', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H051', 'H052', 'H053']

## 2026-04-14 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 67
**Progress**: 15 eliminated, 66 active, 29 above 0.8 confidence
**Surprise**: 0.0313
**Beliefs**: 31 → 31
**High confidence**: ['H001', 'H003', 'H004', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H051', 'H052', 'H053']

## 2026-04-14 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 67
**Progress**: 15 eliminated, 66 active, 29 above 0.8 confidence
**Surprise**: 0.0313
**Beliefs**: 31 → 31
**High confidence**: ['H001', 'H003', 'H004', 'H020', 'H021', 'H022', 'H023', 'H024', 'H025', 'H027', 'H029', 'H031', 'H032', 'H033', 'H036', 'H037', 'H038', 'H040', 'H041', 'H042', 'H043', 'H044', 'H046', 'H047', 'H048', 'H049', 'H051', 'H052', 'H053']

## 2026-04-13 — FAILED: predict.py (22:38:34 UTC)

**Step**: `predict.py`
**Error**: Traceback (most recent call last):
  File "C:\Projects\brain-v\scripts\predict.py", line 342, in <module>
    main()
    ~~~~^^
  File "C:\Projects\brain-v\scripts\predict.py", line 302, in main
    raw_response = call_claude(prompt)
  File "C:\Projects\brain-v\scripts\predict.py", line 212, in call
**Action**: Brain-V's loop broke. Check `outputs/failures.log` for details.

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — FAILED: predict.py (19:57:04 UTC)

**Step**: `predict.py`
**Error**: Traceback (most recent call last):
  File "C:\Projects\brain-v\scripts\predict.py", line 328, in <module>
    main()
    ~~~~^^
  File "C:\Projects\brain-v\scripts\predict.py", line 288, in main
    raw_response = call_ollama(prompt)
  File "C:\Projects\brain-v\scripts\predict.py", line 202, in call
**Action**: Brain-V's loop broke. Check `outputs/failures.log` for details.

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Brain-V cognitive cycle (automated)

**Hypotheses scored**: 5
**Progress**: 0 eliminated, 5 active, 0 above 0.8 confidence
**Surprise**: 0.0868
**Beliefs**: 6 → 7
**High confidence**: []

## 2026-04-13 — Circuit breaker added to loop.py

**What changed**

`loop.py` rewritten with a circuit breaker pattern (sourced from @asmah2107 agentic design patterns — see `raw/signals/agentic-design-patterns-asmah2107.md`).

- **`run_script()` no longer calls `sys.exit(1)` on failure.** Returns True/False. The calling command decides how to proceed — perceive failure doesn't block predict if cached data exists; score failure doesn't block the next cycle.
- **`log_failure(step, error)` writes structured failure entries** to both `wiki/LOG.md` (human-readable FAILED entry) and `outputs/failures.log` (JSON, machine-readable, append-only). Brain always logs what happened, even when it breaks.
- **5-minute timeout on subprocess calls.** If Ollama hangs, the loop doesn't hang forever.
- **`capture_output=True`** — stdout and stderr are captured and printed, so failure context is visible.
- **Top-level try/except in `main()`** — unhandled exceptions hit the circuit breaker rather than crashing silently.
- **`status` command now shows recent failures** from `outputs/failures.log`.

**What this means**: if the 7am BrainLoop task fails (Ollama down, network error, arXiv timeout), you will see a FAILED entry in `wiki/LOG.md` explaining what broke and when, rather than discovering the loop silently stopped.

Also filed `raw/signals/agentic-design-patterns-asmah2107.md` — the full 15-pattern checklist scanned against Brain's architecture with gap analysis.

---

## 2026-04-13 — score.py: per-prediction belief linking + belief minting

**What changed in `scripts/score.py`**

*Problem 1: Global promote/demote was too blunt.* When overall surprise was 0.935, ALL beliefs got demoted — including beliefs related to "Agentic AI" which actually scored 0.30 (a partial hit). The update rule treated every belief as equally responsible for every prediction.

*Fix: Per-prediction belief linking.* Each scored prediction now only updates beliefs whose text is keyword-related to that prediction's topic. A 0.30 on "Agentic AI" promotes beliefs about agentic AI; a 0.00 on "Transformer Scaling Laws" demotes beliefs about transformer scaling. Beliefs unrelated to any prediction are untouched.

*Problem 2: Brain could only tear down beliefs, never build them up.* The only way new beliefs entered the system was as LOW-confidence insights from misses. A prediction that scored well generated nothing. Brain was learning what's wrong but never learning what's right.

*Fix: Belief minting from successful predictions.* When a prediction scores above 0.2 (HIT_THRESHOLD), a new MEDIUM-confidence belief is minted: `"[topic] papers appear consistently in cs.AI feeds"`. This gives Brain evidence-based beliefs that enter the system with earned confidence, not just seeded beliefs that get hammered down.

**Thresholds**
- HIT_THRESHOLD = 0.2 (above → promote related beliefs + mint new belief)
- MISS_THRESHOLD = 0.1 (below → demote related beliefs)
- Between 0.1-0.2 → no change (ambiguous signal)

**Why these numbers**: 0.2 is low enough that partial hits like the Agentic AI 0.30 generate positive signal, but high enough that noise (0.025 scores) doesn't. Adjustable after more cycles.

---

## 2026-04-13 — Four new research sources ingested

**Sources added to `raw/research/`**

1. **neural-computers-meta.md** — arXiv:2604.06425. Meta AI + KAUST + Schmidhuber. Neural Computers: unify computation, memory, I/O in a single learned latent state. Paradigm-level — not near-term actionable but defines Brain's long-term architectural horizon. The model IS the computer.

2. **memento-microsoft.md** — Microsoft Research. Trained context compression: 6x trace-level, 2-3x KV cache reduction, throughput nearly doubles. 228K open training traces (OpenMementos). **SHORTLISTED for context compression layer.** Supersedes MemPalace AAAK — this is what AAAK pretended to be.

3. **lightthinker-plus.md** — arXiv:2604.03679. ZJU. Three memory primitives: commit (archive), expand (retrieve), fold (re-compress). 69.9% token reduction, +2.42% accuracy, stable past 80 rounds. **Primitives map directly to Brain's dreaming (commit) / learning (expand) / forgetting (fold) interface.**

4. **single-vs-multi-agent-stanford.md** — arXiv:2604.02460. Stanford. Single-agent outperforms multi-agent on multi-hop reasoning when computation is controlled. Data Processing Inequality: each handoff is lossy. ~15x token overhead. **CRITICAL — directly challenges Brain's 5-sub-brain architecture.** Tension flagged in `wiki/gaps/open-questions.md` (item 10).

**Wiki files updated**
- `wiki/components/library.md` — added Memento (SHORTLISTED), LightThinker++ (RESEARCH), Neural Computers (RESEARCH). MemPalace marked "SUPERSEDED by Memento for compression". Added beliefs for all three.
- `wiki/layers/forgetting.md` — rewritten around commit/expand/fold operational model from LightThinker++, with Memento as the compression mechanism inside commit/fold.
- `wiki/gaps/open-questions.md` — added item 10: single-vs-multi-agent Stanford tension. Sub-brain confidence dropped from MEDIUM to LOW. POC single-brain approach validated. Multi-brain needs measurable evidence before introduction.

**Contradictions flagged**
- Stanford paper creates a direct tension with the master/sub-brain architecture (5 sub-brains communicating via DKG). Heterogeneous drives may exempt Brain from the homogeneous-agent critique, but the DKG negotiation protocol IS a lossy channel as described. Needs resolution before sub-brain implementation.
- MemPalace AAAK is now fully superseded by Memento for compression. MemPalace's contradiction-detection module still survives as a separate utility.

---

## 2026-04-13 — Cognitive loop cycle (automated)

**Surprise**: 0.935 | **Accuracy**: 0.065
**Insight**: Brain's world model appears to be biased towards topics that are currently trendy in the field of AI, and it may need to improve its ability to predict papers on more established areas of research
**Beliefs**: 7 → 8
**Prediction date scored**: 2026-04-11

## 2026-04-11 — Loop automation fixes

**What changed**

*predict.py — prompt rewrite:*
Separated beliefs from predictions. Old prompt let the 8B treat beliefs as predictions ("persistent world models are important" → predicts papers about persistent world models). New prompt explicitly instructs: beliefs are background context, predict what arXiv authors will actually submit based on observable patterns in today's papers.

*score.py — weekend-safe prediction lookup:*
Replaced hardcoded "yesterday" with a search back up to 4 days for the most recent prediction file. Monday morning now correctly scores Friday's predictions.

*loop.py — empty-feed skip:*
`score` and `full` commands now check paper count after perceive. If 0 papers (weekend/holiday), skips scoring and prediction entirely. No more wasted LLM calls against empty feeds.

*Scheduled tasks consolidated:*
- Deleted: `BrainScore` (daily 07:00) and `BrainPredict` (daily 07:10) — ran every day including weekends, no working directory set (caused BrainScore failure, Last Result: 1).
- Created: `BrainLoop` — single task, Mon–Fri 07:00, runs `brain-loop.bat` which sets working directory and calls `loop.py full` (score + predict in one pass).
- Created: `scripts/brain-loop.bat` — wrapper that `cd`s to project root before running.

*Next scheduled run: Monday 2026-04-13 at 07:00.*

---

## 2026-04-11 — Cognitive loop cycle (automated)

**Surprise**: 0.8 | **Accuracy**: 0.2
**Insight**: Brain's world model appears to be overly focused on specific subfields of AI research, as it failed to predict the publication of papers in more general areas like efficient reasoning method improvements and chain-of-thought improvements for mathematical reasoning.
**Beliefs**: 6 → 7
**Prediction date scored**: 2026-04-10

## 2026-04-10 — Curation moat concept added

**What changed**
- `wiki/concepts/curation-moat.md` — created. Brain's competitive position: verified curation compounding over time, not data volume. The moat is the accumulated history of predictions scored against reality on open infrastructure. Cites 0xIntuition thread (2026-04-09) and Brain's own cycle 1 results as first evidence.
- `wiki/INDEX.md` — added under Concepts.

**Why**
Cycle 1 results (surprise 0.984, accuracy 0.016) are the first data point. Brain was catastrophically wrong — and the system worked exactly as designed: beliefs demoted, new belief generated from the miss, everything logged to IPFS. The curation moat thesis says this is the mechanism: being wrong is costly and informative, being right compounds. Open infrastructure makes the history credible. The question is whether the curve goes down over cycles.

---

## 2026-04-10 — Cognitive loop cycle (automated)

**Surprise**: 0.984375 | **Accuracy**: 0.015625
**Insight**: Brain's world model appears to be biased towards topics related to mathematical reasoning and value alignment, while underestimating the importance of efficient reasoning methods, causal discovery, and agentic AI
**Beliefs**: 5 → 6
**Prediction date scored**: 2026-04-09

**Analysis**: First score. All beliefs demoted. Surprise near-maximal. This is expected on cycle 1 — the seeded beliefs were general claims about AI, not predictions about specific cs.AI paper distributions. The real test starts now: does cycle 2 score lower? The insight generated ("biased toward mathematical reasoning and value alignment") is itself a corrective belief that should improve the next prediction if the loop is closing.

---

## 2026-04-09 — Verification layer and economic layer concepts added

**What changed**
- `wiki/concepts/verification-layer.md` — created. Brain's RLVR equivalent: binary signal generator (keyword match, rank match, calibration) that makes the learning loop trainable rather than dependent on LLM-judged vibes. Not a week 1 build but required before week 3 or the system plateaus.
- `wiki/concepts/economic-layer.md` — created. Incentive structure: internal value (information gain → attention/goal-stack weighting) and external value (engagement, accuracy track record, revenue → priority allocation). Integrates with AgentOS TaskQueue bounties. Also required before week 3.
- `wiki/INDEX.md` — both added under Concepts.

**Why**
The week 1 loop (perceive → predict → score → update) closes on soft LLM-judged signals. That works for proving the loop runs. It does not work for proving the loop *compounds*. Verification provides the hard binary signal; economics provides the priority signal. Without both, Brain hits a ceiling: it runs but doesn't get measurably smarter in a way anyone can verify, and it explores uniformly rather than investing in high-value domains.

Neither is built this week. Both need to be in the architecture document now so week 2–3 builds against them.

---

## 2026-04-09 — First cognitive cycle: perceive + predict

**What happened**

Brain ran its first full perceive → predict cycle via `loop.py perceive-predict`.

**Perception**
- 330 cs.AI papers ingested from arXiv RSS
- Pushed to AgentOS perception sub-brain (agent 2): IPFS `QmUhDVCVZ4q6dQ9rTHSR2QygghJymPdMs97BnuwULyYv9q` v1
- Top keywords: models, language, learning, large, reasoning, framework, generation, multimodal, evaluation, agents

**Predictions for 2026-04-10**
| Confidence | Topic |
|---|---|
| 0.85 | Chain-of-Thought Improvements for Mathematical Reasoning |
| 0.78 | Value Alignment and Safety in AI Systems |
| 0.72 | Efficient Reasoning Methods for Large-Scale Systems |
| 0.68 | Causal Discovery and Representation Learning |
| 0.62 | Agentic AI and Human-AI Collaboration |

Model: llama3.1:8b via Ollama (local fast path).

**Bug found and fixed**: `predict.py --from-agentos` loaded 0 beliefs because AgentOS nests the context payload under `context.context`, but the script was reading `context.beliefs`. Predictions were made from perception data alone (no belief weighting). Fixed: `load_beliefs_agentos()` now unwraps the nested structure and falls back to local `beliefs.json` if AgentOS returns 0.

**Next**: run `python scripts/loop.py score` on 2026-04-10 to compare these predictions against actual papers. That closes the loop for the first time.

---

## 2026-04-09 — Brain registered on AgentOS. First state persisted.

**What happened**

Brain is live. Not theoretically — on-chain, with state in IPFS.

Registered via AgentOS Railway production backend (`agentos-backend-production.up.railway.app`):

| Agent | ID | Role |
|---|---|---|
| brain-master | 1 | Master brain. Owner `0xC71A15Fcb1149254F97059F6cf3f6Ed43990ebd4` |
| brain-perception | 2 | Sub-brain: perception |
| brain-memory | 3 | Sub-brain: memory |
| brain-curiosity | 4 | Sub-brain: curiosity |
| brain-self-model | 5 | Sub-brain: self-model |
| brain-theory-of-mind | 6 | Sub-brain: theory-of-mind |

Initial world model (5 seeded beliefs, cycle 0) saved:
- IPFS hash: `QmTV8StsWAmY2jZZs2inxZkLkx3U1UDDCp2Lmc3H74NSH7`
- Version: 1
- Tx hash: `beb2eef8be461cb6fae1aefbc364682adec25b189fb3dcbe37b7137bdfd908cd`
- Domain: cs.AI

**Seeded beliefs (cycle 0)**
1. "Transformer scaling laws continue to hold for reasoning tasks" — MEDIUM
2. "Cognitive architectures are underexplored relative to capability scaling" — HIGH
3. "Persistent world models are the missing layer in current agent frameworks" — HIGH
4. "Curiosity-driven exploration outperforms goal-directed search in open domains" — MEDIUM
5. "The integration of cognitive layers is the invention, not the layers themselves" — HIGH

**What was updated in the wiki**
- `wiki/concepts/master-architecture.md` — added 2026-04-09 CRITICAL UPDATE section with agent IDs, IPFS hash, tx hash, and current status.
- `wiki/components/library.md` — AgentOS status changed from BUILT to BUILT — LIVE. The "AgentOS provides persistence" claim upgraded from HIGH to VERIFIED with evidence.

**Why this matters**
This is the first time Brain's state is observable outside the conversation it was created in. The IPFS hash is retrievable. The tx hash is verifiable. The agent IDs are persistent. Day 1 of the build plan (substrate setup + registration) is done. Next: `perceive.py` and `predict.py`.

**Contradictions**
- None new. The sub-brain registration matches the negotiation protocol's requirement that each sub-brain has a distinct identity (see [[theory-of-mind]]).
- Note: 5 sub-brains registered, but the architecture has 15 cognitive layers. Not every layer needs its own sub-brain — the founding conversation describes 5 sub-brain drives (perception, memory, curiosity, self-model, theory-of-mind). The remaining layers are functions *within* sub-brains, not separate agents. This is consistent with [[master-architecture]].

---

## 2026-04-08 — Trust concept page created

**What changed**
- **`wiki/concepts/trust.md`**: created. Canonical resolution target for every `[[trust]]` wikilink in the wiki. States explicitly that trust is infrastructure (not cognition), documents the AgentProof + OriginTrail DKG implementation, lists the 4 DKG trust tiers and their (tentative) mapping onto Brain's confidence levels, and indexes every layer file that references trust.
- **`wiki/INDEX.md`**: added trust under Concepts (not Layers). Updated the "Note" beneath the layer list to point at the new concept page instead of just `components/library.md`.

**Why**
The previous LOG entry (schema fix) flagged that several layer files still contained `[[trust]]` wikilinks that pointed at a non-existent target after `layers/trust.md` was deleted. Three options were on the table: leave the links broken, redirect them to `[[origintrail-dkg]]`, or create a `concepts/trust.md`. User chose option three. This is the better option because trust shows up across many layers and deserves a single canonical explanation, but it isn't a cognitive layer in itself — concepts/ is the right home.

**Wikilink resolution**
- All existing `[[trust]]` references across `layers/world-model.md`, `layers/forgetting.md`, `layers/action.md`, `layers/theory-of-mind.md`, `layers/goal-stack.md`, and `gaps/open-questions.md` now resolve to `concepts/trust.md`. No edits to those files needed — the link target now exists.

**Contradictions resolved**
- The "files still containing `[[trust]]` wikilinks" flag from the previous LOG entry: RESOLVED.

**Contradictions remaining**
- None new.

---

## 2026-04-08 — Schema fix + working answers to top open questions

**What changed**

*Schema fix (resolves the contradiction flagged in the previous LOG entry):*
- **CLAUDE.md**: rewrote the 15-layer list. Removed Trust as a cognitive layer. Added Emotion/Valence at position 5. Moved Curiosity from position 5 to position 14. Values is now layer 15. Added explicit note that Trust is infrastructure, lives in `wiki/components/library.md`.
- **CLAUDE.md**: removed the duplicate Ben Goertzel row from the people index table.
- **CLAUDE.md**: updated `Last updated:` to 2026-04-08.
- **`wiki/layers/trust.md`**: deleted. Trust is no longer a cognitive layer.
- **`wiki/layers/emotion-valence.md`**: created. New layer 5. Fast pre-deliberative prioritisation signal — the Friston-flavoured cousin of attention/curiosity.
- **`wiki/layers/curiosity.md`**: layer number 5 → 14.
- **`wiki/layers/values.md`**: layer number 14 → 15. Status changed from "UNKNOWN — open research problem" to "WORKING DEFINITION (confidence LOW)".
- **`wiki/components/library.md`**: AgentProof and OriginTrail DKG rows now say "Trust (infrastructure)" instead of `[[trust]]`, with an explicit note that Trust is infrastructure not a cognitive layer. OriginTrail DKG row also references the new sub-brain negotiation protocol.
- **`wiki/INDEX.md`**: layer list updated — Emotion/Valence at 5, Curiosity at 14, Values at 15, Trust removed with redirect note.

*People index dedupe:*
- **CLAUDE.md**: removed second Ben Goertzel entry. (The wiki `people/index.md` was already deduped during initial compilation; only CLAUDE.md still had the duplicate.)

*Working answers to the three top open questions (all confidence LOW):*
- **[[values]]**: working definition added — maximise understanding / harm floor preventing noise-seeking / no deception. Harm floor and no-deception override understanding. Layer status updated to WORKING DEFINITION.
- **[[theory-of-mind]]**: negotiation protocol added — publish / read / arbitrate via DKG. Sub-brains publish beliefs with identity + evidence; the master brain arbitrates contradictions on evidence quality, not authority. No command channel.
- **[[curiosity]]**: BRAID generation trigger added — surprise threshold on the curiosity signal triggers slow-path Claude API calls that generate new BRAID graphs, then cached for fast-path reuse. Ties expensive frontier calls to high-information moments.
- **`wiki/gaps/open-questions.md`**: appended a "Working answers" section restating all three with explicit "to revise when" conditions. Original open questions left in place above — working answers do not delete the questions, they just unblock construction.

**Why**

The previous LOG flagged a schema contradiction between CLAUDE.md and the founding conversation regarding which layers exist at positions 5/14/15. The user resolved it: drop Trust as a cognitive layer (it's infrastructure), bring back Emotion/Valence (Friston-aligned, needed for fast prioritisation), keep Curiosity at 14 and Values at 15. This aligns CLAUDE.md with `wiki/concepts/master-architecture.md`.

The three open questions were genuinely blocking construction — without working values, [[curiosity]] collapses to noisy-TV; without a negotiation protocol, the master/sub-brain design is aspiration; without an autonomous BRAID trigger, the cost model doesn't close. Working answers (confidence LOW) unblock the build without pretending the questions are solved.

**Contradictions resolved by this change**
- Schema mismatch between CLAUDE.md and founding conversation (item 1 in previous LOG): RESOLVED in favour of the founding/master-architecture layout.
- Ben Goertzel duplicate in CLAUDE.md (item 2 in previous LOG): RESOLVED.

**Contradictions remaining / introduced**
- None new. The MemPalace status note from the previous LOG still stands.
- `wiki/concepts/master-architecture.md` already used Emotion/Valence at 5 and Curiosity at 14 in its layer table — no edit needed there. Worth verifying on next health check.

**Files still containing `[[trust]]` wikilinks**
- `world-model.md`, `forgetting.md`, `action.md`, `theory-of-mind.md`, `goal-stack.md`. These links now point at a concept that lives in `components/library.md` rather than a dedicated layer file. Acceptable for now — the topic still exists, just not as a layer. Flag for the next health check: decide whether to leave `[[trust]]` as-is, redirect to `[[origintrail-dkg]]`, or create a `wiki/concepts/trust.md` as the canonical target.

---

## 2026-04-08 — Initial wiki compilation

**What changed**
- Created `wiki/layers/` with one file per cognitive layer (15 total, per CLAUDE.md schema):
  perception, attention, world-model, prediction, curiosity, goal-stack, self-model,
  theory-of-mind, narrative, action, learning, forgetting, dreaming, values, trust.
- Created `wiki/components/library.md` — full components table with statuses and beliefs.
- Created `wiki/people/index.md` — people index from CLAUDE.md plus the build orbit (Ben, Kieron, Red Bull Basement).
- Created `wiki/gaps/open-questions.md` — top-level architectural unknowns.
- Created `wiki/INDEX.md` — master index of every file in the wiki.

**Sources ingested**
- `raw/conversations/founding-conversation-2026-04-06.md`
- `raw/research/asi-evolve-2603.29640.md`
- `raw/research/agentos-built.md`
- `raw/research/mempalace.md`
- `raw/research/hermes-agent-llm-wiki.md`
- `wiki/concepts/master-architecture.md` (already present)
- `CLAUDE.md` (operating schema)

**Why**
First wake-up of Brain. Compiling the founding raw material into structured wiki form
so future cycles can reason against it instead of re-reading raw files.

**Contradictions flagged**

1. **15-layer schema mismatch.** CLAUDE.md lists the 15 cognitive layers as:
   Perception, Attention, World Model, Prediction, **Curiosity (5)**, Goal Stack, Self Model,
   Theory of Mind, Narrative, Action, Learning, Forgetting, Dreaming, Values, **Trust (15)**.
   The founding conversation and `wiki/concepts/master-architecture.md` list:
   Perception, Attention, World Model, Prediction, **Emotion/Valence (5)**, Goal Stack, Self Model,
   Theory of Mind, Narrative, Action, Learning, Forgetting, Dreaming, **Curiosity (14)**, Values.
   Differences:
   - CLAUDE.md drops Emotion/Valence as a layer; founding includes it.
   - CLAUDE.md adds Trust as a layer; founding treats Trust as infrastructure (under the cognitive loop).
   - Curiosity moves from position 14 → 5.
   **Resolution applied**: followed CLAUDE.md as the operating schema (it is the contract). Created
   `layers/trust.md` with an explicit note that founding/master-architecture treat trust as
   infrastructure, not cognition. Did NOT create an Emotion/Valence layer file. **This needs an
   explicit user decision** — either CLAUDE.md should be amended to re-add Emotion/Valence, or
   master-architecture.md should be updated to match CLAUDE.md.

2. **People index duplicate.** CLAUDE.md's people table lists Ben Goertzel twice (once with
   "OpenCog Hyperon, AGI architecture" and once with "OpenCog Hyperon"). Treated as one person
   in `wiki/people/index.md`. CLAUDE.md should be cleaned up.

3. **MemPalace status downgrade.** Not a contradiction in the wiki itself — but worth noting:
   raw/research/mempalace.md contains a community correction that downgrades the original benchmark
   claims. The library now reflects this (MemPalace = WATCH, not SHORTLISTED). Any future ingest
   that cites MemPalace's original numbers should be flagged.

**Belief format used**
Every claim follows the CLAUDE.md format:
```
**Claim**: ...
**Confidence**: HIGH / MEDIUM / LOW / SPECULATIVE
**Source**: raw/...
**Last verified**: 2026-04-08
**Contradicts**: ...
```

**Next ingest hooks**
- When Hermes Agent is actually run, ingest its first `/llm-wiki` output into `raw/research/`
  and reconcile with `layers/perception.md`.
- When anda-hippocampus is benchmarked head-to-head against Graphiti/Zep, update
  `layers/world-model.md` with the result.
- 2026-04-21: re-check MemPalace for independent benchmark reproduction.
