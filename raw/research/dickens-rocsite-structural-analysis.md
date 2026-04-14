# Dickens/RocSite Structural Analysis — Research Reference

Source: Adam Dickens, "Adversarial Analysis of Voynich Manuscript Structure with Indus Script Control," RocSite, January 2026
URL: https://rocsite.com/rocsite-voynich/
Status: TO VERIFY — claims are testable, conclusions contested
Filed: 2026-04-14

---

## Summary

Dickens ran structural analysis on the full EVA transliteration (35,931 words, ~170,000 glyphs, 242 folios) using mutual information, shuffle tests, and adversarial hypothesis testing. His conclusion: the manuscript is procedurally generated (not natural language), created as a mnemonic scaffold by university physicians in Northern Italy ~1420 CE.

The statistical findings are valuable. The conclusion is one interpretation of those findings. Brain-V should verify the numbers independently and test whether the three-layer model explains the same observations.

---

## Testable Claims — Brain-V Must Verify

### 1. Cross-Line Mutual Information = 0.000

**Claim:** MI between the last glyph of line N and the first glyph of line N+1 is 0.000 — statistically indistinguishable from random baseline (p > 0.001).

**Method:**
```
for each line_pair in corpus:
  last_glyph = line[n][-1]
  first_glyph = line[n+1][0]
  cross_line_pairs.append((last_glyph, first_glyph))
cross_line_MI = calculate_MI(cross_line_pairs)
```

**Significance:** If confirmed, this means zero statistical dependency between lines. Every line is generated independently of the previous one.

**Alternative explanations Brain-V should consider:**
- Pharmaceutical recipe format (each line = one complete instruction) produces the same signature
- A cipher that resets per-line (e.g., key resets at line boundaries) would produce this
- The three-layer model: suffix morphology resets per-word, stem cipher may reset per-line
- This does NOT distinguish between "meaningful content in recipe format" and "procedurally generated nonsense"

**Brain-V action:** Compute cross-line MI on the EVA corpus. Report the value. Compare against shuffled baseline.

---

### 2. Within-Line Mutual Information = 0.671

**Claim:** MI between adjacent glyphs within the same line is 0.671 — highly significant (p < 0.0001). Strong structure within lines.

**Significance:** The text has real internal structure at the word/line level. This is consistent with both language and procedural generation with rules.

**Brain-V action:** Compute within-line MI. Compare against Brain-V's existing entropy and IC measurements. Does within-line MI correlate with section type? (Biological vs. zodiac vs. text-only?)

---

### 3. Cross-Page Mutual Information = 0.260

**Claim:** MI across page boundaries is 0.260. Page ratio = 0.39. Described as "just shared vocabulary, not continuity."

**Significance:** Some cross-page structure exists (shared vocabulary) but weak. Contrasted with Indus Valley script at 2.130 (real discourse structure).

**Brain-V action:** Compute cross-page MI. Compare per-section — does the biological section show different cross-page MI than zodiac?

---

### 4. Shuffle Invariance

**Claim:** Randomising word order within lines does not materially degrade statistical structure. "Meaning is not encoded via sequence."

**Method:** Shuffle words within lines, measure entropy/MI/Zipf before and after. Compare degradation against natural language controls.

**Significance:** If word order doesn't matter, the text cannot encode meaning through syntax. This is a direct falsification of syntactic language encoding.

**Alternative explanations:**
- A codebook cipher where each word is an independent lookup would show shuffle invariance
- A recipe list where each word is a separate ingredient/instruction would show this
- The three-layer model: if each word is independently enciphered (stem cipher operates per-word), shuffling words wouldn't break anything

**Brain-V action:** Run shuffle test. Shuffle words within lines in the EVA corpus. Measure entropy, IC, Zipf exponent, and bigram frequencies before and after. Report degradation percentage.

---

### 5. Glyph-Level Shuffle DOES Break Structure

**Claim:** Shuffling individual glyphs (not words) destroys the statistical profile completely. "The word isn't the unit. The glyph is." — meaning the word-level structure is real and built from glyph-level rules.

**Significance:** Words have genuine internal structure (glyph order matters within words). But word order within lines doesn't matter. This is consistent with templated word generation (prefix+base+suffix).

**Brain-V action:** Verify. Shuffle glyphs within words and measure degradation. Compare against word-shuffle degradation.

---

### 6. Prefix + Base + Suffix Decomposition (~60% of words)

**Claim:** ~60% of Voynich words follow a prefix-base-suffix template. Identified ~12 prefixes and ~9 suffixes.

**Prefixes identified:** qo-, o-, y-, sh-, ch-, s-, k-, p- (and others)
**Suffixes identified:** -y, -dy, -ey, -aiy, -eey, -am, -an, -chy, -shy

**Significance:** Overlaps significantly with Brain-V's own morphological findings (H023 at 0.99). Brain-V found suffix stripping reduces vocabulary by 37.3%. Dickens found ~60% follow the template.

**Brain-V action:** Cross-reference Dickens' prefix/suffix lists against Brain-V's own suffix stripping results. Are the same affixes identified? Does adding Dickens' prefix list improve vocabulary reduction beyond 37.3%?

---

### 7. Null Glyph Dominance

**Claim:** One dominant "null" glyph ('o' in EVA) at ~25% frequency. Previous analyses incorrectly identified ~10 null glyphs. Correction: single dominant null, not padding soup.

**Significance:** If 'o' is a null/padding glyph rather than a meaningful character, frequency analyses treating it as a real letter are corrupted (similar to Brain-V's finding about 'y').

**Brain-V action:** Verify 'o' frequency. Test: does removing 'o' from stems improve Latin frequency correlation? Does 'o' behave differently from other glyphs positionally?

---

### 8. Header/Section Detection via Line-Start Asymmetry

**Claim:** ~88% of lines start with common glyphs; ~12% start with unusual glyphs that behave as structural markers correlating with section changes.

**Significance:** The text has state awareness — it "knows" when sections change. This is consistent with a structured document, not random generation.

**Brain-V action:** Compute line-initial glyph distribution. Identify the ~12% anomalous line starts. Do they correlate with folio boundaries or section transitions?

---

### 9. Synthetic Generation Reproduces Statistics at ~70% Fidelity

**Claim:** A simple prefix+base+suffix Markov generator produces text statistically indistinguishable from the original at ~70%+ fidelity. "The manuscript is reproducible as a system."

**Significance:** If true, the text CAN be explained by a simple combinatorial system. But this does NOT prove it WAS generated that way. A cipher operating on natural language with prefix/suffix morphology would produce the same generatable output.

**Brain-V action:** Build a simple prefix+base+suffix generator using Brain-V's own identified affixes. Measure statistical similarity to real corpus. Then: does the three-layer model (suffix + stem cipher + Latin) produce HIGHER fidelity than pure combinatorial generation? If yes, the meaningful-content model is a better explanation.

---

## Control Comparison: Indus Valley Script

Dickens tested the same methodology against the Indus Valley script as a control.

| Metric | Voynich | Indus | Interpretation |
|---|---|---|---|
| Within-Line MI | 0.671 | 3.649 | Indus has 5x more internal structure |
| Cross-Line MI | 0.000 | 0.000 | Both reset at line boundaries |
| Cross-Page MI | 0.260 | 2.130 | Indus preserves meaning across pages |
| Page Ratio | 0.39 | 0.58 | Indus has semantic continuity |
| Pattern Survivors | 105 (19.1%) | 0 (0%) | Voynich = rigid; Indus = natural variation |

**Key insight:** Both Voynich and Indus have cross-line MI = 0.000, but Indus is a real writing system. This means cross-line MI = 0.000 alone does NOT prove "not language." It proves "line-scoped structure" — which is also what you get from recipes, checklists, ledgers, and pharmaceutical instructions.

---

## Where Dickens' Conclusion Overreaches

**Claim:** "The Voynich Manuscript is a procedurally generated mnemonic scaffold — not a language."

**Problem:** His own data is compatible with multiple explanations:

1. **Procedurally generated nonsense** (Dickens' conclusion)
2. **Pharmaceutical recipe collection** where each line is a complete instruction (kpagel's hypothesis — explains Jaccard anomaly and cross-line MI = 0.000 without invoking meaninglessness)
3. **Three-layer cipher on natural language** (Brain-V's model — suffix morphology + stem cipher produces the combinatorial signature while encoding real content)

Dickens' methodology cannot distinguish between these. His statistical findings are valid. His conclusion is one interpretation, not the only one.

**Brain-V's three-layer model resolves the contradiction:** The text CAN be both procedurally structured (combinatorial word generation from prefix+base+suffix) AND encode meaningful content (pharmaceutical Latin underneath the cipher layers). The layers create the statistical signature of mechanical generation while the substrate carries meaning. This is a more parsimonious explanation than "someone created 240 pages of expensive illustrated meaningless text as a memory aid."

---

## For Brain-V's Hypothesis Pool

### Add as testable hypotheses:

**H-DICKENS-01:** Cross-line mutual information in the EVA corpus is 0.000 (statistically indistinguishable from random). Test: compute MI across all adjacent line pairs.

**H-DICKENS-02:** Word order within lines does not encode meaning. Test: shuffle words within lines, measure statistical degradation. If <5% degradation, hypothesis supported.

**H-DICKENS-03:** Glyph 'o' (EVA) functions as a null/padding character at ~25% frequency. Test: remove all 'o' glyphs, measure whether remaining text shows improved Latin frequency correlation.

**H-DICKENS-04:** The prefix+base+suffix template accounts for ~60% of all words. Test: apply Brain-V's suffix stripping + Dickens' prefix list. Measure coverage.

**H-DICKENS-05:** A simple combinatorial generator (prefix+base+suffix) can reproduce the manuscript's statistical profile at >70% fidelity. Test: build generator, measure fidelity. Then test whether Brain-V's three-layer model produces HIGHER fidelity.

### Cross-reference with existing Brain-V hypotheses:

- H023 (morphological suffixes, 0.99) — directly supported by Dickens' prefix/suffix finding
- H001 (substitution + transposition combo, 0.99) — compatible with Dickens' within-line MI finding
- H020 (homophonic/null cipher, 0.99) — potentially related to Dickens' null glyph 'o' finding
- H027 (text-only as Rosetta stone, 0.99) — test whether text-only section shows different cross-line MI than other sections

---

## Key References from Dickens' Work

- Montemurro & Zanette (2013): Semantic clustering in Voynich. Content-bearing words cluster by topic. CONTRADICTS pure procedural generation.
- Gordon Rugg (2004): Cardan grille hypothesis. Table-based generation. COMPATIBLE with Dickens.
- Gaskell & Bowern (Yale, 2022): "Voynichese is statistically similar to human-produced samples of meaningless text." SUPPORTS Dickens.
- Amancio et al. (2013): Found 90% similarity to real language patterns. CONTRADICTS Dickens.
- Schinner (2007): Statistical support for mechanical generation. SUPPORTS Dickens.

Brain-V should note: the published literature is split. Statistical evidence supports BOTH "real language" and "procedural generation" depending on which metrics you emphasise. Brain-V's three-layer model may be the synthesis that explains both sets of findings.

---

*Filed as research reference. All claims marked for independent verification. Conclusions treated as one hypothesis among several, not as established fact.*
