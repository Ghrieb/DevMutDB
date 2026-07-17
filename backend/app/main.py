# SPDX-FileCopyrightText: 2025 Abdelkarim Hani Ghrieb
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from fastapi.responses import JSONResponse, FileResponse
import asyncio
import httpx
import re
import os
from typing import Dict, Any, List, Optional, Tuple

from .devscore.models import ScoreRequest, DevScoreResponse, HGVS_PATTERNS
from .devscore.engine import calculate_devscore
from .devscore.known_values import KNOWN_VALUES, KNOWN_SET
from .devscore.known_variants import KNOWN_PATHOGENIC_VARIANTS
from .devscore.benchmark_genes import DEVELOPMENTAL_SET, ADULT_ONSET_SET
from .cache import cache
from .demo_data import get_demo_data, DEMO_GENES
from .clients.ensembl import fetch_vep, fetch_gene_info
from .clients.cadd_client import fetch_cadd
from .clients.clinvar import fetch_clinvar
from .clients.gnomad import fetch_gnomad
from .clients.expression_atlas import fetch_expression
from .clients.uniprot import fetch_domains

# Full gene list for autocomplete
KNOWN_GENES = [
    'SOX2', 'PAX6', 'TWIST1', 'FGFR3', 'NKX2-5', 'TBX5', 'PTPN11', 'NIPBL',
    'KAT6A', 'FOXP2', 'CHD7', 'KDM6A', 'MED13L', 'SETD5', 'ADNP', 'ANKRD11',
    'ARID1B', 'KMT2D', 'EP300', 'CREBBP', 'DYRK1A', 'FOXG1', 'MECP2', 'RET',
    'SHH', 'GLI3', 'JAG1', 'EYA1', 'SALL1', 'WT1', 'PAX2', 'OTX2', 'VSX2',
    'FOXC1', 'GJB2', 'MYO7A', 'HESX1', 'LHX3', 'DHCR7', 'PKD1', 'RUNX2',
    'HOXD13', 'SALL4', 'KAT6B', 'FBN1', 'COL1A1', 'COL2A1', 'SMAD3',
    'PDGFRB', 'TRPV4', 'COMP', 'ROBO3', 'EFNB1', 'FGF8', 'PROP1', 'STRA6',
    'CLN3', 'NOTCH3', 'PTEN', 'PDHA1', 'BRCA1', 'BRCA2', 'APOE', 'LRRK2',
    'SNCA', 'ATM', 'MLH1', 'MSH2', 'APC', 'VHL', 'NF1', 'NF2', 'RB1',
    'TP53', 'CDKN2A', 'MEN1', 'SDH', 'TSC1', 'TSC2', 'PKD2', 'MYBPC3',
    'MYH7', 'KCNQ1', 'SCN5A', 'LDLR', 'PCSK9', 'F5', 'HBB', 'CFTR',
    'G6PD', 'GBA', 'AR', 'COL3A1', 'TGFBR2', 'CACNA1A', 'PRKCG', 'DMPK',
    'SOD1', 'FUS', 'TARDBP', 'GRN', 'MAPT', 'FBN2', 'ATXN1',
    'HTT', 'FMR1', 'C9orf72', 'PRNP', 'BMPR2', 'KCNQ4', 'MYO6', 'LMNA',
    'DMD', 'BRIP1', 'PALB2', 'CHEK2', 'RAD51C', 'MUTYH', 'MSH6', 'HEXA',
    'PKHD1', 'SDHB', 'GLA', 'IDUA', 'PAH',
]

# Curated variant suggestions — sourced from known_variants registry
# (ClinVar, literature, and validation-benchmark pathogenic variants)
GENE_VARIANTS = KNOWN_PATHOGENIC_VARIANTS

app = FastAPI(title="DevMutDB", version="0.2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.2.0"}


@app.get("/api/genes")
async def list_demo_genes():
    """List available demo genes with metadata."""
    genes = []
    for gene_name, gene_data in DEMO_GENES.items():
        variants = list(gene_data["variants"].keys())
        genes.append({
            "gene": gene_name,
            "chromosome": gene_data["chromosome"],
            "full_name": gene_data["full_name"],
            "description": gene_data["description"],
            "variants": variants,
        })
    return {"genes": genes}


def _expression_source(gene: str) -> dict:
    """Return expression data source tier for a gene (pure lookup, no API calls)."""
    gene = gene.upper()
    if gene in KNOWN_SET:
        return {"gene": gene, "source": "known", "label": "E-MTAB-6814"}
    if gene in DEVELOPMENTAL_SET:
        return {"gene": gene, "source": "estimated", "label": "Developmental-class estimate"}
    if gene in ADULT_ONSET_SET:
        return {"gene": gene, "source": "estimated", "label": "Adult-onset estimate"}
    return {"gene": gene, "source": "estimated", "label": "General estimate"}


@app.get("/api/genes/autocomplete")
async def autocomplete_genes(q: str = Query("", min_length=1, max_length=50)):
    """Autocomplete gene names based on prefix query."""
    query = q.strip().upper()
    if not query:
        return {"suggestions": []}
    matches = [g for g in KNOWN_GENES if g.startswith(query)]
    matches.sort()
    return {
        "suggestions": [
            {"gene": g, **{k: v for k, v in _expression_source(g).items() if k != "gene"}}
            for g in matches[:10]
        ]
    }


@app.get("/api/genes/{gene_name}/expression-source")
async def gene_expression_source(gene_name: str):
    """Return expression data source tier for a gene (pure lookup, no API calls)."""
    gene = gene_name.strip().upper()
    return _expression_source(gene)


def _generate_plausible_variants(gene: str, count: int = 30) -> List[str]:
    """Generate deterministic plausible HGVS variants for unknown genes."""
    import hashlib
    seed = int(hashlib.md5(gene.encode()).hexdigest()[:8], 16)
    rng = __import__('random').Random(seed)
    bases = ['A', 'C', 'G', 'T']
    variants = []
    positions = rng.sample(range(1, 2001), min(count * 2, 2000))
    for i in range(count):
        pos = positions[i]
        op = rng.choice(['sub', 'del', 'dup', 'splice'])
        if op == 'sub':
            ref = rng.choice(bases)
            alt = rng.choice([b for b in bases if b != ref])
            variants.append(f'c.{pos}{ref}>{alt}')
        elif op == 'del':
            if rng.random() < 0.3:
                end = pos + rng.randint(1, 10)
                variants.append(f'c.{pos}_{end}del')
            else:
                variants.append(f'c.{pos}del')
        elif op == 'dup':
            variants.append(f'c.{pos}dup{rng.choice(bases)}')
        else:
            offset = rng.randint(1, 50)
            vs = rng.choice(['+', '-'])
            ref = rng.choice(bases)
            alt = rng.choice([b for b in bases if b != ref])
            variants.append(f'c.{pos}{vs}{offset}{ref}>{alt}')
    return variants


# ── Coordinate resolution helper ────────────────────────────────────────
_COORDS_CACHE: Dict[str, Optional[Tuple[str, int, int, str, tuple]]] = {}
# Cache key: (chrom, cds_start, cds_end, strand, exons_as_tuple)

_TRANSCRIPT_CACHE: Dict[str, Optional[dict]] = {}
# Transcript-level cache to avoid redundant exon parsing


def _revcomp(seq: str) -> str:
    """Reverse complement of a DNA string."""
    comp = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    return ''.join(comp.get(b.upper(), b) for b in reversed(seq))


async def _resolve_variant_coords(gene: str, hgvs: str) -> Optional[Tuple[str, int, str, str]]:
    """Resolve (chrom, genomic_pos, ref, alt) from gene symbol + HGVS notation.

    Handles SNV, splice-site SNV, deletion, and duplication patterns.
    For indels with empty alt, fetch_cadd returns max-PHRED at the site.

    Iterative Isoform Hunt: tries ALL protein-coding transcripts for the gene
    (sorted longest CDS first) until one accommodates the requested CDS position.
    This prevents false 404s for genes like MAPT and TARDBP that have multiple
    tissue-specific isoforms where the canonical longest transcript may not contain
    the referenced CDS position.

    Returns None if coordinates cannot be resolved.
    """
    raw = hgvs.strip()

    # ── Parse HGVS pattern (priority-ordered) ──────────────────────────
    cds_pos = None
    alt_coding = None
    event_len = 1
    intron_offset = 0

    # (a) Splice SNV: c.123+1G>T or c.456-2A>G
    m = re.match(r'^c\.(\d+)([+-])(\d+)([ACGTN])>([ACGTN])$', raw)
    if m:
        cds_pos = int(m.group(1))
        sign = 1 if m.group(2) == '+' else -1
        intron_offset = sign * int(m.group(3))
        alt_coding = m.group(5)

    # (b) Range deletion: c.123_125del or c.123_125delACT
    if cds_pos is None:
        m = re.match(r'^c\.(\d+)_(\d+)del([ACGTN]*)$', raw)
        if m:
            start = int(m.group(1))
            end = int(m.group(2))
            if start > end:
                start, end = end, start
            cds_pos = start
            event_len = end - start + 1
            alt_coding = ''

    # (c) Single deletion: c.35del or c.35delG
    if cds_pos is None:
        m = re.match(r'^c\.(\d+)del([ACGTN]*)$', raw)
        if m:
            cds_pos = int(m.group(1))
            event_len = len(m.group(2)) if m.group(2) else 1
            alt_coding = ''

    # (d) Range duplication: c.1274_1277dup
    if cds_pos is None:
        m = re.match(r'^c\.(\d+)_(\d+)dup$', raw)
        if m:
            cds_pos = int(m.group(1))
            event_len = int(m.group(2)) - cds_pos + 1
            alt_coding = '__dup__'

    # (e) Single duplication: c.5266dup or c.5266dupC
    if cds_pos is None:
        m = re.match(r'^c\.(\d+)dup([ACGTN]*)$', raw)
        if m:
            cds_pos = int(m.group(1))
            event_len = len(m.group(2)) if m.group(2) else 1
            alt_coding = '__dup__'

    # (f) Standard SNV: c.123A>G
    if cds_pos is None:
        m = re.match(r'^c\.(\d+)([ACGTN])>([ACGTN])$', raw)
        if m:
            cds_pos = int(m.group(1))
            alt_coding = m.group(3)

    if cds_pos is None:
        return None

    # ── Fetch all transcripts for this gene (cached) ────────────────────
    cache_key_txs = f"_transcripts_{gene}"
    if cache_key_txs in _COORDS_CACHE:
        all_transcripts = _COORDS_CACHE[cache_key_txs]
        if all_transcripts is None:
            return None
    else:
        all_transcripts = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=12.0) as client:
                    resp = await client.get(
                        f"https://grch37.rest.ensembl.org/lookup/symbol/homo_sapiens/{gene}?expand=1",
                        headers={"Content-Type": "application/json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    raw_txs = data.get("Transcript", [])
                    if not raw_txs:
                        raise HTTPException(status_code=404, detail=f"Gene '{gene}' not found in Ensembl")

                    protein_coding = [
                        tx for tx in raw_txs
                        if tx.get("biotype") == "protein_coding" and tx.get("Translation")
                    ]
                    if not protein_coding:
                        protein_coding = [tx for tx in raw_txs if tx.get("Translation")]
                    if not protein_coding:
                        _COORDS_CACHE[cache_key_txs] = None
                        return None

                    def _cds_len(tx: dict) -> int:
                        tl = tx.get("Translation", {})
                        s, e = tl.get("start"), tl.get("end")
                        return abs(e - s) + 1 if s and e else 0

                    protein_coding.sort(key=_cds_len, reverse=True)
                    all_transcripts = protein_coding
                    _COORDS_CACHE[cache_key_txs] = all_transcripts
                    break

            except httpx.HTTPStatusError as e:
                if 400 <= e.response.status_code < 500:
                    raise HTTPException(status_code=404, detail=f"Gene '{gene}' not found in Ensembl")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise HTTPException(status_code=502, detail=f"Ensembl API error for {gene}: {e}")
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt < 2:
                    print(f"Ensembl connection error for {gene} (attempt {attempt + 1}): {e} — retry")
                    await asyncio.sleep(2 ** attempt)
                    continue
                print(f"Ensembl connection error for {gene} after 3 attempts: {e}")
                _COORDS_CACHE[cache_key_txs] = None
                return None

        if all_transcripts is None:
            _COORDS_CACHE[cache_key_txs] = None
            return None

    # ── Iterative Isoform Hunt ─────────────────────────────────────────
    for tx in all_transcripts:
        chrom = tx.get("seq_region_name")
        strand = tx.get("strand", 1)
        cds_start = tx["Translation"]["start"]
        cds_end = tx["Translation"]["end"]
        if not chrom:
            continue

        raw_exons = tx.get("Exon", []) or tx.get("exon", [])
        exons = sorted(
            [(ex["start"], ex["end"]) for ex in raw_exons if ex.get("start") and ex.get("end")],
            key=lambda x: x[0]
        )

        cds_regions = []
        for ex_start, ex_end in exons:
            ov_start = max(ex_start, cds_start)
            ov_end = min(ex_end, cds_end)
            if ov_start <= ov_end:
                cds_regions.append((ov_start, ov_end, ov_end - ov_start + 1))

        if not cds_regions:
            continue

        total_cds_len = sum(bases for _, _, bases in cds_regions)
        if cds_pos > total_cds_len:
            continue

        if strand == -1:
            cds_regions_ordered = list(reversed(cds_regions))
        else:
            cds_regions_ordered = cds_regions

        genomic_pos = None
        accumulated = 0
        for ov_start, ov_end, bases in cds_regions_ordered:
            if accumulated + bases >= cds_pos:
                offset = cds_pos - accumulated - 1
                if strand == -1:
                    genomic_pos = ov_end - offset
                else:
                    genomic_pos = ov_start + offset
                break
            accumulated += bases

        if genomic_pos is None:
            if strand == -1:
                genomic_pos = cds_end - cds_pos + 1
            else:
                genomic_pos = cds_start + cds_pos - 1

        # Apply intronic offset for splice-site SNVs
        genomic_pos += intron_offset

        # ── Fetch reference sequence for the affected range ──────────
        seq_end = genomic_pos + event_len - 1
        ref = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    seq_resp = await client.get(
                        f"https://grch37.rest.ensembl.org/sequence/region/human/{chrom}:{genomic_pos}-{seq_end}:1",
                        headers={"Content-Type": "text/plain"},
                    )
                    seq_resp.raise_for_status()
                    ref = seq_resp.text.strip().upper()
                    if not ref:
                        ref = None
                    break
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                print(f"Ensembl sequence error for {gene} tx {tx.get('id', '?')}:{genomic_pos}: {e}")
            except Exception as e:
                print(f"Ensembl sequence error for {gene} tx {tx.get('id', '?')}:{genomic_pos}: {e}")
                break
        if not ref:
            continue

        # ── Build genomic alt ────────────────────────────────────────
        if alt_coding == '__dup__':
            # Duplication: alt = ref + ref (duplicated sequence)
            alt_bases = ref
            genomic_alt = _revcomp(alt_bases) if strand == -1 else alt_bases
        elif alt_coding == '':
            # Deletion: alt is empty, ref carries the deleted bases
            genomic_alt = ''
        else:
            # SNV or splice SNV: convert coding-strand alt to genomic
            genomic_alt = _revcomp(alt_coding) if strand == -1 else alt_coding

        return (chrom, genomic_pos, ref, genomic_alt)

    raise HTTPException(
        status_code=404,
        detail=(
            f"Variant CDS position {cds_pos} exceeds the CDS length of all "
            f"{len(all_transcripts)} protein-coding transcript(s) for gene '{gene}'. "
            "Please verify the HGVS notation and transcript reference."
        )
    )



@app.get("/api/genes/{gene_name}/variants")
async def gene_variants(
    gene_name: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Variants per page"),
):
    """Return paginated variant list for a gene."""
    gene = gene_name.strip().upper()
    variants = GENE_VARIANTS.get(gene, [])
    total = len(variants)
    total_pages = max(1, (total + per_page - 1) // per_page)
    current_page = min(page, total_pages)
    start = (current_page - 1) * per_page
    end = start + per_page
    return {
        "gene": gene,
        "variants": variants[start:end],
        "page": current_page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Return user-friendly validation errors for malformed input."""
    errors = exc.errors()
    detail = {
        "error": errors[0]["msg"] if errors else "Validation error",
        "field": errors[0]["loc"][-1] if errors else None,
        "suggestions": [],
    }
    msg = detail["error"].lower()
    if "/" in msg and ">" in msg:
        detail["suggestions"].append("Use '>' instead of '/' for substitutions")
    return JSONResponse(status_code=422, content={"detail": detail})


@app.post("/api/score")
async def score(request: ScoreRequest) -> Dict[str, Any]:
    """
    Calculate DevScore for a variant.

    Checks demo data first for instant results, then falls back
    to live API calls for unknown genes.
    """

    # ── Explicit re-validation: reject invalid HGVS before any data lookup ──
    trimmed = request.hgvs.strip()
    if not trimmed or not any(p.fullmatch(trimmed) for p in HGVS_PATTERNS):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid HGVS notation: '{request.hgvs}'. "
                "Expected formats: c.70C>T, c.112del, c.68_69del, c.5266dupC, p.Gly12Val"
            )
        )

    # Check cache first
    cache_key = cache.make_key(request.gene, request.hgvs)
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    # Check demo data for instant, reliable results
    demo = get_demo_data(request.gene, request.hgvs)

    if demo:
        raw_data = {
            "gene": demo["gene"],
            "variant": demo["variant"],
            "vep": demo["vep"],
            "clinvar": demo["clinvar"],
            "expression": demo["expression"],
            "domains": demo["domains"],
        }
        position = request.position if hasattr(request, "position") and request.position else 0
        result = calculate_devscore(raw_data, variant_position=position)

        response_dict = {
            "gene": result.gene,
            "variant": demo["variant"],
            "score": result.score,
            "V": result.V,
            "E_peak": result.E_peak,
            "C_stage": result.C_stage,
            "D_domain": result.D_domain,
            "peak_stage": result.peak_stage,
            "interpretation": result.interpretation,
            "ai_interpretation": result.ai_interpretation,
            "component_explanation": result.component_explanation,
            "data_warnings": None,
            "source": "demo_curated",
            # Extra metadata from demo data
            "gene_info": demo["gene_info"],
            "protein_change": demo["vep"].get("protein_change"),
            "expression_profile": demo["expression"],
            "sift_score": demo["vep"].get("sift_score"),
            "polyphen_score": demo["vep"].get("polyphen_score"),
            "gnomad_af": demo["gnomad"].get("allele_frequency"),
            "clinvar_classification": demo["clinvar"]["classification"],
            "source_accessions": {
                "clinvar": demo["gene_info"].get("clinvar_id"),
                "gnomad": demo["gene_info"].get("gnomad_id"),
                "expression_atlas": demo["gene_info"].get("ensembl_id"),
                "uniprot": demo["gene_info"].get("uniprot_id"),
            },
        }

        cache.set(cache_key, response_dict)
        return response_dict

    # Fall back to live API calls for unknown genes
    coords = await _resolve_variant_coords(request.gene, request.hgvs)

    coros = []
    if coords:
        chrom, pos, ref, alt = coords
        coros.append(fetch_vep(request.gene, request.hgvs, chrom, pos, ref, alt))
        coros.append(fetch_cadd(chrom, pos, alt))
    else:
        # Still try HGVS POST; no VCF fallback available
        coros.append(fetch_vep(request.gene, request.hgvs))
        coros.append(None)  # CADD placeholder – filtered out below
    coros.extend([
        fetch_clinvar(request.hgvs),
        fetch_gnomad(request.hgvs),
        fetch_expression(request.gene),
        fetch_domains(request.gene),
        fetch_gene_info(request.gene),
    ])

    results = await asyncio.gather(
        *[c for c in coros if c is not None],
        return_exceptions=True,
    )

    # Unpack results
    if coords:
        vep_result, cadd_result = results[0], results[1]
        remaining = results[2:]
    else:
        vep_result = results[0] if results else {}
        cadd_result = None
        remaining = results[1:] if len(results) > 1 else []

    clinvar_result = remaining[0] if len(remaining) > 0 else {}
    gnomad_result = remaining[1] if len(remaining) > 1 else {}
    expr_result = remaining[2] if len(remaining) > 2 else {}
    domains_result = remaining[3] if len(remaining) > 3 else {}
    gene_info_result = remaining[4] if len(remaining) > 4 else {}

    # Extract CADD phred (None if not available)
    cadd_phred = cadd_result if isinstance(cadd_result, (int, float)) else None

    # Fallback to hardcoded CADD from known_values.py when API returns null
    if cadd_phred is None:
        from .devscore.known_values import KNOWN_VALUES
        kv = KNOWN_VALUES.get(request.gene, {})
        cadd_phred = kv.get("cadd_phred")

    # ── Hard failure: VEP must succeed ──
    if isinstance(vep_result, Exception):
        msg = str(vep_result)
        raise HTTPException(status_code=502, detail=f"VEP API error: {msg}")

    # Validate variant exists in Ensembl
    if isinstance(vep_result, dict) and vep_result.get("most_severe_consequence") is None:
        raise HTTPException(status_code=422, detail=(
            f"Variant '{request.hgvs}' in gene '{request.gene}' could not be found "
            "in Ensembl. Please check the HGVS notation and gene symbol."
        ))

    # ── Soft failures: CADD and non-critical APIs just use defaults ──
    if cadd_result is not None and isinstance(cadd_result, Exception):
        cadd_result = None

    # ── Soft failures: non-critical APIs just use defaults ──
    if isinstance(clinvar_result, Exception):
        clinvar_result = {}
    if isinstance(gnomad_result, Exception):
        gnomad_result = {}
    if isinstance(expr_result, Exception):
        expr_result = {}
    if isinstance(domains_result, Exception):
        domains_result = {}
    if isinstance(gene_info_result, Exception):
        gene_info_result = {}

    # Inject cadd_phred into vep_result for the engine
    if isinstance(vep_result, dict):
        vep_result["cadd_phred"] = cadd_phred

    # Prepare data for DevScore calculation
    raw_data = {
        "gene": request.gene,
        "variant": request.hgvs,
        "vep": vep_result or {},
        "clinvar": clinvar_result or {},
        "expression": expr_result.get("data", {}) if isinstance(expr_result, dict) else {},
        "domains": domains_result or {},
    }

    position = request.position if hasattr(request, "position") and request.position else 0
    result = calculate_devscore(raw_data, variant_position=position)

    response_dict = {
        "gene": result.gene,
        "variant": result.variant,
        "score": result.score,
        "V": result.V,
        "E_peak": result.E_peak,
        "C_stage": result.C_stage,
        "D_domain": result.D_domain,
        "peak_stage": result.peak_stage,
        "interpretation": result.interpretation,
        "ai_interpretation": result.ai_interpretation,
        "component_explanation": result.component_explanation,
        "data_warnings": None,
        "source": "live_api",
        "gene_info": gene_info_result if isinstance(gene_info_result, dict) and gene_info_result.get("chromosome") else None,
        "protein_change": None,
        "expression_profile": expr_result.get("data") if isinstance(expr_result, dict) else None,
        "sift_score": vep_result.get("sift_score") if isinstance(vep_result, dict) else None,
        "polyphen_score": vep_result.get("polyphen_score") if isinstance(vep_result, dict) else None,
        "gnomad_af": gnomad_result.get("allele_frequency") if isinstance(gnomad_result, dict) else None,
        "clinvar_classification": clinvar_result.get("classification") if isinstance(clinvar_result, dict) else None,
        "source_accessions": {
            "clinvar": clinvar_result.get("accession") if isinstance(clinvar_result, dict) else None,
            "gnomad": gnomad_result.get("rsid") if isinstance(gnomad_result, dict) else None,
            "expression_atlas": expr_result.get("gene_id") if isinstance(expr_result, dict) else None,
            "uniprot": domains_result.get("accession") if isinstance(domains_result, dict) else None,
        },
    }

    cache.set(cache_key, response_dict)
    return response_dict


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    file_path = os.path.join(STATIC_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Not found")

