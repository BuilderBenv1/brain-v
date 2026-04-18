"""Execute pre-registered H-BV-BL-MATTR-REPRODUCTION-01.

MATTR (2000-word window, sliding step 1) per Covington & McFall 2010 /
Gheuens 2019 / Bowern & Lindemann 2021.

Efficient sliding-window Counter implementation: O(N) instead of O(N*W).
"""
import json
import re
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")
REF_DIR = ROOT / "raw" / "corpus" / "reference-corpora"
WINDOW = 2000


def load_voynich_tokens(filter_fn=None):
    CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
    tokens = []
    for f in CORPUS["folios"]:
        if filter_fn and not filter_fn(f):
            continue
        for line in f["lines"]:
            for w in line["words"]:
                if w:
                    tokens.append(w.lower())
    return tokens


def load_ud_plaintext(path):
    if path.exists():
        text = path.read_text(encoding="utf-8", errors="ignore")
        tokens = [t for t in re.split(r"\s+", text.lower()) if t]
        return tokens
    return []


def load_esperanto():
    path = REF_DIR / "esperanto-sample.txt"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = [l for l in text.split("\n") if l.strip() and not l.startswith("===")]
    tokens = []
    for line in lines:
        for tok in re.split(r"\s+", line.lower()):
            tok = re.sub(r"[^\w]+", "", tok)
            if tok:
                tokens.append(tok)
    return tokens


def mattr(tokens, window=2000):
    n = len(tokens)
    if n < window + 1:
        return None, 0
    counts = Counter()
    for t in tokens[:window]:
        counts[t] += 1
    ttrs = []
    ttrs.append(len(counts) / window)
    for i in range(window, n):
        old = tokens[i - window]
        new = tokens[i]
        counts[new] += 1
        counts[old] -= 1
        if counts[old] == 0:
            del counts[old]
        ttrs.append(len(counts) / window)
    return statistics.mean(ttrs), len(ttrs)


print("Loading Voynichese subsets...")
hand_a = load_voynich_tokens(lambda f: f.get("currier_language") == "A")
hand_b = load_voynich_tokens(lambda f: f.get("currier_language") == "B")
hand_a_herbal = load_voynich_tokens(lambda f: f.get("currier_language") == "A" and f.get("section") == "herbal")
hand_b_herbal = load_voynich_tokens(lambda f: f.get("currier_language") == "B" and f.get("section") == "herbal")
full_manuscript = load_voynich_tokens(lambda f: True)

voynich_subsets = {
    "Voynich_HandA_all": hand_a,
    "Voynich_HandB_all": hand_b,
    "Voynich_HandA_herbal": hand_a_herbal,
    "Voynich_HandB_herbal": hand_b_herbal,
    "Voynich_full": full_manuscript,
}

print("Loading UD reference corpora...")
ref_families = {
    "Germanic": {
        "English_EWT": load_ud_plaintext(REF_DIR / "en_ewt-ud-train.txt"),
        "German_GSD": load_ud_plaintext(REF_DIR / "de_gsd-ud-train.txt"),
    },
    "Romance": {
        "Spanish_GSD": load_ud_plaintext(REF_DIR / "es_gsd-ud-train.txt"),
        "French_GSD": load_ud_plaintext(REF_DIR / "fr_gsd-ud-train.txt"),
    },
    "Iranian": {
        "Persian_Seraji": load_ud_plaintext(REF_DIR / "fa_seraji-ud-train.txt"),
    },
    "Semitic": {
        "Arabic_PADT": load_ud_plaintext(REF_DIR / "ar_padt-ud-train.txt"),
        "Hebrew_HTB": load_ud_plaintext(REF_DIR / "he_htb-ud-train.txt"),
    },
    "Vasconic": {
        "Basque_BDT": load_ud_plaintext(REF_DIR / "eu_bdt-ud-train.conllu"),
    },
    "Uralic": {
        "Hungarian_Szeged": load_ud_plaintext(REF_DIR / "hu_szeged-ud-train.conllu"),
    },
    "Turkic": {
        "Turkish_IMST": load_ud_plaintext(REF_DIR / "tr_imst-ud-train.conllu"),
    },
    "Dravidian": {
        "Tamil_TTB": load_ud_plaintext(REF_DIR / "ta_ttb-ud-train.txt"),
        "Telugu_MTG": load_ud_plaintext(REF_DIR / "te_mtg-ud-train.txt"),
    },
    "Constructed": {
        "Esperanto_Wiki": load_esperanto(),
    },
}

# Note: Basque/Hungarian/Turkish were downloaded as .conllu only (no extracted .txt)
# Need to extract FORM from their conllu
def load_conllu_forms(path):
    if not path.exists():
        return []
    tokens = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            if "-" in parts[0] or "." in parts[0]:
                continue
            form = parts[1].lower()
            if form and form != "_":
                tokens.append(form)
    return tokens


# Re-load Basque/Hungarian/Turkish from conllu
ref_families["Vasconic"]["Basque_BDT"] = load_conllu_forms(REF_DIR / "eu_bdt-ud-train.conllu")
ref_families["Uralic"]["Hungarian_Szeged"] = load_conllu_forms(REF_DIR / "hu_szeged-ud-train.conllu")
ref_families["Turkic"]["Turkish_IMST"] = load_conllu_forms(REF_DIR / "tr_imst-ud-train.conllu")

print("\n=== MATTR COMPUTATION (window=2000) ===")
results = {}

# Voynichese
print("\nVoynichese subsets:")
for name, tokens in voynich_subsets.items():
    m, n_windows = mattr(tokens, WINDOW)
    results[name] = {"tokens": len(tokens), "mattr": m, "n_windows": n_windows}
    m_str = f"{m:.4f}" if m is not None else "n/a (LOW-POWER)"
    print(f"  {name:<28} tokens={len(tokens):<7}  MATTR={m_str}  windows={n_windows}")

# Reference languages and family means
family_stats = {}
print("\nReference language families:")
for family, langs in ref_families.items():
    lang_mattrs = []
    print(f"  {family}:")
    for lang, tokens in langs.items():
        m, n_w = mattr(tokens, WINDOW)
        m_str = f"{m:.4f}" if m is not None else "n/a"
        print(f"    {lang:<22} tokens={len(tokens):<7}  MATTR={m_str}  windows={n_w}")
        results[f"{family}__{lang}"] = {"tokens": len(tokens), "mattr": m, "n_windows": n_w}
        if m is not None:
            lang_mattrs.append(m)
    family_mean = statistics.mean(lang_mattrs) if lang_mattrs else None
    family_stats[family] = {"mean": family_mean, "n_langs_available": len(lang_mattrs)}
    if family_mean is not None:
        print(f"    [{family} mean: {family_mean:.4f}, n={len(lang_mattrs)}]")

# Classify Hand A
hand_a_mattr = results["Voynich_HandA_all"]["mattr"]
hand_b_mattr = results["Voynich_HandB_all"]["mattr"]
hand_a_herbal_mattr = results["Voynich_HandA_herbal"]["mattr"]
hand_b_herbal_mattr = results["Voynich_HandB_herbal"]["mattr"]
full_mattr = results["Voynich_full"]["mattr"]

NON_AGGLUT = ["Germanic", "Romance", "Iranian", "Semitic"]
AGGLUT = ["Turkic", "Uralic", "Vasconic", "Dravidian"]


def classify(hand_mattr, hand_name):
    print(f"\n  {hand_name} MATTR = {hand_mattr:.4f}")
    print(f"  Distances to family means:")
    distances = {}
    for family, s in family_stats.items():
        if s["mean"] is None:
            continue
        d = abs(hand_mattr - s["mean"])
        distances[family] = d
        print(f"    {family:<14} mean={s['mean']:.4f}  distance={d:.4f}")
    closest = min(distances, key=distances.get)
    closest_d = distances[closest]
    non_ag_d = min(distances[f] for f in NON_AGGLUT if f in distances)
    ag_d = min(distances[f] for f in AGGLUT if f in distances)
    print(f"\n  Closest family: {closest} (distance {closest_d:.4f})")
    print(f"  Closest NON-agglutinative: {non_ag_d:.4f}")
    print(f"  Closest AGGLUTINATIVE: {ag_d:.4f}")
    ratio = ag_d / non_ag_d if non_ag_d > 0 else float("inf")
    print(f"  Ratio (ag/non-ag): {ratio:.2f}")

    if closest in NON_AGGLUT and ratio >= 2.0:
        bin_v = "BIN_1_BL_CONFIRMED"
    elif closest in AGGLUT and (non_ag_d / ag_d if ag_d > 0 else 0) >= 2.0:
        bin_v = "BIN_2_BL_CONTRADICTED"
    else:
        bin_v = "BIN_3_AMBIGUOUS"
    print(f"  CLASSIFICATION: {bin_v}")
    return {"closest": closest, "distances": distances, "bin": bin_v, "ratio_ag_non_ag": ratio}


print("\n" + "=" * 78)
print("  CLASSIFICATION per hand / subset")
print("=" * 78)
classifications = {}
classifications["HandA_all"] = classify(hand_a_mattr, "Hand A (all)")
classifications["HandB_all"] = classify(hand_b_mattr, "Hand B (all)")
if hand_a_herbal_mattr:
    classifications["HandA_herbal"] = classify(hand_a_herbal_mattr, "Hand A herbal")
if hand_b_herbal_mattr:
    classifications["HandB_herbal"] = classify(hand_b_herbal_mattr, "Hand B herbal")
classifications["full_manuscript"] = classify(full_mattr, "Voynich full manuscript")

out = {
    "generated": "2026-04-18",
    "hypothesis": "H-BV-BL-MATTR-REPRODUCTION-01",
    "window_size": WINDOW,
    "methodology": "B&L 2021 LV §3.4 — Moving Average TTR with 2000-word window, sliding step 1",
    "raw_mattr": {k: {"tokens": v["tokens"], "mattr": round(v["mattr"], 4) if v["mattr"] else None, "n_windows": v["n_windows"]} for k, v in results.items()},
    "family_means": {k: {"mean": round(v["mean"], 4) if v["mean"] else None, "n_langs": v["n_langs_available"]} for k, v in family_stats.items()},
    "classifications": {k: {"closest_family": v["closest"], "distances": {f: round(d, 4) for f, d in v["distances"].items()}, "bin": v["bin"], "ratio_ag_non_ag": round(v["ratio_ag_non_ag"], 4)} for k, v in classifications.items()},
    "non_agglutinative_families": NON_AGGLUT,
    "agglutinative_families": AGGLUT,
}
out_path = ROOT / "outputs" / "bl_mattr_reproduction_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")

# Prior finding summary
print("\n=== COMPARISON TO BRAIN-V PRIOR AGGLUTINATIVE FINDING ===")
print("  H-BV-AGGLUTINATIVE-EXPANSION-01 (M1-M5 profile): Hand A BASQUE_UNIQUELY_BEST (distance 0.0, 6/6)")
print(f"  This test (B&L MATTR methodology): Hand A classified {classifications['HandA_all']['bin']}, closest to {classifications['HandA_all']['closest']}")
