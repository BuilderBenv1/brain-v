"""
Execute pre-registered H-BV-HAND-A-LANGUAGE-SCREEN-02.

Seven-language frequency-rank substitution screen against Hand A.
For each candidate: sort Hand-A EVA glyph-units by frequency, map rank-by-rank
to that language's published letter-frequency ranking, decode Hand-A tokens,
measure connector-content bigram delta via shuffle test (identical methodology
to Brady/Pagel/Schechter prior runs).

Thresholds:
  max delta >= +0.010 -> CONFIRMED (promote to primary hypothesis)
  +0.005 < max delta < +0.010 -> MARGINAL (secondary hypothesis)
  max delta <= +0.005 -> REFUTED (frequency-rank substitution eliminated for
    all seven; redirect to cipher/constructed/shorthand models)

Letter-frequency sources:
  italian  -- Bortolini, Tagliavini, Zampolli (1971) Lessico di frequenza
              / CoLFIS (Laudanna et al. 1995) aggregate ranking
  german   -- Leipzig Corpora Collection / Beutelspacher (1993)
  finnish  -- Kielipankki FINTWOL / Hakulinen et al. 2004
  hungarian-- Szószablya Hungarian corpus / Oravecz et al. 2014
  basque   -- Ereduzko Prosa Gaur (EPG) / Sarasola 2007
  ottoman_turkish -- TS Corpus (Aksan et al. 2012) modern-Turkish proxy
              (Ottoman's Arabic-script orthography is not directly comparable
              to EVA's Latin-ish glyph set; modern Turkish is the standard
              Latin-alphabet proxy used in historical comparative studies)
  armenian -- Eastern Armenian National Corpus, Hübschmann-Meillet
              transliteration ranking
"""
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))

# =============================================================================
# EVA tokenization — collapse benched/capped gallows to single glyph-units
# =============================================================================
MULTI_GLYPHS = ["ckh", "cth", "cph", "ch", "sh"]  # longest-first order

def eva_tokenize(word):
    out = []; i = 0
    while i < len(word):
        matched = False
        for t in MULTI_GLYPHS:
            if word.startswith(t, i):
                out.append(t); i += len(t); matched = True; break
        if not matched:
            out.append(word[i]); i += 1
    return out

# =============================================================================
# Candidate language specs
# =============================================================================
# Each lang has:
#   letters: string of letters in DESCENDING frequency order (top ~20 used)
#   connectors: function words (top 10-15); must be in top-80 of frequency list
#   content: content-word proxy lexicon (60-70 common substantives, mostly
#            matching herbal/medicinal/domestic vocabulary)
#
# Lexicon scope: 75-85 total entries per language; first block is connectors,
# remainder is content. Same size band as Brady's 71-skeleton proxy.

LANGUAGES = {
    "italian": {
        "letters": "eaionlrtscdpumvghbfzq",
        "connectors": [
            "e", "di", "il", "la", "che", "in", "per", "con", "non",
            "un", "una", "lo", "le", "al", "del"
        ],
        "content": [
            "acqua", "fuoco", "terra", "aria", "foglia", "fiore", "pianta",
            "radice", "olio", "erba", "sale", "calore", "freddo", "umido",
            "secco", "caldo", "corpo", "sangue", "cuore", "mano", "occhio",
            "testa", "piede", "pelle", "capo", "carne", "osso", "latte",
            "vino", "pane", "miele", "seme", "frutto", "ramo", "albero",
            "bosco", "prato", "monte", "valle", "mare", "sole", "luna",
            "stella", "giorno", "notte", "ora", "tempo", "anno", "mese",
            "uomo", "donna", "figlio", "madre", "padre", "amore", "vita",
            "morte", "anima", "mente", "dio", "santo", "legge", "forza",
            "forma", "colore", "luce", "ombra", "piede", "dente", "labbra"
        ],
    },
    "german": {
        "letters": "enisrathdulcgmobwfkzp",
        "connectors": [
            "der", "die", "das", "und", "ist", "ein", "in", "zu", "ich",
            "nicht", "dem", "den", "mit", "von", "es"
        ],
        "content": [
            "blatt", "blume", "pflanze", "wurzel", "oel", "kraut", "salz",
            "wasser", "feuer", "erde", "luft", "frau", "mann", "kind",
            "herz", "hand", "auge", "tag", "nacht", "mond", "sonne",
            "stern", "stunde", "jahr", "monat", "zeit", "licht", "schatten",
            "koerper", "blut", "milch", "wein", "brot", "honig", "samen",
            "frucht", "zweig", "baum", "wald", "wiese", "berg", "tal",
            "meer", "see", "fluss", "stein", "sand", "eis", "schnee",
            "feld", "haus", "stadt", "dorf", "weg", "leben", "tod",
            "seele", "geist", "liebe", "glaube", "gesetz", "kraft",
            "form", "farbe", "name", "gott", "koenig", "fuss", "mund"
        ],
    },
    "finnish": {
        "letters": "aintesloukmhjvrpydao",
        "connectors": [
            "ja", "on", "ei", "se", "etta", "kuin", "mutta", "tai",
            "niin", "joka", "myos", "jos", "nyt", "jo", "vain"
        ],
        "content": [
            "lehti", "kukka", "kasvi", "juuri", "oljy", "yrtti", "suola",
            "vesi", "tuli", "maa", "ilma", "nainen", "mies", "lapsi",
            "sydan", "kasi", "silma", "paiva", "yo", "kuu", "aurinko",
            "tahti", "tunti", "vuosi", "kuukausi", "aika", "valo", "varjo",
            "keho", "veri", "maito", "viini", "leipa", "hunaja", "siemen",
            "hedelma", "oksa", "puu", "metsa", "niitty", "vuori", "laakso",
            "meri", "jarvi", "joki", "kivi", "hiekka", "jaa", "lumi",
            "pelto", "talo", "kaupunki", "kyla", "tie", "elama", "kuolema",
            "sielu", "henki", "rakkaus", "usko", "laki", "voima",
            "muoto", "vari", "nimi", "jumala", "kuningas", "jalka", "suu"
        ],
    },
    "hungarian": {
        "letters": "eatlnksozirmgydvbhjf",
        "connectors": [
            "a", "az", "es", "van", "hogy", "nem", "ez", "egy", "volt",
            "mint", "is", "csak", "meg", "el", "be"
        ],
        "content": [
            "level", "virag", "noveny", "gyoker", "olaj", "fu", "so",
            "viz", "tuz", "fold", "leveg", "no", "ferfi", "gyerek",
            "sziv", "kez", "szem", "nap", "ej", "hold", "csillag",
            "ora", "ev", "honap", "ido", "feny", "arny", "test", "ver",
            "tej", "bor", "kenyer", "mez", "mag", "gyumolcs", "ag",
            "fa", "erdo", "ret", "hegy", "volgy", "tenger", "to", "folyo",
            "ko", "homok", "jeg", "ho", "mezo", "haz", "varos", "falu",
            "ut", "elet", "halal", "lelek", "szellem", "szeretet",
            "hit", "torveny", "ero", "alak", "szin", "nev", "isten",
            "kiraly", "lab", "szaj"
        ],
    },
    "basque": {
        "letters": "aeirntoklusdbzghpmjf",
        "connectors": [
            "eta", "da", "ez", "bat", "du", "hau", "dira", "baita", "ere",
            "baina", "edo", "oso", "zein", "hor", "hori"
        ],
        "content": [
            "hosto", "lore", "landare", "sustrai", "olio", "belar", "gatz",
            "ur", "su", "lur", "haize", "emakume", "gizon", "haur",
            "bihotz", "esku", "begi", "egun", "gau", "ilargi", "eguzki",
            "izar", "ordu", "urte", "hilabete", "denbora", "argi", "itzal",
            "gorputz", "odol", "esne", "ardo", "ogi", "ezti", "hazi",
            "fruitu", "adar", "zuhaitz", "baso", "larre", "mendi", "haran",
            "itsaso", "aintzira", "ibai", "harri", "hondar", "izotz", "elur",
            "soro", "etxe", "hiri", "herri", "bide", "bizitza", "heriotza",
            "arima", "espiritu", "maitasun", "sinesmen", "lege", "indar",
            "forma", "kolore", "izen", "jainko", "errege", "oin", "aho"
        ],
    },
    "ottoman_turkish": {
        "letters": "aeinrlkdmtsyuboshgcp",
        "connectors": [
            "ve", "bu", "su", "ne", "ki", "da", "de", "bir", "icin",
            "ile", "en", "cok", "ama", "degil", "olan"
        ],
        "content": [
            "yaprak", "cicek", "bitki", "kok", "yag", "ot", "tuz",
            "su", "ates", "toprak", "hava", "kadin", "erkek", "cocuk",
            "kalp", "el", "goz", "gun", "gece", "ay", "gunes", "yildiz",
            "saat", "yil", "zaman", "isik", "golge", "vucut", "kan",
            "sut", "sarap", "ekmek", "bal", "tohum", "meyve", "dal",
            "agac", "orman", "cayir", "dag", "vadi", "deniz", "gol",
            "irmak", "tas", "kum", "buz", "kar", "tarla", "ev", "sehir",
            "koy", "yol", "hayat", "olum", "ruh", "can", "sevgi",
            "inanc", "kanun", "guc", "sekil", "renk", "ad", "tanri",
            "kral", "ayak", "agiz"
        ],
    },
    "armenian": {
        "letters": "aneirtukslomhvgdypbc",
        "connectors": [
            "ev", "na", "te", "mi", "ayl", "bayts", "kam", "vor", "ur",
            "inch", "or", "ays", "ayd", "ayn", "bolor"
        ],
        "content": [
            "terev", "tsaghik", "busn", "armat", "yugh", "khot", "agh",
            "jur", "krak", "hogh", "od", "kin", "ayr", "yerekha",
            "sirt", "dzerk", "ach", "or", "gisher", "lusin", "arev",
            "astgh", "zham", "tari", "amis", "zhamanak", "luys", "stver",
            "marmin", "aryun", "kat", "gini", "hats", "meghr", "sermn",
            "mrgi", "chiugh", "tsar", "antar", "dasht", "sar", "hovit",
            "tsov", "litsh", "get", "kar", "avaz", "sarn", "dzyun",
            "tun", "kaghak", "giwgh", "chanaparh", "kyank", "mah",
            "hogi", "vogi", "ser", "havatk", "orenq", "uzh", "tsev",
            "guyn", "anun", "astvats", "tagavor", "otq", "beran"
        ],
    },
}

# =============================================================================
# Build Hand-A corpus: per-line sequences of (raw_word, eva_tokens)
# =============================================================================
hand_a_lines = []
eva_freq = Counter()
for f in CORPUS["folios"]:
    if f.get("currier_language") != "A":
        continue
    for line in f["lines"]:
        toks = []
        for w in line["words"]:
            t = eva_tokenize(w)
            toks.append(t)
            for g in t:
                eva_freq[g] += 1
        if len(toks) >= 3:
            hand_a_lines.append(toks)

n_lines = len(hand_a_lines)
total_words = sum(len(L) for L in hand_a_lines)
print(f"Hand A: {n_lines} lines, {total_words} tokens")
print(f"EVA glyph-units seen: {len(eva_freq)}")

# Descending-frequency EVA glyph list (top 20 will be mapped)
eva_rank = [g for g, _ in eva_freq.most_common()]
print(f"\nTop-20 Hand-A EVA glyphs by frequency:")
total_glyphs = sum(eva_freq.values())
for i, g in enumerate(eva_rank[:20], 1):
    print(f"  {i:>2}. {g:<4} {eva_freq[g]:>5} ({100*eva_freq[g]/total_glyphs:.2f}%)")

# =============================================================================
# Per-language decode & shuffle test
# =============================================================================
def decode_line(toks_line, eva_to_letter):
    decoded = []
    for eva_toks in toks_line:
        out = "".join(eva_to_letter.get(g, "") for g in eva_toks)
        decoded.append(out)
    return decoded

def match(word, lexicon):
    """Return (matched, is_connector). Exact or single-char-insertion match."""
    if not word: return False, False
    connectors = lexicon["_connectors"]
    if word in lexicon:
        return True, (word in connectors)
    # single-char insertion tolerance (drop one char)
    for i in range(len(word)):
        cand = word[:i] + word[i+1:]
        if cand in lexicon:
            return True, (cand in connectors)
    return False, False

def conn_content_rate(stream):
    """stream = list of (matched, is_connector). Rate of connector followed
    by matched-non-connector."""
    conn_n = 0; hits = 0
    for a, b in zip(stream, stream[1:]):
        _, a_conn = a
        b_m, b_conn = b
        if a_conn:
            conn_n += 1
            if b_m and not b_conn:
                hits += 1
    return hits / conn_n if conn_n else 0.0

results = []
RANDOM_SEED = 0

for lang_name, spec in LANGUAGES.items():
    letters = spec["letters"]
    # Strip any duplicates, take top-20
    seen = set(); clean = []
    for c in letters:
        if c not in seen:
            seen.add(c); clean.append(c)
    letters_ranked = clean[:20]

    # Build rank-by-rank EVA -> letter map (top 20 glyphs)
    eva_to_letter = {}
    for i, g in enumerate(eva_rank[:20]):
        if i < len(letters_ranked):
            eva_to_letter[g] = letters_ranked[i]
        else:
            eva_to_letter[g] = ""

    # Lexicon
    lexicon = {}
    connectors = set()
    for w in spec["connectors"]:
        lexicon[w] = True
        connectors.add(w)
    for w in spec["content"]:
        lexicon[w] = True
    lexicon["_connectors"] = connectors

    # Decode all lines
    decoded_lines = [decode_line(L, eva_to_letter) for L in hand_a_lines]

    # Stream per line = [(matched, is_conn), ...]
    line_streams = []
    for dec in decoded_lines:
        stream = []
        for w in dec:
            m, c = match(w, lexicon)
            stream.append((m, c))
        line_streams.append(stream)

    # Totals
    all_stream = [t for L in line_streams for t in L]
    n_tokens = len(all_stream)
    n_match = sum(1 for m, _ in all_stream if m)
    n_conn = sum(1 for m, c in all_stream if m and c)

    # In-order rate
    in_order_rates = [conn_content_rate(L) for L in line_streams if len(L) >= 3]
    in_order = statistics.mean(in_order_rates) if in_order_rates else 0.0

    # Shuffled (same seed/method as Brady Hand-A test)
    rng = random.Random(RANDOM_SEED)
    all_tokens = [t for L in line_streams for t in L]
    shuffled_pool = list(all_tokens)
    rng.shuffle(shuffled_pool)
    shuffled_lines = []
    idx = 0
    for L in line_streams:
        shuffled_lines.append(shuffled_pool[idx:idx+len(L)])
        idx += len(L)
    shuffled_rates = [conn_content_rate(L) for L in shuffled_lines if len(L) >= 3]
    shuffled = statistics.mean(shuffled_rates) if shuffled_rates else 0.0

    delta = in_order - shuffled

    results.append({
        "language": lang_name,
        "eva_to_letter": eva_to_letter,
        "n_tokens": n_tokens,
        "matched_tokens": n_match,
        "match_rate": round(n_match/n_tokens, 4) if n_tokens else 0,
        "matched_as_connector": n_conn,
        "in_order": round(in_order, 4),
        "shuffled": round(shuffled, 4),
        "delta": round(delta, 5),
    })

# =============================================================================
# Print ranked results
# =============================================================================
results.sort(key=lambda r: r["delta"], reverse=True)
print("\n" + "="*78)
print("  SEVEN-LANGUAGE FREQUENCY-RANK SCREEN — Hand A")
print("="*78)
print(f"  {'rank':<5}{'language':<18}{'match%':>8}{'in-order':>12}"
      f"{'shuffled':>12}{'delta':>12}")
for i, r in enumerate(results, 1):
    print(f"  {i:<5}{r['language']:<18}{r['match_rate']*100:>7.2f}%"
          f"{r['in_order']:>12.4f}{r['shuffled']:>12.4f}"
          f"{r['delta']:>+12.5f}")

# =============================================================================
# Decision
# =============================================================================
best = results[0]
best_delta = best["delta"]

print("\n" + "="*78)
print("  PRE-REGISTERED DECISION")
print("="*78)

if best_delta >= 0.010:
    verdict = "CONFIRMED"
    print(f"  Best delta {best_delta:+.5f} ({best['language']}) >= +0.010")
    print(f"  -> CONFIRMED. Promote {best['language']} to primary Hand-A hypothesis.")
elif best_delta > 0.005:
    verdict = "MARGINAL"
    print(f"  Best delta {best_delta:+.5f} ({best['language']}) in (+0.005, +0.010)")
    print(f"  -> MARGINAL. {best['language']} becomes secondary hypothesis;")
    print(f"     further tests needed before promotion.")
else:
    verdict = "REFUTED"
    print(f"  Best delta {best_delta:+.5f} ({best['language']}) <= +0.005")
    print(f"  -> REFUTED. Simple frequency-rank substitution eliminated for all")
    print(f"     seven candidates. Redirect effort from language-substitution to")
    print(f"     cipher/constructed/shorthand models.")

# Comparison to prior runs
print(f"\n  For comparison:")
print(f"    Brady (Syriac, Hand A only):     +0.0044 (MARGINAL sub-threshold)")
print(f"    Brady (Syriac, full corpus):     -0.0098 (REFUTED)")

# =============================================================================
# Save output
# =============================================================================
out_path = ROOT / "outputs" / "hand_a_language_screen.json"
out_path.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-HAND-A-LANGUAGE-SCREEN-02",
    "n_hand_a_lines": n_lines,
    "n_hand_a_tokens": total_words,
    "eva_glyph_ranking_top20": eva_rank[:20],
    "candidates_tested": list(LANGUAGES.keys()),
    "lexicon_size_per_language": {k: len(v["connectors"]) + len(v["content"])
                                   for k, v in LANGUAGES.items()},
    "ranked_results": results,
    "best_delta": best_delta,
    "best_language": best["language"],
    "verdict": verdict,
    "thresholds": {
        "confirmed": "delta >= +0.010",
        "marginal": "+0.005 < delta < +0.010",
        "refuted": "delta <= +0.005",
    },
    "comparison_priors": {
        "brady_hand_a_only_delta": 0.0044,
        "brady_full_corpus_delta": -0.0098,
    },
}, indent=2), encoding="utf-8")
print(f"\nSaved: {out_path}")
