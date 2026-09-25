"""
MedBuddy Multi-Agent RAG Service
================================
Ez a modul kezeli a különböző kutatói profilokat és a hozzájuk tartozó tudásbázisokat.
Támogatja Hegyi Pétert (Metodológia) és Garami Andrást (Hőszabályozás).
"""

import json
import os
import sys
import io
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

from langchain_chroma import Chroma
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
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class MedBuddyAgent:
    def __init__(self, agent_id="hegyi"):
        self.agent_id = agent_id
        self.config = self._get_config(agent_id)
        
        print(f"🚀 {self.config['name']} Agent inicializálása...")
        
        # 1. Profil betöltése
        with open(self.config['profile_file'], encoding="utf-8") as f:
            self.profile = json.load(f)
        self.system_prompt = self.profile.get("system_prompt", "")
        
        # 2. Vektordatabázis betöltése
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vectorstore = Chroma(
            persist_directory=self.config['vector_db'],
            embedding_function=embeddings
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
        # 3. LLM inicializálása
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0.7
        )
        
        # 4. Prompt Template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", """Használd az alábbi publikációkat kontextusként a válaszodhoz:
---
{context}
---
Kérdés/Téma: {question}

Szakértői válasz:""")
        ])
        
        # 5. RAG Chain
        self.chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _get_config(self, agent_id):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        profiles_dir = os.path.join(base_dir, "data", "profiles")
        configs = {
            "hegyi": {
                "name": "Prof. Hegyi Péter",
                "profile_file": os.path.join(profiles_dir, "hegyi_agent_profile.json"),
                "vector_db": os.path.join(base_dir, "hegyi_chroma")
            },
            "garami": {
                "name": "Dr. Garami András",
                "profile_file": os.path.join(profiles_dir, "garami_agent_profile.json"),
                "vector_db": os.path.join(base_dir, "garami_chroma")
            }
        }
        return configs.get(agent_id, configs["hegyi"])

    def _format_docs(self, docs):
        formatted = []
        for d in docs:
            formatted.append(f"Source: {d.metadata.get('pmid', 'N/A')} ({d.metadata.get('year', 'N/A')})\n"
                             f"Content: {d.page_content}\n")
        return "\n---\n".join(formatted)

    def ask(self, query):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your_anthropic_api_key_here":
            raise ValueError(
                "Az ANTHROPIC_API_KEY nem található vagy érvénytelen a környezetben!\n"
                "Kérjük, hozd létre a .env fájlt a gyökérben a .env.example alapján:\n"
                "  ANTHROPIC_API_KEY=your_anthropic_api_key_here"
            )
        return self.chain.invoke(query)

if __name__ == "__main__":
    try:
        agent = MedBuddyAgent("garami")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your_anthropic_api_key_here":
            print("\n" + "=" * 65)
            print("[!] INFORMÁCIÓ: ANTHROPIC_API_KEY nem található a .env fájlban.")
            print("=" * 65)
            print("Az ágens inicializálása és a beágyazás sikeresen lefutott (UTF-8 OK).")
            print("A kérdés megválaszolásához (LLM híváshoz) érvényes API kulcs szükséges.")
            print("Kérjük, állítsd be az ANTHROPIC_API_KEY kulcsot a .env fájlban:")
            print("  ANTHROPIC_API_KEY=your_anthropic_api_key_here")
            print("=" * 65 + "\n")
        else:
            print(agent.ask("How do TRP channels regulate fever?"))
    except Exception as e:
        print(f"\n[!] HIBA a futtatás során: {e}\n")
        sys.exit(1)
