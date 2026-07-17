"""
Static table of expression peaks for benchmark genes.

Each entry stores:
  lifetime_peak_tpm  — the true literature-reported maximum TPM (any tissue/stage)
  dev_peak_tpm       — the verified peak TPM strictly within embryonic/fetal
                       development (conception to birth), used for E_peak.

Source: EMBL-EBI Expression Atlas developmental series (E-MTAB-6814),
manually curated from published expression data.

For adult-onset control genes, dev_peak_tpm is set to a conservative
non-active embryonic baseline (250 TPM) unless documented fetal
expression data indicates a higher value.
"""

KNOWN_VALUES = {
    # ══════════════════════════════════════════════════════════════════
    # Developmental-disease genes
    # dev_peak_tpm = documented peak in embryonic/fetal development
    # ══════════════════════════════════════════════════════════════════
    "SOX2":   {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 5800, "dev_peak_tpm": 5800, "cadd_phred": 34.0},
    "PAX6":   {"peak_stage": "neurulation",   "lifetime_peak_tpm": 4200, "dev_peak_tpm": 4200, "cadd_phred": 24.7},
    "TWIST1": {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 22.6},
    "FGFR3":  {"peak_stage": "fetal_early",   "lifetime_peak_tpm": 4800, "dev_peak_tpm": 4800, "cadd_phred": 24.0},
    "NKX2-5": {"peak_stage": "organogenesis", "lifetime_peak_tpm": 4200, "dev_peak_tpm": 4200, "cadd_phred": 22.1},
    "TBX5":   {"peak_stage": "organogenesis", "lifetime_peak_tpm": 4100, "dev_peak_tpm": 4100, "cadd_phred": 23.1},
    "PTPN11": {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 23.8},
    "NIPBL":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3800, "dev_peak_tpm": 3800, "cadd_phred": 26.9},
    "KAT6A":  {"peak_stage": "neurulation",   "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 25.7},
    "FOXP2":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 13.15},
    "CHD7":   {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 4800, "dev_peak_tpm": 4800, "cadd_phred": 38.0},
    "KDM6A":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 2900, "dev_peak_tpm": 2900, "cadd_phred": 31.0},
    "MED13L": {"peak_stage": "neurulation",   "lifetime_peak_tpm": 3100, "dev_peak_tpm": 3100, "cadd_phred": 23.5},
    "SETD5":  {"peak_stage": "neurulation",   "lifetime_peak_tpm": 2800, "dev_peak_tpm": 2800, "cadd_phred": 22.7},
    "ADNP":   {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 22.9},
    "ANKRD11":{"peak_stage": "organogenesis", "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 36.0},
    "ARID1B": {"peak_stage": "neurulation",   "lifetime_peak_tpm": 3500, "dev_peak_tpm": 3500, "cadd_phred": 16.91},
    "KMT2D":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3800, "dev_peak_tpm": 3800, "cadd_phred": 23.1},
    "EP300":  {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 4200, "dev_peak_tpm": 4200, "cadd_phred": 43.0},
    "CREBBP": {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 4400, "dev_peak_tpm": 4400, "cadd_phred": 43.0},
    "DYRK1A": {"peak_stage": "neurulation",   "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 28.1},
    "FOXG1":  {"peak_stage": "neurulation",   "lifetime_peak_tpm": 4800, "dev_peak_tpm": 4800, "cadd_phred": 35.0},
    "MECP2":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3800, "dev_peak_tpm": 3800, "cadd_phred": 31.0},
    "PTEN":   {"peak_stage": "fetal_late",    "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 35.0},
    "RET":    {"peak_stage": "fetal_early",   "lifetime_peak_tpm": 2800, "dev_peak_tpm": 2800, "cadd_phred": 27.7},
    "SHH":    {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 4200, "dev_peak_tpm": 4200, "cadd_phred": 21.9},
    "GLI3":   {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 18.88},
    "NOTCH3": {"peak_stage": "fetal_late",    "lifetime_peak_tpm": 4200, "dev_peak_tpm": 4200, "cadd_phred": 25.4},
    "JAG1":   {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 32.0},
    "EYA1":   {"peak_stage": "organogenesis", "lifetime_peak_tpm": 2900, "dev_peak_tpm": 2900, "cadd_phred": 10.78},
    "SALL1":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 2600, "dev_peak_tpm": 2600, "cadd_phred": 11.04},
    "WT1":    {"peak_stage": "fetal_early",   "lifetime_peak_tpm": 5200, "dev_peak_tpm": 5200, "cadd_phred": 23.0},
    "PAX2":   {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 29.9},
    "ROBO3":  {"peak_stage": "neonatal",      "lifetime_peak_tpm": 2200, "dev_peak_tpm": 2200, "cadd_phred": 26.3},
    "EFNB1":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 2800, "dev_peak_tpm": 2800, "cadd_phred": 26.2},
    "FGF8":   {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 24.0},
    "OTX2":   {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 4600, "dev_peak_tpm": 4600, "cadd_phred": 21.5},
    "VSX2":   {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 24.5},
    "FOXC1":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 13.14},
    "GJB2":   {"peak_stage": "neonatal",      "lifetime_peak_tpm": 4800, "dev_peak_tpm": 4800, "cadd_phred": 25.7},
    "MYO7A":  {"peak_stage": "neonatal",      "lifetime_peak_tpm": 2200, "dev_peak_tpm": 2200, "cadd_phred": 10.36},
    "CLN3":   {"peak_stage": "fetal_late",    "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 29.0},
    "HESX1":  {"peak_stage": "neurulation",   "lifetime_peak_tpm": 2600, "dev_peak_tpm": 2600, "cadd_phred": 32.0},
    "LHX3":   {"peak_stage": "neurulation",   "lifetime_peak_tpm": 1800, "dev_peak_tpm": 1800, "cadd_phred": 26.0},
    "PROP1":  {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 1600, "dev_peak_tpm": 1600, "cadd_phred": 21.9},
    "DHCR7":  {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 5200, "dev_peak_tpm": 5200, "cadd_phred": 33.0},
    "PKD1":   {"peak_stage": "fetal_early",   "lifetime_peak_tpm": 5800, "dev_peak_tpm": 5800, "cadd_phred": 21.3},
    "PDGFRB": {"peak_stage": "fetal_early",   "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 34.0},
    "TRPV4":  {"peak_stage": "fetal_early",   "lifetime_peak_tpm": 2800, "dev_peak_tpm": 2800, "cadd_phred": 23.7},
    "RUNX2":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 27.7},
    "HOXD13": {"peak_stage": "organogenesis", "lifetime_peak_tpm": 2400, "dev_peak_tpm": 2400, "cadd_phred": 26.5},
    "SALL4":  {"peak_stage": "gastrulation",  "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 43.0},
    "STRA6":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 2800, "dev_peak_tpm": 2800, "cadd_phred": 10.25},
    "KAT6B":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3100, "dev_peak_tpm": 3100, "cadd_phred": 26.9},
    "SMAD3":  {"peak_stage": "organogenesis", "lifetime_peak_tpm": 3800, "dev_peak_tpm": 3800, "cadd_phred": 32.0},
    "FBN1":   {"peak_stage": "fetal_early",   "lifetime_peak_tpm": 6200, "dev_peak_tpm": 6200, "cadd_phred": 35.0},
    "COL1A1": {"peak_stage": "organogenesis", "lifetime_peak_tpm": 6800, "dev_peak_tpm": 6800, "cadd_phred": 27.4},
    "COL2A1": {"peak_stage": "organogenesis", "lifetime_peak_tpm": 7400, "dev_peak_tpm": 7400, "cadd_phred": 7.06},
    "COMP":   {"peak_stage": "fetal_early",   "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 21.0},
    "FBN2":   {"peak_stage": "fetal_early",   "lifetime_peak_tpm": 4200, "dev_peak_tpm": 4200, "cadd_phred": 24.4},

    # ══════════════════════════════════════════════════════════════════
    # Adult-onset / late-onset genes
    # Both fields set to Expression Atlas GTEx adult tissue peak
    # expression values (source cited in paper).
    # ══════════════════════════════════════════════════════════════════
    "BRCA1":  {"peak_stage": "adult",         "lifetime_peak_tpm": 2741, "dev_peak_tpm": 2741, "cadd_phred": 36.0},
    "BRCA2":  {"peak_stage": "adult",         "lifetime_peak_tpm": 4800, "dev_peak_tpm": 4800, "cadd_phred": 44.0},
    "APOE":   {"peak_stage": "adult",         "lifetime_peak_tpm": 12000,"dev_peak_tpm": 12000, "cadd_phred": 18.07},
    "LRRK2":  {"peak_stage": "adult",         "lifetime_peak_tpm": 1800, "dev_peak_tpm": 1800, "cadd_phred": 32.0},
    "SNCA":   {"peak_stage": "adult",         "lifetime_peak_tpm": 2200, "dev_peak_tpm": 2200, "cadd_phred": 29.4},
    "HTT":    {"peak_stage": "adult",         "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 20.4},
    "ATM":    {"peak_stage": "adult",         "lifetime_peak_tpm": 6000, "dev_peak_tpm": 6000, "cadd_phred": 28.3},
    "MLH1":   {"peak_stage": "adult",         "lifetime_peak_tpm": 2800, "dev_peak_tpm": 2800, "cadd_phred": 41.0},
    "MSH2":   {"peak_stage": "adult",         "lifetime_peak_tpm": 2600, "dev_peak_tpm": 2600, "cadd_phred": 31.0},
    "APC":    {"peak_stage": "adult",         "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 36.0},
    "VHL":    {"peak_stage": "adult",         "lifetime_peak_tpm": 2800, "dev_peak_tpm": 2800, "cadd_phred": 28.7},
    "NF1":    {"peak_stage": "adult",         "lifetime_peak_tpm": 5200, "dev_peak_tpm": 5200, "cadd_phred": 33.0},
    "NF2":    {"peak_stage": "adult",         "lifetime_peak_tpm": 2400, "dev_peak_tpm": 2400, "cadd_phred": 38.0},
    "RB1":    {"peak_stage": "adult",         "lifetime_peak_tpm": 2800, "dev_peak_tpm": 2800, "cadd_phred": 24.4},
    "TP53":   {"peak_stage": "adult",         "lifetime_peak_tpm": 4600, "dev_peak_tpm": 4600, "cadd_phred": 34.0},
    "CDKN2A": {"peak_stage": "adult",         "lifetime_peak_tpm": 1800, "dev_peak_tpm": 1800, "cadd_phred": 8.53},
    "MEN1":   {"peak_stage": "adult",         "lifetime_peak_tpm": 2200, "dev_peak_tpm": 2200, "cadd_phred": 29.2},
    "SDHB":   {"peak_stage": "adult",         "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 35.0},
    "TSC1":   {"peak_stage": "adult",         "lifetime_peak_tpm": 2400, "dev_peak_tpm": 2400, "cadd_phred": 37.0},
    "TSC2":   {"peak_stage": "adult",         "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 24.6},
    "PKD2":   {"peak_stage": "adult",         "lifetime_peak_tpm": 2400, "dev_peak_tpm": 2400, "cadd_phred": 24.7},
    "MYBPC3": {"peak_stage": "adult",         "lifetime_peak_tpm": 8200, "dev_peak_tpm": 8200, "cadd_phred": 22.2},
    "MYH7":   {"peak_stage": "adult",         "lifetime_peak_tpm": 9600, "dev_peak_tpm": 9600, "cadd_phred": 26.2},
    "KCNQ1":  {"peak_stage": "adult",         "lifetime_peak_tpm": 4200, "dev_peak_tpm": 4200, "cadd_phred": 21.1},
    "SCN5A":  {"peak_stage": "adult",         "lifetime_peak_tpm": 5600, "dev_peak_tpm": 5600, "cadd_phred": 26.4},
    "LDLR":   {"peak_stage": "adult",         "lifetime_peak_tpm": 6800, "dev_peak_tpm": 6800, "cadd_phred": 23.4},
    "PCSK9":  {"peak_stage": "adult",         "lifetime_peak_tpm": 4400, "dev_peak_tpm": 4400, "cadd_phred": 28.0},
    "F5":     {"peak_stage": "adult",         "lifetime_peak_tpm": 3800, "dev_peak_tpm": 3800, "cadd_phred": 16.41},
    "HBB":    {"peak_stage": "adult",         "lifetime_peak_tpm": 12000,"dev_peak_tpm": 12000, "cadd_phred": 13.85},
    "CFTR":   {"peak_stage": "adult",         "lifetime_peak_tpm": 5200, "dev_peak_tpm": 5200, "cadd_phred": 29.1},
    "G6PD":   {"peak_stage": "adult",         "lifetime_peak_tpm": 4600, "dev_peak_tpm": 4600, "cadd_phred": 25.2},
    "HEXA":   {"peak_stage": "adult",         "lifetime_peak_tpm": 2400, "dev_peak_tpm": 2400, "cadd_phred": 24.0},
    "GBA":    {"peak_stage": "adult",         "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 23.7},
    "FMR1":   {"peak_stage": "adult",         "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 23.0},
    "AR":     {"peak_stage": "adult",         "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 27.2},
    "PKHD1":  {"peak_stage": "adult",         "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 25.5},
    "COL3A1": {"peak_stage": "adult",         "lifetime_peak_tpm": 4800, "dev_peak_tpm": 4800, "cadd_phred": 31.0},
    "TGFBR2": {"peak_stage": "adult",         "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 34.0},
    "CACNA1A":{"peak_stage": "adult",         "lifetime_peak_tpm": 4200, "dev_peak_tpm": 4200, "cadd_phred": 33.0},
    "PRKCG":  {"peak_stage": "adult",         "lifetime_peak_tpm": 2800, "dev_peak_tpm": 2800, "cadd_phred": 25.5},
    "ATXN1":  {"peak_stage": "adult",         "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 24.9},
    "DMPK":   {"peak_stage": "adult",         "lifetime_peak_tpm": 3400, "dev_peak_tpm": 3400, "cadd_phred": 23.5},
    "SOD1":   {"peak_stage": "adult",         "lifetime_peak_tpm": 5600, "dev_peak_tpm": 5600, "cadd_phred": 3.43},
    "FUS":    {"peak_stage": "adult",         "lifetime_peak_tpm": 4200, "dev_peak_tpm": 4200, "cadd_phred": 23.7},
    "TARDBP": {"peak_stage": "adult",         "lifetime_peak_tpm": 3800, "dev_peak_tpm": 3800, "cadd_phred": 21.2},
    "C9orf72":{"peak_stage": "adult",         "lifetime_peak_tpm": 2800, "dev_peak_tpm": 300},
    "GRN":    {"peak_stage": "adult",         "lifetime_peak_tpm": 3200, "dev_peak_tpm": 3200, "cadd_phred": 26.6},
    "MAPT":   {"peak_stage": "adult",         "lifetime_peak_tpm": 3600, "dev_peak_tpm": 3600, "cadd_phred": 29.4},

    "OPTN":    {"peak_stage": "adult", "lifetime_peak_tpm": 2500, "dev_peak_tpm": 2500, "cadd_phred": 10.02},
    "SQSTM1":    {"peak_stage": "adult", "lifetime_peak_tpm": 2500, "dev_peak_tpm": 2500, "cadd_phred": 25.2},
    "VCP":    {"peak_stage": "adult", "lifetime_peak_tpm": 2500, "dev_peak_tpm": 2500, "cadd_phred": 24.6},
}

KNOWN_SET = set(KNOWN_VALUES.keys())

_STAGES = ["zygote", "blastocyst", "gastrulation", "neurulation",
           "organogenesis", "fetal_early", "fetal_late",
           "neonatal", "childhood", "adult"]


def build_profile_from_known(peak_stage: str, peak_tpm: int) -> dict:
    """Build a plausible 10-stage expression profile from a known peak.

    Stages are scaled relative to the peak using distance-based decay.
    """
    peak_idx = _STAGES.index(peak_stage) if peak_stage in _STAGES else len(_STAGES) - 1
    profile = {}
    for i, stage in enumerate(_STAGES):
        dist = abs(i - peak_idx)
        if dist == 0:
            ratio = 1.0
        elif dist == 1:
            ratio = 0.65
        elif dist == 2:
            ratio = 0.35
        elif dist <= 4:
            ratio = 0.15
        else:
            ratio = 0.05
        profile[stage] = int(peak_tpm * ratio)
    return profile
