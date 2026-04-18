"""Extract FORM (col 2) from CoNLL-U files, skipping comments, MWT ranges, and empty nodes.

Writes plaintext files where each sentence is one line, words whitespace-separated.
"""
import os
import sys

FILES = [
    "en_ewt-ud-train.conllu",
    "de_gsd-ud-train.conllu",
    "es_gsd-ud-train.conllu",
    "fr_gsd-ud-train.conllu",
    "fa_seraji-ud-train.conllu",
    "ta_ttb-ud-train.conllu",
    "te_mtg-ud-train.conllu",
    "ar_padt-ud-train.conllu",
    "he_htb-ud-train.conllu",
]

HERE = os.path.dirname(os.path.abspath(__file__))

def extract(conllu_path, txt_path):
    tokens = 0
    sentences = 0
    sentence = []
    with open(conllu_path, "r", encoding="utf-8") as fin, \
         open(txt_path, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.rstrip("\n")
            if not line:
                if sentence:
                    fout.write(" ".join(sentence) + "\n")
                    sentences += 1
                    sentence = []
                continue
            if line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 2:
                continue
            tok_id = fields[0]
            # Skip multi-word token ranges (e.g. "1-2") and empty nodes ("1.1")
            if "-" in tok_id or "." in tok_id:
                continue
            form = fields[1]
            if form == "_":
                continue
            sentence.append(form)
            tokens += 1
        if sentence:
            fout.write(" ".join(sentence) + "\n")
            sentences += 1
    return tokens, sentences

def main():
    results = []
    for fname in FILES:
        cpath = os.path.join(HERE, fname)
        if not os.path.exists(cpath):
            results.append((fname, None, None, None, "MISSING"))
            continue
        size = os.path.getsize(cpath)
        txt = os.path.join(HERE, fname.replace(".conllu", ".txt"))
        try:
            toks, sents = extract(cpath, txt)
            tsize = os.path.getsize(txt)
            results.append((fname, size, toks, sents, tsize))
        except Exception as e:
            results.append((fname, size, None, None, f"ERR:{e}"))
    # Print a terse table
    print(f"{'file':40} {'conllu_size':>12} {'tokens':>10} {'sents':>8} {'txt_size':>12}")
    for r in results:
        fname, csize, toks, sents, tsize = r
        print(f"{fname:40} {str(csize):>12} {str(toks):>10} {str(sents):>8} {str(tsize):>12}")

if __name__ == "__main__":
    main()
