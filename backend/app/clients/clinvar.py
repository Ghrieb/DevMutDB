"""ClinVar API client."""

import httpx
from typing import Dict, Any, Optional

async def fetch_clinvar(hgvs: str) -> Dict[str, Any]:
    """
    Fetch ClinVar variant classification using NCBI E-utilities / ClinVar E-search.
    
    This searches ClinVar for the given HGVS expression to find its 
    clinical significance classification.
    """
    default_result = {
        "classification": "Uncertain significance",
        "review_status": "no assertion provided",
        "error": "not_found",
    }
    
    # URL encode the HGVS term for search
    import os
    import urllib.parse
    
    term = urllib.parse.quote(hgvs)
    api_key = os.getenv("NCBI_API_KEY")
    key_param = f"&api_key={api_key}" if api_key else ""
    
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={term}&retmode=json{key_param}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Search for the variant ID
            search_response = await client.get(search_url)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return default_result
                
            variant_id = id_list[0]
            
            # 2. Fetch the summary for that ID
            summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id={variant_id}&retmode=json{key_param}"
            summary_response = await client.get(summary_url)
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            
            result = summary_data.get("result", {}).get(variant_id, {})
            
            # 3. Parse classification
            clinical_sig = result.get("clinical_significance", {})
            description = clinical_sig.get("description", "Uncertain significance")
            review_status = clinical_sig.get("review_status", "no assertion provided")
            
            # Handle multiple classifications (e.g., "Pathogenic/Likely pathogenic")
            if "/" in description:
                description = description.split("/")[0].strip()
            
            return {
                "classification": description.capitalize() if description else "Uncertain significance",
                "review_status": review_status,
                "variant_id": variant_id,
                "accession": variant_id,
            }
            
    except Exception as e:
        print(f"ClinVar API error for {hgvs}: {e}")
        return {
            "classification": "Uncertain significance",
            "review_status": "no assertion provided",
            "error": "clinvar_api_error"
        }
