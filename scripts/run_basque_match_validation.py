"""
Execute pre-registered H-BV-BASQUE-MATCH-VALIDATION-01.

Four sub-tests stress-testing the BASQUE_UNIQUELY_BEST verdict from
H-BV-AGGLUTINATIVE-EXPANSION-01.

  S1 Provenance audit (reflective)
  S2 Sensitivity: 20% Basque range narrowing
  S3 Alternative operationalisations (V1, V3, V5)
  S4 Direct UD_Basque corpus measurement (M1 + optional M3)
"""
import json
import statistics
import urllib.request
import urllib.error
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI = sorted(["cth", "cph", "ckh", "cfh", "ch", "sh", "ee"], key=lambda s: -len(s))

HAND_A_LOCKED = {"M1": 4.12, "M2_L1": 10, "M2_L2": 5, "M3": 3.16, "M4": 0.20, "M5": 1.00}

CANDIDATES = {
    "Basque":     {"M1": (2.5, 4.5),  "M2_L1": (8, 16),    "M2_L2": (3, 8),  "M3": (2.0, 5.0),  "M4": (0.02, 0.20), "M5": (0.60, 1.00)},
    "Georgian":   {"M1": (2.0, 4.0),  "M2_L1": (10, 20),   "M2_L2": (4, 10), "M3": (2.0, 4.5),  "M4": (0.10, 0.30), "M5": (0.70, 0.95)},
    "Swahili":    {"M1": (3.0, 5.5),  "M2_L1": (6, 12),    "M2_L2": (8, 16), "M3": (2.5, 5.0),  "M4": (0.05, 0.20), "M5": (0.85, 1.00)},
    "Tagalog":    {"M1": (1.8, 3.2),  "M2_L1": (15, 30),   "M2_L2": (2, 6),  "M3": (1.5, 3.5),  "M4": (0.25, 0.55), "M5": (0.40, 0.70)},
    "Mapudungun": {"M1": (3.0, 6.0),  "M2_L1": (20, 40),   "M2_L2": (6, 14), "M3": (2.0, 5.0),  "M4": (0.30, 0.60), "M5": (0.55, 0.80)},
    "Ainu":       {"M1": (2.5, 5.0),  "M2_L1": (12, 25),   "M2_L2": (4, 10), "M3": (2.0, 4.5),  "M4": (0.20, 0.50), "M5": (0.50, 0.80)},
    "Inuktitut":  {"M1": (4.0, 8.0),  "M2_L1": (300, 500), "M2_L2": (6, 14), "M3": (3.0, 7.0),  "M4": (0.60, 0.90), "M5": (0.75, 0.95)},
}

METRICS = ["M1", "M2_L1", "M2_L2", "M3", "M4", "M5"]


def dist(v, rng):
    lo, hi = rng
    w = hi - lo
    if lo <= v <= hi:
        return 0.0, True
    return min(abs(v - lo), abs(v - hi)) / w if w > 0 else (abs(v - lo), False), False


def profile_distance(hand_a, candidates):
    results = []
    for lang, profile in candidates.items():
        total = 0.0
        matches = 0
        per_m = {}
        for m in METRICS:
            d, in_range = dist(hand_a[m], profile[m])
            per_m[m] = {"v": hand_a[m], "range": profile[m], "d": round(d if isinstance(d, float) else d[0], 4), "in_range": in_range}
            total += d if isinstance(d, float) else d[0]
            if in_range:
                matches += 1
        results.append({"language": lang, "distance": round(total, 4), "matches": matches, "per_metric": per_m})
    results.sort(key=lambda r: r["distance"])
    return results


def margin(results):
    d1, d2 = results[0]["distance"], results[1]["distance"]
    if d1 == 0.0 and d2 > 0.0:
        return float("inf")
    if d1 == 0.0:
        return 1.0
    return d2 / d1


print("=" * 70)
print("S1 PROVENANCE AUDIT")
print("=" * 70)
s1_per_metric = {
    "M1":    {"primary_sources": ["Hualde & Ortiz de Urbina 2003", "de Rijk 2008"], "methodology_alignment": "approximate — Brain-V M1 is mean glyph-units/word; published sources give mean morphemes/word qualitatively", "timing": "literature-derived; locked in H-BV-AGGLUTINATIVE-SCREEN-01 on 2026-04-17 SAME SESSION as Hand A measurement"},
    "M2_L1": {"primary_sources": ["Hualde & Ortiz de Urbina 2003"], "methodology_alignment": "derived from Basque case-marker + clitic count (~12 core case + peripherals); Brain-V M2 is top-K inventory at position N-2; not identical but both are bounded productive inventories", "timing": "same session"},
    "M2_L2": {"primary_sources": ["Hualde & Ortiz de Urbina 2003"], "methodology_alignment": "derived from peripheral clitic/particle count; Brain-V L2 is top-5 outer glyphs; approximate alignment", "timing": "same session"},
    "M3":    {"primary_sources": ["Hualde & Ortiz de Urbina 2003", "de Rijk 2008"], "methodology_alignment": "derived from 'nominal stems take 3-4 case forms'; Brain-V M3 is distinct inners/productive stem; conceptually aligned", "timing": "same session"},
    "M4":    {"primary_sources": ["Hualde & Ortiz de Urbina 2003"], "methodology_alignment": "derived from 'animacy-based categorical constraints'; Brain-V M4 is zero-cells in top-K x top-K paradigm; indirect derivation", "timing": "same session"},
    "M5":    {"primary_sources": ["Hualde & Ortiz de Urbina 2003"], "methodology_alignment": "derived from 'strictly slot-ordered' qualitative description; Brain-V M5 is 3x asymmetry fraction; qualitative-to-quantitative approximation", "timing": "same session"},
}
for m, info in s1_per_metric.items():
    print(f"  {m:7s}: sources={len(info['primary_sources'])}  alignment={info['methodology_alignment'][:60]}...")
s1_contemporaneous_all = all("same session" in info["timing"] for info in s1_per_metric.values())
s1_single_source_count = sum(1 for info in s1_per_metric.values() if len(info["primary_sources"]) == 1)
print(f"\n  All ranges locked in same session as Hand A measurement: {s1_contemporaneous_all}")
print(f"  Sub-metrics with single-source derivation: {s1_single_source_count}/6")
if s1_contemporaneous_all:
    s1_status = "FAIL"
    s1_note = "Contemporaneous derivation: ranges locked same-session as Hand A values. Strict pre-registration discipline requires prior locking. Fails S1."
elif s1_single_source_count > 3:
    s1_status = "PARTIAL"
    s1_note = "Mixed: most ranges are single-source derivations, but the prior Basque locks provide some prior-art anchoring."
else:
    s1_status = "PASS"
    s1_note = "Multi-source, methodology-aligned, and temporally prior."
print(f"  S1 VERDICT: {s1_status}")
print(f"  S1 NOTE: {s1_note}")

print("\n" + "=" * 70)
print("S2 SENSITIVITY (20% Basque range narrowing)")
print("=" * 70)
basque_narrowed = {}
for m in METRICS:
    lo, hi = CANDIDATES["Basque"][m]
    midpoint = (lo + hi) / 2
    half_width = (hi - lo) / 2
    new_half = half_width * 0.8
    basque_narrowed[m] = (midpoint - new_half, midpoint + new_half)
    print(f"  {m:7s}: {CANDIDATES['Basque'][m]} -> ({basque_narrowed[m][0]:.4f}, {basque_narrowed[m][1]:.4f})")

narrowed_candidates = dict(CANDIDATES)
narrowed_candidates["Basque"] = basque_narrowed
s2_results = profile_distance(HAND_A_LOCKED, narrowed_candidates)
s2_margin = margin(s2_results)

print(f"\n  Under 20%-narrowed Basque ranges:")
for i, r in enumerate(s2_results[:3], 1):
    print(f"    rank {i}: {r['language']:<12} distance={r['distance']:.4f}  matches={r['matches']}/6")
print(f"  margin (rank 2 / rank 1): {'infinity' if s2_margin == float('inf') else f'{s2_margin:.4f}'}")

if s2_results[0]["language"] == "Basque":
    if s2_margin == float("inf") or s2_margin >= 1.10:
        s2_status = "PASS"
    else:
        s2_status = "PARTIAL"
else:
    s2_status = "FAIL"
print(f"  S2 VERDICT: {s2_status}")

print("\n" + "=" * 70)
print("S3 ALTERNATIVE OPERATIONALISATIONS")
print("=" * 70)


def tokenize(word):
    out = []
    i = 0
    while i < len(word):
        matched = False
        for t in MULTI:
            if word.startswith(t, i):
                out.append(t)
                i += len(t)
                matched = True
                break
        if not matched:
            out.append(word[i])
            i += 1
    return out


hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") == "A":
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    hand_a_words.append(w)

v1_mean_char = statistics.mean(len(w) for w in hand_a_words)
print(f"  V1 M1 raw-char mean: {v1_mean_char:.4f}  (baseline tokenised glyph-unit mean: 4.12)")

tokenised_A = [tokenize(w) for w in hand_a_words]
valid_N3 = [t for t in tokenised_A if len(t) >= 3]
stems_counter_p3 = Counter(tuple(t[:-2]) for t in valid_N3)
productive_p3 = [s for s, c in stems_counter_p3.items() if c >= 3]
productive_p5 = [s for s, c in stems_counter_p3.items() if c >= 5]

inner_counts_per_stem_p5 = defaultdict(set)
for t in valid_N3:
    stem = tuple(t[:-2])
    inner = t[-2]
    if stems_counter_p3.get(stem, 0) >= 5:
        inner_counts_per_stem_p5[stem].add(inner)
v3_m3 = statistics.mean(len(v) for v in inner_counts_per_stem_p5.values()) if inner_counts_per_stem_p5 else 0.0
print(f"  V3 M3 (productivity threshold >=5): {v3_m3:.4f}  (baseline >=3: 3.16)")

VOWEL_INNERS = {"i", "e", "o", "a"}
CONSONANT_INNERS = {"ch", "d", "k", "t", "sh", "l"}
TOP5_OUTERS = {"y", "n", "r", "ol", "l"}

vowel_outer_counts = defaultdict(int)
cons_outer_counts = defaultdict(int)
for t in valid_N3:
    inner = t[-2]
    outer = t[-1]
    if inner in VOWEL_INNERS:
        vowel_outer_counts[outer] += 1
    elif inner in CONSONANT_INNERS:
        cons_outer_counts[outer] += 1

total_v = sum(vowel_outer_counts.values())
total_c = sum(cons_outer_counts.values())
v5_asym_2x = 0
for o in TOP5_OUTERS:
    pv = vowel_outer_counts.get(o, 0) / total_v if total_v else 0
    pc = cons_outer_counts.get(o, 0) / total_c if total_c else 0
    if pv > 0 and pc > 0:
        ratio = max(pv / pc, pc / pv)
    elif pv > 0 or pc > 0:
        ratio = float("inf")
    else:
        ratio = 1.0
    if ratio >= 2.0:
        v5_asym_2x += 1
v5_m5 = v5_asym_2x / 5
print(f"  V5 M5 (asymmetry >=2x instead of >=3x): {v5_m5:.4f}  (baseline >=3x: 1.00)")


def variant_check(variant_name, override_field, override_value):
    hand_a_v = dict(HAND_A_LOCKED)
    hand_a_v[override_field] = override_value
    res = profile_distance(hand_a_v, CANDIDATES)
    m = margin(res)
    return {"variant": variant_name, "override_field": override_field, "override_value": override_value, "top3": res[:3], "margin": m}


variants = [
    variant_check("V1 M1 raw char length", "M1", round(v1_mean_char, 4)),
    variant_check("V3 M3 productivity >=5", "M3", round(v3_m3, 4)),
    variant_check("V5 M5 asymmetry >=2x", "M5", round(v5_m5, 4)),
]

s3_pass_count = 0
s3_details = []
for v in variants:
    r1 = v["top3"][0]
    s3_margin_pass = r1["language"] == "Basque" and (v["margin"] == float("inf") or v["margin"] >= 1.10)
    s3_basque_first = r1["language"] == "Basque"
    pass_str = "PASS" if s3_margin_pass else ("PARTIAL" if s3_basque_first else "FAIL")
    if s3_margin_pass:
        s3_pass_count += 1
    elif s3_basque_first:
        s3_pass_count += 0.5
    m_str = "inf" if v["margin"] == float("inf") else f"{v['margin']:.4f}"
    print(f"  {v['variant']}: Hand A {v['override_field']} = {v['override_value']}")
    print(f"    rank1={r1['language']} d={r1['distance']:.4f}  rank2={v['top3'][1]['language']} d={v['top3'][1]['distance']:.4f}  margin={m_str}  {pass_str}")
    s3_details.append({"variant": v["variant"], "override": f"{v['override_field']}={v['override_value']}", "rank1": r1["language"], "rank1_d": r1["distance"], "rank2": v["top3"][1]["language"], "rank2_d": v["top3"][1]["distance"], "margin": str(v["margin"]), "verdict": pass_str})

if s3_pass_count >= 3:
    s3_status = "PASS"
elif s3_pass_count >= 2:
    s3_status = "PARTIAL"
else:
    s3_status = "FAIL"
print(f"  S3 pass_count = {s3_pass_count}/3  VERDICT: {s3_status}")

print("\n" + "=" * 70)
print("S4 DIRECT UD_BASQUE CORPUS COMPARISON")
print("=" * 70)

UD_URL = "https://raw.githubusercontent.com/UniversalDependencies/UD_Basque-BDT/master/eu_bdt-ud-train.conllu"
s4_ud_file = ROOT / "raw" / "corpus" / "reference-corpora" / "eu_bdt-ud-train.conllu"

if not s4_ud_file.exists():
    s4_ud_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        print(f"  Downloading UD_Basque-BDT train file...")
        with urllib.request.urlopen(UD_URL, timeout=30) as resp:
            data = resp.read()
        s4_ud_file.write_bytes(data)
        print(f"  Saved: {s4_ud_file}  ({len(data)} bytes)")
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"  Download FAILED: {e}")
        s4_ud_file = None


def parse_conllu_metrics(conllu_path):
    features_per_word = []
    pos_tags = []
    lemmas_per_pos = defaultdict(Counter)
    inflected_forms_per_lemma = defaultdict(set)

    with open(conllu_path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 8:
                continue
            if "-" in parts[0] or "." in parts[0]:
                continue
            form, lemma, upos, feats = parts[1], parts[2], parts[3], parts[5]
            pos_tags.append(upos)
            if upos in {"NOUN", "VERB", "ADJ", "PROPN"}:
                feat_count = 1
                if feats and feats != "_":
                    feat_count = 1 + len([f for f in feats.split("|") if f])
                features_per_word.append(feat_count)
                inflected_forms_per_lemma[(lemma, upos)].add(form)
    return features_per_word, pos_tags, inflected_forms_per_lemma


if s4_ud_file and s4_ud_file.exists():
    features, pos_tags, inflections = parse_conllu_metrics(s4_ud_file)
    if features:
        m1_mean = statistics.mean(features)
        m1_median = statistics.median(features)
        m1_p10 = sorted(features)[int(0.1 * len(features))]
        m1_p90 = sorted(features)[int(0.9 * len(features))]
        print(f"  UD_Basque M1 measured (mean morphemes per content word): {m1_mean:.4f}")
        print(f"    median={m1_median:.1f}  p10={m1_p10}  p90={m1_p90}  n_content_words={len(features)}")
        print(f"  Published range used in EXPANSION-01: [2.5, 4.5]")
        print(f"  Is measured mean in published range? {2.5 <= m1_mean <= 4.5}")
        print(f"  Is Hand A 4.12 in UD_Basque p10-p90 range [{m1_p10}, {m1_p90}]? {m1_p10 <= 4.12 <= m1_p90}")

        productive = [(l, count) for (l, _), count in {(lp, pos): len(forms) for (lp, pos), forms in inflections.items()}.items() if count >= 3]
        all_productive_counts = [count for (l, count) in productive]
        if all_productive_counts:
            m3_mean = statistics.mean(all_productive_counts)
            print(f"  UD_Basque M3 measured (distinct forms per productive lemma): {m3_mean:.4f}")
            print(f"    n_productive_lemmas={len(all_productive_counts)}")
            print(f"  Published range used: [2.0, 5.0]")
            print(f"  Is measured M3 in published range? {2.0 <= m3_mean <= 5.0}")
        else:
            m3_mean = None

        s4_m1_in_range = 2.5 <= m1_mean <= 4.5
        s4_hand_a_in_measured = m1_p10 <= 4.12 <= m1_p90
        if s4_m1_in_range and s4_hand_a_in_measured:
            s4_status = "PASS"
            s4_note = f"Measured M1 {m1_mean:.3f} in [2.5, 4.5]; Hand A 4.12 in UD_Basque p10-p90 [{m1_p10}, {m1_p90}]."
        elif s4_m1_in_range:
            s4_status = "PARTIAL"
            s4_note = f"Measured M1 in range; Hand A 4.12 at/outside central distribution [{m1_p10}, {m1_p90}]."
        else:
            s4_status = "FAIL"
            s4_note = f"Measured M1 {m1_mean:.3f} NOT in published [2.5, 4.5]. Published range miscalibrated."
        print(f"  S4 VERDICT: {s4_status}")
    else:
        s4_status = "NOT-EXECUTED"
        s4_note = "Parse yielded no content words. Possible parser issue."
        m1_mean = m3_mean = None
        m1_p10 = m1_p90 = None
else:
    s4_status = "NOT-EXECUTED"
    s4_note = "UD_Basque download unsuccessful."
    m1_mean = m3_mean = None
    m1_p10 = m1_p90 = None


print("\n" + "=" * 70)
print("AGGREGATE VERDICT")
print("=" * 70)

status_to_score = {"PASS": 1.0, "PARTIAL": 0.5, "FAIL": 0.0, "NOT-EXECUTED": None}

substests = [("S1", s1_status), ("S2", s2_status), ("S3", s3_status), ("S4", s4_status)]
executed_scores = [status_to_score[s] for _, s in substests if status_to_score[s] is not None]
denominator = len(executed_scores)
aggregate = sum(executed_scores)

print(f"  S1 provenance:  {s1_status}")
print(f"  S2 sensitivity: {s2_status}")
print(f"  S3 alt ops:     {s3_status}")
print(f"  S4 corpus:      {s4_status}")
print(f"  Aggregate: {aggregate}/{denominator}")

if denominator == 4:
    if aggregate >= 3.5:
        verdict = "ROBUST_CONFIRMATION"
    elif aggregate >= 2.5:
        verdict = "PROVISIONAL_CONFIRMATION"
    elif aggregate >= 1.5:
        verdict = "FRAGILE"
    else:
        verdict = "REFUTED"
else:
    if aggregate >= 2.5 * (denominator / 4):
        verdict = "ROBUST_CONFIRMATION_REDUCED_DENOM"
    elif aggregate >= 1.5 * (denominator / 4):
        verdict = "PROVISIONAL_CONFIRMATION_REDUCED_DENOM"
    else:
        verdict = "FRAGILE_REDUCED_DENOM"
print(f"  VERDICT: {verdict}")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-BASQUE-MATCH-VALIDATION-01",
    "S1_provenance_audit": {"per_metric": s1_per_metric, "contemporaneous_all": s1_contemporaneous_all, "single_source_count": s1_single_source_count, "status": s1_status, "note": s1_note},
    "S2_sensitivity_20pct": {"basque_narrowed_ranges": basque_narrowed, "top3_results": s2_results[:3], "margin": str(s2_margin), "status": s2_status},
    "S3_alternative_operationalisations": {"V1_M1_raw_char": round(v1_mean_char, 4), "V3_M3_prod_ge_5": round(v3_m3, 4), "V5_M5_asym_2x": round(v5_m5, 4), "variants_detail": s3_details, "pass_count": s3_pass_count, "status": s3_status},
    "S4_ud_basque_corpus": {"m1_measured": round(m1_mean, 4) if m1_mean else None, "m1_p10": m1_p10, "m1_p90": m1_p90, "m3_measured": round(m3_mean, 4) if m3_mean else None, "status": s4_status, "note": s4_note},
    "aggregate_score": aggregate,
    "denominator": denominator,
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "basque_match_validation_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
