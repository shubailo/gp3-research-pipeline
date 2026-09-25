---
description: Deterministic Master Router for the GP3 5-Phase Medical Research Pipeline. Discovers phase state strictly via check_phase_gate.py and routes to the appropriate modular phase workflow.
---

# /research — GP3 Deterministic Master Router

> **Pipeline Architektúra:** CTM & Cochrane v6.5 Kanonikus 5-Fázisú Kutatástervezés  
> **Szabályzat:** [AGENTS.md 2. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) | [Módszertani Wiki](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/INDEX.md)  
> **Központi Koordinátor:** `orchestrator`

---

## 1. Működési Alapelv: Determinisztikus Állapot-Megállapítás

⛔ **SZIGORÚ RENDŐRI SZABÁLY (Zero LLM Memory Dependency):**
A rendszer SOHA nem a csevegési előzményekből, a modell „emlékezetéből” vagy szubjektív becslésből állapítja meg az aktuális fázist. A fázis meghatározása KIZÁRÓLAG a determinisztikus Python auditkód kimenetéből történik.

Minden `/research` hívás azonnal az alábbi paranccsal indít:

```bash
python src/check_phase_gate.py --status
```

---

## 2. Determinisztikus Döntési Logika & Útvonalválasztás

A `python src/check_phase_gate.py` kimenete alapján a router a következő moduláris munkafolyamathoz irányítja a feladatot:

| Ellenőrzött Állapot | Sikertelen Kapu / Hiányzó Feltétel | Aktív Fázis & Meghívandó Workflow | Vezető Ágens |
|---|---|---|---|
| **Phase 1 hiányos** | Nincs érvényes PICO, Címformula vagy Szenvedés Narratíva | **`/phase-1-hypothesis`** | `research-sage` |
| **Phase 2 hiányos** | Nincs 3-lépcsős keresőkulcs, precedens audit vagy PubMed találat | **`/phase-2-search`** | `lit-reviewer` |
| **Phase 3 hiányos** | Nincs $\ge 3$ azonos végpontú primer tanulmány (Poolability) vagy Confounder Matrix | **`/phase-3-feasibility`** | `feasibility-judge` + `meta-analyzer` |
| **Phase 4 hiányos** | Nincs független mentori pontozás, rekonciliáció vagy szókratészi válasz | **`/phase-4-mentors`** | `mentor-hegyi` + `mentor-garami` |
| **Phase 5 hiányos** | Nincs véglegesített PROTOCOL.md vagy Linter pontszám < 70/100 | **`/phase-5-protocol`** | `documentation-writer` |
| **Phase 5 kész (v1.0+)** | Minden kapu zöld; utólagos módosítás (Amending) szükséges | **Oversight Loop** (`--check-amendment`) | `orchestrator` |

---

## 3. A Moduláris Fázis-Munkafolyamatok Áttekintése

1. **[`/phase-1-hypothesis`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/phase-1-hypothesis.md):** Hipotézis, keretrendszer választás, PICO Címformula, 3-as Szenvedés Narratíva, T1–T4 stádium.
2. **[`/phase-2-search`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/phase-2-search.md):** 5–10 precedens MA elemzése, 3-domain keresőkulcs szintaxis (CTM Guide v2.6), Boole 'NOT' tilalom, élő PubMed futtatás.
3. **[`/phase-3-feasibility`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/phase-3-feasibility.md):** Poolability Gate ($\ge 3$ primer cikk), Confounder Matrix, 70%-os hiányzó változó szabály, ökológiai bias szűrés. *(Opcionális: `/generate-study-wiki`)*.
4. **[`/phase-4-mentors`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/phase-4-mentors.md):** Független Kettős Mentori Bírálat (Hegyi 4D + Garami 4D), Külön-Chat kényszer (Single-Context Ban), Rekonciliáció és SHA-256 Zár.
5. **[`/phase-5-protocol`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/phase-5-protocol.md):** 10 fejezetes PROTOCOL.md összeállítása, determinisztikus linter ($\ge 70$ pont), PMID halucináció-ellenőrzés, SemVer v1.0 zárás.

---

## 4. Utólagos Módosítások (Oversight Loop)

Ha a protokoll már elérte a `v1.0` állapotot, tilos közvetlenül szerkeszteni a PICO magot. Futtasd:
```bash
python src/check_phase_gate.py --project <slug> --check-amendment
```
- **MINOR változás:** Formai javítás, adminisztratív pontosítás $\rightarrow$ verzióugrás `v1.1`.
- **MAJOR változás:** PICO vagy beválogatási feltétel módosulása $\rightarrow$ független mentori hatáselemzés kötelező a két külön fülön $\rightarrow$ verzióugrás `v2.0`.
- **Kumulatív Limit:** 3 egymást követő MINOR módosítás automatikusan MAJOR-rá eszkalálódik.
