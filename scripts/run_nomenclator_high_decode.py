"""
Execute pre-registered H-BV-NOMENCLATOR-HIGH-DECODE-01.

Re-run the connector-content bigram shuffle test for Brady, Schechter,
and Pagel — this time restricted to HIGH-class tokens only (top 146
types by Hand-A frequency, covering 50.1% of Hand-A tokens; R locked
from H-BV-NOMENCLATOR-01).

Decision (locked):
  HIGH-only delta >= +0.010 -> CONFIRMED for that map (substrate found)
  0 < delta < +0.010 -> MARGINAL
  delta <= 0 -> REFUTED

Overall:
  any map CONFIRMED -> NOMENCLATOR-SUPPORTED (primary substrate identified)
  all 3 REFUTED on HIGH-only -> NOMENCLATOR-SUBSTRATE-REFUTED
"""
import csv
import json
import random
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# =============================================================================
# Reproduce HIGH_TYPES from NOMENCLATOR-01 (R=146)
# =============================================================================
hand_a_words = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hand_a_words.extend(line["words"])

freq = Counter(hand_a_words)
N_total = sum(freq.values())
sorted_types = freq.most_common()

# Split at cumulative-50% rank (same procedure as NOMENCLATOR-01)
cum = 0; R = 0
for i, (t, c) in enumerate(sorted_types, 1):
    cum += c
    if cum >= N_total / 2:
        R = i; break

HIGH_TYPES = {t for t, _ in sorted_types[:R]}
assert R == 146, f"Expected R=146 from NOMENCLATOR-01, got {R}"
print(f"HIGH class: {R} types covering {cum} Hand-A tokens ({100*cum/N_total:.1f}%)")

# =============================================================================
# Three decoders (verbatim copies from run_hand_a_map_comparison.py)
# =============================================================================
BRADY_EVA_MAP = [
    ("cth","tk"),("ckh","kk"),("cph","pk"),("ch","k"),("sh","s"),
    ("k","k"),("d","d"),("r","r"),("s","s"),("l","l"),
    ("n","n"),("y","y"),("m","m"),("g","g"),
    ("t","t"),("p","p"),("f","s"),("q","w"),
]
BRADY_LEX = {
    "w","d","l","m","k","kl","km","dy","ky","kdy","kdn","yn","kr","krh",
    "sm","smy","tly","tl","ls","ss","tdy","tr","dl","ak","kyn","tks","syy",
    "kdd","kky","ks","ksy","tyn","tn","ts","sy","syw","rp","mpss","mys",
    "myl","dr","bl","ml","mlk","sr","sry","drm","wd","wl","wdl","lm","bn",
    "ny","ry","dy","kss","krd","sdr","ydy","yd","sl","mr","skr","ndr","ssr",
    "kkr","sym","rsm","nsy","lks","dkr",
}
BRADY_CONNECTORS = {"w","d","l","m","wd","wl","wdl","k","kl","km","dy","ky"}

def brady_to_skel(word):
    if word and word[0] in "tp" and (len(word)==1 or word[1]!="h"):
        word = word[1:]
    out = []; i = 0
    while i < len(word):
        matched = False
        for ev, sy in BRADY_EVA_MAP:
            if word.startswith(ev, i):
                out.append(sy); i += len(ev); matched = True; break
        if not matched:
            i += 1
    return "".join(out)

def brady_match(skel):
    if skel in BRADY_LEX: return True
    for pre in ("w","d","l"):
        if skel.startswith(pre) and len(skel)>1 and skel[1:] in BRADY_LEX: return True
    if skel.endswith("yn") and skel[:-2] in BRADY_LEX: return True
    return False

def brady_decode(word):
    sk = brady_to_skel(word)
    return sk, brady_match(sk), sk in BRADY_CONNECTORS

SCHECHTER = {}
with (ROOT / "raw/schechter_glossary.csv").open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        SCHECHTER[r["eva"]] = r["decoded"].upper()
SCHECHTER_CONN_VALUES = {"ET","IN","DE","AD","EST","CUM","EX","NON","SED",
    "PER","VEL","SI","AC","QUOD","QUIA","OR","AN","AL","AM","AUT","NEC",
    "QUE","SUB","SUPER","O","E","EN","A","LA","LO","LAS","LI","ALS","NI"}

def schechter_decode(word):
    decoded = SCHECHTER.get(word)
    if decoded is None:
        return word, False, False
    return decoded, True, decoded in SCHECHTER_CONN_VALUES

PAGEL = {
    "daiin":"DATUR","chedy":"CALIDUS","chol":"FOLIUM","shedy":"SICCUS",
    "dam":"DAM","ol":"OLEUM","otal":"STELLA","or":"OR","sam":"SAM",
    "sal":"SAL","chom":"CHOM","kor":"KOR","sar":"SANARE","chor":"FLOS",
    "y":"ET","sho":"SUME","qokain":"QOKAIN","qokeey":"QOKEEY","otar":"OTAR",
    "oteey":"OTEEY","dain":"DATUM","kal":"CALOR","rar":"RADIX","ar":"AER",
    "al":"ALIUS","shol":"SOL","cheol":"CHEOL","cheor":"CHEOR","s":"EST",
    "dan":"DAN","shy":"SICC","qokedy":"QOKEDY","lchedy":"LCHEDY","keol":"KEOL",
    "qol":"QOL","qokor":"QOKOR","otedy":"OTEDY","bar":"BARID","lach":"LACH",
    "chey":"CUM","shey":"SIC","chy":"QUIA","sheol":"SHEOL","por":"PRO",
    "teody":"TEPIDUS","oky":"OKY","kchy":"KCHY","saiin":"SAIIN",
    "cholaiin":"CHOLAIIN","qoky":"QUOQUE","chckhy":"COCTUS","shekar":"SHEKAR",
    "darchiin":"DARCHIIN","qokal":"QOKAL","aiindy":"INDE","dago":"ERGO",
}
PAGEL_CONNECTORS = {"ET","EST","CUM","SIC","QUIA","PRO","QUOQUE","OR",
                    "AER","ALIUS","SED","NON","INDE","ERGO","SAL"}

def pagel_decode(word):
    decoded = PAGEL.get(word)
    if decoded is None:
        return word, False, False
    return decoded, True, decoded in PAGEL_CONNECTORS

# =============================================================================
# Build HIGH-only filtered lines
# =============================================================================
hand_a_high_lines = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        hi = [w for w in line["words"] if w in HIGH_TYPES]
        if len(hi) >= 3:
            hand_a_high_lines.append(hi)

total_high_tokens = sum(len(L) for L in hand_a_high_lines)
print(f"HIGH-only filtered Hand-A lines (>=3 HIGH tokens): {len(hand_a_high_lines)}")
print(f"HIGH tokens in those lines: {total_high_tokens}")

# =============================================================================
# Shuffle test per map
# =============================================================================
def decode_lines(decode_fn, lines):
    return [[decode_fn(w) for w in L] for L in lines]

def conn_content_rate(decoded_line):
    conn_n = 0; hits = 0
    for a, b in zip(decoded_line, decoded_line[1:]):
        _, _, a_conn = a
        _, b_ok, b_conn = b
        if a_conn:
            conn_n += 1
            if b_ok and not b_conn:
                hits += 1
    return hits / conn_n if conn_n else 0

def shuffle_test(decoded_lines, seed=0):
    all_tokens = [t for L in decoded_lines for t in L]
    in_order = statistics.mean([conn_content_rate(L) for L in decoded_lines])
    rng = random.Random(seed)
    shuffled = list(all_tokens); rng.shuffle(shuffled)
    rechunked = []; idx = 0
    for L in decoded_lines:
        rechunked.append(shuffled[idx:idx+len(L)])
        idx += len(L)
    sh_rates = [conn_content_rate(L) for L in rechunked if len(L) >= 3]
    sh = statistics.mean(sh_rates) if sh_rates else 0
    matched = sum(1 for t in all_tokens if t[1])
    conn = sum(1 for t in all_tokens if t[2])
    return {
        "n_tokens": len(all_tokens),
        "matched": matched,
        "match_rate": matched / len(all_tokens),
        "connectors": conn,
        "connector_rate": conn / len(all_tokens),
        "in_order": in_order,
        "shuffled": sh,
        "delta": in_order - sh,
    }

MAPS = [
    ("Brady-Syriac", brady_decode),
    ("Schechter-LatinOcc", schechter_decode),
    ("Pagel-trilingual", pagel_decode),
]

print("\n" + "="*78)
print("  HIGH-ONLY SHUFFLE TEST — Brady / Schechter / Pagel")
print("="*78)
print(f"  {'map':<22}{'match%':>9}{'conn%':>8}{'in-order':>12}"
      f"{'shuffled':>12}{'delta':>12}")

results = []
for name, fn in MAPS:
    dec = decode_lines(fn, hand_a_high_lines)
    res = shuffle_test(dec)
    res["map"] = name
    results.append(res)
    print(f"  {name:<22}{res['match_rate']*100:>8.1f}%{res['connector_rate']*100:>7.1f}%"
          f"{res['in_order']:>12.4f}{res['shuffled']:>12.4f}{res['delta']:>+12.4f}")

# =============================================================================
# Decision
# =============================================================================
print("\n" + "="*78)
print("  PER-MAP VERDICTS (locked threshold +0.010)")
print("="*78)
for r in results:
    if r["delta"] >= 0.010:
        v = "CONFIRMED"
    elif r["delta"] > 0:
        v = "MARGINAL"
    else:
        v = "REFUTED"
    r["verdict"] = v
    print(f"  {r['map']:<22} delta {r['delta']:+.4f}  -> {v}")

# Compare against prior full-Hand-A results from H-BV-HAND-A-MAP-COMPARISON-01
priors = {
    "Brady-Syriac": 0.0044,
    "Schechter-LatinOcc": -0.0608,
    "Pagel-trilingual": 0.0118,
}
print("\n  Comparison to full-Hand-A priors:")
for r in results:
    prior = priors.get(r["map"], None)
    if prior is not None:
        print(f"    {r['map']:<22} full-Hand-A {prior:+.4f}  HIGH-only {r['delta']:+.4f}  "
              f"shift {r['delta']-prior:+.4f}")

confirmed = [r for r in results if r["verdict"] == "CONFIRMED"]
print("\n" + "="*78)
print("  OVERALL DECISION")
print("="*78)
if confirmed:
    primary = max(confirmed, key=lambda r: r["delta"])
    overall = "NOMENCLATOR-SUPPORTED"
    print(f"  >=1 map CONFIRMED on HIGH-only -> NOMENCLATOR-SUPPORTED.")
    print(f"  Primary substrate candidate: {primary['map']} (delta {primary['delta']:+.4f}).")
    print(f"  The LOW class is the codebook; attack separately.")
else:
    overall = "NOMENCLATOR-SUBSTRATE-REFUTED"
    print(f"  0 of 3 maps confirmed on HIGH-only.")
    print(f"  The two-population structure is real (NOMENCLATOR-01 + NLREF-01)")
    print(f"  but NONE of Brady/Schechter/Pagel is the substrate cipher.")

out_path = ROOT / "outputs" / "nomenclator_high_decode_test.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-NOMENCLATOR-HIGH-DECODE-01",
    "R_split_rank": R,
    "high_types_count": len(HIGH_TYPES),
    "high_only_lines": len(hand_a_high_lines),
    "high_only_tokens_total": total_high_tokens,
    "results": [
        {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}
        for r in results
    ],
    "full_hand_a_priors_for_comparison": priors,
    "overall_verdict": overall,
    "thresholds": {
        "confirmed": "delta >= +0.010",
        "marginal": "0 < delta < +0.010",
        "refuted": "delta <= 0",
    },
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
