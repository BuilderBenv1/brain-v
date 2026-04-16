"""
Execute pre-registered H-BV-HAND-A-CONTENT-INDEPENDENCE-01 (locked 5d56eb5).

For Hand-A plant folios:
  1. Token-frequency vectors; pairwise cosine similarity
  2. Group by plant family via genus->family map
  3. Mean within-family cosine vs mean cross-family cosine
  4. Permutation test 1000 shuffles
  5. Secondary: medicinal-use text Jaccard correlation

Decision:
  within > cross AND perm p<0.05 -> plant-specific (INDEPENDENCE REFUTED)
  within ~= cross AND perm p>0.20 AND med-r<0.1 -> INDEPENDENCE CONFIRMED
  otherwise -> MARGINAL
"""
import csv
import json
import random
import statistics
import math
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

ROOT = Path(r"C:\Projects\brain-v")
CORPUS = json.loads((ROOT / "raw/perception/voynich-corpus.json").read_text(encoding="utf-8"))
PLANT_CSV = ROOT / "raw/research/plant-identifications.csv"

# Genus -> family (from perun test, inlined for self-containment)
GENUS_FAMILY = {
    "rosmarinus": "lamiaceae", "mentha": "lamiaceae", "salvia": "lamiaceae",
    "thymus": "lamiaceae", "lavandula": "lamiaceae", "origanum": "lamiaceae",
    "stachys": "lamiaceae", "prunella": "lamiaceae", "lamium": "lamiaceae",
    "satureja": "lamiaceae",
    "helleborus": "ranunculaceae", "delphinium": "ranunculaceae",
    "aquilegia": "ranunculaceae", "anemone": "ranunculaceae",
    "eranthis": "ranunculaceae", "pulsatilla": "ranunculaceae",
    "adonis": "ranunculaceae", "ranunculus": "ranunculaceae",
    "nigella": "ranunculaceae",
    "atropa": "solanaceae", "mandragora": "solanaceae",
    "leucanthemum": "asteraceae", "tanacetum": "asteraceae",
    "inula": "asteraceae", "erigeron": "asteraceae", "emilia": "asteraceae",
    "aster": "asteraceae", "catananche": "asteraceae",
    "cichorium": "asteraceae", "sonchus": "asteraceae",
    "hieracium": "asteraceae", "scorzonera": "asteraceae",
    "lactuca": "asteraceae", "cynara": "asteraceae",
    "chrysanthemum": "asteraceae", "centaurea": "asteraceae",
    "arnica": "asteraceae", "achillea": "asteraceae",
    "conyza": "asteraceae", "cirsium": "asteraceae",
    "astrantia": "apiaceae", "apium": "apiaceae",
    "coriandrum": "apiaceae", "eryngium": "apiaceae",
    "astragalus": "fabaceae", "pisum": "fabaceae", "lens": "fabaceae",
    "lupinus": "fabaceae",
    "nymphaea": "nymphaeaceae", "nymphoides": "menyanthaceae",
    "crocus": "iridaceae", "tulipa": "liliaceae", "paris": "melanthiaceae",
    "dianthus": "caryophyllaceae", "silene": "caryophyllaceae",
    "stellaria": "caryophyllaceae",
    "viola": "violaceae",
    "ruta": "rutaceae", "dictamnus": "rutaceae",
    "papaver": "papaveraceae", "fumaria": "papaveraceae",
    "saxifraga": "saxifragaceae", "ribes": "grossulariaceae",
    "borago": "boraginaceae", "pulmonaria": "boraginaceae",
    "symphytum": "boraginaceae",
    "rhus": "anacardiaceae",
    "cakile": "brassicaceae", "draba": "brassicaceae",
    "isatis": "brassicaceae", "lunaria": "brassicaceae",
    "brassica": "brassicaceae", "eruca": "brassicaceae",
    "verbena": "verbenaceae",
    "euphorbia": "euphorbiaceae", "ricinus": "euphorbiaceae",
    "sempervivum": "crassulaceae",
    "campanula": "campanulaceae",
    "drosera": "droseraceae",
    "acanthus": "acanthaceae", "thunbergia": "acanthaceae",
    "valeriana": "caprifoliaceae", "lonicera": "caprifoliaceae",
    "linnaea": "caprifoliaceae",
    "polemonium": "polemoniaceae",
    "veronica": "plantaginaceae",
    "curcuma": "zingiberaceae",
    "malva": "malvaceae", "althaea": "malvaceae",
    "myrica": "myricaceae",
    "trientalis": "primulaceae", "anagallis": "primulaceae",
    "primula": "primulaceae",
    "cucumis": "cucurbitaceae", "telfairia": "cucurbitaceae",
    "ficus": "moraceae", "cannabis": "cannabaceae",
    "musa": "musaceae", "dioscorea": "dioscoreaceae",
    "aristolochia": "aristolochiaceae",
    "gentiana": "gentianaceae",
    "cuscuta": "convolvulaceae",
    "erodium": "geraniaceae",
    "spinacia": "amaranthaceae", "atriplex": "amaranthaceae",
    "celosia": "amaranthaceae",
    "sanguisorba": "rosaceae",
    "elytrigia": "poaceae",
    "rhododendron": "ericaceae",
    "actaea": "ranunculaceae",
    "sherardia": "rubiaceae",
    "tamus": "dioscoreaceae",
}

folio_tokens = defaultdict(list)
folio_hand = {}
for f in CORPUS["folios"]:
    fid = f["folio"]
    folio_hand[fid] = f.get("currier_language", "?")
    for line in f["lines"]:
        folio_tokens[fid].extend(line["words"])

# Hand A plant folios with Sherwood genus -> family
records = []
with PLANT_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if "CONFLICT" in (r.get("notes") or "").upper(): continue
        fid = r["folio"]
        if folio_hand.get(fid) != "A": continue
        if len(folio_tokens.get(fid, [])) < 20: continue
        lat = (r.get("latin_name") or "").strip().lower()
        genus = lat.split()[0] if lat else ""
        family = GENUS_FAMILY.get(genus, "unknown")
        med = (r.get("medicinal_use") or "")
        records.append({
            "folio": fid, "latin": lat, "genus": genus, "family": family,
            "medicinal": med,
        })

print(f"Hand-A plant folios: {len(records)}")
fam_counts = Counter(r["family"] for r in records)
print(f"Family distribution: {dict(fam_counts.most_common(10))}")
tested = [r for r in records if r["family"] != "unknown"]
print(f"Folios with known family: {len(tested)}")

# Build TF vectors (use CountVectorizer for simplicity)
docs = [" ".join(folio_tokens[r["folio"]]) for r in tested]
vec = CountVectorizer(min_df=1, token_pattern=r"\S+")
X = vec.fit_transform(docs).toarray().astype(float)
# L2 normalise rows -> cosine sim is dot product
norms = np.linalg.norm(X, axis=1, keepdims=True)
norms[norms == 0] = 1
Xn = X / norms
sim_matrix = Xn @ Xn.T
print(f"Vocab size: {X.shape[1]}")

# Within-family vs cross-family pairs
families = [r["family"] for r in tested]
n = len(tested)
within_vals = []
cross_vals = []
for i in range(n):
    for j in range(i+1, n):
        s = float(sim_matrix[i, j])
        if families[i] == families[j]:
            within_vals.append(s)
        else:
            cross_vals.append(s)

within_mean = statistics.mean(within_vals) if within_vals else 0
cross_mean = statistics.mean(cross_vals) if cross_vals else 0
diff = within_mean - cross_mean
print(f"\n  Within-family pairs: {len(within_vals)}, mean cosine {within_mean:.4f}")
print(f"  Cross-family pairs:  {len(cross_vals)}, mean cosine {cross_mean:.4f}")
print(f"  Difference (within - cross): {diff:+.4f}")

# Permutation test: shuffle family labels
N_PERM = 1000
rng = random.Random(42)
perm_diffs = []
shuffled_families = families[:]
for _ in range(N_PERM):
    rng.shuffle(shuffled_families)
    w = []; c = []
    for i in range(n):
        for j in range(i+1, n):
            s = float(sim_matrix[i, j])
            if shuffled_families[i] == shuffled_families[j]:
                w.append(s)
            else:
                c.append(s)
    wm = statistics.mean(w) if w else 0
    cm = statistics.mean(c) if c else 0
    perm_diffs.append(wm - cm)

perm_mean = statistics.mean(perm_diffs)
perm_sd = statistics.pstdev(perm_diffs)
p_perm = sum(1 for d in perm_diffs if d >= diff) / N_PERM
print(f"\n  Permutation null (N={N_PERM}):")
print(f"    mean diff: {perm_mean:+.4f}  sd: {perm_sd:.4f}")
print(f"    empirical p(perm diff >= observed): {p_perm:.4f}")

# Secondary: medicinal-use Jaccard correlation
def words(text):
    return set(w.lower() for w in text.split() if len(w) >= 3)

med_sims = []
text_sims_paired = []
for i in range(n):
    for j in range(i+1, n):
        wa = words(tested[i]["medicinal"])
        wb = words(tested[j]["medicinal"])
        if not wa and not wb: continue
        jacc = len(wa & wb) / max(1, len(wa | wb))
        med_sims.append(jacc)
        text_sims_paired.append(float(sim_matrix[i, j]))

if med_sims and len(med_sims) == len(text_sims_paired):
    r_med, p_med = stats.pearsonr(text_sims_paired, med_sims)
    rho_med, p_rho_med = stats.spearmanr(text_sims_paired, med_sims)
    print(f"\n  Secondary — medicinal-use Jaccard vs text cosine:")
    print(f"    Pearson r = {r_med:+.4f} (p = {p_med:.4g})")
    print(f"    Spearman rho = {rho_med:+.4f}")

# Decision
print(f"\n{'='*72}")
print(f"  PRE-REGISTERED DECISION")
print(f"{'='*72}")

if diff > 0 and p_perm < 0.05:
    verdict = "INDEPENDENCE_REFUTED"
    print(f"  Within > cross (diff +{diff:.4f}) AND perm p={p_perm:.4f} < 0.05")
    print(f"  -> text IS plant-specific at family level (INDEPENDENCE refuted)")
elif abs(diff) < 0.01 and p_perm > 0.20 and abs(r_med) < 0.1:
    verdict = "INDEPENDENCE_CONFIRMED"
    print(f"  Within ~= cross (diff {diff:+.4f}) AND perm p={p_perm:.4f} > 0.20")
    print(f"  AND medicinal r={r_med:+.4f} below 0.1")
    print(f"  -> INDEPENDENCE CONFIRMED: Hand A text is NOT plant-specific")
else:
    verdict = "MARGINAL"
    print(f"  Mixed signals: diff {diff:+.4f}, perm p {p_perm:.4f}, "
          f"med r {r_med:+.4f}")
    print(f"  -> MARGINAL")

out = ROOT / "outputs" / "content_independence_test.json"
out.write_text(json.dumps({
    "generated": "2026-04-16",
    "hypothesis": "H-BV-HAND-A-CONTENT-INDEPENDENCE-01",
    "locked_in_commit": "5d56eb5",
    "n_folios": len(tested),
    "family_distribution": dict(fam_counts.most_common()),
    "within_family_pairs": len(within_vals),
    "cross_family_pairs": len(cross_vals),
    "within_mean_cosine": round(within_mean, 4),
    "cross_mean_cosine": round(cross_mean, 4),
    "difference": round(diff, 4),
    "permutation": {
        "N": N_PERM,
        "mean_diff": round(perm_mean, 4),
        "sd_diff": round(perm_sd, 4),
        "p_empirical": round(p_perm, 4),
    },
    "secondary_medicinal": {
        "pearson_r": round(r_med, 4),
        "pearson_p": round(p_med, 4),
        "spearman_rho": round(rho_med, 4),
    },
    "verdict": verdict,
}, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out}")
