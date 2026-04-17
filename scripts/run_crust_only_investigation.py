"""
Execute pre-registered H-BV-CRUST-ONLY-INVESTIGATION-01.

Three sub-tests diagnosing the 26-29% vs Stolfi's 75% crust-only
fraction discrepancy:
  S1 transcription version (IT2a, RF1b, ZL3b)
  S2 normal-words filter audit
  S3 sub-corpus scope (Currier, section, cross partitions)
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS_DIR = ROOT / "raw" / "corpus"
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI = sorted(["cth", "cph", "ckh", "cfh", "ch", "sh", "ee"], key=lambda s: -len(s))
CORE_SET = {"t", "p", "k", "f", "cth", "cph", "ckh", "cfh"}
MANTLE_SET = {"ch", "sh", "ee"}
NON_STANDARD = {"b", "c", "j", "u", "v", "z"}

STOLFI_TARGET = 0.75
TOLERANCE = 0.05


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


def crust_only_fraction(tokenised_tokens, include_predicate=lambda t: True):
    n = 0
    d = 0
    for t in tokenised_tokens:
        if not t:
            continue
        if not include_predicate(t):
            continue
        d += 1
        if not any(g in CORE_SET for g in t) and not any(g in MANTLE_SET for g in t):
            n += 1
    return n, d, (n / d if d else 0.0)


IVTFF_ANNOTATION_RE = re.compile(r"@\d+;")
TAG_RE = re.compile(r"<[^>]+>")
BRACE_ALT_RE = re.compile(r"\{([^}]*)\}")
BRACKET_ALT_RE = re.compile(r"\[([^:\]]*)(?::[^\]]*)?\]")


def strip_ivtff_annotations(line_content):
    s = IVTFF_ANNOTATION_RE.sub("?", line_content)
    s = TAG_RE.sub("", s)
    s = BRACKET_ALT_RE.sub(lambda m: m.group(1), s)
    s = BRACE_ALT_RE.sub(lambda m: m.group(1).replace("'", ""), s)
    s = s.replace(",", "")
    return s


def parse_ivtff_file(path):
    words = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("#="):
                continue
            if not line.startswith("<"):
                continue
            m = re.match(r"<([^>]+)>\s*(.*)", line)
            if not m:
                continue
            tag = m.group(1)
            content = m.group(2)
            if "." not in content and tag.startswith("f") and "," not in tag:
                continue
            if not re.search(r"\.", content) and not content.strip():
                continue
            content_clean = strip_ivtff_annotations(content)
            parts = content_clean.split(".")
            for p in parts:
                p = p.strip()
                if p:
                    words.append(p)
    return words


print("=== S1: TRANSCRIPTION VERSION COMPARISON ===")
s1_results = {}
for label, filename in [("IT2a", "IT2a-n.txt"), ("RF1b", "RF1b-e.txt"), ("ZL3b", "ZL3b-n.txt")]:
    path = CORPUS_DIR / filename
    raw_words = parse_ivtff_file(path)
    tokenised = [tokenize(w) for w in raw_words if w]
    n, d, frac = crust_only_fraction(tokenised)
    s1_results[label] = {"n": n, "d": d, "fraction": round(frac, 4)}
    in_band = TOLERANCE >= abs(frac - STOLFI_TARGET)
    print(f"  {label}: {n}/{d} = {frac:.4f}  {'IN BAND' if in_band else ''}")

s1_max_delta = max(r["fraction"] for r in s1_results.values()) - min(
    r["fraction"] for r in s1_results.values()
)
print(f"  max variant delta: {s1_max_delta:.4f}")


all_words_zl = []
folio_words = []
for f in CORPUS["folios"]:
    for line in f["lines"]:
        for w in line["words"]:
            if w:
                all_words_zl.append(w)
                folio_words.append({"word": w, "folio": f, "line": line})

tokenised_zl = [tokenize(w) for w in all_words_zl]
word_freq = Counter(all_words_zl)

n0, d0, frac0 = crust_only_fraction(tokenised_zl)
print(f"\nBaseline (ZL3b, parsed voynich-corpus.json, no filter): {n0}/{d0} = {frac0:.4f}")


def pred_not_hapax(idx):
    return word_freq[all_words_zl[idx]] > 1


def pred_no_nonstandard(idx):
    return not any(g in NON_STANDARD for g in tokenised_zl[idx])


def pred_len_ge_3(idx):
    return len(tokenised_zl[idx]) >= 3


def pred_not_weirdo(idx):
    t = tokenised_zl[idx]
    core_count = sum(1 for g in t if g in CORE_SET)
    return core_count < 2 and len(t) < 12


def crust_only_indexed(predicate):
    n = 0
    d = 0
    for i, t in enumerate(tokenised_zl):
        if not t:
            continue
        if not predicate(i):
            continue
        d += 1
        if not any(g in CORE_SET for g in t) and not any(g in MANTLE_SET for g in t):
            n += 1
    return n, d, (n / d if d else 0.0)


print("\n=== S2: NORMAL-WORDS FILTER AUDIT ===")
s2_results = {}
for label, pred in [
    ("F1_exclude_hapaxes", pred_not_hapax),
    ("F2_exclude_non_standard", pred_no_nonstandard),
    ("F3_exclude_short_len_lt_3", pred_len_ge_3),
    ("F4_exclude_weirdos", pred_not_weirdo),
]:
    n, d, frac = crust_only_indexed(pred)
    in_band = abs(frac - STOLFI_TARGET) <= TOLERANCE
    s2_results[label] = {"n": n, "d": d, "fraction": round(frac, 4)}
    print(f"  {label}: {n}/{d} = {frac:.4f}  {'IN BAND' if in_band else ''}")


def pred_cumulative(idx):
    return (
        pred_not_hapax(idx)
        and pred_no_nonstandard(idx)
        and pred_len_ge_3(idx)
        and pred_not_weirdo(idx)
    )


n_c, d_c, frac_c = crust_only_indexed(pred_cumulative)
s2_results["F_cumulative_F1_F2_F3_F4"] = {"n": n_c, "d": d_c, "fraction": round(frac_c, 4)}
print(f"  F_cumulative (F1+F2+F3+F4): {n_c}/{d_c} = {frac_c:.4f}  "
      f"{'IN BAND' if abs(frac_c - STOLFI_TARGET) <= TOLERANCE else ''}")


def pred_len_ge_2(idx):
    return len(tokenised_zl[idx]) >= 2


def pred_len_ge_4(idx):
    return len(tokenised_zl[idx]) >= 4


for label, pred in [
    ("F3b_len_ge_2", pred_len_ge_2),
    ("F3c_len_ge_4", pred_len_ge_4),
]:
    n, d, frac = crust_only_indexed(pred)
    s2_results[label] = {"n": n, "d": d, "fraction": round(frac, 4)}
    print(f"  {label}: {n}/{d} = {frac:.4f}  "
          f"{'IN BAND' if abs(frac - STOLFI_TARGET) <= TOLERANCE else ''}")


print("\n=== S3: SUB-CORPUS SCOPE ===")
s3_results = {}

folio_indexed_words = []
folio_indexed_tokenised = []
folio_indexed_folio = []
for f in CORPUS["folios"]:
    for line in f["lines"]:
        for w in line["words"]:
            if w:
                folio_indexed_words.append(w)
                folio_indexed_tokenised.append(tokenize(w))
                folio_indexed_folio.append(f)


def frac_for_predicate(idx_pred):
    n = 0
    d = 0
    for i, t in enumerate(folio_indexed_tokenised):
        if not t:
            continue
        if not idx_pred(i):
            continue
        d += 1
        if not any(g in CORE_SET for g in t) and not any(g in MANTLE_SET for g in t):
            n += 1
    return n, d, (n / d if d else 0.0)


for label, lang in [("currier_A", "A"), ("currier_B", "B"), ("currier_other", "?")]:
    def p(i, lang=lang):
        v = folio_indexed_folio[i].get("currier_language")
        if lang == "?":
            return v not in ("A", "B")
        return v == lang
    n, d, frac = frac_for_predicate(p)
    s3_results[label] = {"n": n, "d": d, "fraction": round(frac, 4)}
    in_band = abs(frac - STOLFI_TARGET) <= TOLERANCE
    print(f"  {label}: {n}/{d} = {frac:.4f}  {'IN BAND' if in_band else ''}")

sections_present = sorted(set(f.get("section", "?") for f in CORPUS["folios"]))
for sec in sections_present:
    def p(i, sec=sec):
        return folio_indexed_folio[i].get("section") == sec
    n, d, frac = frac_for_predicate(p)
    key = f"section_{sec}"
    s3_results[key] = {"n": n, "d": d, "fraction": round(frac, 4)}
    in_band = abs(frac - STOLFI_TARGET) <= TOLERANCE
    print(f"  {key}: {n}/{d} = {frac:.4f}  {'IN BAND' if in_band else ''}")

for sec, lang in [("herbal", "A"), ("herbal", "B"), ("pharmaceutical", "B"), ("biological", "B"),
                    ("astronomical", "A"), ("zodiac", "B")]:
    def p(i, sec=sec, lang=lang):
        return (folio_indexed_folio[i].get("section") == sec
                and folio_indexed_folio[i].get("currier_language") == lang)
    n, d, frac = frac_for_predicate(p)
    key = f"cross_{sec}_{lang}"
    s3_results[key] = {"n": n, "d": d, "fraction": round(frac, 4)}
    if d >= 100:
        in_band = abs(frac - STOLFI_TARGET) <= TOLERANCE
        print(f"  {key}: {n}/{d} = {frac:.4f}  {'IN BAND' if in_band else ''}")


print("\n=== LOCKED DECISION ===")
all_variants = []
for label, r in s1_results.items():
    all_variants.append(("S1", label, r["fraction"], r["d"]))
for label, r in s2_results.items():
    all_variants.append(("S2", label, r["fraction"], r["d"]))
for label, r in s3_results.items():
    if r["d"] >= 500:
        all_variants.append(("S3", label, r["fraction"], r["d"]))

in_band_variants = [v for v in all_variants if abs(v[2] - STOLFI_TARGET) <= TOLERANCE]
closest_variant = min(all_variants, key=lambda v: abs(v[2] - STOLFI_TARGET))

print(f"  Closest single variant: {closest_variant[0]} / {closest_variant[1]}  frac = {closest_variant[2]:.4f}  n_tokens = {closest_variant[3]}")
print(f"  In-band variants: {len(in_band_variants)}")
for v in in_band_variants:
    print(f"    {v[0]} / {v[1]}: {v[2]:.4f}  n = {v[3]}")

if in_band_variants:
    verdict = "DIAGNOSED_SINGLE_SOURCE"
    print(f"  VERDICT: DIAGNOSED_SINGLE_SOURCE")
    print(f"  Reconciling variant: {in_band_variants[0][0]} / {in_band_variants[0][1]}")
elif abs(s2_results.get("F_cumulative_F1_F2_F3_F4", {}).get("fraction", 0.0) - STOLFI_TARGET) <= TOLERANCE:
    verdict = "DIAGNOSED_MULTI_SOURCE"
    print(f"  VERDICT: DIAGNOSED_MULTI_SOURCE via cumulative filter")
else:
    verdict = "UNRESOLVED_OPEN_QUESTION"
    print(f"  VERDICT: UNRESOLVED_OPEN_QUESTION")
    print(f"  Best single variant: {closest_variant[2]:.4f} (target 0.75, delta {closest_variant[2]-0.75:+.4f})")

out = {
    "generated": "2026-04-17",
    "hypothesis": "H-BV-CRUST-ONLY-INVESTIGATION-01",
    "stolfi_target": STOLFI_TARGET,
    "tolerance": TOLERANCE,
    "S1_transcription_version": s1_results,
    "S1_max_delta_across_versions": round(s1_max_delta, 4),
    "baseline_zl3b_no_filter": {"n": n0, "d": d0, "fraction": round(frac0, 4)},
    "S2_normal_words_filter": s2_results,
    "S3_sub_corpus_scope": s3_results,
    "closest_variant": {
        "sub_test": closest_variant[0],
        "label": closest_variant[1],
        "fraction": round(closest_variant[2], 4),
        "n_tokens": closest_variant[3],
        "delta_vs_0_75": round(closest_variant[2] - STOLFI_TARGET, 4),
    },
    "in_band_count": len(in_band_variants),
    "in_band_variants": [
        {"sub_test": v[0], "label": v[1], "fraction": round(v[2], 4), "n_tokens": v[3]}
        for v in in_band_variants
    ],
    "verdict": verdict,
}
out_path = ROOT / "outputs" / "crust_only_investigation_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
