"""
Execute pre-registered H-BV-HAND-A-LANGUAGE-01 (locked 2b8171b).

Apply Brady's EVA->Syriac char map to Hand A folios only. Measure
shuffle-test connector-content bigram delta. Compare to the earlier
full-corpus delta of -0.0098.

Decision rule:
  delta >= +0.010 -> CONFIRMED (Brady survives within Hand A)
  0 < delta < +0.010 -> MARGINAL
  delta <= 0 -> REFUTED
"""
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
VOWELS = set("aoei")

# Same proxy lex as Brady-shuffle test (71 skeletons from paper body)
BRADY_LEX = {
    "w","d","l","m","k","kl","km","dy","ky","kdy","kdn","yn","kr","krh",
    "sm","smy","tly","tl","ls","ss","tdy","tr","dl","ak","kyn","tks","syy",
    "kdd","kky","ks","ksy","tyn","tn","ts","sy","syw","rp","mpss","mys",
    "myl","dr","bl","ml","mlk","sr","sry","drm","wd","wl","wdl","lm","bn",
    "ny","ry","dy","kss","krd","sdr","ydy","yd","sl","mr","skr","ndr","ssr",
    "kkr","sym","rsm","nsy","lks","dkr",
}
CONNECTORS = {"w","d","l","m","wd","wl","wdl","k","kl","km","dy","ky"}

def to_skeleton(word):
    if word and word[0] in "tp" and (len(word)==1 or word[1]!="h"):
        word = word[1:]
    out = []; i = 0
    while i < len(word):
        matched = False
        for ev, sy in EVA_MAP:
            if word.startswith(ev, i):
                out.append(sy); i += len(ev); matched = True; break
        if not matched:
            i += 1
    return "".join(out)

def match(skel):
    if skel in BRADY_LEX: return True
    for pre in ("w","d","l"):
        if skel.startswith(pre) and len(skel)>1 and skel[1:] in BRADY_LEX:
            return True
    if skel.endswith("yn") and skel[:-2] in BRADY_LEX: return True
    return False

# Hand A folios with lines
hand_a_lines = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A": continue
    for line in f["lines"]:
        stream = []
        for w in line["words"]:
            sk = to_skeleton(w)
            ok = match(sk)
            stream.append((sk, ok))
        if len(stream) >= 3:
            hand_a_lines.append(stream)

total_tokens = sum(len(L) for L in hand_a_lines)
matched = sum(1 for L in hand_a_lines for _, ok in L if ok)
print(f"Hand A: {len(hand_a_lines)} lines, {total_tokens} tokens, "
      f"matched {matched} ({matched/total_tokens:.1%})")

def conn_content_rate(stream):
    conn_n = 0; hits = 0
    for a, b in zip(stream, stream[1:]):
        a_sk, a_ok = a
        b_sk, b_ok = b
        if a_sk in CONNECTORS:
            conn_n += 1
            if b_ok and b_sk not in CONNECTORS:
                hits += 1
    return hits / conn_n if conn_n else 0

# In-order
in_order_rates = [conn_content_rate(L) for L in hand_a_lines]
in_order = statistics.mean(in_order_rates) if in_order_rates else 0

# Shuffled — pool tokens across Hand A lines, reshuffle, rechunk
random.seed(0)
all_tokens = [t for L in hand_a_lines for t in L]
random.shuffle(all_tokens)
shuffled_lines = []
idx = 0
for L in hand_a_lines:
    shuffled_lines.append(all_tokens[idx:idx+len(L)])
    idx += len(L)
shuffled_rates = [conn_content_rate(L) for L in shuffled_lines if len(L) >= 3]
shuffled = statistics.mean(shuffled_rates) if shuffled_rates else 0

delta = in_order - shuffled
print(f"\n  Hand-A-only connector-content bigram rate:")
print(f"    in-order:   {in_order:.4f}")
print(f"    shuffled:   {shuffled:.4f}")
print(f"    delta:      {delta:+.4f}")
print(f"\n  Compare full-corpus Brady test: delta was -0.0098")

print(f"\n{'='*72}")
print(f"  PRE-REGISTERED DECISION")
print(f"{'='*72}")
if delta >= 0.010:
    verdict = "CONFIRMED"
    print(f"  delta {delta:+.4f} >= +0.010 -> CONFIRMED")
    print(f"  Brady's map survives within Hand A. Original cross-corpus")
    print(f"  failure was Hand-B noise masking a real Hand-A signal.")
elif delta > 0:
    verdict = "MARGINAL"
    print(f"  0 < delta {delta:+.4f} < +0.010 -> MARGINAL")
elif delta <= 0:
    verdict = "REFUTED"
    print(f"  delta {delta:+.4f} <= 0 -> REFUTED")
    print(f"  Hand A alone also fails the shuffle test — Brady's specific")
    print(f"  map is not the right key, even within Hand A.")

out = ROOT / "outputs" / "hand_a_brady_language.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-HAND-A-LANGUAGE-01",
    "locked_in_commit": "2b8171b",
    "hand_a_lines": len(hand_a_lines),
    "total_tokens": total_tokens,
    "matched_tokens": matched,
    "match_rate": round(matched/total_tokens, 4),
    "in_order_conn_content_rate": round(in_order, 4),
    "shuffled_conn_content_rate": round(shuffled, 4),
    "delta": round(delta, 4),
    "verdict": verdict,
    "full_corpus_delta_for_comparison": -0.0098,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
