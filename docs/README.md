# GP3 Pipeline Dokumentáció és Mentori Sablonok (`docs/`)

> **Státusz:** Kanonikus Rendszer-Dokumentáció  
> **Szerepkör:** A GP3 kutatási pipeline hivatalos mentori sablonjainak és keretrendszer-dokumentációjának tára.

---

## 📁 Könyvtárstruktúra

```
docs/
├── README.md               # Ez a tájékoztató dokumentum
└── mentor_prompts/         # Kanonikus, független mentori bírálati promptok (Phase 4)
    ├── hegyi_task_prompt.md                 # Mentor Hegyi független bírálati prompt sablon
    ├── garami_task_prompt.md                # Mentor Garami független bírálati prompt sablon
    └── impact_assessment_prompt_template.md # Mentori hatáselemzési prompt sablon (MAJOR módosításokhoz)
```

---

## 🎯 A Mentori Sablonok Használata (Phase 4)

A rendszer Alkotmánya ([`AGENTS.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) és [`MENTORS.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/MENTORS.md)) értelmében a **Phase 4 Független Mentori Bírálat** SOHA nem futtatható le egyetlen chat-beszélgetésben (Single-Context Mentor Ban).

1. **Task 1 — Mentor Hegyi:** Nyiss egy új Antigravity fület, és másold be a [`hegyi_task_prompt.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/docs/mentor_prompts/hegyi_task_prompt.md) sablont a kutatási terv kivonatával.
2. **Task 2 — Mentor Garami:** Nyiss egy második, független Antigravity fület, és másold be a [`garami_task_prompt.md`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/docs/mentor_prompts/garami_task_prompt.md) sablont a kutatási terv kivonatával.
3. **Kimenet:** A kinyert zárolt pontszámok és szókratészi kérdések közvetlenül a `data/project_state.json` állapotfájlba kerülnek rögzítésre.

---

## 🔒 Projekt-specifikus adatok és kutatási tervek

Az aktív alprojektek (pl. szisztematikus áttekintések és metaanalízisek) protokolljai, adatkivonási táblázatai és prezentációi saját projekt-könyvtáraikban (vagy a helyi `archive/` mappában) élnek, elkülönítve az általános, megosztható pipeline-keretrendszertől.
