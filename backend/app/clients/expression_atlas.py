"""Expression Atlas API client.

Returns expression profiles from the KNOWN_VALUES table where available,
falling back to the Expression Atlas REST API, then to class-aware
benchmark profiles for unlisted genes.
"""

import httpx
from typing import Dict, Any

from ..config import API_TIMEOUT
from ..devscore.benchmark_genes import make_expression_profile
from ..devscore.known_values import KNOWN_VALUES, KNOWN_SET, build_profile_from_known

# The 10 developmental stages used by DevScore (aligned with E-MTAB-6814)
DEV_STAGES = [
    "zygote", "blastocyst", "gastrulation", "neurulation",
    "organogenesis", "fetal_early", "fetal_late",
    "neonatal", "childhood", "adult",
]

# Map Expression Atlas condition labels to DevScore stage names
ATLAS_STAGE_MAP = {
    "zygote": "zygote", "oocyte": "zygote", "1-cell stage": "zygote",
    "blastocyst": "blastocyst",
    "gastrula": "gastrulation", "gastrulation": "gastrulation",
    "neurula": "neurulation", "neurulation": "neurulation",
    "organogenesis": "organogenesis", "organogenesis stage": "organogenesis",
    "fetal early": "fetal_early", "early fetal": "fetal_early",
    "fetal late": "fetal_late", "late fetal": "fetal_late",
    "neonatal": "neonatal", "newborn": "neonatal",
    "childhood": "childhood", "infant": "childhood",
    "adult": "adult",
}


def _map_expression_atlas_response(data: dict) -> Dict[str, Any] | None:
    """Parse Expression Atlas heatmap JSON into a DevScore expression profile."""
    rows = data.get("rows") or data.get("results")
    if not rows:
        return None
    for row in rows:
        gene_name = (row.get("geneName") or row.get("gene") or "").upper()
        expressions = row.get("expressions") or row.get("expressionLevels") or []
        if not expressions:
            continue
        profile = {}
        for exp in expressions:
            condition = (exp.get("condition") or exp.get("experimentalFactorValue") or "").strip().lower()
            value = exp.get("value") or exp.get("expressionLevel") or exp.get("tpm")
            if condition and value is not None:
                stage = None
                for key, mapped in ATLAS_STAGE_MAP.items():
                    if key in condition:
                        stage = mapped
                        break
                if stage:
                    profile[stage] = profile.get(stage, 0) + float(value)
        if not profile:
            continue
        return {
            "data": profile,
            "source": "expression_atlas_api",
            "peak_stage": max(profile, key=profile.get),
            "peak_tpm": max(profile.values()),
        }
    return None


async def fetch_expression(gene: str) -> Dict[str, Any]:
    """
    Fetch developmental gene expression data.

    Priority:
    1. KNOWN_VALUES table (curated from Expression Atlas) — source="known"
    2. Expression Atlas REST API — source="expression_atlas_api"
    3. Class-aware benchmark fallback — source="estimated"
    """
    if gene in KNOWN_SET:
        kv = KNOWN_VALUES[gene]
        peak_stage = kv["peak_stage"]
        peak_tpm = kv["dev_peak_tpm"]
        profile = build_profile_from_known(peak_stage, peak_tpm)
        return {
            "data": profile,
            "source": "known",
            "peak_stage": peak_stage,
            "peak_tpm": peak_tpm,
        }

    # Try live Expression Atlas API
    try:
        url = f"https://www.ebi.ac.uk/gxa/api/v2/experiments/E-MTAB-6814/heatmap?genes={gene}"
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            resp = await client.get(url, headers={"Accept": "application/json"})
        if resp.status_code == 200:
            parsed = _map_expression_atlas_response(resp.json())
            if parsed:
                return parsed
    except Exception:
        pass

    # Fall back to estimated profile
    profile = make_expression_profile(gene)
    return {
        "data": profile,
        "source": "estimated",
    }
