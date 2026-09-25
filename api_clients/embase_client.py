import os
import requests
from typing import List, Dict, Any

class EmbaseClient:
    """
    Client for querying Elsevier Embase API.
    Reads ELSEVIER_API_KEY from environment variables or .env file.
    """
    
    BASE_URL = "https://api.elsevier.com/content/search/embase"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ELSEVIER_API_KEY")
        if not self.api_key:
            # Check if .env file exists and read it
            env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("ELSEVIER_API_KEY="):
                            self.api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
                            
    def search(self, query: str, count: int = 25) -> Dict[str, Any]:
        """Search Embase via Elsevier API."""
        if not self.api_key:
            raise ValueError("ELSEVIER_API_KEY nem található! Kérjük állítsd be a .env fájlban.")
            
        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json"
        }
        params = {
            "query": query,
            "count": count
        }
        
        response = requests.get(self.BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    client = EmbaseClient()
    if client.api_key:
        print("[EmbaseClient] API kulcs észlelve! Készen áll a lekérdezésre.")
    else:
        print("[EmbaseClient] Nincs API kulcs beállítva a .env fájlban.")
