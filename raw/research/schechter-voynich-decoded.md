# Schechter — Voynich Decoded: Oil-Based Pharmaceutical Manual

Source: Scott Schechter, "A Proposed Decoding of the Voynich Manuscript," March 2026
URL: https://voynich-decoded.com
GitHub: https://github.com/scott-schechter/voynich-decoded
Reddit: r/History_Mysteries, ~21 days ago
Status: TO VERIFY — specific claims testable, code is open source
Filed: 2026-04-14

---

## Summary

Schechter claims 87.8% decoding of the Voynich Manuscript using a 3,648-entry EVA→Latin/Occitan/Hebrew glossary. He identifies the text as a bilingual Latin-Occitan oil-based pharmaceutical manual written by a Jewish apothecary in medieval southern France (Montpellier tradition, ~1250-1350). The surviving copy on Italian vellum (dated 1404-1438) would be a diaspora preservation artifact after the 1306 Jewish expulsion from France.

This is the most detailed publicly available claimed decipherment with open-source code. The claims are specific enough to test. Built with Claude Code (Anthropic).

---

## Key Claims — Brain-V Must Verify

### 1. 87.8% Decode Rate (3,648-entry glossary)

**Claim:** 87.8% of 37,886 tokens decoded. Random baseline is 2.1%, giving a 42x ratio.

**Brain-V action:** Download decode.js and the glossary from GitHub. Run the decoder against the EVA corpus. Apply Brain-V's honest scoring methodology:
- What percentage of the 87.8% produces coherent Latin/Occitan?
- What is the dictionary hit rate when ALL tokens are included (the same test that caught Brain-V's own 0.87→0.19 false positive)?
- Does the decoded output pass Brain-V's entropy, IC, and Zipf tests for natural language?

**Critical question:** Is the 87.8% "decoded" in the sense that a glossary entry exists, or in the sense that the decoded output forms coherent pharmaceutical Latin? These are very different claims.

---

### 2. Bilingual Latin-Occitan

**Claim:** The text is bilingual, mixing Latin and Occitan (langue d'oc, medieval southern French).

**Testable specifics:**
- Occitan month names in astronomical section: "mars", "aberil", "octembre"
- Zipf's law exponent of decoded text: -0.919 (natural language range)
- 41.3% Latin hit rate and 35.9% Occitan hit rate against Shem Tov ben Isaac synonym lists (739 entries tested)

**Brain-V action:**
- Build an Occitan frequency profile (medieval Occitan word lists exist in academic sources)
- Run Brain-V's stem-level substitution against Occitan as well as Latin and Italian
- Test whether adding Occitan to the reference profiles improves Brain-V's dictionary hit rates
- Verify the Occitan month names: under Schechter's mapping, do the EVA sequences in the astronomical section actually produce "mars", "aberil", "octembre"?

**Why this matters for Brain-V:** Brain-V currently tests only Latin and Italian. Occitan is a Romance language spoken across southern France and northern Italy in the 15th century. If the manuscript is from the Montpellier medical tradition, Occitan vocabulary would explain words that don't match Latin or Italian.

---

### 3. Oil-Based Pharmaceutical Content

**Claim:** The manuscript documents a six-section oil-based pharmaceutical production system:
- Herbal: plant cataloging, oil yield, bitterness assessment
- Astronomical: zodiac wheels as pharmaceutical calendar
- Biological: heated salt-oil-lard bathing procedures with 673 warnings "HEUS" (beware)
- Case notes: outcomes in past tense
- Recipe: compound preparations (oil, wool, wax, salt, wine, fish sauce, gold)

**Brain-V action:** If the decoded text really contains 673 instances of "HEUS" in the biological section, that's countable. Under Schechter's mapping, which EVA token maps to "HEUS"? Does it appear 673 times? Does it cluster in the biological section?

**Cross-reference with Brain-V findings:**
- Brain-V identified the biological section as optimal attack surface (340x Latin improvement after stripping)
- Brain-V's three-layer model predicts pharmaceutical content
- Oil-based pharmacy is consistent with the illustrations (bathing figures, plant preparations)

---

### 4. Jewish Kabbalistic Framework

**Claim:** Divine vocabulary shifts from feminine (DEA/goddess) in herbal sections to masculine (DEUS/God) in dangerous procedures. Maps to Kabbalistic sefirotic theology. 10,000-iteration permutation test confirms non-random (p < 0.0001).

**Claim:** Zero Christian vocabulary across 117 tested terms.

**Claim:** Hebrew zodiac names dominate undecoded astronomical sections 37:6:3 over Latin and Arabic.

**Brain-V action:** These claims are specific enough to test:
- Under the glossary mapping, verify the DEA/DEUS distribution across sections
- Count Hebrew vs. Latin vs. Arabic astronomical terms
- The permutation test code is in the repo (sefirotic-permutation-test.js) — run it

**Note:** Brain-V lacks expertise in Kabbalistic theology. These claims should be flagged for human domain expert review.

---

### 5. ~150 Base Words Generating ~38,000 Surface Tokens

**Claim:** The cipher generates ~38,000 surface tokens from roughly 150 base words through combinatorial padding.

**Significance:** This is directly comparable to:
- Brain-V's three-layer model (suffix morphology inflating vocabulary)
- Dickens' prefix+base+suffix decomposition (~60% of words)
- Brain-V's 37.3% vocabulary reduction from suffix stripping (8,261 → 5,181)

**Brain-V action:** Compare. Brain-V found ~5,181 stems after stripping. Schechter claims ~150 base words. If Schechter is right, Brain-V's suffix stripping didn't go deep enough — there are more layers of combinatorial padding to strip. Test: apply Schechter's glossary as a more aggressive reduction. Does the stem count drop from 5,181 toward 150? If so, how much of the remaining structure is explained?

---

### 6. Verb Conjugations

**Claim:** 18 correctly conjugated forms of NOCERE (to harm) found in the text.

**Significance:** If real verb conjugation paradigms appear in the decoded output, this is strong evidence for natural language underneath the cipher. Random or procedural generation would not produce conjugated verbs.

**Brain-V action:** Under Schechter's mapping, identify the EVA tokens that decode to NOCERE forms. Verify that the conjugations are grammatically correct Latin. Check if other verbs show similar paradigmatic structure.

---

### 7. Reading Order Problem (Unsolved)

**Claim:** "The word-level cipher appears to work, but there's a page-level reading order that hasn't been recovered. Each page has balanced Latin grammar and the correct vocabulary, but the words read as fragments in the transcription's line order."

**Significance:** This is a major honest caveat. It means the decoded output doesn't read as coherent text in standard line order. Schechter claims the words are correct but their sequence on each page needs a different reading order (spiral? boustrophedon? column-based?).

**Brain-V action:** If word-level decoding produces the right vocabulary but wrong sequence, test Brain-V's existing transposition attacks against the decoded output. Does any transposition scheme (columnar, spiral, route) produce more coherent text?

**Cross-reference:** Brain-V's H001 (substitution + transposition combo, 0.99) predicts exactly this — a transposition layer on top of substitution. Schechter may have cracked the substitution but not the transposition.

---

## Credibility Assessment

### Strengths:
- Open source code (decode.js, glossary, validation scripts)
- Specific, countable claims (87.8%, 673 instances of HEUS, 18 conjugations)
- Honest about what isn't solved (reading order)
- Statistical validation included (permutation tests, Zipf analysis)
- Built with Claude Code — methodology is transparent
- Multiple validation scripts in the repo

### Weaknesses:
- No peer review
- 87.8% decode rate needs honest scoring (Brain-V's methodology)
- Reading order unsolved = decoded text may not form coherent sentences
- Kabbalistic interpretation is not independently verifiable by statistical means
- "Jewish apothecary in southern France" is a historical narrative built on top of the cipher claim — test the cipher first
- Zero engagement from established Voynich researchers visible so far
- The 3,648-entry glossary is large — risk of overfitting (enough parameters to fit anything)

### Red flag to test:
A 3,648-entry glossary mapping EVA tokens to Latin/Occitan/Hebrew is large enough that it could fit noise. Brain-V should test: if you randomly assign 3,648 EVA tokens to Latin/Occitan/Hebrew words from medical dictionaries, what decode rate do you get? If random assignment also produces high "hit rates," the glossary is overfitted.

---

## For Brain-V's Hypothesis Pool

### Add as testable hypotheses:

**H-SCHECHTER-01:** The underlying language is bilingual Latin-Occitan, not monolingual Latin or Italian. Test: add Occitan frequency profiles to Brain-V's reference set. Does Latin+Occitan combined produce higher dictionary hit rates than Latin alone?

**H-SCHECHTER-02:** The astronomical section contains Occitan month names ("mars", "aberil", "octembre") under a substitution cipher. Test: apply Schechter's specific glyph-to-letter mapping to the astronomical section. Do recognizable month names appear?

**H-SCHECHTER-03:** The biological section contains a high-frequency warning term ("HEUS" = beware) appearing ~673 times. Test: under Schechter's mapping, identify the EVA token. Count occurrences. Check section distribution.

**H-SCHECHTER-04:** ~150 base words generate the full ~38,000 token vocabulary through combinatorial padding. Test: apply Schechter's glossary as aggressive reduction. Does stem count approach 150? Compare against Brain-V's 5,181 stems.

**H-SCHECHTER-05:** The unsolved reading order reflects a transposition layer. Test: apply Brain-V's transposition attacks to Schechter's decoded word-level output. Does any transposition scheme produce more coherent Latin/Occitan?

**H-SCHECHTER-06:** The glossary is overfitted. Test: generate 1,000 random glossaries of the same size mapping EVA tokens to Latin/Occitan medical vocabulary. Measure decode rates. If random glossaries produce >30% decode rates, the 87.8% is less impressive.

### Cross-reference with existing Brain-V hypotheses:

- H001 (sub + transposition combo, 0.99) — Schechter's unsolved reading order IS the transposition layer
- H023 (morphological suffixes, 0.99) — Schechter's "combinatorial padding" is the same finding
- H021/H025 (Currier A/B = two scribes same language, 0.99) — compatible with Schechter's model
- Finding 4 (universal substitution table) — Schechter's glossary should work across all sections if Finding 4 is correct
- Finding 5 (biological section optimal) — Schechter specifically highlights biological section with HEUS warnings

---

## Data Available for Brain-V

From the GitHub repo (https://github.com/scott-schechter/voynich-decoded):

- `decode.js` — the full decoder (Node.js, no dependencies)
- `tools/glossary-export.js` — 3,648 EVA→Latin/Occitan/Hebrew mappings
- `tools/eva-data/` — Takahashi EVA transcription
- `tools/sefirotic-permutation-test.js` — divine vocabulary permutation test
- `tools/kabbalistic-structure.js` — 8-test sefirotic coherence
- `tools/zodiac-multilingual.js` — multilingual astronomical testing
- `tools/hebrew-decode.js` — Hebrew transliteration matching
- `tools/shem-tov-match.js` — 739-entry Shem Tov cross-reference
- `publication/` — 17 evidence documents + comprehensive report

Brain-V should download the glossary and run it through the honest scoring pipeline. This is the single highest-value test: does Schechter's claimed decipherment survive Brain-V's methodology?

---

## Key Distinction from Other Claims

Most Voynich "solutions" provide a theory and some cherry-picked examples. Schechter provides:
1. A runnable decoder
2. A complete glossary
3. Validation scripts
4. An honest admission of what isn't solved

This makes it the most testable claimed decipherment currently public. Whether it's correct is a different question — but it's the easiest to falsify, which is scientifically valuable.

---

*Filed as research reference. All claims marked for independent verification. The glossary overfitting test (H-SCHECHTER-06) should be run first — if the glossary is overfitted, all other claims are suspect.*
