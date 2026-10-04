# Build Roadmap

How SAOS gets from 60 controls to its full target, and what has to happen
first.

## Current position

| | |
|---|---|
| Version | v0.1 |
| Controls built | 60 of 905 (6.6%) |
| Domains complete | 1 of 18 (Server Security) |
| Families built | 13 |
| Pipeline status | **Validated end to end** — library → workbook → report all build and pass |
| Blocker | None technical. Blocked on framework-mapping verification (F-04) for external use |

The pilot did its job: the schema, the risk model, the workbook layout and the
report structure are all proven. Authoring the remaining 845 controls is now a
production-line exercise rather than a design exercise.

## Prerequisites before Batch 1

None of these block authoring controls. All of them block *shipping to a
client*, and shipping to a client is the point.

| # | Item | Effort | Why it matters |
|---|---|---|---|
| 1 | Independent verification of framework mappings (F-04) | 2–3 days | ISO/CIS/SOC references in a client report that turn out to be wrong is a credibility and contractual problem. Two-person rule. |
| 2 | Rebuild the blank workbook (F-02) | 5 min | Shipped artefact is stale relative to the toolchain. |
| 3 | Split the library workbook from the engagement workbook | 1 hour | Right now the control library ships inside every client file, where an assessor can edit generated content and it re-ships every engagement. |
| 4 | Adopt the naming convention | 30 min | F-01 happened because filenames were free text. |
| 5 | Add the golden-file test | 2 hours | Catches unintended library changes at review time instead of at client time. |
| 6 | Add `validate_library.py --strict` to the review gate | 30 min | Makes schema conformance non-optional. |

## Batch plan

Targets are the per-domain targets from the project specification. Domain 16's
target of 50 is an assumption (F-05).

### Batch 0 — Pilot ✅ complete

| Domain | Code | Target | Controls | Notes |
|---|---|---|---|---|
| Server Security | SRV | 60 | **60** | 13 families. Validated the pipeline. |

### Batch 1 — Identity, productivity and cloud · 240 controls

| Domain | Code | Target | Notes |
|---|---|---|---|
| Identity and Access Management | IAM | 60 | AD forest, trusts, tiering, admin accounts, GPO; Entra ID MFA, Conditional Access, Identity Protection, access reviews, PIM; PAM sessions, vaulting, JIT |
| Microsoft 365 | M365 | 80 | Exchange, Teams, SharePoint, OneDrive, Purview, Defender, Intune, Entra |
| Cloud Security | CLD | 100 | Azure, AWS, GCP: IAM, networking, storage, monitoring, logging, containers, Kubernetes |

**Why first.** Highest client demand by a wide margin — identity and cloud are
where most engagements start and where most breaches happen. Authoring these
also forces the hardest schema questions early (conditional policy evaluation,
graph-based controls, multi-cloud abstraction), which is better done before 645
controls depend on the answer.

**Watch for.** M365 and CLD both touch Entra ID. Decide the boundary now or you
will author the same control twice: recommend Entra *identity and conditional
access* in IAM, Entra *workload and resource* controls in CLD, and M365
*service configuration* in M365. Record the decision in `meta.yaml` scope text.

### Batch 2 — Governance, inventory, detection and vulnerability · 180 controls

| Domain | Code | Target | Notes |
|---|---|---|---|
| Governance | GOV | 50 | Strategy, programme, policies, standards, procedures, framework alignment, risk governance, third-party governance |
| Asset Management | AST | 25 | Inventory, discovery, shadow IT, software, hardware, cloud and SaaS assets |
| Security Operations | SOC | 70 | Logging, SIEM, SOAR, threat intelligence, detection engineering, incident response |
| Vulnerability Management | VLM | 35 | Discovery, scanning, prioritisation, remediation, validation |

**Why second.** Governance and inventory underpin everything else — you cannot
report patch compliance, asset coverage or finding closure without a trustworthy
inventory and a named owner. SOC and VLM give the detection and remediation
story that turns an assessment into a funded programme.

**Dependency.** AST should be authored *before* the dashboard coverage metrics
are relied upon externally, because "percentage of in-scope assets covered" is
only as good as the inventory behind it.

### Batch 3 — Estate, network, data and recovery · 195 controls

| Domain | Code | Target | Notes |
|---|---|---|---|
| Endpoint Security | END | 50 | Windows, Linux, macOS, iOS, Android including MDM |
| Network Security | NET | 75 | Routers, switches, firewalls, VPN, wireless, NAC, IDS/IPS, DNS, proxy |
| Data Protection | DPR | 40 | Classification, encryption, DLP, retention, privacy |
| Backup and Recovery | BKP | 30 | Backups, replication, recovery, DR testing |

**Why third.** Extends outward from the server estate to the endpoints and
network it depends on, then covers the data and the ability to recover it.
Natural cross-reference surface with SRV (backup, encryption, logging all
appear in both).

### Batch 4 — Applications, APIs, pipelines and Workspace · 230 controls

| Domain | Code | Target | Notes |
|---|---|---|---|
| Application Security | APP | 80 | Secure SDLC, architecture, authentication, authorisation, input validation, logging, secrets management |
| API Security | API | 40 | OAuth, OIDC, JWT, rate limiting, API gateway, API logging |
| DevSecOps | DSO | 60 | CI/CD, repositories, secrets, containers, IaC |
| Google Workspace | GWS | 50 | Admin console, identity and 2SV, Gmail, Drive, Meet, DLP, context-aware access |

**Why last.** Application-layer control authoring is the most framework-dependent
part of SAOS and depends on decisions not yet made — specifically the OWASP ASVS
version (F-06). Authoring it first would mean rework.

**Blocking decision.** ASVS 4.0.3 uses chapters V1–V14; ASVS 5.0 (2025)
restructured them. The specification is ambiguous. Resolve before starting, and
record the answer in `meta.yaml`.

### Placeholders — blocked

| Domain | Code | Target | Blocker |
|---|---|---|---|
| OT/ICS | OT | 0 | Different methodology entirely. IEC 62443, not IT controls. Safety and availability considerations change the risk model. Needs a separate framework decision and probably a separate library. |
| AI Systems | AI | 0 | No agreed scope. Candidates: model supply chain, training data provenance, prompt injection, AI Act compliance, agent/tool permissions. Rapidly moving target. Do not guess. |

## Per-batch authoring process

Reusable checklist. Budget roughly 1.5–3 days per family depending on research
depth.

**1. Scope the family**
Agree the family boundaries and write the `scope` text in `meta.yaml`. Decide
explicitly what belongs to a neighbouring domain — especially where two domains
overlap (see the Entra ID note in Batch 1).

**2. Define the family in `meta.yaml`**
Add the `families` entry: `name`, default `ref`, `iso_clause` (management-system
clauses, not Annex A), `app` (ISO/IEC 27034 category). The family reference is
the default for all its controls, so get it right once.

**3. Draft the controls**
For each control, all 27 fields. Non-negotiables:

- `name` is a positive assertion of the desired state, not a task.
- `q` is a single question the assessor can answer yes/no-with-detail.
- `proc` is step-by-step and specific enough that a different assessor would
  reach the same conclusion. Real commands, real portal paths.
- `ev` is semicolon separated. Each item becomes a PBC row, so split compound
  items — `ev: 'Policy document'` forces a useless request.
- `m1`/`m3`/`m5` are *descriptions of a state*, not actions to perform.
- `L` and `I` are defaults. They must be defensible on their own.
- `w` reflects business criticality to the client, not how hard the control is
  to implement.

**4. Map the frameworks**
Every control to ISO 27001:2022 Annex A, NIST CSF 2.0, CIS v8.1, SOC 2 and
ATT&CK. Use `N/A` honestly rather than inventing a plausible-looking reference —
a wrong mapping is worse than an acknowledged gap.

**5. Validate**

```powershell
python artefacts\03-library\validate_library.py --strict
```

Must return `RESULT: PASS` with zero warnings.

**6. Build and inspect**

```powershell
python artefacts\06-source\build\build_workbook.py check.xlsx --sample
```

Open it. Check the family appears on the Dashboard heat map, the family count is
right, the ATT&CK and Zero Trust matrices populate, and the new mappings appear
in `Mapping_Matrix`. Gridlines and banding will look wrong for one row of
controls; that resolves as the library fills in.

**7. Export and review the diff**

```powershell
python artefacts\03-library\export_library.py
git diff artefacts\03-library\control-catalogue.csv
```

The CSV diff *is* the review artefact. Read it as prose: does each added row
tell an assessor what to do?

**8. Record it**
Changelog entry, version bump if warranted, manifest regeneration.

## Quality bar for a control

A control is done when a competent assessor who has never seen the domain can:
read the name and understand the desired state; answer `q` and get a
defensible maturity score; follow `proc` and reach the same conclusion as
anyone else; request exactly the evidence in `ev`; and explain to a
non-technical executive, using `biz`, why it matters.

If any of those fail, the control is not finished. Most failures are in `proc`
and `ev` — they get written for the author rather than the reader.

## Effort estimate

| | |
|---|---|
| Controls remaining | 845 |
| Average per control | 35–60 min including research, mapping and review |
| Two-person review overhead | +30% |
| **Total remaining** | **Roughly 700–900 hours** |
| At 2 authors part-time | 6–9 months |
| At 1 author full-time | 4–5 months |

Domain 17 and 18 are excluded — they are methodology projects, not authoring
projects.

## Risks to the plan

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Framework mappings found wrong during verification (F-04) | Medium | High | Verify before Batch 1 ships. Budget rework time. |
| Batch scope overlap (Entra ID, backup, encryption across domains) | High | Medium | Decide boundaries in `meta.yaml` before authoring each batch. |
| Domain targets prove unrealistic when authoring starts | Medium | Medium | Revisit after Batch 1; report the real number rather than forcing content to hit a target. |
| ASVS version undecided at Batch 4 | Medium | Low | Blocks only APP; decide by Batch 3 end. |
| Register row limits hit (F-08) | High at full scale | Medium | Extend register rows before the first full-library engagement. |
| v0.1 baseline abandoned rather than extended | Low | High | Keep the schema stable. Additive changes only within v0.x. |