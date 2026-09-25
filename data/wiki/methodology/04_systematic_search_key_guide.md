# 04. Szisztematikus Keresési Stratégia & Keresőkulcs Építés (CTM Guide v2.6)

> **GP3 Methodology Wiki Layer** · Centre for Translational Medicine (CTM / Semmelweis Egyetem)  
> **Szerzők:** Marie Anne Engh (CTM Meta-Analysis Coordinator) & CTM Search Strategy Team · **Verzió:** v2.6  
> **Központi Index:** [Vissza a Módszertani Tartalomjegyzékhez](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/INDEX.md) | [Főportál](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/README.md)  
> **Eredeti CTM Források:** `TM/Systematic-search.MD` és `Search Key Guide v2.6.pdf`  
> **Eredeti PDF Másolat:** [`data/wiki/resources/Search Key Guide v2.6.pdf`](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/resources/Search%20Key%20Guide%20v2.6.pdf)

---

## 1. A Szisztematikus Keresés Célja és Elsődleges Adatbázisok

A szisztematikus keresésnek **minden** releváns tanulmányt fel kell tárnia, amely valaha megjelent a témában, függetlenül attól, hogy pozitív vagy negatív eredménnyel zárult.

### Kötelező Primer Adatbázisok
A CTM szisztematikus áttekintésekben **kötelező** a párhuzamos keresés:
1. **PubMed / MEDLINE**
2. **Embase**
3. **Cochrane CENTRAL**
- **Intervenciós vizsgálatoknál kötelező kiegészítés:** ClinicalTrials.gov és WHO ICTRP regiszterek.
- **Kiegészítő bibliográfiai adatbázisok:** Scopus, Web of Science.
- ⚠️ **Keresőmotorok vs. Adatbázisok:** A Google Scholar és a TRIP search engine-ek (főleg hivatkozáskövetésre alkalmasak), NEM minősülnek elektronikus primer adatbázisnak szisztematikus kereséshez.

### Szürke Irodalom (Gray Literature) Kezelése
- **Definíció:** Nem szakbírálaton átesett közlemények (konferencia-absztraktok, poszterek, személyes adatközlések).
- **CTM Szabály:** Általánosságban **NEM AJÁNLOTT** a szürke irodalom bevonása az alacsonyabb minőség és a hiányos adatközlés miatt.
- **Kivétel:** Konferencia-kivonatok bevonhatók, *ha és amennyiben* a szakterületen rendkívül szűk a primer bizonyítékbázis, de ezt a protokollban előre specifikálni és indokolni kell.

### ⛔ Abszolút 'NOT' Tilalom
- Szigorúan tilos a `NOT` Boole operátor használata az irodalmi keresésekben! A `NOT` operátor olyan értékes cikkeket is kizárhat, amelyek csak futólag említik a kizárandó kifejezést (pl. "not associated with diabetes").

---

## 2. A Keresőkulcs Építés 6 Lépése

```
[1. Domének kijelölése] ➔ [2. Szinonimák & 5-10 MA bányászat] ➔ [3. MeSH/Emtree feltárás]
                                                                        │
[6. Tesztelés & Validáció] 🠔 [5. Keresztdomén szivárgás audit] 🠔 [4. Automata indexelés KI]
```

### 1. Lépés: Domének kijelölése
- A doméneknek **kötelezően szerepelniük kell az absztraktban**: emiatt a specifikus végpontokat (kimeneteleket/outcomes) szinte mindig **kihagyjuk** a keresőkulcsból, mert a szerzők gyakran nem nevezik meg őket a címben/absztraktban.
- **RCT szűrő domén:** Ha a vizsgálat kizárólag randomizált vizsgálatokra korlátozódik:
  - *MEDLINE:* `(random* OR blind* OR controlled clinical trial [pt] OR randomized controlled trial [pt])`
  - *Embase:* `(random* OR blind* OR 'randomized controlled trial'/exp OR 'controlled clinical trial'/de)`
  - *CENTRAL:* ⛔ **TILOS RCT szűrőt használni!** A CENTRAL eleve csak klinikai vizsgálatokat tartalmaz.

### 2. Lépés: Szinonimák kibővítése és Precedens Bányászat
- Használj minden klinikai szinonimát, rövidítést, márkanév-variációt (jóváhagyott eszközök esetén mindegyiket!).
- Vedd figyelembe a többes számokat és az angol/amerikai helyesírási eltéréseket (UK vs. US spelling: pl. *hyperglycaemia* vs. *hyperglycemia*).
- 🔍 **A CTM 5–10 Precedens Szabálya:** Kötelező **5–10 korábban publikált metaanalízis** keresőkulcsát elemezni doménenként (pl. 5–10 cikk az elhízás doménre, és 5–10 cikk a diabétesz doménre).

### 3. Lépés: MeSH és Emtree kifejezések összegyűjtése
- Nyisd meg a MeSH adatbázist (https://www.ncbi.nlm.nih.gov/mesh/) és az Emtree-t (https://www.embase.com/emtree).
- Keresd meg a hierarchiában az alárendelt (narrower) kifejezéseket, és jegyezd fel őket szöveges szinonimaként.

### 4. Lépés: Az Automata Kifejezés-Leképezés (ATM / Explosion) KIKAPCSOLÁSA
> ⚠️ **A Reprodukálhatósági Paradoxon:** A MeSH és Emtree adatbázisokat évente többször frissítik (a COVID-19 alatt még gyakrabban). Ha automata MeSH-címkéket építesz a keresőkulcsba, a keresés reprodukálhatósága néhány hónap alatt megszűnik, és a search update során nem lesz összehasonlítható az eredetivel.
> **CTM Standard:** A MeSH/Emtree kifejezéseket inspirációként használjuk szinonimák gyűjtésére, de a végleges kulcsban **szöveges kifejezésként (text words)** futtatjuk őket, az automata robbantást (explosion) pedig kikapcsoljuk!

### 5. Lépés: Keresztdomén Szivárgási Audit (Leak Check)
- Képzeld el a Domén 1 bármelyik szavának és a Domén 2 bármelyik szavának összes lehetséges kombinációját.
- Keresd meg a leginkább témán kívüli (off-topic) párosításokat: néha két ártalmatlan szó kombinációja nem várt, hatalmas zajt generál.

### 6. Lépés: Tesztelés és Validáció
- Futtasd le a kulcsot a különböző adatbázisokban:
  - Reális és kezelhető-e a találati szám?
  - Nincs-e kirívó eltérés az adatbázisok között (pl. PubMed 500 találat vs. Embase 50,000 találat)?
  - **A kulcscikkek megvannak-e?** Ellenőrizd, hogy a szakterület 3–5 ismert mérföldkő tanulmánya (key articles) benne van-e a találati halmazban.

---

## 3. Adatbázis-Specifikus Szintaxisok és Beállítások

### A. PubMed

- **Operátor sorrend:** Balról jobbra haladva értékeli ki (nem operátor-prioritás szerint!). **ZÁRÓJELEZÉS KÖTELEZŐ.**
- **Csonkolás:** `*`
- **Többszavas kifejezések és Idézőjelek:**
  - Az idézőjeleket (`"..."`) rendkívüli óvatossággal használd! Az idézőjel merev, pontos szórendet kényszerít ki (pl. a `"lip carcinoma"` nem találja meg a *„carcinoma of the lip”*-et).
  - Ha a szavak közé más szavak is kerülhetnek, használd a PubMed közelségi operátorát:  
    `"hip pain"[tiab:~5]` (megtalálja a hip és pain szavakat bármilyen sorrendben, legfeljebb 5 közbeékelt szóval). Ez a leginkább ajánlott módszer!
  - Egyszerű többszavas fogalmaknál: `(pancreatic AND cancer)` a merev `"pancreatic cancer"` helyett.
- **Automata Fordítás (ATM) Kikapcsolása:** Tégy idézőjelet az egyes szavak köré (pl. `"pancreas"`).
- **Beállítások:** Győződj meg róla, hogy a keresés után nincs bekapcsolva rejtett szűrő (pl. évszám, humán, nyelv).

---

### B. Embase

- **Emtree és Indexelés:** Az Embase cikkek kétszer annyi indexelő címkét kapnak, mint a PubMed. Az alsóbb kifejezésekre való robbantás (explosion) az Advanced Search-ben kapcsolható ki.
- **Szintaxis:**
  - Csonkolás: `*` (pl. `pancrea*`)
  - Helyettesítő karakter (Wildcard): `?` egyetlen karakterre (pl. `wom?n` ➔ woman, women).
  - Közelségi operátorok:
    - `NEXT/n` ➔ szavak megtalálása a leírt sorrendben, legfeljebb $n$ szó távolságra.
    - `NEAR/n` ➔ szavak megtalálása **bármilyen sorrendben**, legfeljebb $n$ szó távolságra (pl. `hip NEAR/5 pain`).
- **Beállítások & Mezőkódok:**
  - Használd az **Advanced search** felületet.
  - Minden automatikus mapping jelölőnégyzetet kapcsolj ki.
  - Ha túl sok a találat, szűkítsd a címmel, absztrakttal és kulcsszavakkal: tedd zárójelbe a teljes kulcsot: `(keresőkulcs):ab,kw,ti`
  - *Konferencia absztraktok megtartása:* `((keresőkulcs):ab,kw,ti) OR ((keresőkulcs) AND 'conference abstract':it)`

---

### C. Cochrane Library / CENTRAL

- **Operátor prioritás:** Standard Boole logika: `NOT > AND > OR`.
- **Szintaxis:**
  - Csonkolás: `*`. **Figyelem: A csonkolás idézőjelek között NEM működik a Cochrane-ben!**
  - Helyettesítő karakter: `?`
  - Közelségi operátorok: `NEXT/n` és `NEAR/n` (pl. `hip NEAR/5 pain`).
- **Beállítások:**
  - Használd az **Advanced search** felületet.
  - A találati listában ellenőrizd, hogy a **Trials** (Klinikai vizsgálatok) fülön vagy, NEM a Cochrane Reviews fülön!
  - Kapcsold ki a „Find word variation” opciót a Search Limits alatt.
  - ⛔ **CENTRAL KIKÖTÉS:** Mivel a CENTRAL eleve csak klinikai vizsgálatokat tartalmaz, **TILOS vizsgálattípus szerinti szűrődomént (RCT filter) alkalmazni!**

---

### D. Scopus

- **Operátor prioritás:** Eltérő sorrend: `OR > AND > AND NOT`. **Zárójelezés kötelező!**
- **Közelségi operátorok:**
  - `Pre/n` ➔ szavak a megadott sorrendben.
  - `W/n` ➔ szavak bármilyen sorrendben (pl. `hip W/5 pain`).
- **Beállítások:** A Scopus hatalmas merítése miatt a `TITLE-ABS-KEY` mezőbeállítás kötelező.

---

### E. Web of Science

- **Operátor prioritás:** `NOT > AND > OR`.
- **Helyettesítő karakterek:**
  - `?` ➔ pontosan egy karakter.
  - `$` ➔ nulla vagy egy karakter.
- **Közelségi operátor:** Csak a `NEAR/n` operátor létezik (bármilyen sorrendben, max $n$ távolságra).
- **Beállítások:** Válaszd az **Exact Search** opciót az automata regionális variációk kikapcsolásához.

---

## 4. Hibaelhárítás és Tipikus Hibák (Troubleshooting)

| Hiba / Tünet | Lehetséges Ok | CTM Megoldási Protokoll |
|---|---|---|
| **Túl sok találat / „Lyukas” kulcs (Leaky search key)** | Egy túl tág szinonima vagy domének közötti szóismétlődés | **Fedd fel a szivárgást:** Egyenként törölj ki szavakat a kulcsból, és nézd meg, melyik szó kivétele csökkenti ugrásszerűen a találatokat. Vizsgáld meg a két domén keresztmetszetét. |
| **A kulcscikkek hiányoznak a találatok közül** | Kimaradt egy fontos szinonima vagy elírás van | Nyisd meg a hiányzó cikk absztraktját, és olvasd végig figyelmesen: milyen kifejezést használtak a szerzők a céljelenségre? Építsd be a szinonimát a megfelelő doménbe. |
| **Erősen eltérő találati számok adatbázisonként** | Automata robbantás (explosion) maradt bekapcsolva | Ellenőrizd, hogy az Embase-en nincs-e `/exp` a kulcsban, vagy a Cochrane-ben nincs-e bekapcsolva a szóvariáció. 1.5–2x eltérés normális, de 10x eltérés szintaktikai hibát jelez. |
| **Túl kevés találat** | Véletlenül bekapcsolt limit, elgépelés | Ellenőrizd a dátum- és nyelvszűrőket. Ellenőrizd a brit/amerikai helyesírást (*paediatric* vs. *pediatric*). |
| **„Quoted phrases not found in phrase index” hiba a PubMeden** | Merev idézőjel olyan kifejezésen, amit a PubMed nem indexelt kifejezésként | Használd a nullás közelségi operátort: `"kifejezés"[tiab:~0]`. Ez merev kifejezésként keresi anélkül, hogy a PubMed indexelő hibát dobna. |
| **Szintaktikai hiba / Syntax error** | Tipográfiai idézőjelek („göndör idézőjelek” / curly quotes) | **A Microsoft Word vagy Outlook automatikusan átalakítja az idézőjeleket nyomdai karakterekké (`“ ”`), amit a keresők nem értenek!** A keresőkulcsokat kizárólag kód- vagy szövegszerkesztőben (Notepad, VS Code) szerkeszd sima egyenes idézőjelekkel (`"`). |
