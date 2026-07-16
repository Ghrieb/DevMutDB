"""UniProt API client."""

import httpx
from typing import Dict, Any, Optional

async def fetch_domains(gene: str) -> Dict[str, Any]:
    """
    Fetch protein domain information from UniProt.
    
    Searches UniProt by gene name to find the canonical human protein,
    then extracts its structural/functional domains.
    """
    default_result = {
        "domain_class": "REGULATORY",  # Default baseline
        "domains": [],
        "error": "not_found",
    }
    
    # 1. Search UniProt for the human gene
    search_url = f"https://rest.uniprot.org/uniprotkb/search?query=(gene:{gene}) AND (organism_id:9606) AND (reviewed:true)&format=json"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(search_url)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                return default_result
                
            protein = data["results"][0]
            uniprot_id = protein["primaryAccession"]
            
            # 2. Extract domains and map to DevMutDB classes
            features = protein.get("features", [])
            domain_features = [f for f in features if f.get("type") in ["Domain", "DNA binding", "Active site", "Region"]]
            
            # Simplistic mapping based on UniProt feature descriptions
            # In a production setting, this would be a more robust mapping table
            domain_class = "REGULATORY" # default
            
            # Check keywords/features to determine the most critical domain class
            for feature in domain_features:
                type_name = feature.get("type", "")
                desc = feature.get("description", "").lower()
                
                if type_name == "DNA binding" or "dna-binding" in desc:
                    domain_class = "DNA_BINDING"
                    break  # Highest priority
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
        print(f"UniProt API error for {gene}: {e}")
        return {
            "domain_class": "REGULATORY",
            "error": "uniprot_api_error"
        }
