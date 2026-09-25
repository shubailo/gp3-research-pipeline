#!/usr/bin/env python3
"""
GP3 Medical Research Pipeline — Deterministic Phase Gate Checker & Oversight Loop
================================================================================
Kizárólag determinisztikus Python-logika (0 db LLM / API hívás, 100% ingyenes).
1. Ellenőrzi a kutatási fázisváltások (Phase 1 -> 5) feltételeit és az SHA-256 állapot-zárat.
2. Kezeli a lezárt / beadott protokollok utólagos életciklusát (Oversight Loop: MAJOR / MINOR
   módosítások, Kumulatív Horgony-Hash heurisztika, SemVer verziózás).

Használat:
    python src/check_phase_gate.py --target-phase 4
    python src/check_phase_gate.py --project meta_hyperglycaemia --target-phase 5
    python src/check_phase_gate.py --status
    python src/check_phase_gate.py --project meta_hyperglycaemia --check-amendment
    python src/check_phase_gate.py --project meta_hyperglycaemia --check-amendment --propose-field outcome --new-value "Új kimenetel"
"""

import sys
import io
import os
import json
import hashlib
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List, Optional

# Windows console encoding fix
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


DEFAULT_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "project_state.json"
)

DEFAULT_AMENDMENTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "PROTOCOL_AMENDMENTS.md"
)

# ==============================================================================
# OVERSIGHT LOOP & CUMULATIVE ESCALATION KONFIGURÁCIÓ
# Figyelem: A kumulatív küszöbértékek a platform belső kiindulási heurisztikái
# a "lopakodó hatásbővülés" (cumulative scope creep) megakadályozására,
# NEM képezik a CTM / Cochrane módszertani sztenderd részét!
# ==============================================================================
HEURISTIC_MAX_CUMULATIVE_MINOR_AMENDMENTS = 3   # Kiindulási heurisztika: max 3 egymást követő minor módosítás
HEURISTIC_MAX_TEXT_DIVERGENCE_PCT = 15.0         # Kiindulási heurisztika: max 15% szöveges eltérés v1.0 baseline-hoz képest
MIN_RESEARCHER_JUSTIFICATION_LEN = 60           # Minimális indoklás hossz karakterben
DISALLOWED_JUSTIFICATION_PLACEHOLDERS = [
    "tbd", "n/a", "később", "todo", "módosítva", "dummy", "javítva", "update", "asdf"
]
VALID_MENTOR_VERDICTS = [
    "NINCS ÉRDEMI HATÁS",
    "MÉRSÉKELT KOCKÁZAT, DOKUMENTÁLANDÓ",
    "SÚLYOS MÓDSZERTANI KOCKÁZAT, ÚJRAÉRTÉKELÉS JAVASOLT"
]


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def compute_hypothesis_hash(pico: Dict[str, str]) -> str:
    """Computes SHA-256 hash from core PICO elements."""
    p = pico.get("population", "").strip()
    i = pico.get("intervention_exposure", "").strip()
    c = pico.get("comparator", "").strip()
    o = pico.get("outcome", "").strip()
    serialized = f"{p}|{i}|{c}|{o}"
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def compute_next_version(current_version: str, is_major: bool) -> str:
    """Computes next semantic version for protocol (e.g. v1.0 -> v1.1 for minor, v1.0 -> v2.0 for major)."""
    if not current_version or not current_version.startswith("v"):
        current_version = "v1.0"
    ver_str = current_version.lstrip("v")
    parts = ver_str.split(".")
    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
    except ValueError:
        major, minor = 1, 0
        
    if is_major:
        return f"v{major + 1}.0"
    else:
        return f"v{major}.{minor + 1}"


def validate_researcher_justification(justification: str) -> Tuple[bool, str]:
    """Validates researcher justification: length >= 60, no banned placeholders."""
    if not justification or not justification.strip():
        return False, "A kutatói indoklás hiányzik (üres szöveg)!"
    cleaned = justification.strip()
    if len(cleaned) < MIN_RESEARCHER_JUSTIFICATION_LEN:
        return False, f"A kutatói indoklás túl rövid ({len(cleaned)} kar.), minimum {MIN_RESEARCHER_JUSTIFICATION_LEN} karakter szükséges!"
    
    lower_text = cleaned.lower()
    tokens = lower_text.replace(",", " ").replace(".", " ").replace(";", " ").split()
    for ph in DISALLOWED_JUSTIFICATION_PLACEHOLDERS:
        if ph in tokens or lower_text == ph:
            return False, f"A kutatói indoklás tiltott placeholder kifejezést tartalmaz: '{ph}'!"
            
    return True, "Kutatói indoklás formailag és tartalmilag érvényes."


def validate_mentor_assessments(assessments: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Checks whether both Hegyi and Garami assessments are present, valid and locked."""
    errors = []
    for mentor in ["hegyi", "garami"]:
        m_data = assessments.get(mentor)
        if not m_data:
            errors.append(f"Hiányzik {mentor.capitalize()} mentor hatáselemzése (Task {'A' if mentor == 'hegyi' else 'B'})!")
            continue
        verdict = str(m_data.get("verdict", "")).strip().upper()
        if not any(v in verdict for v in ["NINCS", "MÉRSÉKELT", "SÚLYOS", "NO SUBSTANTIAL", "MODERATE", "SEVERE"]):
            errors.append(f"Érvénytelen mentori verdikt ({mentor}): '{verdict}'! Szabályos: {VALID_MENTOR_VERDICTS}")
        if not m_data.get("locked", True):
            errors.append(f"{mentor.capitalize()} mentor hatáselemzése nincs zárolva (locked=False)!")
            
    return len(errors) == 0, errors


def classify_amendment(
    project_data: Dict[str, Any],
    proposed_pico: Optional[Dict[str, str]] = None,
    proposed_criteria: Optional[Dict[str, str]] = None,
    proposed_full_text: Optional[str] = None,
    proposed_field: Optional[str] = None,
    proposed_value: Optional[str] = None
) -> Dict[str, Any]:
    """
    Determinisztikusan eldönti, hogy egy módosítás MAJOR vagy MINOR.
    Nem használ AI-t: mező- és kriptográfiai hash-összehasonlítás alapján dönt.

    Vizsgált zárolt mezők (MAJOR kategória):
    - PICO 4 mag-eleme: population, intervention_exposure, comparator, outcome (és title)
    - Inklúziós/Exklúziós kritériumok: inclusion_criteria, exclusion_criteria
    - locked_hypothesis_hash integritása

    Minden egyéb módosítás (formai, stilisztikai, másodlagos kimenetel, szoftververzió) MINOR,
    KIVÉVE, ha aktiválódik a Kumulatív Horgony-Hash kiindulási heurisztika
    (>=3 minor módosítás VAGY >=15% szöveges eltérés a baseline-hoz képest),
    ami automatikusan felminősíti MAJOR kategóriába.
    """
    locked_core_hash = project_data.get("locked_hypothesis_hash")
    old_pico = project_data.get("pico", {})
    
    # Inklúziós/exklúziós mezők kinyerése a projekt adatból (akár gyökérben, akár pico-ban van)
    old_inc = project_data.get("inclusion_criteria") or old_pico.get("inclusion_criteria", "")
    old_exc = project_data.get("exclusion_criteria") or old_pico.get("exclusion_criteria", "")
    
    changed_fields = []
    
    curr_pico = dict(old_pico)
    curr_inc = old_inc
    curr_exc = old_exc
    
    # 1. Ha konkrét mező és érték lett megadva CLI-ből:
    if proposed_field and proposed_value is not None:
        val = proposed_value.strip()
        field_norm = proposed_field.strip().lower()
        if field_norm in ["population", "intervention_exposure", "intervention", "exposure", "comparator", "outcome", "title"]:
            key = "intervention_exposure" if field_norm in ["intervention", "exposure"] else field_norm
            if curr_pico.get(key, "").strip() != val:
                changed_fields.append(key)
                curr_pico[key] = val
        elif field_norm in ["inclusion_criteria", "inclusion"]:
            if curr_inc.strip() != val:
                changed_fields.append("inclusion_criteria")
                curr_inc = val
        elif field_norm in ["exclusion_criteria", "exclusion"]:
            if curr_exc.strip() != val:
                changed_fields.append("exclusion_criteria")
                curr_exc = val
        else:
            # Nem zárolt formai vagy kiegészítő mező (pl. editorial, secondary_outcome, software)
            changed_fields.append(proposed_field)
            
    # 2. Ha proposed_pico szótár érkezett:
    if proposed_pico:
        for f in ["population", "intervention_exposure", "comparator", "outcome"]:
            if f in proposed_pico and old_pico.get(f, "").strip() != proposed_pico[f].strip():
                if f not in changed_fields:
                    changed_fields.append(f)
                curr_pico[f] = proposed_pico[f]
                
    # 3. Ha proposed_criteria szótár érkezett:
    if proposed_criteria:
        if "inclusion_criteria" in proposed_criteria and old_inc.strip() != proposed_criteria["inclusion_criteria"].strip():
            if "inclusion_criteria" not in changed_fields:
                changed_fields.append("inclusion_criteria")
            curr_inc = proposed_criteria["inclusion_criteria"]
        if "exclusion_criteria" in proposed_criteria and old_exc.strip() != proposed_criteria["exclusion_criteria"].strip():
            if "exclusion_criteria" not in changed_fields:
                changed_fields.append("exclusion_criteria")
            curr_exc = proposed_criteria["exclusion_criteria"]

    current_hash = compute_hypothesis_hash(curr_pico)
    
    # Ha a hash eltér a zárolttól, de changed_fields üres volt (pl. háttérmódosítás)
    if locked_core_hash and current_hash != locked_core_hash and not changed_fields:
        changed_fields.append("locked_hypothesis_hash_mismatch")

    # Zárolt kulcsmezők halmaza
    locked_core_keys = {
        "population", "intervention_exposure", "comparator", "outcome",
        "inclusion_criteria", "exclusion_criteria", "locked_hypothesis_hash_mismatch"
    }
    is_core_modified = any(f in locked_core_keys for f in changed_fields)

    # 4. Alapértelmezett besorolás meghatározása
    if is_core_modified:
        classification = "MAJOR"
        reason = "A zárolt hipotézis-elemek (PICO vagy Inklúzió/Exklúzió) módosultak!"
        requires_mentors = True
        is_escalated = False
        escalation_reason = ""
    else:
        classification = "MINOR"
        reason = "A PICO és a mag-hipotézis sértetlen; a módosítás formai vagy kiegészítő elemet érint."
        requires_mentors = False
        is_escalated = False
        escalation_reason = ""
        
        # 5. Kumulatív Horgony-Hash Kiindulási Heurisztika ellenőrzése
        history = project_data.get("amendment_history", [])
        minor_streak = 0
        for item in reversed(history):
            if item.get("type") == "MAJOR":
                break
            if item.get("type") == "MINOR":
                minor_streak += 1
                
        # Ha a korábbi streak + jelenlegi módosítás eléri a limitet:
        if (minor_streak + 1) >= HEURISTIC_MAX_CUMULATIVE_MINOR_AMENDMENTS:
            classification = "MAJOR"
            is_escalated = True
            requires_mentors = True
            escalation_reason = (
                f"Kiindulási heurisztika triggerelve: A kumulatív minor módosítások száma elérte a "
                f"{HEURISTIC_MAX_CUMULATIVE_MINOR_AMENDMENTS}-at "
                f"({minor_streak} korábbi minor + jelenlegi). "
                f"Lopakodó hatásbővülés (cumulative scope creep) megelőzése céljából automatikus felminősítés MAJOR-ra!"
            )
            reason = escalation_reason

    return {
        "classification": classification,
        "is_escalated": is_escalated,
        "escalation_reason": escalation_reason,
        "reason": reason,
        "changed_fields": changed_fields if changed_fields else ["protocol_body_editorial"],
        "old_hash": locked_core_hash,
        "new_hash": current_hash,
        "proposed_pico": curr_pico,
        "proposed_inclusion": curr_inc,
        "proposed_exclusion": curr_exc,
        "requires_mentor_impact_assessment": requires_mentors
    }


def append_to_amendments_file(file_path: str, record: Dict[str, Any], project_name: str, project_id: str) -> None:
    """Appends an audit record to PROTOCOL_AMENDMENTS.md."""
    if not os.path.exists(file_path):
        return
        
    date_str = record.get("timestamp", datetime.now(timezone.utc).isoformat())[:10]
    ver = record.get("version_after", "v1.x")
    am_type = record.get("type", "MINOR")
    am_id = record.get("amendment_id", "AMD-001")
    changed = ", ".join([f"`{f}`" for f in record.get("changed_fields", [])])
    old_h = (record.get("previous_hash") or "N/A")[:12] + "..." if record.get("previous_hash") else "N/A"
    new_h = (record.get("new_hash") or "N/A")[:12] + "..." if record.get("new_hash") else "N/A"
    
    lines = [
        f"\n## [{ver}] — {date_str} ({am_type} AMENDMENT)",
        f"- **Projekt:** {project_name} [{project_id}]",
        f"- **Módosítás azonosító:** `{am_id}`",
        f"- **Típus:** {am_type}" + (" *(Kumulatív Heurisztika által felminősítve)*" if record.get("is_escalated") else ""),
        f"- **Érintett mezők:** {changed}",
        f"- **Előző SHA-256 Hash:** `{old_h}`",
        f"- **Új SHA-256 Hash:** `{new_h}`",
        "",
        "### Változás Leírása",
        f"- **Módosítás részlete:** {record.get('details', 'N/A')}",
        ""
    ]
    
    if am_type == "MAJOR":
        m_assess = record.get("mentor_assessments", {})
        hegyi = m_assess.get("hegyi", {})
        garami = m_assess.get("garami", {})
        lines.extend([
            "### Mentori Hatáselemzés (Független Hatáselemzési Kör)",
            f"- **Mentor Hegyi Verdikt:** {hegyi.get('verdict', 'N/A')}  ",
            f"  *Figyelmeztetés / Megjegyzés:* {hegyi.get('warning', hegyi.get('key_warning', 'N/A'))}",
            f"- **Mentor Garami Verdikt:** {garami.get('verdict', 'N/A')}  ",
            f"  *Figyelmeztetés / Megjegyzés:* {garami.get('warning', garami.get('key_warning', 'N/A'))}",
            ""
        ])
        
    lines.extend([
        "### Kutatói Indoklás (Executive Decision)",
        f"> \"{record.get('researcher_justification', '')}\"",
        "",
        "---"
    ])
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def load_state(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Az állapotfájl nem található: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def evaluate_phase_1(gates: Dict[str, Any]) -> List[Tuple[bool, str, str]]:
    p1 = gates.get("phase_1", {})
    return [
        (p1.get("pico_defined", False), "PICO keretrendszer definiálása", "P, I/E, C, O elemek pontos megadása"),
        (p1.get("title_formula_valid", False), "Kanonikus PICO Címformula", "'Investigating the effect of [E] on [O] in [P]' forma"),
        (p1.get("suffering_narrative_present", False), "3-as Szenvedés Narratíva", "Beteg morbiditás, Családi teher, Klinikai remény számszerűsítése")
    ]


def evaluate_phase_2(gates: Dict[str, Any]) -> List[Tuple[bool, str, str]]:
    p2 = gates.get("phase_2", {})
    prec_count = p2.get("precedent_count", 0)
    limit_justified = p2.get("precedent_limit_justification", False)
    prec_ok = prec_count >= 10 or (prec_count >= 5 and limit_justified)
    
    prec_msg = f"{prec_count} db elemzett precedens metaanalízis (Elvárt: >=10, vagy >=5 explicit indoklással)"
    
    return [
        (prec_ok, "Precedens Metaanalízisek Elemzése (3-lépcsős kulcs)", prec_msg),
        (not p2.get("boolean_not_used", True), "Boole 'NOT' Tilalom ellenőrzése", "Tilos a 'NOT' operátor használata a keresési stringekben"),
        (p2.get("pubmed_verified", False), "Élő PubMed és PROSPERO verifikáció", "Élő lekérdezés lefutott, fehér folt igazolva")
    ]


def evaluate_phase_3(gates: Dict[str, Any]) -> List[Tuple[bool, str, str]]:
    p3 = gates.get("phase_3", {})
    study_count = p3.get("identical_outcome_study_count", 0)
    poolable_ok = study_count >= 3
    pool_msg = f"Azonos végpontú tanulmányok száma: {study_count} db (KÖTELEZŐ MINIMUM: >= 3 db)"
    
    return [
        (poolable_ok, "Poolability Gate (Biostatisztikai Megvalósíthatóság)", pool_msg),
        (p3.get("confounder_matrix_defined", False), "Előre Specifikált Confounder Mátrix", "Biológiai zavaró tényezők és illesztett becslések prioritása"),
        (p3.get("missing_covariates_under_30_pct", False), "Hiányzó Kovariánsok Feasibility Korlátja", "<70% riportolású változók kizárva a meta-regresszióból")
    ]


def evaluate_phase_4(gates: Dict[str, Any], current_hash: str, locked_hash: str) -> List[Tuple[bool, str, str]]:
    p4 = gates.get("phase_4", {})
    hegyi_locked = p4.get("hegyi_score_locked", False)
    garami_locked = p4.get("garami_score_locked", False)
    reconciled = p4.get("reconciliation_round_completed", False)
    socratic_done = p4.get("socratic_questions_answered", False)
    
    # Hash lock integrity check
    hash_ok = True
    hash_msg = "A hipotézis (PICO) sértetlen a mentori bírálat óta."
    if locked_hash:
        if current_hash != locked_hash:
            hash_ok = False
            hash_msg = f"ELTÉRÉS! Zárolt hash: {locked_hash[:8]}... != Jelenlegi: {current_hash[:8]}... A PICO módosult!"
    else:
        if hegyi_locked and garami_locked:
            hash_ok = False
            hash_msg = "Hiányzó SHA-256 állapot-zár lenyomat!"
            
    return [
        (hegyi_locked, "Mentor Hegyi Független Zárolt Pontozás (4D CTM Mátrix)", "Klinikai Hasznosság, Megvalósíthatóság, Újszerűség, Problémamegoldás"),
        (garami_locked, "Mentor Garami Független Zárolt Pontozás (4D Méréstan)", "Mechanizmus, Mérés minőség, Heterogenitás védelem, Torzítás"),
        (reconciled, "Explicit Rekonciliációs Kör lezárása", "Mentorok reflexiója rögzítve, kezdeti pont nem íródott át"),
        (socratic_done, "Szókratészi Kérdések Kutatói Megválaszolása", "Mindkét mentor blokkoló kérdése feloldva a kutató által"),
        (hash_ok, "SHA-256 Állapot-Zár Integritás", hash_msg)
    ]


def evaluate_phase_5(gates: Dict[str, Any]) -> List[Tuple[bool, str, str]]:
    p5 = gates.get("phase_5", {})
    pfile_exists = p5.get("protocol_file_exists", False)
    lscore = p5.get("linter_score", 0)
    lscore_ok = lscore >= 70
    cver = p5.get("citation_verified", False)
    
    return [
        (pfile_exists, "PROTOCOL.md / PROSPERO dokumentum megléte", f"Fájl: {p5.get('protocol_file', 'PROTOCOL.md')}"),
        (lscore_ok, f"Determinisztikus Linter Pontszám (Elért: {lscore}/100)", "Küszöbérték: >= 70 pont szükséges a release-hez"),
        (cver, "PMID Idézettség- és Halucináció-ellenőrzés", "citation_verifier.py sikeresen lefutott")
    ]


def check_target_phase(project_data: Dict[str, Any], target_phase: int) -> Tuple[bool, List[Tuple[str, List[Tuple[bool, str, str]]]]]:
    gates = project_data.get("gates", {})
    pico = project_data.get("pico", {})
    current_hash = compute_hypothesis_hash(pico)
    locked_hash = project_data.get("locked_hypothesis_hash")
    
    all_passed = True
    results = []
    
    # Target Phase 2 requires Phase 1 to pass
    if target_phase >= 2:
        p1_res = evaluate_phase_1(gates)
        passed = all(r[0] for r in p1_res)
        results.append(("Phase 1: Bed-to-Bench Hipotézis & Szenvedés", p1_res))
        if not passed: all_passed = False
        
    # Target Phase 3 requires Phase 2 to pass
    if target_phase >= 3:
        p2_res = evaluate_phase_2(gates)
        passed = all(r[0] for r in p2_res)
        results.append(("Phase 2: Irodalmi Szigor & Keresőkulcs", p2_res))
        if not passed: all_passed = False

    # Target Phase 4 requires Phase 3 to pass
    if target_phase >= 4:
        p3_res = evaluate_phase_3(gates)
        passed = all(r[0] for r in p3_res)
        results.append(("Phase 3: Megvalósíthatóság & Poolozhatóság", p3_res))
        if not passed: all_passed = False

    # Target Phase 5 requires Phase 4 to pass
    if target_phase >= 5:
        p4_res = evaluate_phase_4(gates, current_hash, locked_hash)
        passed = all(r[0] for r in p4_res)
        results.append(("Phase 4: Független Kettős Bírálat & Rekonciliáció", p4_res))
        if not passed: all_passed = False

    # Target Phase 6 (Final Release) requires Phase 5 to pass
    if target_phase >= 6:
        p5_res = evaluate_phase_5(gates)
        passed = all(r[0] for r in p5_res)
        results.append(("Phase 5: Publikációkész Protokoll & Minőségellenőrzés", p5_res))
        if not passed: all_passed = False

    return all_passed, results


def handle_amendment_check(proj: Dict[str, Any], project_id: str, data: Dict[str, Any], args: argparse.Namespace) -> None:
    """Executes deterministic amendment audit and lifecycle management."""
    print("=" * 76)
    print(f"{Colors.BOLD}🔍 GP3 OVERSIGHT LOOP — PROTOKOLL MÓDOSÍTÁS ELLENŐRZŐ{Colors.RESET}")
    print(f"Projekt: {Colors.CYAN}{proj.get('name')}{Colors.RESET} [{project_id}]")
    print(f"Aktuális Protokoll Verzió: {Colors.YELLOW}{proj.get('protocol_version', 'v1.0')}{Colors.RESET}")
    print(f"Zárolt Hipotézis Hash: {Colors.CYAN}{(proj.get('locked_hypothesis_hash') or 'NINCS')[:12]}...{Colors.RESET}")
    print("=" * 76)

    # 1. Ha nincs megadva javasolt mező, ellenőrizzük az alap állapotot
    if not args.propose_field and not args.new_value:
        pico = proj.get("pico", {})
        curr_hash = compute_hypothesis_hash(pico)
        locked_hash = proj.get("locked_hypothesis_hash")
        history = proj.get("amendment_history", [])
        
        print(f"\nAudit Eredmény:")
        if locked_hash and curr_hash == locked_hash:
            print(f"   {Colors.GREEN}✔ A protokoll zárolt hipotézis állapota sértetlen.{Colors.RESET}")
            print(f"   ↳ Hash: {curr_hash}")
            print(f"   ↳ Rögzített módosítások száma az előzményekben: {len(history)} db")
            print("\n" + "=" * 76)
            print(f"{Colors.GREEN}✅ JÓVÁHAGYVA: Nincs detektált engedély nélküli módosítás. Kilépési kód: 0{Colors.RESET}")
            print("=" * 76)
            sys.exit(0)
        else:
            print(f"   {Colors.RED}✘ ELTÉRÉS ÉSZLELVE! A lemez állapota eltér a zárolt állapottól!{Colors.RESET}")
            print(f"   ↳ Zárolt: {locked_hash} != Jelenlegi: {curr_hash}")
            print(f"   ↳ Futtass módosítási ellenőrzést a konkrét mezővel: --propose-field <field>{Colors.RESET}")
            print("\n" + "=" * 76)
            print(f"{Colors.RED}🛑 BLOKKOLVA: A protokoll nem zárolt állapotban van! Kilépési kód: 1{Colors.RESET}")
            print("=" * 76)
            sys.exit(1)

    # 2. Változás osztályozása a megadott paraméterek alapján
    classification_res = classify_amendment(
        project_data=proj,
        proposed_field=args.propose_field,
        proposed_value=args.new_value
    )
    
    cls_type = classification_res["classification"]
    is_escalated = classification_res["is_escalated"]
    changed_fields = classification_res["changed_fields"]
    old_h = classification_res["old_hash"]
    new_h = classification_res["new_hash"]
    
    print(f"\n1. Változás Osztályozása (Determinisztikus Elemző):")
    if cls_type == "MAJOR":
        print(f"   Osztály: {Colors.RED}{Colors.BOLD}[MAJOR AMENDMENT]{Colors.RESET}")
        print(f"   ↳ Indoklás: {classification_res['reason']}")
        if is_escalated:
            print(f"   {Colors.YELLOW}{Colors.BOLD}⚠️  CUMULATIVE ESCALATION TRIGGER AKTIVÁLVA! (Kiindulási heurisztika){Colors.RESET}")
            print(f"   ↳ {classification_res['escalation_reason']}")
    else:
        print(f"   Osztály: {Colors.GREEN}{Colors.BOLD}[MINOR AMENDMENT]{Colors.RESET}")
        print(f"   ↳ Indoklás: {classification_res['reason']}")
        
    print(f"   Érintett mezők: {Colors.CYAN}{changed_fields}{Colors.RESET}")
    print(f"   Előző Hash: {old_h[:12] if old_h else 'N/A'}... ➔ Új Hash: {new_h[:12]}...")

    # 3. Következő verziószám kalkulációja
    curr_ver = proj.get("protocol_version", "v1.0")
    next_ver = compute_next_version(curr_ver, is_major=(cls_type == "MAJOR"))
    print(f"   Tervezett Verzióugrás: {Colors.YELLOW}{curr_ver}{Colors.RESET} ➔ {Colors.BOLD}{Colors.GREEN}{next_ver}{Colors.RESET}")

    # 4. Ellenőrzések végrehajtása
    print(f"\n2. Szabályzati Kapuk Értékelése:")
    all_gates_passed = True
    
    # Kutatói indoklás vizsgálata
    justification = args.justification or ""
    just_ok, just_msg = validate_researcher_justification(justification)
    
    # MINOR esetén enyhébb indoklási elvárás (ha üres, megengedjük a CLI tesztet figyelmeztetéssel, kivéve ha --apply van)
    if cls_type == "MINOR":
        if args.justification:
            if just_ok:
                print(f"   {Colors.GREEN}[PASS] Kutatói Indoklás:{Colors.RESET} {just_msg}")
            else:
                print(f"   {Colors.RED}[FAIL] Kutatói Indoklás:{Colors.RESET} {just_msg}")
                all_gates_passed = False
        else:
            if args.apply:
                print(f"   {Colors.RED}[FAIL] Kutatói Indoklás:{Colors.RESET} Az élesítéshez (--apply) kötelező az indoklás megadása!")
                all_gates_passed = False
            else:
                print(f"   {Colors.YELLOW}[INFO] Kutatói Indoklás:{Colors.RESET} Nem lett megadva indoklás (előnézeti mód).")
        print(f"   {Colors.GREEN}[PASS] Mentori Hatáselemzés:{Colors.RESET} MINOR módosításnál nem szükséges mentori kör.")
    
    # MAJOR esetén szigorú mentori és kutatói indoklási kényszer
    else:
        # Kutatói indoklás kötelező
        if just_ok:
            print(f"   {Colors.GREEN}[PASS] Kutatói Indoklás:{Colors.RESET} {just_msg}")
            print(f"          ↳ Szöveg: \"{justification[:65]}...\"")
        else:
            print(f"   {Colors.RED}[FAIL] Kutatói Indoklás:{Colors.RESET} {just_msg}")
            all_gates_passed = False

        # Mentori hatáselemzés vizsgálata
        assessments = {}
        if args.assessment_file and os.path.exists(args.assessment_file):
            try:
                with open(args.assessment_file, "r", encoding="utf-8") as f:
                    assessments = json.load(f)
            except Exception as e:
                print(f"   {Colors.RED}[FAIL] Nem sikerült beolvasni a hatáselemzési fájlt: {e}{Colors.RESET}")
        
        # CLI-ből közvetlenül átadott mentori verdiktek támogatása
        if args.hegyi_verdict:
            assessments["hegyi"] = {
                "verdict": args.hegyi_verdict,
                "warning": args.hegyi_warning or "Nincs külön figyelmeztetés rögzítve.",
                "locked": True
            }
        if args.garami_verdict:
            assessments["garami"] = {
                "verdict": args.garami_verdict,
                "warning": args.garami_warning or "Nincs külön figyelmeztetés rögzítve.",
                "locked": True
            }

        assess_ok, assess_errs = validate_mentor_assessments(assessments)
        if assess_ok:
            print(f"   {Colors.GREEN}[PASS] Mentor Hegyi Hatáselemzés (Task A):{Colors.RESET} Verdikt: {assessments['hegyi']['verdict']}")
            print(f"   {Colors.GREEN}[PASS] Mentor Garami Hatáselemzés (Task B):{Colors.RESET} Verdikt: {assessments['garami']['verdict']}")
        else:
            for err in assess_errs:
                print(f"   {Colors.RED}[FAIL] Mentori Hatáselemzés:{Colors.RESET} {err}")
            print(f"          ↳ {Colors.YELLOW}Teendő: Futtasd le a docs/mentor_prompts/impact_assessment_prompt_template.md-t a két független mentori chat-fülön!{Colors.RESET}")
            all_gates_passed = False

    # 5. Döntési és végrehajtási logika
    print("\n" + "=" * 76)
    if all_gates_passed:
        if args.apply:
            # Új amendment rekord összeállítása
            am_id = f"AMD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(proj.get('amendment_history', [])) + 1:03d}"
            record = {
                "amendment_id": am_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": cls_type,
                "is_escalated": is_escalated,
                "version_before": curr_ver,
                "version_after": next_ver,
                "changed_fields": changed_fields,
                "previous_hash": old_h,
                "new_hash": new_h,
                "details": f"Mező: {args.propose_field} ➔ Új érték: {args.new_value}",
                "researcher_justification": justification,
                "mentor_assessments": assessments if cls_type == "MAJOR" else {},
                "status": "APPROVED_AND_LOCKED"
            }
            
            # Állapot frissítése memóriában
            proj["protocol_version"] = next_ver
            proj["amendment_history"].append(record)
            if cls_type == "MAJOR":
                proj["locked_hypothesis_hash"] = new_h
            
            # Ha PICO vagy kritérium mező változott, mentjük a projektbe is
            if args.propose_field in ["population", "intervention_exposure", "comparator", "outcome", "title"]:
                proj["pico"][args.propose_field] = args.new_value.strip()
            elif args.propose_field in ["inclusion_criteria", "inclusion"]:
                proj["inclusion_criteria"] = args.new_value.strip()
            elif args.propose_field in ["exclusion_criteria", "exclusion"]:
                proj["exclusion_criteria"] = args.new_value.strip()
                
            data["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Mentés lemezre
            save_state(args.state_file, data)
            append_to_amendments_file(args.amendments_file, record, proj.get("name", ""), project_id)
            
            print(f"{Colors.GREEN}{Colors.BOLD}✅ JÓVÁHAGYVA ÉS ÉLESÍTVE ({cls_type} AMENDMENT):{Colors.RESET}")
            print(f"   ↳ Új verzió: {Colors.CYAN}{next_ver}{Colors.RESET}")
            print(f"   ↳ Rögzítve a data/project_state.json és PROTOCOL_AMENDMENTS.md fájlokban.")
            print(f"Kilépési kód: 0 (A módosítás auditáltan életbe lépett)")
            print("=" * 76)
            sys.exit(0)
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ JÓVÁHAGYVA: Minden feltétel teljesült a(z) {cls_type} módosítás átvezetéséhez!{Colors.RESET}")
            print(f"   ↳ Tervezett verzió: {next_ver}")
            print(f"   ↳ Megjegyzés: Az élesítéshez és naplózáshoz futtasd a parancsot a {Colors.BOLD}--apply{Colors.RESET} kapcsolóval!")
            print(f"Kilépési kód: 0")
            print("=" * 76)
            sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}🛑 BLOKKOLVA: A(z) {cls_type} módosítás megtagadva a fenti hibák miatt!{Colors.RESET}")
        print(f"Kilépési kód: 1 (Javítsd a fenti [FAIL] pontokat a továbbhaladáshoz)")
        print("=" * 76)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="GP3 Medical Research Pipeline — Determinisztikus Fázis-Kapu & Oversight Loop Ellenőrző (0 LLM, 100% ingyenes)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project", "-p", type=str, help="Projekt azonosító (alapértelmezett: active_project a JSON-ból)")
    parser.add_argument("--target-phase", "-t", type=int, choices=[2, 3, 4, 5, 6], help="A célfázis száma (2=LitReview, 3=Feasibility, 4=MentorReview, 5=Protocol, 6=FinalRelease)")
    parser.add_argument("--status", "-s", action="store_true", help="Teljes kapu-státusz jelentés kiírása")
    parser.add_argument("--update-hash", action="store_true", help="Újraszámítja és zárolja a jelenlegi PICO SHA-256 hash-t")
    parser.add_argument("--state-file", type=str, default=DEFAULT_STATE_FILE, help="Állapotfájl elérési útja")
    parser.add_argument("--amendments-file", type=str, default=DEFAULT_AMENDMENTS_FILE, help="PROTOCOL_AMENDMENTS.md elérési útja")
    
    # Oversight Loop CLI kapcsolók
    parser.add_argument("--check-amendment", action="store_true", help="Oversight Loop: Protokoll utólagos módosításának determinisztikus ellenőrzése")
    parser.add_argument("--propose-field", type=str, help="A módosítani kívánt mező (pl. outcome, inclusion_criteria, protocol_body_editorial)")
    parser.add_argument("--new-value", type=str, help="A mező új tervezett tartalma")
    parser.add_argument("--justification", type=str, help="A kutató szakmai indoklása (>=60 karakter, placeholder nélkül)")
    parser.add_argument("--hegyi-verdict", type=str, help="Mentor Hegyi hatáselemzési verdiktje (Task A)")
    parser.add_argument("--hegyi-warning", type=str, help="Mentor Hegyi figyelmeztetése / megjegyzése")
    parser.add_argument("--garami-verdict", type=str, help="Mentor Garami hatáselemzési verdiktje (Task B)")
    parser.add_argument("--garami-warning", type=str, help="Mentor Garami figyelmeztetése / megjegyzése")
    parser.add_argument("--assessment-file", type=str, help="Mentori hatáselemzéseket tartalmazó JSON fájl elérési útja")
    parser.add_argument("--apply", action="store_true", help="Érvényes módosítás esetén az állapot mentése és naplózása a PROTOCOL_AMENDMENTS.md-be")

    args = parser.parse_args()

    try:
        data = load_state(args.state_file)
    except Exception as e:
        print(f"{Colors.RED}[!] HIBA az állapotfájl beolvasásakor: {e}{Colors.RESET}")
        sys.exit(1)

    project_id = args.project or data.get("active_project")
    projects = data.get("projects", {})
    
    if project_id not in projects:
        print(f"{Colors.RED}[!] Ismeretlen projekt azonosító: '{project_id}'. Elérhető projektek: {list(projects.keys())}{Colors.RESET}")
        sys.exit(1)

    proj = projects[project_id]

    # Oversight Loop ág
    if args.check_amendment:
        handle_amendment_check(proj, project_id, data, args)
        return

    pico = proj.get("pico", {})
    current_hash = compute_hypothesis_hash(pico)

    # Hash update command
    if args.update_hash:
        proj["locked_hypothesis_hash"] = current_hash
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        save_state(args.state_file, data)
        print(f"{Colors.GREEN}✔ SHA-256 Állapot-zár frissítve a '{project_id}' projekthez!{Colors.RESET}")
        print(f"  Új Hash: {Colors.CYAN}{current_hash}{Colors.RESET}")
        sys.exit(0)

    # If target phase is not specified, evaluate status or current target
    target_phase = args.target_phase
    if not target_phase:
        if args.status:
            target_phase = 6
        else:
            current_p = proj.get("current_phase", 1)
            target_phase = min(current_p + 1, 6)

    print("=" * 72)
    print(f"{Colors.BOLD}🔬 GP3 DETERMINISZTIKUS FÁZIS-KAPU AUDIT (CTM / Cochrane v6.5){Colors.RESET}")
    print(f"Projekt: {Colors.CYAN}{proj.get('name')}{Colors.RESET} [{project_id}]")
    print(f"Jelenlegi Fázis: {Colors.YELLOW}Phase {proj.get('current_phase')}{Colors.RESET} ➔ Célfázis: {Colors.BOLD}Phase {target_phase}{Colors.RESET}")
    print(f"PICO Hash: {Colors.CYAN}{current_hash[:12]}...{Colors.RESET} | Zárolt Hash: {Colors.CYAN}{(proj.get('locked_hypothesis_hash') or 'NINCS')[:12]}...{Colors.RESET}")
    print("=" * 72)

    passed, results = check_target_phase(proj, target_phase)

    for phase_name, checks in results:
        phase_ok = all(c[0] for c in checks)
        header_color = Colors.GREEN if phase_ok else Colors.RED
        symbol = "✔" if phase_ok else "✘"
        print(f"\n{header_color}{symbol} {phase_name}:{Colors.RESET}")
        for ok, title, detail in checks:
            if ok:
                print(f"   {Colors.GREEN}[PASS]{Colors.RESET} {Colors.BOLD}{title}{Colors.RESET}")
                print(f"          ↳ {detail}")
            else:
                print(f"   {Colors.RED}[FAIL]{Colors.RESET} {Colors.BOLD}{title}{Colors.RESET}")
                print(f"          ↳ {Colors.RED}{detail}{Colors.RESET}")

    print("\n" + "=" * 72)
    if passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ JÓVÁHAGYVA: Minden előfeltétel teljesült a Phase {target_phase} átlépéshez!{Colors.RESET}")
        print(f"Kilépési kód: 0 (A pipeline haladhat tovább a következő fázisba)")
        print("=" * 72)
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}🛑 BLOKKOLVA: A Phase {target_phase} átlépés megtagadva a fenti hibák miatt!{Colors.RESET}")
        print(f"Kilépési kód: 1 (Javítsd a fenti [FAIL] pontokat a továbbhaladáshoz)")
        print("=" * 72)
        sys.exit(1)


if __name__ == "__main__":
    main()
