"""gnomAD API client."""

import httpx
from typing import Dict, Any

async def fetch_gnomad(hgvs: str) -> Dict[str, Any]:
    """
    Fetch gnomAD population frequency using the gnomAD GraphQL API.
    
    Takes an HGVS string and attempts to resolve it to an allele frequency
    in the gnomAD v4 dataset.
    """
    default_result = {
        "allele_frequency": 0.0,
        "error": "not_found",
    }
    
    # The gnomAD GraphQL endpoint
    url = "https://gnomad.broadinstitute.org/api"
    
    # First we need to search for the variant ID using the search endpoint
    # Then query its AF. For simplicity, we just do a basic dataset search.
    
    query = """
    query VariantSearch($query: String!, $dataset: DatasetId!) {
        searchResults(query: $query, dataset: $dataset) {
            variants {
                variant_id
                exome { ac an af }
                genome { ac an af }
            }
        }
    }
    """
    
    variables = {
        "query": hgvs,
        "dataset": "gnomad_r4"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url, 
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract AF
            try:
                variants = data["data"]["searchResults"]["variants"]
                if not variants:
                    return default_result
                    
                variant = variants[0]
                
                # Try genome first, then exome
                af = 0.0
                if variant.get("genome") and variant["genome"].get("af") is not None:
                    af = variant["genome"]["af"]
                elif variant.get("exome") and variant["exome"].get("af") is not None:
                    af = variant["exome"]["af"]
                    
                return {
                    "allele_frequency": af,
                    "variant_id": variant.get("variant_id"),
                    "rsid": variant.get("variant_id"),
                }
            except (KeyError, TypeError, IndexError):
                return default_result
                
    except Exception as e:
        print(f"gnomAD API error for {hgvs}: {e}")
        return {
            "allele_frequency": 0.0,
            "error": "gnomad_api_error"
        }
