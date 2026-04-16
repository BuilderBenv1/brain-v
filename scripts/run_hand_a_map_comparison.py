"""
Execute pre-registered H-BV-HAND-A-MAP-COMPARISON-01 (locked d95fce0).

Rank three character/word maps by connector-content bigram delta on
Hand A alone.

  Brady Syriac (char-level EVA->Syriac, 71-term proxy lex)
  Schechter Latin-Occitan (word-level, 4,063 entries)
  Pagel trilingual (word-level, 81 terms)
"""
import csv
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# ----------- Brady Syriac map (from run_hand_a_brady_language.py) -----------
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
    ok = brady_match(sk)
    # Return the skeleton as the "decoded" token, tag connector status
    is_conn = sk in BRADY_CONNECTORS
    return sk, ok, is_conn

# ----------- Schechter Latin-Occitan (word-level) -----------
SCHECHTER = {}
with (ROOT / "raw/schechter_glossary.csv").open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        SCHECHTER[r["eva"]] = r["decoded"].upper()
# Connectors: top Latin/Occitan function words in the decoded values
SCHECHTER_CONNECTORS_VALUES = {"ET","IN","DE","AD","EST","CUM","EX","NON",
    "SED","PER","VEL","SI","AC","QUOD","QUIA","OR","AN","AL","AM","AUT",
    "NEC","QUE","SUB","SUPER","O","E","EN","A","LA","LO","LAS","LI",
    "AC","ALS","NI"}

def schechter_decode(word):
    decoded = SCHECHTER.get(word)
    if decoded is None:
        return word, False, False  # unmatched; treat as unmatched content
    is_conn = decoded in SCHECHTER_CONNECTORS_VALUES
    return decoded, True, is_conn

# ----------- Pagel trilingual (word-level) -----------
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

# ----------- Gather Hand A lines -----------
hand_a_lines_raw = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A": continue
    for line in f["lines"]:
        if len(line["words"]) >= 3:
            hand_a_lines_raw.append(line["words"])

total_tokens = sum(len(L) for L in hand_a_lines_raw)
print(f"Hand A lines >=3 tokens: {len(hand_a_lines_raw)}, "
      f"total tokens: {total_tokens}")

# ----------- Decode + measure per map -----------
def decode_lines(decode_fn, lines):
    decoded_lines = []
    for L in lines:
        dec = [decode_fn(w) for w in L]
        decoded_lines.append(dec)
    return decoded_lines

def conn_content_rate(line):
    conn_n = 0; hits = 0
    for a, b in zip(line, line[1:]):
        (a_tok, a_ok, a_is_conn) = a
        (b_tok, b_ok, b_is_conn) = b
        if a_is_conn:
            conn_n += 1
            if b_ok and not b_is_conn:
                hits += 1
    return hits / conn_n if conn_n else 0

def shuffle_test(decoded_lines, seed=0):
    all_tokens = [t for L in decoded_lines for t in L]
    in_order_rates = [conn_content_rate(L) for L in decoded_lines]
    in_order = statistics.mean(in_order_rates) if in_order_rates else 0
    rng = random.Random(seed)
    shuffled = list(all_tokens); rng.shuffle(shuffled)
    rechunked = []
    idx = 0
    for L in decoded_lines:
        rechunked.append(shuffled[idx:idx+len(L)])
        idx += len(L)
    sh_rates = [conn_content_rate(L) for L in rechunked if len(L) >= 3]
    sh = statistics.mean(sh_rates) if sh_rates else 0
    # Token-level stats
    matched = sum(1 for t in all_tokens if t[1])
    conn_tokens = sum(1 for t in all_tokens if t[2])
    return {
        "n_tokens": len(all_tokens),
        "matched": matched, "match_rate": matched/len(all_tokens),
        "connectors": conn_tokens, "connector_rate": conn_tokens/len(all_tokens),
        "in_order": in_order, "shuffled": sh, "delta": in_order - sh,
    }

MAPS = [
    ("Brady-Syriac",       brady_decode),
    ("Schechter-LatinOcc", schechter_decode),
    ("Pagel-trilingual",   pagel_decode),
]

print("\n" + "="*72)
print("  MAP COMPARISON ON HAND A ALONE")
print("="*72)
print(f"  {'map':<22} {'match%':>8} {'conn%':>7} {'in-order':>10} "
      f"{'shuffled':>10} {'delta':>10}")

results = []
for name, fn in MAPS:
    dec = decode_lines(fn, hand_a_lines_raw)
    res = shuffle_test(dec)
    results.append({"map": name, **res})
    print(f"  {name:<22} {res['match_rate']*100:>7.1f}% {res['connector_rate']*100:>6.1f}% "
          f"{res['in_order']:>10.4f} {res['shuffled']:>10.4f} {res['delta']:>+10.4f}")

# Rank
ranking = sorted(results, key=lambda r: -r["delta"])
print("\n" + "="*72)
print("  RANKING BY DELTA (descending)")
print("="*72)
for rank, r in enumerate(ranking, 1):
    marker = " <-- PRIMARY" if rank == 1 else ""
    conf = "CONFIRMED" if r["delta"] >= 0.010 else (
        "MARGINAL" if r["delta"] > 0 else "REFUTED")
    print(f"  {rank}. {r['map']:<22} delta={r['delta']:+.4f}  [{conf}]{marker}")

winner = ranking[0]
print(f"\n  PRIMARY CANDIDATE FOR HAND A: {winner['map']}")
print(f"  (delta {winner['delta']:+.4f}, "
      f"match rate {winner['match_rate']*100:.1f}%)")

out = ROOT / "outputs" / "hand_a_map_comparison.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-HAND-A-MAP-COMPARISON-01",
    "locked_in_commit": "d95fce0",
    "hand_a_lines": len(hand_a_lines_raw),
    "total_tokens": total_tokens,
    "results": [
        {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}
        for r in results
    ],
    "ranking": [r["map"] for r in ranking],
    "primary_candidate": winner["map"],
    "primary_delta": round(winner["delta"], 4),
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
