#!/usr/bin/env python3
"""Weight sensitivity analysis for CADD:ClinVar ratio in DevScore V component.

Tests how different CADD weights (0.50 to 0.80) affect AUC,
Cohen's d, and rank stability for dev vs adult-onset classification.

Usage: python validation/weight_sensitivity.py
"""

import csv
import json
import math
import statistics
import sys
import time
import urllib.request
import urllib.error

API_BASE = "http://localhost:8000"
THROTTLE_S = 1.5
REQUEST_TIMEOUT = 60

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

# ── 110-gene benchmark (mirrored from run_validation.py) ──────────────────

DEVELOPMENTAL_GENES = [
    ("SOX2",   "c.70C>T"),
    ("PAX6",   "c.357G>A"),
    ("TWIST1", "c.586C>T"),
    ("FGFR3",  "c.1138G>A"),
    ("NKX2-5", "c.655G>T"),
    ("TBX5",   "c.1001C>T"),
    ("PTPN11", "c.922A>G"),
    ("NIPBL",  "c.5350G>T"),
    ("KAT6A",  "c.1358A>G"),
    ("FOXP2",  "c.1652T>C"),
    ("CHD7",   "c.2815G>T"),
    ("KDM6A",  "c.3272C>T"),
    ("MED13L", "c.2623G>A"),
    ("SETD5",  "c.1957C>T"),
    ("ADNP",   "c.2157C>A"),
    ("ANKRD11","c.1903C>T"),
    ("ARID1B", "c.3637C>T"),
    ("KMT2D",  "c.15607C>T"),
    ("EP300",  "c.4417C>T"),
    ("CREBBP", "c.4435C>T"),
    ("DYRK1A", "c.703C>T"),
    ("FOXG1",  "c.256C>T"),
    ("MECP2",  "c.397C>T"),
    ("PTEN",   "c.697C>T"),
    ("RET",    "c.1900T>C"),
    ("SHH",    "c.736C>T"),
    ("GLI3",   "c.2497C>T"),
    ("NOTCH3", "c.328C>T"),
    ("JAG1",   "c.1808G>A"),
    ("EYA1",   "c.1435C>T"),
    ("SALL1",  "c.3167C>T"),
    ("WT1",    "c.1180C>T"),
    ("PAX2",   "c.76C>T"),
    ("ROBO3",  "c.2747C>T"),
    ("EFNB1",  "c.391C>T"),
    ("FGF8",   "c.412C>T"),
    ("OTX2",   "c.402C>T"),
    ("VSX2",   "c.574C>T"),
    ("FOXC1",  "c.829C>T"),
    ("GJB2",   "c.35delG"),
    ("MYO7A",  "c.5936C>T"),
    ("CLN3",   "c.280_461del"),
    ("HESX1",  "c.449G>A"),
    ("LHX3",   "c.236G>A"),
    ("PROP1",  "c.301_302delAG"),
    ("DHCR7",  "c.1210C>T"),
    ("PKD1",   "c.12058C>T"),
    ("PDGFRB", "c.1681C>T"),
    ("TRPV4",  "c.1855C>T"),
    ("RUNX2",  "c.674G>A"),
    ("HOXD13", "c.905G>A"),
    ("SALL4",  "c.1873C>T"),
    ("STRA6",  "c.1219C>T"),
    ("KAT6B",  "c.3978C>T"),
    ("SMAD3",  "c.1024C>T"),
    ("FBN1",   "c.5788C>T"),
    ("COL1A1", "c.934C>T"),
    ("COL2A1", "c.4006C>T"),
    ("COMP",   "c.1273C>T"),
    ("FBN2",   "c.3454C>T"),
]

ADULT_ONSET_GENES = [
    ("BRCA1",  "c.5266dupC"),
    ("BRCA2",  "c.5946delT"),
    ("APOE",   "c.388T>C"),
    ("LRRK2",  "c.6055G>A"),
    ("SNCA",   "c.88G>C"),
    ("HTT",    "c.52G>A"),
    ("ATM",    "c.7271T>G"),
    ("MLH1",   "c.1852_1854del"),
    ("MSH2",   "c.1865T>A"),
    ("APC",    "c.3927_3931del"),
    ("VHL",    "c.499C>T"),
    ("NF1",    "c.3199G>T"),
    ("NF2",    "c.863_864del"),
    ("RB1",    "c.2644C>T"),
    ("TP53",   "c.817C>T"),
    ("CDKN2A", "c.238C>T"),
    ("MEN1",   "c.1546C>T"),
    ("SDHB",   "c.423+1G>T"),
    ("TSC1",   "c.1888C>T"),
    ("TSC2",   "c.5024C>T"),
    ("PKD2",   "c.2243C>T"),
    ("MYBPC3", "c.3330+2T>G"),
    ("MYH7",   "c.1208G>A"),
    ("KCNQ1",  "c.1032G>A"),
    ("SCN5A",  "c.4234C>T"),
    ("LDLR",   "c.1418G>A"),
    ("PCSK9",  "c.1120G>T"),
    ("F5",     "c.1601G>A"),
    ("HBB",    "c.20A>T"),
    ("CFTR",   "c.1521_1523del"),
    ("G6PD",   "c.202G>A"),
    ("HEXA",   "c.1274_1277dup"),
    ("GBA",    "c.1226A>G"),
    ("FMR1",   "c.413G>A"),
    ("AR",     "c.2713C>T"),
    ("PKHD1",  "c.107C>T"),
    ("COL3A1", "c.2411G>A"),
    ("TGFBR2", "c.1582C>T"),
    ("CACNA1A","c.4042C>T"),
    ("PRKCG",  "c.1258C>T"),
    ("ATXN1",  "c.1A>G"),
    ("DMPK",   "c.1268A>G"),
    ("SOD1",   "c.272A>G"),
    ("FUS",    "c.1561C>T"),
    ("TARDBP", "c.1144G>A"),
    ("OPTN",   "c.458G>A"),
    ("VCP",    "c.464G>A"),
    ("SQSTM1", "c.1175C>T"),
    ("GRN",    "c.709-1G>A"),
    ("MAPT",   "c.1853T>C"),
]

# ── API call ───────────────────────────────────────────────────────────────

def query_api(gene, hgvs):
    payload = json.dumps({"gene": gene, "hgvs": hgvs}).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/score",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT)
    return json.loads(resp.read().decode())


# ── Metrics ────────────────────────────────────────────────────────────────

def compute_auc(labels, scores):
    """ROC AUC via the trapezoidal rule."""
    pairs = sorted(zip(scores, labels), key=lambda x: -x[0])
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    rank_sum = 0
    for i, (_, label) in enumerate(pairs):
        if label == 1:
            rank_sum += i + 1
    u = rank_sum - n_pos * (n_pos + 1) / 2
    return u / (n_pos * n_neg)


def compute_cohens_d(group1, group2):
    if len(group1) < 2 or len(group2) < 2:
        return 0.0
    m1, m2 = statistics.mean(group1), statistics.mean(group2)
    v1, v2 = statistics.variance(group1), statistics.variance(group2)
    n1, n2 = len(group1), len(group2)
    s_pooled = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    return (m1 - m2) / s_pooled if s_pooled > 0 else 0.0


def mann_whitney_u(labels, scores):
    """One-sided Mann-Whitney U test p-value via normal approximation."""
    n = len(labels)
    pairs = sorted(zip(scores, labels), key=lambda x: -x[0])
    n_pos = sum(labels)
    n_neg = n - n_pos
    if n_pos == 0 or n_neg == 0:
        return 1.0
    rank_sum_pos = sum(i + 1 for i, (_, label) in enumerate(pairs) if label == 1)
    u = rank_sum_pos - n_pos * (n_pos + 1) / 2
    mu = n_pos * n_neg / 2
    sigma = math.sqrt(n_pos * n_neg * (n + 1) / 12)
    if sigma == 0:
        return 1.0
    z = (u - mu) / sigma
    # one-sided normal CDF approximation
    return 0.5 * math.erfc(z / math.sqrt(2))


def spearman_rho(x, y):
    n = len(x)
    if n < 3:
        return 1.0
    rx = [sorted(x).index(v) + 1 for v in x]
    ry = [sorted(y).index(v) + 1 for v in y]
    d_sq = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1 - 6 * d_sq / (n * (n * n - 1))


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    all_genes = [(g, v, 0) for (g, v) in DEVELOPMENTAL_GENES] + \
                [(g, v, 1) for (g, v) in ADULT_ONSET_GENES]

    total = len(all_genes)

    # ── Step 1: Collect data from API ──
    rows = []  # [(gene, group, cadd, clinvar_w, e_peak, c_stage, d_domain, devscore)]
    failures = []

    print(f"\n  Querying DevMutDB API ({API_BASE}) for {total} genes...\n")

    for idx, (gene, hgvs, group) in enumerate(all_genes, 1):
        print(f"    [{idx:>3}/{total}] {gene:<12} {hgvs:<16} ... ", end="", flush=True)
        try:
            data = query_api(gene, hgvs)
        except Exception as exc:
            print(f"FAILED — {exc}")
            failures.append((gene, hgvs, str(exc)))
            time.sleep(THROTTLE_S)
            continue

        try:
            vcomp = data.get("component_explanation", {}).get("V_pathogenicity", {})
            cadd = vcomp.get("cadd_phred")
            clinvar_w = vcomp.get("clinvar_weight")
            e_peak = data.get("E_peak")
            c_stage = data.get("C_stage")
            d_domain = data.get("D_domain")
            devscore = data.get("score")

            if cadd is None or clinvar_w is None:
                print(f"SKIP — missing CADD/ClinVar")
                failures.append((gene, hgvs, "missing CADD/ClinVar"))
                time.sleep(THROTTLE_S)
                continue

            rows.append((gene, group, float(cadd), float(clinvar_w),
                         float(e_peak or 0), float(c_stage or 0),
                         float(d_domain or 0), float(devscore or 0)))
            print(f"V={data.get('V'):.3f}  CADD={cadd}  ClinVar={clinvar_w:.1f}  DevScore={devscore}")
        except (KeyError, TypeError, ValueError) as exc:
            print(f"PARSE ERROR — {exc}")
            failures.append((gene, hgvs, f"parse error: {exc}"))

        time.sleep(THROTTLE_S)

    n_success = len(rows)
    print(f"\n  Successfully collected: {n_success}/{total}")
    if failures:
        print(f"  Failures ({len(failures)}):")
        for g, h, reason in failures:
            print(f"    - {g} {h}: {reason}")
    print()

    if n_success == 0:
        print("  No data collected. Aborting.")
        sys.exit(1)

    # ── Step 2: Evaluate each weighting ──
    cadd_weights = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
    ref_idx = cadd_weights.index(0.60)
    metrics = []

    for w_cadd in cadd_weights:
        w_clinvar = 1.0 - w_cadd
        scores = []
        labels = []
        ref_scores_60 = []

        for gene, group, cadd, clinvar_w, e_peak, c_stage, d_domain, devscore_ref in rows:
            labels.append(group)
            v_new = clamp((cadd / 40.0) * w_cadd + clinvar_w * w_clinvar)
            devscore_new = v_new * e_peak * c_stage * d_domain * 100
            scores.append(devscore_new)

            if w_cadd == 0.60:
                ref_scores_60.append(devscore_new)

        dev_scores = [scores[i] for i, lbl in enumerate(labels) if lbl == 0]
        adult_scores = [scores[i] for i, lbl in enumerate(labels) if lbl == 1]

        auc = compute_auc(labels, scores)
        d = compute_cohens_d(dev_scores, adult_scores)
        p = mann_whitney_u(labels, scores)

        if w_cadd == 0.60:
            rho = 1.0
        else:
            rho = spearman_rho(ref_scores_60, scores)

        med_dev = statistics.median(dev_scores) if dev_scores else 0
        med_adult = statistics.median(adult_scores) if adult_scores else 0

        metrics.append((w_cadd, auc, d, p, rho, med_dev, med_adult))

    # ── Step 3: Print summary table ──
    print("=" * 92)
    print("  WEIGHT SENSITIVITY ANALYSIS — CADD:ClinVar Ratio Impact on DevScore")
    print("=" * 92)
    print(f"  Benchmark: {n_success} genes ({sum(1 for r in rows if r[1]==0)} dev, "
          f"{sum(1 for r in rows if r[1]==1)} adult)")
    print()
    print(f"  {'Weight':>10} | {'AUC':>8} | {'Cohen d':>8} | {'p-value':>10} | "
          f"{'Spearman ρ':>10} | {'Dev Med':>8} | {'Adult Med':>9}")
    print(f"  {'-'*10}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*8}-+-{'-'*9}")
    for w, auc, d, p, rho, md, ma in metrics:
        flag = "  ← current" if abs(w - 0.60) < 0.001 else ""
        print(f"  {w*100:>5.0f}:{w*100:>3.0f}   | {auc:>8.4f} | {d:>8.3f} | {p:>10.2e} | {rho:>10.4f} | {md:>8.1f} | {ma:>9.1f}{flag}")

    print("=" * 92)

    # ── Step 4: Compare AUC differences ──
    print()
    print("  AUC delta from 60:40 baseline:")
    base_auc = metrics[ref_idx][1]
    for w, auc, _, _, _, _, _ in metrics:
        delta = auc - base_auc
        marker = " ← current" if abs(w - 0.60) < 0.001 else ""
        print(f"    {w*100:>5.0f}:{w*100:>3.0f} → AUC Δ = {delta:+.5f}{marker}")

    print()
    print("  Done.")

    # ── Step 5: Write CSV (per-gene raw data) ──
    csv_path = "validation/weight_sensitivity_genes.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["gene", "group", "cadd", "clinvar_w", "e_peak", "c_stage", "d_domain", "devscore"])
        for gene, group, cadd, clinvar_w, e_peak, c_stage, d_domain, devscore in rows:
            writer.writerow([gene, "dev" if group == 0 else "adult",
                             cadd, clinvar_w, e_peak, c_stage, d_domain, devscore])
    print(f"\n  Per-gene data saved to: {csv_path}")

    # ── Step 6: Write CSV (sensitivity summary) ──
    csv_path2 = "validation/weight_sensitivity_summary.csv"
    with open(csv_path2, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cadd_weight", "clinvar_weight", "auc", "cohens_d", "p_value", "spearman_rho", "dev_median", "adult_median"])
        for w, auc, d, p, rho, md, ma in metrics:
            writer.writerow([w, 1-w, round(auc, 5), round(d, 4), f"{p:.2e}", round(rho, 5), round(md, 2), round(ma, 2)])
    print(f"  Summary table saved to:  {csv_path2}")


if __name__ == "__main__":
    main()
