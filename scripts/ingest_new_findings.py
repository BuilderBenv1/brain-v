"""
Ingest the findings from the 4-parallel-tests cycle as hypotheses +
belief updates.

Six new hypotheses:
  H-BV-NULL-01  Coverage >=80% is a null floor, not evidence
  H-BV-VOWEL-01 EVA vowels encode section-linked info at p<0.01 in 79% of groups
  H-BV-Q-01     EVA 'q' is a categorical word-initial marker (98.9%)
  H-BV-MG-01    EVA 'm'/'g' are suffix markers (extending H023 class)
  H-BV-AB-01    Currier A structurally resists lexical decipherment
  H-BV-SHUF-01  Word-order syntactic signal absent across all tested lexicons

Belief updates:
  - Downgrade "A=B same language, different scribes" cluster
  - Upgrade "vowels are meaningful (not noise)"
  - Add "coverage alone is insufficient for decipherment"
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
HYP = ROOT / "hypotheses"
BELIEFS = ROOT / "scripts" / "beliefs.json"

today = str(date.today())

def mk(hid, claim, typ, conf, ef, ea, test, metric, thresh, reasoning,
       source="Brain-V 2026-04-15 four-parallel-tests cycle"):
    return {
        "id": hid, "claim": claim, "type": typ, "confidence": conf,
        "evidence_for": ef, "evidence_against": ea,
        "test": test, "test_metric": metric, "test_threshold": thresh,
        "tests_run": [{
            "date": today, "test": test, "score": conf,
            "passed": True if conf >= 0.5 else None,
            "details": reasoning, "confidence_change": f"initial {conf:.2f}"
        }],
        "tests_remaining": [], "status": "active", "parent": None,
        "created": today, "last_tested": today,
        "reasoning": reasoning, "source": source, "researcher": "brain-v",
    }

HYPS = [
    mk("H-BV-NULL-01",
       "Coverage >=80% on the Voynich corpus is achievable by 1,300 phonotactically plausible nonsense skeletons (20-trial mean 83.56%, sigma 1.03pp) and therefore cannot, alone, be evidence of decipherment. Any abjad-reducible lexicon of 1,000-4,000 entries matching corpus word-length and bigram distributions clears this floor by construction.",
       "null", 0.92,
       ["20-trial null test: 83.56% +/- 1.03pp coverage from bigram-Markov nonsense",
        "Brady Syriac (86.9%) only +3.3pp above null floor",
        "Schechter Latin (82.81%) is 0.75pp BELOW null floor",
        "Hebrew medieval (57.9%) is 25.6pp below null floor - only genuine outlier"],
       ["Brady's character-permutation z=3.83 is a different null (alphabet-mapping, not key-selection) and survives this critique on its own terms",
        "Null floor depends on corpus bigram statistics - a non-abjad or different-length lexicon may show different floors"],
       "Confirmed by four-parallel-tests.py; retest on any future lexicon claim by running the same 20-trial bigram-Markov null",
       "null_floor_coverage",
       "New lexicon claims must report z-score against corpus-derived null, not just raw coverage",
       "Publishable negative result. Challenges every coverage-based Voynich decipherment claim in the literature. Validated with 20 independent trials on 1,300-skeleton nonsense lexicons."),

    mk("H-BV-VOWEL-01",
       "EVA vowel choice within a fixed consonant skeleton is section-linked. Across 70 skeleton groups with >=3 vowel variants and >=100 tokens each, 55 (78.6%) show section-distribution chi-square significant at p<0.01. Headline case 'kdy' (Brady's chedy/chody): chi2=262.17, df=28, critical 50.89, i.e. 5.15x over threshold.",
       "structural", 0.90,
       ["55/70 skeleton groups significant at p<0.01",
        "Top-5 couplings exceed critical value by 4.88-8.51x",
        "Independent verification of Brady 2026 section 3.10 claim",
        "chedy (501 tokens): biological/recipes dominant; chody (88 tokens): herbal-exclusive",
        "Signal is language-independent - tests distribution, not identity"],
       ["Section-coupling could reflect topical/domain vocabulary differences rather than a genuine vowel-encoding layer",
        "Variants may cluster due to scribal preferences in different production phases, not semantic content"],
       "Chi-square test on all skeleton groups meeting size thresholds",
       "vowel_section_chi_square_p01_rate",
       ">=50% of testable skeletons significant at p<0.01: confirmed. Current result 78.6%.",
       "Strongest positive structural finding of the session. EVA vowels are not padding - they carry information the rest of the decipherment effort has been throwing away."),

    mk("H-BV-Q-01",
       "EVA 'q' is a categorical word-initial marker, appearing word-initial in 98.9% of its 5,416 corpus occurrences. This is the strongest positional constraint of any EVA glyph, supporting Brady's H-BRADY-03 (q maps to Syriac waw / wa- conjunction) as a structural claim independent of language identification.",
       "structural", 0.92,
       ["98.9% initial position rate across 5,416 occurrences",
        "Strongest positional asymmetry of any EVA glyph",
        "Compatible with Brady's q -> wa- (Syriac conjunction) hypothesis",
        "Also compatible with Latin/Italian conjunction or article marker"],
       ["Position constraint doesn't specify phonetic value",
        "Same pattern could arise from several unrelated grammatical roles"],
       "Positional distribution computable from corpus directly",
       "q_initial_rate",
       ">=95% initial: confirmed. Current 98.9%.",
       "Very strong positional signal. Future decipherment attempts should treat 'q' as a structural prefix/marker, not as a free phonetic consonant."),

    mk("H-BV-MG-01",
       "EVA 'm' (1,055 tokens) and 'g' (127 tokens) are suffix/final-marker glyphs, extending the suffix class beyond {y,n,l,r} per H023. Final-position rates: m 93.6%, g 83.5%. EVA 'l' (previously assumed final-dominant) is actually balanced (53.6% final / 32.6% mid) and should be demoted from the suffix class.",
       "structural", 0.85,
       ["m at 93.6% word-final across 1,055 occurrences",
        "g at 83.5% word-final across 127 occurrences",
        "n at 97.0% final, y at 84.3% final, r at 74.4% final (previously known)",
        "l at 53.6% final is a mis-assignment in H023"],
       ["g's sample size (127) is modest; rate could shift with more data",
        "Suffix class membership is a surface feature, not guaranteed to be grammatical suffixes"],
       "Positional counts from corpus",
       "m_g_final_rates",
       "m >=90% final AND g >=80% final: confirmed",
       "Expands H023 suffix class to {y,n,r,m,g}; demotes l. Any stem-stripping pipeline should be updated."),

    mk("H-BV-AB-01",
       "Currier A is structurally distinct from Currier B at the lexical-accessibility level, resisting decipherment across three independent language hypotheses: Schechter Latin (B-A gap +8.21pp), Brady Syriac proxy (+3.92pp), Hebrew medieval (+3.07pp). B consistently fits lexicons better than A by 3-8 percentage points regardless of source language.",
       "structural", 0.80,
       ["Three independent methodologies, three language families, same B>A direction",
        "Gap magnitudes vary but direction is invariant",
        "Cannot be lexicon-bias since lexicons are unrelated",
        "Challenges Brain-V's own A=B same-language cluster (H004, H021, H025 etc. at >=0.95)"],
       ["Gaps could still reflect sample bias - bio/recipes B-dominant sections may be over-represented in pharma vocab sources",
        "Need a full-Brady-lexicon retest to confirm direction with stronger statistics"],
       "Compute coverage by Currier language under each lexicon",
       "ab_gap_direction",
       "Sign consistent across >=2 independent lexicons: supported",
       "Brain-V's high-confidence A=B hypotheses made a testable prediction (equal lexical fit) and it failed on 3 independent tests. This hypothesis is the replacement."),

    mk("H-BV-SHUF-01",
       "Word-order syntactic structure is absent from Voynichese. Across all tested lexicons (Schechter Latin, Brady Syriac proxy, Hebrew medieval, Brain-V v1), in-order decoded text scores equal to or LOWER than across-corpus-shuffled decoded text on the connector-to-content bigram metric. Both-matched-adjacency shows a small positive cluster effect (+0.003 to +0.028 pp) that is lexicon-size-monotonic and therefore a topical-clustering artefact, not grammatical signal.",
       "null", 0.85,
       ["Schechter Latin: in-order conh -0.003, shuffle test failure",
        "Brady Syriac proxy: conn_content -0.0098 in-order vs shuffled",
        "Hebrew medieval: conn_content -0.0144 in-order vs shuffled",
        "Brain-V v1 dict: conn_content -0.0321 in-order vs shuffled",
        "Four independent lexicons, identical qualitative failure"],
       ["Full Brady lexicon may change the picture once supplementary file is released",
        "Shuffle test is defined at line level; some longer-range structure could survive"],
       "Standard coherence metrics (connector-content bigrams, match adjacency) with seeded random shuffle baseline",
       "shuffle_conn_content_delta",
       "Positive and >=+0.01 in-order vs shuffled on connector-to-content metric: syntactic signal present",
       "The fundamental barrier to Voynich decipherment. Coverage-based methods find words but not sentences. Future work needs order-independent signals (vowel layer, glyph-role, section-structure) rather than pursuing more lexicons."),
]

# Write hypothesis files
for h in HYPS:
    p = HYP / f"{h['id']}.json"
    p.write_text(json.dumps(h, indent=2), encoding="utf-8")
    print(f"  wrote {p.name}")

# Belief updates
beliefs = json.loads(BELIEFS.read_text(encoding="utf-8"))

def find(substr):
    for i, b in enumerate(beliefs):
        if substr.lower() in b["belief"].lower():
            return i
    return None

def upd(idx, new_conf, reason):
    b = beliefs[idx]
    old = b["confidence"]
    b["confidence"] = new_conf
    b["last_scored"] = today
    b["fix_reason"] = f"{today}: {old:.2f} -> {new_conf:.2f} — {reason}"
    print(f"  updated [{idx}] {b['belief'][:60]}  {old:.2f} -> {new_conf:.2f}")

def add(belief, conf, evidence):
    beliefs.append({
        "belief": belief, "confidence": conf, "source": "brain-v",
        "date": today, "evidence": evidence, "last_scored": today,
    })
    print(f"  added: {belief[:70]}  ({conf:.2f})")

# Downgrade A=B same-language (if present)
idx = find("same language")
if idx is not None:
    upd(idx, max(0.35, beliefs[idx]["confidence"] - 0.25),
        "3-lexicon test shows B>A gap 3-8pp across Latin/Syriac/Hebrew; A=B equal-fit prediction failed")

# Upgrade vowel-meaningful (or add)
idx = find("vowel")
if idx is not None:
    upd(idx, 0.90,
        "55/70 skeleton groups section-coupled at p<0.01; chedy/chody case 5.15x over threshold")
else:
    add("EVA vowel choice within a fixed consonant skeleton encodes section-linked information (Brady H-BRADY-05 verified)",
        0.90, "55/70 skeleton groups significant at p<0.01; kdy case chi2=262 vs crit 50.9")

# Add coverage-alone-insufficient belief
idx = find("coverage alone")
if idx is None:
    add("Token coverage alone is insufficient for Voynich decipherment: the null floor from 1,300 bigram-Markov nonsense skeletons is 83.56% (+/- 1pp), above Schechter and within 3pp of Brady",
        0.92, "20-trial null lexicon test; Brady +3.3pp above null, Schechter -0.75pp below null")

# Add word-order-absent belief
idx = find("word-order") or find("shuffle")
if idx is None:
    add("Word-order syntactic structure is not recoverable by lexicon substitution: all 4 tested lexicons (Schechter, Brady, Hebrew, Brain-V v1) fail the shuffle test on connector-to-content bigrams",
        0.85, "4-lexicon shuffle test; conn_content deltas range -0.003 to -0.032 in-order vs shuffled")

# Add gallows-marker belief
idx = find("gallows")
if idx is None:
    add("Plain EVA gallows 't' and 'p' function as line-initial paragraph markers (H-BRADY-02): p at 5.0x line-initial enrichment, t at 2.8x, bench gallows cth/ckh/cph at <0.5x",
        0.90, "Brain-V independent verification of Brady 2026 section 3.5")

# Upgrade/add q-initial-marker
idx = find("q ") or find("q-")
if idx is None:
    add("EVA 'q' is a categorical word-initial marker at 98.9% word-initial frequency (n=5,416), the strongest positional constraint of any EVA glyph",
        0.92, "four-parallel-tests.py glyph positional analysis")

# Persist
BELIEFS.write_text(json.dumps(beliefs, indent=2, ensure_ascii=False),
                   encoding="utf-8")
print(f"\n{len(beliefs)} beliefs total in {BELIEFS.name}")
print(f"{len(HYPS)} hypotheses written")
