import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("HIBA: GEMINI_API_KEY hiányzik a .env-ből!")
    exit()

genai.configure(api_key=api_key)

print("\n--- Elérhető Gemini modellek listája ---\n")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}  (Leírás: {m.display_name})")
except Exception as e:
    print(f"Hiba a listázás közben: {e}")
