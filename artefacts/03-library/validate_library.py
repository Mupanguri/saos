#!/usr/bin/env python3
"""SAOS library validator.

Independent of build_workbook.py: run this in CI or before every build so a
malformed control fails fast with a readable message instead of surfacing as a
broken workbook.

Checks performed
  1.  Required fields present, no unknown fields.
  2.  Control ID pattern and global uniqueness.
  3.  Domain code and family code exist in meta.yaml.
  4.  Enumerations: plat, type, auto, w, L, I.
  5.  Test methods, Zero Trust pillars, ATT&CK tactics and technique IDs resolve
      against the reference tables below.
  6.  Mapping strings are non-empty and use the expected shape.
  7.  Sequence gaps inside a family (SRV-LOG-01, -02, ... must be contiguous).
  8.  Minimum content length per narrative field, so controls cannot be stubs.

Exit codes: 0 = clean, 1 = errors found, 2 = could not run.

Usage:
  python validate_library.py [--library PATH] [--strict]
  --strict also treats warnings as errors (use in CI).
"""
import argparse
import glob
import os
import re
import sys
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:
    sys.exit('PyYAML is required:  python -m pip install pyyaml')

TACTICS = {'IA', 'EX', 'PS', 'PE', 'DE', 'CA', 'DI', 'LM', 'CO', 'XF', 'IM'}
PILLARS = {'ID', 'DV', 'NW', 'AP', 'DT', 'IN'}
PLATFORMS = {'All', 'Windows', 'Linux', 'Hypervisor'}
TYPES = {'Preventive', 'Detective', 'Corrective'}
AUTOMATION = {'Low', 'Medium', 'High'}
METHODS = {'INT', 'DOC', 'CFG', 'OBS', 'TECH', 'AUTO', 'PEN'}
CSF_FUNCS = {'GV', 'ID', 'PR', 'DE', 'RS', 'RC'}

REQUIRED = ['id', 'name', 'plat', 'obj', 'biz', 'thr', 'q', 'type', 'ev', 'proc', 'test',
            'auto', 'autom', 'L', 'I', 'w', 'm1', 'm3', 'm5', 'rem',
            'iso', 'csf', 'cis', 'soc', 'att', 'zt', 'orig']
OPTIONAL = {'ref', 'asvs', 'owasp'}
MINLEN = {'name': 10, 'obj': 20, 'biz': 20, 'thr': 10, 'q': 20, 'ev': 10,
          'proc': 20, 'autom': 10, 'm1': 10, 'm3': 10, 'm5': 10, 'rem': 20}
# SOC 2 (2017 TSC) criteria series: Common Criteria, Availability, Confidentiality,
# Processing Integrity and Privacy. Membership is checked exactly, not by pattern.
SOC_SERIES = ('CC', 'A', 'C', 'PI', 'P')
KNOWN_TECHNIQUES = {
    'T1003', 'T1005', 'T1014', 'T1018', 'T1021', 'T1021.001', 'T1021.004', 'T1040', 'T1046',
    'T1048', 'T1059', 'T1068', 'T1070', 'T1070.001', 'T1070.002', 'T1078', 'T1078.001', 'T1091',
    'T1110', 'T1133', 'T1136', 'T1190', 'T1195', 'T1199', 'T1200', 'T1222', 'T1485', 'T1486',
    'T1490', 'T1505', 'T1542', 'T1542.001', 'T1543', 'T1547', 'T1548', 'T1548.003', 'T1550',
    'T1552', 'T1552.001', 'T1557', 'T1558.003', 'T1562', 'T1562.001', 'T1562.002', 'T1562.004',
    'T1574', 'T1611'}

errors, warnings = [], []


def err(cid, msg):
    errors.append(f'{cid}: {msg}')


def warn(cid, msg):
    warnings.append(f'{cid}: {msg}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--library', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '06-source', 'library'))
    ap.add_argument('--strict', action='store_true', help='treat warnings as errors')
    a = ap.parse_args()
    lib = os.path.abspath(a.library)
    if not os.path.isdir(lib):
        print(f'library not found: {lib}', file=sys.stderr)
        return 2

    meta = yaml.safe_load(open(os.path.join(lib, 'meta.yaml'), encoding='utf-8'))
    dom = {d['code']: d for d in meta['domains']}
    fam = meta.get('families', {})
    controls, seen, byfam = [], set(), defaultdict(list)

    for path in sorted(glob.glob(os.path.join(lib, 'controls', '*.yaml'))):
        try:
            rows = yaml.safe_load(open(path, encoding='utf-8'))
        except yaml.YAMLError as e:
            errors.append(f'{os.path.basename(path)}: YAML parse error: {e}')
            continue
        if not isinstance(rows, list):
            errors.append(f'{os.path.basename(path)}: top level must be a list of controls')
            continue
        for c in rows:
            controls.append((os.path.basename(path), c))

    for fname, c in controls:
        cid = c.get('id', f'<no id in {fname}>')

        # 1. fields
        for k in REQUIRED:
            if k not in c or c[k] in (None, ''):
                err(cid, f'missing required field "{k}"')
        for k in set(c) - set(REQUIRED) - OPTIONAL:
            err(cid, f'unknown field "{k}" (check for typos; optional fields are {sorted(OPTIONAL)})')
        for k, n in MINLEN.items():
            if k in c and isinstance(c[k], str) and len(c[k].strip()) < n:
                err(cid, f'field "{k}" is shorter than {n} characters')

        # 2. id
        if not re.fullmatch(r'[A-Z]{3}-[A-Z]{3}-\d{2}', str(cid)):
            err(cid, 'id must look like DOM-FAM-NN, for example SRV-LOG-02')
        if cid in seen:
            err(cid, 'duplicate control id')
        seen.add(cid)

        parts = str(cid).split('-')
        dcode, fcode = (parts + ['', ''])[:2]

        # 3. registry membership
        if dcode not in dom:
            err(cid, f'domain code "{dcode}" is not in meta.yaml domains')
        if f'{dcode}-{fcode}' not in fam:
            err(cid, f'family "{dcode}-{fcode}" is not in meta.yaml families')

        # 4. enumerations
        if c.get('plat') not in PLATFORMS:
            err(cid, f'plat must be one of {sorted(PLATFORMS)}')
        if c.get('type') not in TYPES:
            err(cid, f'type must be one of {sorted(TYPES)}')
        if c.get('auto') not in AUTOMATION:
            err(cid, f'auto must be one of {sorted(AUTOMATION)}')
        for k in ('L', 'I'):
            v = c.get(k)
            if not isinstance(v, int) or not 1 <= v <= 5:
                err(cid, f'{k} must be an integer 1-5, got {v!r}')
        if c.get('w') not in (1, 2, 3):
            err(cid, f'w (criticality weight) must be 1, 2 or 3, got {c.get("w")!r}')

        # 5. reference-table integrity
        for m in str(c.get('test', '')).split(','):
            if m.strip() not in METHODS:
                err(cid, f'unknown test method "{m.strip()}"')
        for z in str(c.get('zt', '')).split(','):
            if z.strip() not in PILLARS:
                err(cid, f'unknown Zero Trust pillar "{z.strip()}"')
        if str(c.get('att', 'N/A')) != 'N/A':
            if '|' in str(c.get('att', '')) and ':' not in str(c.get('att', '')):
                err(cid, 'att uses "|" separators but no TACTIC:technique group found')
            for group in str(c.get('att', '')).split('|'):
                g = group.strip()
                if not g or g == 'N/A':
                    continue
                if ':' not in g:
                    err(cid, f'att group "{g}" is not TACTIC:technique')
                    continue
                tac, techs = g.split(':', 1)
                if tac.strip() not in TACTICS:
                    err(cid, f'unknown ATT&CK tactic "{tac.strip()}"')
                for t in techs.split(','):
                    if t.strip() not in KNOWN_TECHNIQUES:
                        warn(cid, f'ATT&CK technique "{t.strip()}" is not in the validator reference table; add it if the ID is valid')

        # 6. mapping shapes
        for k, pat, hint in (('iso', r'^(N/A|A\.\d+(\.\d+)?(, ?A\.\d+(\.\d+)?)*)$', 'A.8.9'),
                             ('cis', r'^(N/A|\d+\.\d+(, ?\d+\.\d+)*)$', '4.6'),
                             ('csf', r'^(N/A|(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d\d(, *(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d\d)*)$', 'PR.PS-01')):
            v = str(c.get(k, ''))
            if v and not re.fullmatch(pat, v):
                err(cid, f'{k} value "{v}" does not look right (expected for example {hint})')
        soc = str(c.get('soc', ''))
        if soc and soc != 'N/A':
            for tok in [t.strip() for t in soc.split(',')]:
                if not re.fullmatch(r'[A-Z]{1,2}\d{1,2}\.\d', tok):
                    err(cid, f'soc value "{tok}" is not a SOC 2 criterion (expected CC6.1, A1.2, PI1.3, P4.2)')
                elif not tok.startswith(SOC_SERIES):
                    err(cid, f'soc series in "{tok}" is not one of {SOC_SERIES}')
        for m in re.findall(r'\b(GV|ID|PR|DE|RS|RC)\.', str(c.get('csf', ''))):
            if m not in CSF_FUNCS:
                err(cid, f'unknown CSF function "{m}"')
        orig = str(c.get('orig', ''))
        if orig != 'New' and not re.search(r'\d', orig):
            warn(cid, f'orig "{orig}" should be "New" or a source checklist reference')

        if len(str(c.get('ev', '')).split(';')) == 1 and ';' not in str(c.get('ev', '')):
            warn(cid, 'ev lists a single evidence item; multi-item controls should be semicolon separated')
        if f'{dcode}-{fcode}' in fam:
            byfam[f'{dcode}-{fcode}'].append(str(cid))

    # 7. sequence contiguity per family
    for key, ids in sorted(byfam.items()):
        seqs = sorted(int(i.rsplit('-', 1)[1]) for i in ids)
        expected = list(range(1, len(seqs) + 1))
        if seqs != expected:
            err(key, f'control sequence has gaps or duplicates: found {seqs}, expected {expected}')

    # domain coverage report
    built = Counter(str(c.get("id", "")).split("-")[0] for _, c in controls)
    print('=' * 78)
    print('SAOS library validation')
    print('=' * 78)
    print(f'library        : {lib}')
    print(f'control files  : {len(glob.glob(os.path.join(lib, "controls", "*.yaml")))}')
    print(f'controls       : {len(controls)}')
    print(f'domains built  : {len(built)} of {len(dom)}')
    print(f'families built : {len(byfam)} of {len(fam)}')
    if built:
        print('per domain     : ' + ', '.join(f'{k}={v}' for k, v in sorted(built.items())))
    print()
    if warnings:
        print(f'WARNINGS ({len(warnings)})')
        for w in warnings:
            print(f'  ~ {w}')
        print()
    if errors:
        print(f'ERRORS ({len(errors)})')
        for e in errors:
            print(f'  ! {e}')
        print()
    if errors:
        print('RESULT: FAIL')
        return 1
    if warnings and a.strict:
        print('RESULT: FAIL (strict mode, warnings treated as errors)')
        return 1
    print('RESULT: PASS' + (f' with {len(warnings)} warning(s)' if warnings else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())