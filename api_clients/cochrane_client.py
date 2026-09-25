from typing import List, Dict, Any
from .pubmed_client import PubMedClient

class CochraneClient:
    """
    Client for querying Cochrane Library.
    Since Cochrane does not offer a free public API and aggressively blocks scraping,
    this implementation queries PubMed specifically for the "Cochrane Database of Systematic Reviews"
    to find Cochrane reviews.
    """
    
    def __init__(self, email: str = "researcher@example.com"):
        self.pubmed_client = PubMedClient(email=email, tool="cochrane_analyzer")

    def search(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search Cochrane reviews and return a list of publication metadata."""
        # Append journal restriction to find only Cochrane Systematic Reviews
        cochrane_query = f'({query}) AND "Cochrane Database Syst Rev"[Journal]'
        print(f"[Cochrane] Keresés (PubMed áttétellel): {query}")
        
        publications = self.pubmed_client.search(cochrane_query, max_results)
        
        # Override source for clarity
        for pub in publications:
            pub["source"] = "Cochrane"
            
        return publications
