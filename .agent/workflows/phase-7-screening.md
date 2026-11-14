---
description: Phase 7 workflow — Title & Abstract Screening & Dual Adjudication. NLP relevance ranking, blinded dual screening, Cohen's Kappa calculation, and conflict resolution table.
---

# /phase-7-screening — Cím & Absztrakt Szűrés & Kettős Független Arbitráció

> **Fázis:** Phase 7 a Bővített Kutatási Folyamatban  
> **Vezető Ágensek:** `lit-reviewer` (Szűrési Specialist) + `feasibility-judge` (Klinikai Megvalósíthatóság)  
> **Szabvány:** Cochrane Handbook v6.5 §4.6 (Study Selection) · PRISMA 2020 Statement §8 · Cohen's Kappa ($\kappa$) Standard  
> **Releváns Módszertani Wiki Fejezet:**  
> • [06. Válogatás, Szűrés & Cohen's Kappa](file:///c:/Users/shuba/Desktop/Researcher%20-%20D%C3%B3ri/data/wiki/methodology/06_screening_and_selection.md)

---

## 1. Célkitűzés & Ágenshatárok

A Phase 7 feladata a Phase 6-ban előállított deduplikált bibliográfiai rekordok (`deduplicated_records.csv`) szisztematikus szűrése a Phase 1-ben rögzített PICO kritériumok mentén.
- **Vezető felelősök:**
  - `Reviewer 1 (R1 - Klinikai/Populációs Profil):` A betegpopuláció, életkor és elsődleges kimenetelek szigorú vizsgálata.
  - `Reviewer 2 (R2 - Módszertani/Expozíciós Profil):` Az expozíció dózisa, időtartama, a komparátor és a vizsgálati típus ellenőrzése.
- ⛔ **Ágenshatár:** A szűrési döntések során a két független bíráló nem beszélhet össze (Zero Cross-Talk Mandate). Az inter-rater megbízhatóságot kizárólag a független döntésekből számított Cohen's Kappa ($\kappa$) statisztikával szabad igazolni.

---

## 2. Műveleti Sorrend (Operational Steps)

1. **Relevancia-vezérelt NLP Prioritási Rangsorolás (Rayyan-szerű motor):**
   - A beválogatott referencia-tanulmányokból és a PICO kulcsszavakból TF-IDF relevanciát számolunk, és prioritási sorrendbe rendezzük a rekordokat, hogy a legvalószínűbb beválogatandó cikkek kerüljenek előre:
     ```bash
     python src/run_pipeline.py screen-nlp <projekt_slug> --threshold 0.15
     ```
   - Ezzel drasztikusan csökkenthető az átnézendő irreleváns cikkek ideje és elkerülhető a téves kizárás (False Negative Bias).

2. **Kettős Független Szűrés & Inter-Rater Megbízhatóság:**
   - A rekordok szűrése a két független algoritmus/emberi bíráló profiljával:
     ```bash
     python src/screen_literature.py --from-file projects/<slug>/literature/deduplicated_records.csv --p-terms "<populációs_kulcsszavak>" --e-terms "<expozíciós_kulcsszavak>" --dual-adjudicate --project <slug>
     ```
   - A rendszer automatikusan kiszámítja a **Cohen's Kappa ($\kappa$)** értéket:
     - $\kappa \ge 0.80$: Kiváló egyetértés (Almost perfect agreement)
     - $0.60 \le \kappa < 0.80$: Jó/Elfogadható egyetértés (Substantial agreement)
     - $\kappa < 0.60$: Nem megfelelő egyetértés ➔ a szűrési kritériumok kalibrációja kötelező!

3. **Konfliktus-Arbitráció és Döntőbírói Táblázat:**
   - Bármilyen discordancia esetén (R1 = INCLUDE, R2 = EXCLUDE, vagy UNSURE jelölés):
   - A rendszer automatikusan legenerálja az arbitrációs Excel táblát:
     `projects/<slug>/results/adjudication_conflicts.xlsx`
   - A tételeket a harmadik független szakértő (R3 - Senior Supervisor) bírálja el a konszenzus eléréséig.

4. **PRISMA 2020 Folyamatszámok Frissítése:**
   - A cím és absztrakt alapján kizárt cikkek száma rögzítésre kerül a `PRISMA_FLOW_DATA.json`-ban.
   - Előáll a **teljes szövegű vizsgálatra jogosult cikkek listája** (`full_text_candidates.csv`).

---

## 3. Záró Kapu: Phase 7 Jóváhagyás

A Phase 7 sikeresen lezártnak minősül, ha:
1. Minden deduplikált tétel elbírálásra került mindkét független ágon.
2. A Cohen's Kappa $\kappa \ge 0.60$ (ideális esetben $\ge 0.70$).
3. Minden konfliktus feloldásra került az arbitrációs táblában.
4. A teljes szövegre beválogatott cikkek listája átadható a **CTM BoostR Adatkinyerés** és az **Excel Auto-Populator** számára.

