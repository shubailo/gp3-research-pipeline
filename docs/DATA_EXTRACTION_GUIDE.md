# PROTOKOLL ÉS MÓDSZERTANI ÚTMUTATÓ AZ ADATKIVONÁSHOZ (DATA EXTRACTION GUIDE)
> **Projekt:** Elhúzódó empirikus antibiotikum-kezelés és klinikai biztonságosság (NEC, mortalitás) kultúra-negatív koraszülöttekben  
> **Szabvány:** PRISMA 2020 & Cochrane Handbook for Systematic Reviews of Interventions (v6.4)  
> **Munkatábla:** `results/neonatal_antibiotics/Data_Extraction_Template_Neonatal_ABX.xlsx` & `C:\Users\shuba\Downloads\Data_Extraction_Template_Neonatal_ABX.xlsx`  
> **Készítette:** Reviewer 1 (A. Shubail + AI Co-Reviewer) & Co-Lead (Teodóra Eklics / Dóri)

---

## 🎯 1. Az adatkivonás célja és PICO fókusza

Az adatkivonási táblázat célja, hogy a teljes szöveg szintjén beválogatott (Tier A és Tier B) tanulmányokból egységes, reprodukálható formában kinyerje a kvantitatív metaanalízishez és a minőségértékeléshez szükséges adatokat.

* **Populáció (P):** Koraszülött (<37 hét, <34 hét vagy <32 hét) és/vagy VLBW (<1500 g) / ELBW (<1000 g) újszülöttek, akiknél korai szepszis (EOS) gyanúja miatt empirikus antibiotikumot indítottak az első 72 órában, és a tenyésztések (vér/liquor) 48–72 óránál **negatívak (steril)** maradtak.
* **Expozíció (I):** Elhúzódó empirikus antibiotikum-kezelés (prolonged duration: tipikusan $\ge 4-5$ nap, $>72$ óra, vagy $\ge 7$ nap, illetve folyamatos DOT [Days of Therapy]).
* **Kontroll / Összehasonlító (C):** Rövid empirikus antibiotikum-kezelés (short duration: korszerű stewardship célérték $\le 48$ óra, vagy korábbi gyakorlat $\le 72$ óra / $\le 3$ nap, illetve kezeletlen 0 óra).
* **Elsődleges kimenetelek (O):**
  1. **Necrotising Enterocolitis (NEC):** Bell stádium $\ge 2$ (orvosi és sebészi NEC).
  2. **Összesített kórházi mortalitás (All-cause in-hospital mortality):** elbocsátás előtti vagy 30 napos halálozás.
  3. **Kombinált végpont:** NEC vagy halálozás.
* **Másodlagos kimenetelek (O):**
  * Késői szepszis (Late-Onset Sepsis, LOS: igazolt tenyésztéssel a 72. életóra után).
  * Invazív candidiasis / gombás fertőzés.
  * Bronchopulmonalis dysplasia (BPD: oxigénigény 36. postmenstrualis gesztációs héten).
  * Teljes enterális táplálás elérésének ideje (napokban).
  * Kórházi tartózkodás hossza (napokban).

---

## 📑 2. A munkafüzet 4 füle és azok felépítése

A generált `Data_Extraction_Template_Neonatal_ABX.xlsx` fájl 4 egymással összefüggő munkalapot tartalmaz:

### 1. Fül: `Extraction_Guide_Codebook` (Szótár és útmutató)
* Minden egyes oszlop pontos definíciója.
* Elfogadott mértékegységek, formátumok (pl. $N$, átlag $\pm$ SD, medián [IQR]).
* Valós irodalmi példák (Cotten 2009 alapján).

### 2. Fül: `Primary_Data_Extraction` (A fő adatkivonási tábla)
* **Azonosítás:** Study ID (`Szerző_Év`), Folyóirat, DOI, Ország, Centrumok száma, Tervezés (RCT / Retrospektív / Prospektív).
* **Betegjellemzők:** Összes $N$, Gesztációs kor, Születési súly, Kultúra-negatív státusz igazolása, Igazolt bakterémia kizárása.
* **Kezelés:** Antibiotikum típusa, Rövid csoport definíciója és létszáma ($N$), Elhúzódó csoport definíciója és létszáma ($N$).
* **NEC adatok:** Bell kritérium, Nyers $2 \times 2$ kontingencia ($a, b, c, d$), Nyers OR (95% CI), **Korrigált multivariábilis hatásméret (aOR / aHR / aRR)**, 95% CI (Alsó, Felső), Standard hiba ($SE$), és a modellben korrigált zavaró tényezők (confounders) listája.
* **Mortalitás adatok:** Időzítés, Nyers $2 \times 2$ kontingencia, Nyers OR, Korrigált hatásméret (aOR / aHR), 95% CI, $SE$, korrigált kovariánsok.
* **Másodlagos kimenetelek:** LOS, Gomba, BPD.
* **Adminisztráció:** Bíráló 1, Bíráló 2 (Dóri), Státusz, Megjegyzések, PDF fájlnév.

> 🌟 **Beépített aranystandard példák:** A táblázat első 5 sora már előre ki van töltve a legismertebb mérföldkő tanulmányok (Cotten 2009, Ting 2019, Kuppala 2011, Stocker 2016 NeoPInS RCT, és a legfrissebb Mackay 2026) valós számaival, hogy pontosan látható legyen az elvárt szint!

### 3. Fül: `Risk_of_Bias_Assessment` (Minőségértékelési mátrix)
* **Kohorsz vizsgálatokhoz:** **ROBINS-I** eszköz (7 domén: Confounding, Selection, Classification of interventions, Deviations, Missing data, Measurement of outcomes, Selection of reported result; Összesített: Alacsony, Mérsékelt, Súlyos, Kritikus).
* **Randomizált vizsgálatokhoz (RCT):** **Cochrane RoB 2** (Randomizáció, Eltérés a kezeléstől, Hiányzó adatok, Kimenetel mérése, Szelektív közlés).

### 4. Fül: `Stat_Export_R_Meta` (Statisztikai export Farkas Nelli biostatisztikusnak)
* Tiszta, géppel olvasható numerikus mátrix:
  * `study`, `author`, `year`, `design`, `n_total`
  * `nec_a`, `nec_n1`, `nec_c`, `nec_n2`, `nec_ln_es`, `nec_se`
  * `mort_a`, `mort_n1`, `mort_c`, `mort_n2`, `mort_ln_es`, `mort_se`
  * `rob_category`
* Közvetlenül behívható R-be (`meta::metagen` és `meta::metabin`), illetve STATA / RevMan környezetbe a Forest plotok és alcsoportelemzések generálásához!

---

## 🧮 3. Statisztikai szabályok az adatkivonáshoz

1. **Hatásméret prioritás (Adjusted vs. Crude):**
   * Mindig az **igazított (multivariábilis logisztikus vagy Cox regresszióból származó aOR / aHR)** értéket részesítjük előnyben a nyers arányokkal szemben, mivel a koraszülött kohorszokban a súlyosabb állapotú újszülöttek hajlamosabbak hosszabb kezelést kapni (confounding by indication).
   * Ha csak nyers $2 \times 2$ esetszámok állnak rendelkezésre, azokat vonjuk ki, és a statisztikus a nyers analízisben fogja futtatni.
2. **Standard hiba ($SE$) kiszámítása a 95%-os konfidenciaintervallumból:**
   Ha a cikk csak a becslést és a 95% CI-t közli, a log-hatásméret standard hibáját az alábbi Cochrane-képlettel számoljuk:
   $$SE = \frac{\ln(\text{CI Felső Határ}) - \ln(\text{CI Alsó Határ})}{3{,}92}$$
   *(A táblázat ezt automatikusan segíti kiszámolni).*
3. **Időtartam kontrasztok egységesítése:**
   * Ha egy cikk több csoportot képez (pl. $\le 2$ nap, 3–5 nap, $>5$ nap), a bázis összehasonlítás a modern $\le 48$ óra vs. elhúzódó ($\ge 5$ nap). Az alcsoport analízisnél a köztes kategóriát külön regisztráljuk.

---

## 🤝 4. Munkamegosztás és validáció (Dóri & Shubail)

* **Elsődleges adatkivonó:** Reviewer 1 (Shubail + AI) elvégzi a kinyerést a 38–53 Tier A cikkből.
* **Másodlagos ellenőrző:** Co-Lead Dóri függetlenül ellenőrzi a kulcsszámokat (esetszámok, aOR, 95% CI) a PDF táblázataiban.
* **Konszenzus:** Ha bármelyik számnál eltérés mutatkozik, az adott tétel `Status` oszlopában jelöljük, és közösen vagy a garantőrrel (Dr. Garami András / Nelli Farkas) egyeztetjük.
