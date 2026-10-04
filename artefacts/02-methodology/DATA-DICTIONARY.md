# Data Dictionary

Every sheet and every column in the assessment workbook, with type, source and
whether the assessor touches it.

**Legend**

| Mark | Meaning |
|---|---|
| 🔵 **INPUT** | Blue text on yellow. Overtype this. |
| ⚙️ FORMULA | Calculated. Do not overtype. |
| 📚 GENERATED | Built from the YAML library. Do not edit — edit the YAML and rebuild. |
| 🔒 CONFIG | Editable configuration parameter. Change deliberately and disclose it. |
| 📖 REFERENCE | Static reference content. |
| ▫️ EXAMPLE | Grey italic worked example, row 5. Excluded from all counts. |

**Sheet tab colours** — navy = generated or results, amber = working sheets you
fill, grey = configuration.

---

## 1. README

In-workbook instructions. Not data.

| Cell | Content |
|---|---|
| B1 | Title |
| B2 | Version, build date, and `SAMPLE DATA - CLIENT NAME REDACTED` when built with `--sample` |
| B4+ | Purpose, how to run an engagement, colour legend, worked example, scoring summary, sheet guide, limitations |

---

## 2. Scope

The only sheet you must complete before anything else works. Applicability and
target maturity both derive from it.

| Cell/Col | Name | Type | Notes |
|---|---|---|---|
| C4 | Client name | 🔵 INPUT | Appears on the Dashboard header and in the report |
| C5 | Engagement reference | 🔵 INPUT | |
| C6 | Assessment start date | 🔵 INPUT | `yyyy-mm-dd` |
| C7 | Assessment end date | 🔵 INPUT | |
| C8 | Lead assessor | 🔵 INPUT | |
| C9 | Reviewer | 🔵 INPUT | |
| C10 | Organisation size tier | 🔵 INPUT | Drop-down: SMB / Mid-size / Enterprise / Multinational / Government |
| C11 | Industry | 🔵 INPUT | |
| C12 | Regulatory and contractual drivers | 🔵 INPUT | e.g. PCI DSS, ISO 27001 certification scope, customer contract |
| C13 | Default target maturity | ⚙️ FORMULA | `INDEX/MATCH` on the tier table below. Overtype for a client-specific target |
| E5:F9 | Default target by tier | 🔒 CONFIG | SMB 2.0, Mid-size 3.0, Enterprise 3.0, Multinational 4.0, Government 4.0 |
| C18:C20 | Platform scope | 🔵 INPUT | Windows / Linux / Hypervisor — Yes/No. Controls with `plat: All` ignore this |
| G18:G20 | Platform notes | 🔵 INPUT | e.g. "VMware, Hyper-V, Proxmox" |
| B24:C41 | Domain scope | 🔵 INPUT | One Yes/No per domain, all 18 |

> **Setting a domain to `No` removes every control in it from the dashboard.**
> Out-of-scope controls read `N/A` and are excluded from weighted averages. That
> is correct behaviour, but confirm the domain scope is right before assessing.

---

## 3. Dashboard

Read-only results. Nothing here is an input.

| Block | Location | Content |
|---|---|---|
| Header | B1:B2 | Title; client name and assessment period pulled from Scope |
| KPI tiles | B4:L5 | Six tiles: overall maturity (0-5), maturity %, assessment completion, controls with a gap, critical/high residual, open critical/high findings |
| Domain scores | B8:I26 | Per domain: controls in library, in scope, assessed, avg maturity, avg target, gap, status |
| Family scores | B29:I42 | Same, per family, with a colour scale heat map |
| Maturity distribution | B45:C52 | Controls at each level 0–5, plus a "not yet assessed" row |
| Inherent risk heat map | B55:G60 | Count of in-scope controls by likelihood × impact, coloured by band |
| Residual distribution | B63:C67 | Count of assessed controls by residual rating |
| Top 10 residual risks | B70:G80 | Control, ID, current, target, residual score, residual rating |
| Findings overview | B83:E89 | By severity: total, open/in progress, overdue |
| Remediation and evidence | B92:C99 | Action counts by status, overdue actions, average % complete, evidence requests received % |
| Trend analysis | B102:E109 | Current (live) plus 6 rows for pasted historical periods |

**Charts** (3): maturity vs target by family; maturity distribution; overall
maturity trend.

**Overall maturity formula**

```
SUMPRODUCT((Applicable="Yes") * ISNUMBER(Current) * Weight * Current)
  / SUMPRODUCT((Applicable="Yes") * ISNUMBER(Current) * Weight)
```

**Status thresholds** — gap ≤ 0 `On target`, ≤ 1.0 `Minor gap`, > 1.0
`Significant gap`, no data `Not assessed`.

**Trend rows are manual.** Copy the live values down as values at the end of
each cycle. Nothing accumulates automatically.

---

## 4. Assessment

One row per control, rows 5–64 for v0.1. **This is the main working sheet.**

| Col | Name | Type | Notes |
|---|---|---|---|
| A | Control ID | 📚 GENERATED | `SRV-LOG-02`. Never edit |
| B | Domain | 📚 GENERATED | Drives domain scoring |
| C | Control Family | 📚 GENERATED | Drives family scoring |
| D | Platform | 📚 GENERATED | Drives applicability |
| E | Control Name | 📚 GENERATED | |
| F | Assessment Question | 📚 GENERATED | The question you are answering |
| G | Weight | 📚 GENERATED | 1–3 criticality weight |
| H | Default Likelihood | 📚 GENERATED | Library default |
| I | Default Impact | 📚 GENERATED | Library default |
| J | Applicable? | ⚙️ FORMULA 🔵 | Pre-filled from Scope. Overtype to override |
| K | **Current Maturity (0-5)** | 🔵 INPUT | The score. Drop-down 0–5 |
| L | Target Maturity (0-5) | 🔵 INPUT ⚙️ | Defaults from `Scope!C13`. Overtype per control |
| M | Gap | ⚙️ FORMULA | `MAX(0, L − K)` while applicable and scored |
| N | Status | ⚙️ FORMULA | `N/A` / `Not assessed` / `Meets target` / `Gap` |
| O | **Tests Performed** | 🔵 INPUT | Free text, e.g. `DOC, CFG, TECH` |
| P | **Evidence Ref(s)** | 🔵 INPUT | Evidence IDs from `Evidence_Register`. Required for auditability |
| Q | **Assessor Notes / Observations** | 🔵 INPUT | Sample method, evidence quality, what you saw |
| R | Likelihood Override | 🔵 INPUT | 1–5. Empty = use default |
| S | Impact Override | 🔵 INPUT | 1–5. Empty = use default |
| T | Likelihood Used | ⚙️ FORMULA | `R` if set, else `H` |
| U | Impact Used | ⚙️ FORMULA | `S` if set, else `I` |
| V | Inherent Score | ⚙️ FORMULA | `T × U` |
| W | Inherent Rating | ⚙️ FORMULA | Rating band lookup |
| X | Control Effectiveness | ⚙️ FORMULA | From `Risk_Model` by maturity. Empty until K is scored |
| Y | Residual Score | ⚙️ FORMULA | `ROUND(V × (1 − X), 1)` |
| Z | Residual Rating | ⚙️ FORMULA | Rating band lookup |
| AA | Rank Key (helper) | ⚙️ FORMULA | `Y + ROW()/1000000`. **Hidden.** Breaks ties for the top-10 lookup. Never delete or reorder rows |

**Reading order for a row:** K (score) → O/P/Q (evidence) → R/S (overrides if
needed) → read V/W/Y/Z for the risk picture.

---

## 5. Evidence_Requests

The client PBC list. 257 rows for v0.1, generated from `ev` in the library.
Send this to the client.

| Col | Name | Type | Notes |
|---|---|---|---|
| A | Request ID | 📚 GENERATED | `ER-SRV-PHY-01-1` |
| B | Control ID | 📚 GENERATED | |
| C | Control Name | 📚 GENERATED | |
| D | Evidence Item Requested | 📚 GENERATED | One item per row |
| E | Date Requested | 🔵 INPUT | |
| F | Status | 🔵 INPUT | Not requested / Requested / Received / Partial / Not available / N/A |
| G | Date Received | 🔵 INPUT | |
| H | Evidence ID | 🔵 INPUT | `EV-nnn` from the register. Closes the loop |
| I | Notes | 🔵 INPUT | Chased, substituted, waived |

Conditional formatting: `Received` green, `Not available` red.

---

## 6. Evidence_Register

What was actually collected. 200 rows formatted (6–205). Row 5 is the worked
example.

| Col | Name | Type | Notes |
|---|---|---|---|
| A | Evidence ID | 🔵 INPUT | `EV-001` |
| B | Control ID | 🔵 INPUT | Drop-down from `Assessment!A` |
| C | Control Name | ⚙️ FORMULA | Looked up from Assessment |
| D | Evidence Type | 🔵 INPUT | 16 types: Screenshot, Configuration Export, Audit Report, System Log, Policy Document, Network Diagram, Firewall Export, Azure/AWS/GCP/M365 Export, Architecture Document, Interview Notes, Scan Report, Observation Record, Script Output |
| E | Description | 🔵 INPUT | What it shows, precisely enough to re-perform |
| F | Source System / Asset | 🔵 INPUT | Which host, tenant or system |
| G | Collection Method | 🔵 INPUT | Manual / Automated / Client-provided |
| H | Collected By | 🔵 INPUT | |
| I | Date Collected | 🔵 INPUT | `yyyy-mm-dd` |
| J | Storage Location / Link | 🔵 INPUT | Path or reference. Use a controlled evidence store |
| K | SHA-256 (optional) | 🔵 INPUT | Integrity proof. Strongly recommended for anything that evidences a Critical finding |
| L | Reviewer | 🔵 INPUT | |
| M | Review Status | 🔵 INPUT | Pending / Accepted / Rejected / Needs more |
| N | Confidentiality | 🔵 INPUT | Public / Internal / Confidential / Restricted |

---

## 7. Findings_Register

200 rows formatted (6–205). Row 5 is the worked example.

| Col | Name | Type | Notes |
|---|---|---|---|
| A | Finding ID | 🔵 INPUT | `F-001` |
| B | Control ID | 🔵 INPUT | Drop-down from Assessment |
| C | Control Name | ⚙️ FORMULA | |
| D | Domain | ⚙️ FORMULA | |
| E | Finding | 🔵 INPUT | What is wrong, stated in plain language. Not "fails SRV-LOG-02" |
| F | Severity | 🔵 INPUT | Critical / High / Medium / Low / Informational |
| G | Evidence Ref(s) | 🔵 INPUT | Evidence IDs supporting the finding |
| H | Recommendation | 🔵 INPUT | The action, not the aspiration |
| I | Owner | 🔵 INPUT | A named person or role, not a department |
| J | Due Date | 🔵 INPUT | Aligned to the severity timeline from `Risk_Model` |
| K | Status | 🔵 INPUT | Open / In Progress / Remediated / Risk Accepted / Closed |
| L | Date Raised | 🔵 INPUT | |
| M | Days Open | ⚙️ FORMULA | `TODAY() − L`. Blank unless open |
| N | Overdue? | ⚙️ FORMULA | `Overdue` when past due and not closed/accepted/remediated |

**"Open" for reporting** = `Open` + `In Progress`.

---

## 8. Risk_Register

200 rows formatted (6–205). Row 5 is the worked example.

| Col | Name | Type | Notes |
|---|---|---|---|
| A | Risk ID | 🔵 INPUT | `R-001` |
| B | Control ID | 🔵 INPUT | Drop-down from Assessment |
| C | Control | ⚙️ FORMULA | |
| D | Linked Finding ID | 🔵 INPUT | Ties the risk to a finding |
| E | Finding / Risk Description | 🔵 INPUT | Written as a business scenario, not a technical statement |
| F | Likelihood (1-5) | 🔵 INPUT | Drop-down |
| G | Impact (1-5) | 🔵 INPUT | Drop-down |
| H | Risk Score | ⚙️ FORMULA | `F × G` (inherent) |
| I | Rating | ⚙️ FORMULA | |
| J | Treatment | 🔵 INPUT | Mitigate / Accept / Transfer / Avoid |
| K | Control Maturity | ⚙️ FORMULA | Pulled from `Assessment!K` for the linked control. Drives residual |
| L | Residual Score | ⚙️ FORMULA | `ROUND(H × (1 − effectiveness(K)), 1)` |
| M | Residual Rating | ⚙️ FORMULA | |
| N | Owner | 🔵 INPUT | |
| O | Target Date | 🔵 INPUT | |
| P | Status | 🔵 INPUT | Same list as finding status |
| Q | Business Impact | 🔵 INPUT | Financial / Operational / Regulatory / Reputational / Safety / Data |

> Every risk entry inherits the assessed maturity of its linked control. If the
> risk rating and the control's residual rating disagree, one of the two is
> wrong — reconcile before reporting.

---

## 9. Remediation_Tracker

200 rows formatted (6–205). Row 5 is the worked example.

| Col | Name | Type | Notes |
|---|---|---|---|
| A | Action ID | 🔵 INPUT | `RA-001` |
| B | Finding ID | 🔵 INPUT | Links the action to a finding |
| C | Control ID | ⚙️ FORMULA | |
| D | Severity | ⚙️ FORMULA | Inherited from the finding |
| E | Remediation Action | 🔵 INPUT | Concrete and deliverable. "Deploy LAPS to 14 remaining servers", not "improve IAM" |
| F | Owner | 🔵 INPUT | |
| G | Priority | 🔵 INPUT | P1 Urgent / P2 High / P3 Medium / P4 Low |
| H | Start Date | 🔵 INPUT | |
| I | Due Date | 🔵 INPUT | |
| J | Status | 🔵 INPUT | Not Started / In Progress / Blocked / Completed / Verified / Deferred |
| K | % Complete | 🔵 INPUT | `0%` format |
| L | Days to Due | ⚙️ FORMULA | Negative when overdue |
| M | RAG | ⚙️ FORMULA | `Done` / `Overdue` / `Due within 14d` / `On track` |
| N | Verification Evidence ID | 🔵 INPUT | Evidence that the action was actually completed and tested |
| O | Notes | 🔵 INPUT | Blockers, dependencies, decisions needed |

---

## 10. Crown_Jewels

20 rows (6–25). Row 5 is the worked example. **This is what turns control gaps
into a business argument.**

| Col | Name | Type | Notes |
|---|---|---|---|
| A | ID | 🔵 INPUT | `CJ-01` |
| B | Crown Jewel | 🔵 INPUT | Asset, service or dataset |
| C | Business Process Supported | 🔵 INPUT | What breaks if it is unavailable |
| D | Business Owner | 🔵 INPUT | Named person |
| E | Data Classification | 🔵 INPUT | Public / Internal / Confidential / Restricted |
| F | C (Confidentiality) | 🔵 INPUT | 1–5 |
| G | I (Integrity) | 🔵 INPUT | 1–5 |
| H | A (Availability) | 🔵 INPUT | 1–5 |
| I | Criticality | ⚙️ FORMULA | `MAX(F:H)` — the highest dimension drives it |
| J | RTO | 🔵 INPUT | e.g. `4h` |
| K | RPO | 🔵 INPUT | e.g. `15m` |
| L | Upstream Dependencies | 🔵 INPUT | What it depends on — this is where attack paths start |
| M | Downstream Dependencies | 🔵 INPUT | What depends on it — this is what the blast radius is |
| N | Hosting / Platforms | 🔵 INPUT | |
| O | High-Value Target? | 🔵 INPUT | Yes/No. Drives ATT&CK prioritisation |
| P | Linked Control IDs / Domains | 🔵 INPUT | Which controls protect it |
| Q | Notes | 🔵 INPUT | |

---

## 11. Attack_Paths

20 rows (6–25). Row 5 is the worked example.

| Col | Name | Type | Notes |
|---|---|---|---|
| A | Path ID | 🔵 INPUT | `AP-01` |
| B | Category | 🔵 INPUT | External / Internal / Cloud / Identity / Supply Chain |
| C | Target Crown Jewel ID | 🔵 INPUT | Drop-down from `Crown_Jewels!A` |
| D | Entry Point | 🔵 INPUT | Where the attacker starts |
| E | Attack Path Narrative | 🔵 INPUT | Numbered steps. This is the section executives read |
| F | ATT&CK Techniques | 🔵 INPUT | `T1078, T1550, T1490, T1486` |
| G | Enabling Weaknesses | 🔵 INPUT | Control and finding IDs the path depends on |
| H | Existing Detection | 🔵 INPUT | What would catch this, and where it stops |
| I | Likelihood (1-5) | 🔵 INPUT | |
| J | Impact (1-5) | 🔵 INPUT | |
| K | Path Risk Score | ⚙️ FORMULA | `I × J` |
| L | Rating | ⚙️ FORMULA | |
| M | Recommended Chokepoints | 🔵 INPUT | Where one control change breaks several paths. The highest-value output of this sheet |
| N | Owner | 🔵 INPUT | |
| O | Status | 🔵 INPUT | |

---

## 12. Control_Library — GENERATED

All 60 controls × 33 columns. **Do not edit.** Edit
`06-source/library/controls/*.yaml` and rebuild.

| Col | Name | Notes |
|---|---|---|
| A | Control ID | |
| B | Domain | |
| C | Control Family | |
| D | Control Name | |
| E | Platform | All / Windows / Linux / Hypervisor |
| F | Objective | `obj` |
| G | Business Justification | `biz` |
| H | Threat Prevented | `thr` |
| I | Assessment Question | `q` |
| J | Control Type | Preventive 44 / Detective 11 / Corrective 5 |
| K | Evidence Required | One item per line |
| L | Validation Procedure | Multi-line |
| M–S | Test method ticks | Interview, Document Review, Configuration Review, Observation, Technical Validation, Automated Validation, Penetration Validation. `●` = applies |
| T | Automation Possibility | Low 6 / Medium 23 / High 31 |
| U | Automation Method | The specific tool or API |
| V | Default Likelihood (1-5) | |
| W | Default Impact (1-5) | |
| X | Inherent Score | `V × W` |
| Y | Risk Rating | Band lookup |
| Z | Criticality Weight (1-3) | 3: 29 controls, 2: 27, 1: 4 |
| AA | Maturity Anchor L1 (Initial) | State description |
| AB | Maturity Anchor L3 (Defined) | State description |
| AC | Maturity Anchor L5 (Optimized) | State description |
| AD | Remediation Guidance | |
| AE | References | Control override or family default |
| AF | Framework Mapping (summary) | Single-line roll-up |
| AG | Checklist Origin | `New` (16) or source reference (44) |

---

## 13. Mapping_Matrix — GENERATED

| Col | Name | Level |
|---|---|---|
| A | Control ID | |
| B | Control Name | |
| C | ISO 27001:2022 Clause | **Family** level — clauses 4–10 are management-system requirements |
| D | ISO 27001:2022 Annex A | Control level |
| E | NIST CSF 2.0 Function | Derived from the subcategory prefix |
| F | NIST CSF 2.0 Subcategory | Control level |
| G | CIS v8.1 Control | Major number, deduplicated |
| H | CIS v8.1 Safeguard | Full `major.minor` |
| I | SOC 2 CC Series | Series letters only |
| J | SOC 2 Criteria | Full criterion |
| K | OWASP ASVS 4.0.3 Chapter | **Unmapped for all v0.1 controls** (F-06) |
| L | OWASP Top 10:2021 | **Unmapped for all v0.1 controls** (F-06) |
| M | ISO/IEC 27034 Category | Family default: Application Security Controls / Verification / Development / Runtime / N/A |

---

## 14. MITRE_Matrix — GENERATED

| Location | Content |
|---|---|
| Row 2 (B) | Label |
| Row 3 (C:M) | Count of controls mapped per tactic |
| A4:B4 | Headers |
| A:B | Control ID, Control Name |
| C–M | The 11 tactics: Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Exfiltration, Impact |
| P4:R4 | Secondary table headers: Technique ID, Technique name, Controls mapped |
| P5:P51 | The 47 techniques used, in use order |
| Q | Technique name from the build script's reference table |
| R | Controls mapped — `COUNTIF` with wildcard match, so a parent ID also counts its sub-techniques |

---

## 15. ZeroTrust_Matrix — GENERATED

| Location | Content |
|---|---|
| Row 2 (B) | "Controls per pillar" + counts |
| Row 3 (B) | "Share of controls" + percentages |
| A:B | Control ID, Control Name |
| C–H | Identity (15), Device (4), Network (10), Application (1), Data (9), Infrastructure (42) |
| I | Pillars — how many pillars the control touches |

---

## 16. Maturity_Model — 📖 REFERENCE

| Block | Rows | Content |
|---|---|---|
| Levels | 5–10 | Level, name, definition, typical evidence, coverage, characteristics |
| Scoring rules | 13–18 | The six caps. Merged across A:F |

Edit the rules text if a client's methodology differs — and say so in report
section 3.

---

## 17. Risk_Model — 🔒 CONFIG

**Fixed layout. Do not insert or delete rows** — the lookup ranges are hard-coded
(F-10).

| Block | Rows | Content |
|---|---|---|
| Likelihood scale | 5–9 | Level, label, description |
| Impact scale | 13–17 | Level, label + 5 business dimensions. **Blue = editable** |
| Inherent matrix | 21–25 | `L × I` grid, coloured by band |
| Rating bands | 30–33 | **Lower bound, rating, expected response, timeline.** Referenced as `$A$30:$A$33` / `$B$30:$B$33` by every rating formula in the workbook |
| Effectiveness | 38–43 | Maturity, level name, risk reduction. Referenced as `$A$38:$A$43` / `$C$38:$C$43` |

Edit impact thresholds and effectiveness percentages freely. Inserting a **row**
breaks every rating formula silently — add at the bottom and update the hard-coded
ranges in `build_workbook.py` instead.

---

## 18. Domain_Registry

Live build status, generated from `meta.yaml` with live counts.

| Col | Name | Type | Notes |
|---|---|---|---|
| A | No. | 📚 GENERATED | 1–18 |
| B | Code | 📚 GENERATED | GOV, AST, IAM, END, SRV, NET, M365, CLD, APP, API, SOC, VLM, DPR, BKP, DSO, GWS, OT, AI |
| C | Domain | 📚 GENERATED | |
| D | Scope | 📚 GENERATED | One-line scope description |
| E | Target controls | 🔒 CONFIG | Blue = editable. Sum **905** |
| F | Controls built | ⚙️ FORMULA | Live `COUNTIF` over `Control_Library` |
| G | % of target | ⚙️ FORMULA | |
| H | Proposed batch | 🔒 CONFIG | Batch 1–4, Pilot, Placeholder |
| I | Status | ⚙️ FORMULA | Placeholder / Not started / In progress / Complete |

Total row sums E and F. Note beneath records the 905 vs "700+" discrepancy
(F-05).

---

## 19. Lists — 🔒 CONFIG

16 drop-down source lists laid out in columns A–P, headers on row 3, values from
row 4. **Every data validation in the workbook points here.**

| Col | List | Values |
|---|---|---|
| A | Severity | Critical, High, Medium, Low, Informational (5) |
| B | Finding status | Open, In Progress, Remediated, Risk Accepted, Closed (5) |
| C | Remediation status | Not Started, In Progress, Blocked, Completed, Verified, Deferred (6) |
| D | Priority | P1 Urgent, P2 High, P3 Medium, P4 Low (4) |
| E | Risk treatment | Mitigate, Accept, Transfer, Avoid (4) |
| F | Evidence type | 16 types (see Evidence_Register) |
| G | Evidence review | Pending, Accepted, Rejected, Needs more (4) |
| H | Collection method | Manual, Automated, Client-provided (3) |
| I | Yes/No | Yes, No (2) |
| J | Org tier | SMB, Mid-size, Enterprise, Multinational, Government (5) |
| K | Confidentiality | Public, Internal, Confidential, Restricted (4) |
| L | Request status | Not requested, Requested, Received, Partial, Not available, N/A (6) |
| M | Path category | External, Internal, Cloud, Identity, Supply Chain (5) |
| N | Maturity | 0, 1, 2, 3, 4, 5 (6) |
| O | Score 1-5 | 1, 2, 3, 4, 5 (5) |
| P | Business impact | Financial, Operational, Regulatory, Reputational, Safety, Data (6) |

To add a value, extend the list in `Lists` — never edit a cell's validation
directly. Removing a value that is already in use breaks the drop-down for those
rows.

---

## Cross-sheet formula dependencies

Understanding these prevents most "why is this wrong" questions.

```
Scope!C4, C6, C7 ──────────────► Dashboard!B2 (client and period header)
Scope!C13 ─────────────────────► Assessment!L (target maturity)
Scope!C24:C41 (domain) ────────► Assessment!J (applicable, domain test)
Scope!C18:C20 (platform) ──────► Assessment!J (applicable, platform test)
Assessment!K (current) ────────► Dashboard tiles, domain/family scores, trends
                                ► Assessment!X (effectiveness)
                                ► Risk_Register!K (control maturity)
Assessment!T,U ─► V ─► W,Y ─► X ─► Y ─► Z
Assessment!AA ──────────────────► Dashboard top-10 (LARGE + MATCH)
Assessment!Y,Z ───────────────► Dashboard residual distribution
Risk_Model!$A$30:$A$33 ────────► every rating formula in the workbook
Risk_Model!$C$38:$C$43 ────────► every residual calculation
Risk_Model!$B$38:$B$43 (via A) ─► effectiveness lookup by maturity
Assessment!A ─────────────────► Evidence_Register!C, Findings_Register!C/D,
                                Risk_Register!C, Remediation_Tracker!C/D,
                                all Control ID drop-downs
Lists ────────────────────────► every drop-down in the workbook
Control_Library!A:B ───────────► Domain_Registry!F, Dashboard domain counts
Findings_Register!F,K,N ───────► Dashboard findings overview and open-finding tile
Crown_Jewels!A ────────────────► Attack_Paths!C drop-down
```

**Consequence:** insert or delete rows in the middle of `Assessment`,
`Findings_Register`, `Risk_Register`, `Remediation_Tracker`, `Evidence_Register`
or `Crown_Jewels` and formula ranges will silently misalign. Append at the
bottom, or extend the ranges in `build_workbook.py` and rebuild.