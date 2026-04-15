"""
Extract Schechter's glossary from voynich-decoded/tools/glossary-export.js
into a flat CSV: eva,decoded,language

Language classification mirrors decode.js:classifyLanguage:
  - HEBREW_WORDS set -> hebrew
  - OCCITAN_WORDS set -> occitan
  - else -> latin
"""
import csv
import json
import re
from pathlib import Path

SRC = Path(r"C:\Projects\voynich-decoded\tools\glossary-export.js")
OUT = Path(r"C:\Projects\brain-v\raw\schechter_glossary.csv")

HEBREW_WORDS = {
    "SHALOM", "ADAR", "GEDI", "QAISAR", "ILAN", "TELI", "TAHOR",
    "TAMEI", "TEOM", "DELI",
}
OCCITAN_WORDS = {
    "OR", "LAIN", "BAIN", "SAIN", "TAIN", "FRAN", "LOR", "AL", "LAS",
    "NOCAN", "FOCAN", "NOCAR", "FOCAR", "ODAR", "SARE", "HABE",
    "AN", "BEN", "DES", "HEC", "HIS", "AC", "las", "ALS",
    "LAVAR", "BAIR", "FAIR", "LAIR", "GARUM", "AIRAT",
}

def classify(word: str) -> str:
    if not word or word.startswith("["):
        return "undecoded"
    if word in HEBREW_WORDS:
        return "hebrew"
    if word in OCCITAN_WORDS:
        return "occitan"
    return "latin"

text = SRC.read_text(encoding="utf-8")
m = re.search(r"\{.*\}", text, re.DOTALL)
gloss = json.loads(m.group(0))

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["eva", "decoded", "language"])
    for eva, decoded in gloss.items():
        w.writerow([eva, decoded, classify(decoded)])

by_lang = {}
for v in gloss.values():
    lang = classify(v)
    by_lang[lang] = by_lang.get(lang, 0) + 1
print(f"Wrote {len(gloss)} entries to {OUT}")
print(f"By language: {by_lang}")
