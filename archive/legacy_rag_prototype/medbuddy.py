import os
import sys
import io
import json
import time
from typing import List, Dict
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import google.generativeai as genai

# Load environment variables
load_dotenv()

class MedBuddyCLI:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("\n" + "=" * 65)
            print("[!] HIBA: GEMINI_API_KEY nem található vagy érvénytelen!")
            print("=" * 65)
            print("A MedBuddy CLI futtatásához Google Gemini API kulcs szükséges.")
            print("Kérjük, hozd létre a .env fájlt a gyökérben a .env.example alapján:")
            print("  GEMINI_API_KEY=your_gemini_api_key_here")
            print("API kulcsot itt szerezhetsz: https://aistudio.google.com/app/apikey")
            print("=" * 65 + "\n")
            sys.exit(1)
        
        # Using the verified stable 2.0 Flash model
        self.model_id = "gemini-2.0-flash"
        
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            print(f"[!] SDK Config Error: {e}")
            exit(1)
        
        # Agents setup
        self.agents = self._load_agents()
        self.active_agent_id = "hegyi"
        self.history = []
        
        # Terminal colors (ANSI codes)
        self.COLORS = {
            "hegyi": "\033[94m",    # Blue
            "garami": "\033[93m",   # Gold/Yellow
            "user": "\033[97m",     # White
            "info": "\033[90m",     # Gray
            "reset": "\033[0m"
        }

    def _load_agents(self) -> Dict:
        """Loads Hegyi and Garami profiles from JSON."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        profiles_dir = os.path.join(base_dir, "data", "profiles")
        
        agents = {}
        paths = {
            "hegyi": os.path.join(profiles_dir, "hegyi_agent_profile.json"),
            "garami": os.path.join(profiles_dir, "garami_agent_profile.json")
        }
        
        for aid, path in paths.items():
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        agents[aid] = json.load(f)
                except Exception as e:
                    print(f"[!] Hiba a profil betöltésekor ({path}): {str(e)}")
            else:
                print(f"[!] Figyelem: Profil fájl nem található: {path}")
        
        if not agents:
            print("[!] HIBA: Semelyik profil nem tölthető be.")
            exit(1)
        return agents

    def _get_system_prompt(self, agent_id: str) -> str:
        """Combines agent prompt with publication abstracts."""
        agent = self.agents.get(agent_id)
        if not agent: return "You are a medical research assistant."
        
        abstracts = "\n\n".join(agent.get("context_abstracts", []))
        return f"{agent['system_prompt']}\n\n### SCIENTIFIC BACKGROUND & PUBLICATIONS:\n{abstracts}"

    def print_header(self):
        print("\n" + "="*60)
        print("  MEDBUDDY V2 - RESEARCH MENTOR CLI (VERIFICATED)")
        print("  Translational Medicine Center / Semmelweis / PTE")
        print("="*60)
        print(f"{self.COLORS['info']}Parancsok: /hegyi, /garami, /clear, /exit{self.COLORS['reset']}\n")

    def run(self):
        self.print_header()
        
        while True:
            try:
                agent = self.agents[self.active_agent_id]
                agent_color = self.COLORS[self.active_agent_id]
                
                # Input prompt
                prompt = f"{agent_color}[{agent['name']}]{self.COLORS['reset']} > "
                user_input = input(prompt).strip()

                if not user_input:
                    continue

                # Command handling
                cmd = user_input.lower()
                if cmd == "/exit":
                    print("\nViszlát! Jó kutatást!")
                    break
                elif cmd == "/clear":
                    self.history = []
                    print(f"\n{self.COLORS['info']}--- Beszélgetés törölve ---{self.COLORS['reset']}\n")
                    continue
                elif cmd == "/hegyi":
                    self.active_agent_id = "hegyi"
                    print(f"\n{self.COLORS['info']}Átváltva: Prof. Hegyi Péter{self.COLORS['reset']}\n")
                    continue
                elif cmd == "/garami":
                    self.active_agent_id = "garami"
                    print(f"\n{self.COLORS['info']}Átváltva: Dr. Garami András{self.COLORS['reset']}\n")
                    continue

                # AI logic
                print(f"{self.COLORS['info']}Gondolkodik (Modell: {self.model_id})...{self.COLORS['reset']}", end="\r")
                
                model = genai.GenerativeModel(
                    model_name=self.model_id,
                    system_instruction=self._get_system_prompt(self.active_agent_id)
                )
                
                chat = model.start_chat(history=self.history)
                response = chat.send_message(user_input, stream=True)
                
                print(f"{agent_color}{agent['name']}:{self.COLORS['reset']}")
                for chunk in response:
                    print(chunk.text, end="", flush=True)
                print("\n")
                
                self.history = chat.history

            except KeyboardInterrupt:
                print("\n\nViszlát!")
                break
            except Exception as e:
                print(f"\n[!] HIBA: {str(e)}\n")
                if "404" in str(e):
                    print(f"{self.COLORS['info']}Próbálkozás alternatívval (gemini-flash-latest)...{self.COLORS['reset']}")
                    self.model_id = "gemini-flash-latest"

if __name__ == "__main__":
    cli = MedBuddyCLI()
    cli.run()
