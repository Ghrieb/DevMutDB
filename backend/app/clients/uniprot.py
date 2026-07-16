"""UniProt API client."""

import httpx
import asyncio
from typing import Dict, Any, Optional

async def fetch_domains(gene: str, max_retries: int = 2) -> Dict[str, Any]:
    """
    Fetch protein domain information from UniProt with retry logic.
    
    Searches UniProt by gene name to find the canonical human protein,
    then extracts its structural/functional domains.
    Retries up to max_retries times on transient failures.
    """
    default_result = {
        "domain_class": "REGULATORY",
        "domains": [],
        "error": "not_found",
    }
    
    search_url = f"https://rest.uniprot.org/uniprotkb/search?query=(gene:{gene}) AND (organism_id:9606) AND (reviewed:true)&format=json"
    
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(search_url)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("results"):
                    return default_result
                    
                protein = data["results"][0]
                uniprot_id = protein["primaryAccession"]
                
                features = protein.get("features", [])
                domain_features = [f for f in features if f.get("type") in ["Domain", "DNA binding", "Active site", "Region"]]
                
                domain_class = "REGULATORY"
                
                for feature in domain_features:
                    type_name = feature.get("type", "")
                    desc = feature.get("description", "").lower()
                    
                    if type_name == "DNA binding" or "dna-binding" in desc:
                        domain_class = "DNA_BINDING"
                        break
                    elif type_name == "Active site" or "catalytic" in desc or "kinase" in desc:
                        domain_class = "CATALYTIC"
                        break
                    elif "structural" in desc or "actin" in desc or "collagen" in desc:
                        if domain_class not in ["DNA_BINDING", "CATALYTIC"]:
                            domain_class = "STRUCTURAL"
                
                return {
                    "domain_class": domain_class,
                    "uniprot_id": uniprot_id,
                    "extracted_features": len(domain_features)
                }
                
        except Exception as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"UniProt API error for {gene} (attempt {attempt + 1}): {e} — retrying in {wait}s")
                await asyncio.sleep(wait)
            else:
                print(f"UniProt API error for {gene} after {max_retries + 1} attempts: {e}")
                return {
                    "domain_class": "REGULATORY",
                    "error": "uniprot_api_error"
                }
    
    return default_result
