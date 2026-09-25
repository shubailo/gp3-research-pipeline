---
description: Optional utility workflow to generate structured study extraction dossiers in data/wiki/<project>/studies/ from extraction data or search results. (Pilot utility, not a mandatory pipeline gate).
---

# /generate-study-wiki — Tanulmány Dosszié Generálás (Opcionális)

> **Státusz:** Pilot Eszköz (jelenleg tesztelés alatt a `neonatal_antibiotics` adathalmazon)  
> **Felelős Eszköz:** `src/generate_study_wiki.py`  
> **Wiki Célkönyvtár:** `data/wiki/<project_slug>/studies/`

---

## 1. Rendeltetés & Hatókör

Ez a parancs egy **kiegészítő, opcionális segédeszköz**, amely a beválogatott primer tanulmányokból automatikusan létrehozza a strukturált egyedi tanulmány-dossziékat a projekt wiki könyvtárában.

⚠️ **NEM KÖTELEZŐ PIPELINE KAPU:**
Ez a lépés NEM része a Phase 3 vagy Phase 4 kötelező determinisztikus kapuinak (`check_phase_gate.py`). A kutató és a csapat szabadon dönthet arról, hogy igénybe veszi-e a dossziék generálását, amíg a funkció pilot validációja be nem fejeződik.

---

## 2. Futtatás & Paraméterek

A dossziék generálása a projekt azonosítójával indítható:

```bash
python src/generate_study_wiki.py --project <project_slug>
```

Példák:
```bash
# Újszülöttkori hiperglikémia projekt 5 tanulmányának generálása:
python src/generate_study_wiki.py --project meta_hyperglycaemia

# Koraszülött antibiotikum projekt 97 kohorszának generálása:
python src/generate_study_wiki.py --project neonatal_antibiotics
```

---

## 3. Generált Tanulmány Dosszié Felépítése

Minden létrejövő lap (`<study_id>.md`) a következő elemeket tartalmazza:
1. Kanonikus hivatkozás, PMID és DOI
2. PICO megfeleltetés és betegcsoport demográfia
3. Kinyert számszerű eredmények (nyers 2x2 vagy korrigált aOR/aHR)
4. Torzításkockázat (RoB 2 vagy QUIPS doménenkénti értékelés)
5. Adatkinyerés forrása (Excel lap vagy PDF hivatkozás)
