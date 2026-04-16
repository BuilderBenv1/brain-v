"""
Execute pre-registered H-BV-GALLOWS-STRIP-HEADER-01.

Strip gallows-initial prefixes from Hand A paragraph-initial tokens
and recompute header recurrence. Compare to Isidore's 0.003 +/- 0.05
tolerance band.

Decision (locked):
  stripped recurrence <= 0.053 -> CONFIRMED (gallows artifact; all 4
    CIRCA-INSTANS-BENCHMARK-01 measures now match Isidore)
  stripped recurrence > 0.053 -> REFUTED (gap is genuine; Hand A has
    an additional structural feature beyond standard encyclopedic prose)
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# =============================================================================
# Reload Hand A paragraphs (same as CIRCA-INSTANS-BENCHMARK-01)
# =============================================================================
def starts_gallows(w):
    if not w or w[0] not in "tp": return False
    return len(w) == 1 or w[1] != "h"

paragraphs = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    current = []
    for line in f["lines"]:
        ws = line["words"]
        if not ws: continue
        if starts_gallows(ws[0]) and current:
            paragraphs.append(current); current = []
        current.extend(ws)
    if current:
        paragraphs.append(current)
paragraphs = [p for p in paragraphs if len(p) >= 3]

# Truncate to 11022 preserving paragraph structure (same as benchmark script)
TARGET = 11022
out = []; total = 0
for p in paragraphs:
    if total + len(p) <= TARGET:
        out.append(p); total += len(p)
    elif TARGET - total >= 3:
        out.append(p[:TARGET - total]); total = TARGET; break
    else:
        break
paragraphs = out
print(f"Hand A paragraphs used: {len(paragraphs)}, tokens: {total}")

# =============================================================================
# Extract paragraph-initial tokens (unstripped)
# =============================================================================
unstripped_initials = [p[0] for p in paragraphs if p]

# =============================================================================
# Strip gallows prefix (longest match first)
# =============================================================================
def strip_gallows(tok):
    if len(tok) >= 3 and tok[:3] in ("cth", "ckh", "cph"):
        return tok[3:]
    if tok and tok[0] in "tp":
        return tok[1:]
    return tok

stripped_initials = [strip_gallows(t) for t in unstripped_initials]

# =============================================================================
# Recurrence measurement
# =============================================================================
def recurrence(initials):
    count = Counter(initials)
    types = set(count.keys())
    recur = {t: c for t, c in count.items() if c >= 3}
    return len(recur) / len(types) if types else 0, count, recur

unstripped_rate, unstripped_count, unstripped_recur = recurrence(unstripped_initials)
stripped_rate, stripped_count, stripped_recur = recurrence(stripped_initials)

print(f"\nUNSTRIPPED:")
print(f"  n_types: {len(unstripped_count)}")
print(f"  n_types in >=3 paragraphs: {len(unstripped_recur)}")
print(f"  recurrence rate: {unstripped_rate:.4f}")
print(f"  Top recurring: "
      f"{sorted(unstripped_recur.items(), key=lambda x: -x[1])[:10]}")

print(f"\nSTRIPPED:")
print(f"  n_types: {len(stripped_count)}")
print(f"  n_types in >=3 paragraphs: {len(stripped_recur)}")
print(f"  recurrence rate: {stripped_rate:.4f}")
print(f"  Top recurring: "
      f"{sorted(stripped_recur.items(), key=lambda x: -x[1])[:10]}")

# Diagnostic: which unstripped-nonrecurring stems merge up?
unstripped_recurring_types = set(unstripped_recur.keys())
stripped_recurring_types = set(stripped_recur.keys())
# Trace: for each stripped-recurring stem, show which unstripped tokens feed it
print(f"\nFor each stripped-recurring stem, contributing unstripped tokens:")
stem_to_raw = {}
for raw, stem in zip(unstripped_initials, stripped_initials):
    stem_to_raw.setdefault(stem, Counter())[raw] += 1
for stem, cnt in sorted(stripped_recur.items(), key=lambda x: -x[1])[:10]:
    contribs = stem_to_raw[stem]
    print(f"  '{stem}' (total {cnt}): {dict(contribs)}")

# =============================================================================
# Decision
# =============================================================================
ISIDORE_VAL = 0.003
TOLERANCE = 0.05
BAND_MAX = ISIDORE_VAL + TOLERANCE  # 0.053

print("\n" + "="*72)
print("  PRE-REGISTERED DECISION")
print("="*72)
print(f"  Isidore reference header recurrence: {ISIDORE_VAL:.4f}")
print(f"  Tolerance band:                      +/- {TOLERANCE}")
print(f"  Match if stripped recurrence <=      {BAND_MAX:.4f}")
print(f"  Hand A stripped recurrence:          {stripped_rate:.4f}")
print()
if stripped_rate <= BAND_MAX:
    verdict = "CONFIRMED"
    print(f"  {stripped_rate:.4f} <= {BAND_MAX:.4f} -> CONFIRMED")
    print(f"  Hand A's header-recurrence miss in CIRCA-INSTANS-BENCHMARK-01")
    print(f"  was a GALLOWS ARTIFACT. Stripping recovers the underlying")
    print(f"  non-gallows header vocabulary, which matches Isidore.")
    print(f"  All 4 signature measures now within tolerance of Isidore.")
    print(f"  Herbal-encyclopedic framework is FULLY SUPPORTED.")
else:
    verdict = "REFUTED"
    print(f"  {stripped_rate:.4f} > {BAND_MAX:.4f} -> REFUTED")
    print(f"  Stripping did NOT close the header-recurrence gap. Hand A")
    print(f"  has a genuine additional structural feature beyond standard")
    print(f"  medieval encyclopedic prose.")

# Save
out_path = ROOT / "outputs" / "gallows_strip_header_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-GALLOWS-STRIP-HEADER-01",
    "n_paragraphs": len(paragraphs),
    "n_tokens": total,
    "unstripped": {
        "n_types": len(unstripped_count),
        "n_recurring_types_ge3": len(unstripped_recur),
        "recurrence_rate": round(unstripped_rate, 4),
        "top_recurring": sorted(
            [{"token": t, "count": c} for t, c in unstripped_recur.items()],
            key=lambda x: -x["count"])[:15],
    },
    "stripped": {
        "n_types": len(stripped_count),
        "n_recurring_types_ge3": len(stripped_recur),
        "recurrence_rate": round(stripped_rate, 4),
        "top_recurring": sorted(
            [{"token": t, "count": c} for t, c in stripped_recur.items()],
            key=lambda x: -x["count"])[:15],
    },
    "strip_merge_trace": {
        stem: dict(contribs)
        for stem, contribs in stem_to_raw.items()
        if stem in stripped_recur
    },
    "isidore_reference": ISIDORE_VAL,
    "tolerance": TOLERANCE,
    "band_max": BAND_MAX,
    "verdict": verdict,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
