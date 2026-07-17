# SPDX-FileCopyrightText: 2025 Abdelkarim Hani Ghrieb
# SPDX-License-Identifier: LicenseRef-Proprietary

"""DevScore engine - core formula implementation."""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
try:
    import google.generativeai as genai
except Exception:
    genai = None  # Fallback if the package is unavailable
from .stage_index import STAGE_CRITICALITY
from .domain_weights import DOMAIN_WEIGHTS, CLINVAR_WEIGHTS

# Configure Gemini
# In production, ensure GEMINI_API_KEY is in your environment
if os.getenv("GEMINI_API_KEY") and genai is not None:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@dataclass
class DevScoreResult:
    """Result of DevScore calculation."""
    gene: str
    variant: str
    V: float
    E_peak: float
    C_stage: float
    D_domain: float
    score: float
    peak_stage: str
    interpretation: str
    component_explanation: Dict[str, Any]
    ai_interpretation: bool = False


def interpret(score: float, stage: str, criticality: float, gene: str, variant: str) -> tuple[str, bool]:
    """Interpret the calculated DevScore using Gemini if available.
    Returns (interpretation_text, was_ai_generated)."""
    
    # Generic fallback if no API key or if LLM fails
    fallback_interp = ""
    if score >= 80:
        fallback_interp = f"Critical developmental impact. Peak expression during {stage} (criticality {criticality}) means perturbation is likely irreversible."
    elif score >= 50:
        fallback_interp = f"Moderate developmental impact. Expression during {stage} warrants functional follow-up."
    else:
        fallback_interp = f"Limited developmental impact. Low expression or adult-stage timing reduces embryonic relevance."

    if not os.getenv("GEMINI_API_KEY") or genai is None:
        return fallback_interp, False

    prompt = f"""
    You are an expert clinical geneticist specializing in developmental disorders.
    Interpret the following variant using the novel 'DevScore' metric (0-100 scale).
    
    Gene: {gene}
    Variant: {variant}
    DevScore: {score}/100
    Peak Developmental Expression Stage: {stage} (Criticality Weight: {criticality})
    
    Write a single, concise, professional paragraph (3-4 sentences maximum) explaining the developmental impact of this variant. Focus on the timing of expression and how early perturbation (if high criticality) might lead to congenital phenotypes. Do not use markdown or bullet points.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip(), True
    except Exception as e:
        print(f"Gemini API error: {e}")
        return fallback_interp, False


def map_position_to_domain(domains_data: dict, variant_position: int) -> str:
    """
    Map the variant position to a specific protein domain.
    If position-specific data isn't available, returns the overall domain_class.

    TODO: variant_position is reserved for future position-aware domain mapping
    (e.g., checking whether the variant falls within a specific Pfam/InterPro
    domain boundary rather than using the gene-level domain class).
    """
    return domains_data.get("domain_class", "REGULATORY")


def calculate_devscore(raw_data: dict, variant_position: int = 0) -> DevScoreResult:
    """
    Calculate DevScore for a genetic variant.
    
    The DevScore formula: DevScore = V × E_peak × C_stage × D_domain × 100
    """
    
    # V: Pathogenicity component
    vep_data = raw_data.get("vep", {})
    cadd_phred = vep_data.get("cadd_phred")
    if cadd_phred is None:
        cadd_norm = 0.0  # No CADD data — exclude from V component
    else:
        cadd_norm = min(float(cadd_phred) / 40.0, 1.0)
    
    clinvar_data = raw_data.get("clinvar", {})
    clinvar_classification = clinvar_data.get("classification", "Uncertain significance")
    clinvar_w = CLINVAR_WEIGHTS.get(clinvar_classification, 0.5)
    
    V = max(0.0, min(1.0, (cadd_norm * 0.6) + (clinvar_w * 0.4)))
    
    # E_peak: Expression intensity
    TPM_99TH_PERCENTILE = 10000
    expression_data = raw_data.get("expression", {})
    gene = raw_data.get("gene", "unknown")
    
    if expression_data:
        peak_stage = max(expression_data.items(), key=lambda x: x[1])[0]
        peak_tpm = expression_data[peak_stage]
    else:
        peak_stage = "unknown"
        peak_tpm = 0

    E_peak = min(peak_tpm / TPM_99TH_PERCENTILE, 1.0) if peak_tpm > 0 else 0.1
    
    # C_stage: Developmental stage criticality
    C_stage = STAGE_CRITICALITY.get(peak_stage, 0.25)
    
    # D_domain: Protein domain weight
    domains_data = raw_data.get("domains", {})
    domain_class = map_position_to_domain(domains_data, variant_position)
    D_domain = DOMAIN_WEIGHTS.get(domain_class, 0.4)
    
    # Final score
    score = round(max(0.0, min(100.0, V * E_peak * C_stage * D_domain * 100)), 1)
    
    gene = raw_data.get("gene", "unknown")
    variant = raw_data.get("variant", "unknown")
    
    # Interpretation via AI
    interpretation, ai_interpretation = interpret(score, peak_stage, C_stage, gene, variant)
    
    component_explanation = {
        "V_pathogenicity": {
            "cadd_phred": cadd_phred,
            "cadd_normalized": round(cadd_norm, 3),
            "clinvar_classification": clinvar_classification,
            "clinvar_weight": clinvar_w,
            "V_final": round(V, 3)
        },
        "E_peak_expression": {
            "peak_stage": peak_stage,
            "peak_tpm": peak_tpm,
            "tpm_99th_percentile": TPM_99TH_PERCENTILE,
            "E_peak": round(E_peak, 3)
        },
        "C_stage_criticality": {
            "stage": peak_stage,
            "criticality": C_stage
        },
        "D_domain_weight": {
            "domain_class": domain_class,
            "weight": D_domain
        }
    }
    
    return DevScoreResult(
        gene=gene,
        variant=variant,
        V=round(V, 3),
        E_peak=round(E_peak, 3),
        C_stage=C_stage,
        D_domain=D_domain,
        score=score,
        peak_stage=peak_stage,
        interpretation=interpretation,
        ai_interpretation=ai_interpretation,
        component_explanation=component_explanation
    )
