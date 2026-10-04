# Control Schema

How to write a control that passes validation and is actually usable in an
engagement.

- **Machine-checkable contract:** `../03-library/control-schema.json` (JSON Schema draft 2020-12)
- **Enforced by:** `../03-library/validate_library.py`
- **Worked examples:** `../03-library/control-catalogue.csv` — read the existing 60 before writing new ones

---

## File and structure rules

**File naming.** `library/controls/NN_<domaincode>_partN.yaml`, where `NN` is
the domain number and `partN` splits large families across files for reviewable
diffs.

```
library/
├── meta.yaml                      domain registry + family metadata
└── controls/
    ├── 05_srv_part1.yaml          SRV-PHY, SRV-CFG …
    ├── 05_srv_part2.yaml
    └── 05_srv_part3.yaml
```

**Structure.** Each file is a YAML **list of mappings**. One control per list
item. No document markers, no nesting beyond the list.

```yaml
- id: SRV-LOG-01
  name: …
  # … 27 fields

- id: SRV-LOG-02
  name: …
```

The build script globs `library/controls/*.yaml` in sorted order, so file naming
controls the order controls appear in the workbook. Within a file, list order is
preserved. **Control sequence numbers must be contiguous within each family** —
the validator fails on gaps.

---

## Field reference

27 required fields, 3 optional. Types shown as they must appear in YAML.

### Identity

#### `id` · string · required

Pattern `^[A-Z]{3}-[A-Z]{3}-[0-9]{2}$` — `DOMAIN-FAMILY-SEQUENCE`.

```yaml
id: SRV-LOG-02
```

The domain code must exist in `meta.yaml` domains; the family code must exist in
`meta.yaml` families. Sequence starts at 01 and is contiguous per family.

#### `name` · string · required · min 10 chars

The control statement, written as a **positive assertion of the desired state**.
Not a task, not a question, not a topic.

```yaml
name: Out-of-band management interfaces are isolated and hardened          # good
name: Review BMC configurations                                          # a task, not a control
name: Servers                                                            # a topic, not a control
```

Test: read ten of them in a row. If they could describe a good environment and a
bad one equally, they are not controls.

---

### Scope and rationale

#### `plat` · enum · required

`All` · `Windows` · `Linux` · `Hypervisor`

```yaml
plat: All
```

`All` means the control applies whatever the platform scope says. A specific
value means the control drops to `N/A` when that platform is out of scope — which
is correct, but be deliberate. 54 of 60 controls are `All`; 5 `Hypervisor`; 1
`Linux`.

#### `obj` · string · required · min 20 chars

**Objective.** What the control achieves, and why it is written this way. This
is where design rationale belongs — a future maintainer needs to know why the
control is scoped the way it is before they widen or narrow it.

```yaml
obj: Ensure BMC, iDRAC, iLO, IPMI and KVM-over-IP interfaces cannot be used to take over servers.
```

#### `biz` · string · required · min 20 chars

**Business justification.** The consequence of absence, in business language.
This field is quoted verbatim into executive-facing material, so it must survive
being read to someone who has never heard of a BMC.

```yaml
biz: A compromised BMC gives console, power and virtual-media control that sits below the operating system and its security tooling.
```

Test: would a CFO understand the consequence in this sentence? If it is purely
technical, rewrite it.

#### `thr` · string · required · min 10 chars

**Threat prevented.** Semicolon-separated threat scenarios.

```yaml
thr: BMC firmware and IPMI protocol exploitation, default credentials, firmware implants, remote console takeover.
```

These scenarios drive the ATT&CK mapping. If you cannot write a threat here, the
control may not be pulling its weight.

#### `q` · string · required · min 20 chars

**Assessment question.** The single question the assessor answers.

```yaml
q: Are out-of-band management interfaces on a dedicated management network, patched, with default credentials changed and strong authentication enforced?
```

One question, answerable, unambiguous. Compound questions ("…and are they also
monitored?") produce inconsistent scores between assessors.

---

### Testing

#### `type` · enum · required

`Preventive` (44) · `Detective` (11) · `Corrective` (5)

#### `ev` · string · required · min 10 chars

**Evidence required.** Semicolon-separated. **Each semicolon-separated item
becomes one row on the Evidence_Requests sheet** with its own request ID
`ER-<control-id>-<n>`. 257 items across 60 controls, mean 4.3.

```yaml
ev: Management network diagram; BMC inventory with firmware versions; firewall rules for the management VLAN; BMC user list and authentication settings
```

**Split compound items.** This is the single most common mistake:

```yaml
ev: Backup policy and evidence of backups        # useless: one row, two things
ev: Backup policy; evidence of backups          # correct: two requests
```

A useful evidence item is something a client can hand over as a discrete
artefact. If you cannot imagine the client attaching it, split it differently.

#### `proc` · string · required · min 20 chars

**Validation procedure.** Step-by-step test instructions. Use a `|-` block
scalar. Include real commands and real portal paths.

```yaml
proc: |-
  From an authorised host on the management VLAN, discover IPMI exposure with `nmap -sU -p 623 --script ipmi-version <mgmt-subnet>` and confirm IPMI-over-LAN is disabled or restricted.
  Review BMC accounts, TLS certificate and firmware date in the web console or via Redfish (`curl -k -u <user> https://<bmc>/redfish/v1/Managers`).
  Confirm the BMC subnet is unreachable from user and internet segments (`nc -vz <bmc-ip> 443` from a user VLAN should fail).
```

Requirements for a usable procedure:

1. **Number the steps** or use separate lines. A paragraph is not a procedure.
2. **Say what you expect to see.** "…should fail" tells the assessor what a pass
   looks like.
3. **Use placeholders in angle brackets**: `<mgmt-subnet>`, `<bmc-ip>`, `<user>`.
   Never a real hostname, IP or credential.
4. **Mark destructive or intrusive steps** and state the authorisation needed.
5. **Name the sampling approach** where a sample is needed.

> Commands in `proc` are technical validation. They must be run only under
> written authorisation, and in a test environment first. Never embed
> credentials.

#### `test` · string · required

Comma-separated, no spaces: `INT` `DOC` `CFG` `OBS` `TECH` `AUTO` `PEN`.

```yaml
test: INT,CFG,TECH
```

| Code | Method |
|---|---|
| INT | Interview |
| DOC | Document review |
| CFG | Configuration review |
| OBS | Observation |
| TECH | Technical validation |
| AUTO | Automated validation |
| PEN | Penetration validation — requires rules of engagement |

Declare every method that **could** legitimately be used. The assessor records
which they actually performed; the gap between the two is informative. Usage
across the current library: TECH 54, CFG 39, AUTO 33, DOC 25, INT 14, OBS 6,
PEN 2.

#### `auto` · enum · required

`Low` (6) · `Medium` (23) · `High` (31) — automation potential for evidence
collection or testing.

#### `autom` · string · required · min 10 chars

**Automation method.** The specific tool, API or query. Name products, not
categories.

```yaml
autom: Redfish API inventory of firmware versions and accounts; vendor tools (OpenManage, iLO RESTful API).
```

Bad: `Various tools`. Good: `Intune compliance report API`.

---

### Risk and weight

#### `L` · integer 1–5 · required

Default likelihood that the weakness is exploited within 12 months. See
`METHODOLOGY.md` for the scale. Defensible on its own, without the client
context.

#### `I` · integer 1–5 · required

Default impact if exploited.

#### `w` · integer 1–3 · required

Criticality weight used in weighted-average maturity: 1 low, 2 medium, 3 high.
Current distribution: 3 → 29 controls, 2 → 27, 1 → 4.

Weight reflects **business criticality**, not implementation difficulty. A
trivial-to-implement control protecting the payment switch is weight 3.

---

### Maturity anchors

#### `m1` · `m3` · `m5` · string · required · min 10 chars each

Descriptions of the **state** at levels 1, 3 and 5. Levels 2 and 4 are
interpolated as "between" the anchors.

```yaml
m1: BMCs reachable from the production LAN with default credentials.
m3: Dedicated management VLAN, unique credentials, firmware versions tracked.
m5: Access only via MFA jump host, Redfish-driven firmware compliance, IPMI-over-LAN disabled, BMC configuration baselined and monitored.
```

Requirements:

- **Describe a state, not an action.** `m1` is what you observe, not what you do.
- **`m3` must be the minimum bar for "defined".** If a client satisfies `m3`,
  the control is operating. If satisfying `m3` is aspirational, the anchor is
  wrong.
- **`m5` must be reachable.** Continuous improvement plus automation, not an
  aspiration to buy a product.
- Keep all three the same grammatical shape so they read as a progression.

---

### Remediation

#### `rem` · string · required · min 20 chars

The concrete action that raises the control to the next level. This is pasted
straight into findings and remediation actions in the sample build, so write it as
a deliverable.

```yaml
rem: Move BMCs to an isolated management network, change all default credentials, disable IPMI-over-LAN or restrict it, patch firmware, and require access through a hardened jump host.
```

---

### Framework mappings

#### `iso` · string · required

ISO/IEC 27001:2022 Annex A controls. `A.8.9, A.8.20` or `N/A`.

```yaml
iso: A.8.9, A.8.20, A.8.22
```

#### `csf` · string · required

NIST CSF 2.0 subcategories. **Must carry the function prefix** or the validator
fails.

```yaml
csf: PR.IR-01, PR.PS-01
```

Valid functions: `GV.` `ID.` `PR.` `DE.` `RS.` `RC.`

#### `cis` · string · required

CIS Controls v8.1 safeguards as `major.minor`.

```yaml
cis: '4.6, 12.2'          # QUOTED — see gotchas
```

#### `soc` · string · required

SOC 2 (2017 TSC) criteria. Series must be `CC`, `A`, `C`, `PI` or `P`.

```yaml
soc: CC6.1, CC6.6
soc: A1.2, CC9.1
```

#### `att` · string · required

MITRE ATT&CK as `TACTIC:technique[,technique]` groups separated by `|`.

```yaml
att: 'IA:T1200'
att: 'IA:T1190 | PS:T1542.001'
att: N/A
```

Tactics: `IA` `EX` `PS` `PE` `DE` `CA` `DI` `LM` `CO` `XF` `IM`.
Technique IDs must exist in the reference table in `build_workbook.py`; the
validator warns on unknown IDs so you can add genuine new ones deliberately.

#### `zt` · string · required

NIST SP 800-207 Zero Trust pillars touched, comma separated: `ID` `DV` `NW` `AP`
`DT` `IN`.

```yaml
zt: NW,IN
```

Be honest about breadth. Quoting every pillar on every control makes the Zero
Trust matrix useless as a prioritisation tool.

#### `orig` · string · required

Checklist origin: `New` for SAOS-authored, or the source checklist reference when
ported.

```yaml
orig: New
orig: '4.6'
orig: '4.1, 4.7'
```

Current split: 16 `New`, 44 ported.

---

### Optional fields

#### `ref` · string

Overrides the family default references from `meta.yaml`. Use for controls that
need a standard the family does not cite.

```yaml
ref: 'NIST SP 800-207; vendor hypervisor hardening guide'
```

#### `asvs` · string

OWASP ASVS chapter. **Unmapped for all v0.1 controls** — blocked on the ASVS
version decision (F-06).

#### `owasp` · string

OWASP Top 10:2021 category. **Unmapped for all v0.1 controls.**

---

## YAML gotchas

These cause silent data loss, not errors. All four are documented in the
original source README.

**1. Quote anything that looks like a number with a decimal point.**

```yaml
cis: 4.6, 12.2      # WRONG → parsed as the float 4.6; "12.2" is lost
cis: '4.6, 12.2'    # RIGHT
```

Applies to `cis`, `orig`, and any field holding a dotted number. The validator
catches the resulting shape error, but you lose the value first.

**2. Quote any text containing a comma inside a `{flow}` mapping.**

```yaml
SRV-BCK: {name: Backup, Restore and Recovery, ref: '…'}   # WRONG: mapping breaks
SRV-BCK: {name: 'Backup, Restore and Recovery', ref: '…'} # RIGHT
```

**3. Never name a key `no` or `yes`.** YAML 1.1 parses them as booleans, so
`no: value` becomes `{False: 'value'}` and the key vanishes.

**4. Use `|-` for multi-line text.** A plain scalar folds newlines into spaces
and mangles any indented command.

```yaml
proc: |-
  Step one.
  Step two.
```

**Also worth knowing:**

- **Tabs are illegal** in YAML indentation. Use spaces.
- **A colon followed by a space** inside an unquoted scalar starts a mapping and
  breaks the line. Quote the string.
- **Duplicate keys silently overwrite.** The validator will not catch a
  duplicated `m3` — check your work when adding fields.
- **Non-ASCII is fine** but keep it UTF-8 and avoid smart quotes inside YAML.

---

## Validation

```powershell
python artefacts\03-library\validate_library.py
python artefacts\03-library\validate_library.py --strict    # CI: warnings fail too
```

### What it checks

| # | Check | Failure means |
|---|---|---|
| 1 | Required fields present; no unknown fields | Typo in a field name silently drops data |
| 2 | ID pattern; global uniqueness | Broken references |
| 3 | Domain and family exist in `meta.yaml` | Control will not score on the Dashboard |
| 4 | `plat`, `type`, `auto`, `L`, `I`, `w` enumerations and ranges | Invalid input to the risk model |
| 5 | Test methods, ZT pillars, ATT&CK tactics and techniques resolve | Dangling references |
| 6 | Mapping string shapes (ISO / CIS / SOC / CSF regexes) | Malformed mapping |
| 7 | Per-family sequence contiguity | Gap in the numbering |
| 8 | Minimum content length per narrative field | Stub controls |

### Current state

```
controls       : 60
domains built  : 1 of 18
families built : 13 of 13
RESULT: PASS
```

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Clean |
| 1 | Errors found (or warnings, in `--strict`) |
| 2 | Could not run — library path missing |

---

## Adding controls — checklist

- [ ] Family exists in `meta.yaml` with `name`, `ref`, `iso_clause`, `app`
- [ ] File named `NN_<domaincode>_partN.yaml`, list of mappings
- [ ] Sequence continues contiguously from the last control in the family
- [ ] All 27 required fields present
- [ ] `name` is a positive assertion of a state
- [ ] `q` is a single question
- [ ] `ev` is split into individually requestable items
- [ ] `proc` is numbered steps with expected results and `<placeholders>`
- [ ] `m1`/`m3`/`m5` describe states, `m3` is a realistic bar
- [ ] `L`, `I`, `w` defensible on their own
- [ ] Six framework mappings present, `N/A` used honestly
- [ ] `cis` and `orig` values quoted
- [ ] `validate_library.py --strict` returns PASS
- [ ] Workbook rebuilt; family appears on the Dashboard
- [ ] `export_library.py` rerun; CSV diff reviewed
- [ ] Changelog updated

---

## Quality bar

A control is finished when a competent assessor who has never seen the domain
can read the name and understand the desired state; answer `q` and reach a
defensible maturity score; follow `proc` and reach the same conclusion as
anyone else; request exactly the evidence in `ev`; and explain to a
non-technical executive, using `biz`, why it matters.

Most failures are in `proc` and `ev`, and they have the same cause: both were
written for the author rather than the reader.