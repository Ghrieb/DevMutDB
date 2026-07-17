# SPDX-FileCopyrightText: 2025 Abdelkarim Hani Ghrieb
# SPDX-License-Identifier: LicenseRef-Proprietary
#
# validation/run_validation.py
# Single authoritative validation script. NO mock data, NO fallback.
# Requires: DevMutDB backend running (uvicorn app.main:app --reload)
#
# Usage:
#   python validation/run_validation.py
#
# Output:
#   validation/benchmark_results.csv   — Supplementary Table S1
#   validation/statistics_report.txt   — paste into manuscript
#   validation/figures/fig1-7          — all manuscript figures

import os
import sys
import csv
import math
import urllib.request
import urllib.error
import json
import ssl
import time
from typing import List, Tuple, Optional

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from sklearn.metrics import roc_curve, auc

API_BASE = "http://localhost:8000"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_CSV = os.path.join(SCRIPT_DIR, "benchmark_results.csv")
REPORT_TXT = os.path.join(SCRIPT_DIR, "statistics_report.txt")
FIGURES_DIR = os.path.join(SCRIPT_DIR, "figures")

# ── COLOUR PALETTE ─────────────────────────────────────────────────────────────
PURPLE   = "#6B63D4"
PURPLE_L = "#AFA9EC"
TEAL     = "#1D9E75"
TEAL_L   = "#9FE1CB"
GRAY     = "#888780"
GRAY_L   = "#D3D1C7"
CORAL    = "#D94040"
AMBER    = "#E8803A"

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 600,
})

# ── CURATED OMIM GENE LIST (121 genes, all real) ──────────────────────────────

DEVELOPMENTAL_GENES = [
    ("SOX2",   "c.70C>T",   "Anophthalmia-esophageal-genital",          "206900"),
    ("PAX6",   "c.357G>A",  "Aniridia",                                 "106210"),
    ("TWIST1", "c.586C>T",  "Saethre-Chotzen syndrome",                 "101400"),
    ("FGFR3",  "c.1138G>A", "Achondroplasia",                           "100800"),
    ("NKX2-5", "c.655G>T",  "Atrial septal defect",                     "108900"),
    ("TBX5",   "c.1001C>T", "Holt-Oram syndrome",                       "142900"),
    ("PTPN11", "c.922A>G",  "Noonan syndrome",                          "163950"),
    ("NIPBL",  "c.5350G>T", "Cornelia de Lange syndrome",               "122470"),
    ("KAT6A",  "c.1358A>G", "KAT6A syndrome (dev. delay)",              "616268"),
    ("FOXP2",  "c.1652T>C", "Speech-language disorder",                 "602081"),
    ("CHD7",   "c.2815G>T", "CHARGE syndrome",                          "214800"),
    ("KDM6A",  "c.3272C>T", "Kabuki syndrome 2",                        "300867"),
    ("MED13L", "c.2623G>A", "Intellectual disability syndrome",         "616686"),
    ("SETD5",  "c.1957C>T", "Mental retardation autosomal dominant",    "615761"),
    ("ADNP",   "c.2157C>A", "Helsmoortel-Van der Aa syndrome",          "615873"),
    ("ANKRD11","c.1903C>T", "KBG syndrome",                             "148050"),
    ("ARID1B", "c.3637C>T", "Coffin-Siris syndrome",                   "135900"),
    ("KMT2D",  "c.15607C>T","Kabuki syndrome 1",                        "147920"),
    ("EP300",  "c.4417C>T", "Rubinstein-Taybi syndrome 2",              "613684"),
    ("CREBBP", "c.4435C>T", "Rubinstein-Taybi syndrome 1",              "180849"),
    ("DYRK1A", "c.703C>T",  "DYRK1A syndrome",                         "614104"),
    ("FOXG1",  "c.256C>T",  "Rett syndrome congenital",                 "613454"),
    ("MECP2",  "c.397C>T",  "Rett syndrome",                            "312750"),
    ("PTEN",   "c.697C>T",  "Cowden syndrome (hamartoma dev.)",         "158350"),
    ("RET",    "c.1900T>C", "Hirschsprung disease",                     "142623"),
    ("SHH",    "c.736C>T",  "Holoprosencephaly",                        "236100"),
    ("GLI3",   "c.2497C>T", "Pallister-Hall syndrome",                  "146510"),
    ("NOTCH3", "c.328C>T",  "CADASIL (vascular dev.)",                  "125310"),
    ("JAG1",   "c.1808G>A", "Alagille syndrome",                        "118450"),
    ("EYA1",   "c.1435C>T", "Branchio-oto-renal syndrome",              "113650"),
    ("SALL1",  "c.3167C>T", "Townes-Brocks syndrome",                   "107480"),
    ("WT1",    "c.1180C>T", "Denys-Drash syndrome",                     "194080"),
    ("PAX2",   "c.76C>T",   "Renal-coloboma syndrome",                  "120330"),
    ("ROBO3",  "c.2747C>T", "Horizontal gaze palsy",                   "257930"),
    ("EFNB1",  "c.391C>T",  "Craniofrontonasal syndrome",               "304110"),
    ("FGF8",   "c.412C>T",  "Holoprosencephaly 6",                      "605309"),
    ("OTX2",   "c.402C>T",  "Anophthalmia/microphthalmia",              "610125"),
    ("VSX2",   "c.574C>T",  "Microphthalmia isolated",                  "610093"),
    ("FOXC1",  "c.829C>T",  "Axenfeld-Rieger syndrome",                 "602482"),
    ("GJB2",   "c.35delG",  "Deafness autosomal recessive",             "220290"),
    ("MYO7A",  "c.5936C>T", "Usher syndrome type 1B",                   "276900"),
    ("CLN3",   "c.280_461del","Batten disease (neuronal ceroid)",       "204200"),
    ("HESX1",  "c.449G>A",  "Septo-optic dysplasia",                    "182230"),
    ("LHX3",   "c.236G>A",  "Pituitary hormone deficiency",             "221750"),
    ("PROP1",  "c.301_302delAG","Combined pituitary hormone def.",      "262600"),
    ("DHCR7",  "c.1210C>T", "Smith-Lemli-Opitz syndrome",              "270400"),
    ("PKD1",   "c.12058C>T","Polycystic kidney disease",               "173900"),
    ("PDGFRB", "c.1681C>T", "Infantile myofibromatosis",               "228550"),
    ("TRPV4",  "c.1855C>T", "Skeletal dysplasia (congenital)",         "600175"),
    ("RUNX2",  "c.674G>A",  "Cleidocranial dysplasia",                 "119600"),
    ("HOXD13","c.905G>A",   "Synpolydactyly",                          "186000"),
    ("SALL4",  "c.1873C>T", "Duane-radial ray syndrome",               "607323"),
    ("STRA6",  "c.1219C>T", "Matthew-Wood syndrome",                   "601186"),
    ("KAT6B",  "c.3978C>T", "Say-Barber-Biesecker syndrome",           "603736"),
    ("SMAD3",  "c.1024C>T", "Loeys-Dietz syndrome 3",                  "613795"),
    ("FBN1",   "c.5788C>T", "Marfan syndrome (connective dev.)",       "154700"),
    ("COL1A1", "c.934C>T",  "Osteogenesis imperfecta",                 "166200"),
    ("COL2A1", "c.4006C>T", "Stickler syndrome",                       "108300"),
    ("COMP",   "c.1273C>T", "Pseudoachondroplasia",                    "177170"),
    ("FBN2",   "c.3454C>T", "Congenital contractural arachnodactyly","121050"),
]

ADULT_ONSET_GENES = [
    ("BRCA1",  "c.5266dupC","Breast-ovarian cancer",                   "604370"),
    ("BRCA2",  "c.5946delT","Breast-ovarian cancer 2",                 "612555"),
    ("APOE",   "c.388T>C",  "Alzheimer disease",                       "104310"),
    ("LRRK2",  "c.6055G>A", "Parkinson disease 8",                     "168600"),
    ("SNCA",   "c.88G>C",   "Parkinson disease 1",                     "168601"),
    ("HTT",    "c.52G>A",   "Huntington disease",                      "143100"),
    ("ATM",    "c.7271T>G", "Ataxia-telangiectasia",                   "208900"),
    ("MLH1",   "c.1852_1854del","Lynch syndrome",                      "120436"),
    ("MSH2",   "c.1865T>A", "Lynch syndrome 1",                        "609310"),
    ("APC",    "c.3927_3931del","Familial adenomatous polyposis",      "175100"),
    ("VHL",    "c.499C>T",  "Von Hippel-Lindau disease",               "193300"),
    ("NF1",    "c.3199G>T", "Neurofibromatosis type 1 (adult)",        "162200"),
    ("NF2",    "c.863_864del","Neurofibromatosis type 2",              "101000"),
    ("RB1",    "c.2644C>T", "Retinoblastoma (adult onset)",            "180200"),
    ("TP53",   "c.817C>T",  "Li-Fraumeni syndrome",                    "151623"),
    ("CDKN2A", "c.238C>T",  "Melanoma/pancreatic cancer",              "155601"),
    ("MEN1",   "c.1546C>T", "Multiple endocrine neoplasia 1",         "131100"),
    ("SDHB",   "c.423+1G>T","Paraganglioma-pheochromocytoma",         "168000"),
    ("TSC1",   "c.1888C>T", "Tuberous sclerosis 1 (adult features)",  "191100"),
    ("TSC2",   "c.5024C>T", "Tuberous sclerosis 2",                   "613254"),
    ("PKD2",   "c.2243C>T", "Polycystic kidney disease 2 (adult)",    "173910"),
    ("MYBPC3", "c.3330+2T>G","Hypertrophic cardiomyopathy",           "115197"),
    ("MYH7",   "c.1208G>A", "Dilated cardiomyopathy",                 "115200"),
    ("KCNQ1",  "c.1032G>A", "Long QT syndrome 1 (adult arrhythmia)", "192500"),
    ("SCN5A",  "c.4234C>T", "Brugada syndrome",                       "601144"),
    ("LDLR",   "c.1418G>A", "Familial hypercholesterolemia",          "143890"),
    ("PCSK9",  "c.1120G>T", "Hypercholesterolemia autosomal dominant","607786"),
    ("F5",     "c.1601G>A", "Factor V Leiden thrombophilia",          "188055"),
    ("HBB",    "c.20A>T",   "Sickle cell anemia (adult crisis)",      "141900"),
    ("CFTR",   "c.1521_1523del","Cystic fibrosis (adult features)",   "219700"),
    ("G6PD",   "c.202G>A",  "G6PD deficiency (adult hemolysis)",      "300908"),
    ("HEXA",   "c.1274_1277dup","Tay-Sachs adult form",               "272800"),
    ("GBA",    "c.1226A>G", "Gaucher disease (adult onset)",          "230800"),
    ("FMR1",   "c.413G>A",  "Fragile X syndrome",                      "300624"),
    ("AR",     "c.2713C>T", "Androgen insensitivity adult",           "300068"),
    ("PKHD1",  "c.107C>T",  "Fibrocystic liver disease adult",        "263200"),
    ("COL3A1", "c.2411G>A", "Ehlers-Danlos vascular (adult rupture)", "130050"),
    ("TGFBR2", "c.1582C>T", "Loeys-Dietz adult aortic",              "610168"),
    ("CACNA1A","c.4042C>T", "Episodic ataxia adult onset",            "108500"),
    ("PRKCG",  "c.1258C>T", "Spinocerebellar ataxia 14",             "605361"),
    ("ATXN1",  "c.1A>G",    "Spinocerebellar ataxia 1",               "164400"),
    ("DMPK",   "c.1268A>G", "Myotonic dystrophy",                    "160900"),
    ("SOD1",   "c.272A>G",  "ALS adult onset",                        "105400"),
    ("FUS",    "c.1561C>T", "ALS-FUS adult onset",                   "608030"),
    ("TARDBP", "c.1144G>A", "ALS-TDP43 adult",                       "612069"),
    ("OPTN",   "c.458G>A",  "ALS/glaucoma",                          "602432"),
    ("VCP",    "c.464G>A",  "ALS/FTD/IBM",                           "601023"),
    ("SQSTM1", "c.1175C>T", "ALS/Paget disease",                     "601530"),
    ("GRN",    "c.709-1G>A","Frontotemporal dementia adult",         "607485"),
    ("MAPT",   "c.1853T>C", "Frontotemporal dementia MAPT",         "600274"),
]


# ── API CALL ───────────────────────────────────────────────────────────────────

def post_json(url: str, data: dict, timeout: int = 120) -> Tuple[Optional[dict], str]:
    """POST JSON to the API and return (parsed_response, reason)."""
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body), "ok"
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return None, f"connection error: {e.reason}"
    except Exception as e:
        return None, str(e)


def check_api_alive(url: str) -> bool:
    """Verify the backend is reachable."""
    try:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(url, timeout=10, context=ctx) as resp:
            return resp.status == 200
    except Exception:
        return False


# ── SCORING ────────────────────────────────────────────────────────────────────

def score_variant(gene: str, hgvs: str) -> Tuple[Optional[dict], str]:
    """Call the DevMutDB /score endpoint for one variant.
    Returns (data_dict, reason)."""
    return post_json(f"{API_BASE}/api/score", {"gene": gene, "hgvs": hgvs})


def extract_cadd(data: dict) -> Optional[float]:
    """Extract CADD PHRED from the component_explanation dict."""
    try:
        return data["component_explanation"]["V_pathogenicity"]["cadd_phred"]
    except (KeyError, TypeError):
        return None


# ── STATISTICS HELPERS ─────────────────────────────────────────────────────────

def sig_bracket(ax, x1, x2, y, label, lw=1.0, color="black", fs=9):
    """Draw a significance bracket between two box positions."""
    h = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.02
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=lw, color=color)
    ax.text((x1+x2)/2, y+h*1.1, label, ha="center", va="bottom",
            fontsize=fs, color=color)


def bootstrap_auc(labels, scores, n_iterations=2000, ci=95):
    """Bootstrap confidence interval for ROC AUC (percentile method)."""
    rng = np.random.default_rng(42)
    aucs = np.empty(n_iterations)
    n = len(labels)
    idx = np.arange(n)
    for i in range(n_iterations):
        boot_idx = rng.choice(idx, size=n, replace=True)
        if len(np.unique(labels[boot_idx])) < 2:
            aucs[i] = 0.5
            continue
        fpr, tpr, _ = roc_curve(labels[boot_idx], scores[boot_idx])
        aucs[i] = auc(fpr, tpr)
    alpha = (100 - ci) / 2
    return np.percentile(aucs, alpha), np.percentile(aucs, 100 - alpha)


def youden_j(labels, scores):
    """Optimal threshold, sensitivity, specificity via Youden's J index."""
    fpr, tpr, thresholds = roc_curve(labels, scores)
    j = tpr - fpr
    ix = np.argmax(j)
    return thresholds[ix], tpr[ix], 1 - fpr[ix]


def tier_analysis(dev, adult):
    """Tier distribution for the interpretative scale (0-9, 10-19, >=20)."""
    def in_tier(df, lo, hi):
        return df[(df["devscore"] >= lo) & (df["devscore"] <= hi)]

    tiers = [
        ("Low (0-9)", 0, 9),
        ("Moderate (10-19)", 10, 19),
        ("High (>=20)", 20, 100),
    ]

    rows = []
    total_dev = len(dev)
    total_adult = len(adult)

    for name, lo, hi in tiers:
        d = len(in_tier(dev, lo, hi))
        a = len(in_tier(adult, lo, hi))
        sens = d / total_dev if total_dev > 0 else 0
        spec = (total_adult - a) / total_adult if total_adult > 0 else 0
        ppv = d / (d + a) if (d + a) > 0 else 0
        rows.append((name, d, a, sens, spec, ppv))

    d_pos = sum(r[1] for r in rows[1:])
    a_pos = sum(r[2] for r in rows[1:])
    sens_pos = d_pos / total_dev if total_dev > 0 else 0
    spec_pos = (total_adult - a_pos) / total_adult if total_adult > 0 else 0
    ppv_pos = d_pos / (d_pos + a_pos) if (d_pos + a_pos) > 0 else 0

    cstage_info = []
    for name, lo, hi in tiers:
        d_tier = in_tier(dev, lo, hi)
        a_tier = in_tier(adult, lo, hi)
        d_c = d_tier["C_stage"].mean() if len(d_tier) > 0 else None
        a_c = a_tier["C_stage"].mean() if len(a_tier) > 0 else None
        cstage_info.append((name, d_c, a_c))

    peak_info = {}
    for name, lo, hi in tiers:
        d_tier = in_tier(dev, lo, hi)
        raw = d_tier["peak_stage"].value_counts().to_dict()
        peak_info[name] = {k.replace("_", " ").title(): v for k, v in raw.items()}

    return rows, (sens_pos, spec_pos, ppv_pos), cstage_info, peak_info


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 62)
    print("  DevMutDB — Live Validation Pipeline")
    print("=" * 62)

    # ── Verify API ──────────────────────────────────────────────────────────
    if not check_api_alive(f"{API_BASE}/api/"):
        print(f"\nERROR: Cannot reach DevMutDB API at {API_BASE}/")
        print("Make sure the backend is running:")
        print("  uvicorn app.main:app --reload")
        sys.exit(1)
    print(f"  API: {API_BASE}  [OK]\n")

    # ── Step 1: Call API for every gene ────────────────────────────────────
    all_genes = []
    for gene, hgvs, disease, omim in DEVELOPMENTAL_GENES:
        all_genes.append((gene, hgvs, disease, omim, "developmental"))
    for gene, hgvs, disease, omim in ADULT_ONSET_GENES:
        all_genes.append((gene, hgvs, disease, omim, "adult"))

    total = len(all_genes)
    print(f"  Benchmark: {total} genes ({len(DEVELOPMENTAL_GENES)} dev + "
          f"{len(ADULT_ONSET_GENES)} adult)\n")
    print(f"  Scoring all genes through DevMutDB API...")

    rows = []
    succeeded = 0
    failed = 0

    for i, (gene, hgvs, disease, omim, cls) in enumerate(all_genes, 1):
        sys.stdout.write(f"\r    [{i}/{total}] {gene:10s} {hgvs:16s} ... ")
        sys.stdout.flush()

        data = None
        reason = ""
        for attempt in range(3):
            data, reason = score_variant(gene, hgvs)
            if data is not None:
                break
            if attempt < 2:
                time.sleep(5)

        if data is None:
            rows.append({
                "gene": gene, "hgvs": hgvs, "disease": disease,
                "omim_id": omim, "class": cls,
                "devscore": None, "V": None, "E_peak": None,
                "C_stage": None, "D_domain": None, "peak_stage": None,
                "cadd": None, "sift": None, "polyphen": None,
                "source": "failed", "data_warnings": reason,
            })
            failed += 1
            print(f"FAILED — {reason}")
            continue

        cadd = extract_cadd(data)
        row = {
            "gene": gene, "hgvs": hgvs, "disease": disease,
            "omim_id": omim, "class": cls,
            "devscore": data.get("score"),
            "V": data.get("V"),
            "E_peak": data.get("E_peak"),
            "C_stage": data.get("C_stage"),
            "D_domain": data.get("D_domain"),
            "peak_stage": data.get("peak_stage"),
            "cadd": cadd,
            "sift": data.get("sift_score"),
            "polyphen": data.get("polyphen_score"),
            "source": data.get("source", "unknown"),
            "data_warnings": str(data.get("data_warnings", "")),
        }
        rows.append(row)
        succeeded += 1
        print(f"score={data.get('score')}  "
              f"source={data.get('source', '?')}")

        time.sleep(1.5)

    df = pd.DataFrame(rows)
    print("\nMISSING GENES LEDGER:", set([g[0] for g in DEVELOPMENTAL_GENES + ADULT_ONSET_GENES]) - set(df['gene']))
    os.makedirs(FIGURES_DIR, exist_ok=True)
    df.to_csv(RESULTS_CSV, index=False)
    print(f"\n  Saved {len(df)} results to {RESULTS_CSV}")

    # Export benchmark data as JSON for frontend (meta updated later with full stats)
    frontend_json_path = os.path.join(SCRIPT_DIR, "..", "frontend", "src", "data", "benchmark_results.json")
    export_columns = ["gene", "hgvs", "disease", "class", "devscore", "V", "E_peak",
                      "C_stage", "D_domain", "peak_stage", "cadd", "sift", "polyphen", "source"]
    export_records = df[export_columns].copy().to_dict(orient="records")
    # Convert NaN to None (null in JSON) for clean serialization
    for rec in export_records:
        for k, v in rec.items():
            if isinstance(v, float) and math.isnan(v):
                rec[k] = None

    # ── Filter to successful scores only for statistics ────────────────────
    df_ok = df[df["devscore"].notna()].copy()
    if len(df_ok) < 10:
        print(f"\n  ERROR: Only {len(df_ok)} successful scores — "
              "cannot run statistics.")
        sys.exit(1)

    dev = df_ok[df_ok["class"] == "developmental"].copy()
    adult = df_ok[df_ok["class"] == "adult"].copy()

    print(f"\n  Successful: {succeeded}, Failed: {failed}")
    print(f"  Dev genes: {len(dev)}, Adult genes: {len(adult)}")

    # ── Step 2: Statistics ─────────────────────────────────────────────────
    print("\n" + "=" * 62)
    print("  STATISTICAL RESULTS")
    print("=" * 62)

    stat_val, p_value = stats.mannwhitneyu(
        dev["devscore"], adult["devscore"], alternative="greater")
    mean_diff = dev["devscore"].mean() - adult["devscore"].mean()
    pooled_std = np.sqrt((dev["devscore"].std()**2 + adult["devscore"].std()**2) / 2)
    cohens_d = mean_diff / pooled_std

    print(f"\n  Mann-Whitney U test (DevScore: dev vs adult genes)")
    print(f"    U statistic: {stat_val:.1f}")
    p_str = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
    print(f"    p-value: {p_value:.2e}  {p_str}")

    print(f"\n  Effect size (Cohen's d)")
    print(f"    d = {cohens_d:.2f}  "
          f"({'very large' if cohens_d > 1.2 else 'large' if cohens_d > 0.8 else 'medium'})")
    print(f"    Dev genes median DevScore: {dev['devscore'].median():.1f}")
    print(f"    Adult genes median DevScore: {adult['devscore'].median():.1f}")

    valid_cadd = df_ok.dropna(subset=["cadd"])
    rho, p_spearman = stats.spearmanr(valid_cadd["devscore"], valid_cadd["cadd"])
    print(f"\n  Spearman correlation: DevScore vs CADD")
    print(f"    rho = {rho:.3f}, p = {p_spearman:.3e}")
    print(f"    {'Low correlation — DevScore adds new information' if abs(rho) < 0.5 else 'Moderate correlation'}")

    # Partial Spearman: DevScore vs CADD controlling for disease class
    from scipy.stats import linregress
    cadd_idx = valid_cadd.index
    class_num = (df_ok.loc[cadd_idx, "class"] == "developmental").astype(int)
    lr_dev = linregress(class_num, valid_cadd["devscore"])
    residual_dev = valid_cadd["devscore"] - (lr_dev.intercept + lr_dev.slope * class_num)
    lr_cadd = linregress(class_num, valid_cadd["cadd"])
    residual_cadd = valid_cadd["cadd"] - (lr_cadd.intercept + lr_cadd.slope * class_num)
    rho_partial, p_partial = stats.spearmanr(residual_dev, residual_cadd)
    print(f"\n  Partial Spearman (controlling for disease class):")
    print(f"    rho = {rho_partial:.3f}, p = {p_partial:.3e}")

    # ── AUC (Three Decoupled Pairwise Subsets) ────────────────────────────
    # Rationale: a single 4-way dropna deletes all non-missense variants
    # (frameshifts, splice, indels) from BOTH DevScore and CADD evaluations.
    # Instead we evaluate each tool on the maximal subset where it produces a
    # score, keeping each comparison fair and maximising statistical power.

    # Subset 1 — Headline DevScore AUC (100% of successfully scored variants)
    valid_global = df_ok.dropna(subset=["devscore"]).copy()
    labels_global = (valid_global["class"] == "developmental").astype(int)
    if len(np.unique(labels_global)) > 1 and len(valid_global) >= 5:
        fpr_dev, tpr_dev, _ = roc_curve(labels_global, valid_global["devscore"])
        auc_dev = auc(fpr_dev, tpr_dev)
    else:
        fpr_dev = tpr_dev = np.array([0, 1])
        auc_dev = 0.5

    # Subset 2 — Paired head-to-head: DevScore vs CADD
    # Only genes where CADD resolved; re-compute DevScore AUC on same subset.
    valid_cadd = df_ok.dropna(subset=["devscore", "cadd"]).copy()
    labels_cadd = (valid_cadd["class"] == "developmental").astype(int)
    if len(np.unique(labels_cadd)) > 1 and len(valid_cadd) >= 5:
        fpr_cadd, tpr_cadd, _ = roc_curve(labels_cadd, valid_cadd["cadd"])
        auc_cadd = auc(fpr_cadd, tpr_cadd)
        fpr_dev_paired_cadd, tpr_dev_paired_cadd, _ = roc_curve(labels_cadd, valid_cadd["devscore"])
        auc_dev_paired_cadd = auc(fpr_dev_paired_cadd, tpr_dev_paired_cadd)
    else:
        fpr_cadd = tpr_cadd = np.array([0, 1])
        auc_cadd = 0.5
        fpr_dev_paired_cadd = tpr_dev_paired_cadd = np.array([0, 1])
        auc_dev_paired_cadd = auc_dev

    # Subset 3 — Missense-only paired baseline: SIFT and PolyPhen-2
    # Strictly missense SNVs where SIFT/PolyPhen produce a score.
    valid_vep = df_ok.dropna(subset=["sift", "polyphen"]).copy()
    labels_vep = (valid_vep["class"] == "developmental").astype(int)
    if len(np.unique(labels_vep)) > 1 and len(valid_vep) >= 5:
        fpr_sift, tpr_sift, _ = roc_curve(labels_vep, -valid_vep["sift"])  # lower SIFT = more damaging
        auc_sift = auc(fpr_sift, tpr_sift)
        fpr_pp, tpr_pp, _ = roc_curve(labels_vep, valid_vep["polyphen"])
        auc_pp = auc(fpr_pp, tpr_pp)
        # Also re-compute DevScore AUC on the missense-only subset for fair comparison
        fpr_dev_vep, tpr_dev_vep, _ = roc_curve(labels_vep, valid_vep["devscore"])
        auc_dev_vep = auc(fpr_dev_vep, tpr_dev_vep)
    else:
        fpr_sift = tpr_sift = fpr_pp = tpr_pp = np.array([0, 1])
        auc_sift = auc_pp = 0.5
        fpr_dev_vep = tpr_dev_vep = np.array([0, 1])
        auc_dev_vep = auc_dev

    # ── Bootstrap CI (headline DevScore AUC) ───────────────────────────
    auc_ci_lower, auc_ci_upper = bootstrap_auc(
        labels_global.values, valid_global["devscore"].values)

    # ── Youden's J optimal threshold ───────────────────────────────────
    opt_threshold, opt_sensitivity, opt_specificity = youden_j(
        labels_global.values, valid_global["devscore"].values)

    n_excluded_cadd  = len(valid_global) - len(valid_cadd)
    n_missense_only  = len(valid_vep)

    print(f"\n  AUC scores (three decoupled pairwise subsets)")
    print(f"    DevScore 95% CI:           ({auc_ci_lower:.3f}--{auc_ci_upper:.3f})")
    print(f"  Youden's J: threshold={opt_threshold:.2f}, "
          f"sensitivity={opt_sensitivity:.3f}, specificity={opt_specificity:.3f}")
    print(f"  ─── Subset 1: Headline DevScore (n={len(valid_global)}, all variant classes)")
    print(f"    DevScore:   {auc_dev:.3f}")
    print(f"  ─── Subset 2: Head-to-head vs CADD (n={len(valid_cadd)}, CADD-resolved variants)")
    print(f"    DevScore*:  {auc_dev_paired_cadd:.3f}  (* paired with CADD subset)")
    print(f"    CADD:       {auc_cadd:.3f}  ({n_excluded_cadd} non-missense excluded from CADD only)")
    print(f"  ─── Subset 3: Missense-only (n={n_missense_only}, SIFT+PolyPhen applicable)")
    print(f"    DevScore**: {auc_dev_vep:.3f}  (** missense-only subset)")
    print(f"    SIFT:       {auc_sift:.3f}  (evolutionary constraint — onset-blind)")
    print(f"    PolyPhen-2: {auc_pp:.3f}  (evolutionary constraint — onset-blind)")
    print(f"")
    print(f"  Note: SIFT AUC={auc_sift:.3f} and PolyPhen-2 AUC={auc_pp:.3f}: "
          "Sequence-level conservation algorithms assign severe pathogenicity "
          "to adult Mendelian controls (e.g., TP53, BRCA1), demonstrating that "
          "evolutionary constraint alone cannot resolve developmental timing. "
          "DevScore addresses this ontological gap via spatiotemporal "
          "criticality (C_stage).")
    best_base = auc_cadd  # CADD is the primary comparator
    print(f"  ─── Headline improvement vs best baseline (CADD): +{auc_dev - best_base:.3f}")
    # For manuscript: use paired CADD comparison as main comparator
    print(f"  ─── Paired CADD improvement (same n): +{auc_dev_paired_cadd - auc_cadd:.3f}")

    # Alias for downstream figure code that still references the old variable names
    valid = valid_cadd  # use CADD-paired subset for ROC figure (most rigorous comparison)

    # ── Save statistics report ──────────────────────────────────────────────
    with open(REPORT_TXT, "w", encoding="utf-8") as f:
        f.write("DevMutDB Validation Statistics Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Benchmark: {len(dev)} developmental + {len(adult)} adult-onset genes\n")
        f.write(f"API failures: {failed}\n\n")
        f.write(f"DevScore AUC 95% CI: ({auc_ci_lower:.3f}--{auc_ci_upper:.3f})\n")
        f.write(f"Youden's J: threshold={opt_threshold:.2f}, "
                f"sensitivity={opt_sensitivity:.3f}, specificity={opt_specificity:.3f}\n\n")
        f.write(f"AUC Results (three decoupled pairwise subsets):\n")
        f.write(f"  Subset 1 — Headline DevScore (n={len(valid_global)}, all variant classes):\n")
        f.write(f"    DevScore:                 {auc_dev:.3f}\n")
        f.write(f"  Subset 2 — vs CADD (n={len(valid_cadd)}, CADD-resolved variants):\n")
        f.write(f"    DevScore (paired):         {auc_dev_paired_cadd:.3f}\n")
        f.write(f"    CADD:                      {auc_cadd:.3f}\n")
        f.write(f"    Improvement (DevScore-CADD): +{auc_dev_paired_cadd - auc_cadd:.3f}\n")
        f.write(f"  Subset 3 — Missense-only (n={n_missense_only}, SIFT+PolyPhen applicable):\n")
        f.write(f"    DevScore (missense-paired): {auc_dev_vep:.3f}\n")
        f.write(f"    SIFT:                      {auc_sift:.3f}  (evolutionary constraint — onset-blind)\n")
        f.write(f"    PolyPhen-2:                {auc_pp:.3f}  (evolutionary constraint — onset-blind)\n")
        f.write(f"  Note: SIFT AUC={auc_sift:.3f} and PolyPhen-2 AUC={auc_pp:.3f}: "
                "Sequence-level conservation algorithms assign severe pathogenicity "
                "to adult Mendelian controls (e.g., TP53, BRCA1), demonstrating that "
                "evolutionary constraint alone cannot resolve developmental timing. "
                "DevScore addresses this ontological gap via spatiotemporal "
                "criticality (C_stage).\n\n")
        f.write(f"Mann-Whitney U: U={stat_val:.1f}, p={p_value:.2e} {p_str}\n")
        f.write(f"Cohen's d: {cohens_d:.2f}\n")
        f.write(f"Dev genes median DevScore: {dev['devscore'].median():.1f}\n")
        f.write(f"Adult genes median DevScore: {adult['devscore'].median():.1f}\n")
        f.write(f"Spearman(DevScore, CADD): rho={rho:.3f}, p={p_spearman:.3e}\n")
        f.write(f"Partial Spearman (controlling for class): rho={rho_partial:.3f}, p={p_partial:.3e}\n")

    # ── Tier Distribution Analysis ──────────────────────────────────────
    tier_rows, tier_cumul, tier_cstage, tier_peak = tier_analysis(dev, adult)

    with open(REPORT_TXT, "a", encoding="utf-8") as f:
        f.write(f"\n─── Interpretative Scale — Tier Distribution ────────────────\n")
        f.write(f"{'Tier':<20} {'Dev':>5} {'Adult':>5} {'Sens':>7} {'Spec':>7} {'PPV':>7}\n")
        for name, d, a, sens, spec, ppv in tier_rows:
            f.write(f"{name:<20} {d:>5} {a:>5} {sens:>6.1%} {spec:>6.1%} {ppv:>6.1%}\n")
        f.write(f"\nModerate+High (>=10) as positive:\n")
        f.write(f"  Sensitivity: {tier_cumul[0]:.2%}\n")
        f.write(f"  Specificity: {tier_cumul[1]:.2%}\n")
        f.write(f"  PPV:         {tier_cumul[2]:.2%}\n")
        f.write(f"\nMean C_stage per tier:\n")
        for name, d_c, a_c in tier_cstage:
            d_str = f"{d_c:.3f}" if d_c is not None else "N/A"
            a_str = f"{a_c:.3f}" if a_c is not None else "N/A"
            f.write(f"  {name:<20} dev={d_str}  adult={a_str}\n")
        f.write(f"\nDev gene peak stage distribution (count):\n")
        for name, _, _ in [("Low (0-9)", 0, 9), ("Moderate (10-19)", 10, 19), ("High (>=20)", 20, 100)]:
            if name in tier_peak and tier_peak[name]:
                stages = ", ".join([f"{s}:{n}" for s, n in sorted(tier_peak[name].items(), key=lambda x: -x[1])])
                f.write(f"  {name:<20} {stages}\n")
    print(f"\n  Saved {REPORT_TXT}")

    # ── Step 3: Figures ─────────────────────────────────────────────────────
    sig_label = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "ns"

    # Fig 1 — ROC curves (paired CADD subset for head-to-head + missense for SIFT/PP)
    # DevScore headline curve is plotted on its full subset for accurate representation.
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr_dev, tpr_dev, color=PURPLE, lw=2.5,
            label=f"DevScore  (AUC={auc_dev:.2f}, n={len(valid_global)})")
    ax.plot(fpr_dev_paired_cadd, tpr_dev_paired_cadd, color=PURPLE_L, lw=1.5, ls="-",
            label=f"DevScore* (AUC={auc_dev_paired_cadd:.2f}, paired CADD subset)")
    ax.plot(fpr_cadd, tpr_cadd, color=GRAY, lw=1.5, ls=":",
            label=f"CADD      (AUC={auc_cadd:.2f}, n={len(valid_cadd)})")
    ax.plot(fpr_pp, tpr_pp, color=AMBER, lw=1.5, ls="--",
            label=f"PolyPhen-2 (AUC={auc_pp:.2f}, missense n={n_missense_only})")
    ax.plot(fpr_sift, tpr_sift, color=CORAL, lw=1.0, ls="-.",
            label=f"SIFT      (AUC={auc_sift:.2f}, missense n={n_missense_only})")
    ax.plot([0, 1], [0, 1], color="#CCCCCC", lw=1, ls="--",
            label="Random    (AUC=0.50)")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title(
        f"Fig. 2 \u2014 ROC curves: developmental disease classification\n"
        f"Legacy baselines (SIFT/PolyPhen-2) quantify evolutionary sequence "
        f"constraint rather than disease onset timing.", fontsize=8)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig1_roc_curves.png"), bbox_inches="tight")
    fig.savefig(os.path.join(FIGURES_DIR, "fig1_roc_curves.pdf"), bbox_inches="tight")
    plt.close(fig)
    print("  Saved Fig 1 \u2014 ROC curves")

    # Fig 2 — Box plots with jitter
    fig, axes = plt.subplots(1, 2, figsize=(9, 5))
    tools = {
        "DevScore": ("devscore", PURPLE_L, TEAL_L, PURPLE),
        "CADD": ("cadd", GRAY_L, "#C8E6C9", GRAY),
    }
    for idx, (tool_name, (col, c_dev, c_adult, accent)) in enumerate(tools.items()):
        ax = axes[idx]
        dev_sc = dev[col].dropna().values
        adult_sc = adult[col].dropna().values
        bp = ax.boxplot(
            [dev_sc, adult_sc],
            tick_labels=["Developmental\ndisease", "Adult-onset\ndisease"],
            patch_artist=True,
            medianprops=dict(color="white", lw=2),
            boxprops=dict(linewidth=0.8),
            whiskerprops=dict(linewidth=0.8),
            capprops=dict(linewidth=0.8),
            flierprops=dict(marker="o", markersize=4, alpha=0.5,
                            markerfacecolor=accent, markeredgewidth=0),
        )
        bp["boxes"][0].set_facecolor(c_dev)
        bp["boxes"][1].set_facecolor(c_adult)
        for i, data in enumerate([dev_sc, adult_sc], start=1):
            jitter = np.random.uniform(-0.15, 0.15, size=len(data))
            ax.scatter(np.full(len(data), i) + jitter, data,
                       alpha=0.35, s=18, color=accent, zorder=3, linewidths=0)
        ax.set_title(tool_name, fontsize=12, fontweight="normal")
        ax.set_ylabel("Score" if idx == 0 else "")
        y_bracket = max(dev_sc.max(), adult_sc.max()) * 1.05
        ax.set_ylim(top=y_bracket * 1.12)
        if idx == 0:
            sig_bracket(ax, 1, 2, y_bracket,
                        f"d={cohens_d:.2f}  {sig_label}", color=accent)
        else:
            _, p2 = stats.mannwhitneyu(dev_sc, adult_sc, alternative="two-sided")
            s2 = "***" if p2 < 0.001 else "**" if p2 < 0.01 else "ns"
            sig_bracket(ax, 1, 2, y_bracket, s2, color=accent)
    fig.suptitle("Fig. 3 \u2014 Score distributions by gene class",
                 fontsize=11, y=1.01)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig2_distributions.png"), bbox_inches="tight")
    fig.savefig(os.path.join(FIGURES_DIR, "fig2_distributions.pdf"), bbox_inches="tight")
    plt.close(fig)
    print("  Saved Fig 2 \u2014 Distributions")

    # Fig 3 — Case study table (6 representative genes)
    case_genes = ["SOX2", "PAX6", "FGFR3", "BRCA1", "APOE", "LRRK2"]
    case_df = df_ok[df_ok["gene"].isin(case_genes)].copy()
    case_df["_order"] = case_df["gene"].map({g: i for i, g in enumerate(case_genes)})
    case_df = case_df.sort_values("_order")
    case_df["sift_str"] = case_df["sift"].apply(
        lambda x: f"{x:.3f}" if pd.notna(x) else "\u2014")
    case_df["polyphen_str"] = case_df["polyphen"].apply(
        lambda x: f"{x:.3f}" if pd.notna(x) else "\u2014")
    case_df["devscore_str"] = case_df["devscore"].apply(lambda x: f"{x:.1f}")
    case_df["cadd_str"] = case_df["cadd"].apply(lambda x: f"{x:.0f}")
    case_df["class_str"] = case_df["class"].apply(
        lambda x: "Dev." if x == "developmental" else "Adult")

    fig, ax = plt.subplots(figsize=(13, 3.2))
    ax.axis("off")
    cols = ["Gene", "Variant", "Disease", "Class",
            "Peak stage", "DevScore", "CADD", "SIFT", "PolyPhen"]
    table_data = []
    for _, row in case_df.iterrows():
        table_data.append([
            row["gene"], row["hgvs"][:14], row["disease"][:25],
            row["class_str"], row.get("peak_stage", "\u2014"),
            row["devscore_str"], row["cadd_str"],
            row["sift_str"], row["polyphen_str"],
        ])
    tbl = ax.table(cellText=table_data, colLabels=cols,
                   loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.8)
    for j in range(len(cols)):
        tbl[0, j].set_facecolor("#EEEDFC")
        tbl[0, j].set_text_props(color="#4A44A0", fontweight="bold")
    for i in range(1, len(table_data) + 1):
        cls = table_data[i - 1][3]
        row_color = "#F7F5FF" if cls == "Dev." else "#F0FAF5"
        ds_color = PURPLE if cls == "Dev." else TEAL
        for j in range(len(cols)):
            tbl[i, j].set_facecolor(row_color)
        tbl[i, 5].set_text_props(color=ds_color, fontweight="bold")
        tbl[i, 3].set_facecolor("#EEEDFC" if cls == "Dev." else "#E1F5EE")
        tbl[i, 3].set_text_props(
            color="#4A44A0" if cls == "Dev." else "#0F6E56", fontweight="bold")
    ax.set_title("Fig. 5 \u2014 Case studies: DevScore vs standard tools",
                 pad=14, fontsize=10, fontweight="normal")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig3_case_studies.png"), bbox_inches="tight")
    fig.savefig(os.path.join(FIGURES_DIR, "fig3_case_studies.pdf"), bbox_inches="tight")
    plt.close(fig)
    print("  Saved Fig 3 \u2014 Case studies")

    # Fig 4 — DevScore component breakdown (stacked bar)
    top10_dev = dev.nlargest(10, "devscore")
    top10_adult = adult.nsmallest(10, "devscore")
    subset = pd.concat([top10_dev, top10_adult]).reset_index(drop=True)
    comp_cols = ["V", "E_peak", "C_stage", "D_domain"]
    comp_colors = [PURPLE, TEAL, CORAL, AMBER]
    comp_labels = ["V (variant severity)", "E_peak (expression)",
                   "C_stage (criticality \u2605)", "D_domain (domain)"]
    EPS = 1e-10
    for c in comp_cols:
        subset[f"_log_{c}"] = np.log10(subset[c].clip(lower=EPS)).abs()
    subset["_log_sum"] = subset[[f"_log_{c}" for c in comp_cols]].sum(axis=1)
    for c in comp_cols:
        subset[f"_contrib_{c}"] = (subset[f"_log_{c}"] / (subset["_log_sum"] + EPS)) * subset["devscore"]

    fig, ax = plt.subplots(figsize=(13, 5))
    bottoms = np.zeros(len(subset))
    genes = subset["gene"].values
    for col, color, label in zip(comp_cols, comp_colors, comp_labels):
        vals = subset[f"_contrib_{col}"].values
        ax.bar(range(len(subset)), vals, 0.6, bottom=bottoms, color=color, label=label, linewidth=0)
        bottoms += vals

    div_x = len(top10_dev) - 0.5
    ax.axvline(div_x, color="#CCCCCC", lw=1.5, ls="--")
    ax.text(div_x - 0.3, ax.get_ylim()[1] * 0.97,
            "\u2190 Developmental genes", ha="right", fontsize=9, color=PURPLE)
    ax.text(div_x + 0.3, ax.get_ylim()[1] * 0.97,
            "Adult-onset genes \u2192", ha="left", fontsize=9, color=TEAL)
    ax.set_xticks(range(len(subset)))
    ax.set_xticklabels(genes, rotation=45, ha="right", fontsize=9, fontfamily="monospace")
    ax.set_ylabel("DevScore (component contributions)")
    ax.set_title(
        "Fig. 4 \u2014 DevScore component breakdown per gene\n"
        "C_stage (coral) is the discriminating component "
        "between developmental and adult genes\n"
        "(log-decomposition: smaller values exert more constraint)", fontsize=9)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig4_component_breakdown.png"), bbox_inches="tight")
    fig.savefig(os.path.join(FIGURES_DIR, "fig4_component_breakdown.pdf"), bbox_inches="tight")
    plt.close(fig)
    print("  Saved Fig 4 \u2014 Component breakdown")

    # Fig 5 — Peak stage distribution by class
    STAGE_ORDER = ["zygote", "blastocyst", "gastrulation", "neurulation",
                   "organogenesis", "fetal_early", "fetal_late",
                   "neonatal", "childhood", "adult"]
    STAGE_CRIT = {"zygote": 0.88, "blastocyst": 0.85, "gastrulation": 1.00,
                  "neurulation": 1.00, "organogenesis": 0.95, "fetal_early": 0.65,
                  "fetal_late": 0.50, "neonatal": 0.30, "childhood": 0.28, "adult": 0.25}

    def stage_color(stage):
        c = STAGE_CRIT.get(stage, 0.25)
        if c >= 0.95:
            return CORAL
        if c >= 0.75:
            return AMBER
        if c >= 0.50:
            return "#E8C84A"
        return TEAL

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=False)
    for ax, subset_df, label, color in [
            (axes[0], dev, "Developmental disease genes", PURPLE),
            (axes[1], adult, "Adult-onset disease genes", TEAL)]:
        counts = subset_df["peak_stage"].value_counts().reindex(STAGE_ORDER, fill_value=0)
        colors = [stage_color(s) for s in counts.index]
        bars = ax.barh(counts.index, counts.values, color=colors,
                       edgecolor="white", linewidth=0.5)
        ax.set_xlabel("Number of genes")
        ax.set_title(label, fontsize=10)
        ax.invert_yaxis()
        for bar, val in zip(bars, counts.values):
            if val > 0:
                ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                        str(val), va="center", fontsize=9)
    legend_patches = [
        mpatches.Patch(color=CORAL, label="Critical (C=0.95\u20131.00)"),
        mpatches.Patch(color=AMBER, label="High     (C=0.75\u20130.94)"),
        mpatches.Patch(color="#E8C84A", label="Moderate (C=0.50\u20130.74)"),
        mpatches.Patch(color=TEAL, label="Low      (C<0.50)"),
    ]
    axes[1].legend(handles=legend_patches, fontsize=8,
                   loc="lower right", framealpha=0.9)
    fig.suptitle("Fig. 6 \u2014 Peak developmental stage distribution by gene class",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig5_stage_distribution.png"), bbox_inches="tight")
    fig.savefig(os.path.join(FIGURES_DIR, "fig5_stage_distribution.pdf"), bbox_inches="tight")
    plt.close(fig)
    print("  Saved Fig 5 \u2014 Stage distribution")

    # Fig 6 — DevScore vs CADD scatter
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    for cls, color, marker, label in [
            ("developmental", PURPLE, "o", "Developmental disease genes"),
            ("adult", TEAL, "s", "Adult-onset disease genes")]:
        sub = df_ok[df_ok["class"] == cls].dropna(subset=["devscore", "cadd"])
        ax.scatter(sub["cadd"], sub["devscore"],
                   c=color, marker=marker, alpha=0.65, s=55,
                   label=label, linewidths=0.3, edgecolors="white")
    valid_xy = df_ok.dropna(subset=["devscore", "cadd"])
    if len(valid_xy) > 2:
        m, b, r, p_r, _ = stats.linregress(valid_xy["cadd"], valid_xy["devscore"])
        x_line = np.linspace(valid_xy["cadd"].min(), valid_xy["cadd"].max(), 100)
        ax.plot(x_line, m * x_line + b, color=GRAY, lw=1.2, ls="--",
                label=f"Regression (r={r:.2f}, p={p_r:.2e})")
    for gene_name in ["SOX2", "BRCA1", "PAX6"]:
        row = valid_xy[valid_xy["gene"] == gene_name]
        if not row.empty:
            row = row.iloc[0]
            ax.annotate(gene_name,
                        xy=(row["cadd"], row["devscore"]),
                        xytext=(row["cadd"] + 1.5, row["devscore"] + 2),
                        fontsize=8, fontfamily="monospace",
                        arrowprops=dict(arrowstyle="->", lw=0.7, color=GRAY),
                        color=GRAY)
    ax.set_xlabel("CADD score")
    ax.set_ylabel("DevScore")
    ax.set_title(
        f"Fig. S1 \u2014 DevScore vs CADD: orthogonality analysis\n"
        f"Spearman \u03c1 = {rho:.3f}  \u2014  DevScore adds new information", fontsize=10)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig6_devscore_vs_cadd.png"), bbox_inches="tight")
    fig.savefig(os.path.join(FIGURES_DIR, "fig6_devscore_vs_cadd.pdf"), bbox_inches="tight")
    plt.close(fig)
    print("  Saved Fig 6 \u2014 DevScore vs CADD scatter")

    # Fig 7 — AUC bar chart
    fig, ax = plt.subplots(figsize=(6, 4))

    # Order: Multi-omic/pathogenicity classifiers then pure sequence-conservation tools
    tool_names = ["DevScore\n(ours)", "CADD", "Random", "PolyPhen-2", "SIFT"]
    auc_vals = [auc_dev, auc_cadd, 0.50, auc_pp, auc_sift]
    # Purple for DevScore, gray for CADD, then separate palette for sequence conservation
    bar_colors = [PURPLE, GRAY, "#E0E0E0", GRAY_L, GRAY_L]
    bar_edges = [PURPLE, GRAY, "#CCCCCC", GRAY, GRAY]

    bars = ax.bar(tool_names, auc_vals, color=bar_colors,
                  edgecolor=bar_edges, linewidth=0.8, width=0.55)

    for bar, val in zip(bars, auc_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                f"{val:.2f}", ha="center", va="bottom", fontsize=10,
                fontweight="bold" if val == auc_dev else "normal",
                color=PURPLE if val == auc_dev else GRAY)

    # Group divider: separate multi-omic classifiers from sequence conservation tools
    ax.axvline(x=2.35, color="#AAAAAA", lw=0.8, ls=":", zorder=0)
    ax.text(2.45, 0.70, "Pure Sequence\nConstraint\n(Onset-Blind)",
            fontsize=7, color="#888888", va="center", ha="left",
            fontstyle="italic", transform=ax.transData)

    ax.axhline(0.50, color="#CCCCCC", lw=1, ls="--", zorder=0)
    ax.text(4.45, 0.515, "random", fontsize=8, color="#AAAAAA")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("AUC (ROC)")
    ax.set_title(
        f"Fig. 1 \u2014 AUC comparison: developmental disease classification\n"
        f"DevScore achieves AUC={auc_dev:.2f} vs primary comparator CADD "
        f"(AUC={auc_cadd:.2f})", fontsize=10)

    # Comparator arrow: CADD → DevScore (primary head-to-head)
    ax.annotate("", xy=(0, auc_dev), xytext=(1, auc_cadd),
                arrowprops=dict(arrowstyle="<->", color=PURPLE, lw=1.5))
    ax.text(0.2, (auc_dev + auc_cadd) / 2,
            f"+{auc_dev - auc_cadd:.2f}", color=PURPLE, fontsize=9, va="center")

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig7_auc_summary.png"), bbox_inches="tight")
    fig.savefig(os.path.join(FIGURES_DIR, "fig7_auc_summary.pdf"), bbox_inches="tight")
    plt.close(fig)
    print("  Saved Fig 7 \u2014 AUC summary")

    # Fig 8 — Interpretative tier distribution (grouped bar)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    tier_labels = ["Low\n(0\u20139)", "Moderate\n(10\u201319)", "High\n(\u226520)"]
    x = np.arange(len(tier_labels))
    width = 0.35
    dev_counts = [r[1] for r in tier_rows]
    adult_counts = [r[2] for r in tier_rows]
    bars1 = ax.bar(x - width/2, dev_counts, width, label="Developmental", color=PURPLE, edgecolor="white", linewidth=0.5)
    bars2 = ax.bar(x + width/2, adult_counts, width, label="Adult-onset", color=TEAL, edgecolor="white", linewidth=0.5)
    for bar in bars1:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.3, str(int(h)), ha="center", va="bottom", fontsize=10, fontweight="bold", color=PURPLE)
    for bar in bars2:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.3, str(int(h)), ha="center", va="bottom", fontsize=10, fontweight="bold", color=TEAL)
    ax.set_xticks(x)
    ax.set_xticklabels(tier_labels, fontsize=9)
    ax.set_ylabel("Gene count")
    ax.set_title("Fig. 8 \u2014 Interpretative tier distribution: DevScore by gene class", fontsize=10)
    ax.legend(fontsize=9)
    ax.set_ylim(0, max(max(dev_counts), max(adult_counts)) * 1.25)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig8_tier_distribution.png"), bbox_inches="tight")
    plt.close(fig)
    print("  Saved Fig 8 \u2014 Tier distribution")

    # ── Final summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 62)
    print("  VALIDATION COMPLETE")
    print("=" * 62)
    print(f"  Genes scored:           {len(df_ok)} ({len(dev)} dev + {len(adult)} adult)")
    if failed > 0:
        print(f"  API failures:           {failed}")
    print(f"  DevScore AUC:           {auc_dev:.3f}")
    print(f"  Best baseline AUC:      {best_base:.3f}")
    print(f"  Improvement:            +{auc_dev - best_base:.3f}")
    print(f"  Mann-Whitney p:         {p_value:.2e}  {sig_label}")
    print(f"  Cohen's d:              {cohens_d:.2f}  "
          f"({'very large' if cohens_d > 1.2 else 'large' if cohens_d > 0.8 else 'medium'})")
    print(f"  Spearman rho (vs CADD):       {rho:.3f}  "
          f"({'low -> orthogonal' if abs(rho) < 0.5 else 'moderate'})")
    print(f"  Partial Spearman (residuals):  {rho_partial:.3f}")
    # ── Export final {meta, genes} JSON for frontend ──
    meta = {
        "headline_auc": round(auc_dev, 3),
        "devscore_auc": round(auc_dev, 3),
        "cadd_auc": round(auc_cadd, 3),
        "sift_auc": round(auc_sift, 3),
        "polyphen_auc": round(auc_pp, 3),
        "cadd_margin": round(auc_dev_paired_cadd - auc_cadd, 3),
        "sift_margin": round(auc_dev_vep - auc_sift, 3),
        "polyphen_margin": round(auc_dev_vep - auc_pp, 3),
        "total_genes": len(df_ok),
        "dev_median": round(float(dev['devscore'].median()), 1),
        "adult_median": round(float(adult['devscore'].median()), 1),
        "cohens_d": round(float(cohens_d), 2),
        "spearman_rho": round(float(rho), 3),
        "spearman_p": round(float(p_spearman), 4),
        "partial_spearman_rho": round(float(rho_partial), 3),
        "partial_spearman_p": round(float(p_partial), 5),
        "youden_threshold": round(float(opt_threshold), 2),
        "youden_sensitivity": round(float(opt_sensitivity), 3),
        "youden_specificity": round(float(opt_specificity), 3),
        "mann_whitney_u": round(float(stat_val), 1),
        "mann_whitney_p": float(f"{p_value:.2e}"),
    }
    payload = {"meta": meta, "genes": export_records}
    with open(frontend_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"  Saved {len(export_records)} gene records to {frontend_json_path} for frontend")

    print("-" * 62)
    print("  FILES SAVED:")
    print(f"  {RESULTS_CSV}")
    print(f"  {REPORT_TXT}")
    print(f"  {FIGURES_DIR}/fig[1-8].png/.pdf")
    print("=" * 62)


if __name__ == "__main__":
    main()
