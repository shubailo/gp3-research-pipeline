"""
Hegyi Péter Knowledge Base Creator
==================================
Ez a script felépíti a ChromaDB vektordatabázist az absztraktokból.
Lokális embeddinget használ (SentenceTransformers), így nem igényel API kulcsot.

Használat:
    python hegyi_knowledge_base.py
"""

import json
import os
import sys
import io
import glob

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- KONFIGURÁCIÓ ---
INPUT_DIR = "hegyi_publications"
VECTOR_DB_DIR = "hegyi_chroma"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_data():
    """Betölti a legfrissebb JSON fájlt."""
    json_files = glob.glob(os.path.join(INPUT_DIR, "hegyi_publications_*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nem találtam publikációs fájlt a '{INPUT_DIR}' mappában.")
    latest = max(json_files)
    print(f"📂 Betöltés: {latest}")
    with open(latest, encoding="utf-8") as f:
        return json.load(f)

def create_vector_db():
    # 1. Adat betöltése
    publications = load_data()
    print(f"📚 {len(publications)} publikáció feldolgozása...")

    # 2. Document objektumok létrehozása
    documents = []
    for p in publications:
        if not p.get("abstract"):
            continue
        
        # A tartalom a cím + absztrakt legyen a jobb kereshetőségért
        page_content = f"Title: {p['title']}\n\nAbstract: {p['abstract']}"
        
        # Metaadatok a visszakövethetőséghez
        metadata = {
            "pmid": p.get("pmid", ""),
            "year": str(p.get("year", "")),
            "journal": p.get("journal", ""),
            "url": p.get("pubmed_url", ""),
            "author": "Hegyi Peter et al."
        }
        
        documents.append(Document(page_content=page_content, metadata=metadata))

    print(f"📄 {len(documents)} dokumentum előkészítve.")

    # 3. Darabolás (bár az absztraktok kicsik, jó gyakorlat)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(documents)
    print(f"✂️ {len(splits)} text split létrehozva.")

    # 4. Embeddings & Vector Store
    print(f"🧠 Indexelés a '{EMBEDDING_MODEL}' modellel (ez eltarthat egy ideig)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # Chroma létrehozása és perzisztálása
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    
    print(f"✅ Vektordatabázis sikeresen létrehozva és elmentve: {VECTOR_DB_DIR}")

if __name__ == "__main__":
    create_vector_db()
