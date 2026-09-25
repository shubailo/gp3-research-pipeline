# OVERSIGHT_LOOP_PLAN.md — Permanens Felügyeleti Kör és Utólagos Protokoll-módosítási Rendszer

> **Státusz:** Architektúra-terv (Jóváhagyásra vár, kódmódosítás nélkül)  
> **Szabvány:** CTM / Cochrane Handbook v6.5 / PROSPERO 2026 Amendment Guidelines  
> **Cél:** A lezárt, beadott vagy Phase 5 utáni protokollok életciklusának determinisztikus felügyelete  
> **Alapelv:** 0 Ft extra költség, kizárólag a meglévő `check_phase_gate.py` és Antigravity Manager architektúrára építve  
> **Fájl elérési út:** `c:\Users\shuba\Desktop\Researcher - Dóri\OVERSIGHT_LOOP_PLAN.md`

---

## 1. DETERMINISZTIKUS VÁLTOZÁS-OSZTÁLYOZÓ (CHANGE ANALYZER)

A protokoll-módosítások besorolása **NEM bízható szubjektív LLM-értékelésre**. A rendszer kizárólag a már meglévő, egzakt meződefiníciók és kriptográfiai hash-összehasonlítás alapján dönt.

```
                      [Kutató Módosítást Kezdeményez]
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │  DETERMINISZTIKUS ELEMZŐ    │
                      │  (check_phase_gate.py)      │
                      └──────────────┬──────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│          MAJOR VÁLTOZÁS         │         │          MINOR VÁLTOZÁS         │
│  (Zárolt hipotézis-hash sérült) │         │ (Csak leíró/stilisztikai mezők) │
│                                 │         │                                 │
│ • PICO bármely eleme            │         │ • Nyelvhelyesség, hivatkozások  │
│ • Elsődleges végpont definíciója│         │ • Másodlagos végpontok leírása  │
│ • Inklúziós/exklúziós határok   │         │ • Szoftver verziók, formai rész │
└────────────────┬────────────────┘         └────────────────┬────────────────┘
                 │                                           │
                 ▼                                           ▼
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│ 1. Független Mentori Hatáselemzés│        │ 1. Nincs Mentori Kör            │
│ 2. Kötelező Kutatói Indoklás    │         │ 2. Egyszerűsített naplózás      │
│ 3. Verzióugrás: v1.0 ➔ v2.0     │         │ 3. Verzióugrás: v1.0 ➔ v1.1     │
│ 4. PROSPERO Amendment Generálás │         │ 4. Új hash rögzítése            │
└─────────────────────────────────┘         └─────────────────────────────────┘
```

### 1.1 A Két Osztály Egzakt Kritériumai

| Osztály | Érintett Terület | Példák | Következmény |
|---|---|---|---|
| **MAJOR** | **A `locked_hypothesis_hash` által védett mezők bármelyikének változása** | • Betegpopuláció életkora (pl. <34 hét ➔ <32 hét)<br>• Intervenció dózisa/időtartama (pl. 48h ➔ 72h)<br>• Elsődleges kimenetel módosítása (pl. NEC II+ ➔ Műtéti NEC)<br>• Kontrollcsoport definíciójának megváltoztatása | **Kötelező Kettős Független Mentori Hatáselemzés + Kutatói Indoklás + Verzióugrás (v1.x ➔ v2.0)** |
| **MINOR** | **Minden egyéb, a hipotézis magját NEM érintő szövegrész** | • Elírások, stilisztikai javítások, fordítások<br>• Háttérirodalom frissítése (újabb bevezető hivatkozás)<br>• Másodlagos végpontok felsorolási sorrendje<br>• Biostatisztikai szoftvercsomag pontosítása (pl. R metafor v4.2) | **Nincs mentori kör; közvetlen kutatói indoklás a naplóban + Alverzió ugrás (v1.0 ➔ v1.1)** |

### 1.2 Logikai Vázlat (Pszeudokód a `check_phase_gate.py`-hoz)

```python
def classify_amendment(project_data, current_pico, current_full_text):
    """
    Determinisztikusan eldönti, hogy egy módosítás MAJOR vagy MINOR.
    Nem használ AI-t: kizárólag SHA-256 hash összehasonlítással működik.
    """
    locked_core_hash = project_data.get("locked_hypothesis_hash")
    current_core_hash = compute_hypothesis_hash(current_pico)
    
    # 1. Alapvető Hipotézis Integritás Ellenőrzése
    if locked_core_hash != current_core_hash:
        # Azonosítjuk a konkrét eltérő mezőket
        changed_fields = []
        old_pico = project_data.get("pico", {})
        for field in ["population", "intervention_exposure", "comparator", "outcome"]:
            if old_pico.get(field, "").strip() != current_pico.get(field, "").strip():
                changed_fields.append(field)
                
        return {
            "classification": "MAJOR",
            "reason": "A zárolt hipotézis-hash megváltozott!",
            "changed_fields": changed_fields,
            "old_hash": locked_core_hash,
            "new_hash": current_core_hash,
            "requires_mentor_impact_assessment": True
        }
    
    # 2. Ha a mag változatlan, de a teljes szöveg módosult -> MINOR
    return {
        "classification": "MINOR",
        "reason": "A PICO és a mag-hipotézis sértetlen; a változás kiegészítő elemet érint.",
        "changed_fields": ["protocol_body_editorial"],
        "old_hash": locked_core_hash,
        "new_hash": current_core_hash,
        "requires_mentor_impact_assessment": False
    }
```

---

## 2. MAJOR ÁG: FÜGGETLEN MENTORI HATÁSELEMZÉS (IMPACT ASSESSMENT)

### 2.1 Működési Modell
MAJOR változás esetén **NEM futtatunk le új 1–10-es pontozást**, mert a tanulmány alapjait a mentorok a Phase 4-ben már jóváhagyták. 

Ehelyett egy célzott **Hatáselemzési Kört (Impact Assessment)** indítunk el a jól bevált kétkülön-task izolációs modellben:
- **Task A (Hegyi):** Külön chat-fülön kapja meg a módosítási tervezetet.
- **Task B (Garami):** Párhuzamosan, izolált chat-fülön kapja meg a módosítási tervezetet.
- Egyik sem látja a másik véleményét a saját hatáselemzésének lezárásáig.

### 2.2 A 3 Szintű Mentori Hatás-Verdikt
A mentorok kizárólag az alábbi 3 szabványos verdikt egyikét adhatják:

1. 🟢 **NINCS ÉRDEMI HATÁS (NO SUBSTANTIAL IMPACT):**
   *A módosítás nem veszélyezteti a korábban megállapított klinikai hasznot vagy élettani kauzalitást.*
2. 🟡 **MÉRSÉKELT KOCKÁZAT, DOKUMENTÁLANDÓ (MODERATE RISK — DOCUMENT & MONITOR):**
   *A módosítás korlátozza az általánosíthatóságot vagy növeli a statisztikai heterogenitást, de a kutatás módszertanilag tartható. A kutató köteles a kompromisszumot expliciten rögzíteni.*
3. 🔴 **SÚLYOS MÓDSZERTANI KOCKÁZAT, ÚJRAÉRTÉKELÉS JAVASOLT (SEVERE RISK — RE-EVALUATION ADVISED):**
   *A módosítás invalidálhatja a korábbi eredményeket (pl. ökológiai torzítás kockázata, nem poolozható heterogén kimenetel). **Ez erős szakmai javaslat, de NEM vétójog: a kutató átlépheti, ha ezt tudományosan megindokolja.***

### 2.3 Független Hatáselemzési Minta-Prompt Sablon

```markdown
Szerepköröd: [Prof. Dr. Hegyi Péter VAGY Dr. Garami András].
Feladatod: PROTOKOLL MÓDOSÍTÁSI HATÁSELEMZÉS (Impact Assessment).
Szabály: Vakon bírálsz. Nem pontozol 1-10-ig, hanem a módosítás kockázatait méred fel.

Korábban jóváhagyott állapot (v1.0):
- PICO: [KORÁBBI PICO]
- Elsődleges végpont: [KORÁBBI VÉGPONT]
- Korábbi mentori pontszámod és kulcsérved: [KORÁBBI INDOKLÁS]

Tervezett módosítás (Proposed Amendment):
- Érintett mezők: [MÓDOSÍTOTT MEZŐK]
- Új szöveg: [ÚJ SZÖVEG]
- Kutató kezdeti indoklása: [MIÉRT AKARJA MÓDOSÍTANI]

Kérdések, amikre szigorúan válaszolnod kell:
1. Mit veszélyeztet ez a módosítás a szakterületeden (klinikai túlélés / guideline hatás vs. élettani kauzalitás / méréstechnika)?
2. Melyik korábbi megállapításod vagy pontszámod veszíti érvényét emiatt?
3. Mi a konkrét verdiktje a módosításnak?

Válaszod zárd az alábbi gépi JSON blokkal:
```json
{
  "mentor": "hegyi | garami",
  "amendment_id": "<AMENDMENT_ID>",
  "verdict": "NINCS ÉRDEMI HATÁS | MÉRSÉKELT KOCKÁZAT, DOKUMENTÁLANDÓ | SÚLYOS MÓDSZERTANI KOCKÁZAT, ÚJRAÉRTÉKELÉS JAVASOLT",
  "affected_prior_reasoning": "<Melyik korábbi érv sérült>",
  "key_warning": "<A legfontosabb kockázat 1-2 mondatban>",
  "locked": true
}
```
```

---

## 3. KÖTELEZŐ KUTATÓI INDOKLÁS ÉS VERZIÓZÁS

### 3.1 A Kutatói Döntési Monopólium és a Felelősség Elve
A GP3 filozófiája szerint **a kutatásért végső soron a kutató (PI / R1) felel, nem az AI és nem a mentorok**. 
- A mentorok nem rendelkeznek vétójoggal.
- Ha a kutató egy 🔴 *SÚLYOS KOCKÁZAT* figyelmeztetés ellenére is végre akarja hajtani a változtatást, megteheti — **de nem teheti meg csendben vagy indoklás nélkül**.

### 3.2 Determinisztikusan Ellenőrizhető Indoklási Kapu
A `check_phase_gate.py` fizikailag ellenőrzi a kutatói indoklást:
1. `researcher_justification` mező hossza: $\ge 60$ karakter (nem lehet üres string).
2. Tiltólista (Placeholder Ban): Ha a szöveg `"tbd"`, `"n/a"`, `"később"`, `"módosítva"`, `"dummy"` vagy triviális ismétlés, a script megtagadja a jóváhagyást (`Exit 1`).
3. Reflektálás a mentori kritikára: Ha a mentori verdikt 🟡 vagy 🔴 volt, a kutatónak explicite le kell írnia, miért vállalja a kockázatot.

### 3.3 Szemantikus Verzióséma (SemVer for Protocols)
- **v1.0:** A Phase 4 kettős mentori bírálat után jóváhagyott, lezárt protokoll (Baseline).
- **v1.x (pl. v1.1, v1.2):** **MINOR** módosítások (elírások, új irodalmi hivatkozás a bevezetőben, szoftvercsomag frissítése).
- **v2.0 (v3.0, stb.):** **MAJOR** módosítás (bármely zárolt PICO elem, primer végpont vagy inklúziós feltétel változása).

### 3.4 A `PROTOCOL_AMENDMENTS.md` Struktúrája (PROSPERO Standard)
A gyökérben létrehozandó `PROTOCOL_AMENDMENTS.md` minden változást auditálható formában naplóz:

```markdown
# PROTOCOL_AMENDMENTS.md — Hivatalos Protokoll Módosítási Napló

## [v2.0] — 2026-10-15 (MAJOR AMENDMENT)
- **Típus:** MAJOR
- **Érintett mezők:** `PICO.Outcome` (Elsődleges végpont definíciója)
- **Előző SHA-256 Hash:** `78243dbad901...`
- **Új SHA-256 Hash:** `27500839e5d0...`

### Változás Leírása
- **Eredeti szöveg:** *"All-cause mortality and severe neurodevelopmental impairment (Bayley III < 70)"*
- **Módosított szöveg:** *"All-cause mortality and composite severe disability (Bayley III/IV < 70 or severe CP)"*

### Független Mentori Hatáselemzés
- **Mentor Hegyi Verdikt:** 🟢 NINCS ÉRDEMI HATÁS  
  *Indoklás:* A klinikai cél és az elkerülhető morbiditás nem változik; a Bayley-IV integrálása növeli az elérhető tanulmányok körét.
- **Mentor Garami Verdikt:** 🟡 MÉRSÉKELT KOCKÁZAT, DOKUMENTÁLANDÓ  
  *Indoklás:* A Bayley-III és Bayley-IV kognitív skálái nem 100%-ban egyenértékűek. Alcsoportelemzés szükséges a skálák szerint.

### Kutatói Indoklás (Executive Decision)
> *"A 2024-ben publikált legújabb centrumok már kizárólag Bayley-IV-et használtak. A vizsgálat poolozhatóságának megtartása érdekében szükséges az összevonás, de Garami mentor javaslatát beépítve a statisztikai szintézistervbe (9. fejezet) előre rögzített Bayley-verzió szerinti alcsoportelemzést illesztettünk be."*
```

---

## 4. ÁLLAPOTMODELL BŐVÍTÉSE (`data/project_state.json`)

A `data/project_state.json` kiegészül egy `amendment_history` tömbbel és egy aktuális `protocol_version` mezővel:

```json
{
  "active_project": "meta_hyperglycaemia",
  "projects": {
    "meta_hyperglycaemia": {
      "name": "Hyperglycaemia & Therapeutic Hypothermia Meta-Analysis",
      "protocol_version": "v2.0",
      "baseline_v1_hash": "78243dbad901bac3caf139a08a2b954e705df7c2446329ee405bc08f22b817d8",
      "locked_hypothesis_hash": "27500839e5d0bb4c91f1a5a08a2b954e705df7c2446329ee405bc08f22b817d8",
      "amendment_history": [
        {
          "amendment_id": "AMD-2026-001",
          "timestamp": "2026-10-15T09:30:00Z",
          "type": "MAJOR",
          "version_before": "v1.0",
          "version_after": "v2.0",
          "changed_fields": ["pico.outcome"],
          "previous_hash": "78243dbad901bac3caf139a08a2b954e705df7c2446329ee405bc08f22b817d8",
          "new_hash": "27500839e5d0bb4c91f1a5a08a2b954e705df7c2446329ee405bc08f22b817d8",
          "mentor_assessments": {
            "hegyi": {
              "verdict": "NINCS ÉRDEMI HATÁS",
              "warning": "Klinikailag indokolt a Bayley-IV integrálása.",
              "timestamp": "2026-10-15T10:15:00Z"
            },
            "garami": {
              "verdict": "MÉRSÉKELT KOCKÁZAT, DOKUMENTÁLANDÓ",
              "warning": "A skálák eltérő mérési érzékenysége miatt alcsoportelemzés kötelező.",
              "timestamp": "2026-10-15T10:30:00Z"
            }
          },
          "researcher_justification": "A 2024-es kohorszok bevonhatósága érdekében szükséges; a skálaeltérést alcsoportelemzéssel kezeljük.",
          "prospero_sync_required": true,
          "status": "APPROVED_AND_LOCKED"
        }
      ]
    }
  }
}
```

---

## 5. A GATE-CHECKER KITERJESZTÉSE MÁR LEZÁRT PROJEKTEKRE

A jelenlegi `check_phase_gate.py` a `--target-phase <N>` logikát követi. A lezárt projektek életciklusának kezelésére bevezetünk egy új parancssori kapcsolót:

```bash
python src/check_phase_gate.py --project meta_hyperglycaemia --check-amendment
```

### 5.1 A `--check-amendment` Futási Menete:
1. **PICO és Szöveg Kinyerése:** Beolvassa a protokoll jelenlegi szövegét.
2. **Hash Újraszámítása:** Kiszámítja az aktuális PICO SHA-256 hash-t.
3. **Összevetés a Zárolttal:**
   - **Ha megegyezik:**  
     `Exit 0` ➔ *"Nincs detektált módosítás. A protokoll vX.Y zárolt állapota sértetlen."*
   - **Ha eltér (Módosítás észlelve):**  
     A script megvizsgálja az `amendment_history` legfrissebb bejegyzését:
     1. Létezik-e függőben lévő amendment bejegyzés?
     2. MAJOR esetén megvan-e mindkét mentor hatáselemzése a `data/reviews/` mappában?
     3. Kitöltötte-e a kutató az érvényes indoklást ($\ge 60$ karakter, nincs placeholder)?
     4. Frissült-e a `PROTOCOL_AMENDMENTS.md` napló?
4. **Kilépési Kódok:**
   - **`0` (APPROVED):** A módosítás szabályosan dokumentált, a mentori reflexió megtörtént, a kutatói indoklás érvényes ➔ a script átírja a `locked_hypothesis_hash`-t az új értékre, növeli a verziószámot, és engedélyezi a továbbhaladást.
   - **`1` (BLOCKED):** A módosítás illegitim: a hash eltér, de hiányzik a mentori hatáselemzés vagy a kutatói indoklás ➔ a rendszer blokkolja a pipeline-t.

---

## 6. NYITOTT KÉRDÉSEK ÉS MÓDSZERTANI MEGOLDÁSOK

### 6.1 Mi történjen, ha a kutató szerint a mentori hatáselemzés téves vagy irreleváns?
- **Probléma:** Ha a mentorok túlbonyolítják vagy félreértik az új klinikai szituációt, a kutatónak joga kell legyen felülbírálni őket anélkül, hogy a mentori tekintély sérülne.
- **Megoldás: A Formalizált Eltérési Jegyzőkönyv (Formal Dissenting Rationale):**
  - A kutató **nem törölheti ki** a mentor figyelmeztetését a naplóból.
  - A `PROTOCOL_AMENDMENTS.md`-ben a mentori 🔴 *Súlyos Kockázat* bejegyzés alatt kötelezően megjelenik a kutató által megírt **Dissenting Addendum**:
    > *"A kutatócsoport megfontolta Dr. Garami módszertani aggályát a glükóz mérési időablakok kapcsán, azonban az elérhető primer közlemények hiányos időbeli bontása miatt a szigorúbb ablakok alkalmazása a mintanagyság 80%-os elvesztésével járna. A vizsgálat fenntartja az összevont időablakot, és a korlátot a Discussion fejezetben explicite deklarálja."*
  - **Eredmény:** Teljes tudományos transzparencia. A bírálók a folyóiratnál látni fogják, hogy a döntés megfontolt kompromisszum volt, nem pedig felületesség.

### 6.2 Hogyan kezeljük a "Lopakodó Hatásbővülést" (Cumulative Scope Creep)?
- **Probléma:** A kutató 5 egymást követő alkalommal végez "kis" MINOR pontosítást (pl. kizárja az ikerterhességeket, majd a kis súlyúakat, majd finomítja a gyógyszerelést), amik egyenként nem aktiválják a mentori kört, de együttesen teljesen új betegpopulációt hoznak létre.
- **Megoldás: A Kumulatív Horgony-Hash (Baseline Anchor Divergence):**
  1. A rendszer a `data/project_state.json`-ban örökre megőrzi a legelső, v1.0-s állapot **Horgony-Hash-ét (`baseline_v1_hash`)**.
  2. Minden MINOR módosításnál a script kiszámítja a teljes protokoll-szöveg távolságát (Levenshtein-távolság / szószám-eltérés) a v1.0-hoz képest.
  3. **Szabályzat:**
     - Ha a MINOR módosítások száma eléri a **3-at**, VAGY
     - A kumulatív szöveges eltérés meghaladja a **15%-ot**,
     - A script a következő MINOR módosítást **automatikusan felminősíti MAJOR kategóriába (Cumulative Escalation Trigger)**, és kötelezővé tesz egy átfogó kettős mentori hatáselemzést.
