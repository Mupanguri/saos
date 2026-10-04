# File Format Guide

**The question:** how should SAOS files be represented, stored and named so they
stay usable as a library, an engagement record and a deliverable?

This is the assessment of the current formats, what to keep, what to add, what
to change, and the conventions to adopt.

---

## Summary of recommendations

| # | Recommendation | Effort | Impact |
|---|---|---|---|
| 1 | **Keep YAML as the canonical library format** | — | — |
| 2 | **Split the library workbook out of the engagement workbook** | 1 hour | High — stops generated content being edited and re-shipped to clients |
| 3 | **Adopt a strict filename convention** | 30 min | High — F-01 happened because filenames were free text |
| 4 | **Stamp retracted files internally, not just in the name** | 30 min | High — closes the data-governance gap in F-01 |
| 5 | **Publish the catalogue as CSV + JSON** | Done | High — YAML is unreadable to BI tools and non-technical reviewers |
| 6 | **Add a JSON Schema for the control contract** | Done | Medium — machine-checkable in any language or editor |
| 7 | **Ship the catalogue as tidy long-format data too** | Done | Medium — the wide matrix cannot be pivot-reported |
| 8 | **Add dependency manifests and a lock file** | Done | Medium — the build did not run out of the box (F-03) |
| 9 | **Ship a SHA-256 manifest** | Done | Medium — prove which version a client received |
| 10 | **Add a golden-file build test** | 2 hours | Medium — catch unintended library changes at review time |
| 11 | **Generate the report from the workbook rather than retyping figures** | 2–3 days | Medium — removes the main source of report/evidence drift |
| 12 | **Pin the framework standard editions in `meta.yaml`** | 1 hour | Medium — mappings must state which edition they target |

---

## 1. Keep the current choices

### YAML for the control library — correct, do not change

| Strength | Detail |
|---|---|
| Diffable | A control change is a readable text diff in a pull request. This is the whole reason the library is not a spreadsheet |
| Reviewable | A domain owner or a client can read a control without running anything |
| Structured | Nested mappings, block scalars, anchors — needed for 27 fields per control and multi-line procedures |
| Comments | Can carry rationale that does not need to survive into the schema |
| Diffable at scale | Adding a control is +30 lines in one file. Adding it to a spreadsheet creates a conflict for every concurrent editor |

The alternatives are worse for this use case:

| Alternative | Why not |
|---|---|
| **XLSX as source** | Binary diff. No review. Concurrent edits collide. Formulas and formatting become part of the source. The `ev` → PBC expansion and the ATT&CK parsing would need to be hand-maintained |
| **JSON** | No comments, and every field needs a comma. Strictly worse to hand-edit than YAML for the same data |
| **A database** | Correct for querying, wrong for authoring. Review happens in a diff, not in a grid |
| **Markdown** | No structure guarantee; validation becomes string matching |

**One caveat:** YAML 1.1 has the footguns listed in
`../02-methodology/CONTROL-SCHEMA.md`. They are all avoidable, all documented,
and two are now caught by the validator. Keep YAML.

### XLSX for the engagement workbook — correct

Assessors need filters, freeze panes, data validation, conditional formatting,
colour scales, named formula ranges and charts. A web form or CSV cannot do
that, and asking an assessor to type scores into a web form during a client
site visit is a different product with a different failure mode.

The formats are complementary, not competing: YAML for the library, XLSX for the
data, and now CSV/JSON for the interchange.

---

## 2. Split the library workbook out of the engagement workbook

**Current state — one workbook, 19 sheets, two audiences:**

```
Server Security assessment for Client A.xlsx   ← 419 KB
├── README, Scope, Dashboard                   engagement
├── Assessment, 5 registers, Crown_Jewels…     engagement
├── Control_Library        60 × 33             ← GENERATED REFERENCE
├── Mapping_Matrix         60 × 13             ← GENERATED REFERENCE
├── MITRE_Matrix           60 × 11             ← GENERATED REFERENCE
├── ZeroTrust_Matrix       60 × 9              ← GENERATED REFERENCE
└── Maturity_Model, Risk_Model, Domain_Registry, Lists   CONFIGURATION
```

Four generated reference sheets travel inside every client file. That produces
four problems:

1. **An assessor can edit generated content.** The `Control_Library` sheet is
   editable. Nothing stops someone changing a control name, and the next build
   silently reverts it — or worse, it does not get rebuilt and the client's
   report references a control that does not exist in the library.
2. **The library re-ships on every engagement.** A change made for Client A
   appears in Client B's file. Version confusion, and a confidentiality problem
   if per-client tailoring was applied.
3. **No integrity guarantee.** Nothing in the file proves which library version
   it was built from. Today the answer is only "read the README build date" —
   and the blank workbook's date is stale (F-02).
4. **The version of the *reference* is invisible.** The report quotes a workbook
   version that covers library and engagement data together.

### The split

```
SAOS-Library-and-Method-v0.1.xlsx          READ-ONLY REFERENCE
├── README, Control_Library, Mapping_Matrix, MITRE_Matrix, ZeroTrust_Matrix
├── Maturity_Model, Risk_Model, Domain_Registry, Lists
└── Version banner: "Library v0.1 — SHA-256 in MANIFEST.csv"

SAOS-Assessment-Workbook-v0.1-<Client>-<period>.xlsx    PER ENGAGEMENT
├── README, Scope, Dashboard, Assessment
├── 5 registers, Crown_Jewels, Attack_Paths
└── Risk_Model reference copy (read-only, so risk maths is auditable)
```

`Risk_Model` appears in both: the engagement needs it to calculate, and the
auditor needs to see the parameters the risk was calculated with. It must be an
identical copy — if a client recalibrates thresholds, that is a documented,
disclosed change, not a silent divergence.

**Implementation.** The generator already supports this. `build_workbook.py:169`
defines the sheet list; split it into two lists, write two workbooks, and add
the parameters as CLI flags:

```powershell
python build\build_workbook.py --library SAOS-Library-and-Method-v0.1.xlsx
python build\build_workbook.py --engagement SAOS-Assessment-Workbook-v0.1-ACL-2026Q3.xlsx
```

Roughly 1 hour. Highest-value single change on this list.

### Interim mitigation, before the split

If you do not split immediately, at minimum:

- Mark the four generated sheets as protected in the delivered workbook.
- Add a version-and-hash line to the `README` sheet so the library version is
  visible in the file.
- Add the library SHA-256 to the report's Document Control.

---

## 3. Filename convention

**Current filenames and what is wrong with them:**

```
SAOS Assessment Workbook v0.1.xlsx                              spaces, no state, no client
SAOS Workbook v0.1 <client> retracted Data.xlsx                 ambiguous, name contradicted contents (F-01)
SAOS Executive Report Template.docx                              no version
SAOS_Source_Library_v0.1/                                       underscores, no separator convention
artefacts/03-library/control-catalogue.csv                      no version
```

Mixed case, spaces, underscores and no consistent separator. That forces quoting
in every shell command, breaks scripted sorting, and — as F-01 demonstrates —
allows a filename to make a claim the contents do not support.

### Adopt

```
SAOS-<ARTEFACT>-v<VERSION>[-<CLIENT>[-<PERIOD>]][-<STATE>].<ext>
```

| Part | Values |
|---|---|
| `ARTEFACT` | `Library-and-Method`, `Assessment-Workbook`, `Executive-Report`, `Control-Catalogue`, `Evidence-Index` |
| `VERSION` | `v0.1`, `v0.2`, `v1.0` — always present, including on templates |
| `CLIENT` | Omit for templates and the library. Use a short stable token, not the full legal name |
| `PERIOD` | `2026Q3`, `2026-09` |
| `STATE` | `BLANK` · `SAMPLE` · `DRAFT` · `FINAL` · `SUPERSEDED` — always upper case |

### Examples

```
SAOS-Library-and-Method-v0.1.xlsx
SAOS-Assessment-Workbook-v0.1-BLANK.xlsx
SAOS-Assessment-Workbook-v0.1-SAMPLE.xlsx
SAOS-Assessment-Workbook-v0.1-ACL-2026Q3-DRAFT.xlsx
SAOS-Assessment-Workbook-v0.1-ACL-2026Q3-FINAL.xlsx
SAOS-Assessment-Workbook-v0.1-ACL-2026Q3-SUPERSEDED.xlsx
SAOS-Executive-Report-Template-v0.1.docx
SAOS-Executive-Report-v0.1-ACL-2026Q3-DRAFT.pdf
SAOS-Control-Catalogue-v0.1.csv
SAOS-Control-Catalogue-v0.1.json
```

### Separator rules

| Context | Convention | Reason |
|---|---|---|
| Filenames | `kebab-case` with `-` | No quoting needed in any shell; sorts predictably |
| Directory names | `NN-kebab-case` | Numeric prefix sorts into reading order |
| YAML keys | `snake_case` | Matches YAML conventions and the existing code |
| Python / JavaScript | `snake_case` / `camelCase` | Language convention |
| Sheet names | `PascalCase` | Excel convention, no spaces so formulas need no quoting |
| Column headers | `Title Case` | Matches the existing workbook |
| CSV columns | `snake_case` | Machine-friendly |

---

## 4. Stamp retracted and superseded files internally

F-01 is the argument. A delivered workbook carried a filename asserting it held
a specific client's engagement data when it held synthetic sample data. A reader
who trusted the filename would have handled it as confidential client data — or,
worse, concluded an engagement existed and reported numbers that were never
measured.

**A retraction that lives only in the filename is not a retraction.** Anyone
who received the file before the rename still has a file that looks authoritative.

### When a file is retracted or superseded

1. **Do not delete it.** Retained as evidence of what was issued and when.
2. **Rename** with the `-SUPERSEDED` suffix and never reuse the token.
3. **Stamp the inside of the file** — the only part that survives a copy-paste or
   an email forward:

   | Where | What |
   |---|---|
   | Workbook `README` sheet, row 2 | `**SUPERSEDED <date>** — replaced by <filename>. Do not use.` |
   | Workbook `Scope!C4` | Prefixed `[SUPERSEDED]` |
   | Document properties | `title` = `SUPERSEDED — <original title>` |
   | Report cover | `SUPERSEDED` watermark or banner above the classification |
   | Report Document Control | Superseded-by row in the version history |
   | File name | `-SUPERSEDED` suffix |

4. **Record it** in `../01-governance/CHANGELOG.md` and `MANIFEST.csv`, with the
   reason and the replacement.
5. **Notify everyone** who received the original, in writing.

### Data classification in filenames

Where a filename will be visible outside your control (email subject, shared
drive listing), add a classification prefix:

```
CLIENT-ACL-CONFIDENTIAL-SAOS-Assessment-Workbook-v0.1-ACL-2026Q3-DRAFT.xlsx
```

Not necessary for the library. Necessary for anything client-derived.

---

## 5. The catalogue exports — added

`../03-library/` now contains six generated exports. The problem they solve:
**YAML is unreadable by BI tools and non-technical reviewers**, so a coverage
question ("how many controls map to CIS 4.1?") cannot be answered without a
build.

| File | Shape | Use |
|---|---|---|
| `control-catalogue.csv` | Wide, 60 rows × 34 cols | Excel, BI import, bulk review |
| `control-catalogue.json` | Nested, with registry and reference tables | API, notebooks, version diffing |
| `control-evidence.csv` | Long, 257 rows | PBC list, request tracking, bulk email merge |
| `domain-registry.csv` | 18 rows + total | Roadmap reporting |
| `family-registry.csv` | 13 rows | Family reference, ownership |
| `framework-mapping.csv` | **Long/tidy**, one row per control per framework | Coverage reporting, pivot tables |

### Why the long format matters

The `Mapping_Matrix` sheet is **wide** — one column per framework:

```
Control ID | ISO Clause | ISO Annex A | CSF Function | CSF Subcategory | CIS Control | CIS Safeguard | SOC Series | SOC Criteria | ASVS | OWASP | 27034
```

That is right for reading across one control. It is **unusable** for the
question a coverage report asks: "how many controls map to each ISO clause?"
Answering that on a wide table means 12 separate `COUNTIF`s or a manual
unpivot.

The long format is one row per mapping:

```
control_id | control_name | framework | mapping | mapping_level
SRV-PHY-01  | …            | ISO/IEC 27001:2022 Annex A | A.7.1, A.7.2 | control
SRV-PHY-01  | …            | NIST CSF 2.0 | PR.AA-06 | control
SRV-PHY-01  | …            | ISO/IEC 27001:2022 management system | 6.1.3, 8.1 | family
```

Now coverage is `GROUP BY framework, mapping`, and every framework is a row
rather than a column that has to be anticipated in advance. `mapping_level`
(`control` vs `family`) preserves the distinction between an Annex A control and
a management-system clause.

**Rule of thumb:** wide for human reading, long for machine analysis, JSON for
nesting. Ship all three; do not try to make one file do all three jobs.

### CSV encoding

All CSVs are written **UTF-8 with BOM** (`utf-8-sig`). Without the BOM, Excel on
Windows opens UTF-8 CSVs in the local code page and mangles every non-ASCII
character. This is a real, recurring problem and it is why the exporter is
explicit about the encoding.

---

## 6. JSON Schema for the contract

`../03-library/control-schema.json` (JSON Schema draft 2020-12) makes the YAML
contract machine-checkable in any language or editor.

What it buys:

- **Editor validation** — VS Code, IntelliJ and Neovim validate YAML against a
  JSON Schema as you type, before any script runs.
- **Language independence** — the contract is not expressed in Python, so a
  JavaScript or Go tool can consume it.
- **Documentation that cannot drift** — the descriptions are the field reference.
- **Generated documentation** — field reference, forms and validation can all be
  derived from it.

What it deliberately does **not** do: replace `validate_library.py`. The schema
validates one control in isolation; the validator additionally checks
cross-document concerns — ID uniqueness across files, domain and family
registration, and per-family sequence contiguity.

---

## 7. Build tooling and reproducibility

### F-03: the build did not run out of the box

`build_report.js` requires the `docx` package. The original delivery shipped no
`package.json`, no lock file and no `node_modules`, so:

```
Error: Cannot find module 'docx'
```

Note that `node_modules` in the *working directory* does not help — Node resolves
modules by walking up from the **script's own directory**. A `package.json` must
exist at or above `build/`.

Now supplied:

| File | Purpose |
|---|---|
| `../08-infrastructure/requirements.txt` | Python deps with version ranges |
| `../08-infrastructure/package.json` | Node dependency and script definitions |
| `../08-infrastructure/package-lock.json` | Exact resolved versions for reproducible builds |

### Dependency policy

| Rule | Reason |
|---|---|
| Pin minor versions, range major | `openpyxl>=3.1,<4` — allows fixes, blocks breaking changes |
| Commit the lock file | Builds are reproducible only with exact versions |
| No runtime network access | Both scripts are offline and deterministic |
| Declare every import explicitly | `build_workbook.py` also uses `yaml`, not just `openpyxl` |

### Record the toolchain

`DOCUMENT-CONTROL.md` now records the exact versions used for this build
(Python 3.14.0, openpyxl 3.1.5, PyYAML 6.0.3, Node v25.1.0, docx 9.x).
"Which version of openpyxl generated this file?" is otherwise unanswerable a year
later.

### The recalculation step

`openpyxl` writes formulas but cannot evaluate them. A freshly built workbook has
**no cached values**. Excel recalculates on open and shows correct numbers;
`pandas`, most previewers and any automated report generator see `None`.

This is why the shipped workbook carries a `calcChain` part and cached values —
someone opened and saved it in Excel or LibreOffice. **The step is mandatory, not
optional.** Full recipe, verified:
`../08-infrastructure/BUILD-AND-VERIFY.md`.

---

## 8. Integrity and provenance

`MANIFEST.csv` and `MANIFEST.md` record every file with its SHA-256, size, role
and provenance.

| Question the manifest answers |
|---|
| Is this the version I think it is? |
| Has anything changed since delivery? |
| Can I prove to a client exactly what they received? |
| Which library files produced this workbook? |

`control-catalogue.json` additionally embeds the SHA-256 of each source YAML
file, so a catalogue export is traceable to the exact library snapshot that
produced it.

---

## 9. Add tests

There are currently no tests beyond the validator. Two additions, in order of
value:

**1. Golden-file test** (2 hours)

```python
# build the workbook, hash the Control_Library sheet, compare to a committed baseline
# any diff means an unintended library change and must be reviewed deliberately
```

Catches at review time what currently surfaces at client time.

**2. Export round-trip test** (1 hour)

Export the catalogue to CSV, read it back, and assert the field count, the
control count, no duplicate IDs and no empty required fields. Catches exporter
bugs that would otherwise ship silently.

Both belong in CI alongside `validate_library.py --strict`.

---

## 10. Framework edition pinning

The mappings reference specific editions: ISO/IEC 27001:2022, NIST CSF 2.0,
CIS Controls v8.1, SOC 2 (2017 TSC), NIST SP 800-207, OWASP ASVS 4.0.3, OWASP
Top 10:2021.

These editions change. Today `meta.yaml` records edition numbers in free text
inside the `ref` strings, which is not machine-checkable and will not be updated
when an edition is superseded.

### Add a pin block to `meta.yaml`

```yaml
framework_editions:
  iso_iec_27001_2022: {edition: '2022', status: verified, verified_by: '', verified_on: ''}
  iso_iec_27002_2022: {edition: '2022', status: verified, verified_by: '', verified_on: ''}
  nist_csf_20:          {edition: '2.0', status: verified, verified_by: '', verified_on: ''}
  cis_controls_v8:      {edition: '8.1', status: unverified, verified_by: '', verified_on: ''}
  soc2_tsc:             {edition: '2017', status: unverified, verified_by: '', verified_on: ''}
  nist_sp_800_207:      {edition: 'Rev.1', status: unverified, verified_by: '', verified_on: ''}
  owasp_asvs:           {edition: '4.0.3', status: pending_decision, note: '5.0 (2025) restructured chapters; resolve before Batch 4 (F-06)'}
  owasp_top_10:         {edition: '2021', status: unverified, verified_by: '', verified_on: ''}
  mitre_attack:         {edition: 'Enterprise', status: unverified, note: 're-validate technique IDs on upgrade'}
```

This turns F-04 from a footnote into a trackable status per framework, gives the
exporter a machine-readable field, and lets a future build refuse to ship
`unverified` mappings to a client.

---

## 11. Generate the report rather than retyping it

Today the report is a template and the assessor copies Dashboard figures into it
by hand. That is the main remaining route by which the report and the evidence
can drift.

### Target

```
Engagement workbook (completed)
    │
    ├─► Dashboard figures ──► Executive summary tiles, domain table, findings counts
    ├─► Top 10 residual ────► Section 5 risk scenarios
    ├─► Evidence_Register ──► Appendix C evidence index
    ├─► Findings_Register ──► Section 7 + Appendix A
    └─► Risk_Register ──────► Appendix D

    build_report.js <workbook.xlsx> <output.docx> --fill
```

`build_report.js` already reads the workbook structure conceptually; adding
`--fill` with an XLSX reader on the Node side, or generating a JSON intermediate
from Python and passing that to Node, keeps the Word layout code unchanged.

**Effort:** 2–3 days. **Value:** removes an entire class of report error, and
makes "the report says 24 controls with a gap, the workbook says 23" impossible.

**Keep the template as a template.** `--fill` populates figures; the narrative
sections remain the assessor's, because the judgement is the deliverable.

---

## 12. Directory structure

```
SAOS/                                     # the project, in version control
├── README.md
├── src/
│   ├── library/
│   │   ├── meta.yaml
│   │   └── controls/
│   │       ├── 05_srv_part1.yaml
│   │       └── …
│   └── build/
│       ├── build_workbook.py
│       └── build_report.js
├── requirements.txt
├── package.json
├── package-lock.json
├── tests/
│   ├── validate_library.py
│   ├── export_library.py
│   └── test_golden.py
└── dist/                                # generated; gitignored
    ├── SAOS-Library-and-Method-v0.1.xlsx
    ├── SAOS-Assessment-Workbook-v0.1-BLANK.xlsx
    ├── SAOS-Executive-Report-Template-v0.1.docx
    ├── SAOS-Control-Catalogue-v0.1.csv
    ├── SAOS-Control-Catalogue-v0.1.json
    └── MANIFEST.csv

engagements/                             # client work; access-controlled, NOT in version control
└── ACL-2026Q3/
    ├── SAOS-Assessment-Workbook-v0.1-ACL-2026Q3-FINAL.xlsx
    ├── SAOS-Executive-Report-v0.1-ACL-2026Q3-FINAL.pdf
    ├── evidence/
    └── engagement-file.md               # calibration changes, overrides, decisions
```

**Library and engagement data must not live in the same place.** The library is
version-controlled, non-confidential and shared. Engagement data is confidential,
access-controlled, retention-managed and per-client. Putting them in one folder
is how a client's workbook ends up attached to an email to another client.

**`dist/` is generated.** Never edit it and never treat it as source. The YAML is
the source; `dist/` is what came out of the build.

---

## 13. Anti-patterns to avoid

| Anti-pattern | Why it hurts | Do instead |
|---|---|---|
| Editing `Control_Library` in Excel | Silently reverted on the next build | Edit the YAML, rebuild |
| Reusing a previous client's workbook as a starting point | Cross-client data leakage | Always start from `-BLANK` |
| Naming a file after a client without checking its contents | F-01 | `-SAMPLE` suffix; check the README banner before issue |
| Deleting a retracted file | Loses the record of what was issued | `-SUPERSEDED` and stamp the inside |
| Storing `node_modules` in version control | 13 MB and 412 files of noise | `.gitignore`, install from the lock file |
| Hand-editing generated CSVs | Overwritten on the next export | Rerun `export_library.py` |
| Version in a filename only | Invisible inside the file | Version in the filename **and** the README sheet **and** Document Control |
| Sending a freshly built workbook without recalculating | Previewers and `pandas` see blanks | Recalculate first |
| Inserting rows mid-table in a register | Formula ranges misalign silently | Append at the bottom, or extend and rebuild |
| Committing client data to version control | Unrecoverable confidentiality breach | `engagements/` outside the repository |

---

## 14. Recommended sequence

**Now, before the next engagement**

1. Rename the deliverables to the convention above. *(30 min)*
2. Stamp the sample workbook internally as sample data. *(15 min)*
3. Add the manifests and lock files. *(done)*
4. Ship the catalogue exports. *(done)*
5. Rebuild the blank workbook so its build stamp is current. *(5 min)*
6. Recalculate and confirm cached values are present. *(5 min)*

**Before Batch 1 ships**

7. Split the library workbook from the engagement workbook. *(1 hour)*
8. Add the framework edition pin block to `meta.yaml`. *(1 hour)*
9. Add the golden-file test and wire `validate_library.py --strict` into review. *(3 hours)*
10. Verify framework mappings with a second reviewer. *(2–3 days)*

**When there is time**

11. Implement `build_report.js --fill`. *(2–3 days)*
12. Extend register row counts past 200 for full-library engagements. *(1 hour)*
13. Add the override-reason column. *(1 hour)*

---

## Related documents

| Document | Covers |
|---|---|
| `../02-methodology/CONTROL-SCHEMA.md` | The 27 fields, YAML gotchas, validation |
| `../03-library/control-schema.json` | The machine-checkable contract |
| `../07-reference/QA-FINDINGS.md` | The 12 known issues these recommendations address |
| `../08-infrastructure/BUILD-AND-VERIFY.md` | Reproducible build, including recalculation |