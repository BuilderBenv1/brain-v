# Brain-V v2 — Bowern & Lindemann Framework Audit

**Date:** 2026-04-17
**Purpose:** Re-audit 12 Brain-V findings against the combined Bowern & Lindemann framework (B&L-2020-LV = "The Linguistics of the Voynich Manuscript," Annual Review of Linguistics 2021, preprint/PDF via Yale Alumni Academy; B&L-2020-CE = "Character Entropy in Modern and Historical Texts," arXiv:2010.14697).
**Method:** Both papers downloaded and OCR-extracted (Linguistics = 27pp, Character Entropy = 53pp). Exact passages quoted with paper tag and page number. Brain-V's v2 audit (`v2-literature-audit.md`) is the baseline.

---

## Classification table

| # | Finding (one line) | Classification | B&L citation / page | Notes |
|---|---|---|---|---|
| 1 | Currier A/B differ in conditional entropy h2 | **RE_DISCOVERY** | CE §4.3.2 p.27; LV §3.2 p.12 | B&L state explicitly: *"For example, Voynich A has a somewhat higher h2 (2.17) than Voynich B (2.01)"* (LV p.12); CE Table gives "Voynich A 68,612… 2.122" / "Voynich B 145,745… 1.973" (p.26) and dedicates §4.3.2 to "Languages A and B." B&L own this finding numerically. Brain-V re-derived the same hand-separated h2 gap. |
| 2 | -edy suffix concentrates heavily in Voynich B | **RE_DISCOVERY** | CE §4.3.2 p.27 | Direct quote: *"The -edy glyph sequence found at the end of words is eighty-six times more common in Voynich B (one out of five words in Voynich B end with this sequence)"* (CE p.27). B&L footnote 34 adds the chedy-is-dominant-contributor caveat. Brain-V independently re-observed. |
| 3 | qo- prefix more common in Voynich B | **RE_DISCOVERY** | CE §4.3.2 p.27; LV §3.2 p.12 | CE: *"the qo- sequence at the beginning of a word is about twice as common in Voynich B (also found in one in five words)"* (p.27). LV: *"Language B has a higher frequency of both the qo- prefix and the -dy suffix (they are about two times and three times more common, respectively)"* (p.12). B&L also show removing the two affixes collapses the A/B entropy gap to <1% — a stronger, framework-grade claim than Brain-V has made. |
| 4 | Voynichese character positions heavily constrained within words | **RE_DISCOVERY** | CE §4.7 pp.37, §4.6.2 p.34; LV §3.2 p.12 | CE Summary: *"it is largely the result of common characters which are heavily restricted to certain positions within the word"* (p.37). CE §4.6.2: *"All characters are heavily restricted in whether they can appear at the beginning, middle, or end of the word"* (p.34). LV: *"Many Voynich characters and character combinations are restricted to certain parts of the word"* and attribute the low h2 directly to this positional structure (p.11–12). This is arguably the single load-bearing B&L conclusion. |
| 5 | Hand A herbal ≈ Hand B herbal on TTR (0.83=0.83) and mean length (4.99 vs 5.07) | **EXTENDS_B&L** | LV §3.3–3.4 pp.13–15 (no direct within-section A vs B test) | B&L compute TTR/MATTR at the whole-language (A, B, Full) level and conclude Voynichese has "medium morphological complexity" close to Germanic/Iranian/Romance (LV p.15). They do **not** slice by section-hand intersection. Brain-V's controlled within-herbal A-vs-B convergence test is a specificity extension of B&L's MATTR methodology and, if anything, makes B&L's claim stronger (the character-level A/B gap shrinks further when section is held constant). |
| 6 | Section-specific vocabulary concentration (chedy/shedy/qokain biological, al/l recipes, daiin herbal) | **EXTENDS_B&L** | LV §3.3 Table 2 p.13, §4.3 p.19 | B&L acknowledge section-vocabulary clustering and cite Montemurro et al. 2013 as the source of the phenomenon: *"They… identify words which are more uniformly distributed throughout the Voynich Manuscript and compare them to those which tend to cluster. Those which tend to cluster are more likely to provide information about the subject matter"* (LV p.19). B&L list chedy/shedy/qokain as Voynich B's top words and daiin as Voynich A's top word (Table 2, p.13) but do **not** themselves partition by section. Brain-V's per-token section concentration (biological vs herbal vs recipes) refines B&L + Montemurro within B&L's stated framework. |
| 7 | Layer-1/Layer-2 morphological structure with inner/outer inventories closed at >90% | **EXTENDS_B&L** | LV §3.2 pp.11–12 | B&L adopt the prefix / root-midfix / suffix three-field structure (Tiltman 1950 → Roe 1997 → Stolfi 2005 → Reddy & Knight 2011 → Palmer 2014; LV p.11), and list six prefixes, eight roots, seven suffixes as "a few of the most common character combinations in each field" (p.11–12). They do **not** report closure-rate percentages for the inventories. Brain-V's >90% closure is a quantitative extension within B&L's accepted three-field slot-grammar frame. |
| 8 | Phonological sub-class partition of Layer-1 inners: n vowel-exclusive (0/2240 A, 0/7403 B) | **TRULY_NOVEL** | LV §2.3.1 pp.8–9 (Sukhotin vowel/consonant discussion is related but not overlapping) | B&L discuss the Sukhotin-algorithm vowel-consonant split on the whole Voynich character set (LV pp.8–9), noting that *"three characters that are almost exclusively word final are identified (g, n, y)"* (p.8). They do not perform a vowel-class × morpheme-slot co-occurrence test, nor report per-hand zero-count cells for n. The specific "n has 0 vowel-context occurrences" finding is absent from both papers. Stands as novel. |
| 9 | Basque as a candidate language for Voynichese | **TRULY_NOVEL** (Basque is absent from B&L's language-identification section) | LV §5 pp.21–23; CE Appendix language list p.38 incl. *"38. Vasconic: Basque"* | LV §5 surveys Latin/Romance (§5.1), Hebrew (§5.2), Nahuatl (§5.3), and Bax's "unknown language" (§5.4), plus a footnote 14 mentioning Greek, Estonian, and mixed-language hypotheses — **Basque is nowhere on the list**. CE includes Basque only as one of 311 Wikipedia baseline samples with h2=3.250 (Table, p.38) — the highest-entropy Vasconic entry in their corpus, but it is a comparison sample, not a candidate. B&L's framework neither proposes nor rules out Basque. Brain-V's Basque-candidate hypothesis is unaddressed by B&L. |
| 10 | Agglutinative typology match for Voynichese | **CONTRADICTS_B&L** (modest but real) | LV §3.3–3.4 pp.14–16 | LV MATTR & top-10 frequency analysis explicitly concludes: *"Voynich most closely resembles the averages for Germanic and Iranian, and least resembles those for Turkic, Dravidian, and Kartvelian"* (p.16). Since Turkic/Dravidian/Kartvelian are B&L's *agglutinative* comparison families, their conclusion is that Voynichese is **not** agglutinative-like but rather medium-morphology (Germanic/Iranian/Romance range). Brain-V's agglutinative-match claim runs against this. Brain-V must either (a) re-examine its MATTR figure against B&L's MATTR ranges, or (b) explain why the typological diagnostic that B&L used gives the opposite verdict on its data. **High-impact flag.** |
| 11 | Vowel harmony testing in Voynichese A or B | **TRULY_NOVEL** (B&L do not run vowel-harmony tests) | LV §2.3.1 pp.8–9 | B&L run Sukhotin's algorithm to identify vowels (LV p.8) and discuss vowel/consonant distinctions, including noting *"different characters are identified between the two Voynich Languages, A and B"* (p.9), but they do **not** test for vowel harmony (backness/rounding co-occurrence patterns within words). The word "harmony" does not appear in either paper. Brain-V's V-harmony test is genuinely uncovered territory within the B&L framework. |
| 12 | Per-plant content encoding refutation | **EXTENDS_B&L** | LV §4.3 pp.19–20 | B&L (via Sterneck & Bowern 2020, cited on p.19–20) operationalise topic clustering across the manuscript and find *"different scribes may have used different encipherment strategies or written about different subjects"* (p.20), and that topic clusters align with hand and section. They do **not** test the narrower "one plant page = one plant-name encoding" hypothesis. Brain-V's per-plant-content refutation is a specificity extension of B&L's topic-modeling framework, testing a finer-grained prediction that B&L didn't.

---

## Summary

### Count per category

| Category | Count | Items |
|---|---|---|
| RE_DISCOVERY | 4 | #1, #2, #3, #4 |
| EXTENDS_B&L | 4 | #5, #6, #7, #12 |
| TRULY_NOVEL | 3 | #8, #9, #11 |
| CONTRADICTS_B&L | 1 | #10 (agglutinative) |

### Items that shift from prior "TRULY_NOVEL" to EXTENDS_B&L or RE_DISCOVERY

The prior v2-literature-audit did not cover exactly these 12 items (it covered a different 20-item list), so strict re-classification is partial. However:

- **#1 (A/B entropy gap)** — Prior audit classified as INDEPENDENT_VERIFICATION of Lindemann & Bowern. The re-audit confirms this, **but tightens it to RE_DISCOVERY** because B&L give per-hand h2 numbers (Voynich A = 2.17 / 2.122, Voynich B = 2.01 / 1.973), a near-identical decomposition of the affix contribution, and the "remove qo-/-dy → A≈B" collapse test. Brain-V's per-hand h2 numbers are not additive over what B&L already published.
- **#2 (-edy in B)** — B&L publish an exact "eighty-six times more common" ratio and name chedy as the dominant contributor. RE_DISCOVERY, not EXTENDS.
- **#3 (qo- in B)** — B&L publish "about twice as common" and the joint-affix-removal collapse. RE_DISCOVERY.
- **#4 (positional constraints)** — This is B&L's thesis statement. RE_DISCOVERY.
- **#7 (Layer-1/Layer-2 inventories)** — Shifts from TRULY_NOVEL (v2 audit's implicit classification via Stolfi/Zattera comparison) to EXTENDS_B&L because B&L explicitly adopt the three-field structure. Brain-V's >90% closure rate is still a quantitative addition, not a re-discovery of the structure itself.

### Items that hold up as TRULY_NOVEL

- **#8 — n vowel-exclusive per-hand zero-count partition.** B&L note n as word-final but do not cross n with vowel-context counts or separate by hand.
- **#9 — Basque candidate.** Absent from B&L's language-identification survey; only present as a Wikipedia baseline sample with h2=3.250. B&L neither propose nor dismiss Basque. The Basque hypothesis remains Brain-V's own (extending Havrankova 2025 / Caveney 2020) and is not constrained by B&L.
- **#11 — Vowel harmony test.** B&L run vowel-identification (Sukhotin) but not V-harmony. The word "harmony" does not appear in either paper.

### CONTRADICTS_B&L flags (high-impact if true)

- **#10 — Agglutinative typology match.** This is the single most important flag from the re-audit. B&L's MATTR and top-10-frequency analysis explicitly concludes Voynichese *"least resembles"* Turkic/Dravidian/Kartvelian (the agglutinative families) and is closest to Germanic/Iranian/Romance (LV p.16). Brain-V claiming an agglutinative-typology match **directly contradicts** a published B&L conclusion. This needs to be either (a) defended with a side-by-side MATTR comparison that shows B&L's MATTR conclusion does not hold on a hand-separated, section-controlled re-computation, or (b) downgraded. For v2 this is the item most likely to draw peer critique, and the audit flags it as highest-priority resolve-before-submission. Note that Brain-V's own Basque work (H-BV-BASQUE-FREQ-DIST-01 MARGINAL 2/3, H-BV-BASQUE-PHONOTACTIC-01 at threshold 3/5) suggests the Basque/agglutinative picture is not airtight even internally.

### Methodological takeaway

Four items (#1–4) were **already established by B&L** with exact numerical claims that Brain-V reproduces. v2 must frame these as RE_DISCOVERIES with full citation, not as Brain-V novelty. The earlier v2-audit labeled most of them as INDEPENDENT_VERIFICATION/QUANTITATIVE_REFINEMENT, which understates B&L's specificity: B&L give 86× for -edy, "about twice" for qo-, per-hand h2 numbers, and the affix-removal collapse test. Brain-V's numbers are not visibly finer than B&L's on these four.

Four items (#5, #6, #7, #12) are **genuine extensions** within B&L's framework — B&L establish the broader phenomenon, Brain-V adds within-section controls, per-hand closure rates, and finer per-token/per-plant slices.

Three items (#8, #9, #11) are **truly outside** B&L's scope: phoneme-typed slot partitioning, Basque as candidate, and vowel harmony.

One item (#10) **contradicts** a published B&L conclusion and requires a reconciliation pass before v2 submission.

### Items B&L address that Brain-V should cite in v2

- The qo- + -dy affix-removal test (CE §4.3.2 p.27): "If the two sequences are removed from both texts, then the h2 value for Language A and Language B come within about 1% of each other." LV p.12 gives the post-removal values as 2.23 / 2.24. Brain-V has not published this exact test; running it would both (a) reproduce B&L cleanly and (b) test whether the A/B character-level convergence Brain-V reported in its within-herbal comparison is the same phenomenon or independent.
- MATTR by language family (LV Fig. 9 / §3.4): B&L's MATTR analysis with a 2000-word window is the yardstick the agglutinative claim must be measured against. v2 should either reproduce B&L's MATTR numbers with Hand A herbal / Hand B herbal windows or explain the methodological divergence.

---

*Words: ~1,420. Dense B&L citations throughout. UNKNOWN flags were not needed — both papers were obtained in full and both address, or fail to address, each listed finding unambiguously.*
*Sources consulted: arXiv:2010.14697 (PDF via Yale Alumni Academy mirror; downloaded 2026-04-17), Bowern & Lindemann 2021 Annual Review of Linguistics preprint (PDF via info-quest.org → alumniacademy.yale.edu; downloaded 2026-04-17). Both saved to `outputs/reports/_bl_char_entropy.txt` and `_bl_linguistics.txt` for auditability.*
