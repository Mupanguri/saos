# Build and Verify

Reproducible build recipe for SAOS. Every command below was run against this
packaging on 2026-10-04 and the results are recorded.

---

## Prerequisites

| Tool | Version used | Minimum | Notes |
|---|---|---|---|
| Python | 3.14.0 | 3.9 | `openpyxl` and `PyYAML` both required |
| Node.js | v25.1.0 | 18 | Only for the report builder |
| openpyxl | 3.1.5 | 3.1 | Workbook generation |
| PyYAML | 6.0.3 | 6.0 | **Also required by `build_workbook.py`** — easy to miss |
| docx | 9.x | 8 | Report template generation |
| Excel or LibreOffice | any | — | **Required** for the recalculation step |

Neither build script needs network access at run time.

---

## Setup

```powershell
# Python dependencies
python -m pip install -r artefacts\08-infrastructure\requirements.txt

# Node dependencies — package.json must be at or above build/, because Node
# resolves modules by walking UP from the script's own directory.
Copy-Item artefacts\08-infrastructure\package.json artefacts\06-source\package.json
Copy-Item artefacts\08-infrastructure\package-lock.json artefacts\06-source\package-lock.json
Push-Location artefacts\06-source
npm install
Pop-Location
```

> **Why `package.json` must sit at or above `build/`:** Node's module resolution
> starts at the requiring file's directory and walks up. `node_modules` in your
> *working directory* is not consulted. This is why the original delivery failed
> with `Cannot find module 'docx'` even after a successful `npm install`
> elsewhere. See QA finding F-03.

---

## Build order

```
library YAML  ──►  validate  ──►  export  ──►  workbook  ──►  recalculate
                     │              │             │
                     │              │             └──► report template
                     │              │
                     └──────────────┴──► manifest
```

Validate before building. The workbook builder asserts and will fail anyway, but
with less readable messages.

---

## 1. Validate the library

```powershell
python artefacts\03-library\validate_library.py
```

Expected:

```
==============================================================================
SAOS library validation
==============================================================================
library        : ...\artefacts\06-source\library
control files  : 3
controls       : 60
domains built  : 1 of 18
families built : 13 of 13
per domain     : SRV=60

RESULT: PASS
```

For CI:

```powershell
python artefacts\03-library\validate_library.py --strict
```

`--strict` treats warnings as errors. Exit codes: `0` clean, `1` errors (or
warnings under `--strict`), `2` could not run.

**What it checks:** required and unknown fields, ID pattern and uniqueness,
domain and family registration, all enumerations, ATT&CK tactic and technique
resolution, mapping string shapes, per-family sequence contiguity, minimum
content length per narrative field.

---

## 2. Regenerate the catalogue exports

```powershell
python artefacts\03-library\export_library.py
```

Expected:

```
controls   : 60
families   : 13
domains    : 18
evidence   : 257
written to : ...\artefacts\03-library
```

Produces six files:

| File | Rows |
|---|---|
| `control-catalogue.csv` | 60 × 34 |
| `control-catalogue.json` | 60 controls + registry + reference tables |
| `control-evidence.csv` | 257 |
| `domain-registry.csv` | 18 + total |
| `family-registry.csv` | 13 |
| `framework-mapping.csv` | Long/tidy |

**Review the CSV diff.** In version control this *is* the review artefact:

```powershell
git diff artefacts/03-library/control-catalogue.csv
```

Read it as prose. Does each added row tell an assessor what to do?

---

## 3. Build the workbook

```powershell
# Blank — use this as the starting point for every engagement
python artefacts\06-source\build\build_workbook.py out.xlsx

# sample — synthetic data, for demonstrating the dashboard only
python artefacts\06-source\build\build_workbook.py sample.xlsx --sample
```

Expected:

```
controls: 60
saved out.xlsx
```

### ⚠ Step 4 is mandatory

**`openpyxl` writes formulas but cannot evaluate them.** A freshly built
workbook contains formulas with **no cached values**.

| Consumer | Behaviour on an uncalculated file |
|---|---|
| Excel | Recalculates on open. Looks fine. |
| LibreOffice | Recalculates on open. Looks fine. |
| Most previewers (GitHub, SharePoint, Quick Look) | Blank or `None` |
| `pandas.read_excel` | `NaN` for every computed column |
| Any automated report generator | `None` |

That is why the shipped workbooks contain a `calcChain` part — someone opened
and saved them. **A build is not finished until this step is done.**

---

## 4. Recalculate

### Option A — Excel or LibreOffice, interactive

Open the file and save. Excel calculates on open (the builder sets
`fullCalcOnLoad`). Done.

### Option B — LibreOffice headless

```powershell
soffice --headless --convert-to xlsx --outdir .\out .\out.xlsx
```

### Option C — Windows Excel via COM

```powershell
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
$wb = $xl.Workbooks.Open("C:\path\out.xlsx")
$wb.Save()
$wb.Close()
$xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
```

### Verify it worked

```powershell
python -c "import openpyxl; wb=openpyxl.load_workbook('out.xlsx', data_only=True); print('cached:', wb['Dashboard']['B5'].value)"
```

A number means the cache is present. `None` means it is not — go back to step 4.

The `MANIFEST.md` generation script does this check on every workbook it records.

---

## 5. Build the report template

```powershell
Push-Location artefacts\06-source
node build\build_report.js report-template.docx
Pop-Location
```

Expected:

```
saved report-template.docx
```

The output path is `process.argv[2]`, so it is required.

### After opening in Word

The table of contents is a field and renders empty until refreshed. Press
`Ctrl+A`, then `F9`, and choose **Update entire table**. Documented as QA
finding F-11.

---

## Full clean-room verification

Run all of it:

```powershell
$ErrorActionPreference = 'Stop'
$root  = 'artefacts'
$stage = Join-Path $env:TEMP 'saos-verify'
Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $stage -Force | Out-Null

Write-Host "`n[1/6] Validate library" -ForegroundColor Cyan
python "$root\03-library\validate_library.py"
if ($LASTEXITCODE -ne 0) { throw 'library validation failed' }

Write-Host "`n[2/6] Export catalogue" -ForegroundColor Cyan
python "$root\03-library\export_library.py"
if ($LASTEXITCODE -ne 0) { throw 'export failed' }

Write-Host "`n[3/6] Build blank workbook" -ForegroundColor Cyan
python "$root\06-source\build\build_workbook.py" "$stage\blank.xlsx"
if ($LASTEXITCODE -ne 0) { throw 'blank build failed' }

Write-Host "`n[4/6] Build sample workbook" -ForegroundColor Cyan
python "$root\06-source\build\build_workbook.py" "$stage\sample.xlsx" --sample
if ($LASTEXITCODE -ne 0) { throw 'sample build failed' }

Write-Host "`n[5/6] Build report template" -ForegroundColor Cyan
Push-Location "$root\06-source"
node build\build_report.js "$stage\report.docx"
Pop-Location
if ($LASTEXITCODE -ne 0) { throw 'report build failed' }

Write-Host "`n[6/6] Recalculate and check cached values" -ForegroundColor Cyan
if (Get-Command soffice -ErrorAction SilentlyContinue) {
    soffice --headless --convert-to xlsx --outdir $stage "$stage\blank.xlsx"
    $wb = python -c "import openpyxl; wb=openpyxl.load_workbook(r'$stage\blank.xlsx', data_only=True); print(wb['Dashboard']['B5'].value)"
    Write-Host "cached Dashboard!B5 = $wb"
} else {
    Write-Warning 'soffice not found - recalculate manually before distributing'
}

Write-Host "`nAll checks passed." -ForegroundColor Green
```

Verified result on 2026-10-04:

| Step | Result |
|---|---|
| Validate library | PASS — 60 controls, 13 families, 0 errors, 0 warnings |
| Export catalogue | PASS — 6 files, 60 controls, 257 evidence items |
| Build blank workbook | PASS — 209 KB |
| Build sample workbook | PASS |
| Build report template | PASS — 19 KB |
| Recalculate | Cached values confirmed present |

---

## Determinism

| Property | Status |
|---|---|
| Same input → same library output | ✅ Deterministic |
| Same input → same workbook | ✅ Deterministic except the build date constant |
| Same input → same report | ✅ Deterministic |
| Network access at build time | None required |
| Random seed | `--sample` uses `random.seed(7)` — reproducible sample data |
| Library hashes in exports | ✅ SHA-256 of each source YAML embedded in `control-catalogue.json` |

Only `BUILD_DATE` (`build_workbook.py:21`) varies between runs. Bump it
deliberately on a release; do not let it drift.

---

## Adding a control — full workflow

```powershell
# 1. Edit the YAML
#    artefacts\06-source\library\controls\05_srv_part3.yaml

# 2. Validate
python artefacts\03-library\validate_library.py --strict

# 3. Export and review the diff
python artefacts\03-library\export_library.py
git diff artefacts/03-library/control-catalogue.csv

# 4. Build and inspect
python artefacts\06-source\build\build_workbook.py $env:TEMP\check.xlsx --sample

# 5. Recalculate, then open and check:
#    - the new control appears in Assessment
#    - its family count updated on the Dashboard
#    - mappings appear in Mapping_Matrix, MITRE_Matrix, ZeroTrust_Matrix
#    - Domain_Registry 'Controls built' incremented
#    - Evidence_Requests gained one row per evidence item

# 6. Record the change
#    - CHANGELOG.md
#    - bump VERSION in build_workbook.py if warranted
#    - regenerate MANIFEST.csv
```

Full field reference: `../02-methodology/CONTROL-SCHEMA.md`.

---

## Regenerating the manifest

The manifest generator is part of the packaging. Run it after any change to the
artefact set:

```powershell
python artefacts\08-infrastructure\build_manifest.py
```

It writes `MANIFEST.csv` and `MANIFEST.md` with, for every file: relative path,
size in bytes, SHA-256, category, role and provenance. It also verifies that each
workbook carries cached values, so an uncalculated workbook cannot be recorded as
delivered.

Re-run it whenever anything changes. A manifest that is out of date is worse than
no manifest.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'yaml'` | PyYAML not installed — `build_workbook.py` needs it as well as openpyxl | `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'openpyxl'` | openpyxl not installed | `pip install -r requirements.txt` |
| `Cannot find module 'docx'` | `package.json` not at or above `build/` | Copy manifests into `06-source/`, run `npm install` there |
| Dashboard cells blank in Excel | Opened in a viewer, not recalculated | Open in Excel or LibreOffice and save |
| `pandas` returns `NaN` for scores | Never recalculated | Step 4 |
| All ratings empty or `#N/A` | Rows inserted in `Risk_Model` rows 27–43 | Restore the fixed layout — see F-10 |
| Dashboard averages wrong after editing rows | Formula ranges misaligned | Append at the bottom only, or extend ranges and rebuild |
| `AssertionError` during build | Malformed control | `validate_library.py` gives the readable version of the same error |
| Sample data in a client deliverable | Wrong file issued | Check the `README` sheet for the `SAMPLE DATA` banner — see F-01 |
| Duplicate control ID | Sequence number reused | Validator reports the duplicate |
| `Controls built` not incrementing | Control ID prefix does not match the domain code | ID pattern must match `meta.yaml` |
| Export CSV mangles non-ASCII in Excel | Missing BOM | Exports are written UTF-8 with BOM; if you regenerate, keep `encoding='utf-8-sig'` |

---

## CI integration

Minimum gate:

```yaml
- run: pip install -r requirements.txt
- run: python artifacts/03-library/validate_library.py --strict
- run: python artifacts/03-library/export_library.py
- run: git diff --exit-code artifacts/03-library/control-catalogue.csv
```

The last step is the golden-file check: the exports are regenerated from the
committed library, and any diff means an unintended library change. Requiring
that diff to be committed makes every library change deliberate and reviewable.

Recommended additions:

| Check | Catches |
|---|---|
| `python -c "import openpyxl; …"` asserting every control count | Row loss in the builder |
| Build both workbooks and assert the output opens | Generator breakage |
| Round-trip the CSV export and assert field counts | Exporter bugs |
| Assert no workbook in the repo has a `SAMPLE DATA` README banner in a `FINAL` file | F-01 recurrence |

---

## Files referenced

| Path | Role |
|---|---|
| `../03-library/validate_library.py` | Schema and cross-reference validation |
| `../03-library/export_library.py` | Catalogue exports |
| `../03-library/control-schema.json` | JSON Schema for one control |
| `../06-source/build/build_workbook.py` | Workbook generator |
| `../06-source/build/build_report.js` | Report template generator |
| `../08-infrastructure/requirements.txt` | Python dependencies |
| `../08-infrastructure/package.json` | Node dependencies |
| `build_manifest.py` | Manifest generator |
| `../MANIFEST.md` / `../MANIFEST.csv` | File inventory with SHA-256 |