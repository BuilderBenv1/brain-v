# Brain-V: An Autonomous Cognitive Architecture Attacks the Voynich Manuscript

**One day. Sixty scoring cycles. Six findings.**

Brain-V is a persistent cognitive architecture — a system that generates hypotheses, tests them against statistical evidence, eliminates failures, updates its beliefs, and repeats. It was pointed at the Voynich Manuscript on April 14, 2026. This is what it found.

Everything described here is reproducible. The code, the data, the scoring methodology, and every hypothesis file are public in this repository. Every claim includes the test that produced it and the numbers behind it.

---

## Background

The Voynich Manuscript (MS 408, Yale Beinecke Library) is a 15th-century document written in an undeciphered script across 226 folios. It contains approximately 38,000 words using 25 distinct glyphs, alongside illustrations of unidentified plants, astronomical diagrams, and bathing figures. No one has produced an accepted decipherment in over a century of attempts.

In November 2025, Michael Greshko published the Naibbe cipher in *Cryptologia* — a historically plausible mechanism that encrypts Latin and Italian into text matching the manuscript's statistical profile. The Naibbe cipher does not decode the manuscript, but it demonstrates that the "cipher hypothesis" remains viable.

Brain-V builds on this foundation. Rather than proposing a single theory, it systematically tests competing hypotheses against the corpus statistics and eliminates those that fail.

---

## How Brain-V Works

Brain-V runs a cognitive loop:

1. **Perceive** — Parse the EVA transliteration of all 226 folios into structured data: words, glyphs, sections, Currier language classification (A/B).
2. **Hypothesise** — Generate testable claims about the manuscript's structure, encoding, and source language. Each hypothesis specifies what statistical test would confirm or deny it.
3. **Test** — Run the specified test against the corpus. 90 attacks per cycle, including frequency substitution, transposition, homophonic reduction, morphological stripping, section-comparative analysis, and combined multi-layer approaches.
4. **Score** — Evaluate results honestly. Measure frequency correlation to Latin and Italian reference profiles, dictionary hit rates, entropy, Index of Coincidence (IC), and Zipf's law fit.
5. **Update** — Promote hypotheses supported by evidence. Demote or eliminate those contradicted. Update the belief state.
6. **Repeat.**

Over 60 cycles, Brain-V generated 123 hypotheses, eliminated 18, and converged on 53 with confidence above 0.8. The system's surprise score (a measure of how much the world model changed per cycle) dropped from 0.087 to 0.023, indicating convergence.

---

## Finding 1: Honest Scoring Killed a False Positive

**The field needs this correction.**

Brain-V's initial word-level codebook attack scored 0.8701 against Latin — an apparently strong signal. The attack mapped high-frequency Voynich words to Latin equivalents and produced output containing recognisable Latin function words (*de*, *et*, *quod*, *medicina*).

On inspection, the scoring was dishonest. It excluded 64% of the text (unmapped words in brackets) from the dictionary hit calculation. When unmapped words were included in the score — as they must be, since a real decipherment must account for all text — the score dropped to **0.1894**.

**Honest score: 0.1894. Not 0.8701.**

This matters because partial-coverage attacks that ignore what they can't decode will always produce flattering numbers. Any claimed decipherment of the Voynich that reports accuracy only on the words it successfully maps should be treated with scepticism.

The medical Latin codebook variant scored 0.2753 with 50.8% coverage and 51.2% real dictionary hits — better, but still far from a decipherment.

---

## Finding 2: Systematic Morphological Structure

**37.3% vocabulary reduction from suffix stripping. This is real morphology.**

The Voynich Manuscript has an anomalously high hapax legomenon ratio — 70.1% of all word types appear only once. This has fuelled speculation that the text is meaningless or randomly generated. Brain-V tested the alternative: that the apparent vocabulary size is inflated by systematic suffixes.

Stripping word-final glyphs identified as probable suffixes (y, n, l, r, and multi-character sequences including dy, ey, in, ain, ol) reduced the unique vocabulary from 8,261 types to 5,181 — a **37.3% reduction**.

This is consistent across all sections of the manuscript. It is not an artefact of a single section or a small sample.

The suffix stripping also revealed that glyph **y** is not a letter in the cipher alphabet. It drops 7–10 percentage points in frequency in every section after stripping. It is overwhelmingly word-final. It functions as a grammatical marker — most likely an inflectional suffix in the source language — not a phoneme in the plaintext.

**Implication:** Previous frequency analyses that treated y as a cipher letter were working with a corrupted frequency distribution. Any substitution attack must strip morphological suffixes first.

---

## Finding 3: A Three-Layer Cipher Model

**This is why 600 years of single-layer attacks have failed.**

After suffix stripping, Brain-V measured the hapax ratio of the remaining stems. It barely changed — from 70.1% to 70.4%. The suffixes are real morphology, but the stems underneath are still overwhelmingly unique.

This means the encoding has (at least) three layers:

| Layer | What it does | Evidence |
|---|---|---|
| 1. Suffix morphology | Attaches grammatical markers (y/n/l/r/...) to stems | 37.3% vocabulary reduction on stripping |
| 2. Stem cipher | Substitution and/or transposition on the content words | High stem hapax ratio (70.4%), IC consistent with monoalphabetic substitution |
| 3. Natural language | Medieval Latin or northern Italian underneath | Zipf's law fit (R²=0.91), frequency correlation to Latin/Italian after stripping |

Every known decipherment attempt has attacked a single layer — either treating the text as a straight substitution cipher, or as a natural language, or as a codebook. None have addressed the layered structure.

The Naibbe cipher (Greshko, 2025) is compatible with this model. Its dice-and-card mechanism produces exactly this kind of layered output: natural language → substitution table → verbose encoding with positional structure.

---

## Finding 4: One Cipher, Not Many

**The biological section's substitution table transfers to all other sections with less than 5% loss.**

A persistent question in Voynich research is whether different sections use different encoding methods. Brain-V tested this by deriving a stem-level frequency substitution table from the biological section (the section with the strongest Latin signal after stripping) and applying it to every other section.

The cross-section transfer loss was below 5% in all cases. This means the entire manuscript — herbal, astronomical, biological, cosmological, pharmaceutical, recipes, and text-only sections — uses the **same underlying cipher on the stems**.

The Currier A/B language split (a well-established statistical difference between portions of the manuscript) is real — Brain-V confirmed it at 0.99 confidence across multiple tests — but it reflects different scribal hands or dialect variation, not different cipher systems.

---

## Finding 5: The Biological Section Is the Optimal Attack Surface

**IC = 0.100 after stripping. 340x improvement in Latin dictionary hits. This is where the cipher is thinnest.**

| Section | Latin Dict Hits (raw) | Latin Dict Hits (stems) | Improvement | IC (stems) |
|---|---|---|---|---|
| Biological | 0.02% | 6.81% | 340x | 0.100 |
| Text-only | 0.17% | 3.28% | 19x | 0.087 |
| Recipes | 0.37% | 3.09% | 8x | — |
| Herbal | 0.21% | 2.32% | 11x | — |

The biological section's IC of 0.100 after suffix stripping is above the natural language range (0.065–0.075 for Latin). This is consistent with a monoalphabetic substitution cipher on a restricted vocabulary — exactly what you would expect from a medical or anatomical text repeating body-part terminology and preparation instructions.

**The biological section is the Rosetta Stone.** If the stem cipher can be cracked anywhere, it will be cracked here first, and Finding 4 shows that solution will generalise to the rest of the manuscript.

---

## Finding 6: Stem Families Reveal Cipher Structure

**The word qo spawns qol, qotol, qotain, qopar — all sharing a root with systematic suffix variation.**

Stem analysis revealed consistent word families where a root glyph sequence appears with multiple different suffixes:

| Word | Stem | Maps to (freq. sub.) | Suffix |
|---|---|---|---|
| daly | dal | "ab" | y |
| olain | ol | "est" | ain |
| qol | qo | "os" | l |
| qotol | qo | "os" | tol |
| qotain | qo | "os" | tain |
| qopar | qo | "os" | par |

Additionally, high-frequency single-character words (d, r, o, l — each appearing 9 times in the text-only section) may be standalone function particles or abbreviated Latin terms (d for *de* or *dosis*, r for *recipe*).

This internal consistency — the same stems recurring with the same suffix patterns — is strong evidence against the "meaningless text" hypothesis and supports a natural language with real grammatical inflection underneath the cipher layers.

---

## What Brain-V Has Not Done

Brain-V has **not** deciphered the Voynich Manuscript.

It has not produced a reading of any folio. It has not identified the source language with certainty. It has not recovered the cipher key.

What it has done is:

- Identified and validated a morphological suffix system with quantitative evidence
- Proposed and tested a three-layer cipher model that explains why previous approaches failed
- Demonstrated that one cipher system underlies the entire manuscript
- Identified the biological section as the optimal attack surface
- Corrected a false positive in its own scoring and published the correction
- Completed 60 cycles of hypothesis generation, testing, and elimination — all logged, timestamped, and reproducible

The 49.2% of stems that remain unmapped after codebook and frequency substitution represent the frontier. Cracking the stem cipher is the next phase.

---

## Methodology and Reproducibility

All code is in this repository.

- `scripts/perceive.py` — Parses the EVA transliteration into structured data
- `scripts/predict.py` — Generates hypotheses via Claude Sonnet
- `scripts/score.py` — Tests hypotheses against corpus statistics via Claude Haiku
- `scripts/decrypt.py` — Runs 90 cipher attacks per cycle (pure Python, no LLM)
- `hypotheses/` — Every hypothesis file with confidence scores, evidence, and test history
- `outputs/scores/` — Every scoring cycle's full results
- `outputs/decryption/` — Every decryption attempt's full output
- `wiki/LOG.md` — Chronological log of all cycles, findings, and belief updates

The corpus is the standard EVA transliteration of MS 408, publicly available. Reference frequency profiles for medieval Latin and Italian are included in `raw/corpus/reference-profiles/`.

Brain-V uses Claude Sonnet for hypothesis generation and Claude Haiku for scoring evaluation. The decryption engine (`decrypt.py`) is pure Python — no LLM in the attack loop. All statistical tests are deterministic and reproducible.

---

## Architecture

Brain-V is a fork of [Project Brain](https://github.com/BuilderBenv1/project-brain), a persistent cognitive architecture built by Ben Maybury. Project Brain runs a daily perceive-predict-score loop on arXiv cs.AI papers, with beliefs persisted on-chain via AgentOS. Brain-V duplicates that architecture and retargets it at the Voynich Manuscript.

Both systems run on [AgentProof](https://agentproof.sh) infrastructure — ERC-8004 compliant reputation and trust scoring for autonomous AI agents. Brain-V's agents are registered on SKALE (zero gas fees, enabling aggressive cycling). Every hypothesis, every cycle log, and every belief update is anchored to IPFS with on-chain timestamps.

The cognitive loop — perceive, hypothesise, test, score, update, repeat — is the core innovation. Brain-V doesn't apply a single theory and check if it works. It maintains a population of competing theories, tests them against evidence, eliminates failures, and compounds its knowledge over time.

---

## What Comes Next

1. **Crack the stem cipher on the biological section.** IC of 0.100 and 6.81% Latin dictionary hits after stripping suggest a monoalphabetic substitution. Focused hill-climbing on the stem substitution table with biological/medical Latin vocabulary constraints.

2. **Cross-validate against the Naibbe cipher.** Greshko's mechanism produces layered output compatible with Brain-V's three-layer model. Testing whether the Naibbe cipher's specific structure matches Brain-V's observed suffix and stem patterns.

3. **Community hypothesis intake.** Submit theories as GitHub Issues. Brain-V will test them using the same methodology and publish results. Every hypothesis gets the same treatment — honest scoring, full evidence chain, public results.

4. **Deeper Currier A/B analysis.** The universal substitution table transfers across sections, but A/B show measurable differences. Are these dialectal? Different hands with different suffix preferences? Different source texts?

---

## Contributing

If you have a hypothesis about the Voynich Manuscript, open a GitHub Issue with:

- **Claim** — plain English statement of what you believe is true
- **Type** — cipher / language / structural / null hypothesis
- **Test** — what statistical test would confirm or deny it

Brain-V will add it to the hypothesis pool and test it in the next cycle batch. Results will be posted back to the issue.

---

## Contact

Built by Ben Maybury ([@AgentProof](https://x.com/AgentProof_sh)) using the Project Brain cognitive architecture.

Brain-V is part of the [AgentProof](https://agentproof.sh) ecosystem — trust scoring infrastructure for autonomous AI agents.

---

*Brain-V's first thought was about a 600-year-old mystery. Everything it found is here. Verify it, challenge it, extend it.*
