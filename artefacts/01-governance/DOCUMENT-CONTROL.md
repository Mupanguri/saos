# Document Control

## SAOS — Security Assessment Operating System

| Field | Value |
|---|---|
| Document title | SAOS Source Library and Assessment Toolkit |
| Artefact set | `artefacts/` |
| Version | **v0.1** |
| Release name | Phase 0 foundations + Server Security pilot |
| Status | **Pilot complete — not for unrestricted client issue** |
| Version scheme | `MAJOR.MINOR`. Minor = additive (new domains, controls, fields). Major = breaking change to the control schema, the risk model or the workbook layout. |
| Canonical source | `artefacts/06-source/library/` (YAML) |
| Classification | Internal — contains assessment methodology and control IP |
| Contains client data | **No.** See QA finding F-01. |

## Release contents

| Component | Version | Location |
|---|---|---|
| Control library (YAML) | 0.1 | `06-source/library/` |
| Domain + family registry | 0.1 | `06-source/library/meta.yaml` |
| Workbook builder | 0.1 | `06-source/build/build_workbook.py` |
| Report builder | 0.1 | `06-source/build/build_report.js` |
| Blank engagement workbook | 0.1 | `05-deliverables/SAOS-Assessment-Workbook-v0.1-BLANK.xlsx` |
| sample workbook | 0.1 | `05-deliverables/SAOS-Assessment-Workbook-v0.1-SAMPLE.xlsx` |
| Report template | 0.1 | `05-deliverables/SAOS-Executive-Report-Template-v0.1.docx` |
| Catalogue exports | 0.1 | `03-library/control-catalogue.{csv,json}` + 4 more |
| Control schema | 0.1 | `03-library/control-schema.json` |
| Library validator | 0.1 | `03-library/validate_library.py` |
| Library exporter | 0.1 | `03-library/export_library.py` |

## Build identity

| | |
|---|---|
| Library snapshot | 2026-10-04 (file timestamps on `06-source/library/**`) |
| Blank workbook build stamp | 2025-11-28 (from its `README` sheet — see F-02) |
| sample workbook build stamp | 2026-10-04 (from its `README` sheet) |
| Script `BUILD_DATE` constant | 2026-10-04 (`build_workbook.py:21`) |
| Toolchain | Python 3.14.0, openpyxl 3.1.5, PyYAML 6.0.3, Node v25.1.0, docx 9.x |

The blank workbook's earlier stamp means it predates the current
`BUILD_DATE` constant. Its `Control_Library`, `Mapping_Matrix`,
`MITRE_Matrix`, `ZeroTrust_Matrix`, `Maturity_Model`, `Risk_Model`,
`Domain_Registry` and `Lists` sheets are byte-identical to the sample build, so
the **library content has not changed** — only the stamp. Rebuild before
distributing.

## Ownership

| Area | Owner | Notes |
|---|---|---|
| Methodology, risk and maturity models | Methodology owner | Changes here require a version bump and re-issue of the report template, because section 3 of the report describes them |
| Control library content | Domain owners per batch | One owner per domain in the build roadmap |
| Build tooling | Engineering | `build_workbook.py`, `build_report.js` |
| Schema and validator | Engineering | `control-schema.json`, `validate_library.py` |
| Framework mappings | Methodology owner **+** independent reviewer | Two-person rule — see `07-reference/FRAMEWORK-REFERENCES.md` |

Named individuals are deliberately not recorded here. Fill them in before this
document set is used for a real engagement.

## Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Author | | | |
| Technical reviewer | | | |
| Methodology reviewer | | | |
| Approves release | | | |

**No release may be issued to a client with an empty approvals table.**

## Change control

1. Control content changes go into a YAML file in `06-source/library/controls/`.
2. `python 03-library/validate_library.py --strict` must pass.
3. `python 03-library/export_library.py` regenerates the exports.
4. Rebuild the workbook and the report template.
5. Record the change in `CHANGELOG.md`.
6. Update the `VERSION` constant in `build_workbook.py` and this document.
7. Regenerate `MANIFEST.csv` / `MANIFEST.md`.
8. Obtain approvals.

## Distribution

| Audience | May receive | Must not receive |
|---|---|---|
| Internal assessors | Everything | — |
| Engagement team | Everything | — |
| Client | `05-deliverables/` (blank, template), methodology docs | `03-library/`, `06-source/`, QA findings, other clients' workbooks |
| External auditor / regulator | Final client report, evidence index | Internal roadmaps, QA findings, source |

## Retention

| Item | Retention |
|---|---|
| Source library and tooling | Permanent, version controlled |
| Blank and template deliverables | Permanent |
| Engagement workbooks | Per engagement policy and applicable regulation; typically 7 years where a SOC 2 or ISO scope exists |
| Evidence artefacts | Per engagement policy; evidence may contain client confidential data and personal data — apply the client's retention instruction |
| sample workbooks | Do not retain client-adjacent copies. This file must never be mistaken for client output. |

## Known blocking issues for release

| ID | Severity | Blocks release? |
|---|---|---|
| F-01 Delivered filename asserted an unsupported provenance | High | **Yes** — resolved in this packaging |
| F-02 Stale blank workbook build stamp | Medium | **Yes** — rebuild before issue |
| F-03 No dependency manifests | Medium | No — resolved in this packaging |
| F-04 Framework mappings unverified | Medium | **Yes** for client issue — two-person verification required |
| F-05 Domain target sum 905 vs "700+" | Medium | No — disclose in internal docs, resolve before external commitment |
| F-06..F-12 | Low / Info | No |

Full detail: `../07-reference/QA-FINDINGS.md`.