# QA Findings

Independent review of the SAOS v0.1 delivery, performed by inspecting every
file: parsing both workbooks cell by cell, reading all three control YAML files,
reading both build scripts, and reading the Word template's XML structure.

| | |
|---|---|
| Review date | 2026-10-04 |
| Artefacts reviewed | 4 delivered files + 6 source files |
| Method | Cell-level diff of both workbooks (719 differences), full source read, control-count and mapping verification |
| Findings | 12 — 1 High, 4 Medium, 5 Low, 2 Informational |
| Build verification | `validate_library.py` PASS · `build_workbook.py` PASS (blank + sample) · `build_report.js` PASS (after `npm install`) · `export_library.py` PASS |

## Summary

| ID | Severity | Finding | Status |
|---|---|---|---|
| F-01 | **High** | Delivered filename asserted a provenance the contents did not support | **Resolved — see note** |
| F-02 | Medium | Blank workbook build stamp stale | Open — rebuild |
| F-03 | Medium | No dependency manifests; build fails out of the box | **Resolved in this packaging** |
| F-04 | Medium | Framework mappings unverified | Open — blocks client issue |
| F-05 | Medium | Domain targets sum to 905, not "700+" | Open — resolve before external commitment |
| F-06 | Low | ASVS version ambiguous; `asvs` and `owasp` unmapped | Open — blocks Batch 4 |
| F-07 | Low | OT/ICS and AI are placeholders | Open by design |
| F-08 | Low | Registers formatted for 200 rows | Open |
| F-09 | Low | No reason column for risk overrides | Open |
| F-10 | Low | `Risk_Model` lookup ranges are hard-coded rows | Open |
| F-11 | Info | Report template lacks document properties; TOC needs manual refresh | Accepted |
| F-12 | Info | Thin coverage in two matrix areas | Accepted — disclose in reporting |

---

## F-01 · High · Delivered filename asserted a provenance the contents did not support

**Category:** data governance · **Status:** resolved in this packaging

> **Note on redaction.** This finding is published in generalised form. The
> original evidence named a specific engagement and identified the specific
> sample file involved; those details have been removed from this published copy
> and the file itself has been renamed to state its true contents. Retain an
> internal copy of the original record if the audit trail is needed.

### The control that failed

Every deliverable in this toolkit is identified by a filename that asserts what
the file **is**: which artefact, which version, which client, and what state it
is in. That convention is only safe if the name and the contents agree. During
the v0.1 review, one delivered workbook did not satisfy that.

A workbook whose name asserted it held a specific client's engagement data was,
in fact, the synthetic `--sample` build. Verification:

| Check | Result |
|---|---|
| Cell-level comparison against the blank workbook | **719 differing cells**, all of them synthetic content |
| `README!B2` build banner | Declared the file to be sample data |
| `Scope!C4` / `C5` | Contained the sample-data identity values, not engagement values |
| `Assessment!K` × 60 | Values matched the seeded generator exactly (`random.seed(7)`) |
| `Findings_Register`, `Risk_Register`, `Remediation_Tracker`, `Evidence_Register` | Synthetic rows, each carrying the sample marker |
| Generated Dashboard figures | Internally consistent with random data — `Overall maturity 2.78`, `24` controls with a gap, `12` Critical/High residual |
| Any genuine client data present | **None** |

### Why this is High, not cosmetic

1. **The name was the only provenance claim a hurried reader would check.** A
   recipient who trusted the filename would apply client-data handling,
   distribution restrictions and retention rules to a file that warranted none
   of them — or, worse, would conclude an engagement had been performed and
   produce findings from numbers that were never measured.
2. **It implied a retraction event that never occurred.** The name asserted that
   data had been withdrawn. A withdrawal is a notifiable data-governance event.
   Raising a false one, or leaving an implied one unresolved, damages trust in
   every other artefact in the set.
3. **It made the set unauditable.** If a filename can assert provenance
   independently of content, no filename in the set can be relied upon — and the
   convention is worthless.

### Root cause

Filenames were free text. Nothing constrained the name to describe the content,
and no pre-issue check compared the name against the file's own self-declaration.

### Resolution applied

| Action | Detail |
|---|---|
| Renamed | The file is now `SAOS-Assessment-Workbook-v0.1-SAMPLE.xlsx`, stating what it actually contains |
| Sample identity redacted | All identifying fields in `--sample` mode are written as `Redacted`, so the build can never emit a plausible-looking client identity |
| Banner retained | `README!B2` carries `SAMPLE DATA - CLIENT NAME REDACTED` |
| Filename convention formalised | [`FILE-FORMAT-GUIDE.md`](FILE-FORMAT-GUIDE.md) §3 — mandatory `SAOS-<artefact>-v<version>[-<client>[-<period>]][-<state>].<ext>` |
| Internal stamping specified | §4 — a retraction that lives only in a filename is not a retraction |
| Pre-issue check added | [`ENGAGEMENT-RUNBOOK.md`](../04-workflows/ENGAGEMENT-RUNBOOK.md) — open `README`, confirm no sample-data banner, before any issue |

### Prevention — the standing rule

> **Never rename a file into a provenance claim. Name every file after what it
> actually is.**

Three checks make that hold:

1. **Self-declaration.** Every generated artefact declares its own state inside
   itself — the `README!B2` banner for workbooks, the Document Control block for
   reports. If the two disagree, the inner declaration wins and the file is
   wrong.
2. **Pre-issue scan.** Open the `README` sheet. Five seconds. This check alone
   would have prevented the original finding.
3. **CI assertion.** No file with a `FINAL` or client-scoped name may carry a
   sample-data banner. Add as an automated test — see
   [`BUILD-AND-VERIFY.md`](../08-infrastructure/BUILD-AND-VERIFY.md).

**Retention rule.** A superseded file is never deleted. It is renamed with the
`SUPERSEDED` state, stamped internally, and recorded in `CHANGELOG.md` and
`MANIFEST.csv` with the reason and its replacement. The record of what was
issued, and when, is part of the deliverable.

---

## F-02 · Medium · Blank workbook build stamp is stale

**Artefact:** `SAOS Assessment Workbook v0.1.xlsx`

### Evidence

| Source | Value |
|---|---|
| `README!B2` in the blank workbook | `built 2025-11-28` |
| `README!B2` in the sample workbook | `built 2026-10-04` |
| `build_workbook.py:21` | `BUILD_DATE = datetime.date(2026, 10, 4)` |
| File timestamps on `library/**` | 2026-10-04 |

The full cell-by-cell diff shows **no differences** in `Control_Library`,
`Mapping_Matrix`, `MITRE_Matrix`, `ZeroTrust_Matrix`, `Maturity_Model`,
`Risk_Model`, `Domain_Registry` or `Lists`. The library content is therefore
unchanged; only the stamp differs.

### Impact

A recipient cannot tell whether the workbook reflects the current library. The
build date is the only version indicator inside the file, and it disagrees with
the toolchain. If the library *had* changed since 2025-11-28 without the stamp
being noticed, the workbook would silently be wrong — which is exactly the
failure the build date exists to prevent.

### Resolution

Rebuild before distributing. Five minutes. Confirm the recalculation step
completes and cached values are present.

### Prevention

- After the library/engagement workbook split (F-03 / format guide §2), embed the
  library SHA-256 in the workbook `README` sheet rather than relying on a date.
- Add the golden-file test so unintended library drift is caught at review time.

---

## F-03 · Medium · No dependency manifests; the report build fails out of the box

**Artefact:** `SAOS_Source_Library_v0.1/build/`

### Evidence

```
> node build\build_report.js out.docx
Error: Cannot find module 'docx'
Require stack:
- ...\SAOS_Source_Library_v0.1\build\build_report.js
```

The delivered source tree contained only `README.md`, `build/` and `library/`. No
`package.json`, no `requirements.txt`, no lock file, no `node_modules`.

`build_report.js:5` requires `docx`. `build_workbook.py:9-15` requires `yaml`,
`openpyxl` and `openpyxl.styles` — note **`yaml` as well as `openpyxl`**, which
is easy to miss.

A secondary subtlety: installing `node_modules` in the *working directory* does
not fix it. Node resolves modules by walking up from the **script's own
directory**, so `package.json` must exist at or above `build/`.

### Impact

A new operator cannot build the report or the workbook without already knowing
the dependencies. Reproducibility is not possible, so a client asking for the
exact tooling used to produce their workbook cannot be answered.

### Resolution — **fixed in this packaging**

| File | Provides |
|---|---|
| `../08-infrastructure/requirements.txt` | `openpyxl>=3.1,<4`, `PyYAML>=6.0,<7` |
| `../08-infrastructure/package.json` | `docx` dependency, script definitions |
| `../08-infrastructure/package-lock.json` | Exact resolved versions |

Verified: `build_workbook.py` builds blank and `--sample`; `build_report.js` builds
after `npm install`.

### Prevention

Treat dependency manifests as part of the definition of done for any buildable
component.

---

## F-04 · Medium · Framework mappings are unverified

### Evidence

`README` sheet, Limitations section:

> "Framework mappings (ISO 27001:2022 Annex A, NIST CSF 2.0, CIS Controls v8.1,
> SOC 2 2017 TSC, MITRE ATT&CK, OWASP) were authored from working knowledge of
> the published frameworks and must be verified against the licensed or current
> source documents before being issued to a client."

60 controls carry mappings across six frameworks. `Mapping_Matrix` carries a
similar note. Report Appendix E carries the disclaimer.

### Assessment

**The disclosures are present and correctly placed.** This is a finding about
residual risk, not about concealment. Three observations sharpen it:

1. **The disclaimers live in the tool, not in a control process.** Nothing stops
   someone copying the `Mapping_Matrix` into a client deck without the
   disclaimer travelling with it.
2. **The SOC 2 mapping has a specific gap worth checking.** The `soc` field
   mixes Common Criteria with Availability (`A1.2`, `A1.3`) criteria, which is
   correct for availability-heavy controls but means the mapping is only valid
   for a service-organisation scope. It is not valid for a security-only or
   confidentiality-only scope.
3. **The ASVS and OWASP Top 10 columns are entirely empty** for all 60 controls
   (see F-06), so a client asking for ASVS coverage gets a blank column rather
   than a gap disclosure.

### Impact

- A wrong mapping in a client report is a credibility problem and potentially a
  contractual one, if the report was used to support a compliance assertion.
- The empty ASVS and OWASP columns can be misread as "no gaps" rather than
  "not assessed".

### Resolution

1. Two-person verification per framework, recorded in the edition pin block
   proposed in [`FILE-FORMAT-GUIDE.md`](FILE-FORMAT-GUIDE.md) §10:
   `status`, `verified_by`, `verified_on`.
2. Build fails or warns when a client-facing build contains `unverified`
   mappings.
3. Scope the SOC 2 mapping per engagement and state which TSC categories are in
   the assessment scope.
4. Replace empty ASVS/OWASP columns with an explicit `Not assessed` marker.

### Prevention

Add `framework_editions` to `meta.yaml` with a verification status per framework.
Turn F-04 from a footnote into a trackable state.

---

## F-05 · Medium · Domain targets sum to 905, not "700+"

### Evidence

`library/meta.yaml` domains 1–16 targets:

```
50 + 25 + 60 + 50 + 60 + 75 + 80 + 100 + 80 + 40 + 70 + 35 + 40 + 30 + 60 + 50 = 905
```

Domains 1–15 sum to **855**. `Domain_Registry` footnote:

> "the specification states a 700+ control goal; its per-domain targets add up to
> 855 (905 with domain 16)."

Domain 16's comment: `target 50 is an assumption`.

### Assessment

Three separate quantities are in play and they are easy to conflate:

| Quantity | Value | Source |
|---|---|---|
| Specification's stated goal | "700+" | Project specification |
| Sum of per-domain targets 1–15 | 855 | Derived |
| Sum including assumed domain 16 | 905 | Derived |

Domain 16 (Google Workspace, 50) is explicitly an assumption with no
specification backing. The specification's "700+" is 21% below the 855 derived
from its own per-domain figures.

### Impact

- Effort estimates built on 905 are 29% above a 700-control plan.
- If the real target is 700+, either some per-domain targets are wrong or the
  domains overlap. Both change the roadmap.
- Externally, committing to a 905-control framework when the specification says
  700+ is an avoidable credibility problem.

### Resolution

Resolve with the specification owner before Batch 1 planning completes. Do not
force content to hit a target — if a domain genuinely needs 60 controls rather
than 50, report the real number.

### Prevention

Make targets a first-class field with a `source` attribute
(`specification` / `assumption`) so assumptions are visible in the registry
rather than in prose.

---

## F-06 · Low · ASVS version ambiguous; `asvs` and `owasp` unmapped

### Evidence

`Mapping_Matrix` footnote:

> "ASVS: the specification asks for V1-V14 (ASVS 4.0.3). ASVS 5.0 (2025)
> restructured the chapters; confirm the target version before the Application
> Security batch. OWASP Top 10 mapped to the 2021 edition."

All 60 controls have `asvs: N/A` and `owasp: N/A` — the columns exist, the values
do not.

### Assessment

Correct handling for a server domain; OWASP ASVS and Top 10 are application-layer
frameworks and have no natural home in a server control set. Forcing mappings
would be worse than leaving them blank.

The real issue is the **ambiguous target version**, which is a Batch 4 blocker.
ASVS 4.0.3 uses chapters V1–V14; ASVS 5.0 (2025) restructured them. Mapping a
control to a chapter number that means something different in the version the
client uses is worse than not mapping it.

### Impact

A client asking for ASVS coverage gets a blank column with no explanation. And
Batch 4 cannot start until the version is fixed.

### Resolution

1. Decide the target ASVS version now and record it in `meta.yaml`.
2. Replace the blank columns' `N/A` with an explicit `Not assessed — server domain`
   so a blank is never misread as a pass.
3. Map ASVS and OWASP Top 10 in the Application Security batch (Batch 4).

---

## F-07 · Low · OT/ICS and AI Systems are placeholders

### Evidence

```yaml
- {num: 17, code: OT,  name: OT/ICS (future),  target: 0, batch: 'Placeholder', …}
- {num: 18, code: AI,  name: AI Systems (future), target: 0, batch: 'Placeholder', …}
```

`Domain_Registry` shows both as `Placeholder`, `Controls built` 0,
`% of target` `n/a`.

### Assessment

Deliberate and correctly labelled. The scope strings say "Reserved for
operational technology and industrial control systems" and "Reserved for AI/ML
systems, model supply chain, and AI governance".

### Impact

A client in OT or with AI systems cannot be assessed with v0.1, and the
dashboard will show those domains as `Not assessed`. That is honest, but it must
be stated in the report scope rather than left for the reader to notice.

### Resolution

No code change. Add a standing note in the report template scope section: domains
with zero built controls are out of assessment scope, and list them.

---

## F-08 · Low · Registers formatted for 200 rows

### Evidence

| Sheet | Formatted rows | Formula ranges read to |
|---|---|---|
| `Evidence_Register` | 6–205 | 200 |
| `Findings_Register` | 6–205 | 200 |
| `Risk_Register` | 6–205 | 200 |
| `Remediation_Tracker` | 6–205 | 200 |
| `Assessment` | 5–64 (60 controls) | 2000 |
| `Evidence_Requests` | 5–261 (257 items) | 261 |

`README` sheet, Limitations: "Registers are formatted for 200 rows; Assessment and
dashboard formulas read to row 2000 so the library can grow to its full size."

### Assessment

The library grows to row 2000 fine. The registers are the constraint. A
single-domain Server Security engagement produces ~8 findings and ~257 evidence
requests, so 200 rows is comfortable. A **full 905-control** engagement could
plausibly produce 400+ findings and 3,900+ evidence items.

### Impact

At full scale an engagement silently loses register capacity. Findings entered
past row 205 fall outside every dashboard count and conditional format, and the
failure is silent.

### Resolution

Before the first full-library engagement, parameterise the register row count in
`build_workbook.py` from a CLI flag or a constant, and extend all dependent ranges
together.

### Prevention

Add an assertion or a build-time warning when the library size implies more
register rows than are formatted.

---

## F-09 · Low · No reason column for risk overrides

### Evidence

`Assessment` provides `R` (Likelihood Override) and `S` (Impact Override), both
plain input cells with a 1–5 validation. `T` and `U` resolve override-or-default.

`Assessment!Q` (Assessor Notes) is the only place a justification can go.

### Assessment

The design is good — overrides are non-destructive and defaults stay visible, so
the maths is reconstructable. What is missing is a structured, queryable record
of *why* a default was overridden. For a report that discusses risk calibration,
"three controls were overridden, reasons in free text" is weaker than a
populated reason field.

### Impact

Low for the engagement; higher for trend analysis across cycles, where you want
to know whether the same controls are consistently overridden.

### Resolution

Add `R_override_reason` and `S_override_reason` columns, or a single
`override_reason`. Two extra columns, minimal downstream impact since the sheets
are generated.

---

## F-10 · Low · `Risk_Model` lookup ranges are hard-coded rows

**Artefact:** `build_workbook.py:181-182`

```python
RM_LOW, RM_LAB = 'Risk_Model!$A$30:$A$33', 'Risk_Model!$B$30:$B$33'
MAT_LVL, MAT_EFF = 'Risk_Model!$A$38:$A$43', 'Risk_Model!$C$38:$C$43'
```

Every rating formula in the workbook routes through these four ranges via
`band()`:

```python
def band(expr):
    return f'INDEX({RM_LAB},MATCH({expr},{RM_LOW},1))'
```

`Risk_Model` is commented `# fixed layout`, and the `Risk_Model` sheet itself says
"Rating bands (lower bound is inclusive; **used by every rating formula in the
workbook**)".

### Assessment

The risk of inserting a row in the rating-bands table (rows 29–33) or the
effectiveness table (rows 37–43) is **total and silent**. Every rating in every
sheet stops resolving, and the workbook shows no error — just wrong or empty
values. A client would receive a report with no risk ratings and, depending on
the exact breakage, no warning at all.

The same class of risk applies to inserting rows mid-table in any register
(`Evidence_Register`, `Findings_Register`, `Risk_Register`,
`Remediation_Tracker`, `Crown_Jewels`), where formula ranges are absolute.

### Impact

A plausible and destructive mistake. In Excel a user inserting a row to "make
space" would not expect it to disable risk rating across the workbook.

### Resolution

1. **Protect the `Risk_Model` sheet** in delivered workbooks, or at minimum the
   rows 27–43 range.
2. Replace the hard-coded references with **defined names** (`RiskBands_Low`,
   `RiskBands_Label`, `Effectiveness_Level`, `Effectiveness_Rate`) so inserts
   cannot silently misalign in the same way, and so the formula reads as
   `INDEX(RiskBands_Label, MATCH(...))`.
3. Alternatively, compute the bands in Python and write the rating as a nested
   `IFS`, removing the cross-sheet lookup entirely — at the cost of losing
   client-editable bands.

### Prevention

A CI assertion that the band rows are where the code expects them, or defined
names, or both.

---

## F-11 · Info · Report template properties and TOC refresh

### Evidence

`build_report.js:201-209` sets `creator` and `title` only. No `subject`,
`description`, `keywords` or `category`. No classification property.

`build_report.js:71` creates `new TableOfContents('Contents', …)`, which is a
Word field. Word does not populate a TOC field until it is refreshed.

### Impact

- The TOC renders empty until the user presses `Ctrl+A` then `F9`. A template
  recipient may not notice.
- No classification in document properties means a `CONFIDENTIAL` document can be
  indexed and emailed without the property carrying that signal.

### Resolution

1. Document the TOC refresh step prominently — in the template's own guidance box
   and in `BUILD-AND-VERIFY.md`.
2. Add `subject`, `description`, `keywords` and `category: 'Confidential'` to the
   `Document` constructor.
3. Consider `docx`'s `features.updateFields` option if the library version
   supports it, so Word offers to update on open.

---

## F-12 · Info · Thin coverage in two matrix areas

### Evidence

Zero Trust pillar distribution across 60 controls:

| Pillar | Controls |
|---|---|
| Infrastructure | 42 |
| Identity | 15 |
| Network | 10 |
| Data | 9 |
| Device | 4 |
| **Application** | **1** |

ATT&CK tactic group distribution:

| Tactic | Groups | | Tactic | Groups |
|---|---|---|---|---|
| Initial Access | 21 | | Credential Access | 10 |
| Defense Evasion | 14 | | Execution | 6 |
| Privilege Escalation | 13 | | Collection | 6 |
| Lateral Movement | 11 | | Discovery | 5 |
| Impact | 11 | | **Exfiltration** | **1** |

### Assessment

**Expected and correct** for a server domain. A server estate is infrastructure,
so 42 Infrastructure mappings is right. Application controls belong to
Application Security (Batch 4). Server-side exfiltration is a small part of a
server domain's threat surface — it mostly happens at the endpoint or network
layer.

The finding is about **reporting risk**, not library quality. A client reading
"1 of 60 controls addresses the Exfiltration tactic" without context would
reasonably conclude the assessment had a gap. There isn't one.

### Resolution

1. Quote these matrices in reports only with the domain context attached: *"Server
   Security domain; application-layer and exfiltration controls are assessed in
   Application Security (Batch 4), not yet in scope."*
2. Once more domains are built, the distribution will normalise without any
   change to the library.
3. Consider a "coverage not applicable to this domain" note on the matrix sheets.

---

## What is working well

Recording this matters as much as the defects — it tells you what not to break
when fixing them.

| Area | Assessment |
|---|---|
| **Control schema depth** | 27 fields with maturity anchors, validation procedures containing real commands, and framework mappings is a genuinely high bar. Most published control libraries stop at a statement and a reference |
| **Validation procedures** | Real commands: `nmap -sU -p 623 --script ipmi-version`, Redfish `curl` calls, `reg query` for USBSTOR, `lsmod \| grep usb_storage`, `nc -vz` reachability tests. An assessor can act on these without interpretation |
| **Evidence design** | `ev` as a semicolon-separated list that auto-expands into a PBC request list with stable IDs is elegant. It removes an entire class of "we asked for the wrong thing" failure |
| **Maturity caps** | The evidence cap, coverage cap and design-vs-operation cap are the difference between an honest maturity score and a flattering one. Most frameworks have no equivalent |
| **Formula integrity** | The whole risk chain recalculates: override → used → inherent → rating → effectiveness → residual → rating. No hardcoded results anywhere in the Assessment sheet |
| **Worked examples** | Grey italic example rows on all five registers, excluded from counts, showing the expected shape of a good entry |
| **Colour convention** | Blue-on-yellow input, black formula, grey library, `●` for mappings. Learnable in a minute and consistently applied |
| **Build-time validation** | The builder asserts on duplicate IDs, L/I ranges, platform and test-method enumerations, ATT&CK tactic and technique resolution, and column letter alignment — it fails loudly rather than producing a subtly wrong workbook |
| **Disclaimer discipline** | The unverified-mappings limitation appears in the workbook README, on `Mapping_Matrix`, in `Mapping_Matrix`'s footnote and in report Appendix E |
| **Domain registry transparency** | Live `COUNTIF` build counts, `% of target`, explicit `Placeholder` status, and a footnote recording the 905 vs "700+" discrepancy rather than hiding it |

---

## Verification log

Commands run against this delivery on 2026-10-04:

| Check | Command | Result |
|---|---|---|
| Library validation | `python artefacts/03-library/validate_library.py` | **PASS** — 60 controls, 13 families, 0 errors, 0 warnings |
| Workbook build (blank) | `python artefacts/06-source/build/build_workbook.py out.xlsx` | **PASS** |
| Workbook build (sample) | `python artefacts/06-source/build/build_workbook.py sample.xlsx --sample` | **PASS** |
| Report build | `node artefacts/06-source/build/build_report.js out.docx` | **PASS** after `npm install` (see F-03) |
| Catalogue export | `python artefacts/03-library/export_library.py` | **PASS** — 6 files, 60 controls, 257 evidence items |
| Workbook diff | Cell-level comparison of both workbooks | 719 differences, all synthetic content (F-01) |
| Control count | Library vs `Control_Library` vs `Assessment` | 60 in all three — consistent |
| Mapping integrity | ATT&CK techniques in library vs build reference table | 47 defined, 47 used, 0 orphans in either direction |
| Family registration | Control families vs `meta.yaml` families | 13 built, 13 defined, 0 orphans |
| Sequence contiguity | All 13 families | Contiguous, no gaps |

## Recommended order of work

| Order | Action | Addresses |
|---|---|---|
| 1 | Confirm every deliverable name matches its contents; re-stamp superseded files | F-01 |
| 2 | Rebuild the blank workbook and recalculate | F-02 |
| 3 | Ship dependency manifests | F-03 — **done** |
| 4 | Verify framework mappings, two-person, per framework | F-04 |
| 5 | Resolve the 905 vs "700+" target discrepancy | F-05 |
| 6 | Adopt the filename convention and internal stamping | F-01 prevention |
| 7 | Protect `Risk_Model`; move to defined names | F-10 |
| 8 | Parameterise register row counts | F-08 |
| 9 | Decide the ASVS version | F-06, blocks Batch 4 |
| 10 | Add override-reason columns | F-09 |
| 11 | Add `framework_editions` pin block to `meta.yaml` | F-04 prevention |
| 12 | Add document properties; document the TOC refresh | F-11 |
| 13 | Add domain context to matrix reporting | F-12 |

Items 1–3 are minutes of work and remove all High and trivially-fixable Medium
findings. Item 4 is the only one that needs real expert time before external
release.