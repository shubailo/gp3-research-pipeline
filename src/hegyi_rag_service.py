"""
Hegyi Péter RAG Service
=======================
Ez a modul kezeli a tudásbázis lekérdezését és a Claude AI hívásokat.
Integrálja a Hegyi-szintű system promptot és a publikációs kontextust.

Használat:
    # Az ANTHROPIC_API_KEY környezeti változó beállítása szükséges!
    python hegyi_rag_service.py "Mi a véleményed a profilaktikus antibiotikumról akut pancreatitiben?"
"""

import json
import os
import sys
import io
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
except ImportError:
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema.output_parser import StrOutputParser

# --- KONFIGURÁCIÓ ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "hegyi_chroma")
PROFILE_FILE = os.path.join(BASE_DIR, "data", "profiles", "hegyi_agent_profile.json")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class HegyiAgent:
    def __init__(self):
        print("🚀 Hegyi Agent inicializálása...")
        
        # 1. Profil betöltése
        with open(PROFILE_FILE, encoding="utf-8") as f:
            self.profile = json.load(f)
        self.system_prompt = self.profile.get("system_prompt", "")
        
        # 2. Vektordatabázis betöltése
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vectorstore = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
        # 3. LLM inicializálása (Claude-3.5-Sonnet)
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0.7,
            timeout=None,
            max_retries=2
        )
        
        # 4. Prompt Template összeállítása
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", """Használd az alábbi publikációkat kontextusként a válaszodhoz:
---
{context}
---
Kérdés/Téma: {question}

Hegyi-stílusú válasz:""")
        ])
        
        # 5. RAG Chain
        self.chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _format_docs(self, docs):
        formatted = []
        for d in docs:
            formatted.append(f"PMID: {d.metadata.get('pmid', 'N/A')}\n"
                             f"Year: {d.metadata.get('year', 'N/A')}\n"
                             f"Journal: {d.metadata.get('journal', 'N/A')}\n"
                             f"Content: {d.page_content}\n")
        return "\n---\n".join(formatted)

    def ask(self, query):
        return self.chain.invoke(query)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: python hegyi_rag_service.py \"Kutatási kérdésed...\"")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # Ellenőrizzük az API kulcsot
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_anthropic_api_key_here":
        print("\n" + "=" * 65)
        print("[!] HIBA: Az ANTHROPIC_API_KEY nincs beállítva a .env fájlban!")
        print("=" * 65)
        print("Kérjük, hozd létre a .env fájlt a gyökérben a .env.example alapján:")
        print("  ANTHROPIC_API_KEY=your_anthropic_api_key_here")
        print("=" * 65 + "\n")
        sys.exit(1)
        
    agent = HegyiAgent()
    print(f"\n--- Kérdés: {query} ---\n")
    response = agent.ask(query)
    print(f"🤖 Hegyi Agent:\n\n{response}")
