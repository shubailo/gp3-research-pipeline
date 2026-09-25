# 📄 PROTOCOL.md — Neonatális Hyperglikaemia × Terápiás Hypothermia

## Integrált Kutatási Program: Meta-analízis + Állatkísérleti Program

> **Generálva:** /research orchestráció — 6 ágens szintézise  
> **Mentorok:** MentorGarami ✅ | MentorHegyi ✅  
> **Státusz:** Jóváhagyott terv — részletes kivitelezésre kész

---

## I. PROGRAM ÖSSZEFOGLALÁS

```
META-ANALÍZIS (T1→T2)              ÁLLATKÍSÉRLET (T0→T1)
      │                                    │
      │  Fókuszált asszociáció             │  Kauzális mechanizmus
      │  (TH alatti diszglikémia)          │  igazolása
      │                                    │
      ▼                                    ▼
"Van-e összefüggés a klinikán?"  "Miért és hogyan hat egymásra?"
      │                                    │
      └──────────────┬─────────────────────┘
                     ▼
         Jövőbeli klinikai RCT-k alapja
    "Szükséges-e glikémiás kontroll TH alatt?"
```

---

## II. META-ANALÍZIS PROTOKOLL

> Részletes keresési string és PRISMA checklist: [meta_analysis_protocol_PROSPERO.md](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/meta_analysis_protocol_PROSPERO.md)

### II.1 Kutatási kérdések (véglegesített)

**Fő kérdés:** A terápiás hypothermia *alatt* fennálló diszglikémia (hyperglikaemia, glikémiás variabilitás) asszociálható-e rosszabb kimenetellel (halálozás, neurofejlődési károsodás) HIE miatt hűtött érett és késői koraszülöttekben (≥35 hét)?

*(A koraszülött populáció TH alatti adatait másodlagos, exploratív narratív szintézisként értékeljük a limitált adatok miatt.)*

### II.2 Asszociáció erősségének és keretrendszerének értékelése

A meta-analízis az asszociáció erősségét és a lehetséges mechanisztikus hátteret vizsgálja, elismerve, hogy tisztán obszervációs adatokból a kauzalitás nem bizonyítható véglegesen:

| Kritérium | Alkalmazás a meta-analízisben | Értékelési módszer |
|-----------|------------------------------|-------------------|
| **1. Erő** | Mekkora a diszglikémia és a rossz kimenetel közti OR/RR? | Pooled effect size, 95% CI |
| **2. Konzisztencia** | Reprodukálható-e a hatás különböző kohorszokban és küszöböknél? | Szubgrupp-analízisek, I² |
| **3. Temporalitás** | Számít-e a hyperglikaemia fellépésének ideje (TH *alatt*)? | Időbeli szubgrupp: korai (<24h) vs. késői (24–72h) |
| **4. Biológiai gradiens** | Szigorúbb vércukor-küszöbök erősebb asszociációt mutatnak? | Kategorikus meta-regresszió / szubgrupp-analízis (küszöbök szerint) |
| **5. Plausibilitás** | Milyen mechanizmus magyarázhatja az asszociációt? | Állatkísérleti programunk (T0) fogja szolgáltatni a mechanisztikus bizonyítékot |

> **Publikációs stratégia:** Bár a review asszociatív, a fókuszált szubgrupp-analízisek (időzítés, küszöbök, CGM metrikák) adják az újdonságtartalmat a korábbi, általánosabb meta-analízisekhez (pl. Puzone 2023, Wang 2024) képest.

### II.3 Reviewer-k feladatmegosztása

| Feladat | Primer reviewer | Szekunder reviewer (PhD hallgató) |
|---------|-----------------|----------------------------------|
| Cím + absztrakt szűrés | ✅ | ✅ (párhuzamosan, vakon) |
| Teljes szöveg értékelés | ✅ | ✅ (párhuzamosan, vakon) |
| Adatextrakció | ✅ | ✅ (double-entry) |
| Risk of Bias (RoB2/ROBINS-I) | ✅ | ✅ (párhuzamosan) |
| Nézeteltérés feloldása | Harmadik személy (témavezető) | — |
| GRADE értékelés | ✅ | Konzultáció |

> **Javasolt szoftver:** [Rayyan](https://rayyan.ai) (ingyenes, online, vakon szűrés támogatott) → adatextrakció: Excel/Google Sheets standardizált formával → analízis: R (`meta` csomag)

### II.4 Azonnali tennivalók — Meta-analízis

- [ ] **PROSPERO regisztráció** benyújtása (a keresési string + PICO kész)
- [ ] Hyperglikaemia elsődleges definíciójának véglegesítése (javasolt: **>10 mmol/L**)
- [ ] Második reviewer (PhD hallgató) azonosítása és bevonása
- [ ] Embase + CINAHL + Cochrane hozzáférés biztosítása az intézményen keresztül
- [ ] Rayyan account létrehozás, projekt inicializálása

---

## III. ÁLLATKÍSÉRLETI PROTOKOLL

### III.1 Mérési rendszer — MentorGarami által jóváhagyott

```
HŐMÉRSÉKLET-MÉRÉSI ARCHITEKTÚRA (Garami COIN-kompatibilis)

┌─────────────────────────────────────────────┐
│  Rektális mikro-termopár (T_core)           │  ← Arany standard
│  Bőrfelszíni elvezető (T_skin, faroktő)    │  ← Autonóm effektor proxy
│                                             │
│  Δ(T_core − T_skin) = Termális gradiens    │  ← Vasoconstriction marker
│                                             │
│  COIN = (37 − T_core_mean) × idő (h)       │  ← Hűtési dózis számítás
│  Cél: COIN = (37 − 33.5) × 72 = 252 °C·h  │  ← Reprodukálható protokoll
└─────────────────────────────────────────────┘
```

**Mérési frekvencia:** T_core + T_skin: 15 percenként (adatlogger), regisztrálás az egész 72h-s TH-s időszak alatt.

**Elfogadhatósági kritérium:** T_core 33,0–34,0 °C között kell maradnia a TH teljes időtartama alatt. Eltérés esetén az állat kizárva és dokumentálva.

### III.2 STZ-Wistar Pilot Study — Dózis-optimálás

> 🔴 **Ez az első lépés — az etikai engedéllyel együtt kell tervezni**

**Cél:** Meghatározni a Wistar patkánypupokban azt a STZ-dózist, amely:
- Stabil hyperglikaémiát (≥ 15 mM P7-re) okoz
- Elfogadható mortalitással jár (< 20%)
- Nem okoz irrelevánsan extrém (> 30 mM) vércukrot

| Csoport | STZ dózis | n | Kimenetel |
|---------|-----------|---|-----------|
| Pilot A | 60 mg/kg | 6 | Vércukor P3, P5, P7 |
| Pilot B | 80 mg/kg | 6 | Vércukor P3, P5, P7 |
| Pilot C | 100 mg/kg | 6 | Vércukor P3, P5, P7 |
| **Összesen** | | **18** | |

**STZ készítési protokoll:**
```
1. Feloldás: STZ + 0.1 M nátrium-citrát puffer, pH 4.5
2. Hőmérséklet: JÉGEN tartva
3. Időlimit: Elkészítéstől számítva MAX 15-20 perc
4. Fénytől védve (alumíniumfólia)
5. Adminisztráció: P2, intraperitonealisan
6. P2 + 6-8h: 20% dextróz i.p. (10 ml/kg) — kötelező rescue
7. P3-tól: napi vércukormérés farkpontból (glükométer)
```

**Döntési kritérium:** Az optimált dózis az, amelyik ≥ 15 mM vércukrot ad P7-re, ≤ 20% mortalitással.

### III.3 Fő Kísérlet 1 — STZ-hyperglikaemia + BIOBASE-TH (aszfixia nélkül)

**Protokoll összefoglalása:**

```
P0: Születés (Wistar patkánypupok)
P2: STZ i.p. (optimált dózis) + P2+6h: dextróz rescue
P3–P6: Napi vércukor (farkpont) → dokumentálás
P7: BIOBASE hűtés indítása (33–34°C) + T_core/T_skin monitorozás
P7–P10: 72h TH protokoll
P10: TH befejezés → korai biológiai végpontok (szövet, szérum)
P10–P14: Korai viselkedési tesztek
P21–P35: Késői viselkedési tesztek + szövettani végpontok
```

**Csoportok:**

| # | Csoport | n | Megjegyzés |
|---|---------|---|------------|
| 1 | Naiv kontroll | 12 | Nincs STZ, normothermia |
| 2 | STZ-vehicle (citrát puffer) + normothermia | 12 | STZ-hatás vs. puffer hatás szétválasztás |
| 3 | STZ-hyperglikaemia + normothermia | 12 | Hyperglikaemia önálló hatása |
| 4 | STZ-hyperglikaemia + TH (BIOBASE) | 12 | **Fő kérdés: TH véd-e?** |
| 5 | STZ + inzulin-rescue + TH | 12 | BBB-specificitás kontroll |
| **Összesen** | | **60** | |

### III.4 Fő Kísérlet 2 — Rice–Vannucci + STZ + BIOBASE-TH (Fázis 3)

```
P2: STZ i.p. (optimált dózis) + rescue
P3–P6: Napi vércukor ellenőrzés
P7: Bal a. carotis communis lekötés + 8% O₂ / 90 min (Rice–Vannucci)
P7+1h: BIOBASE TH indítás (33–34°C, 72h)
P7–P10: T_core + T_skin monitorozás (15 percenként)
P10: Korai végpontok
P10–P35: Viselkedési + szövettani + biomarker végpontok
```

**Csoportok:**

| # | Csoport | n |
|---|---------|---|
| 1 | Sham + normoglikaemia + normothermia | 12 |
| 2 | HI + normoglikaemia + normothermia | 12 |
| 3 | HI + normoglikaemia + TH | 12 |
| 4 | HI + STZ-hyperglikaemia + normothermia | 12 |
| **5** | **HI + STZ-hyperglikaemia + TH** | **12** |
| **Összesen** | | **60** |

### III.5 Végpontpanel (mindkét állatkísérletre)

| Modalitás | Specifikus markerek | Mikor |
|-----------|---------------------|-------|
| **Szövettan** | H&E (neuronális kiesés), NeuN (neuronszám), GFAP (asztrogliózis), Iba-1 (mikroglia), TUNEL (apoptosis) | Hippocampus + cortex; P10 + P35 |
| **Szérumbiomarkerek** | S100B, NSE (agykárosodás), BDNF (neuroprotekció) | P7, P10, P35 |
| **Szöveti biomarkerek** | MDA, SOD (oxidatív stressz), IL-6, TNF-α (gyulladás) | P10, agyszövet |
| **Termális adatok** | T_core (rektális), T_skin (bőrfelszíni), COIN, Δ gradiens | Folyamatos 72h |
| **Metabolikus adatok** | Vércukor (naponta), testsúly | P2–P35 |
| **Viselkedési tesztek** | Righting reflex + Negative geotaxis (P10–14), Open field + Rotarod (P21–28) | Korai + késői |

---

## IV. INTEGRÁLT ÜTEMTERV

```
2026 Q3-Q4
├── MOSTANTÓL: PROSPERO benyújtás (meta-analízis)
├── MOSTANTÓL: ÁTET etikai kérelem előkészítés (állatkísérlet)
│
2026 Q4 – 2027 Q1
├── Meta-analízis: Keresés + szűrés (Rayyan)
├── BIOBASE validáció: Pilot hűtési tesztek (STZ nélkül)
│
2027 Q1-Q2
├── Meta-analízis: Adatextrakció + Risk of Bias + analízis
├── STZ pilot study (dózis-optimálás, 18 állat)
│
2027 Q2-Q3
├── Meta-analízis: Írás + beküldés (célfolyóirat: Neonatology / Pediatric Research)
├── Fő kísérlet 1: STZ + BIOBASE-TH (aszfixia nélkül)
│
2027 Q4 – 2028 Q2
├── Fő kísérlet 2: Rice–Vannucci + STZ + TH
│
2028 Q2-Q3
└── Összesített publikáció (translational paper)
```

---

## V. NYITOTT AKCIÓK — Prioritás szerint

### 🔴 Azonnali (következő 2-4 hét)
- [ ] **Hyperglikaemia definíció véglegesítése** → Javasolt: **>10 mmol/L** primer, >8 és >8,3 mmol/L szenzitivitásként
- [ ] **PROSPERO regisztráció benyújtása** (cím, PICO, search strategy kész)
- [ ] **Második reviewer azonosítása** — PhD hallgató kijelölése és bevonása
- [ ] **Intézményi Embase/CINAHL hozzáférés ellenőrzése**

### 🟡 Rövid távú (1-3 hónap)
- [ ] **ÁTET etikai kérelem** megírása (Fő kísérlet 1 + STZ pilot egyszerre)
- [ ] **BIOBASE validáció** — hűtési teszt patkánypupokon STZ nélkül (COIN-ellenőrzés)
- [ ] **G*Power analízis** — pontos állatszám kalkuláció a pilot adatokból

### 🟢 Közép távú (3-6 hónap)
- [ ] STZ pilot study elvégzése (18 állat, dózis-optimálás)
- [ ] Meta-analízis keresés lefuttatása + Rayyan szűrés megkezdése

---

## VI. VÁRHATÓ PUBLIKÁCIÓK

| # | Cím | Célfolyóirat | Impact Factor (becsült) | Időszak |
|---|-----|--------------|------------------------|---------|
| 1 | Bidirectional causal relationship between neonatal hyperglycaemia and therapeutic hypothermia (meta-analízis) | *Neonatology* / *Arch Dis Child* | 5–7 | 2027 Q3 |
| 2 | STZ-induced hyperglycaemia impairs BIOBASE-based therapeutic hypothermia neuroprotection in neonatal Wistar rats | *Pediatric Research* / *JCBFM* | 5–8 | 2028 Q1 |
| 3 | Carotid ligation asphyxia + hyperglycaemia + TH: triple-insult neonatal model | *Brain* / *JCBFM* | 10–15 | 2028 Q3 |

---

*Protokoll generálva: /research orchestráció | ResearchSage + LitReviewer + FeasibilityJudge + MetaAnalyzer + MentorGarami + MentorHegyi*  
*Dátum: 2026-09-04*
