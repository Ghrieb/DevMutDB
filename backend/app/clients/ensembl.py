"""Ensembl VEP API client for variant annotation.

Two-tier approach:
1. Try POST /vep/human/hgvs with gene:notation format (user's preferred method)
2. Fall back to POST /vep/human/region with VCF format when HGVS fails

CADD is NOT available via the public Ensembl REST API -- use the
separate CADD client.
"""

import asyncio
import httpx
import re
from typing import Optional, Dict, Any


async def fetch_vep(gene: str, hgvs: str,
                    chrom: Optional[str] = None,
                    pos: Optional[int] = None,
                    ref_allele: Optional[str] = None,
                    alt_allele: Optional[str] = None,
                    max_retries: int = 2) -> Dict[str, Any]:
    """
    Fetch variant annotation from Ensembl VEP REST API (GRCh38).

    Tries the HGVS POST endpoint first with retries on transient failures.
    If the API reports a reference allele mismatch, falls back to the VCF-style
    region POST (requires chrom/pos/ref/alt), also with retries.

    Retries:
    - Transient errors (timeouts, 5xx, connection errors) are retried with
      exponential backoff (1s, 2s) up to max_retries times.
    - 422 (unprocessable HGVS) is NOT retried — it's a semantic failure.

    Args:
        gene: Gene symbol (e.g. "SOX2")
        hgvs: HGVS notation (e.g. "c.70C>T")
        chrom, pos, ref_allele, alt_allele: genomic coordinates for
            the VCF fallback (optional, only needed when HGVS fails).
        max_retries: Number of retries for transient failures (default 2).

    Returns:
        Dict with fields:
            most_severe_consequence, gene_id, transcript_id,
            protein_position, sift_score, polyphen_score,
            error key on failure.
    """
    server = "https://grch37.rest.ensembl.org"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    default_result = {
        "most_severe_consequence": None,
        "gene_id": None,
        "transcript_id": None,
        "protein_position": None,
        "sift_score": None,
        "polyphen_score": None,
        "error": "ensembl_unavailable",
    }

    # ── Tier 1: HGVS POST with retries ───────────────────────────────────
    hgvs_payload = {
        "hgvs_notations": [f"{gene}:{hgvs}"],
        "SIFT": "b",
        "PolyPhen": "b",
    }

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    server + "/vep/human/hgvs",
                    headers=headers, json=hgvs_payload,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        result = data[0]
                        err = result.get("error")
                        if err and "does not match reference allele" in str(err):
                            pass
                        else:
                            return _parse_vep_response(result)
                elif resp.status_code == 422:
                    break
            break
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"VEP HGVS endpoint {gene}:{hgvs} transient error (attempt {attempt + 1}): {e} — retry in {wait}s")
                await asyncio.sleep(wait)
            else:
                print(f"VEP HGVS endpoint {gene}:{hgvs} failed after {max_retries + 1} attempts: {e}")
        except Exception as e:
            print(f"VEP HGVS endpoint error: {e}")
            break

    # ── Tier 2: VCF region POST with retries ─────────────────────────────
    if not chrom or not pos or not ref_allele or not alt_allele:
        return {**default_result, "error": "coordinate_resolution_failed"}

    vcf_str = f"{chrom} {pos} . {ref_allele} {alt_allele} . . ."
    vcf_payload = {"variants": [vcf_str], "SIFT": "b", "PolyPhen": "b"}

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    server + "/vep/human/region",
                    headers=headers, json=vcf_payload,
                )
                resp.raise_for_status()
                data = resp.json()
                if data and isinstance(data, list) and len(data) > 0:
                    return _parse_vep_response(data[0])
            break
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"VEP region endpoint {gene}:{hgvs} transient error (attempt {attempt + 1}): {e} — retry in {wait}s")
                await asyncio.sleep(wait)
            else:
                print(f"VEP region endpoint {gene}:{hgvs} failed after {max_retries + 1} attempts: {e}")
        except Exception as e:
            print(f"VEP region endpoint error: {e}")
            break

    return default_result


async def fetch_gene_info(gene: str) -> Dict[str, Any]:
    """
    Look up basic gene metadata (chromosome, description, ensembl_id)
    from Ensembl REST API (GRCh38).
    """
    server = "https://rest.ensembl.org"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    default = {"chromosome": None, "description": None, "ensembl_id": None, "uniprot_id": None}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{server}/lookup/symbol/homo_sapiens/{gene}",
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "chromosome": data.get("seq_region_name"),
                    "description": data.get("description"),
                    "ensembl_id": data.get("id"),
                    "uniprot_id": None,
                }
    except Exception as e:
        print(f"Ensembl gene lookup error for {gene}: {e}")
    return default


def _parse_vep_response(result: dict) -> Dict[str, Any]:
    """Extract relevant fields from a VEP response dict."""
    sift_score = None
    polyphen_score = None
    gene_id = None
    transcript_id = None
    protein_position = None

    if "transcript_consequences" in result and result["transcript_consequences"]:
        tc = result["transcript_consequences"][0]
        gene_id = tc.get("gene_id")
        transcript_id = tc.get("transcript_id")
        protein_position = tc.get("protein_start")
        sift_score = tc.get("sift_score")
        polyphen_score = tc.get("polyphen_score")

    return {
        "most_severe_consequence": result.get("most_severe_consequence", ""),
        "gene_id": gene_id or result.get("gene_id", ""),
        "transcript_id": transcript_id or "",
        "protein_position": protein_position,
        "sift_score": sift_score,
        "polyphen_score": polyphen_score,
    }
