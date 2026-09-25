import requests
import xml.etree.ElementTree as ET
import time
from typing import List, Dict, Any

class PubMedClient:
    """Client for querying PubMed via NCBI E-utilities."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(self, email: str = "researcher@example.com", tool: str = "white_spot_analyzer"):
        self.email = email
        self.tool = tool
        self.rate_limit_delay = 0.4  # Max 3 requests per second without API key

    def search(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search PubMed and return a list of publication metadata."""
        pmids = self._get_pmids(query, max_results)
        if not pmids:
            return []
        
        return self._fetch_details(pmids)

    def _get_pmids(self, query: str, max_results: int) -> List[str]:
        """Fetch PMIDs for a given query."""
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "email": self.email,
            "tool": self.tool
        }
        
        try:
            response = requests.get(self.BASE_URL + "esearch.fcgi", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"[PubMed] Keresési hiba: {e}")
            return []

    def _fetch_details(self, pmids: List[str], batch_size: int = 100) -> List[Dict[str, Any]]:
        """Fetch XML details for PMIDs in batches."""
        publications = []
        total_batches = (len(pmids) + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start = batch_num * batch_size
            end = start + batch_size
            batch = pmids[start:end]

            params = {
                "db": "pubmed",
                "id": ",".join(batch),
                "retmode": "xml",
                "rettype": "abstract",
                "email": self.email,
                "tool": self.tool
            }

            try:
                response = requests.get(self.BASE_URL + "efetch.fcgi", params=params)
                response.raise_for_status()
                publications.extend(self._parse_xml(response.text))
            except Exception as e:
                print(f"[PubMed] Letöltési hiba batch {batch_num}: {e}")

            time.sleep(self.rate_limit_delay)

        return publications

    def _parse_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response."""
        publications = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            print(f"[PubMed] XML Parse hiba: {e}")
            return []

        for article in root.findall(".//PubmedArticle"):
            pub = {"source": "PubMed"}
            
            # PMID
            pmid_el = article.find(".//PMID")
            pub["id"] = pmid_el.text if pmid_el is not None else ""
            
            # Title
            title_el = article.find(".//ArticleTitle")
            pub["title"] = "".join(title_el.itertext()) if title_el is not None else ""
            
            # Abstract
            abstract_texts = article.findall(".//AbstractText")
            if abstract_texts:
                abstract_parts = []
                for at in abstract_texts:
                    label = at.get("Label", "")
                    text = "".join(at.itertext()) if at.text is not None or len(at) > 0 else ""
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                pub["abstract"] = " ".join(abstract_parts)
            else:
                pub["abstract"] = ""
                
            # Year
            year_el = article.find(".//PubDate/Year")
            if year_el is None:
                 date_el = article.find(".//PubDate/MedlineDate")
                 if date_el is not None and date_el.text:
                     pub["year"] = date_el.text[:4]
                 else:
                     pub["year"] = ""
            else:
                pub["year"] = year_el.text
                
            # DOI
            pub["doi"] = ""
            for id_el in article.findall(".//ArticleId"):
                if id_el.get("IdType") == "doi":
                    pub["doi"] = id_el.text or ""
                    break
                    
            publications.append(pub)

        return publications
