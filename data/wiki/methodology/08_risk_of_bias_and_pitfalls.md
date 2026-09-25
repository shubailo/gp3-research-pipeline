# 08. Torzításkockázat (Risk of Bias) & Módszertani Buktatók

> **GP3 Methodology Wiki Layer** · Centre for Translational Medicine (CTM) · Cochrane Handbook v6.5  
> **Központi Index:** [Vissza a Módszertani Tartalomjegyzékhez](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/INDEX.md) | [Főportál](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/README.md)  
> **Eredeti CTM Forrás:** `TM/META_ANALYSIS_BRAINSTORMING_SKILL.md`

---

## 1. Dizájn-Specifikus Torzításkockázat Eszközök

A torzításkockázat értékelése nem-tárgyalható, kötelező lépés minden szisztematikus áttekintésben. Mindig a primer tanulmány tervéhez illeszkedő, nemzetközileg validált eszközt kell alkalmazni:

| Tanulmány Típusa | Kötelező Eszköz | Fő Értékelési Domének |
|---|---|---|
| **Randomizált Kontrollált Vizsgálat (RCT)** | **RoB 2** (Cochrane) | Randomizáció, eltérések a beavatkozástól, hiányzó kimeneteladatok, kimenetelmérés, szelektív riportálás |
| **Nem-randomizált Beavatkozásos Vizsgálat** | **ROBINS-I** | Zavaró tényezők (confounding), szelekció, intervenció-besorolás, eltérések, hiányzó adatok, mérés, riportálás |
| **Obszervációs Prognosztikai / Etiológiai Kohorsz** | **QUIPS** (Quality in Prognosis Studies) | Részvétel (participation), Lemorzsolódás (attrition), Prognosztikai faktor mérése, Kimenetelmérés, Zavaró tényezők (Study confounding), Statisztikai analízis |
| **Diagnosztikai Pontossági Vizsgálat** | **QUADAS-2** | Betegkiválasztás, Index teszt, Referencia standard, Időzítés és betegáramlás |
| **Prevalencia / Incidencia Vizsgálat** | **JBI Critical Appraisal** | Mintavételi keret, toborzás, mintanagyság, állapot definíciója, statisztikai analízis |

### Vizualizáció és Szenzitivitás-elemzés
- **RobVis Ábrázolás:** Az eredményeket kötelező RobVis traffic-light és összesítő (summary bar) grafikonokon ábrázolni.
- **Kezelés a szintézisben:** A magas torzításkockázatú tanulmányokat **nem zárjuk ki automatikusan** a metaanalízisből. Ehelyett előre tervezett alcsoport-analízisben vagy szenzitivitás-analízisben vizsgáljuk, hogy a kizárásuk megváltoztatja-e az összesített hatásbecslést.

---

## 2. A 3 Fő Módszertani Buktató Obszervációs Metaanalízisekben

### A. Kauzális Túlállítás (Causal Overreach) Obszervációs Adatokból
- **A hiba:** Obszervációs összefüggésekből („a hiperglikémia asszociált a mortalitással”) közvetlen terápiás következtetés levonása („a vércukorcsökkentés javítja a túlélést”).
- **A védelem:** A szintézisnek szigorúan prognosztikai nyelvezetet kell használnia. Ha a primer tanulmányok nem randomizált intervenciók, kizárólag asszociációról, predikcióról és független prognosztikai értékről beszélhetünk.

### B. Hiányzó Kovariánsok Szabálya (Missing Variable Feasibility Rule)
- **A hiba:** Olyan zavaró tényező bevonása meta-regressziós modellbe, amit a primer tanulmányok jelentős része nem közölt.
- ⛔ **A 70%-os Feasibility Szabály:** Ha egy tervezett kovariánst a beválogatott primer cikkek kevesebb mint **70%-a** közöl részletesen, a változót **tilos meta-regresszióba vonni**! A változót kötelező narratív szintézisbe sorolni a hamis aggregációs torzítás kivédésére.

### C. Ökológiai Torzítás (Ecological Fallacy / Bias)
- **A hiba:** Tanulmányszintű átlagok (pl. kohorszok átlagos testhőmérséklete) alapján egyéni betegszintű kockázatokra következtetni.
- ⛔ **Ökológiai Torzítás Piros Zászló:** IPD (Individual Participant Data) hiányában tilos tanulmányi átlagokat egyéni túlélési végpontok magyarázatára használni, mert a csoportszintű regressziós egyenes iránya gyakran ellentétes az egyéni betegszintű hatással (Simpson-paradoxon).

---

## 3. Confounder Matrix és Multivariable Becslések Prioritása

Obszervációs kohorszok szintézisénél:
1. Előre specifikálni kell a biológiailag kritikus zavaró tényezőket (Confounder Matrix).
2. Mindig a korrigált hatásbecsléseket (**adjusted OR / HR**) kell előnyben részesíteni a nyers (crude) 2x2 arányokkal szemben.
3. Dokumentálni kell, hogy az egyes tanulmányok pontosan milyen faktorokra végeztek multivariábilis korrekciót (QUIPS 5. domén: Study Confounding).
