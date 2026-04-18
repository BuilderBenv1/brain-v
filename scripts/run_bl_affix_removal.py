"""Execute pre-registered H-BV-BL-AFFIX-REMOVAL-01.

Reproduces Bowern & Lindemann 2021's post-affix-removal h2 collapse:
A and B both should reach approximately 2.23-2.24 when -edy and qo-
are removed.
"""
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))


def normalise(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def conditional_entropy(text):
    bigrams = Counter()
    firsts = Counter()
    for i in range(len(text) - 1):
        bigrams[(text[i], text[i + 1])] += 1
        firsts[text[i]] += 1
    total = sum(bigrams.values())
    if total == 0:
        return 0.0
    H = 0.0
    for (a, b), ab_c in bigrams.items():
        p_ab = ab_c / total
        p_b_given_a = ab_c / firsts[a] if firsts[a] > 0 else 0
        if p_b_given_a > 0:
            H += p_ab * math.log2(1 / p_b_given_a)
    return H


def get_tokens(currier):
    words = []
    for f in CORPUS["folios"]:
        if f.get("currier_language") == currier:
            for line in f["lines"]:
                for w in line["words"]:
                    if w:
                        words.append(w)
    return words


def text_from_tokens(tokens):
    return normalise(" ".join(tokens))


def filter_locked(tokens):
    """Locked rule: remove tokens ending in 'edy' OR starting with 'qo'."""
    return [t for t in tokens if not (t.endswith("edy") or t.startswith("qo"))]


def filter_substring_edy_only(tokens):
    return [t for t in tokens if "edy" not in t]


def filter_substring_anywhere(tokens):
    return [t for t in tokens if "edy" not in t and "qo" not in t]


def filter_remove_substring(tokens):
    """Variant 2: remove the substrings -edy and qo- but keep token stems."""
    out = []
    for t in tokens:
        s = t
        if s.startswith("qo"):
            s = s[2:]
        if s.endswith("edy"):
            s = s[:-3]
        if s:
            out.append(s)
    return out


def filter_only_edy(tokens):
    return [t for t in tokens if not t.endswith("edy")]


def filter_only_qo(tokens):
    return [t for t in tokens if not t.startswith("qo")]


hand_a = get_tokens("A")
hand_b = get_tokens("B")
print(f"Hand A tokens: {len(hand_a)}")
print(f"Hand B tokens: {len(hand_b)}")

# Baseline h2
h2_a_base = conditional_entropy(text_from_tokens(hand_a))
h2_b_base = conditional_entropy(text_from_tokens(hand_b))
print(f"\nBASELINE h2:")
print(f"  Hand A: {h2_a_base:.4f}  (B&L LV: 2.17, B&L CE: 2.122; Brain-V prior: 2.19)")
print(f"  Hand B: {h2_b_base:.4f}  (B&L LV: 2.01, B&L CE: 1.973; Brain-V prior: 2.02)")
print(f"  Gap A-B baseline: {h2_a_base - h2_b_base:+.4f}")

# Locked filter: end in 'edy' or start with 'qo'
hand_a_locked = filter_locked(hand_a)
hand_b_locked = filter_locked(hand_b)
removed_a = len(hand_a) - len(hand_a_locked)
removed_b = len(hand_b) - len(hand_b_locked)

h2_a_post = conditional_entropy(text_from_tokens(hand_a_locked))
h2_b_post = conditional_entropy(text_from_tokens(hand_b_locked))
gap_post = h2_a_post - h2_b_post

print(f"\nPOST-AFFIX-REMOVAL h2 (LOCKED filter: endswith 'edy' OR startswith 'qo'):")
print(f"  Hand A: {h2_a_post:.4f}  (removed {removed_a}/{len(hand_a)} = {removed_a/len(hand_a)*100:.1f}%)")
print(f"  Hand B: {h2_b_post:.4f}  (removed {removed_b}/{len(hand_b)} = {removed_b/len(hand_b)*100:.1f}%)")
print(f"  Gap A-B post-removal: {gap_post:+.4f}")
print(f"  B&L target: A=2.23, B=2.24, gap <1%")

# Verdict
target = 2.235
dev_a = abs(h2_a_post - target)
dev_b = abs(h2_b_post - target)
gap_pct = abs(gap_post) / max(h2_a_post, h2_b_post) if max(h2_a_post, h2_b_post) > 0 else 1.0
gap_collapsed = abs(gap_post) < 0.05

print(f"\n  Deviation from B&L target 2.235:")
print(f"    Hand A: {dev_a:.4f}")
print(f"    Hand B: {dev_b:.4f}")
print(f"  A/B gap absolute: {abs(gap_post):.4f}  fraction: {gap_pct*100:.2f}%")

if dev_a <= 0.10 and dev_b <= 0.10 and gap_collapsed:
    verdict = "CONFIRMED"
elif dev_a <= 0.25 and dev_b <= 0.25:
    verdict = "PARTIAL"
else:
    verdict = "REFUTED"

print(f"\n  VERDICT: {verdict}")
print(f"  GAP IMPLICATION: {'GAP_COLLAPSED' if gap_collapsed else 'GAP_PRESERVED'}")

# Sensitivity diagnostics
print(f"\n=== SENSITIVITY DIAGNOSTICS (not part of locked verdict) ===")
diagnostics = {}
for label, fn in [
    ("V1 substring 'edy' or 'qo' anywhere -> remove token", filter_substring_anywhere),
    ("V2 remove substrings -edy and qo- but keep stems", filter_remove_substring),
    ("V3 only -edy removed (endswith)", filter_only_edy),
    ("V4 only qo- removed (startswith)", filter_only_qo),
]:
    a_filt = fn(hand_a); b_filt = fn(hand_b)
    h2_a = conditional_entropy(text_from_tokens(a_filt))
    h2_b = conditional_entropy(text_from_tokens(b_filt))
    rem_a = (len(hand_a) - len(a_filt)) / len(hand_a) * 100 if 'remove substrings' not in label else 0
    rem_b = (len(hand_b) - len(b_filt)) / len(hand_b) * 100 if 'remove substrings' not in label else 0
    print(f"  {label}")
    print(f"    A h2={h2_a:.4f}  B h2={h2_b:.4f}  gap={h2_a-h2_b:+.4f}")
    diagnostics[label] = {"h2_a": round(h2_a, 4), "h2_b": round(h2_b, 4), "gap": round(h2_a - h2_b, 4)}

out = {
    "generated": "2026-04-18",
    "hypothesis": "H-BV-BL-AFFIX-REMOVAL-01",
    "n_hand_a_tokens": len(hand_a),
    "n_hand_b_tokens": len(hand_b),
    "baseline": {
        "hand_a_h2": round(h2_a_base, 4),
        "hand_b_h2": round(h2_b_base, 4),
        "gap_a_minus_b": round(h2_a_base - h2_b_base, 4),
        "bl_lv_reference": "A=2.17, B=2.01",
        "bl_ce_reference": "A=2.122, B=1.973",
    },
    "locked_filter_post_removal": {
        "rule": "token.endswith('edy') OR token.startswith('qo') -> remove",
        "tokens_removed_hand_a": removed_a,
        "tokens_removed_hand_b": removed_b,
        "removal_rate_a_pct": round(removed_a / len(hand_a) * 100, 2),
        "removal_rate_b_pct": round(removed_b / len(hand_b) * 100, 2),
        "hand_a_h2_post": round(h2_a_post, 4),
        "hand_b_h2_post": round(h2_b_post, 4),
        "gap_a_minus_b_post": round(gap_post, 4),
        "bl_target": "A=2.23, B=2.24, gap <1%",
        "deviation_a_from_target": round(dev_a, 4),
        "deviation_b_from_target": round(dev_b, 4),
    },
    "sensitivity_diagnostics": diagnostics,
    "verdict": verdict,
    "gap_implication": "GAP_COLLAPSED" if gap_collapsed else "GAP_PRESERVED",
}
out_path = ROOT / "outputs" / "bl_affix_removal_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
