# SAOS — Security Assessment Operating System

**Version:** v0.1 (Phase 0 foundations + Server Security pilot)
**Status:** Pilot complete. 1 of 18 domains built (60 of 905 target controls).
**Last build:** 2026-10-04
**Canonical source of truth:** `artefacts/06-source/library/` (YAML)

SAOS is a vendor-neutral, framework-driven toolkit for running cybersecurity
posture assessments for client engagements. It replaces the usual pile of
spreadsheet checklists with three things:

1. a **versioned control library** in plain text that can be reviewed, diffed and
   diff-tested like code;
2. a **generated Excel workbook** that does the scoring, risk maths and
   dashboarding for the assessor;
3. a **Word report template** that pulls its narrative and figures from the
   workbook so the report and the evidence cannot drift apart.

Everything in this folder is generated from the YAML library. There is no
hand-maintained spreadsheet of controls.

---

## Table of contents

- [1. What is in this folder](#1-what-is-in-this-folder)
- [2. How the pieces fit together](#2-how-the-pieces-fit-together)
- [3. The control library](#3-the-control-library)
- [4. The risk model](#4-the-risk-model)
- [5. The maturity model](#5-the-maturity-model)
- [6. The workbook, sheet by sheet](#6-the-workbook-sheet-by-sheet)
- [7. The report template](#7-the-report-template)
- [8. How to build](#8-how-to-build)
- [9. How to run an engagement](#9-how-to-run-an-engagement)
- [10. Best way to represent these files](#10-best-way-to-represent-these-files)
- [11. Known issues in this release](#11-known-issues-in-this-release)
- [12. Build roadmap](#12-build-roadmap)
- [13. Where everything is](#13-where-everything-is)

---

## 1. What is in this repository

```
.
├── README.md                        This file
├── .gitignore
└── artefacts/                       Everything else — start at artefacts/README.md
    ├── README.md                    Index
    ├── MANIFEST.md / MANIFEST.csv   Every file, size, SHA-256, provenance
    ├── 01-governance/               Document control, changelog, build roadmap
    ├── 02-methodology/              Methodology, data dictionary, control schema
    ├── 03-library/                  Control catalogue exports + validator + JSON Schema
    ├── 04-workflows/                Engagement runbook, evidence handling
    ├── 05-deliverables/             The three client-facing files
    ├── 06-source/                   The buildable source project (YAML + scripts)
    ├── 07-reference/                File-format guide, QA findings, framework refs
    └── 08-infrastructure/           Dependency manifests + build, verify and publish instructions
```

Numbered folders sort into reading order. `05-deliverables/` holds what a client
receives; `06-source/` holds what you edit; the rest is the reasoning behind both.

### The three deliverables

| File | What it is | Use it for |
|---|---|---|
| `artefacts/05-deliverables/SAOS-Assessment-Workbook-v0.1-BLANK.xlsx` | Engagement workbook, 19 sheets, no client data | **Start every engagement from this.** |
| `artefacts/05-deliverables/SAOS-Assessment-Workbook-v0.1-SAMPLE.xlsx` | Synthetic sample data for demonstrating the dashboard | Never issue to a client |
| `artefacts/05-deliverables/SAOS-Executive-Report-Template-v0.1.docx` | Word report template, 8 sections + 5 appendices, 14 tables | Fill in from the Dashboard figures |

## 2. How the pieces fit together

```
                    ┌──────────────────────────────────────┐
                    │  library/meta.yaml                   │
                    │  18 domains, 13 family definitions   │
                    └───────────────┬──────────────────────┘
                                    │
                    ┌───────────────▼──────────────────────┐
                    │  library/controls/*.yaml             │
                    │  60 controls × 27 fields             │  ← EDIT HERE
                    └───────────────┬──────────────────────┘
                                    │  yaml.safe_load
             ┌──────────────────────┴───────────────────────┐
             │                      │                        │
  ┌──────────▼──────────┐  ┌────────▼─────────┐  ┌───────────▼──────────┐
  │ build_workbook.py   │  │ export_library.py│  │ validate_library.py  │
  │ (Python + openpyxl) │  │ (Python + YAML)  │  │ (Python + YAML)      │
  └──────────┬──────────┘  └────────┬─────────┘  └──────────────────────┘
             │                      │
   ┌─────────▼──────────┐  ┌────────▼─────────────────────────────────┐
   │ *.xlsx             │  │ CSV / JSON exports of the catalogue      │
   │ 19 sheets, 3 charts│  │ control-catalogue, evidence, mappings,    │
   │ 257 PBC rows       │  │ domain + family registries              │
   └─────────┬──────────┘  └──────────────────────────────────────────┘
             │  assessor fills Scope → Assessment → Registers
   ┌─────────▼──────────┐
   │ build_report.js    │  Node + docx
   └─────────┬──────────┘
             │
   ┌─────────▼──────────┐
   │ *.docx report      │  ← figures copied from Dashboard
   └────────────────────┘
```

**The single most important rule:** the YAML library is the source of truth. The
`Control_Library`, `Mapping_Matrix`, `MITRE_Matrix` and `ZeroTrust_Matrix`
sheets are *generated*. Editing them in Excel means the next build silently
overwrites your change.

---

## 3. The control library

### Domains

18 domains are registered. Targets 1–15 come from the project specification;
16 is an assumption; 17–18 are reserved placeholders.

| # | Code | Domain | Target | Batch | Built |
|---|---|---|---|---|---|
| 1 | GOV | Governance | 50 | Batch 2 | 0 |
| 2 | AST | Asset Management | 25 | Batch 2 | 0 |
| 3 | IAM | Identity and Access Management | 60 | Batch 1 | 0 |
| 4 | END | Endpoint Security | 50 | Batch 3 | 0 |
| **5** | **SRV** | **Server Security** | **60** | **Pilot (built)** | **60 ✅** |
| 6 | NET | Network Security | 75 | Batch 3 | 0 |
| 7 | M365 | Microsoft 365 | 80 | Batch 1 | 0 |
| 8 | CLD | Cloud Security | 100 | Batch 1 | 0 |
| 9 | APP | Application Security | 80 | Batch 4 | 0 |
| 10 | API | API Security | 40 | Batch 4 | 0 |
| 11 | SOC | Security Operations | 70 | Batch 2 | 0 |
| 12 | VLM | Vulnerability Management | 35 | Batch 2 | 0 |
| 13 | DPR | Data Protection | 40 | Batch 3 | 0 |
| 14 | BKP | Backup and Recovery | 30 | Batch 3 | 0 |
| 15 | DSO | DevSecOps | 60 | Batch 4 | 0 |
| 16 | GWS | Google Workspace | 50 | Batch 4 | 0 |
| 17 | OT | OT/ICS (future) | 0 | Placeholder | — |
| 18 | AI | AI Systems (future) | 0 | Placeholder | — |
| | | **Total** | **905** | | **60 (6.6%)** |

The specification states a "700+ control" goal; the per-domain targets sum to
855, or 905 including domain 16. That discrepancy is flagged in the workbook's
`Domain_Registry` sheet and should be resolved before external use.

### Control families (Server Security)

60 controls across 13 families:

| Family | Controls | Focus |
|---|---|---|
| SRV-PHY Physical and Environmental Security | 4 | Rack locks, BMC/iDRAC isolation, removable media, media sanitisation |
| SRV-CFG Secure Configuration and Change | 7 | Baselines, GPO, configuration drift, change control |
| SRV-PAT Patch and Lifecycle Management | 5 | Patch cadence, KEV, OS lifecycle, vulnerability scanning |
| SRV-LOG Logging and Time Synchronization | 6 | Log forwarding, retention, tamper resistance, NTP, host logging |
| SRV-HST Host Protection | 4 | EDR, host firewall, application control, FIM |
| SRV-VUL Vulnerability Assessment | 4 | Scanning coverage, authenticated scanning, triage, validation |
| SRV-NET Network Placement and Exposure | 1 | Management plane isolation |
| SRV-IAM Authentication and Access Control | 9 | LAPS, MFA, privileged access, dormant accounts, service accounts |
| SRV-ADM Secure Administration | 2 | Admin tiering, just-in-time administration |
| SRV-BCK Backup, Restore and Recovery | 6 | 3-2-1-1-0, immutability, restore testing, recovery |
| SRV-DAT Data Protection | 3 | Encryption at rest and in transit, key management |
| SRV-GOV Governance, Ownership and Risk | 4 | Asset ownership, exception management, third-party servers |
| SRV-VIR Virtualization Platforms | 5 | vSphere, Hyper-V, Proxmox, ESXi hardening |

### Every control carries 27 fields

The schema is the product. Each control is written so an assessor with no prior
knowledge of the domain can test it and a reviewer can reproduce the score.

| Field | Meaning |
|---|---|
| `id` | `SRV-LOG-02` — domain, family, sequence. Unique library-wide. |
| `name` | The control statement, written as a positive assertion of the desired state. |
| `plat` | `All` / `Windows` / `Linux` / `Hypervisor` — drives the Scope applicability logic. |
| `obj` | Objective: what the control achieves and why it is written this way. |
| `biz` | Business justification: the consequence if absent, in business language. |
| `thr` | Threat prevented — semicolon-separated threat scenarios. |
| `q` | Assessment question: the one question the assessor answers. |
| `type` | Preventive (44) / Detective (11) / Corrective (5). |
| `ev` | Evidence required, semicolon separated. **Each item becomes one PBC request row.** |
| `proc` | Validation procedure: step-by-step, with real commands. |
| `test` | Which methods apply: INT 14, DOC 25, CFG 39, OBS 6, TECH 54, AUTO 33, PEN 2. |
| `auto` | Automation potential: High 31, Medium 23, Low 6. |
| `autom` | The specific tool, API or query used. |
| `L` / `I` | Default likelihood / impact 1–5 → inherent risk. |
| `w` | Criticality weight 1–3 used in weighted-average maturity. |
| `m1`/`m3`/`m5` | Maturity anchors for levels 1, 3 and 5. L2 and L4 are interpolated. |
| `rem` | Remediation guidance — the concrete action that raises the level. |
| `iso` | ISO/IEC 27001:2022 Annex A controls. |
| `csf` | NIST CSF 2.0 subcategories. |
| `cis` | CIS Controls v8.1 safeguards. |
| `soc` | SOC 2 (2017 TSC) criteria. |
| `att` | MITRE ATT&CK: `TACTIC:technique` groups separated by `\|`. |
| `zt` | NIST SP 800-207 Zero Trust pillars touched. |
| `orig` | `New`, or the source checklist reference when ported. |

Optional: `ref` (override the family default references), `asvs`, `owasp`.

### Library statistics

| Measure | Value |
|---|---|
| Controls | 60 |
| Control families | 13 |
| Individual evidence items | 257 (min 3, max 6 per control, mean 4.3) |
| ATT&CK techniques mapped | 47 — every technique in the build table is used |
| ATT&CK tactic coverage | All 11 tactics. Heaviest: Initial Access 21, Defense Evasion 14, Privilege Escalation 13, Lateral Movement 11, Impact 11, Credential Access 10. Lightest: Exfiltration 1 |
| Zero Trust pillars | Infrastructure 42, Identity 15, Network 10, Data 9, Device 4, Application 1 |
| Inherent risk spread | 9 Critical, 39 High, 11 Medium, 1 Low (range 2–20) |
| Criticality weights | 29 controls at weight 3, 27 at weight 2, 4 at weight 1 |
| Platform coverage | 54 `All`, 5 `Hypervisor`, 1 `Linux` |
| Controls authored new | 16 `New`; 44 ported from an existing checklist (CIS-style references) |

### YAML authoring rules

The build script fails loudly rather than silently mis-parsing, but three
gotchas are worth internalising:

1. **Quote anything that looks like a number with a dot.** `cis: '4.6, 12.2'`
   unquoted becomes the float `4.6`, and the CIS parser loses `12.2`.
2. **Quote any text containing a comma inside a `{flow}` mapping**, e.g.
   `SRV-BCK: {name: 'Backup, Restore and Recovery', ...}`.
3. **Never name a key `no` or `yes`.** YAML 1.1 reads them as booleans.
4. Use `|-` block scalars for `proc` so multi-line procedures stay readable.

Full field reference: `artefacts/02-methodology/CONTROL-SCHEMA.md`.
Machine-checkable schema: `artefacts/03-library/control-schema.json`.

---

## 4. The risk model

Defined once on the `Risk_Model` sheet and referenced by every formula in the
workbook via `INDEX/MATCH` on the rating bands.

```
Inherent risk  = Likelihood (1-5) × Impact (1-5)                 → 1 to 25
Effectiveness  = f(assessed maturity)                           → 0% to 90%
Residual risk  = Inherent × (1 − Effectiveness)                 → 0.0 to 25.0
```

### Rating bands (lower bound inclusive)

| Band | Rating | Expected response | Timeline |
|---|---|---|---|
| 0 | Low | Accept or monitor | Within 12 months |
| 5 | Medium | Plan and fund remediation; owner assigned | Within 6 months |
| 10 | High | Prioritised remediation; monthly reporting | Within 90 days |
| 17 | Critical | Immediate escalation to CISO and executive risk owner | Within 30 days or compensating control now |

Band 0 starts at zero rather than 1 because residual scores are fractional.

### Control effectiveness by maturity

| Maturity | Level | Risk reduction |
|---|---|---|
| 0 | Non-Existent | 0% |
| 1 | Initial | 10% |
| 2 | Repeatable | 30% |
| 3 | Defined | 55% |
| 4 | Managed | 75% |
| 5 | Optimized | 90% |

These six percentages are **calibration parameters, not facts.** They sit in
editable blue cells so they can be tuned per client or sector, and any change
must be recorded in the engagement file. A client with a published risk appetite
statement should have its own values here, and the report must say so.

### Worked example (from the workbook README)

`SRV-LOG-02` — logs forwarded to a central tamper-resistant store. Forwarding
found on 60% of servers, no alert for cleared Security logs.
Maturity **2**, target **3**, gap **1**.

```
Default L4 × I5                      = 20 inherent            → Critical
Effectiveness at maturity 2          = 30%
Residual = 20 × (1 − 0.30)           = 14.0                  → High
```

Then: raise a finding, a risk entry, and a remediation action.

---

## 5. The maturity model

Six levels, 0–5. Full definitions, typical evidence and coverage thresholds are
on the `Maturity_Model` sheet.

| Level | Name | Meaning | Coverage |
|---|---|---|---|
| 0 | Non-Existent | No control, no awareness, or cannot be demonstrated | 0% |
| 1 | Initial | Ad hoc, informal, depends on individuals | <25% |
| 2 | Repeatable | Done similarly but not consistently documented or approved | 25–74% |
| 3 | Defined | Documented, approved, consistently operated, evidence exists | ≥75% |
| 4 | Managed | Measured and monitored; exceptions governed; reviewed | ≥90% |
| 5 | Optimized | Continuously improved, automated, threat-informed | ≥95% + automation |

### Scoring rules that stop inflation

1. **Evidence cap** — a score above 1 requires operating evidence, not just a
   policy. Interview-only evidence caps the score at **2**.
2. **Coverage cap** — under 50% of in-scope assets covered caps at **2**;
   under 90% caps at **3**.
3. **Design vs operation** — documented design without proof of operation caps
   at **2**. Consistent operation proven by sampling supports **3**.
4. **Level 4 needs measurement** — metrics, reviews, tested outcomes, on top of
   level 3. Level 5 needs automation or continuous assurance.
5. **Calibrate to the anchors** — use the per-control `m1`/`m3`/`m5` anchors;
   interpolate L2 and L4 as "between" the anchors.
6. **Record the evidence ID** behind every score so a reviewer can re-perform it.

These caps are what separate an honest maturity score from a flattering one.
They are the difference between "we have a policy" and "the policy is operating".

---

## 6. The workbook, sheet by sheet

19 sheets. Tab colours: **navy** = generated reference or results, **amber** =
working sheets the assessor fills, **grey** = configuration.

### Working sheets (amber)

| Sheet | What it is | Input cells |
|---|---|---|
| **Scope** | Client, dates, tier, industry, drivers, platform and domain scope | Yellow + blue |
| **Assessment** | One row per control: applicability, current/target maturity, gap, status, tests, evidence, notes, L/I overrides, and all risk formula columns | K, L, R, S + notes |
| **Evidence_Requests** | The PBC list. 257 rows, one per evidence item, pre-filled from the library | Dates, status, evidence ID |
| **Evidence_Register** | What was actually collected: type, source system, method, collector, date, storage path, SHA-256, reviewer, review status, confidentiality | All rows from 6 |
| **Findings_Register** | One row per gap: severity, recommendation, owner, due date, status, days open, overdue flag | All rows from 6 |
| **Risk_Register** | Risks with inherent and residual scoring linked to the assessed control maturity | All rows from 6 |
| **Remediation_Tracker** | Actions with owner, priority, dates, % complete, days to due, RAG, verification evidence | All rows from 6 |
| **Crown_Jewels** | Critical assets with CIA scoring, RTO/RPO, dependencies, high-value target flag | All rows from 6 |
| **Attack_Paths** | Realistic paths to crown jewels by category (External, Internal, Cloud, Identity, Supply Chain) with chokepoints | All rows from 6 |

### Results and reference (navy / grey)

| Sheet | What it is |
|---|---|
| **Dashboard** | 6 KPI tiles, domain scores, family heat map, maturity distribution, inherent risk heat map, residual distribution, top 10 residual risks, findings overview, remediation and evidence overview, trend table, 3 charts |
| **Control_Library** | **Generated.** All 60 controls × 32 columns, including the seven test-method tick columns and the L1/L3/L5 anchors |
| **Mapping_Matrix** | **Generated.** ISO 27001:2022 (clause + Annex A), NIST CSF 2.0, CIS v8.1, SOC 2, OWASP ASVS 4.0.3, OWASP Top 10:2021, ISO/IEC 27034 category |
| **MITRE_Matrix** | **Generated.** Technique IDs per tactic, plus a per-technique control count |
| **ZeroTrust_Matrix** | **Generated.** Pillar coverage per control with pillar totals and share |
| **Maturity_Model** | The 6 levels, evidence expectations, coverage, and the 6 scoring rules |
| **Risk_Model** | Likelihood scale, impact scale with 5 business dimensions, the L×I matrix, rating bands, effectiveness table |
| **Domain_Registry** | Live build status: controls built, % of target, batch, status |
| **Lists** | All 16 drop-down source lists. Data validation points here — edit here, never at the cell |
| **README** | In-workbook instructions, colour legend, worked example, limitations |

### Colour convention (this is the whole UX)

| Appearance | Meaning |
|---|---|
| Navy header row | Table headings |
| **Blue text on yellow** | **Input cell — overtype this** |
| Black on white/grey | Formula or library data — **do not overtype** |
| Grey italic row 5 on registers | Worked example, excluded from all counts |
| `●` in MITRE/ZT matrices | Mapping present |

### Dashboard KPI formulas

| Tile | Formula intent |
|---|---|
| Overall maturity (0-5) | Criticality-weighted mean of Current Maturity over in-scope assessed controls |
| Maturity % | Same ÷ 5 |
| Assessment completion | Assessed ÷ in-scope |
| Controls with a gap | `COUNTIF(Status, "Gap")` |
| Critical / High residual | Count of residual rating Critical + High |
| Open Critical/High findings | `COUNTIFS` over severity × status |

Domain and family scores are the same weighted mean, computed with
`SUMPRODUCT`. Status thresholds: gap ≤ 0 = **On target**, ≤ 1.0 = **Minor
gap**, > 1.0 = **Significant gap**.

---

## 7. The report template

`SAOS-Executive-Report-Template-v0.1.docx` — A4, Arial, navy/grey house style,
header "Cybersecurity Posture Assessment | CONFIDENTIAL", footer with page
number, live table of contents.

| Section | Content |
|---|---|
| Cover | Classification, client, reference, period, version, author |
| Document Control | Classification, workbook version, prepared/reviewed by, distribution, version history, TOC |
| 1. Executive Summary | Overall conclusion, headline measure table, "what matters most", decisions requested. **Write this last, max one page, for a non-technical reader** |
| 2. Scope | Organisation, domains, platforms, sites, **explicit exclusions**, assumptions and limitations |
| 3. Methodology | Framework description, testing approach, maturity scale table, risk rating table, client calibration note |
| 4. Key Observations | Themed, not per-control. Strengths *and* improvement areas, with evidence references |
| 5. Top Risks | Top 10 residual risks as **business scenarios**, plus crown jewels and attack paths |
| 6. Maturity Assessment | Domain table, maturity-vs-target chart, framework alignment, Zero Trust and ATT&CK coverage |
| 7. Findings Summary | Severity counts; Critical and High detail in the body, the rest in Appendix A |
| 8. Remediation Roadmap | 0–30 / 30–90 / 3–6 / 6–12 month horizons with owners and dependencies |
| Appendix A | Detailed findings |
| Appendix B | Control results export |
| Appendix C | Evidence index |
| Appendix D | Risk register extract |
| Appendix E | Glossary and limitations |

Placeholders are **red bracketed text** (`[Client name]`). Grey shaded boxes
with a left border are **author guidance** — they are instructions to the
assessor and must be deleted before issue. The template ships with the guidance
still in it, which is correct for a template.

### Figures must trace to the workbook

Every number in the report comes from the `Dashboard` sheet, and Document
Control must quote the workbook version. Appendix E already carries the correct
disclaimer: mappings are indicative professional judgement and do not
constitute certification or attestation.

---

## 8. How to build

### Prerequisites

```powershell
python -m pip install -r artefacts\08-infrastructure\requirements.txt   # PyYAML
cd artefacts\06-source ; npm install                                    # docx
```

### Build the workbook

```powershell
python artefacts\06-source\build\build_workbook.py out.xlsx            # blank
python artefacts\06-source\build\build_workbook.py sample.xlsx --sample  # synthetic data
```

`--sample` fills the workbook with seeded random scores so the dashboard can be
seen working. Every identifying field is written as `Redacted`, so the build can
never emit a plausible client identity. **Never ship a `--sample` build.**

### Build the report template

```powershell
cd artefacts\06-source
node build\build_report.js report-template.docx
```

`build_report.js` takes the output path as `argv[2]` and resolves the `docx`
module by walking up from its own directory — so `package.json` and
`node_modules` must live at or above `06-source/`.

### Validate the library

```powershell
python artefacts\03-library\validate_library.py
python artefacts\03-library\validate_library.py --strict   # CI: warnings fail too
```

Checks required fields, unknown/typo'd fields, ID pattern and uniqueness,
domain/family registration, every enumeration, ATT&CK tactic and technique
IDs, mapping string shapes, per-family sequence contiguity and minimum content
length. Current state: **PASS, 60 controls, 0 errors.**

### Regenerate the exports

```powershell
python artefacts\03-library\export_library.py
```

### Always recalculate after building

Open in Excel or LibreOffice and save once to cache the values:

```powershell
# LibreOffice headless recalculation
soffice --headless --convert-to xlsx --outdir .\out .\out.xlsx
```

Full instructions, including the verified CI recipe:
`artefacts/08-infrastructure/BUILD-AND-VERIFY.md`.

---

## 9. How to run an engagement

The in-workbook README gives the six-step version. Expanded with what actually
goes wrong:

### 1. Scope
Complete the `Scope` sheet: client, reference, dates, lead assessor, reviewer,
org tier, industry, regulatory drivers, platform scope, domain scope.
`Applicable?` and `Target Maturity` in the Assessment sheet pre-fill from it.
Set the default target from the tier table (SMB 2.0, Mid-size 3.0,
Enterprise 3.0, Multinational 4.0, Government 4.0) unless the client has a
published target. Overtype `Scope!C13` for a client-specific figure; overtype
individual cells in `Assessment` column L where a control deserves a different
target.

> Watch the platform trap: controls with `plat: All` stay applicable whatever you
> set, but a domain marked out of scope silently drops every control to `N/A`,
> which quietly removes them from the dashboard averages.

### 2. Evidence
Send `Evidence_Requests` to the client as the PBC list — it is already one row
per evidence item with a request ID. Track status. Log what arrives in
`Evidence_Register` and write the Evidence ID back onto the request row so the
chain request → evidence → control is traceable in both directions.

### 3. Assess
For each in-scope control: pick the tests you actually performed, score Current
Maturity 0–5 using `Maturity_Model` plus the control's `m1`/`m3`/`m5` anchors,
record the evidence IDs and your observations. Apply the caps. Overriding
`Likelihood` or `Impact` is allowed and expected where the client context
differs from the default — record why in the notes column.

### 4. Findings and risks
One finding per material gap. Severity is your judgement, but it should be
consistent with the residual rating the workbook calculated. Every Critical or
High residual risk should have a matching finding.

### 5. Context
Fill `Crown_Jewels` and `Attack_Paths`. This is what converts a list of control
gaps into a prioritised business argument, and it is the section executives
actually read.

### 6. Report
Read the Dashboard, then complete the Word template. Replace every red
placeholder, delete every grey guidance box, and make sure Document Control
quotes the exact workbook version.

Expanded version with timings and reviewer checkpoints:
`artefacts/04-workflows/ENGAGEMENT-RUNBOOK.md`.

---

## 10. Best way to represent these files

This is the question that matters most for anything downstream of v0.1. The
short answer and the reasoning are in
**`artefacts/07-reference/FILE-FORMAT-GUIDE.md`**; the summary:

### Keep

| Format | Used for | Why |
|---|---|---|
| **YAML** | Control library | The one canonical format. Diffable, reviewable in a pull request, comments allowed, no code required to read. Correct choice — do not change it. |
| **JSON Schema** | `control-schema.json` | Makes the YAML contract machine-checkable in any language or editor. New. |
| **CSV (UTF-8 BOM)** | Catalogue exports | Opens cleanly in Excel everywhere. New. |
| **JSON** | `control-catalogue.json` | Nested, for APIs, notebooks, diffing across versions. New. |
| **XLSX** | The engagement working surface | Correct. Assessors need filters, validation, conditional formatting and charts. |

### Add

| Addition | Why |
|---|---|
| **CSV/JSON catalogue export** | The YAML is unreadable by BI tools and non-technical reviewers. Now generated. |
| **Tidy long-format mapping table** | `framework-mapping.csv` — one row per control per framework. Pivot-table ready for coverage reporting; the wide matrix is unusable for that. |
| **Independent validator** | `validate_library.py` catches malformed controls before the build does, with readable messages. |
| **Dependency manifests** | `requirements.txt`, `package.json`, `package-lock.json`. Reproducible builds. |
| **SHA-256 manifest** | `MANIFEST.csv` / `MANIFEST.md` — prove which version of which file a client received. |

### Change or reconsider

| Issue | Recommendation |
|---|---|
| **One monolithic workbook holds both the library and the client data** | **Split it.** Ship `SAOS-Library-and-Method-v0.1.xlsx` (reference, read-only, versioned with the YAML) separately from `SAOS-Assessment-Workbook-<client>-<period>.xlsx` (engagement data). Right now the library travels with every client file, so it can be edited by an assessor and it re-ships on every engagement. The generator already supports this — it is a one-line change to the `SHEETS` list. |
| **File names do not describe contents** | Adopt the convention in the format guide: `SAOS-<artefact>-v<version>[-<client>[-<period>]][-<state>].<ext>`, where state is `BLANK`, `SAMPLE`, `DRAFT`, `FINAL` or `SUPERSEDED`. A v0.1 delivery failed exactly this test — see QA finding F-01. |
| **`SUPERSEDED` / retracted files have no marker inside** | When data is retracted, keep the file but stamp it: set `docProps` title/status, add a `README` banner, and record it in the manifest. A retracted workbook that is indistinguishable from a live one is a data-governance failure. |
| **The Word template has no version in its filename** | `SAOS-Executive-Report-Template-v0.1.docx` — now applied. |
| **Report figures are retyped by hand** | Medium-term: generate the report from `control-catalogue.json` + the completed workbook so numbers cannot drift. |
| **YAML block scalars hide trailing-whitespace errors** | Keep `proc` as `|-`, but add a lint step for tabs and trailing spaces in CI. |
| **No tests** | `validate_library.py` is the first test. Add a golden-file test: build the workbook, hash the `Control_Library` sheet, compare to a committed baseline. |

### Naming convention to adopt

```
SAOS-Library-and-Method-v0.1.xlsx
SAOS-Assessment-Workbook-v0.1-BLANK.xlsx
SAOS-Assessment-Workbook-v0.1-SAMPLE.xlsx
SAOS-Assessment-Workbook-v0.1-<Client>-2026Q3-FINAL.xlsx
SAOS-Assessment-Workbook-v0.1-<Client>-2026Q3-SUPERSEDED.xlsx
SAOS-Executive-Report-Template-v0.1.docx
SAOS-Executive-Report-v0.1-<Client>-2026Q3-DRAFT.docx
SAOS-Control-Catalogue-v0.1.csv
SAOS_ControlCatalogue_v0.1.json
```

Use `UPPER_SNAKE` or `kebab-case` consistently — the current filenames mix
spaces, underscores and mixed case, which breaks scripted sorting and forces
quoting in every shell command.

---

## 11. Known issues in this release

Full detail and evidence: `artefacts/07-reference/QA-FINDINGS.md`.

| ID | Severity | Issue |
|---|---|---|
| **F-01** | **High** | A delivered filename asserted a provenance its contents did not support. Resolved: the file was renamed to state its true contents, and `--sample` mode now redacts every identity field. |
| **F-02** | Medium | Blank workbook is stamped `built 2025-11-28`; the current script stamps `2026-10-04`. Re-running the build changes the README line, so the shipped workbook is stale relative to the toolchain. |
| **F-03** | Medium | No `package.json`, no `requirements.txt`, no lock file in the delivered source. `build_report.js` fails with `Cannot find module 'docx'` out of the box. Now supplied. |
| **F-04** | Medium | Framework mappings (ISO 27001:2022, NIST CSF 2.0, CIS v8.1, SOC 2, MITRE, OWASP) were authored from working knowledge. They must be verified against the licensed source documents before any client issue. Stated in the workbook README and report Appendix E, but it is a legal exposure if missed. |
| **F-05** | Medium | Domain targets sum to 905, not the "700+" in the specification. Domain 16's target of 50 is an explicit assumption. |
| **F-06** | Low | No validation of ASVS chapters or OWASP Top 10 values — `asvs` and `owasp` default to `N/A` and are unmapped for all 60 Server Security controls. Expected; the specification is ambiguous between ASVS 4.0.3 (V1–V14) and ASVS 5.0 (2025). |
| **F-07** | Low | Domain 17 (OT/ICS) and 18 (AI) are placeholders with target 0. A client in those sectors cannot be assessed with v0.1. |
| **F-08** | Low | Registers are formatted for 200 rows. Formulas read to row 2000, so the library can grow, but a full 905-control engagement needs the register row counts extended. |
| **F-09** | Low | `Likelihood Override` / `Impact Override` change the risk maths but are not recorded in the audit trail — there is no "override reason" column, only free-text notes. |
| **F-10** | Low | `Risk_Model!$A$30:$A$33` and related lookup ranges are **hard-coded row references**. Inserting a row in the rating-bands or effectiveness tables silently breaks every rating formula in the workbook. Marked "fixed layout" in the code but not enforced. |
| **F-11** | Info | `build_report.js` does not set document properties for classification, and the TOC field requires a manual F9 refresh in Word. |
| **F-12** | Info | Zero Trust **Application** pillar has only 1 control and **Exfiltration** has 1 ATT&CK tactic group. Expected for a server domain; will look thin in a client report if quoted without that context. |

---

## 12. Build roadmap

Full plan with sequencing rationale: `artefacts/01-governance/BUILD-ROADMAP.md`.

| Batch | Domains | Controls | Sequencing rationale |
|---|---|---|---|
| Pilot ✅ | SRV | 60 | Done. Validated the whole pipeline. |
| Batch 1 | IAM, M365, CLD | 240 | Highest client demand. Identity and cloud are where engagements start. Also unblocks SRV cross-references. |
| Batch 2 | GOV, AST, SOC, VLM | 180 | Governance and inventory underpin everything; SOC and VLM give the detection and remediation story. |
| Batch 3 | END, NET, DPR, BKP | 195 | Extends outward from the server estate to the endpoints and network it depends on. |
| Batch 4 | APP, API, DSO, GWS | 230 | Application-layer work; needs the ASVS version decision (F-06) resolved first. |
| Placeholder | OT, AI | 0 | Blocked on scope and methodology. |

Before Batch 1: resolve F-02 through F-05, split the library workbook out
(F-03 / format guide), and add the golden-file test.

---

## 13. Where everything is

### Start here

| I want to… | Go to |
|---|---|
| Understand the whole system | This file |
| Find any file | `artefacts/MANIFEST.md` |
| Know what changed | `artefacts/01-governance/CHANGELOG.md` |
| Know what is wrong | `artefacts/07-reference/QA-FINDINGS.md` |
| Decide on formats | `artefacts/07-reference/FILE-FORMAT-GUIDE.md` |
| Understand the scoring | `artefacts/02-methodology/METHODOLOGY.md` |
| Look up a column | `artefacts/02-methodology/DATA-DICTIONARY.md` |
| Write a new control | `artefacts/02-methodology/CONTROL-SCHEMA.md` |
| Import the catalogue | `artefacts/03-library/control-catalogue.csv` / `.json` |
| Run an engagement | `artefacts/04-workflows/ENGAGEMENT-RUNBOOK.md` |
| Build and verify | `artefacts/08-infrastructure/BUILD-AND-VERIFY.md` |
| Edit controls | `artefacts/06-source/library/controls/*.yaml` |

### File formats at a glance

36 files, 1,271 KB. Full inventory with SHA-256 in `artefacts/MANIFEST.csv`.

| Extension | Count | Role |
|---|---|---|
| `.md` | 15 | Documentation (this file + 13 in `artefacts/` + the source README) |
| `.py` | 4 | Workbook builder, exporter, validator, manifest generator |
| `.csv` | 5 | Catalogue exports (catalogue, evidence, mappings, domain and family registries) |
| `.yaml` | 4 | Canonical control library (3 control files + `meta.yaml`) |
| `.json` | 4 | Catalogue, control JSON Schema, `package.json`, lock file |
| `.xlsx` | 2 | Blank workbook, sample workbook |
| `.js` | 1 | Report builder |
| `.docx` | 1 | Report template |
| `.txt` | 1 | `requirements.txt` |

### Verified state of this delivery

| Check | Result |
|---|---|
| `validate_library.py` | **PASS** — 60 controls, 13 families, 0 errors, 0 warnings |
| `build_workbook.py` (blank + `--sample`) | **PASS** — both build cleanly |
| `build_report.js` | **PASS** — builds after `npm install` |
| `export_library.py` | **PASS** — 6 exports regenerated |
| Manifest SHA-256 | Recorded for every file in `artefacts/MANIFEST.csv` |

---

*SAOS v0.1 — vendor-neutral assessment toolkit. Framework mappings are indicative
professional judgement and do not constitute certification, attestation or
legal advice. Validate all technical commands in a test environment under
written authorisation before use.*
