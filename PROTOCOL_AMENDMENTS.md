# PROTOCOL_AMENDMENTS.md — Hivatalos Protokoll Módosítási Napló

> **Szabvány:** CTM / Cochrane Handbook v6.5 / PROSPERO 2026 Amendment Guidelines  
> **Rendszer:** GP3 Medical Research Pipeline — Oversight Loop  
> **Cél:** A lezárt (Phase 5 jóváhagyott vagy PROSPERO-ra benyújtott) protokollok összes utólagos módosításának formális, auditálható naplózása.  
> **Fájl elérési út:** `c:\Users\shuba\Desktop\Researcher - Dóri\PROTOCOL_AMENDMENTS.md`

---

## 📌 MÓDSZERTANI ÉS HEURISZTIKAI ALAPELVEK

### 1. Módosítási Osztályok
- **MAJOR (Lényegi Módosítás):**
  - Érintett területek: PICO bármely eleme (`population`, `intervention_exposure`, `comparator`, `outcome`), elsődleges kimenetel, vagy inklúziós/exklúziós kritériumok (`inclusion_criteria`, `exclusion_criteria`).
  - Következmény: **Kötelező Kettős Független Mentori Hatáselemzés (Task A: Hegyi, Task B: Garami)** + **Kötelező Részletes Kutatói Indoklás ($\ge 60$ karakter)** + **Főverzió-ugrás (`v1.x` ➔ `v2.0`)**.
- **MINOR (Kiegészítő Módosítás):**
  - Érintett területek: Elírások, stilisztikai pontosítások, bevezető háttérhivatkozások frissítése, másodlagos végpontok leíró finomítása, szoftververziók rögzítése.
  - Következmény: Nincs mentori kör; közvetlen kutatói indoklás a naplóban + Alverzió-ugrás (`v1.0` ➔ `v1.1`).

### 2. Kumulatív Horgony-Hash és Lopakodó Hatásbővülés (Cumulative Escalation)
> ⚠️ **FONTOS MÓDSZERTANI MEGJEGYZÉS:**  
> A kumulatív korlátok (**3 egymást követő MINOR módosítás** VAGY **$\ge 15\%$ kumulatív szöveges eltérés a `baseline_v1_hash` állapothoz képest**) a GP3 platform **belső kiindulási heurisztikáiként** szolgálnak a „lopakodó hatásbővülés” (cumulative scope creep) megakadályozására.  
> **Ezek a határértékek technikai biztonsági heurisztikák, NEM képezik a CTM (Centre for Translational Medicine) vagy a Cochrane hivatalos módszertani sztenderdjének részét.**  
> A küszöb elérésekor a rendszer a 3. minor módosítást automatikusan MAJOR kategóriába minősíti át, megkövetelve az átfogó kettős mentori hatáselemzést.

---

## 📋 MÓDOSÍTÁSI NAPLÓ (AMENDMENT LOG)

*(A lezárt protokollok módosításai itt kerülnek determinisztikus rögzítésre a `python src/check_phase_gate.py --check-amendment --apply` parancs futtatásával.)*

---

<!-- Sablon új bejegyzéshez:
## [{VERSION}] — {YYYY-MM-DD} ({CLASSIFICATION} AMENDMENT)
- **Projekt:** {PROJECT_NAME} [{PROJECT_ID}]
- **Módosítás azonosító:** {AMENDMENT_ID}
- **Típus:** {MAJOR | MINOR}
- **Érintett mezők:** `{CHANGED_FIELDS}`
- **Előző SHA-256 Hash:** `{OLD_HASH}`
- **Új SHA-256 Hash:** `{NEW_HASH}`

### Változás Leírása
- **Eredeti szöveg:** *"{OLD_CONTENT}"*
- **Módosított szöveg:** *"{NEW_CONTENT}"*

### Mentori Hatáselemzés (Csak MAJOR esetén)
- **Mentor Hegyi Verdikt:** {NINCS ÉRDEMI HATÁS | MÉRSÉKELT KOCKÁZAT | SÚLYOS KOCKÁZAT}  
  *Figyelmeztetés / Megjegyzés:* {HEGYI_WARNING}
- **Mentor Garami Verdikt:** {NINCS ÉRDEMI HATÁS | MÉRSÉKELT KOCKÁZAT | SÚLYOS KOCKÁZAT}  
  *Figyelmeztetés / Megjegyzés:* {GARAMI_WARNING}

### Kutatói Indoklás (Executive Decision)
> "{RESEARCHER_JUSTIFICATION}"
-->

## [v1.1] — 2026-09-25 (MINOR AMENDMENT)
- **Projekt:** Hyperglycaemia & Therapeutic Hypothermia Meta-Analysis [meta_hyperglycaemia]
- **Módosítás azonosító:** `AMD-20260925-001`
- **Típus:** MINOR
- **Érintett mezők:** `protocol_body_editorial`
- **Előző SHA-256 Hash:** `78243dbad901...`
- **Új SHA-256 Hash:** `78243dbad901...`

### Változás Leírása
- **Módosítás részlete:** Mező: protocol_body_editorial ➔ Új érték: PRISMA 2020 és PRISMA-P hivatkozások egységesítése a bevezetőben és módszertanban

### Kutatói Indoklás (Executive Decision)
> "A bevezető fejezetben a PRISMA-P és PRISMA 2020 irányelvek formai hivatkozásainak pontosítása történt a PROSPERO submission előtt."

---

## [v1.2] — 2026-09-25 (MINOR AMENDMENT)
- **Projekt:** Hyperglycaemia & Therapeutic Hypothermia Meta-Analysis [meta_hyperglycaemia]
- **Módosítás azonosító:** `AMD-20260925-002`
- **Típus:** MINOR
- **Érintett mezők:** `software_package`
- **Előző SHA-256 Hash:** `78243dbad901...`
- **Új SHA-256 Hash:** `78243dbad901...`

### Változás Leírása
- **Módosítás részlete:** Mező: software_package ➔ Új érték: R metafor v4.4-0 és Cochrane RevMan Web specifikáció

### Kutatói Indoklás (Executive Decision)
> "Biostatisztikai szoftvercsomag és script-verziók pontosítása a reprodukálhatóság érdekében."

---

## [v2.0] — 2026-09-25 (MAJOR AMENDMENT)
- **Projekt:** Hyperglycaemia & Therapeutic Hypothermia Meta-Analysis [meta_hyperglycaemia]
- **Módosítás azonosító:** `AMD-20260925-003`
- **Típus:** MAJOR *(Kumulatív Heurisztika által felminősítve)*
- **Érintett mezők:** `secondary_outcome`
- **Előző SHA-256 Hash:** `78243dbad901...`
- **Új SHA-256 Hash:** `78243dbad901...`

### Változás Leírása
- **Módosítás részlete:** Mező: secondary_outcome ➔ Új érték: Kiegészítő glikémiás variabilitási mutatók (SD, CV) leíró táblázatos bemutatása

### Mentori Hatáselemzés (Független Hatáselemzési Kör)
- **Mentor Hegyi Verdikt:** NINCS ÉRDEMI HATÁS  
  *Figyelmeztetés / Megjegyzés:* Nincs külön figyelmeztetés rögzítve.
- **Mentor Garami Verdikt:** MÉRSÉKELT KOCKÁZAT, DOKUMENTÁLANDÓ  
  *Figyelmeztetés / Megjegyzés:* A variabilitási metrikák definíciója eltér a kohorszokban, narratív szintézis javasolt.

### Kutatói Indoklás (Executive Decision)
> "A másodlagos glikémiás variabilitási mutatók leíró jellegű finomítása a feltárt újabb kohorszok alapján, Garami mentor ajánlását követve narratív szintézisként kezelve."

---
