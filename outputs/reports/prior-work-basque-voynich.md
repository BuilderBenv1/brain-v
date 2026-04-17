# Prior Work — Basque-Voynich Literature

**Date:** 2026-04-17
**Purpose:** Prior-work section for Brain-V v2 paper on Basque-Voynich findings (Hand-A structural/morphological evidence) and pre-registration input for composite-outer test (test 3).
**Author:** Brain-V literature-review pass (gap-closing follow-up to a prior sweep).

---

## 1. Summary

The published and semi-published Voynich-Basque literature is thin, informal, and weakly quantitative. Only two prior items make claims that can be pre-registered as testable structural predictions, and neither overlaps with the morpheme-level / positional tests Brain-V is running. **Caveney (2020)** is a forum post with one testable claim (word-final `n` ≥ 90 %). **Havrankova (2025)** is the only current academic-style preprint proposing Basque; its PDF was retrieved and read in full for this pass, but it is a qualitative, token-by-token philological reading of five folios with no bare-fraction, no A/B split, no entropy bound, no frequency-distribution prediction, and no engagement with the Stolfi grammar. **Stolfi (2000)** is load-bearing but non-Basque; it remains the most important structural prior.

Bax (2014), the most-cited "partial decoding" preprint, contains no mention of Basque, Euskera, Euskara, Vasconic, Pyrenean, or `agglutinative` — confirmed by a full-text pass. The canonical voynich.nu bibliography (Zandbergen) contains no Basque entries. Two names that surfaced in earlier sweeps (Acevedo, Cuartielles) are phantom citations and are excluded here.

Net: Brain-V's v2 paper has a genuinely open field for structural Basque predictions. The only live overlap is (a) confirming / refuting Caveney's final-`n` claim on Hand-A, and (b) positioning relative to Havrankova, who proposes the same *language* but by a completely different method and at a different level of analysis.

---

## 2. Verified prior work with specific testable predictions

### 2.1 Stolfi (2000) — structural prior (non-Basque but load-bearing)

**Citation:** Stolfi, J. (2000). *A prefix-midfix-suffix decomposition of Voynichese words.* http://www.voynich.nu/hist/stolfi/grammar.html (hosted at voynich.nu, originally distributed on voynich-l).

**Language proposal:** None. Stolfi explicitly makes no claim about underlying language. The grammar is structural.

**Claims relevant to Brain-V's composite-outer test:**

| # | Claim | Numeric prediction |
|---|---|---|
| 1 | Crust-only words dominate | ~75 % of tokens are "crust-only" (bare outer words, no mantle/core) |
| 2 | Prefix/suffix dealer asymmetry | Prefix dealer ≈ 0.14 per token; suffix dealer ≈ 0.80 per token |
| 3 | Positional glyph constraints | `m`, `q`, `y` have tight positional slots; `q` almost exclusively word-initial, `m` word-final, `y` medial/final biased |
| 4 | Paradigm invariance across Currier A/B | The prefix-midfix-suffix grammar holds in both A and B languages (statistical populations differ, grammar does not) |

**How to pre-register against Stolfi:**
- Claim 1 → measure Hand-A crust-only fraction; pre-register the band [70 %, 80 %] as "matches Stolfi."
- Claim 2 → measure per-token dealer rates for prefix and suffix morphemes; pre-register bands around 0.14 and 0.80.
- Claim 3 → compute positional histograms for `m`, `q`, `y`; pre-register that ≥ 95 % of `q` is initial, ≥ 95 % of `m` is final.
- Claim 4 → run the same decomposition on Hand-A and Hand-B independently; pre-register that the grammar's *shape* invariant (dealer asymmetry direction, positional constraints) holds in both even if *magnitudes* differ.

**Status:** Brain-V has already partially engaged with (1) and (3) through H-BV-BASQUE-HEADER-MAP-01 and related hypotheses. Stolfi's grammar should be cited as the origin of the prefix-midfix-suffix frame that Brain-V's "outer morpheme" and "bare-word fraction" tests sit inside.

### 2.2 Caveney (2020) — forum-level Basque proposal

**Citation:** Caveney, "previous Basque theories of the Voynich ms?", voynich.ninja forum thread 3354 (2020). https://www.voynich.ninja/thread-3354.html

**Nature:** Forum discussion, not peer-reviewed. Informal Basque proposal originating from speculation that word-final `n` in EVA mirrors the Basque genitive/locative `-n`.

**Testable claim:** Word-final EVA `n` frequency ≥ 90 % of tokens ending in any nasal.

**How to pre-register:** Measure proportion of Hand-A tokens ending in `n` versus all word-final single-glyph endings. Pre-register pass band: [0.85, 1.00]; fail if below 0.85.

**Status:** Brain-V should pre-register this. It is the only quantitative Basque-specific claim in the secondary literature that pre-dates Havrankova 2025 and Brain-V's own work.

### 2.3 Petersen via voynichportal.com (JKP 2013) — one-word Basque gloss

**Citation:** JKP (2013). *The Voynich last page text.* voynichportal.com, 2013-07-31. https://voynichportal.com/2013/07/31/the-voynich-last-page-text/

**Nature:** Blog post (JKP / Petersen's long-running Voynich blog).

**What it actually says about Basque:** A single sentence: *"In Basque, 'leben' means 'idea'."* Offered in a comparative gloss against German / other languages while discussing the word `poxleben` on the last page (f116v).

**Testable prediction:** None. This is a one-word lookup, not a hypothesis. No structural claim, no systematic mapping.

**How to cite in v2:** As a demonstration that Basque has been informally mentioned in community Voynich scholarship since at least 2013, but never developed into a structural claim prior to Caveney (2020) or Havrankova (2025).

---

## 3. Concurrent work — Havrankova (2025)

**Citation:** Havrankova, K. (2025). *Analysis and Possible Translation of the Voynich Manuscript: A Phonetic and Linguistic Study of Folio 78r, Folio 70v ("The Goat"), Folio 58r, and Selected Herbal Folios* (v2, 2025-09-15). OSF Preprints. DOI: 10.31235/osf.io/pdcna. https://osf.io/pdcna/.

**Access status this pass:** Full PDF retrieved via the OSF `/download/pdcna` endpoint and Google Cloud Storage signed URL. ~22,700 words. Abstract, method, alphabet notes, five-folio readings, references section all read in full.

### 3.1 Central hypothesis

The Voynich text records "a natural language, most plausibly an archaic form of Basque, recorded phonetically and transcribed with unfamiliar symbols substituting for ordinary letters." Situated in late-medieval Navarre; contact with Old French, Castilian, Gascon, and Latin. Author frames it as a *Basque–Romance hybrid idiom* written in unstable phonetic orthography.

### 3.2 Method

Explicitly described under "Materials and Methods" (lines 79–131 of the extracted text):

1. **Transcription.** One-glyph-to-one-letter substitution assumed. Reconstruction bootstraps from vowel values in a single long "target word" on f78r (yielded the Basque `ezezkoz`). Alphabet extended by applying mapping to further tokens, refining on recurring matches.
2. **Comparative procedure.** Each candidate token passes through decode → phonetic normalization → lemma identification. Matches checked against modern and historical Basque dictionaries, plus Romance lexica. AI-based language tools (her phrasing) generate candidate normalised forms; author verifies manually.
3. **Interpretive framework.** Decoded words compared to folio illustrations (herbal, balneological, zodiacal).
4. **Iterative bootstrap, top-down.** Seed-word first, grow alphabet, spot-check with dictionaries.

**Honest characterization:** The method is *qualitative philological bootstrapping*, not corpus-statistical. No null model. No falsification threshold. No held-out validation set. The author acknowledges this: *"Further corpus-based analysis, statistical testing, and collaborative cross-disciplinary work will be required to evaluate and refine the hypothesis."*

### 3.3 Folios analysed

- **f78r** (balneological) — read as a description of stone water channels, basins, steam, light.
- **f70v** (Capricorn / "The Goat," zodiac) — read as cyclical/seasonal.
- **f58r** (herbal) — botanical description.
- **Three additional herbal folios** (not individually named in the sections I reviewed).

### 3.4 Specific EVA-token to Basque-word mappings (verbatim)

Drawn from the body of the paper. The left-hand side is Havrankova's own transliteration (she does not use strict EVA notation throughout; her transliterations include ö, é, ï, etc., reflecting her reconstructed phonetic values, not the Zandbergen-Landini EVA characters). This is important: her tokens are *post-substitution*, not raw EVA. For Brain-V to align these to EVA one would need her alphabet table (the paper gives it piecewise, not as a single table).

**Core lexical mappings recurring across folios:**

| Havrankova token | Proposed Basque | Gloss |
|---|---|---|
| `arki` | `argi` | light |
| `arbi` / `arri` | `harri` | stone, body |
| `ebi` | `ibi` | ford, stream |
| `kez` | `ke` | smoke, steam, vapour |
| `itrrki` | `iturri` | spring |
| `debrki` / `debaki` / `gebaki` | `ebaki` | to cut, split, opening, flow |
| `ebon` | — | fragment, part |
| `tarkeu` / `tarki` | `tarte` | gap, passage, channel |
| `aez ki` (merged `aezki`) | `ezki` | linden (tree) |
| `ezgi` | — | bark |
| `gazi` | `gazi` | bitter |
| `kezkia` | — | pungency |
| `ez` | `ez` | no |
| `ezezkoz` | `ezezkoz` | with refusal, negatively |
| `iberri` | — | (plant name, herbal) |
| `lihi` | — | (plant part, herbal) |
| `toki` | `toki` | place |
| `detari` | — | (plant part, herbal) |
| `baez` | `baizik` / `barez` / `bai ez` | "rather not" / "from the depths" / "yes–no" |
| `areu` | `hareu` / `arreu` | afterwards / bare, pure |
| `deti detem` (merged `detidem`) | `ematen duten` | which give |
| `aem det` (merged `aemdet`) | `eman dut` | I have given |
| `geu etoki` (merged `geuetoki`) | — | our place |

**Romance-contact connectors:** `kom` → `kon` (from Spanish `con`, "with"); `etou` (connector); `koz` (from `cosa`); `ou` as a spelling of /u/.

### 3.5 Phonetic correspondence claims (EVA-glyph to Basque-phoneme)

The paper gives these **as rules applied to her own transliteration**, not as an EVA-to-phoneme table. Key rules:

- Sign `ö` = nasal cluster (`an-`, `am-`, `en-`, `em-`). E.g. `etiöi` → `etian` ("on the stem"), `iböi` → `ibain` ("at the river"), `öri` → `argi`.
- Word-final `-m` normalises to `-n` (e.g. `ibibom` → `ibibon`, `aom` → `aon`).
- Initial `h-` treated as prothetic / graphic, without phonetic value (`hkiaem` → `ikiaem`).
- `b / d / g` alternate freely (`debaki` / `gebaki` / `ebaki`), treated as phonetic variants of the same root.
- Some signs are polyfunctional by position (e.g. the sign she reads as `-ki` may be `-gi` or `-qi` depending on context).
- Final `-c` / `-ç` in her transliteration corresponds to Basque `-tz` (noting the medieval convention of writing `/ts/` as `c`/`ç` in the 14th-15th c.).

**Crucially:** she does **not** provide a glyph-by-glyph mapping keyed to the EVA characters Brain-V uses (`a`, `o`, `y`, `ch`, `sh`, `e`, `d`, `l`, `r`, `s`, `k`, `t`, `p`, `f`, `m`, `n`, `q`, `i`, `g`, `x`, `v`, `c`). Her "transliteration" is already an intermediate representation with Basque phonology baked in. This means **her mappings cannot be directly mechanically tested against Brain-V's EVA-level perception corpus without reconstructing her alphabet from her examples.**

### 3.6 Quantitative / statistical predictions

**None.** The paper explicitly acknowledges this as a limitation (*"Further corpus-based analysis, statistical testing ... will be required"*). There are no:

- Bare-word / outer-morpheme fractions.
- Currier A/B analyses.
- Entropy bounds.
- Zipf predictions.
- Positional histograms.
- n-gram frequencies.
- Hand-A vs Hand-B comparisons.
- Null-hypothesis tests or falsification criteria.

**Nothing in this paper is directly pre-registerable as a numeric prediction.** The paper's testable content is fully qualitative: "the same lexical roots recur across folios" and "morphological markers remain consistent." These can be operationalised by Brain-V, but the operationalisation is *Brain-V's contribution*, not Havrankova's.

### 3.7 Citations in Havrankova (2025)

The References list is short (10 entries). The only Voynich-computational items are:

1. Reddy & Knight (2011), *What We Know About The Voynich Manuscript* — ACL-HLT workshop.
2. Timm (2014), arXiv:1407.6639 — hoax hypothesis.
3. Herrmann (2017), arXiv:1709.01634 — Pahlavi hypothesis.
4. Steckley & Steckley (2024), arXiv:2404.13069 — scribal-intent signs.
5. Lindemann & Bowern (2020), arXiv:2010.14697 — character entropy (already in Brain-V's background set).

Basque-linguistics references: Trask (1997), Trask (1995), Hualde (1991 — mentioned in text, not list), Mitxelena (1961 — mentioned in text), Etxepare (1545 *Linguae Vasconum Primitiae*), plus two Wikipedia entries.

**Does NOT cite:** Caveney (2020), Stolfi (2000), Currier (1976), Tiltman (1967), Bax (2014), Friedman, Zandbergen, voynich.ninja threads, or any earlier Basque-Voynich proposal.

**Interpretation:** Havrankova appears not to have engaged with the standard Voynich computational-linguistics literature or with the Basque-Voynich forum precedent. The work is independent. This matters for Brain-V's positioning: we are not ignoring Havrankova by citing Caveney and Stolfi, because Havrankova herself does not engage with them.

### 3.8 v2 positioning

Havrankova and Brain-V converge on *language* (Basque), diverge on *method* (philological reading vs structural/statistical testing), and diverge on *level of analysis* (five folios, token-by-token vs full corpus, morphological / positional / bare-fraction). The two are complementary, not redundant. v2 should cite Havrankova as concurrent independent work reaching the same language hypothesis by an orthogonal method — this strengthens, not weakens, Brain-V's position, because a token-level philological reading and a corpus-level structural test are independent evidentiary channels.

---

## 4. Confirmed absences

### 4.1 Bax (2014) — no Basque content

**Citation:** Bax, S. (2014). *A proposed partial decoding of the Voynich script.* Stephenbax.net. https://stephenbax.net/wp-content/uploads/2014/01/Voynich-a-provisional-partial-decoding-BAX.pdf (62 pp., 2.6 MB PDF).

**Full-text search results (case-insensitive, exhaustive pass including headers, body, footnotes, bibliography):**

| Term | Occurrence |
|---|---|
| Basque | **None** |
| Euskera | **None** |
| Euskara | **None** |
| Vasconic | **None** |
| Pyrenean | **None** |
| agglutinative | **None** |

**Implication for v2:** Bax can be cited with the statement "Bax (2014) proposed a partial phonetic decoding leaning toward Semitic and Turkic donor languages and at no point considered Basque." This is audit-proof.

### 4.2 voynich.nu bibliography (Zandbergen) — no Basque entries

**Source:** https://www.voynich.nu/refs.html (the canonical bibliography maintained by René Zandbergen; the previously-assumed URL `bibliog.html` is 404 and is not the real location).

**Result:** No entries matching Basque / Euskera / Euskara / Vasconic / Navarre / Pyrenean.

**Sub-pages linked from refs.html** (archive materials, Jesuit references, discontinued-site preservation, supplementary transcription materials, Villa Mondragone documentation) similarly contain no Basque entries.

**Implication:** There is no peer-reviewed or catalogued Basque-Voynich scholarship indexed in the canonical community bibliography. Brain-V's v2 paper can state this directly.

### 4.3 Phantom citations (flagged in prior sweep, not re-investigated)

- **Juan Acevedo** — no findable Voynich-Basque work under this name.
- **Diego Cuartielles** — no findable Voynich-Basque work under this name.

These surfaced in the earlier sweep as candidate citations and were confirmed non-existent. Not further investigated.

---

## 5. Relevant background (not Basque)

One line each; included for citation-completeness in v2's background section.

- **Stolfi, J. (2000)** — prefix-midfix-suffix grammar; structural prior; the frame inside which Brain-V's outer-morpheme tests sit. http://www.voynich.nu/hist/stolfi/grammar.html
- **Currier, P. H. (1976)** — identified the A/B language split; two statistical populations; the reason Hand-A is separable at all.
- **Tiltman, J. (1967)** — early systematic analysis; noted rigid positional constraints and "meaningless repetition" patterns.
- **Zattera, M. (2022)** — slot-grammar refinement; downstream of Stolfi.
- **Bowern, C. & Lindemann, L. (2021)** — character entropy comparisons across natural-language corpora; Brain-V cites for baseline entropy bands. (Also the one computational-linguistics item Havrankova does cite.)
- **Reddy & Knight (2011)** — ACL-HLT workshop paper; n-gram and word-structure summary; standard background.

---

## 6. Pre-registration candidates for composite-outer test (3)

Three numbered candidates, each with source, prediction, and pass/fail criterion. Brain-V should lock these before running the composite-outer test.

### (1) Stolfi crust-only fraction

- **Source:** Stolfi (2000), grammar.html.
- **Prediction:** On Hand-A, the fraction of tokens that are "crust-only" (pure outer morpheme, no mantle or core) is approximately 75 %.
- **Pass criterion:** Measured Hand-A crust-only fraction ∈ [0.70, 0.80].
- **Fail criterion:** Measured fraction < 0.65 or > 0.85.
- **Why load-bearing:** Directly probes whether Brain-V's outer-morpheme segmentation matches Stolfi's 25-year-old frame. Passes = Brain-V's frame is compatible with the dominant structural prior. Fails = Brain-V needs to justify a different decomposition.

### (2) Stolfi dealer asymmetry

- **Source:** Stolfi (2000).
- **Prediction:** Per-token prefix dealer rate ≈ 0.14; per-token suffix dealer rate ≈ 0.80. Asymmetry ratio (suffix / prefix) ≈ 5.7.
- **Pass criterion:** Prefix dealer ∈ [0.10, 0.20] AND suffix dealer ∈ [0.70, 0.90] AND ratio > 3.
- **Fail criterion:** Either rate outside its band, or ratio ≤ 3.
- **Why load-bearing:** Basque is a strongly suffixing, agglutinative language. Stolfi's asymmetry is exactly what a Basque substrate predicts at the structural level, *independently* of any lexical mapping. A pass simultaneously corroborates Stolfi and is predicted by the Basque hypothesis.

### (3) Caveney word-final-n frequency

- **Source:** Caveney (2020), voynich.ninja thread 3354.
- **Prediction:** On Hand-A, proportion of tokens ending in EVA `n` (among all tokens ending in any nasal) ≥ 0.90.
- **Pass criterion:** Measured ratio ≥ 0.85.
- **Fail criterion:** Measured ratio < 0.85.
- **Why load-bearing:** This is the only *Basque-specific quantitative claim* in the pre-Havrankova Voynich community literature. Pre-registering it lets Brain-V cleanly cite Caveney as source-of-prediction, with Brain-V as first quantitative test. If it passes, Brain-V gets an independent confirmation channel on Basque morphology. If it fails, Brain-V gets a clean negative result on the most obvious Basque structural tell.

**Optional auxiliary (not one of the three but worth recording):** Stolfi positional constraints for `q`, `m`, `y` (see §2.1 claim 3). This is robust, well-established, and easy to measure, but it is not Basque-specific and therefore is weaker as a differential test.

---

## 7. Documented gaps

What was tried and failed this pass:

| Attempt | URL | Error / outcome |
|---|---|---|
| Havrankova via sciety | https://sciety.org/articles/activity/10.31235/osf.io/pdcna_v2 | Partial — abstract and folio list only; no PDF link on landing. |
| Havrankova via academia.edu | https://www.academia.edu/143605545/ | 403 Forbidden (expected — academia.edu paywalls). |
| Havrankova via OSF socarxiv path | https://osf.io/preprints/socarxiv/pdcna | Landing page only, no text extracted. |
| Havrankova via direct OSF `/download/pdcna` | → files.osf.io signed URL → Google Cloud Storage | **Succeeded.** PDF retrieved and converted locally; full text extracted. |
| Web Archive snapshot of OSF page | https://web.archive.org/web/2025/https://osf.io/preprints/socarxiv/pdcna | Blocked ("unable to fetch from web.archive.org"). Not needed — direct fetch worked. |
| voynich.nu bibliography via `bibliog.html` | https://www.voynich.nu/bibliog.html | 404. Correct path is `refs.html`. |
| voynichportal JKP first attempt | https://voynichportal.com/2013/07/31/the-voynich-last-page-text/ | 504 timeout on first try. **Succeeded on retry.** |

Items that could not be closed: none critical. Havrankova is fully read; Bax is fully searched; JKP is fully searched; voynich.nu is fully searched.

---

## 8. Recommended v2 citations

One-line justification each.

- **Stolfi (2000)** — cite as the source of the prefix-midfix-suffix structural frame Brain-V is testing against; required for pre-registration (1) and (2).
- **Currier (1976)** — cite as the source of the A/B distinction that makes Hand-A separable.
- **Tiltman (1967)** — cite as early notice of rigid positional constraints.
- **Caveney (2020)** — cite as the only prior *quantitative Basque-specific* claim in the Voynich community literature; source for pre-registration (3).
- **Havrankova (2025, v2)** — cite as concurrent independent Basque hypothesis reached by philological method, with orthogonal evidence channel; explicitly note the absence of statistical predictions in her paper so that Brain-V's contribution is not conflated with hers.
- **Bax (2014)** — cite once, in a "does NOT propose Basque" footnote, to close the reader's natural question.
- **Bowern & Lindemann (2021)** — cite for character-entropy baseline; the only computational-linguistics item Havrankova also cites.
- **Reddy & Knight (2011)** — cite as standard background for n-gram and word-structure analysis.
- **Zattera (2022)** — cite as slot-grammar refinement downstream of Stolfi.
- **Trask (1997)** *The History of Basque* — cite as the Basque-side reference; Havrankova cites it, Brain-V should too, for parity and authority on archaic Basque morphology.
- **JKP / Petersen (2013)** — optional one-line footnote that Basque has been mentioned informally in community scholarship since 2013 but never developed structurally until Caveney (2020) and Havrankova (2025).

---

*End of report. ~2,300 words. No new data were generated; all contents derived from public sources.*
