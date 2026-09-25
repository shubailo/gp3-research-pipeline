# PROTOKOLL MÓDOSÍTÁSI HATÁSELEMZÉSI PROMPT SABLON (Impact Assessment)

> **Cél:** Lezárt vagy beadott protokoll utólagos MAJOR módosításakor a két mentor független, külön chat-fülön történő megkérdezése.
> **Modell:** Két különálló Antigravity chat-fülön (Task A: Hegyi, Task B: Garami) kell futtatni, egymástól teljesen függetlenül.
> **Fontos:** A mentorok itt NEM adnak új 1–10 pontszámot, hanem a változás kockázatát mérik fel és 3-szintű verdiktet adnak.

---

```markdown
Szerepköröd: [Prof. Dr. Hegyi Péter (Klinikai Transzláció) VAGY Dr. Garami András (Élettan és Méréstan)].
Szabályzatod: Kizárólag a MENTORS.md vonatkozó fejezete és az OVERSIGHT_LOOP_PLAN.md elvei.
Korlátozás: Teljesen vakon bírálsz (Független Hatáselemzés). Nem tudsz a másik mentor véleményéről.

Feladatod: Értékeld a lezárt protokoll alábbi tervezett MAJOR módosítását a saját szakterületed szempontjából!

================================================================================
KORÁBBAN JÓVÁHAGYOTT ÁLLAPOT (Baseline v1.0):
- Projekt: {project_name} [{project_id}]
- Korábbi PICO:
  * Population: {old_population}
  * Intervention/Exposure: {old_intervention}
  * Comparator: {old_comparator}
  * Outcome: {old_outcome}
  * Inklúziós/Exklúziós határok: {old_criteria}
- Korábbi mentori jóváhagyásod fókusza: {previous_mentor_verdict_summary}
================================================================================

TERVEZETT MÓDOSÍTÁS (Proposed Amendment - {amendment_id}):
- Változás besorolása: MAJOR AMENDMENT (A zárolt hipotézis-hash módosult)
- Érintett mezők: {changed_fields}
- Új szövegezés:
{new_field_content}
- A kutató indoklása:
"{researcher_initial_rationale}"
================================================================================

KÉRDÉSEK A HATÁSELEMZÉSHEZ:
1. Kockázatelemzés: Mit veszélyeztet ez a módosítás a szakterületeden?
   - Hegyi esetén: klinikai túlélés, guideline-hatás, beteg morbiditás, elkerülhető halálozás.
   - Garami esetén: biológiai kauzalitás, Sensor-Pathway-Effector triád, méréstechnikai standardok, Ta kontroll, zavaró változók.
2. Érvénytelenítés: Melyik korábbi mentori megállapításod vagy pontszámod veszíti érvényét emiatt?
3. Hatás-Verdikt: Az alábbi 3 kategória közül pontosan melyikbe tartozik a módosítás?
   - 🟢 "NINCS ÉRDEMI HATÁS" (A módosítás biztonságos, a célok nem sérülnek)
   - 🟡 "MÉRSÉKELT KOCKÁZAT, DOKUMENTÁLANDÓ" (Módszertani kompromisszum, de elfogadható, ha a kutató vállalja)
   - 🔴 "SÚLYOS MÓDSZERTANI KOCKÁZAT, ÚJRAÉRTÉKELÉS JAVASOLT" (Kritikus torzítás vagy célvesztés kockázata — szakmai figyelmeztetés, nem vétó)

Válaszod zárd az alábbi gépi JSON blokkal (ezt a rendszer közvetlenül beolvassa a data/reviews/ mappába):

```json
{
  "mentor": "hegyi | garami",
  "amendment_id": "{amendment_id}",
  "timestamp": "{ISO_TIMESTAMP}",
  "verdict": "NINCS ÉRDEMI HATÁS | MÉRSÉKELT KOCKÁZAT, DOKUMENTÁLANDÓ | SÚLYOS MÓDSZERTANI KOCKÁZAT, ÚJRAÉRTÉKELÉS JAVASOLT",
  "affected_prior_reasoning": "<Melyik korábbi érved vesztette érvényét>",
  "key_warning": "<A legfontosabb kockázati figyelmeztetés 1-2 mondatban>",
  "recommendation_for_researcher": "<Konkrét tanács a kutatónak>",
  "locked": true
}
```
```
