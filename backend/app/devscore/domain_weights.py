"""Domain weight constants from UniProt for DevScore calculation.

Each weight represents the essentiality of the protein domain type at the variant's position.
These reflect UniProt domain classifications specific to variant impact on protein structure/function:
- DNA_BINDING (transcription factors, DNA-binding domains) = 1.00
- CATALYTIC (enzyme active sites) = 1.00
- STRUCTURAL (protein scaffolds, folding) = 0.70
- REGULATORY (transcriptional/translational control) = 0.50
- DISORDERED (intrinsic disorder regions) = 0.40
- UTR (3' UTR/mRNA regulatory) = 0.20

Source: Based on UniProt domain essentiality scores used in missense variant impact prediction.
"""

DOMAIN_WEIGHTS = {
    "DNA_BINDING": 1.0,
    "CATALYTIC": 1.0,
    "STRUCTURAL": 0.7,
    "REGULATORY": 0.5,
    "DISORDERED": 0.4,
    "UTR": 0.2,
}

CLINVAR_WEIGHTS = {
    "Pathogenic": 1.0,
    "Likely pathogenic": 0.75,
    "Uncertain significance": 0.5,
    "Likely benign": 0.2,
    "Benign": 0.0,
}

__all__ = ["DOMAIN_WEIGHTS", "CLINVAR_WEIGHTS"]
