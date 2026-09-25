# Researcher Dóri — GP3 Medical Research Pipeline Architecture

> Elite Academic Medical Research AI System — Centre for Translational Medicine (CTM) Standards

---

## 📋 Overview

This workspace implements a **6-Agent GP3 Medical Research Pipeline** designed to take any new research idea through a rigorous, publication-ready protocol development process — from initial brainstorm to PROSPERO-quality academic protocol.

```
New Idea
   ↓
/brainstorm  →  Idea validation, novelty check, Mentor verdicts
   ↓
/feasibility →  Live PubMed search, poolability gate, Go/No-Go verdict
   ↓
/plan        →  6-Agent orchestration, plan file (PLAN-{slug}.md)
   ↓
/research    →  Full 5-phase pipeline: PICO, Literature, Feasibility, Mentor Debate, PROTOCOL.md
   ↓
validate_protocol.py  →  7-gate CTM compliance linter (score 0-100)
screen_literature.py  →  PRISMA 2020 automated screening engine
```

---

## 🤖 The 6 Core Research Agents

| Agent | Role | Key Rules Enforced |
|-------|------|--------------------|
| `research-sage` | Principal Investigator & Study Design | PICO Title Formula, Suffering Narrative, T1-T4 Stage, FINER |
| `lit-reviewer` | Systematic Search Expert | 6-Point Background Check, 3-Step Search Key, NOT Ban, PROSPERO check |
| `feasibility-judge` | Operational & Ethical Evaluator | Missing Variable Audit, Ecological Bias, Poolability collaboration |
| `meta-analyzer` | Biostatistics & Synthesis | Poolability Rule (≥3 studies), Confounder Matrix, QUIPS/RoB 2/ROBINS-I, RVE |
| `mentor-hegyi` | Translational Medicine Mentor | SAP, Suffering Narrative, Avoidable Mortality, 1-10 Clinical Matrix |
| `mentor-garami` | Physiological Conscience | Sensor-Pathway-Effector Triad, COIN, Fever vs Hyperthermia, 1-10 Method Matrix |

---

## 🔄 Workflows (Slash Commands)

| Command | Description | Primary Agents |
|---------|-------------|----------------|
| `/brainstorm` | Generate 3-5 validated research ideas + Mentor verdict | research-sage, mentor-hegyi, mentor-garami |
| `/feasibility` | White-spot check + live PubMed search + Go/No-Go | lit-reviewer, meta-analyzer, feasibility-judge |
| `/plan` | Create full plan file (PLAN-{slug}.md) via 6-agent pipeline | All 6 agents |
| `/research` | Full 5-phase research orchestration → PROTOCOL.md | All 6 agents |
| `/orchestrate` | Multi-agent coordination for complex tasks | Variable |
| `/debug` | Debug issues in scripts or analysis pipelines | debugger, explorer-agent |
| `/status` | Check project status and open tasks | project-planner |
| `/preview` | Local dev server management | N/A |

---

## 🛠️ Automation Scripts

| Script | Location | Purpose | Usage |
|--------|----------|---------|-------|
| `validate_protocol.py` | `.agent/scripts/` & `src/` | 7-Gate CTM Protocol Compliance Linter (score 0-100) | `python src/validate_protocol.py PROTOCOL.md` |
| `screen_literature.py` | `src/` | PRISMA 2020 Automated Literature Screening | `python src/screen_literature.py --from-file results/search.json --p-terms "..."` |
| `literature_search.py` | `src/` | Live PubMed + Cochrane search with white-spot analysis | `python src/literature_search.py "QUERY" --analyze --max-results 100` |
| `white_spot_analyzer.py` | `src/` | Quantitative trend analysis + abstract digest builder | Used internally by literature_search.py |

---

## 📐 The 7 GP3 Compliance Gates (`validate_protocol.py`)

| Gate | Rule | Max Points |
|------|------|-----------|
| 1 | PICO Title Formula: *"Investigating the effect of [E] on [O] in [P]"* | 15 |
| 2 | The Suffering Narrative: Patient, Family, Clinical Hope | 15 |
| 3 | 6-Point Quantitative Background: Incidence, Mortality %, etc. | 15 |
| 4 | Search Key Syntax: 3-domain, NO Boolean NOT | 10 |
| 5 | Feasibility Poolability: ≥3 primary studies with identical outcome | 15 |
| 6 | Methodological Rigor: RoB 2/QUIPS/ROBINS-I + Confounder Matrix + RVE | 15 |
| 7 | Translational Impact: Explicit T1-T4 stage + Avoidable Mortality | 15 |

Scores ≥70/100 = APPROVED. Scores <70/100 = REJECTED (address red gates first).

---

## 🔬 The 5-Phase `/research` Orchestration Pipeline

```
PHASE 1 (research-sage + mentor-hegyi)
→ PICO architecture, Title Formula, Suffering Narrative, T1-T4 declaration

PHASE 2 (lit-reviewer)
→ 6-Point Background, 3-Step Search Key, PROSPERO novelty check

PHASE 3 (feasibility-judge + meta-analyzer)
→ Poolability Gate, Confounder Matrix, RoB tooling, Sensor-Pathway-Effector audit

PHASE 4 (mentor-hegyi ↔ mentor-garami DIALECTICAL DEBATE)
→ Round 1: Clinical vs. Mechanistic Critique
→ Round 2: Cross-Talk Tension
→ Joint Socratic Gate (blocking questions)

PHASE 5 (upon Socratic Gate clearance)
→ Compile PROTOCOL.md (10 sections, PROSPERO-ready)
→ Run: python src/validate_protocol.py PROTOCOL.md
```

---

## 📁 Key Directory Structure

```plaintext
Researcher - Dóri/
├── .agent/
│   ├── ARCHITECTURE.md          # This file
│   ├── agents/                  # 6 Core GP3 Research Agents + support agents
│   ├── workflows/               # Slash command procedures
│   ├── scripts/                 # validate_protocol.py, session_manager.py
│   ├── rules/                   # GEMINI.md workspace rules
│   └── skills/                  # Modular knowledge domains
├── src/                         # Executable Python pipeline scripts
│   ├── literature_search.py     # Live PubMed/Cochrane search
│   ├── screen_literature.py     # PRISMA 2020 Screening Engine
│   ├── white_spot_analyzer.py   # Trend & abstract analysis
│   └── validate_protocol.py    # Protocol compliance linter (copy)
├── TM/                          # Translational Medicine methodology docs
│   ├── META_ANALYSIS_BRAINSTORMING_SKILL.md
│   ├── Cochrane-Handbook-v6.5.MD
│   └── [12 other methodological guides]
├── agents/                      # Root agents (legacy mirror — primary in .agent/agents/)
├── results/                     # Search JSON outputs, screening CSVs
├── meta_hyperglycaemia/         # Real active meta-analysis project
├── PROTOCOL.md                  # Current working research protocol
└── docs/                        # PLAN-{slug}.md plan files
```

---

## 🏁 GP3 Mandatory Rule Chain (Priority Order)

```
P0: GEMINI.md (workspace global rules — always active)
P1: Agent .md files (mentor-hegyi, mentor-garami, etc.)
P2: TM/ skill files (META_ANALYSIS_BRAINSTORMING_SKILL.md, Cochrane-Handbook)
P3: Workflow .md files (/research, /brainstorm, /plan, /feasibility)
```

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Core Research Agents** | 6 |
| **Total Agents** | 14 (.agent/agents/) |
| **GP3 Compliance Gates** | 7 |
| **Workflow Commands** | 8 |
| **Automation Scripts** | 4 |
| **TM Methodology Docs** | 14 |
