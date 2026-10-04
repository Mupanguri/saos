# Methodology

How SAOS turns evidence into a maturity score, a risk rating and a defensible
executive conclusion.

The method has four parts, applied in this order:

1. **Scope** — decide what is in scope; applicability and targets flow from it
2. **Test** — apply the permitted methods and collect the specified evidence
3. **Score** — maturity 0–5, subject to evidence and coverage caps
4. **Rate** — inherent risk from likelihood and impact, residual from maturity

Everything else in the workbook is presentation.

---

## 1. Scope

### Domain and platform scope

`Scope` drives two things automatically:

- **Applicability.** `Assessment!J` (Applicable?) resolves to `No` when either
  the control's domain or its platform is out of scope. Out-of-scope controls
  show `N/A` and drop out of every dashboard average — deliberately, so an
  average never mixes assessed and excluded controls.
- **Target maturity.** `Assessment!L` defaults from the tier table, and
  `Scope!C13` derives from the selected org tier.

### Default targets by organisation tier

| Tier | Default target | Typical rationale |
|---|---|---|
| SMB | 2.0 | Limited budget and headcount. Repeatable beats documented-and-unoperated. |
| Mid-size | 3.0 | Documented and operating, without formal measurement. |
| Enterprise | 3.0 | Same bar; maturity differentiation shows in coverage and measurement, not documentation. |
| Multinational | 4.0 | Multi-jurisdiction consistency and measurement become the differentiator. |
| Government | 4.0 | As above, plus demonstrable oversight. |

Override `Scope!C13` when the client has a published target or risk appetite.
Override individual cells in `Assessment!L` where a specific control warrants a
different target — and say why in the notes. A target with no stated rationale
is an assumption the client will challenge.

### The platform trap

A control with `plat: All` remains applicable whatever the platform scope says.
A control with `plat: Linux` is marked `No` if Linux is out of scope. This is
correct, but it means a client with, say, no Linux estate still sees
platform-specific Server Security controls silently drop to `N/A`. Confirm the
platform scope is genuinely accurate before the assessment, not after — it is
much harder to defend a report that quietly excluded half a control family.

---

## 2. Test

### Permitted test methods

| Code | Method | What it establishes |
|---|---|---|
| INT | Interview | What people say they do. Weakest evidence on its own. |
| DOC | Document review | What is written and approved. |
| CFG | Configuration review | What is actually configured. |
| OBS | Observation | What happens during a live operation. |
| TECH | Technical validation | Measured output from a command, query or tool. |
| AUTO | Automated validation | The same, executed at scale by script or platform API. |
| PEN | Penetration validation | Whether an adversary could actually do it. Requires rules of engagement. |

Each control declares which methods apply. The assessor records which were
**actually performed** in `Assessment!O`. The gap between declared and performed
is itself informative — a control where only DOC was possible has not been
tested, it has been read.

### Evidence discipline

Three principles, all aimed at the same failure mode (an assessor writing what
they want to be true):

1. **Evidence, not assertion.** A score above 1 requires an artefact. Interview
   testimony alone caps the score at 2.
2. **Sample, do not survey.** Take a documented sample, state how it was chosen,
   and record the sample in the notes. "10 servers selected by highest risk
   rating" is defensible; "random servers" is not, because you cannot reproduce
   it.
3. **Record the evidence ID.** Every score must point at an entry in
   `Evidence_Register`. This is what makes the assessment re-performable by a
   reviewer, and it is the field most often skipped.

---

## 3. Score — the maturity model

| Level | Name | Meaning | Coverage |
|---|---|---|---|
| 0 | Non-Existent | No control, no awareness of the need, or the control cannot be demonstrated. | 0% |
| 1 | Initial | Ad hoc and informal; depends on individuals; not documented. | <25% |
| 2 | Repeatable | Similar tasks are done similarly but not consistently documented or approved. | 25–74% |
| 3 | Defined | Documented, approved, communicated and consistently implemented across scope; operating evidence exists. | ≥75% |
| 4 | Managed | Measured and monitored with metrics; exceptions governed; regular management review. | ≥90% |
| 5 | Optimized | Continuously improved, automated and threat-informed; assurance is built in. | ≥95% with automation |

### The six scoring rules

These are the load-bearing part of the method. Without them, maturity scores
inflate towards the documentation the client happens to own.

**Rule 1 — Evidence cap.** A score above 1 requires at least one piece of
operating evidence, not just a policy. Interview-only evidence caps the score
at **2**.

**Rule 2 — Coverage cap.** If the control covers under 50% of in-scope assets,
the maximum is **2**. Under 90%, the maximum is **3**.

**Rule 3 — Design versus operation.** Documented design without proof of
operation caps the score at **2**. Consistent operation proven by sampling
supports **3**.

**Rule 4 — Measurement gate.** Level 4 requires measurement — metrics, reviews,
tested outcomes — *in addition to* level 3 criteria. Level 5 requires automation
or continuous assurance. "We have a dashboard nobody reads" is level 3 at best.

**Rule 5 — Anchor calibration.** Use the control's own `m1`, `m3` and `m5`
anchors. Interpolate L2 and L4 as "between" the anchors. The anchors describe
states, so they are the calibration reference — not your intuition about what
maturity looks like in this organisation.

**Rule 6 — Reproducibility.** Record the evidence ID used for each score so any
score can be re-performed by a reviewer.

### Worked example

`SRV-LOG-02` — logs are forwarded to a central, tamper-resistant store.

| Observation | Inference |
|---|---|
| Policy exists and is approved | Level 3 candidate on documentation |
| Forwarding confirmed on 60% of in-scope servers | Coverage 60% → Rule 2 caps at **3** |
| No alert exists for cleared Security logs | The control is not operating as designed |
| 3 of 4 sampled hosts evidenced by config export | Consistent operation on the sample |
| **Score: 2** | Operating evidence exists but coverage and detection are incomplete |

Target 3, gap 1. Note that the policy being approved did **not** earn level 3 —
Rule 3 blocks it, because there is no proof the design operates as written.

### Aggregation

```
Domain maturity  = Σ(weight × current maturity) / Σ(weight)      over in-scope assessed controls
Family maturity  = same, within one family
Overall maturity = same, across all in-scope assessed controls
```

Only controls that are **in scope** and **assessed** (a numeric score is
present) contribute. Criticality weights are 1 (low), 2 (medium), 3 (high) and
come from the library, so a trivial control cannot drag a domain score down.

Status from the gap:

| Gap | Status |
|---|---|
| ≤ 0 | On target |
| ≤ 1.0 | Minor gap |
| > 1.0 | Significant gap |

---

## 4. Rate — the risk model

```
Inherent risk = Likelihood × Impact                    (1 to 25)
Residual risk = Inherent × (1 − Effectiveness)         (0.0 to 25.0)
```

### Likelihood

The probability that the weakness is exploited, or that the control fails,
within 12 months.

| L | Label | Description |
|---|---|---|
| 1 | Rare | Needs highly skilled, targeted effort; not exposed, or multiple strong compensating controls. |
| 2 | Unlikely | Exploitation needs privileged access or unusual conditions. |
| 3 | Possible | A motivated attacker with moderate skill could exploit it using known techniques. |
| 4 | Likely | Commodity tooling or a common technique in this sector; plausible within the year. |
| 5 | Almost certain | Actively exploited in the wild, trivially exploitable, or already exposed. |

### Impact

Calibrated across five dimensions. The assessor picks the **highest** dimension
that applies — impact is not an average.

| I | Label | Financial | Operational | Regulatory and legal | Reputational | Data / confidentiality |
|---|---|---|---|---|---|---|
| 1 | Negligible | <0.1% revenue | No noticeable disruption | No notification or findings | No external awareness | No sensitive data affected |
| 2 | Minor | 0.1–0.5% | Non-critical service <4h | Minor policy breach, internal finding | Limited internal awareness | Small amount of internal data |
| 3 | Moderate | 0.5–2% | Business service 4–24h | Audit finding or possible regulator notification | Customer complaints, local media | Confidential data, limited volume |
| 4 | Major | 2–5% | Multi-day outage of a critical service | Regulatory investigation or fines likely | National media, customer loss | Large volume of confidential or personal data |
| 5 | Severe | >5% or threatens viability | Prolonged enterprise-wide outage; safety impact | Licence at risk, major fines, prosecution | Sustained loss of trust | Mass exposure of regulated or crown-jewel data |

Financial thresholds are expressed as a percentage of annual revenue so they
transfer across organisations of different sizes. Replace them with the client's
risk appetite statement where one exists, and disclose the change.

### Control effectiveness

The share of inherent risk the control removes at each maturity level.

| Maturity | Effectiveness |
|---|---|
| 0 Non-Existent | 0% |
| 1 Initial | 10% |
| 2 Repeatable | 30% |
| 3 Defined | 55% |
| 4 Managed | 75% |
| 5 Optimized | 90% |

> **These six numbers are calibration assumptions, not measurements.** They are
> editable in `Risk_Model` precisely because they should be challenged. If a
> client has published risk-effectiveness data, use it. Whatever is used must be
> recorded in the engagement file and described in report section 3.

### Rating bands

| Band | Rating | Expected response | Suggested timeline |
|---|---|---|---|
| 0 | Low | Accept or monitor; address in the normal improvement cycle. | Within 12 months |
| 5 | Medium | Plan and fund remediation; owner assigned. | Within 6 months |
| 10 | High | Prioritised remediation; monthly reporting to management. | Within 90 days |
| 17 | Critical | Immediate escalation to CISO and executive risk owner. | Within 30 days or compensating control now |

Band 0 starts at zero rather than one because residual scores are fractional
and a residual of 0.5 is not the same as an inherent of 0.5.

### Overrides

`Assessment!R` and `Assessment!S` override the library defaults for likelihood
and impact. Use them where client context genuinely differs — a control scored
L4 by default in a company with no internet-facing estate may be L2.

Then `Assessment!T`/`U` resolve *used* values as override-or-default, so the
defaults remain visible and the override is auditable. There is no dedicated
reason column (F-09), so record the justification in the notes column.

### Worked example, complete

`SRV-LOG-02`, maturity 2, no override:

```
L4 × I5 = 20                                  inherent          → Critical
Effectiveness at maturity 2 = 30%
20 × (1 − 0.30) = 14.0                        residual          → High
```

Note the gap between inherent and residual rating. This is the intended
behaviour and it is worth understanding before a client asks: a control can be
**critically** important to prevent and only **partially** effective as
currently operated. The roadmap is what closes that distance — maturity 3 would
give 55% effectiveness and a residual of 9.0 (Medium).

---

## 5. From results to a conclusion

The workbook produces numbers. The report has to make an argument. The
transformation:

| Workbook output | Report output |
|---|---|
| Overall maturity + target | One sentence: where the organisation is against the bar for its size and sector |
| Family heat map | The three themes that matter, in business language |
| Top 10 residual risks | Business scenarios — "an attacker who phishes one helpdesk account can delete all backups" — not "SRV-BCK-06 scores 12.4" |
| Findings by severity | Only Critical and High in the body; everything else in Appendix A |
| Crown jewels + attack paths | Where to put the money, and which chokepoints break several paths at once |
| Framework matrices | Indicative alignment, with the disclaimer that it is not certification |

Rules that keep the report honest:

1. **Write the executive summary last.** It is the hardest section and it should
   reflect what you actually found.
2. **Include genuine strengths.** They build credibility and protect what
   already works. A report with no strengths reads as uninformed.
3. **State exclusions explicitly.** Readers assume anything not excluded was
   assessed.
4. **Do not overclaim the mappings.** Appendix E already carries the correct
   disclaimer: indicative professional judgement, not certification or
   attestation.
5. **Every figure traces to the Dashboard.** Quote the workbook version in
   Document Control.

---

## 6. Limitations

State these in the report, not just in your head:

- Mappings to external frameworks are **indicative** and were authored from
  working knowledge. Verify against the licensed sources before issue (F-04).
- Maturity and risk are **judgements based on the evidence available at the
  time** of assessment. Different assessors with the same evidence may differ by
  one level.
- Findings reflect the state of the environment **during the assessment period
  only**.
- Coverage percentages depend on the client's asset inventory. A thin inventory
  produces a confident-looking coverage figure over a small denominator.
- Validation commands assume standard configurations and must be run only under
  written authorisation, in a test environment first.
- Registers are formatted for 200 rows. Formulas read to row 2000 (F-08).