# Engagement Runbook

How to run a SAOS assessment from kick-off to signed-off report. Expanded from
the six steps in the workbook README with the things that actually go wrong.

**Assumed shape:** one assessor, one reviewer, one client engagement, 4–8 weeks
for a single-domain scope such as the v0.1 Server Security library.

---

## Phase 0 — Before you start

| Check | Why |
|---|---|
| Library validated | `python artefacts/03-library/validate_library.py` — a broken control produces an unusable engagement |
| Library version pinned | Record the control catalogue version in the report's Document Control. A re-tested assessment must compare like with like |
| Mappings verified | F-04. Verify framework mappings against licensed sources **before** client issue, not after |
| Scope deliverable available | Confirm the target domains are actually built. v0.1 covers Server Security only |
| Rules of engagement agreed | Required before any `TECH` or `PEN` testing |
| Evidence store provisioned | Path structure decided before the first evidence item arrives, not after 200 of them |

**Blocker for v0.1:** only Domain 5 (Server Security) can be assessed. OT/ICS and
AI Systems are placeholders (F-07).

---

## Phase 1 — Scope

**Owner:** lead assessor · **Output:** completed `Scope` sheet · **Typical: 2–4 hours including client workshops**

1. **Copy the blank workbook.** Start from `SAOS-Assessment-Workbook-v0.1-BLANK.xlsx`.
   Never reuse a previous client's file — that is how data leaks between
   engagements.
2. **Complete `Scope` rows 4–12:** client, reference, dates, lead assessor,
   reviewer, org tier, industry, regulatory drivers.
3. **Set the org tier** (`Scope!C10`). This drives the default target maturity.
   Getting the tier wrong shifts every target in the assessment.
4. **Review the target** (`Scope!C13`). If the client has a published maturity
   target or risk appetite, use it and say so in report section 3.
5. **Platform scope** (`C18:C20`). Confirm against the real estate, not the
   network diagram. This silently removes platform-specific controls.
6. **Domain scope** (`B24:C41`). One Yes/No per domain.
7. **Record explicit exclusions in the report's scope table.** Readers assume
   anything not excluded was assessed. This is the most common scope dispute in
   post-engagement review.

**Reviewer checkpoint:** scope signed off in writing before testing begins.

> **Watch:** a domain marked `No` removes every control in it from the dashboard
> and from all averages. Confirm the domain list with the client explicitly,
> because "you didn't assess our cloud" is otherwise unanswerable.

---

## Phase 2 — Evidence request (PBC)

**Owner:** lead assessor · **Output:** issued request list · **Typical: 1 day to issue, 1–2 weeks to receive**

1. **Export `Evidence_Requests`.** 257 rows for a full Server Security scope,
   one per evidence item, with request IDs `ER-<control-id>-<n>`.
2. **Add the request dates** (column E) and set status to `Requested` (F).
3. **Send to the client** with a deadline and a named owner on their side. State
   the format expected (native export, not screenshots, where possible).
4. **Chase on a schedule.** Set status honestly: `Partial`, `Not available`.
   `Not available` is a finding, not a neutral outcome — a control that cannot be
   evidenced cannot be scored above 1, and that is a real result.
5. **Log receipts** in `Evidence_Register` as items arrive, and write the
   Evidence ID back onto the request row (column H). This closes the loop and
   lets you report "x of y requests received" on the Dashboard.

**Reviewer checkpoint:** evidence completeness reviewed before scoring. Identify
early which controls will be interview-only, because those cap at maturity 2.

> **Highest-value early action:** ask for the CMDB or asset inventory export in
> week one. Coverage-based scoring and the "percentage of in-scope assets"
> claim are both only as good as the inventory behind them.

---

## Phase 3 — Assess

**Owner:** assessor · **Output:** completed `Assessment` sheet · **Typical: 3–5 days per 20 controls**

For each in-scope control:

1. **Read the control.** `name`, `obj`, `biz`, `thr`, `q`, then `ev` and `proc`.
2. **Perform the tests** declared in `test`. Record what you actually performed
   in `Assessment!O`.
3. **Collect or verify the evidence.** Log anything new in `Evidence_Register`
   with type, source system, method, collector, date and storage path.
4. **Score Current Maturity** (`Assessment!K`) using `Maturity_Model` and the
   control's `m1`/`m3`/`m5` anchors. **Apply the caps:**
   - interview-only evidence → maximum **2**
   - under 50% of in-scope assets covered → maximum **2**
   - under 90% covered → maximum **3**
   - documented design with no proof of operation → maximum **2**
   - level 4 needs measurement; level 5 needs automation
5. **Record the evidence IDs** in `Assessment!P`. Non-negotiable — it is what
   makes the score re-performable.
6. **Write the notes** (`Assessment!Q`). Sample method, sample size, what you saw,
   what you could not test and why.
7. **Override L/I if needed** (`R`/`S`) where client context genuinely differs
   from the library default. There is no dedicated reason column (F-09) — put the
   justification in the notes.

### Sampling discipline

State how the sample was chosen and record it. "10 servers selected by highest
risk rating" is defensible and reproducible. "random servers" is not, because
nobody can repeat it and the score cannot be defended in review.

Prefer **10–15% of the population, minimum 5, maximum 25**, stratified so that
each platform, environment and business unit appears. For most controls the
interesting cases are the exceptions, not the median.

### Self-check before moving on

- [ ] Every scored control has at least one evidence ID
- [ ] Every score of 3+ has an operating-evidence artefact, not just a policy
- [ ] Coverage percentages are based on a documented population
- [ ] No control scored above 2 without a `TECH` or `AUTO` test
- [ ] Overrides have a recorded reason
- [ ] `Assessment!M` (gap) and `N` (status) look plausible for your scores

---

## Phase 4 — Findings, risks and remediation

**Owner:** assessor, agreed with client · **Typical: 2–3 days**

### Findings (`Findings_Register`)

One finding per material gap — where the assessed maturity is below target by
enough to matter.

| Field | What good looks like |
|---|---|
| Finding | Plain language: what is wrong and what it exposes. Not "fails SRV-LOG-02" |
| Severity | Consistent with the residual rating the workbook calculated |
| Evidence Ref(s) | The evidence IDs that prove it |
| Recommendation | The action. Reuse the control's `rem` as a starting point, then make it specific to this client |
| Owner | A named person or role, not a department |
| Due Date | Aligned to the severity timeline in `Risk_Model` |

**Severity consistency rule:** if the workbook says a control's residual risk is
Critical but your finding is Medium, one of the two is wrong. Reconcile before
reporting — clients notice.

### Risks (`Risk_Register`)

Every Critical or High residual risk should have a risk entry. Note that the
register pulls `Control Maturity` from the `Assessment` sheet automatically, so
residual risk here is consistent with the assessment by construction.

Write the description as a **business scenario**, not a technical statement:

- Bad: `SRV-BCK-06 has insufficient immutable backup isolation`
- Good: `An attacker who compromises one domain-joined backup server can delete
  all recovery points for the estate`

### Remediation (`Remediation_Tracker`)

One action per finding, or per coherent group of findings. `Control ID` and
`Severity` are inherited from the finding automatically.

Write the action as a deliverable: "Deploy LAPS to 14 remaining servers", not
"improve IAM hygiene".

**Dependencies matter.** Asset inventory before patch compliance reporting;
backup isolation before the ransomware finding can be closed. Record them —
`Attack_Paths!M` (chokepoints) is the best source.

---

## Phase 5 — Context: crown jewels and attack paths

**Owner:** lead assessor with the client's security lead · **Typical: 1 day**

This is the phase that converts a list of control gaps into a prioritised
investment argument, and it is the section executives actually read.

### Crown jewels (20 rows available)

Identify 5–15 critical assets or services. For each:

- **C / I / A** scored 1–5. `Criticality` takes the **highest** dimension.
- **RTO and RPO** — ask the business owner, do not guess from the technical
  documentation.
- **Upstream and downstream dependencies** — this is where attack paths start
  and what determines the blast radius.
- **High-Value Target?** — drives ATT&CK prioritisation in the report.

### Attack paths (20 rows available)

Document realistic paths to each crown jewel, across all five categories:
External, Internal, Cloud, Identity, Supply Chain.

For each path:

1. **Entry point** — realistic, not theoretical.
2. **Numbered steps** — the actual route an attacker would take.
3. **Enabling weaknesses** — the control and finding IDs the path depends on.
   This is what ties the path back to the assessment.
4. **Existing detection** — what would catch it, and at which stage it stops.
   "EDR alerts only on the final stage" is a finding in itself.
5. **Recommended chokepoints** — where one control change breaks several paths
   at once. **The highest-value output of the whole engagement.** Three
   chokepoints that each break four paths is a better recommendation than thirty
   individual findings.

**Client validation is essential here.** An attack path the client's own team
believes is impossible will damage your credibility more than any finding.

---

## Phase 6 — Review and report

**Owner:** assessor, then reviewer · **Typical: 3–5 days**

### Quality review (before drafting)

- [ ] `validate_library.py` still passes
- [ ] Every score has an evidence ID
- [ ] Scores of 3+ have operating evidence
- [ ] Severity is consistent with residual ratings
- [ ] Findings all have owners and realistic due dates
- [ ] Crown jewels validated with the client
- [ ] Attack paths validated with the client
- [ ] Dashboard figures reconciled against the registers

### Complete the report

Open `SAOS-Executive-Report-Template-v0.1.docx`.

1. **Replace every red bracketed placeholder.** They are red for a reason —
   a leftover placeholder is the most embarrassing error in this document type.
2. **Delete every grey guidance box.** They are instructions to you, not content.
3. **Write the executive summary last.** Maximum one page, plain language, for
   someone who does not do this for a living. Structure: overall conclusion,
   three to five messages that matter, the decisions you need from leadership.
4. **Source every figure from the `Dashboard` sheet.** Do not compute anything by
   hand and do not take numbers from an email.
5. **Quote the workbook version** in Document Control.
6. **State exclusions explicitly** in section 2.
7. **Keep the Appendix E disclaimer intact.** Framework mappings are indicative
   judgement, not certification or attestation.

### Refresh the table of contents

The TOC is a field. In Word press `Ctrl+A` then `F9`, and choose *Update entire
table*. (F-11.)

### Deliver

| Item | Format |
|---|---|
| Executive report | PDF for issue; DOCX for the client's markup |
| Assessment workbook | XLSX with the filename convention from `FILE-FORMAT-GUIDE.md` |
| Evidence index | CSV export of `Evidence_Register` |
| Evidence pack | Per the client's evidence handling requirements — see `EVIDENCE-HANDLING.md` |

**Never issue:** a `--sample` build, a workbook with grey guidance boxes, or a
report where the workbook version does not match the file you sent.

---

## Phase 7 — Close

| Action | Detail |
|---|---|
| Archive | Workbook, report, evidence pack, engagement file |
| Record the calibration | Any change to `Risk_Model` impact thresholds or effectiveness percentages |
| Record the overrides | Likelihood and impact overrides with reasons |
| Feed the trend | Copy the Dashboard live values into the next empty trend row, paste as values |
| Log the gaps | Controls that could not be assessed, and why — this drives the next version's scope |
| Update the roadmap | Feed real engagement experience back into `BUILD-ROADMAP.md` |

> **The trend table is manual.** Nothing accumulates automatically. If you skip
> this step you lose the ability to demonstrate improvement, which is usually the
> first question at the next annual review.

---

## Roles and review gates

| Gate | Who | What must be true |
|---|---|---|
| Scope sign-off | Lead assessor + client | Domains, platforms, exclusions agreed in writing |
| Evidence completeness | Lead assessor | Which controls are interview-only identified |
| Quality review | Independent reviewer | Sampling, caps applied, evidence IDs present, severity consistent |
| Attack path validation | Lead assessor + client security lead | Client agrees the paths are realistic |
| Report review | Independent reviewer | No placeholders, no guidance boxes, figures trace to Dashboard |
| Issue | Engagement partner | Approvals complete, filenames correct, version recorded |

---

## Effort estimate — one domain (60 controls)

| Phase | Hours |
|---|---|
| Scope | 4–8 (incl. client workshops) |
| Evidence request | 4 (issue) + client-dependent wait |
| Assess | 24–40 |
| Findings, risks, remediation | 16–24 |
| Crown jewels and attack paths | 6–8 |
| Report and review | 24–40 |
| **Total assessor effort** | **~80–120 hours** |

Client-side effort is typically 40–80 hours, dominated by evidence collection.
Set that expectation at kick-off; evidence chasing is the most common cause of
slippage.

---

## Common failure modes

| Failure | Consequence | Prevention |
|---|---|---|
| Assessor scores from policy alone | Inflated maturity, indefensible report | Rule 3 caps it at 2. Reviewer checks for operating evidence on every 3+ |
| Coverage claimed over an unverified population | Confident number over a small denominator | Ask for the CMDB in week one |
| Domain scope set too wide | Silent `N/A` on controls nobody scoped out | Confirm the domain list explicitly with the client |
| `Risk_Model` rows edited | Every rating formula breaks silently | Treat as fixed layout; change values, not rows |
| Rows inserted mid-table | Formula ranges misalign | Append at the bottom only |
| Recalculation skipped after build | Previewers and `pandas` see blanks | Recalculate in Excel or LibreOffice before sending |
| sample file issued as a client deliverable | Data-governance incident | Use the naming convention; check the README banner before issue |
| Executive summary written first | Says something the evidence does not support | Write it last |
| Guidance boxes left in the report | Client receives a template | Search the DOCX for grey-shaded paragraphs before issue |
| Overrides with no recorded reason | Risk maths cannot be reconstructed | Note the reason in `Assessment!Q` |