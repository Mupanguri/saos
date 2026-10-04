# Changelog

All notable changes to SAOS. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) adapted for a control
library — see `DOCUMENT-CONTROL.md` for the version scheme.

---

## [0.1] — 2026-10-04

Phase 0 foundations plus the first complete domain. This is the pilot release
whose purpose is to validate the pipeline end to end before the remaining 845
target controls are authored.

### Added — methodology

- **Maturity model**, levels 0–5, with definitions, typical evidence, coverage
  thresholds and six scoring rules that cap scores where evidence is thin
  (interview-only caps at 2; under 50% coverage caps at 2; under 90% caps at 3;
  design without proof of operation caps at 2).
- **Risk model.** Inherent = Likelihood × Impact (1–25). Residual = Inherent ×
  (1 − effectiveness at assessed maturity). Effectiveness by maturity: 0 / 10 /
  30 / 55 / 75 / 90%. Rating bands Low <5, Medium 5–9.9, High 10–16.9, Critical
  ≥17, with expected response and remediation timeline per band.
- **Impact scale** defined across five business dimensions (financial as a
  percentage of annual revenue, operational, regulatory and legal,
  reputational, data and confidentiality) rather than a bare 1–5.
- **Criticality weighting** (1–3 per control) so domain and family maturity
  averages are not distorted by trivial controls.

### Added — control library

- **Domain registry**: 18 domains with per-domain targets, scope descriptions
  and proposed build batches. Targets 1–15 from the project specification;
  domain 16 (Google Workspace, 50) is an explicit assumption; domains 17 (OT/ICS)
  and 18 (AI Systems) are placeholders with target 0.
- **Family registry**: 13 Server Security families with default references, ISO
  27001:2022 management-system clauses and ISO/IEC 27034 category defaults.
- **60 Server Security controls** across 13 families, each with 27 fields
  (objective, business justification, threat, assessment question, evidence
  items, validation procedure, test methods, automation potential and method,
  default likelihood and impact, criticality weight, three maturity anchors,
  remediation guidance, and six framework mappings).
- **257 individual evidence items** extracted from the library into a PBC list.
- **Framework mappings**: ISO/IEC 27001:2022 Annex A, NIST CSF 2.0, CIS
  Controls v8.1, SOC 2 (2017 TSC), MITRE ATT&CK, NIST SP 800-207 Zero Trust,
  with optional OWASP ASVS 4.0.3 and OWASP Top 10:2021 slots.
- **ATT&CK coverage**: 47 techniques across all 11 tactics.
- **Zero Trust coverage**: all six pillars; Infrastructure 42, Identity 15,
  Network 10, Data 9, Device 4, Application 1.

### Added — workbook generator

- `build_workbook.py` producing a 19-sheet engagement workbook: README, Scope,
  Dashboard, Assessment, Evidence_Requests, Evidence_Register,
  Findings_Register, Risk_Register, Remediation_Tracker, Crown_Jewels,
  Attack_Paths, Control_Library, Mapping_Matrix, MITRE_Matrix,
  ZeroTrust_Matrix, Maturity_Model, Risk_Model, Domain_Registry, Lists.
- **Live formula chain.** Applicability derives from Scope. Target maturity
  derives from the org tier table. Likelihood and impact honour per-control
  overrides. Inherent score, inherent rating, control effectiveness, residual
  score and residual rating all recalculate from the model sheets — no hardcoded
  results.
- **Weighted scoring** via `SUMPRODUCT` across domain, family and overall.
- **Dashboard**: 6 KPI tiles, domain table, family heat map, maturity
  distribution, inherent risk heat map, residual distribution, top 10 residual
  risks, findings overview, remediation and evidence overview, 7-period trend
  table, and 3 charts.
- **16 drop-down lists** in `Lists` driving all data validation.
- **Conditional formatting**: RAG colouring on every rating and status column,
  colour scale on maturity and gap columns, overdue and RAG highlighting.
- **Worked example rows** on all five registers (grey italic, excluded from all
  counts) so an assessor sees the expected shape of a good entry.
- **`--sample` mode** filling the workbook with synthetic data so the dashboard
  can be demonstrated without a client.

### Added — report template

- `build_report.js` producing a Word template: cover with classification,
  document control, version history, live table of contents, 8 body sections
  and 5 appendices, 14 tables, house styling, running header and page footer.
- **Guidance boxes** in the template telling the author what each section must
  achieve, and a rule to delete them before issue.
- **Red bracketed placeholders** so no placeholder can be missed in review.
- Report section 3 describes the maturity scale and risk rating tables so the
  report is self-contained for a non-technical reader.

### Added — documentation and tooling (this packaging)

- `README.md` at the delivery root: full system explanation, risk and maturity
  models, all 19 sheets, build and engagement instructions, format
  recommendations, known issues and roadmap.
- `artefacts/` folder structure with 13 documents across governance,
  methodology, workflows, reference and infrastructure.
- **`control-catalogue.csv`** and **`control-catalogue.json`** — 60 controls in
  flat and nested form for BI tools, notebooks and APIs.
- **`control-evidence.csv`** — the 257 evidence items as tidy data.
- **`domain-registry.csv`** and **`family-registry.csv`** with live build counts.
- **`framework-mapping.csv`** — long/tidy format, one row per control per
  framework, pivot-ready for coverage reporting.
- **`control-schema.json`** — JSON Schema (draft 2020-12) for one control, with
  patterns for every enumerated and shaped field.
- **`validate_library.py`** — independent validator: required and unknown
  fields, ID pattern and uniqueness, domain and family registration, all
  enumerations, ATT&CK tactic and technique resolution, mapping string shapes,
  per-family sequence contiguity, minimum content length. `--strict` mode for
  CI. Current state: PASS, 0 errors, 0 warnings.
- **`export_library.py`** — regenerates all six exports from YAML with SHA-256
  provenance recorded in the JSON.
- **`MANIFEST.csv`** and **`MANIFEST.md`** — SHA-256 inventory of every file.
- **`requirements.txt`**, **`package.json`** and **`package-lock.json`** — the
  dependency manifests the original delivery lacked (fixes F-03).
- **`BUILD-AND-VERIFY.md`** — reproducible build recipe including the
  LibreOffice recalculation step that caches formula values.

### Known issues at release

Twelve findings recorded in `../07-reference/QA-FINDINGS.md`:

- **F-01 (High)** — a delivered workbook's filename asserted a provenance its
  contents did not support. Resolved: renamed to
  `SAOS-Assessment-Workbook-v0.1-SAMPLE.xlsx`, and `--sample` mode now writes
  every identifying field as `Redacted`. Published in generalised form; see the
  note at the head of the finding.
- **F-02 (Medium)** — the blank workbook is stamped 2025-11-28 while the current
  script stamps 2026-10-04; library content is unchanged but the artefact is
  stale.
- **F-03 (Medium)** — no dependency manifests in the original delivery;
  `build_report.js` failed with `Cannot find module 'docx'`. Resolved here.
- **F-04 (Medium)** — framework mappings authored from working knowledge and
  requiring verification against licensed sources before client issue.
- **F-05 (Medium)** — domain targets sum to 905 against a stated "700+" goal.
- **F-06 (Low)** — ASVS version ambiguity (4.0.3 V1–V14 vs 5.0 2025);
  `asvs` and `owasp` unmapped for all 60 controls.
- **F-07 (Low)** — OT/ICS and AI Systems are placeholders; those sectors cannot
  be assessed with v0.1.
- **F-08 (Low)** — registers formatted for 200 rows; a full 905-control
  engagement needs them extended.
- **F-09 (Low)** — likelihood and impact overrides have no dedicated reason
  column.
- **F-10 (Low)** — `Risk_Model` lookup ranges are hard-coded row references;
  inserting a row silently breaks every rating formula.
- **F-11 (Info)** — report template has no document properties and the TOC field
  needs a manual refresh.
- **F-12 (Info)** — thin coverage in the Zero Trust Application pillar (1
  control) and ATT&CK Exfiltration tactic (1 group).

---

## [Unreleased]

Planned for v0.2. See `BUILD-ROADMAP.md` for sequencing.

### To do

- [ ] Split the library workbook out of the engagement workbook (one-line
      change to the `SHEETS` list in `build_workbook.py`)
- [ ] Adopt the `SAOS-<artefact>-v<version>[-<client>[-<period>]][-<state>]`
      naming convention across all deliverables
- [ ] Stamp retracted or superseded workbooks internally (README banner plus
      document properties), not just in the filename
- [ ] Replace the hard-coded `Risk_Model` row references with defined names or
      a lookup table
- [ ] Add an override-reason column for likelihood and impact overrides
- [ ] Extend register row counts beyond 200 for full-library engagements
- [ ] Golden-file test: build the workbook, hash the `Control_Library` sheet,
      compare to a committed baseline
- [ ] YAML lint step for tabs and trailing whitespace
- [ ] Resolve the 905 vs "700+" target discrepancy
- [ ] Resolve the ASVS version question before the Application Security batch
- [ ] Independent verification of all framework mappings (two-person rule)
- [ ] Batch 1: Identity and Access Management (60), Microsoft 365 (80),
      Cloud Security (100)