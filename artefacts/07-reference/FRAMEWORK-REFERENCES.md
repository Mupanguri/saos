# Framework References

What SAOS maps to, at what level, with what caveats, and what must be verified
before the mapping is shown to a client.

**Read this alongside:** [`QA-FINDINGS.md`](QA-FINDINGS.md) finding **F-04**
(mappings are unverified) and [`METHODOLOGY.md`](../02-methodology/METHODOLOGY.md)
§6 (limitations).

---

## Summary

| Framework | Edition | Level | Controls mapped | Verified |
|---|---|---|---|---|
| ISO/IEC 27001:2022 | 2022 | Control (Annex A) + family (clauses 4–10) | 60 / 60 | ❌ |
| ISO/IEC 27002:2022 | 2022 | Family reference only | 13 families | ❌ |
| NIST CSF 2.0 | 2.0 | Subcategory | 60 / 60 | ❌ |
| CIS Controls | v8.1 | Safeguard (`major.minor`) | 60 / 60 | ❌ |
| SOC 2 | 2017 TSC | Criterion | 60 / 60 | ❌ |
| MITRE ATT&CK | Enterprise | Technique | 47 techniques | ❌ |
| NIST SP 800-207 | Rev.1 | Pillar | 60 / 60 | ❌ |
| OWASP ASVS | 4.0.3 or 5.0 — **undecided** | Chapter | **0 — unmapped** | n/a |
| OWASP Top 10 | 2021 | Category | **0 — unmapped** | n/a |
| ISO/IEC 27034 | — | Category (family default) | 13 families | ❌ |

**No framework in this table has been verified.** The mapping work is
structurally sound and internally consistent; it has not been checked against the
licensed source documents. That distinction matters: structural plausibility is
not correctness.

---

## ISO/IEC 27001:2022

### Two levels, deliberately distinguished

This is the most commonly botched mapping in assessment tooling, so SAOS separates
it explicitly.

| Level | What it holds | Where |
|---|---|---|
| **Management system** | Clauses 4–10 — organisational requirements, not controls | `meta.yaml` family `iso_clause` |
| **Annex A** | The 93 reference controls | Per-control `iso` field |

ISO 27001:2022 clauses 4–10 (Context, Leadership, Planning, Support, Operation,
Performance improvement, Improvement) are **not controls**. A mapping to
"clause 6.1.3" is a management-system statement, not an Annex A control. The
`Mapping_Matrix` carries both as separate columns for exactly this reason.

### Control position

ISO 27001:2022 has 93 Annex A controls in four themes (Organizational 37,
People 8, Physical 14, Technological 34). Server Security controls map mostly to
Physical (A.7.x) and Technological (A.8.x), with some Organizational (A.5.x).

### Caveats

1. **Annex A controls are not a control set.** ISO 27001:2022 states Annex A is
   a reference list, not requirements, and applicability is determined by risk
   assessment. A mapping is a *starting point* for scoping, never a compliance
   statement.
2. **"Indicative alignment" must be stated.** Both the workbook README and
   report Appendix E already do this. Do not let the phrase "aligned to ISO
   27001" appear in a client deck without it.
3. **SoA coverage is a separate exercise.** SAOS maps *to* Annex A; it does not
   assess a client's Statement of Applicability. Never present a coverage
   percentage as a compliance percentage.

---

## ISO/IEC 27002:2022

Referenced at **family level only**, in `meta.yaml` `ref` strings — the guidance
behind each Annex A control. Not a separate mapping column.

---

## NIST CSF 2.0

### Structure

Six functions: Govern (GV), Identify (ID), Protect (PR), Detect (DE), Respond
(RS), Recover (RC). The `csf` field must carry the function prefix or the
validator fails, because `build_workbook.py:81` derives the function from it:

```python
c['csf_f'] = sorted({CSF_FUNC[m] for m in re.findall(r'\b(GV|ID|PR|DE|RS|RC)\.', str(c['csf']))}, …)
```

That is a useful guard. A subcategory without a function prefix would silently
vanish from the Dashboard's function coverage.

Server Security maps predominantly to **Protect** (`PR.PS`, `PR.AC`, `PR.IP`,
`PR.DS`) with some **Detect** (`DE.CM`, `DE.AE`) and **Govern** (`GV.PO`).

### Caveats

1. **CSF 2.0 added Govern.** CSF 1.1 had no Govern function. Any comparison
   against an older assessment will not map cleanly — do not compare CSF 1.1
   coverage figures to CSF 2.0 ones.
2. **CSF 2.0 is not a control catalogue.** It organises outcomes, not controls.
   Coverage means "this control supports this outcome", not "this requirement is
   met".
3. **Informative references.** CSF's informative references are examples, not
   exhaustive. Do not read an absent mapping as a gap.

---

## CIS Controls v8.1

### Structure

18 Safeguards in 6 Implementation Groups, each with `major.minor` identifiers
(IG1: 1.1–4.x, IG2: 5.x–12.x, IG3: 13.x–14.x, IG4: 15.x–18.x). IG1 is the
baseline; IG2+ scale with risk and maturity.

The builder parses major numbers for the `Mapping_Matrix` control column and
keeps the full `major.minor` in the safeguard column:

```python
c['cis_ctl'] = sorted({int(m) for m in re.findall(r'(\d+)\.\d+', str(c['cis']))})
```

### Caveats

1. **A safeguard mapping is not an IG assignment.** Mapping a control to 4.6 does
   not mean the client is at IG2. IG assignment is a risk-based organisational
   decision, not a per-control attribute.
2. **Version pinning matters.** CIS v8.1 → v8.2 changed numbering. Mappings are
   version-specific and must be re-checked on any CIS upgrade.
3. **YAML quoting is mandatory here.** `cis: '4.6, 12.2'` unquoted becomes the
   float `4.6` and `12.2` is lost. The validator catches the resulting shape
   error, but the data is gone first.

---

## SOC 2 (2017 Trust Services Criteria)

### The scope problem

This is the mapping most likely to be misread. SOC 2 has five categories:

| Category | Series |
|---|---|
| Security (Common Criteria) | CC1.1–CC9.2 |
| Availability | A1.1–A1.3 |
| Confidentiality | C1.1 |
| Processing Integrity | PI1.1–PI1.5 |
| Privacy | P1.1–P8.1 |

SAOS maps primarily to **CC**, with some **A** criteria on backup and recovery
controls (`SRV-BCK` maps to `A1.2`, `A1.3`).

**The consequence:** the mapping is only valid for an engagement whose scope
includes Availability. For a security-only or confidentiality-only scope, every
`A1.x` mapping is out of scope and must be excluded from the report. Quote the
in-scope TSC categories alongside the mapping, every time.

### Caveats

1. **A mapping is not an exception.** A control supporting `CC6.1` does not mean
   the client's control satisfies it. Only a licensed practitioner performing a
   SOC 2 examination can state that.
2. **Availability criteria need the right scope.** See above.
3. **Privacy criteria are almost entirely unmapped.** If the client has a privacy
   scope, SAOS v0.1 does not cover it. Say so rather than implying coverage.

---

## MITRE ATT&CK

### Structure

14 tactics, 11 in use. The `att` field encodes groups separated by `|`, tactic
and techniques separated by `:`:

```yaml
att: 'IA:T1190 | PS:T1542.001'
```

The builder validates every tactic against `TACT` and every technique against a
47-entry reference table (`build_workbook.py:31-46`).

### Coverage

| Tactic | Groups | | Tactic | Groups |
|---|---|---|---|---|
| Initial Access | 21 | | Credential Access | 10 |
| Defense Evasion | 14 | | Execution | 6 |
| Privilege Escalation | 13 | | Collection | 6 |
| Lateral Movement | 11 | | Discovery | 5 |
| Impact | 11 | | **Exfiltration** | **1** |
| Persistence | 7 | | | |

47 techniques defined, 47 used, no orphans in either direction.

### Caveats

1. **Techniques change.** ATT&CK is updated continuously. IDs are stable but
   names, tactics and sub-technique relationships move — a technique can be
   re-parented. Re-validate on every ATT&CK version bump, and record the version
   in `meta.yaml` (see format guide §10).
2. **A mapping is prevent-or-detect, not exclusive.** The builder does not
   distinguish which. Where it matters — usually in a detection-coverage report —
   separate `prevents` from `detects`.
3. **Coverage is not completeness.** 21 Initial Access mappings out of a
   technique library in the hundreds means the library covers the techniques
   relevant to *servers*, not ATT&CK. Frame it that way or the number will be
   read as a gap.
4. **The sub-technique count in `MITRE_Matrix` includes parent matches.** The
   `COUNTIF` uses a wildcard, so a parent ID counts sub-technique mappings. The
   sheet carries a footnote saying so, but the number is higher than a strict
   read implies.

---

## NIST SP 800-207 · Zero Trust Architecture

Six pillars: **Identity (ID)**, **Device (DV)**, **Network (NW)**,
**Application (AP)**, **Data (DT)**, **Infrastructure (IN)**.

The `zt` field records which pillars a control *touches*. The matrix counts
`●` per pillar and a total per control.

| Pillar | Controls |
|---|---|
| Infrastructure | 42 |
| Identity | 15 |
| Network | 10 |
| Data | 9 |
| Device | 4 |
| **Application** | **1** |

### Caveats

1. **"Touches" is not "delivers".** SP 800-207 describes pillars and a
   deployment model; it does not define per-pillar control catalogues. A control
   that touches a pillar does not implement Zero Trust for that pillar. The
   report must not read the pillar counts as a Zero Trust maturity score.
2. **Be honest about breadth.** Quoting every pillar on every control would make
   the matrix useless as a prioritisation tool. Thin coverage in a server domain
   is correct.
3. **Identity-centric.** SP 800-207 is explicit that identity is the primary
   control plane. Identity at 15 of 60 controls is low for a Zero Trust
   narrative. Batch 1 (IAM, 60 controls) will rebalance it — note the sequencing
   dependency.

---

## OWASP ASVS 4.0.3 · and the 5.0 question

**Currently unmapped for all 60 controls.** Two separate issues:

**1. Applicability.** ASVS is an application-security verification standard. A
server domain has little natural overlap. Correctly deferred to Batch 4
(Application Security, API Security, DevSecOps).

**2. The version question — a real blocker.**

| Version | Chapters | Status |
|---|---|---|
| ASVS 4.0.3 | V1–V14 | The specification asks for this |
| ASVS 5.0 (2025) | Restructured | Current release |

`Mapping_Matrix` footnote:

> "ASVS: the specification asks for V1-V14 (ASVS 4.0.3). ASVS 5.0 (2025)
> restructured the chapters; confirm the target version before the Application
> Security batch."

**Chapter numbers mean different things across these versions.** Mapping a
control to a chapter number that means something else in the client's version is
worse than leaving it unmapped. Decide before Batch 4 and record the decision in
`meta.yaml`.

---

## OWASP Top 10:2021

**Currently unmapped for all 60 controls.** Same applicability reasoning as ASVS.
The `owasp` field exists and `Mapping_Matrix` carries the column; only the values
are absent. Note this is the **2021** edition — the 2025 edition differs.

---

## ISO/IEC 27034

Referenced at **family level** as `app` in `meta.yaml` — the default category for
application-security controls, from *Security and privacy engineering — Application
security requirements and verification*.

Categories: Application Security Controls, Verification, Development, Runtime,
N/A.

Used as the family default in `Mapping_Matrix` column M, with `SRV-GOV` forced to
`N/A` (governance is not application engineering).

---

## The `N/A` convention

**`N/A` means "we assessed and there is no defensible mapping".**
It never means "not yet looked at".

Current distribution of `N/A` values:

| Field | `N/A` count | Meaning |
|---|---|---|
| `cis` | 6 of 60 | No CIS v8.1 safeguard corresponds |
| `soc` | 0 of 60 | Every control maps to at least one criterion |
| `att` | 0 of 60 | Every control has at least one technique |
| `asvs` | **60 of 60** | **Not assessed — application-layer frameworks** |
| `owasp` | **60 of 60** | **Not assessed — application-layer frameworks** |

The last two rows are the problem. `N/A` conflates "does not apply" with "not
done", and both mean the same thing in the data. Given that ASVS and OWASP Top 10
are entirely unmapped (F-06), a client reading a blank column could reasonably
conclude either "no gaps" or "not covered".

**Fix:** distinguish them. Use `Not assessed — server domain` for ASVS and OWASP,
reserving `N/A` for "assessed, no mapping applies". Then the empty columns read
correctly.

---

## Verification protocol

Two-person rule. Per framework.

### Steps

1. **Pin the edition** in `meta.yaml` (format guide §10). Record `status`,
   `verified_by`, `verified_on`.
2. **Sample 10% of controls, minimum 10, stratified** across families and across
   all mapping fields.
3. **Check against the licensed source**, not a summary or a secondary article.
   For ISO that means the licensed standard; for CIS the current version's
   published safeguard list; for ATT&CK the current version's technique database.
4. **Record each discrepancy** as control ID, field, current value, correct value,
   and reason.
5. **Fix the YAML, never the workbook.** Rebuild, re-export, review the CSV diff.
6. **Re-verify the whole sample after any framework version bump.** Version
   changes invalidate verification.
7. **Two signatures** per framework: preparer and reviewer.

### Prioritise

| Priority | Framework | Why |
|---|---|---|
| 1 | **SOC 2** | Most likely to be client-facing, and the CC/A scope mix is easy to misread |
| 2 | **ISO 27001:2022** | Most commonly quoted in client reports and tenders |
| 3 | **CIS v8.1** | Widely referenced, numbering is version-sensitive |
| 4 | **NIST CSF 2.0** | Structurally derived from the subcategory prefix, so lower risk of silent error |
| 5 | **MITRE ATT&CK** | Validated by tactic and technique against a reference table; still needs name and parentage checks |
| 6 | **NIST SP 800-207** | Lowest risk; pillar assignment is inherently a judgement |

### What verification is likely to find

Expect the highest error rate in:

- **SOC 2 criteria selection** — many criteria are plausibly related to any given
  control, so over-mapping is the likely error. Over-mapping is also the more
  damaging error: it implies coverage that does not exist.
- **CIS safeguard numbers** — plausible-looking neighbours (`4.6` vs `4.8`) are
  easy to transpose.
- **ATT&CK technique-to-tactic assignment** — techniques move between tactics
  between versions.
- **ISO clause-level mappings** — the family-level management-system clauses are
  broad by nature, so these will need narrowing.

---

## Required disclaimer

Already present in the workbook README, on `Mapping_Matrix`, and in report
Appendix E. **Do not remove it, and do not let it get separated from the
mapping.** Keep it adjacent wherever mappings appear, including in client decks.

> Maturity levels, risk ratings and framework mappings are professional
> judgements based on the evidence available at the time of assessment.
> Mappings to external frameworks are indicative and do not constitute
> certification, attestation or legal advice. Findings reflect the state of the
> environment during the assessment period only.

And when quoting coverage:

> *"Server Security domain, 60 controls. Application-layer and exfiltration
> controls are assessed in Application Security, not yet in scope for this
> assessment."*

That second sentence is what turns a coverage number from a liability into a
scope statement.