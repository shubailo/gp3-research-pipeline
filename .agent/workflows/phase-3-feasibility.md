---
description: Phase 3 workflow — Feasibility & Biostatistical Gates. Poolability rule enforcement, design-specific RoB, confounder matrix, missing variable audit, and optional study wiki dossiers.
---

# /phase-3-feasibility — Megvalósíthatósági & Biostatisztikai Kapuk

> **Fázis:** Phase 3 a Kanonikus 5-Fázisú Kutatási Folyamatban  
> **Vezető Ágensek:** `feasibility-judge` (Clinical Operations) & `meta-analyzer` (Biostatistics Specialist)  
> **Kanonikus Szabályzat:** [AGENTS.md 3.3 & 3.4. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md)  
> **Releváns Módszertani Wiki Fejezetek:**  
> • [07. CTM Adatkinyerési & BoostR Útmutató (`Template v9`)](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/07_data_extraction_and_boostr.md)  
> • [08. Torzításkockázat (Risk of Bias) & Módszertani Buktatók](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/08_risk_of_bias_and_pitfalls.md)  
> • [09. Biostatisztikai Szintézis & Heterogenitás](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/09_statistical_synthesis_and_heterogeneity.md)

---

## 1. Célkitűzés & Ágenshatárok

A Phase 3 feladata a kinyerhető primer adatok matematikai és módszertani szintézisének biztosítása, az adathalmaz poolozhatóságának elbírálása, valamint a torzítások (ökológiai fallacy, zavaró tényezők, szelekciós bias) kivédése.
- **Vezető felelősök:** `feasibility-judge` (klinikai logisztika, hiányzó adatok, időzítés) és `meta-analyzer` (biostatisztika, RoB, BoostR, RVE).
- ⛔ **Ágenshatár:** A `meta-analyzer` nem fogalmaz meg klinikai indikációt; a `feasibility-judge` nem dönt statisztikai modellekről.

---

## 2. Műveleti Sorrend (Operational Steps)

1. **A Poolozhatósági Kapu Elbírálása (Poolability Gate):**
   - A beválogatott primer cikkek ellenőrzése az [AGENTS.md 3.4.1](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) szabályai szerint: **legalább 3 primer tanulmánynak PONTOSAN UGYANAZT az elsődleges kimenetelt** kell számszerűen közölnie. Ennek hiányában a fázis REJECTED.

2. **Dizájn-Specifikus Torzításkockázat Eszközök Kijelölése:**
   - A tanulmánytervhez illeszkedő validált eszköz (RoB 2, ROBINS-I, QUIPS, QUADAS-2, JBI) előírása az [AGENTS.md 3.4.2](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) és a [Wiki 08. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/08_risk_of_bias_and_pitfalls.md) szerint.

3. **Kötelező Confounder Mátrix Felállítása:**
   - Obszervációs adatoknál a biológiai zavaró változók rögzítése és a korrigált becslések (adjusted OR/HR) prioritása az [AGENTS.md 3.4.3](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) alapján.

4. **Hiányzó Változók Feasibility Auditja (70%-os Szabály):**
   - A tervezett kovariánsok áttekintése: ha a cikkek <70%-a közli, a változót tilos meta-regresszióba vonni (kötelező narratív szintézis) az [AGENTS.md 3.3.1](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) és a [Wiki 08. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/08_risk_of_bias_and_pitfalls.md) szerint.

5. **Ökológiai Torzítás Piros Zászló Szűrés:**
   - Egyéni betegszintű kimenetelek csoportszintű átlagokkal való magyarázatának kizárása az [AGENTS.md 3.3.2](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) szerint.

6. **Függő Adatok & Statisztikai Modellterv:**
   - Multilevel Meta-Analysis (Robust Variance Estimation — RVE) specifikálása az [AGENTS.md 3.4.4](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/AGENTS.md) és a [Wiki 09. Fejezet](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/09_statistical_synthesis_and_heterogeneity.md) szerint.

7. 💡 **Opcionális Lépés: Tanulmány Dossziék Generálása (`/generate-study-wiki`):**
   - Ha a projekt primer kohorszaiból strukturált Markdown dossziékat kívánsz létrehozni a `data/wiki/<project>/studies/` alá, hívd meg a [`/generate-study-wiki`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/generate-study-wiki.md) parancsot.  
   *(⚠️ Ez a funkció jelenleg pilot fázisban van a neonatal_antibiotics projekten — NEM képez kötelező kaput a Phase 4-hez).*

8. **Projekt Állapot Rögzítése:**
   - A poolozható tanulmányok listájának és a confounder mátrixnak a mentése a `data/project_state.json` állományba.

---

## 3. Záró Kapu & Determinisztikus Verifikáció

A fázis lezárása és a mentori bírálat előkészítése KIZÁRÓLAG a determinisztikus kapu sikere után engedélyezett:

```bash
python src/check_phase_gate.py --project <slug> --target-phase 4
```

- **Siker feltétele:** Kilépési kód: `0` (Gate 5 és Gate 6 PASS).
- **Kimeneti dokumentum:** `feasibility_report.md` az artifact könyvtárban.
- **Következő lépés:** [`/phase-4-mentors`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/.agent/workflows/phase-4-mentors.md) indítása.
