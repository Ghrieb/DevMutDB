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
                
                # Fallback: check UniProt keywords for DNA-binding
                if domain_class == "REGULATORY":
                    for kw in protein.get("keywords", []):
                        if "dna-binding" in kw.get("name", "").lower():
                            domain_class = "DNA_BINDING"
                            break
                
                # Fallback: check domain descriptions for known DNA-binding domains
                if domain_class == "REGULATORY":
                    dna_domain_kw = [
                        "homeobox", "homeodomain", "paired box",
                        "forkhead", "winged helix",
                        "bhlh", "helix-loop-helix", "basic helix",
                        "hmg box", "hmg-box",
                        "zinc finger", "t-box", "arid",
                        "pou", "ets", "runx", "gata", "myb", "rel", "stat",
                        "leucine zipper", "bzip",
                        "p53", "pax",
                    ]
                    for feature in domain_features:
                        desc = feature.get("description", "").lower()
                        if any(kw in desc for kw in dna_domain_kw):
                            domain_class = "DNA_BINDING"
                            break
                
                # Fallback: check keywords + domain descriptions for catalytic activity
                if domain_class == "REGULATORY":
                    catalytic_keywords = [
                        "kinase", "transferase", "methyltransferase",
                        "demethylase", "hydrolase", "helicase",
                        "oxidoreductase", "dioxygenase",
                        "lyase", "isomerase", "ligase",
                        "protease", "nuclease",
                    ]
                    for kw in protein.get("keywords", []):
                        kw_name = kw.get("name", "").lower()
                        if any(k in kw_name for k in catalytic_keywords):
                            domain_class = "CATALYTIC"
                            break
                
                if domain_class == "REGULATORY":
                    for feature in domain_features:
                        desc = feature.get("description", "").lower()
                        if any(kw in desc for kw in [
                            "jmjc", "jmjd", "set domain",
                            "catalytic", "methyltransferase", "demethylase",
                        ]):
                            domain_class = "CATALYTIC"
                            break
                
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
