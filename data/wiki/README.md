# GP3 Medical Research Wiki & Knowledge Portal

> **Kanonikus Orvostudományi és Transzlációs Kutatási Tudásbázis**  
> **Szabvány:** Centre for Translational Medicine (CTM / Semmelweis Egyetem) · Cochrane Handbook v6.5 · PRISMA 2020  
> **Dátum:** 2026-09-25  

---

## 🏛️ A WIKI STRUKTÚRÁJA ÉS RENDELTETÉSE

Ez a tudásbázis két szervesen összefüggő pillérre épül:
1. **[Módszertani és CTM Képzési Tudástár (`methodology/`)](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/INDEX.md):** A Semmelweis Egyetem Transzlációs Medicina Központjának (CTM) 22-lépéses mester munkafolyamata, a Cochrane Handbook v6.5 direktívái, adatgyűjtési és biostatisztikai szabványai (12 kanonikus fejezet).
2. **Kutatási Projektek & Tanulmány Dossziék:** A folyamatban lévő szisztematikus áttekintések és metaanalízisek tételes, transzparens primer adatlapjai és extrakciós táblázatai.

```
data/wiki/
├── README.md                                  ◄── Ön itt áll (Központi Portál)
├── methodology/                               ◄── CTM & Cochrane Módszertani Tudástár (12 fejezet)
│   ├── INDEX.md                                   Módszertani Navigációs Index
│   ├── 01_translational_medicine_model.md         A 4-elemes transzlációs ciklus
│   ├── 02_topic_selection_finer.md                Témaválasztás & FINER kritériumok
│   ├── 03_clinical_question_frameworks.md         PICO/PEO/CoCoPop/PIRD & Tanulmánytervek
│   ├── 04_systematic_search_key_guide.md          Szisztematikus keresés & Keresőkulcs CTM v2.6
│   ├── 05_protocol_and_prospero.md                Protokoll-tervezés & PROSPERO
│   ├── 06_screening_and_selection.md              Kettős független szűrés & Cohen's Kappa
│   ├── 07_data_extraction_and_boostr.md           CTM Template v9 & BoostR adattisztítás
│   ├── 08_risk_of_bias_and_pitfalls.md            RoB 2, QUIPS, ROBINS-I & Módszertani Buktatók
│   ├── 09_statistical_synthesis_and_heterogeneity.md  Poolozhatóság, RVE & TSA
│   ├── 10_grade_and_storytelling.md               6-mondatos narratíva & GRADE
│   ├── 11_ctm_22_step_master_workflow.md          A 22-lépéses CTM Mester Folyamat & Moodle
│   └── 12_cochrane_handbook_v6_5_reference.md     Cochrane Handbook v6.5 kézikönyv
├── neonatal_antibiotics/                      ◄── Koraszülött Antibiotikum Meta-analízis
│   └── studies/                                   97 primer tanulmány extrakciós dossziéja
└── meta_hyperglycaemia/                       ◄── Újszülöttkori HIE & Hűtés alatti Vércukor
    └── studies/                                   Megerősített poolozható tanulmányok (k=5)
```

---

## 📚 1. CTM MÓDSZERTANI TUDÁSTÁR (12 KANONIKUS FEJEZET)

| Fejezet | Cím | Kulcstémák & CTM Szabványok |
|:---:|---|---|
| **01** | **[Transzlációs Medicina Modell](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/01_translational_medicine_model.md)** | Healthcare ➔ Science ➔ Knowledge ➔ Communication ciklus; a szisztematikus áttekintések hídszerepe |
| **02** | **[Témaválasztás & FINER](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/02_topic_selection_finer.md)** | Feasible, Interesting, Novel, Ethical, Relevant; a 3-as Szenvedés Narratíva (Beteg, Család, Remény) |
| **03** | **[Klinikai Kérdés & Tervezés](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/03_clinical_question_frameworks.md)** | A 7 keretrendszer: PICO, PECO, PEO, PFO, CoCoPop, PCC, PICo; RCT vs. Kohorsz; Lumping/Splitting |
| **04** | **[Keresési Stratégia & CTM Guide v2.6](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/04_systematic_search_key_guide.md)** | Marie Anne Engh 6 lépése; 5-10 MA bányászata; ⛔ 'NOT' tilalom; PubMed/Embase/CENTRAL/Scopus |
| **05** | **[Protokoll & PROSPERO](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/05_protocol_and_prospero.md)** | Kötelező a priori regisztráció adatgyűjtés előtt; reporting bias kivédése; PRISMA-P |
| **06** | **[Szűrés & Választás](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/06_screening_and_selection.md)** | Kettős független szűrés (R1, R2, R3), Cohen's Kappa mérés, CitationChaser másodlagos keresés |
| **07** | **[Adatkinyerés & BoostR](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/07_data_extraction_and_boostr.md)** | `Data_extraction_template_v9.xlsx` 14 lapja; BoostR 5-pontos adattisztítási ellenőrzőlista |
| **08** | **[Torzításkockázat & Buktatók](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/08_risk_of_bias_and_pitfalls.md)** | RoB 2, QUIPS, ROBINS-I, QUADAS-2, JBI; Kauzális túlállítás, 70%-os hiányzó változó szabály, Ökológiai bias |
| **09** | **[Biostatisztikai Szintézis](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/09_statistical_synthesis_and_heterogeneity.md)** | Poolability Rule (≥3 primer cikk), RVE függő adatokra, heterogenitás ($I^2$), TSA |
| **10** | **[GRADE & Storytelling](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/10_grade_and_storytelling.md)** | CTM 6-mondatos eredménykommunikáció, GRADE bizonyítékminőség (SoF táblázatok), PRISMA 2020 |
| **11** | **[CTM 22-Lépéses Mester Munkafolyamat](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/11_ctm_22_step_master_workflow.md)** | Governance: 8 SMS jóváhagyási kapu; a teljes hivatalos Semmelweis CTM Moodle tananyag (45 oldal) |
| **12** | **[Cochrane Handbook v6.5 Kézikönyv](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/12_cochrane_handbook_v6_5_reference.md)** | A nemzetközi arany standard kézikönyv fejezetenkénti összefoglalója és ágens direktívái |

---

## 🔬 2. AKTÍV KUTATÁSI PROJEKTEK A WIKIBEN

### A. Neonatal Empirical Antibiotic Duration (`neonatal_antibiotics`)
- **Státusz:** Phase 3 — Adatkinyerés befejezve, 97 primer kohorsz extrahálva
- **Tanulmány Dossziék:** [97 Kohorsz Lap (`neonatal_antibiotics/studies/`)](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/neonatal_antibiotics/studies/)
- **Fő Végpontok:** Koraszülöttek NEC, all-cause mortalitás, szepszis, kórházi tartózkodás (LOS)
- **Fő Forrás:** `Data_Extraction_Template_Neonatal_ABX.xlsx`

### B. Hyperglycaemia & Therapeutic Hypothermia in HIE (`meta_hyperglycaemia`)
- **Státusz:** Phase 3 — Új 3-domain keresés lefutva (524 rekord), 5 poolozható kohorsz megerősítve
- **Kanonikus Cím:** *"Investigating the effect of hyperglycaemia on neurodevelopmental outcomes in neonates with HIE undergoing therapeutic hypothermia"*
- **Megerősített Poolozható Vizsgálatok ($k = 5$, $N = 961$):**
  1. **Perez et al., 2023** ([PMID: 37655394](https://pubmed.ncbi.nlm.nih.gov/37655394)) — $n = 491$ HIE + TH
  2. **Kamino et al., 2023** ([PMID: 37181414](https://pubmed.ncbi.nlm.nih.gov/37181414)) — $n = 108$ NE (95% TH) — *Újonnan visszanyerve!*
  3. **Ali et al., 2024** ([PMID: 38782623](https://pubmed.ncbi.nlm.nih.gov/38782623)) — $n = 153$ HIE + TH
  4. **Chouthai et al., 2015** ([PMID: 26410436](https://pubmed.ncbi.nlm.nih.gov/26410436)) — $n = 102$ HIE + TH
  5. **Basu et al., 2017** ([PMID: 27799322](https://pubmed.ncbi.nlm.nih.gov/27799322)) — $n = 107$ HIE + TH

---

## 🛠️ KAPCSOLÓDÓ ESZKÖZÖK ÉS SCRIPTEK

- **Protokoll Linter:** `python src/validate_protocol.py PROTOCOL.md`
- **Fáziskapu Ellenőrző:** `python src/check_phase_gate.py --target-phase <N>`
- **Irodalomkutató:** `python src/literature_search.py "<query>" --analyze`
- **Irodalomszűrő:** `python src/screen_literature.py --from-file <search.json>`
- **Dosszié Generáló (Opcionális eszköz):** `python src/generate_study_wiki.py`
