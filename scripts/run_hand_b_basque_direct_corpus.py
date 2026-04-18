"""Execute pre-registered H-BV-HAND-B-BASQUE-DIRECT-CORPUS-01."""
import json
from pathlib import Path

ROOT = Path(r"C:\Projects\brain-v")

HAND_B = {"M1":4.4935, "M2_L1":10, "M2_L2":5, "M3":2.7901, "M4":0.26, "M5":0.80}
UD_BASQUE = {"M1":3.3796, "M2_L1":6, "M2_L2":25, "M3":4.4107, "M4":0.1333, "M5":0.6429}
PUBLISHED = {"M1":(2.5,4.5),"M2_L1":(8,16),"M2_L2":(3,8),"M3":(2.0,5.0),"M4":(0.02,0.20),"M5":(0.60,1.00)}

def hand_a_or_b_fits_band(metric, val, direct):
    if metric in ("M1","M3"): tol = direct * 0.5; lo, hi = direct-tol, direct+tol
    elif metric in ("M2_L1","M2_L2"): tol = direct * 0.3; lo, hi = direct-tol, direct+tol
    elif metric == "M4": tol = direct * 0.5; lo, hi = direct-tol, direct+tol
    elif metric == "M5": lo, hi = max(0, direct-0.1), min(1.0, direct+0.1)
    return (lo <= val <= hi, (round(lo,4), round(hi,4)))

# Hand A reference values (from H-BV-BASQUE-DIRECT-CORPUS-01)
HAND_A = {"M1":4.12, "M2_L1":10, "M2_L2":5, "M3":3.16, "M4":0.20, "M5":1.00}

print("=== HAND B vs UD_Basque DIRECT MEASUREMENT ===")
print(f"{'metric':<8}{'HB':<10}{'UD':<10}{'tolerance':<22}{'fit':<6}{'HA fit (ref)'}")

hb_fits_count = 0; pub_validated_count = 0
results = []
for m in ["M1","M2_L1","M2_L2","M3","M4","M5"]:
    val = HAND_B[m]; direct = UD_BASQUE[m]
    hb_in, band = hand_a_or_b_fits_band(m, val, direct)
    if hb_in: hb_fits_count += 1
    pub_lo, pub_hi = PUBLISHED[m]
    pub_validated = pub_lo <= direct <= pub_hi
    if pub_validated: pub_validated_count += 1
    ha_in, _ = hand_a_or_b_fits_band(m, HAND_A[m], direct)
    print(f"{m:<8}{val:<10}{direct:<10}{str(band):<22}{'YES' if hb_in else 'NO':<6}{'YES' if ha_in else 'NO'}")
    results.append({"metric":m, "hand_b":val, "direct":direct, "tolerance":band,
                    "hand_b_fits": hb_in, "hand_a_fits": ha_in,
                    "published_validated": pub_validated})

print(f"\n  HAND B fits: {hb_fits_count}/6")
print(f"  HAND A reference: 3/6 (M1, M3, M4 fit; M2_L1, M2_L2, M5 missed)")

if hb_fits_count == 6: verdict = "CORPUS_CONFIRMED"
elif hb_fits_count in (4,5): verdict = "CORPUS_PARTIAL"
elif hb_fits_count == 3: verdict = "CORPUS_WEAK"
else: verdict = "CORPUS_REFUTED"

print(f"\n  VERDICT: {verdict}")

out = {"generated":"2026-04-18","hypothesis":"H-BV-HAND-B-BASQUE-DIRECT-CORPUS-01",
       "hand_b_values":HAND_B, "ud_basque_direct":UD_BASQUE,
       "per_metric":results,
       "hand_b_fits_count":hb_fits_count, "hand_a_fits_count_reference":3,
       "verdict":verdict,
       "hand_a_reference":"CORPUS_WEAK 3/6 (M1, M3, M4 fit)"}
out_path = ROOT / "outputs" / "hand_b_basque_direct_corpus_test.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nSaved: {out_path}")
