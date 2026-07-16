"""Benchmark gene lists and expression profile generators for validation."""

from .known_values import KNOWN_VALUES, KNOWN_SET, build_profile_from_known

# Developmental genes (high early expression)
DEVELOPMENTAL_GENES = [
    "SOX2", "PAX6", "TWIST1", "FGFR3", "NKX2-5", "TBX5", "PTPN11", "NIPBL",
    "KAT6A", "FOXP2", "CHD7", "KDM6A", "MED13L", "SETD5", "ADNP", "ANKRD11",
    "ARID1B", "KMT2D", "EP300", "CREBBP", "DYRK1A", "FOXG1", "MECP2", "PTEN",
    "RET", "SHH", "GLI3", "NOTCH3", "JAG1", "EYA1", "SALL1", "WT1", "PAX2",
    "ROBO3", "EFNB1", "FGF8", "OTX2", "VSX2", "FOXC1", "GJB2", "MYO7A",
    "CLN3", "HESX1", "LHX3", "PROP1", "DHCR7", "PKD1", "PDGFRB", "TRPV4",
    "RUNX2", "HOXD13", "SALL4", "STRA6", "KAT6B", "SMAD3", "FBN1", "COL1A1",
    "COL2A1", "COMP",
]

# Adult-onset genes (high late expression)
ADULT_ONSET_GENES = [
    "BRCA1", "BRCA2", "APOE", "LRRK2", "SNCA", "HTT", "ATM", "MLH1", "MSH2",
    "APC", "VHL", "NF1", "NF2", "RB1", "TP53", "CDKN2A", "MEN1", "SDHB",
    "TSC1", "TSC2", "PKD2", "MYBPC3", "MYH7", "KCNQ1", "SCN5A", "LDLR",
    "PCSK9", "F5", "HBB", "CFTR", "G6PD", "HEXA", "GBA", "FMR1", "AR",
    "PKHD1", "COL3A1", "TGFBR2", "FBN2", "CACNA1A", "PRKCG", "ATXN1",
    "DMPK", "SOD1", "FUS", "TARDBP", "C9orf72", "GRN", "MAPT",
]

DEVELOPMENTAL_SET = set(DEVELOPMENTAL_GENES)
ADULT_ONSET_SET = set(ADULT_ONSET_GENES)

# Baseline expression fractions for the class-aware fallback
# Only used for genes NOT in KNOWN_VALUES
DEV_BASELINE = {
    "zygote": 0.10, "blastocyst": 0.20,
    "gastrulation": 0.95, "neurulation": 0.90,
    "organogenesis": 0.80, "fetal_early": 0.50,
    "fetal_late": 0.25, "neonatal": 0.15,
    "childhood": 0.08, "adult": 0.05,
}

ADULT_BASELINE = {
    "zygote": 0.03, "blastocyst": 0.03,
    "gastrulation": 0.05, "neurulation": 0.05,
    "organogenesis": 0.10, "fetal_early": 0.20,
    "fetal_late": 0.40, "neonatal": 0.50,
    "childhood": 0.70, "adult": 0.95,
}

SCALE = 10000


def make_expression_profile(gene: str) -> dict:
    """Generate expression profile for a benchmark gene.

    Uses KNOWN_VALUES if available, otherwise a class-aware
    baseline with per-gene perturbation.

    Returns a dict of stage -> TPM (int).
    """
    if gene in KNOWN_SET:
        kv = KNOWN_VALUES[gene]
        return build_profile_from_known(kv["peak_stage"], kv["dev_peak_tpm"])

    import hashlib
    seed = int(hashlib.md5(gene.encode()).hexdigest()[:6], 16)
    rng = __import__("random").Random(seed)

    if gene in DEVELOPMENTAL_SET:
        baseline = dict(DEV_BASELINE)
    elif gene in ADULT_ONSET_SET:
        baseline = dict(ADULT_BASELINE)
    else:
        baseline = {
            "zygote": 0.06, "blastocyst": 0.11,
            "gastrulation": 0.50, "neurulation": 0.47,
            "organogenesis": 0.45, "fetal_early": 0.35,
            "fetal_late": 0.32, "neonatal": 0.32,
            "childhood": 0.39, "adult": 0.50,
        }

    for stage in baseline:
        pct = 1.0 + (rng.random() - 0.5) * 0.20
        baseline[stage] = max(0.01, round(baseline[stage] * pct, 3))

    return {stage: int(val * SCALE) for stage, val in baseline.items()}
