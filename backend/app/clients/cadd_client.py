"""CADD REST API client for PHRED scores.

CADD scores are retrieved from the public CADD REST API at
cadd.gs.washington.edu.  Unlike the public Ensembl VEP REST API,
the CADD API returns PHRED scores for all possible SNVs at a
given genomic coordinate.  Indels and multi-nucleotide variants
are not supported by the SNV range lookup endpoint.

The CADD REST API endpoint expects a half-open interval:
    GET /api/v1.0/GRCh38-v1.6/{chrom}:{start}-{end}
where end = start + 1 for a single-base query.  The response
is a JSON array with columns [Chrom, Pos, Ref, Alt, RawScore, PHRED].

The response is filtered to return only the PHRED for the requested
alt allele.
"""

import httpx
from typing import Optional


async def fetch_cadd(chrom: str, pos: int, alt: str = "") -> Optional[float]:
    """
    Query CADD v1.6 GRCh38 REST API for the PHRED score at a given SNV.

    Args:
        chrom: Chromosome (e.g. "3", "17")
        pos:   Genomic position (1-based)
        alt:   Alt allele (e.g. "T", "G") — filters the response.
               If empty or no match, returns None.

    Returns:
        PHRED score as float, or None if the API fails or no score is found.
    """
    url = f"https://cadd.gs.washington.edu/api/v1.0/GRCh37-v1.4/{chrom}:{pos}-{pos+1}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if not data or not isinstance(data, list) or len(data) < 2:
                return None

            # data[0] is the header row ("Chrom","Pos","Ref","Alt","RawScore","PHRED")
            # data[1:] are data rows
            max_phred = None
            for row in data[1:]:
                if isinstance(row, dict):
                    entry = row.get("value", [])
                elif isinstance(row, list):
                    entry = row
                else:
                    continue

                if len(entry) >= 6:
                    row_alt = str(entry[3]).upper() if entry[3] else ""
                    if alt and row_alt != alt.upper():
                        continue
                    try:
                        phred = float(entry[5])
                        if alt:
                            return round(phred, 2)
                        max_phred = max(max_phred, phred) if max_phred is not None else phred
                    except (ValueError, TypeError):
                        continue

            if alt:
                return None
            return round(max_phred, 2) if max_phred is not None else None

    except Exception as e:
        print(f"CADD API error for {chrom}:{pos}: {e}")
        return None
