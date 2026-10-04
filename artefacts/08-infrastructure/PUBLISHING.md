# Publishing to GitHub

Verified command sequence for putting this repository on GitHub. Tested against
git 2.51.2 on Windows PowerShell.

---

## Before you start

| Check | Why |
|---|---|
| `.gitignore` present at the repository root | Excludes the pre-packaging originals and every build artefact |
| No client data anywhere in the staged set | Engagement data must never enter version control |
| `git --version` | Any 2.x works |
| A GitHub account | — |
| Decide: public or private | **Read the warning below** |

> ### ⚠ Decide public vs private before you push
> This repository contains a complete, unredacted **control library** — 60
> controls with maturity anchors, validation procedures containing real commands,
> and remediation guidance. That is your intellectual property and methodology.
>
> **Make it private unless you intend to open-source the framework.** Public and
> irreversible: once pushed, assume it has been cloned, cached and indexed. GitHub
> also indexes public repositories into search engines and code-search services.
>
> If you want the code public but the method private, publish
> `artefacts/06-source/` and `artefacts/03-library/` only, and keep
> `01-governance/`, `02-methodology/` and `07-reference/` in a private repository.

---

## Step 1 — Configure git identity

Skip if you have already set this globally. Verify first:

```powershell
git config --global user.name
git config --global user.email
```

Both empty on this machine. Set them:

```powershell
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
```

Use the same email you use for GitHub, or the noreply address GitHub provides
(`<id>+<username>@users.noreply.github.com`) if you want to hide it from public
commit metadata.

---

## Step 2 — Initialise and stage

```powershell
cd "C:\Users\RonaldMupanguri\Downloads\New Stuff"
git init -b main
git add -A
git status
```

**Read the `git status` output before committing.** You should see 38 files:

| Location | Count |
|---|---|
| `README.md` | 1 |
| `.gitignore` | 1 |
| `artefacts/` | 36 |

Confirm these are **absent** — they are the pre-packaging originals, superseded by
`artefacts/`:

```
SAOS Assessment Workbook v0.1.xlsx
SAOS Workbook v0.1 Client 1 retracted Data.xlsx
SAOS Executive Report Template.docx
SAOS_Source_Library_v0.1/
```

If any appear, stop and fix `.gitignore`. Verify explicitly:

```powershell
git check-ignore -v "SAOS Workbook v0.1 Client 1 retracted Data.xlsx"
```

Expected: a line naming `.gitignore` and the matching pattern. Exit code `0`
means ignored.

---

## Step 3 — Commit

```powershell
git commit -m "SAOS v0.1: control library, workbook generator and assessment methodology

Vendor-neutral security assessment toolkit.

- 60 Server Security controls across 13 families, 257 evidence items
- 18-domain registry (905 target controls; 1 domain built)
- Maturity model 0-5 with evidence and coverage scoring caps
- Risk model: inherent = L x I, residual reduced by maturity effectiveness
- 19-sheet engagement workbook generator with live formula chain
- Word executive report template, 8 sections + 5 appendices
- Catalogue exports (CSV/JSON), JSON Schema and an independent validator
- Filename convention and self-declaring provenance on every artefact

All framework mappings are indicative and require verification against the
licensed source documents before client issue."
```

If `git commit` asks for identity, Step 1 was not completed.

---

## Step 4 — Create the GitHub repository

### Option A — GitHub CLI (recommended)

`gh` is **not currently installed** on this machine. Install it:

```powershell
winget install --id GitHub.cli
```

Then close and reopen PowerShell, and:

```powershell
gh auth login
gh auth status

gh repo create saos --private --source=. --remote=origin --push
```

| Flag | Effect |
|---|---|
| `saos` | Repository name. Change as you like |
| `--private` | **Keep this.** See the warning above |
| `--source=.` | Use the current directory |
| `--remote=origin` | Name the remote `origin` |
| `--push` | Push `main` and set upstream in one step |

### Option B — Web interface, no CLI

1. Go to <https://github.com/new> → **New repository**
2. **Repository name:** `saos`
3. **Visibility:** Private
4. **Do not** tick *Add a README*, `.gitignore` or licence — you already have them
5. **Create repository**

Then:

```powershell
git remote add origin https://github.com/<your-username>/saos.git
git push -u origin main
```

GitHub will prompt for credentials. If it asks for a username and password, use a
**Personal Access Token** as the password, not your account password — classic
password auth was removed by GitHub in August 2021.

Create a token at <https://github.com/settings/tokens> with scope `repo` (or
`public_repo` for a public repository).

### Option C — SSH

```powershell
ssh-keygen -t ed25519 -C "you@example.com"
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
```

Paste the clipboard into <https://github.com/settings/keys>, then:

```powershell
git remote add origin git@github.com:<your-username>/saos.git
git push -u origin main
```

---

## Step 5 — Verify

```powershell
git status                      # expect: working tree clean
git log --oneline               # expect: 1 commit
git remote -v                   # expect: origin -> your repo
git ls-files | Measure-Object   # expect: 38
```

Then open the repository URL and confirm:

- [ ] `README.md` renders as the landing page, with a working table of contents
- [ ] All 13 documentation files are reachable from the READMEs
- [ ] `artefacts/MANIFEST.md` renders its tables
- [ ] No client data and no pre-packaging originals are present
- [ ] The repository is **Private** if you followed the recommendation
- [ ] Repository description and topics are set (below)

---

## Step 6 — Repository settings

```powershell
gh repo edit --description "Vendor-neutral security assessment toolkit: control library, scoring engine and client reporting" `
             --add-topic security --add-topic compliance --add-topic risk `
             --add-topic assessment --add-topic python --add-topic excel `
             --enable-issues --enable-wiki=false
```

Web equivalent: **Settings → General → Description**, and **Settings → Topics**.

---

## Branch protection

Worth adding before anyone else touches it. **Settings → Branches → Add rule**:

| Setting | Value |
|---|---|
| Branch name pattern | `main` |
| Require a pull request before merging | On |
| Require approvals | 1 |
| Require status checks | On |
| Require branches to be up to date | On |
| Block force pushes | On |

The library is the product. A force-push to `main` can silently change a control
that 60 client workbooks were built from.

---

## Ongoing workflow

```powershell
# 1. Edit the library — never the generated sheets
notepad artefacts\06-source\library\controls\05_srv_part3.yaml

# 2. Validate (must pass before any commit)
python artefacts\03-library\validate_library.py --strict

# 3. Regenerate exports and read the diff — this IS the review artefact
python artefacts\03-library\export_library.py
git diff artefacts\03-library\control-catalogue.csv

# 4. Commit the library change AND the regenerated exports together
git add artefacts/06-source artefacts/03-library
git commit -m "Add SRV-LOG-07: log source health monitoring

Objective: detect silent log sources before an attacker exploits them.
L4 x I5 = inherent 20; maturity 1 -> residual 18.0 Critical.
Mapped: ISO A.8.15, CSF DE.CM-9, CIS 8.2, SOC CC7.2, ATT&CK T1070.001"
git push
```

**The commit message format above matters.** Each control carries its objective,
risk arithmetic and mappings in the body, so `git log` doubles as the control
change history.

### Release tagging

```powershell
git tag -a v0.1 -m "SAOS v0.1 - Phase 0 foundations + Server Security pilot"
git push origin v0.1
```

Then **Releases → Draft a new release → choose the tag**. The tag is what lets a
client be told exactly which version produced their workbook, and
`MANIFEST.csv` gives the per-file hashes to prove it.

---

## Adding the CI gate

`.github/workflows/validate.yml`:

```yaml
name: validate
on:
  push:
    branches: [main]
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - run: pip install -r artefacts/08-infrastructure/requirements.txt

      - name: Validate control library
        run: python artefacts/03-library/validate_library.py --strict

      - name: Regenerate catalogue exports
        run: python artefacts/03-library/export_library.py

      - name: Golden-file check - exports must be committed and current
        run: |
          git diff --exit-code artefacts/03-library/ \
            || (echo "::error::Catalogue exports are stale. Run export_library.py and commit the result." && exit 1)

      - name: Build workbook
        run: python artefacts/06-source/build/build_workbook.py /tmp/ci.xlsx

      - name: Build workbook with sample data
        run: python artefacts/06-source/build/build_workbook.py /tmp/ci-sample.xlsx --sample
```

That `git diff --exit-code` step is the important one: it makes every library
change **deliberate**. A control edited without regenerating the exports fails
the build.

Create it with:

```powershell
New-Item -ItemType Directory -Force .github\workflows | Out-Null
notepad .github\workflows\validate.yml
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `Please tell me who you are` | Git identity unset | Step 1 |
| `fatal: not a git repository` | Wrong directory | `cd` to the folder containing `.gitignore` |
| `remote origin already exists` | Second run | `git remote set-url origin <url>` |
| `Permission denied (publickey)` | SSH key not registered | Option C, or use HTTPS |
| `Authentication failed` on push | Password used instead of a PAT | Create a token, scopes `repo` |
| `Updates were rejected` | Remote has commits you do not have | `git pull --rebase origin main` then `git push` |
| Pre-packaging originals get committed | `.gitignore` not at the root | It must be beside `README.md`, not inside `artefacts/` |
| `node_modules` committed | `.gitignore` overwritten | Restore it; `git rm -r --cached node_modules` |
| `__pycache__` committed | `.gitignore` missing the rule | It is covered; confirm the file is at the root |
| Client data pushed | Engagement file inside the repo | **Rotate any exposed credentials immediately.** `git rm` is not enough — use `git filter-repo`, then force-push and ask GitHub support to purge caches |

---

## If you accidentally commit something sensitive

Git history is permanent. Removing a file in a later commit does **not** remove
it from history.

```powershell
pip install git-filter-repo
git filter-repo --path <offending-path> --invert-paths
git push --force --mirror origin
```

Then contact GitHub Support to purge cached views and forks. If credentials were
exposed, **rotate them first** — assume anything pushed publicly is compromised.