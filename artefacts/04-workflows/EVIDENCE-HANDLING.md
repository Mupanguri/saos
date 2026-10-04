# Evidence Handling

How evidence is requested, received, stored, referenced and disposed of — and
why the workbook's evidence chain is designed the way it is.

---

## The chain

Three sheets form a traceable chain. Each link is a foreign key, so the chain
can be walked in both directions at any point during or after the engagement.

```
Library (YAML)                  What is needed and why
   │  ev field, split on ";"
   ▼
Evidence_Requests               What we asked the client for
   ER-SRV-PHY-01-1              257 rows, one per item, v0.1
   │  "Received"
   ▼
Evidence_Register               What we actually got
   EV-001                       200 rows formatted
   │  Evidence Ref(s) on the control
   ▼
Assessment!K (maturity)         The score this evidence supports
   Assessment!P                 Re-performable by a reviewer
   │
   ▼
Findings_Register ──► Risk_Register ──► Remediation_Tracker
   F-001                          R-001              RA-001
```

**The walk that matters:** pick any score, follow `Assessment!P` to the evidence
ID, open that item, see the source system and collection date. That is what
makes an assessment auditable rather than merely persuasive.

**The reverse walk:** pick any client deliverable, find the request ID, find the
control, find the assessment question it answers.

---

## Requesting evidence

`Evidence_Requests` is generated from the `ev` field of each control in the
library. It is already a usable PBC list — request IDs, control names and item
descriptions are populated. You add dates and status.

| Col | Field | Notes |
|---|---|---|
| A | Request ID | `ER-SRV-PHY-01-1` — stable, cite it in client correspondence |
| B–D | Control ID, name, item | Pre-filled |
| E | Date Requested | 🔵 |
| F | Status | 🔵 Not requested / Requested / Received / Partial / Not available / N/A |
| G | Date Received | 🔵 |
| H | Evidence ID | 🔵 `EV-nnn` — closes the loop |
| I | Notes | Chased, substituted, waived |

### Good practice

**Ask for native exports, not screenshots.** A `Get-WinEvent` export or a GPO
report can be re-analysed. A screenshot cannot, and will not survive a technical
review.

**Ask for the machine-readable form.** Registry exports, `auditd` logs, GPO
reports, SIEM query results as CSV, firewall rule sets. These are also what
enables `AUTO` test methods later.

**Split compound items at the source.** `ev: 'Backup policy and evidence of
backups'` becomes one useless request. This is a library authoring issue — fix
it in the YAML rather than trying to unpick it in the request list.

**Set a deadline and name an owner** on the client side. Evidence chasing is the
single largest cause of engagement slippage.

**Prioritise by criticality.** Ask for `SRV-IAM` and `SRV-BCK` evidence in week
one. Those families carry the highest inherent risk and the longest
remediation lead times.

### `Not available` is a finding

When the client cannot produce evidence, the control cannot be scored above 1 —
interview-only caps at maturity 2 (Rule 1). That is not a gap in the assessment;
it **is** the assessment result. Record it as `Not available`, raise a finding
against the missing evidence, and move on.

A common variant worth naming explicitly in the report: evidence that exists but
cannot be produced on request. That is a maturity finding, not a missing-evidence
finding.

---

## Receiving and logging

Every item goes into `Evidence_Register` (200 rows formatted, 6–205). Row 5 is a
worked example.

| Col | Field | Notes |
|---|---|---|
| A | Evidence ID | 🔵 `EV-001` — your scheme, be consistent |
| B | Control ID | 🔵 Drop-down from `Assessment!A`. One item may serve several controls — log it once and reference the ID from each |
| C | Control Name | ⚙️ Auto-looked-up |
| D | Evidence Type | 🔵 16 types — pick the most specific |
| E | Description | 🔵 What it shows, precisely enough for someone else to re-perform the check |
| F | Source System / Asset | 🔵 Which host, tenant, system |
| G | Collection Method | 🔵 Manual / Automated / Client-provided |
| H | Collected By | 🔵 |
| I | Date Collected | 🔵 |
| J | Storage Location / Link | 🔵 Path or reference in the evidence store |
| K | SHA-256 | 🔵 Optional — strongly recommended for anything evidencing a Critical or High finding |
| L | Reviewer | 🔵 |
| M | Review Status | 🔵 Pending / Accepted / Rejected / Needs more |
| N | Confidentiality | 🔵 Public / Internal / Confidential / Restricted |

### Write descriptions for the next person

The description is the only place the substance of an evidence item is recorded.
A reviewer six months from now will not open the file.

Weak: `Screenshot of SIEM`
Strong: `SIEM log-source health dashboard showing last-seen time per server,
captured 2026-10-01; two of 40 sources silent for more than 24 hours`

### "Needs more" is a normal outcome

Rejecting evidence is normal, not adversarial. `Needs more` means the artefact
does not answer the assessment question — usually a partial export, a policy
without the configuration, or a dashboard with no time range. Say what is missing
in the notes and re-request it.

---

## Storage

### Suggested structure

```
Evidence/<engagement-ref>/
├── SRV-PHY-01/
│   ├── ER-SRV-PHY-01-1_badge-logs_2026-09-28.zip
│   │     └── evidence.md          what it is, what it shows, hash, chain of custody
│   └── ER-SRV-PHY-01-2_access-list.pdf
├── SRV-LOG-02/
│   └── ...
└── manifest.csv                   generated from Evidence_Register
```

**One folder per control ID**, named for the request. The control ID is the only
identifier that is stable across the engagement, the report and any re-test.

### Storage principles

| Principle | Reason |
|---|---|
| Use the client's evidence store where one exists | You will be asked to delete or hand over at the end. Do not create a second copy you then have to find |
| Encrypt at rest | Evidence routinely contains credentials, keys, internal IPs, personal data and customer data |
| Restrict by engagement | Evidence from one client must never be visible to another. This is the most common real-world leak in assessment work |
| Record SHA-256 on receipt | Proves the artefact is unaltered since collection. Cheap insurance for Critical findings |
| Never store credentials | If evidence contains a secret, redact it and record what was redacted. A stored plaintext password in an evidence pack is an incident |
| Log chain of custody for anything disputed | Date, collector, method, hash |

### Confidentiality

`Evidence_Register!N` carries Public / Internal / Confidential / Restricted.
Most assessment evidence is **Confidential** at minimum; anything showing
personal data, customer data or authentication material is **Restricted**.

Restricted evidence frequently cannot go into the report appendix. Reference it
by Evidence ID and state that it is available on request under separate cover.

---

## Client-supplied evidence

Mark `Collection Method` as `Client-provided` and record the date **you received
it**, not the date it was generated. You are attesting to what you received, not
to when it was created.

Where a client artefact could have been edited after the fact and it matters,
say so in the notes. A screenshot supplied by the client with no metadata is weak
evidence regardless of how convincing it looks — score accordingly.

---

## Automated evidence

33 of 60 controls declare `AUTO` as a permitted test method, and 31 have `auto:
High`. This is where an assessment gets both faster and more defensible.

| Approach | Example |
|---|---|
| Platform API | Intune compliance reports, Entra sign-in logs and Conditional Access reports, Redfish for BMC firmware |
| Configuration management | GPO export, Ansible check mode, OpenSCAP, CIS-CAT |
| Configuration as code | Parsed firewall rules, `sshd -T` compliance scans |
| EDR / SIEM | Defender for Endpoint device inventory, SIEM API last-seen per source |
| Fleet inventory | `osquery` scheduled queries — listening ports, services, programs tables |
| Reconciliations | Badge export vs HR leavers; CMDB vs scanner coverage; backup platform API vs CMDB |

**Reconciliation checks are the highest-value automation in the toolkit.** They
compare two independent sources and the disagreement *is* the finding:

- Badge system vs HR leaver list → access revocation failures
- CMDB vs vulnerability scanner → unscanned assets, unsupported OS
- SIEM last-seen vs known servers → silent log sources
- Backup platform vs CMDB → unprotected systems
- HR vs IAM → dormant and orphan accounts

Where an automated check produces a finding, record the script or query in the
notes so the client can re-run it. A check the client can reproduce themselves is
worth more than a paragraph of narrative.

---

## Integrity and reproducibility

| Field | Use |
|---|---|
| `Date Collected` | Evidence freshness. A 14-month-old baseline export proves the environment was compliant then, not now |
| `Collected By` | Accountability, and knowing who to ask about context |
| `Collection Method` | Distinguishes a verified configuration export from a self-report |
| `Source System / Asset` | Whether the evidence actually covers the in-scope population |
| `SHA-256` | Proves unaltered since collection |
| `Review Status` | Accepted means a reviewer agreed it answers the question |

### Sampling evidence

When the population is too large to collect from every asset, record in
`Assessment!Q`:

- The sample size and how it was selected
- The selection criteria, stated so it can be repeated
- What the sample does and does not cover
- Whether any sampled item was an outlier

Prefer 10–15% of the population, minimum 5, maximum 25, stratified across
platform, environment and business unit. For most controls the exceptions matter
more than the median, so stratify toward risk rather than sampling uniformly.

---

## Retention and disposal

| Item | Retention |
|---|---|
| Engagement evidence | Per the client's instruction and applicable regulation. Typically 7 years where a SOC 2 or ISO 27001 scope exists |
| Evidence containing personal data | Apply the client's retention schedule and any applicable privacy law |
| Evidence containing credentials or keys | Redact on receipt; destroy the original |
| Your working copies after the engagement | Delete, or return to the client. Do not retain for convenience |
| sample and template evidence | Never contains client data; safe to retain |

**Disposal must be evidenced.** Record what was destroyed, when, by whom and by
what method. If the client's policy requires a certificate of destruction,
obtain one.

---

## Quality checklist

Before the report is drafted:

- [ ] Every scored control has at least one evidence ID in `Assessment!P`
- [ ] Every control scored 3+ has an operating-evidence artefact, not only a policy
- [ ] Every evidence description is understandable without opening the file
- [ ] Every `Source System / Asset` is specific enough to confirm coverage
- [ ] `Not available` items have findings raised against them
- [ ] Critical and High findings have hashes recorded
- [ ] Evidence is stored in one place, access-restricted, encrypted
- [ ] No credentials or secrets in any artefact
- [ ] Chain of custody recorded for anything disputed
- [ ] Evidence requests received % on the Dashboard is accurate
- [ ] Retention and disposal instructions confirmed with the client
- [ ] No evidence from another engagement is reachable from this evidence store