"""
Execute pre-registered H-BV-SYLLABLE-LEVEL-01 (locked 2c2e471).

Per Hand-A plant folio: Pearson r and Spearman rho between
x = Hand-A token count, y = Sherwood medicinal_use+notes char length
as proxy for canonical pharma-entry length.

Decision rule LOCKED:
  r > 0.5 AND rho > 0.4 -> CONFIRMED
  0.3 < r <= 0.5 -> MARGINAL
  r <= 0.3 -> REFUTED
"""
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from scipy import stats

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
PLANT_CSV = ROOT / "raw/research/plant-identifications.csv"

# Hand A token count per folio
folio_token_count = {}
folio_hand = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_hand[fid] = f.get("currier_language", "?")
    count = sum(len(line["words"]) for line in f["lines"])
    folio_token_count[fid] = count

# Sherwood/Cohen proxy text lengths (exclude CONFLICT)
data = []
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        fid = r["folio"]
        if folio_hand.get(fid) != "A": continue
        if fid not in folio_token_count: continue
        if folio_token_count[fid] < 20: continue
        proxy_text = (r.get("medicinal_use") or "") + " " + (r.get("notes") or "")
        proxy_len = len(proxy_text.strip())
        if proxy_len == 0: continue  # skip folios with no proxy data
        data.append({
            "folio": fid,
            "latin": r.get("latin_name") or "",
            "common": r.get("common_name") or "",
            "tokens": folio_token_count[fid],
            "proxy_len": proxy_len,
        })

print(f"Hand-A plant folios with both token count and proxy text: {len(data)}")

xs = [d["tokens"] for d in data]
ys = [d["proxy_len"] for d in data]

print(f"\n  Token count: mean {statistics.mean(xs):.1f}, "
      f"sd {statistics.pstdev(xs):.1f}, min {min(xs)}, max {max(xs)}")
print(f"  Proxy length: mean {statistics.mean(ys):.1f}, "
      f"sd {statistics.pstdev(ys):.1f}, min {min(ys)}, max {max(ys)}")

# Pearson r
r_pearson, p_pearson = stats.pearsonr(xs, ys)
# Spearman rho
r_spearman, p_spearman = stats.spearmanr(xs, ys)

print(f"\n  Pearson r:  {r_pearson:+.4f}  (p = {p_pearson:.4g})")
print(f"  Spearman rho: {r_spearman:+.4f}  (p = {p_spearman:.4g})")

# Scatter sample
print(f"\n  Sample data (first 20, sorted by tokens):")
print(f"  {'folio':<8} {'plant':<30} {'tokens':>6} {'proxy_len':>10}")
for d in sorted(data, key=lambda x: x["tokens"])[:20]:
    name = (d["latin"] or d["common"])[:28]
    print(f"  {d['folio']:<8} {name:<30} {d['tokens']:>6} {d['proxy_len']:>10}")
print(f"  ... (n={len(data)})")

# Decision
print(f"\n{'='*72}")
print(f"  PRE-REGISTERED DECISION")
print(f"{'='*72}")
if r_pearson > 0.5 and r_spearman > 0.4:
    verdict = "CONFIRMED"
    print(f"  r = {r_pearson:+.3f} > 0.5 AND rho = {r_spearman:+.3f} > 0.4")
    print(f"  -> CONFIRMED (syllable-level Latin hypothesis supported)")
elif 0.3 < r_pearson <= 0.5:
    verdict = "MARGINAL"
    print(f"  0.3 < r = {r_pearson:+.3f} <= 0.5")
    print(f"  -> MARGINAL")
elif r_pearson <= 0.3:
    verdict = "REFUTED"
    print(f"  r = {r_pearson:+.3f} <= 0.3")
    print(f"  -> REFUTED (syllable-level not supported under this proxy)")
    print(f"     Next test: H-BV-HOMOPHONIC-01")
else:
    verdict = "OTHER"

out = ROOT / "outputs" / "syllable_level_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-SYLLABLE-LEVEL-01",
    "locked_in_commit": "2c2e471",
    "n_folios": len(data),
    "token_count_stats": {
        "mean": round(statistics.mean(xs), 2),
        "sd": round(statistics.pstdev(xs), 2),
        "min": min(xs), "max": max(xs),
    },
    "proxy_length_stats": {
        "mean": round(statistics.mean(ys), 2),
        "sd": round(statistics.pstdev(ys), 2),
        "min": min(ys), "max": max(ys),
    },
    "pearson_r": round(r_pearson, 4),
    "pearson_p": round(p_pearson, 6),
    "spearman_rho": round(r_spearman, 4),
    "spearman_p": round(p_spearman, 6),
    "verdict": verdict,
    "sample_data": data,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out}")
