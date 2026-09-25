"""
Garami András Knowledge Base Creator
====================================
Ez a script felépíti a ChromaDB vektordatabázist a Garami-absztraktokból.
Lokális embeddinget használ.
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
INPUT_DIR = "garami_publications"
VECTOR_DB_DIR = "garami_chroma"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_data():
    json_files = glob.glob(os.path.join(INPUT_DIR, "garami_publications_*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nem találtam publikációs fájlt.")
    latest = max(json_files)
    print(f"📂 Betöltés: {latest}")
    with open(latest, encoding="utf-8") as f:
        return json.load(f)

def create_vector_db():
    publications = load_data()
    print(f"📚 {len(publications)} publikáció feldolgozása...")

    documents = []
    for p in publications:
        if not p.get("abstract"):
            continue
        
        page_content = f"Title: {p['title']}\n\nAbstract: {p['abstract']}"
        metadata = {
            "pmid": p.get("pmid", ""),
            "year": str(p.get("year", "")),
            "journal": p.get("journal", ""),
            "url": p.get("pubmed_url", ""),
            "author": "Garami Andras et al."
        }
        documents.append(Document(page_content=page_content, metadata=metadata))

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(documents)
    
    print(f"🧠 Indexelés a '{EMBEDDING_MODEL}' modellel...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    
    print(f"✅ Vektordatabázis mentve: {VECTOR_DB_DIR}")

if __name__ == "__main__":
    create_vector_db()
