"""
MedBuddy Multi-Agent UI
======================
Streamlit alkalmazás, amely lehetővé teszi a váltást a kutatói profilok között.
"""

import sys
import io
import os
import streamlit as st

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from multi_agent_service import MedBuddyAgent

# --- OLDAL KONFIGURÁCIÓ ---
st.set_page_config(
    page_title="MedBuddy - Kutatási Mentor",
    page_icon="🧬",
    layout="wide"
)

# --- STÍLUSOK ---
st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    .stChatFloatingInputContainer { bottom: 20px; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e7d32,#1b5e20); color: white; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: ÁGENS VÁLASZTÁS ---
with st.sidebar:
    st.title("🎛️ Beállítások")
    
    agent_options = {
        "hegyi": "Prof. Hegyi Péter (Metodológia)",
        "garami": "Dr. Garami András (Hőszabályozás)"
    }
    
    selected_agent_id = st.radio(
        "Válassz mentort:",
        options=list(agent_options.keys()),
        format_func=lambda x: agent_options[x]
    )
    
    st.divider()
    st.info("""
    **Hegyi Péter:** 749 publikáció alapján. Fókusz: Transzlációs medicina, PICO, precizitás.
    **Garami András:** 92 publikáció alapján. Fókusz: Thermoreguláció, TRP csatornák, láz-élettan.
    """)
    
    if st.button("💬 Chat törlése"):
        st.session_state.messages = []
        st.rerun()

# --- ÁGENS INICIALIZÁLÁSA ---
if "active_agent_id" not in st.session_state or st.session_state.active_agent_id != selected_agent_id:
    st.session_state.active_agent_id = selected_agent_id
    with st.spinner(f"🔄 {agent_options[selected_agent_id]} betöltése..."):
        st.session_state.agent = MedBuddyAgent(selected_agent_id)
        # Automatikus üdvözlés az ágens nevében
        if "messages" not in st.session_state or not st.session_state.messages:
            st.session_state.messages = [{
                "role": "assistant", 
                "content": f"Üdvözlöm! {st.session_state.agent.config['name']} vagyok. Milyen kutatási témában segíthetek ma?"
            }]

# --- FŐOLDAL ---
st.title(f"🧬 MedBuddy: {st.session_state.agent.config['name']}")
st.caption(f"Digitális kutatási mentor - {st.session_state.agent.agent_id.capitalize()} Knowledge Base (RAG)")

# Üzenetek megjelenítése
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Felhasználói input
if prompt := st.chat_input("Írja ide az ötletét vagy kérdését..."):
    # Felhasználói üzenet mentése
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Válasz generálása
    with st.chat_message("assistant"):
        with st.spinner("Gondolkodás..."):
            try:
                response = st.session_state.agent.ask(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Hiba történt: {str(e)}")
                if "ANTHROPIC_API_KEY" not in os.environ:
                    st.warning("Hiányzik az ANTHROPIC_API_KEY környezeti változó!")

# Workflow help (Expandable)
with st.expander("🛠️ Segítség kutatóknak"):
    st.markdown("""
    ### Javasolt parancsok:
    - **/brainstorm** [téma] - Új kutatási irányok keresése.
    - **/plan** [ötlet] - Részletes kutatási terv (PICO) összeállítása.
    - **Szekunder elemzés** - Meglévő adatok transzlációs értelmezése.
    """)
