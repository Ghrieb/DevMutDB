"""Pydantic data models for DevMutDB API requests/responses."""

import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any


# Valid HGVS patterns for server-side validation
HGVS_PATTERNS = [
    re.compile(r'^c\.\d+[ACGT]>[ACGT]$'),              # c.70C>T
    re.compile(r'^c\.\d+_\d+[ACGT]>[ACGT]$'),          # c.70_71CA>TG
    re.compile(r'^c\.\d+del$'),                       # c.112del
    re.compile(r'^c\.\d+_\d+del$'),                   # c.68_69del
    re.compile(r'^c\.\d+dup$'),                       # c.5266dupC
    re.compile(r'^c\.\d+_\d+dup$'),                   # c.1274_1277dup
    re.compile(r'^c\.\d+del[ACGTacgt]+$'),              # c.35delG
    re.compile(r'^c\.\d+_\d+del[ACGTacgt]+$'),          # c.301_302delAG
    re.compile(r'^c\.\d+dup[ACGTacgt]+$'),              # c.5266dupC
    re.compile(r'^c\.\d+_\d+ins[ACGTacgt]+$'),         # c.123_124insAGC
    re.compile(r'^c\.\d+_\d+delins[ACGTacgt]+$'),       # c.123_125delinsAGC
    re.compile(r'^c\.\d+[-+]\d+[ACGT]>[ACGT]$'),       # c.1620+1G>A
    re.compile(r'^c\.\*\d+[ACGT]>[ACGT]$'),            # c.*123A>G
    re.compile(r'^c\.-\d+[ACGT]>[ACGT]$'),             # c.-123A>G
    re.compile(r'^p\.\w+\d+\w+$'),                    # p.Gly12Val
    re.compile(r'^p\.\w+\d+\*$'),                     # p.Gly12*
    re.compile(r'^p\.\w+\d+\w+fs\*?\d*$'),           # p.Gly12Valfs*5
    re.compile(r'^n\.\d+[ACGT]>[ACGT]$'),              # n.123A>G
    re.compile(r'^g\.\d+[ACGT]>[ACGT]$'),              # g.123456A>G
    re.compile(r'^g\.\d+_\d+del$'),                   # g.123456_123789del
]


class ScoreRequest(BaseModel):
    """Request model for variant scoring."""
    gene: str = Field(..., description="Gene name or Ensembl ID")
    hgvs: str = Field(..., description="HGVS variant notation (e.g., c.70C>T)")
    position: Optional[int] = Field(None, description="Genomic position")

    @field_validator('hgvs')
    @classmethod
    def validate_hgvs(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('HGVS notation cannot be empty')
        trimmed = v.strip()
        # ── Gatekeeper: reject strings that cannot be HGVS at all ──
        if not re.match(r'^[cngp]\.\w', trimmed) and not re.match(r'^\d+[ACGT]>', trimmed):
            raise ValueError(
                'HGVS notation must start with c., p., n., or g. prefix — '
                'e.g., "c.70C>T"'
            )
        # Check for common mistakes
        if '/' in trimmed and '>' not in trimmed:
            raise ValueError('Use ">" not "/" for substitutions — e.g., "c.70C>T"')
        if re.match(r'^\d+[ACGT]>[ACGT]$', trimmed):
            raise ValueError('Missing "c." prefix — use "c.70C>T" format')
        if re.match(r'^[a-z]\.[a-z]', trimmed) and not re.match(r'^[cngp]\.', trimmed):
            raise ValueError('Invalid HGVS prefix — use "c.", "p.", "n.", or "g."')
        # Check against valid patterns
        if not any(p.match(trimmed) for p in HGVS_PATTERNS):
            raise ValueError(
                'Invalid HGVS notation. Expected formats: c.70C>T, c.112del, '
                'c.68_69del, c.5266dupC, p.Gly12Val, p.Gly12Valfs*5, n.123A>G'
            )
        return trimmed


class VEPResult(BaseModel):
    """Variant Effect Prediction result."""
    cadd_phred: float
    most_severe_consequence: Optional[str]
    gene_id: Optional[str]
    transcript_id: Optional[str]
    protein_position: Optional[int]
    sift_score: Optional[float]
    polyphen_score: Optional[float]


class ClinVarResult(BaseModel):
    """ClinVar variant classification."""
    classification: str
    review_status: Optional[str]


class ExpressionResult(BaseModel):
    """Gene expression data."""
    data: Dict[str, float]  # stage -> TPM


class DevScoreResponse(BaseModel):
    """Response model for scoring endpoint."""
    gene: str
    variant: str
    score: float
    V: float
    E_peak: float
    C_stage: float
    D_domain: float
    peak_stage: str
    interpretation: str
    ai_interpretation: bool = False
    data_warnings: Optional[List[str]] = None
