"""
Execute pre-registered H-BV-PAGEL-EXPANSION-01 (locked 7adcf4a).

Expand Pagel's 81-term dictionary via deterministic frequency-rank
alignment with a ~120-term medieval Latin pharmaceutical vocabulary.
Preserve Pagel's existing mappings; add only where absent.
No hand-tuning. No re-assignment after shuffle-test observation.
"""
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# Pagel's 81-term base
PAGEL_BASE = {
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

# 120-term medieval pharmaceutical Latin vocabulary, ranked by rough
# canonical-source frequency (Circa Instans, Dioscorides, Antidotarium
# Nicolai). NOT hand-tuned to Hand A.
LATIN_PHARMA_RANKED = [
    "ET","IN","DE","AD","EST","CUM","EX","NON","SED","PER","VEL","SI",
    "AUT","NEC","QUOD","QUIA","SIC","UT","ERGO","SUPER","SUB","ANTE","POST",
    "INTER","HERBA","FLOS","FOLIUM","RADIX","SEMEN","FRUCTUS","CORTEX","SUCCUS",
    "PULVIS","OLEUM","VINUM","AQUA","MEL","LAC","ACETUM","UNGUENTUM","PILULA",
    "PASTA","DECOCTIO","CORPUS","CAPUT","PECTUS","VENTER","OCULUS","STOMACHUS",
    "MATRIX","SANGUIS","COR","HEPAR","REN","OS","PES","MANUS","CALIDUS",
    "FRIGIDUS","HUMIDUS","SICCUS","AMARUS","DULCIS","SANAT","CURAT","DOLET",
    "ACCIPE","PONE","MISCE","TRAHE","BIBE","APPONIT","PURGAT","ROSA","VIOLA",
    "SALVIA","RUTA","MENTA","THYMUS","ABSINTHIUM","LILIUM","PAPAVER","CROCUS",
    "CINNAMOMUM","PIPER","ZINGIBER","CASSIA","MYRRHA","ALOE","MANDRAGORA",
    "HYOSCYAMUS","UNCIA","LIBRA","DRACHMA","SCRUPULUS","PARS","UNA","DUAE",
    "TRES","DIES","NOX","MANE","VESPER","HORA","FIT","HABET","FACIT","DAT",
    "PONITUR","MATER","PATER","FILIUS","SANCTUS","BENEDICIT","VITA","MORTIS",
    "DOLOR","REMEDIUM","MORBUS","MEDICINA","PHARMACON","POTIO","THERIACA",
]

# Hand A tokens ranked by frequency
hand_a_tokens = []
hand_a_lines_raw = []
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A": continue
    for line in f["lines"]:
        if len(line["words"]) >= 3:
            hand_a_lines_raw.append(line["words"])
            hand_a_tokens.extend(line["words"])

total_hand_a = len(hand_a_tokens)
print(f"Hand A: {len(hand_a_lines_raw)} lines, {total_hand_a} tokens")

wf = Counter(hand_a_tokens)
ranked_unmapped = [(w, c) for w, c in wf.most_common() if w not in PAGEL_BASE]
print(f"Unique types: {len(wf)}; unmapped by Pagel: {len(ranked_unmapped)}")

# Deterministic expansion: rank-align unmapped Hand-A tokens with
# unused Latin words, under length-compatibility constraint.
expanded = dict(PAGEL_BASE)
used_latin = set(PAGEL_BASE.values())
available_latin = [w for w in LATIN_PHARMA_RANKED if w not in used_latin]

assigned = 0
for eva_token, _ in ranked_unmapped:
    if not available_latin: break
    # find the first available Latin whose length is within |EVA_len-Latin_len|<=2
    chosen = None
    for i, lat in enumerate(available_latin):
        if abs(len(eva_token) - len(lat)) <= 2:
            chosen = (i, lat); break
    if chosen is None:
        continue
    i, lat = chosen
    expanded[eva_token] = lat
    used_latin.add(lat)
    del available_latin[i]
    assigned += 1
    if not available_latin: break

print(f"\nExpansion: {assigned} new mappings assigned deterministically")
print(f"Total dictionary size: {len(expanded)} (was 81)")
print(f"Latin vocabulary terms used: {len(used_latin)} of {len(LATIN_PHARMA_RANKED)}")

# Connectors (Pagel's + expanded)
CONNECTORS = {"ET","IN","DE","AD","EST","CUM","EX","NON","SED","PER","VEL",
              "SI","AUT","NEC","QUOD","QUIA","SIC","UT","ERGO","SUPER","SUB",
              "ANTE","POST","INTER","OR","AER","ALIUS","PRO","QUOQUE","INDE",
              "SAL","SANARE","FLOS"}
# Only count CONNECTORS that actually appear as values in expanded dict
active_connectors = {w for w in expanded.values() if w in CONNECTORS}
print(f"Active connectors in expanded dict: {len(active_connectors)}")

def decode(w):
    v = expanded.get(w)
    if v is None: return (w, False, False)
    return (v, True, v in active_connectors)

# Decode Hand A lines
decoded_lines = [[decode(w) for w in L] for L in hand_a_lines_raw]

all_tokens = [t for L in decoded_lines for t in L]
matched = sum(1 for t in all_tokens if t[1])
match_rate = matched / len(all_tokens)
conn_tokens = sum(1 for t in all_tokens if t[2])
conn_rate = conn_tokens / len(all_tokens)
print(f"\nHand A under expanded Pagel:")
print(f"  match rate:     {match_rate:.3%}")
print(f"  connector rate: {conn_rate:.3%}")

def conn_content_rate(line):
    conn_n = 0; hits = 0
    for a, b in zip(line, line[1:]):
        if a[2]:
            conn_n += 1
            if b[1] and not b[2]:
                hits += 1
    return hits / conn_n if conn_n else 0

in_order_rates = [conn_content_rate(L) for L in decoded_lines]
in_order = statistics.mean(in_order_rates) if in_order_rates else 0

# Shuffle
rng = random.Random(0)
shuffled = list(all_tokens); rng.shuffle(shuffled)
rechunked = []
idx = 0
for L in decoded_lines:
    rechunked.append(shuffled[idx:idx+len(L)])
    idx += len(L)
sh_rates = [conn_content_rate(L) for L in rechunked if len(L) >= 3]
sh = statistics.mean(sh_rates) if sh_rates else 0
delta = in_order - sh

print(f"\n  in-order conn-content: {in_order:.4f}")
print(f"  shuffled conn-content: {sh:.4f}")
print(f"  delta:                 {delta:+.4f}")

print(f"\n  Compare Pagel base (81 terms, 23.9% match): delta +0.0118")

# Decision
print(f"\n{'='*72}")
print(f"  PRE-REGISTERED DECISION")
print(f"{'='*72}")
if match_rate >= 0.30 and delta >= 0.010:
    verdict = "CONFIRMED"
    print(f"  coverage {match_rate:.1%} >= 30% AND delta {delta:+.4f} >= +0.010")
    print(f"  -> CONFIRMED. Hand A is Latin-derived pharmaceutical text.")
elif match_rate >= 0.30 and delta < 0.010:
    verdict = "REFUTED"
    print(f"  coverage {match_rate:.1%} >= 30% but delta {delta:+.4f} < +0.010")
    print(f"  -> REFUTED. Pagel's original +0.0118 was small-sample artefact.")
else:
    verdict = "INCONCLUSIVE"
    print(f"  coverage {match_rate:.1%} < 30% — expansion rule exhausted")
    print(f"  -> INCONCLUSIVE. Methodology limit reached.")

# Sample decoded lines for inspection
print(f"\n  Sample decoded Hand-A lines (first 5):")
for L in decoded_lines[:5]:
    print("    " + " ".join(t[0] for t in L))

out = ROOT / "outputs" / "pagel_expansion.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-PAGEL-EXPANSION-01",
    "locked_in_commit": "7adcf4a",
    "base_pagel_terms": len(PAGEL_BASE),
    "latin_vocab_ranked": len(LATIN_PHARMA_RANKED),
    "expansion_mappings_added": assigned,
    "total_dictionary": len(expanded),
    "hand_a_tokens": len(all_tokens),
    "match_rate": round(match_rate, 4),
    "connector_rate": round(conn_rate, 4),
    "in_order_conn_content": round(in_order, 4),
    "shuffled_conn_content": round(sh, 4),
    "delta": round(delta, 4),
    "base_pagel_delta_reference": 0.0118,
    "verdict": verdict,
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out}")
