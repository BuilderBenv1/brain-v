# kpagel — Trilingual Pharmaceutical Hypothesis

**Source:** Pagel, K. (2026) "Deciphering the Voynich Manuscript: A Trilingual Pharmaceutical Compendium in Medieval Abbreviation." Zenodo DOI 10.5281/zenodo.18478526

**Status:** Tested by Brain-V on 2026-04-14. Major discrepancies found.

## Claims vs Brain-V Verification

### Coverage
- **Pagel claims:** 96% text coverage at >=50% confidence with 81 terms
- **Brain-V finds:** 23.8% token coverage with 56 terms matching EVA corpus
- **Discrepancy:** 4x overclaim. 76.2% of tokens unmatched.

### Occurrence Counts
| EVA word | Pagel claims | Actual (EVA corpus) | Discrepancy |
|---|---|---|---|
| daiin | 1,247 | 799 | +56% overcounted |
| chedy | 892 | 501 | +78% overcounted |
| dam | 558 | 80 | +598% overcounted |
| sam | 245 | 12 | +1942% overcounted |
| chom | 156 | 14 | +1014% overcounted |
| otal | 362 | 129 | +181% overcounted |
| ol | 489 | 553 | -12% (only accurate one) |

**Pagel's counts are systematically inflated**, especially for Hebrew terms (dam, sam, chom). This suggests substring matching rather than exact word matching — e.g., counting "dam" inside "daiin" and "odam" and "damy".

### Hapax Ratio
- **Pagel claims:** 43.2%
- **Brain-V measures:** 70.1%
- **This is not reconcilable.** The EVA corpus has 70.1% hapax. Pagel may be measuring a transformed version of the corpus or counting differently.

### Collocations
- **Pagel claims:** daiin-sar PMI = 2.9 (high significance)
- **Brain-V finds:** daiin followed by sar = 1 time (0.6x expected by chance)
- **The claimed collocation does not exist at the claimed strength.**

### Statistical Tests
- Character entropy: Pagel 4.02 vs Brain-V 3.86 — close but not matching
- Zipf exponent: Pagel 0.72 vs Brain-V 0.89 — different corpus or method
- 3 dictionary terms not found in EVA corpus at all: bar, lach, darchiin

## Dictionary (57 terms verified in corpus)

### 100% Confidence (12 terms, Pagel)
| EVA | Meaning | Language | Pagel count | Actual |
|---|---|---|---|---|
| daiin | is given (datur) | Latin | 1,247 | 799 |
| chedy | warm (calidus) | Latin | 892 | 501 |
| chol | leaf (folium) | Latin | 723 | 380 |
| shedy | dry (siccus) | Latin | 634 | 431 |
| dam | blood / Give! | Hebrew/Latin | 558 | 80 |
| ol | oil (oleum) | Latin | 489 | 553 |
| otal | star (stella) | Latin | 362 | 129 |
| or | skin | Hebrew | 312 | 378 |
| sam | medicine | Hebrew | 245 | 12 |
| sal | salt | Latin | 178 | 48 |
| chom | heat | Hebrew | 156 | 14 |
| kor | cold | Hebrew | 134 | 26 |

### 95% Confidence (12 terms)
| EVA | Meaning | Language |
|---|---|---|
| sar | to heal (sanare) | Latin |
| chor | flower (flos) | Latin |
| y | and (et) | Latin |
| sho | Take! (sume) | Latin |
| qokain | by which heat | Latin |
| qokeey | with which heat | Latin |
| otar | stars (pl.) | Latin |
| oteey | of the star | Latin |
| dain | was given (datum) | Latin |
| kal | warmth (calor) | Latin |
| rar | root (radix) | Latin |

### 85-94% Confidence (14 terms)
ar (air), al (other), shol (sun), cheol (warm leaf), cheor (warm flower), s (is), dan (to be given), shy (dry-), qokedy (which warm), lchedy (lukewarm), keol (heat-oil), qol (which oil), qokor (which cold), otedy (hot star)

### 70-84% Confidence (19 terms)
bar* (cold/Arabic), lach* (moist/Hebrew), chey (with), shey (thus), chy (because), sheol (sub-oil), por (for), teody (lukewarm), oky (affliction), kchy (thorny), saiin (heal-indeed), cholaiin (leaf-indeed), qoky (also), chckhy (cooked), shekar (sugar/Arabic), darchiin* (cinnamon/Arabic), qokal (alkali/Arabic), aiindy (thence), dago (therefore)

*Not found in EVA corpus

## Brain-V Assessment

**H106 confidence: 0.20** (downgraded from 0.35)

The pharmaceutical interpretation is plausible in principle — Brain-V independently found medical context signals. But Pagel's specific claims have serious verification failures:

1. **Token coverage is 23.8%, not 96%.** This is the most critical failure.
2. **Occurrence counts are systematically inflated** — likely from substring matching.
3. **Key collocations don't verify** (daiin-sar: 1 occurrence vs claimed high PMI).
4. **Hapax ratio discrepancy** (43.2% vs 70.1%) suggests different corpus or methodology.

The individual word meanings (daiin = datur, chedy = calidus, etc.) may still have merit as a partial mapping, but the statistical claims attached to them do not hold up against the standard EVA transliteration.
