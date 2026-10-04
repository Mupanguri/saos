# SAOS source library (v0.1)

library/meta.yaml          Domain registry (18 domains) and control-family metadata
library/controls/*.yaml    Master control library (one file per batch; currently 60 Server Security controls)
build/build_workbook.py    Generates the Excel workbook:  python build/build_workbook.py out.xlsx [--sample]
build/build_report.js      Generates the Word report template:  node build/build_report.js out.docx

Add controls by appending to a YAML file in library/controls/ (same keys as the existing entries), then rebuild.
YAML gotchas: quote CIS/SOC values ('3.10'), quote any text containing a comma inside a {flow} mapping, never name a key 'no' or 'yes'.
After building the workbook, recalculate it (LibreOffice) so values are cached for previewers.
