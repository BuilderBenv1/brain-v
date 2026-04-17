"""
Execute pre-registered H-BV-CAVENEY-FINAL-N-01.

Metric (locked):
  numerator   = count of n occurrences at word-final position in Hand A
  denominator = count of all n occurrences at any position in Hand A
  caveney_ratio = numerator / denominator

Pass condition: caveney_ratio >= 0.85
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

MULTI = sorted(["cth", "cph", "ckh", "cfh", "ch", "sh", "ee"], key=lambda s: -len(s))


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
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])
hand_a_words = [w for w in hand_a_words if w]
tokenised = [tokenize(w) for w in hand_a_words]

count_n_total = 0
count_n_final = 0
for t in tokenised:
    last_idx = len(t) - 1
    for i, g in enumerate(t):
        if g == "n":
            count_n_total += 1
            if i == last_idx:
                count_n_final += 1

caveney_ratio = count_n_final / count_n_total if count_n_total else 0.0
T_pass = caveney_ratio >= 0.85
verdict = "CONFIRMED" if T_pass else "REFUTED"

print(f"Hand A tokens:       {len(hand_a_words)}")
print(f"Total n occurrences: {count_n_total}")
print(f"Word-final n:        {count_n_final}")
print(f"Caveney ratio:       {caveney_ratio:.4f}")
print(f"Pass threshold:      >= 0.85")
print(f"VERDICT:             {verdict}")

out_path = ROOT / "outputs" / "caveney_final_n_test.json"
out_path.write_text(
    json.dumps(
        {
            "generated": "2026-04-17",
            "hypothesis": "H-BV-CAVENEY-FINAL-N-01",
            "n_hand_a_tokens": len(hand_a_words),
            "count_n_total": count_n_total,
            "count_n_final": count_n_final,
            "caveney_ratio": round(caveney_ratio, 4),
            "pass_threshold": 0.85,
            "pass": T_pass,
            "verdict": verdict,
        },
        indent=2,
        default=str,
    ),
    encoding="utf-8",
)
print(f"\nSaved: {out_path}")
