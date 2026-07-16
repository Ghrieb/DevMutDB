"""
Curated demo dataset for key genes.

NOTE on CADD version: All CADD PHRED scores in this file are from
CADD v1.3 (GRCh37), pre-fetched from the CADD web server.  These may
differ from CADD v1.6 (GRCh38) values returned by the live CADD API.
See the Methods section for the full version rationale.

Provides realistic, pre-calculated data so the platform can demonstrate
DevScore without depending on external APIs. Values are scientifically
plausible and internally consistent with the DevScore formula.
"""

from typing import Optional, Dict, Any


# ---------- expression profiles (TPM per developmental stage) ----------
# Generated from known_values.py via build_profile_from_known() so that
# demo and live API paths produce identical E_peak values.

from .devscore.known_values import KNOWN_VALUES, build_profile_from_known

_SOX2_EXPRESSION = build_profile_from_known("gastrulation",  5800)
_PAX6_EXPRESSION = build_profile_from_known("neurulation",   4200)
_BRCA1_EXPRESSION = build_profile_from_known("adult",         2741)
_SHH_EXPRESSION = build_profile_from_known("gastrulation",   4200)
_TP53_EXPRESSION = build_profile_from_known("adult",          4600)
_FOXP2_EXPRESSION = build_profile_from_known("organogenesis", 3400)
_ANKRD11_EXPRESSION = build_profile_from_known("organogenesis", 3600)


# ---------- gene metadata + default variants ----------

DEMO_GENES: Dict[str, Dict[str, Any]] = {
    "SOX2": {
        "chromosome": "3q26.33",
        "full_name": "SRY-box transcription factor 2",
        "description": "HMG-box transcription factor",
        "ensembl_id": "ENSG00000181449",
        "uniprot_id": "P48431",
        "clinvar_id": "VCV000018107",
        "gnomad_id": "SOX2:c.70C>T",
        "variants": {
            "c.70C>T": {
                "protein_change": "p.Arg24Cys",
                "cadd_phred": 34.0,
                "clinvar_classification": "Pathogenic",
                "sift_score": 0.0,
                "polyphen_score": 0.999,
                "domain_class": "DNA_BINDING",
                "gnomad_af": 0.0,
                "expression": _SOX2_EXPRESSION,
            },
        },
    },
    "PAX6": {
        "chromosome": "11p13",
        "full_name": "Paired box protein Pax-6",
        "description": "Transcription factor for eye and brain development",
        "ensembl_id": "ENSG00000007372",
        "uniprot_id": "P26367",
        "clinvar_id": "VCV000011971",
        "gnomad_id": "PAX6:c.718C>T",
        "variants": {
            "c.718C>T": {
                "protein_change": "p.Arg240Ter",
                "cadd_phred": 32.0,
                "clinvar_classification": "Pathogenic",
                "sift_score": 0.0,
                "polyphen_score": 0.998,
                "domain_class": "DNA_BINDING",
                "gnomad_af": 0.0,
                "expression": _PAX6_EXPRESSION,
            },
        },
    },
    "BRCA1": {
        "chromosome": "17q21.31",
        "full_name": "BRCA1 DNA repair associated",
        "description": "Tumor suppressor involved in DNA repair",
        "ensembl_id": "ENSG00000012048",
        "uniprot_id": "P38398",
        "clinvar_id": "VCV000017661",
        "gnomad_id": "rs80357906",
        "variants": {
            "c.5266dupC": {
                "protein_change": "p.Gln1756ProfsTer74",
                "cadd_phred": 36.0,
                "clinvar_classification": "Pathogenic",
                "sift_score": None,
                "polyphen_score": None,
                "domain_class": "DNA_BINDING",
                "gnomad_af": 0.0006,
                "expression": _BRCA1_EXPRESSION,
            },
        },
    },
    "SHH": {
        "chromosome": "7q36.3",
        "full_name": "Sonic hedgehog signaling molecule",
        "description": "Key morphogen in embryonic patterning",
        "ensembl_id": "ENSG00000164690",
        "uniprot_id": "Q15465",
        "clinvar_id": "VCV000004088",
        "gnomad_id": "SHH:c.347G>A",
        "variants": {
            "c.347G>A": {
                "protein_change": "p.Gly116Asp",
                "cadd_phred": 28.0,
                "clinvar_classification": "Pathogenic",
                "sift_score": 0.001,
                "polyphen_score": 0.995,
                "domain_class": "CATALYTIC",
                "gnomad_af": 0.0,
                "expression": _SHH_EXPRESSION,
            },
        },
    },
    "TP53": {
        "chromosome": "17p13.1",
        "full_name": "Tumor protein p53",
        "description": "Guardian of the genome — tumor suppressor",
        "ensembl_id": "ENSG00000141510",
        "uniprot_id": "P04637",
        "clinvar_id": "VCV000012356",
        "gnomad_id": "TP53:c.742C>T",
        "variants": {
            "c.742C>T": {
                "protein_change": "p.Arg248Trp",
                "cadd_phred": 30.0,
                "clinvar_classification": "Likely pathogenic",
                "sift_score": 0.0,
                "polyphen_score": 0.999,
                "domain_class": "DNA_BINDING",
                "gnomad_af": 0.00001,
                "expression": _TP53_EXPRESSION,
            },
        },
    },
    "ANKRD11": {
        "chromosome": "16q24.3",
        "full_name": "Ankyrin repeat domain-containing protein 11",
        "description": "Transcriptional regulator with ankyrin repeats; KBG syndrome",
        "ensembl_id": "ENSG00000165684",
        "uniprot_id": "Q6RW13",
        "clinvar_id": "VCV000126653",
        "gnomad_id": "ANKRD11:c.1903C>T",
        "variants": {
            "c.1903C>T": {
                "protein_change": "p.Arg635Ter",
                "cadd_phred": 36.0,
                "clinvar_classification": "Pathogenic",
                "sift_score": None,
                "polyphen_score": None,
                "domain_class": "REGULATORY",
                "gnomad_af": 0.0,
                "expression": _ANKRD11_EXPRESSION,
            },
        },
    },
    "FOXP2": {
        "chromosome": "7q31.1",
        "full_name": "Forkhead box protein P2",
        "description": "Transcription factor involved in speech and language",
        "ensembl_id": "ENSG00000128573",
        "uniprot_id": "O15409",
        "clinvar_id": "VCV000004263",
        "gnomad_id": "FOXP2:c.1553G>A",
        "variants": {
            "c.1553G>A": {
                "protein_change": "p.Arg518His",
                "cadd_phred": 26.0,
                "clinvar_classification": "Pathogenic",
                "sift_score": 0.002,
                "polyphen_score": 0.987,
                "domain_class": "DNA_BINDING",
                "gnomad_af": 0.0,
                "expression": _FOXP2_EXPRESSION,
            },
        },
    },
}


def get_demo_data(gene: str, hgvs: str) -> Optional[Dict[str, Any]]:
    """
    Look up curated demo data for a gene + variant pair.

    Returns a dict ready for the DevScore engine, or None if the
    gene/variant is not in the demo dataset.
    """
    gene_upper = gene.upper()
    gene_data = DEMO_GENES.get(gene_upper)
    if not gene_data:
        return None

    variant_data = gene_data["variants"].get(hgvs)
    if not variant_data:
        return None

    return {
        "gene": gene_upper,
        "variant": hgvs,
        "gene_info": {
            "chromosome": gene_data["chromosome"],
            "full_name": gene_data["full_name"],
            "description": gene_data["description"],
            "ensembl_id": gene_data["ensembl_id"],
            "uniprot_id": gene_data["uniprot_id"],
            "clinvar_id": gene_data["clinvar_id"],
            "gnomad_id": gene_data["gnomad_id"],
        },
        "vep": {
            "cadd_phred": variant_data["cadd_phred"],
            "most_severe_consequence": "missense_variant",
            "sift_score": variant_data["sift_score"],
            "polyphen_score": variant_data["polyphen_score"],
            "protein_change": variant_data["protein_change"],
        },
        "clinvar": {
            "classification": variant_data["clinvar_classification"],
        },
        "expression": variant_data["expression"],
        "domains": {
            "domain_class": variant_data["domain_class"],
        },
        "gnomad": {
            "allele_frequency": variant_data["gnomad_af"],
        },
        "source": "demo_curated",
    }
