# Artefacts — SAOS v0.1

Organised, documented and machine-readable packaging of the SAOS v0.1 delivery.
Generated from the canonical YAML library. Start with `../README.md` for the
system overview, then use this folder as the reference.

## Contents

| # | Folder | What is in it |
|---|---|---|
| — | `MANIFEST.md` / `MANIFEST.csv` | Every file with size, SHA-256, role and provenance |
| 01 | [`01-governance/`](01-governance/) | Document control, changelog, build roadmap |
| 02 | [`02-methodology/`](02-methodology/) | Methodology, data dictionary, control schema |
| 03 | [`03-library/`](03-library/) | Catalogue exports, JSON Schema, exporter, validator |
| 04 | [`04-workflows/`](04-workflows/) | Engagement runbook, evidence handling |
| 05 | [`05-deliverables/`](05-deliverables/) | The three client-facing files |
| 06 | [`06-source/`](06-source/) | The buildable source project |
| 07 | [`07-reference/`](07-reference/) | File-format guide, QA findings, framework references |
| 08 | [`08-infrastructure/`](08-infrastructure/) | Dependency manifests, build and verify, and publishing to GitHub |

36 files, 1,271 KB, SHA-256 recorded for every one.

## Read in this order

**If you are new to SAOS**
1. `../README.md` — the system, the risk and maturity models, all 19 sheets
2. `02-methodology/METHODOLOGY.md` — the scoring method in depth
3. `04-workflows/ENGAGEMENT-RUNBOOK.md` — how an engagement actually runs

**If you are writing controls**
1. `02-methodology/CONTROL-SCHEMA.md` — every field, with examples
2. `03-library/control-schema.json` — the machine-checkable contract
3. `03-library/validate_library.py` — run it before you build
4. `03-library/control-catalogue.csv` — the existing 60 as a worked example

**If you are integrating SAOS into a pipeline**
1. `07-reference/FILE-FORMAT-GUIDE.md` — formats, naming, split strategy
2. `03-library/control-catalogue.json` — the stable API surface
3. `03-library/framework-mapping.csv` — tidy data for coverage reporting
4. `08-infrastructure/BUILD-AND-VERIFY.md` — reproducible build recipe

**If you are reviewing or signing off**
1. `07-reference/QA-FINDINGS.md` — 12 known issues, 1 high severity
2. `07-reference/FRAMEWORK-REFERENCES.md` — what must be verified before issue
3. `01-governance/DOCUMENT-CONTROL.md` — version, ownership, approvals

## Key facts

| | |
|---|---|
| Version | v0.1 — Phase 0 foundations + Server Security pilot |
| Controls | 60 of 905 target (6.6%) |
| Domains built | 1 of 18 (SRV) |
| Families | 13 |
| Evidence items | 257 |
| ATT&CK techniques | 47 (all tactics covered) |
| Framework mappings | ISO/IEC 27001:2022, NIST CSF 2.0, CIS v8.1, SOC 2, MITRE ATT&CK, NIST SP 800-207, OWASP ASVS 4.0.3, OWASP Top 10:2021, ISO/IEC 27034 |
| Canonical source | `06-source/library/*.yaml` |
| Toolchain | Python 3.9+ (openpyxl, PyYAML), Node 18+ (docx) |
| Validator state | PASS — 60 controls, 0 errors, 0 warnings |

## ⚠ Read this before circulating anything

`05-deliverables/SAOS-Assessment-Workbook-v0.1-SAMPLE.xlsx` is **synthetic
sample data for demonstrating the dashboard.** It is not a client deliverable
and contains no client information — every identifying field is written as
`Redacted`. Its `README` sheet says so in the build banner. See
`07-reference/QA-FINDINGS.md` finding **F-01** for why this warning exists and
why the filename convention is mandatory.

Framework mappings are indicative professional judgement authored from working
knowledge of the published frameworks. **They must be verified against the
licensed source documents before being issued to a client.** See
`07-reference/FRAMEWORK-REFERENCES.md`.

## Reproducing this folder

```powershell
python -m pip install -r 08-infrastructure\requirements.txt
python 03-library\validate_library.py
python 03-library\export_library.py
python 06-source\build\build_workbook.py <out>.xlsx --sample
cd 06-source ; npm install ; node build\build_report.js <out>.docx
```

All four were run and pass against this packaging. See
`08-infrastructure/BUILD-AND-VERIFY.md`.