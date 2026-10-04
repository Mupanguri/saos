#!/usr/bin/env python3
"""SAOS library exporter.

Reads the canonical YAML library (library/meta.yaml + library/controls/*.yaml) and
writes machine-readable representations into this directory:

  control-catalogue.csv    Flat, one row per control. Spreadsheet- and BI-friendly.
  control-catalogue.json   Nested, one object per control plus the domain/family registry.
  control-evidence.csv     One row per individual evidence item (drives the PBC list).
  domain-registry.csv      Domain registry with live build counts.
  family-registry.csv      Control-family metadata.
  framework-mapping.csv    Long-format control-to-framework mapping (tidy data).

Usage:
  python export_library.py [--library PATH_TO_SAOS_SOURCE] [--out .]

Defaults assume this file sits in <source>/build-export/ and that the source
library is at ../library. Run `python export_library.py --help` for overrides.
Every artefact is regenerated from YAML; nothing here is hand-edited.
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import sys
from collections import OrderedDict

try:
    import yaml
except ImportError:
    sys.exit('PyYAML is required:  python -m pip install pyyaml')

TACT = OrderedDict([('IA', 'Initial Access'), ('EX', 'Execution'), ('PS', 'Persistence'), ('PE', 'Privilege Escalation'),
                    ('DE', 'Defense Evasion'), ('CA', 'Credential Access'), ('DI', 'Discovery'), ('LM', 'Lateral Movement'),
                    ('CO', 'Collection'), ('XF', 'Exfiltration'), ('IM', 'Impact')])
ZT = OrderedDict([('ID', 'Identity'), ('DV', 'Device'), ('NW', 'Network'), ('AP', 'Application'), ('DT', 'Data'), ('IN', 'Infrastructure')])
TESTS = OrderedDict([('INT', 'Interview'), ('DOC', 'Document Review'), ('CFG', 'Configuration Review'), ('OBS', 'Observation'),
                     ('TECH', 'Technical Validation'), ('AUTO', 'Automated Validation'), ('PEN', 'Penetration Validation')])


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load_library(libdir):
    meta = yaml.safe_load(open(os.path.join(libdir, 'meta.yaml'), encoding='utf8'))
    dom = {d['code']: d for d in meta['domains']}
    fam = meta['families']
    controls = []
    files = []
    for f in sorted(glob.glob(os.path.join(libdir, 'controls', '*.yaml'))):
        rows = yaml.safe_load(open(f, encoding='utf8'))
        files.append({'file': os.path.basename(f), 'controls': len(rows), 'sha256': sha256(f)})
        for c in rows:
            c['_src'] = os.path.basename(f)
            controls.append(c)
    for c in controls:
        parts = c['id'].split('-')
        c['_dom_code'], c['_fam_code'] = parts[0], parts[1]
        c['_domain'] = dom[c['_dom_code']]['name']
        c['_family'] = fam[f'{c["_dom_code"]}-{c["_fam_code"]}']['name']
        c['_tests'] = [t.strip() for t in str(c['test']).split(',') if t.strip()]
        c['_evs'] = [e.strip() for e in str(c['ev']).split(';') if e.strip()]
        c['_zt'] = [z.strip() for z in str(c['zt']).split(',') if z.strip()]
        c['_inherent'] = int(c['L']) * int(c['I'])
    return meta, dom, fam, controls, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--library', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '06-source', 'library'))
    ap.add_argument('--out', default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    libdir = os.path.abspath(args.library)
    out = os.path.abspath(args.out)
    meta, dom, fam, controls, files = load_library(libdir)

    # ---------------------------------------------------------------- CSV: control catalogue
    cols = ['control_id', 'domain_code', 'domain', 'family_code', 'control_family', 'control_name', 'platform',
            'control_type', 'objective', 'business_justification', 'threat_prevented', 'assessment_question',
            'evidence_items', 'validation_procedure', 'test_methods', 'automation_potential', 'automation_method',
            'default_likelihood', 'default_impact', 'inherent_score', 'criticality_weight',
            'maturity_anchor_l1', 'maturity_anchor_l3', 'maturity_anchor_l5', 'remediation_guidance',
            'references', 'iso_27001_2022', 'nist_csf_2_0', 'cis_controls_v8_1', 'soc2_2017_tsc',
            'mitre_attack', 'mitre_tactics', 'zero_trust_pillars', 'checklist_origin', 'source_file']
    with open(os.path.join(out, 'control-catalogue.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for c in controls:
            tactics = []
            if str(c['att']) != 'N/A':
                for part in str(c['att']).split('|'):
                    tactics.append(part.strip().split(':', 1)[0].strip())
            w.writerow([c['id'], c['_dom_code'], c['_domain'], c['_fam_code'], c['_family'], c['name'], c['plat'],
                        c['type'], c['obj'], c['biz'], c['thr'], c['q'], len(c['_evs']), c['proc'],
                        '; '.join(TESTS.get(t, t) for t in c['_tests']), c['auto'], c['autom'],
                        c['L'], c['I'], c['_inherent'], c['w'], c['m1'], c['m3'], c['m5'], c['rem'],
                        c.get('ref') or fam[f'{c["_dom_code"]}-{c["_fam_code"]}']['ref'],
                        c['iso'], c['csf'], c['cis'], c['soc'], c['att'],
                        '; '.join(TACT.get(t, t) for t in tactics), '; '.join(ZT.get(z, z) for z in c['_zt']),
                        c['orig'], c['_src']])

    # ---------------------------------------------------------------- CSV: evidence items
    with open(os.path.join(out, 'control-evidence.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['request_id', 'control_id', 'control_name', 'sequence', 'evidence_item'])
        for c in controls:
            for i, e in enumerate(c['_evs'], start=1):
                w.writerow([f"ER-{c['id']}-{i}", c['id'], c['name'], i, e])

    # ---------------------------------------------------------------- CSV: domain registry
    built = {}
    for c in controls:
        built[c['_dom_code']] = built.get(c['_dom_code'], 0) + 1
    with open(os.path.join(out, 'domain-registry.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['num', 'code', 'domain', 'scope', 'target_controls', 'controls_built', 'percent_of_target',
                    'proposed_batch', 'status'])
        tt = tb = 0
        for d in meta['domains']:
            n = built.get(d['code'], 0)
            tt += d['target']
            tb += n
            pct = 'n/a' if d['target'] == 0 else round(n / d['target'], 4)
            status = 'Placeholder' if d['target'] == 0 else ('Not started' if n == 0 else ('Complete' if n >= d['target'] else 'In progress'))
            w.writerow([d['num'], d['code'], d['name'], d['scope'], d['target'], n, pct, d['batch'], status])
        w.writerow(['', '', 'Total', '', tt, tb, round(tb / tt, 4) if tt else '', '', ''])

    # ---------------------------------------------------------------- CSV: family registry
    with open(os.path.join(out, 'family-registry.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['family_key', 'family_name', 'controls_built', 'default_references',
                    'iso_27001_management_system_clauses', 'iso_iec_27034_category'])
        cnt = {}
        for c in controls:
            k = f'{c["_dom_code"]}-{c["_fam_code"]}'
            cnt[k] = cnt.get(k, 0) + 1
        for k, v in fam.items():
            w.writerow([k, v['name'], cnt.get(k, 0), v['ref'], v['iso_clause'], v['app']])

    # ---------------------------------------------------------------- CSV: tidy framework mapping
    with open(os.path.join(out, 'framework-mapping.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['control_id', 'control_name', 'framework', 'mapping', 'mapping_level'])
        for c in controls:
            fk = f'{c["_dom_code"]}-{c["_fam_code"]}'
            rows = [('ISO/IEC 27001:2022 Annex A', c['iso'], 'control'),
                    ('ISO/IEC 27001:2022 management system', fam[fk]['iso_clause'], 'family'),
                    ('NIST CSF 2.0', c['csf'], 'control'),
                    ('CIS Controls v8.1', c['cis'], 'control'),
                    ('SOC 2 (2017 TSC)', c['soc'], 'control'),
                    ('MITRE ATT&CK', c['att'], 'control'),
                    ('NIST SP 800-53 / vendor', c.get('ref') or fam[fk]['ref'], 'family'),
                    ('OWASP ASVS 4.0.3', c.get('asvs', 'N/A'), 'control'),
                    ('OWASP Top 10:2021', c.get('owasp', 'N/A'), 'control'),
                    ('NIST SP 800-207 Zero Trust', c['zt'], 'control')]
            for fw, mapping, lvl in rows:
                if str(mapping) not in ('N/A', '', None):
                    w.writerow([c['id'], c['name'], fw, mapping, lvl])

    # ---------------------------------------------------------------- JSON catalogue
    payload = OrderedDict()
    payload['$schema'] = './control-schema.json'
    payload['catalogue_id'] = 'SAOS'
    payload['version'] = '0.1'
    payload['source_files'] = files
    payload['counts'] = {'controls': len(controls), 'families': len(fam), 'domains': len(meta['domains']),
                         'evidence_items': sum(len(c['_evs']) for c in controls)}
    payload['reference_data'] = {'mitre_tactics': TACT, 'zero_trust_pillars': ZT, 'test_methods': TESTS}
    payload['domains'] = [OrderedDict([('num', d['num']), ('code', d['code']), ('name', d['name']),
                                      ('target', d['target']), ('batch', d['batch']), ('scope', d['scope'])])
                          for d in meta['domains']]
    payload['families'] = [OrderedDict([('key', k), ('name', v['name']), ('references', v['ref']),
                                       ('iso_clause', v['iso_clause']), ('iso_iec_27034_category', v['app'])])
                           for k, v in fam.items()]
    payload['controls'] = []
    for c in controls:
        fk = f'{c["_dom_code"]}-{c["_fam_code"]}'
        payload['controls'].append(OrderedDict([
            ('id', c['id']), ('domain_code', c['_dom_code']), ('domain', c['_domain']),
            ('family_code', c['_fam_code']), ('family', c['_family']), ('name', c['name']),
            ('platform', c['plat']), ('control_type', c['type']),
            ('objective', c['obj']), ('business_justification', c['biz']), ('threat', c['thr']),
            ('assessment_question', c['q']),
            ('evidence_required', c['_evs']), ('validation_procedure', c['proc']),
            ('test_methods', c['_tests']),
            ('automation', OrderedDict([('potential', c['auto']), ('method', c['autom'])])),
            ('risk', OrderedDict([('default_likelihood', c['L']), ('default_impact', c['I']),
                                  ('inherent_score', c['_inherent'])])),
            ('criticality_weight', c['w']),
            ('maturity_anchors', OrderedDict([('l1_initial', c['m1']), ('l3_defined', c['m3']), ('l5_optimized', c['m5'])])),
            ('remediation_guidance', c['rem']),
            ('references', c.get('ref') or fam[fk]['ref']),
            ('mapping', OrderedDict([('iso_27001_2022_annex_a', c['iso']), ('nist_csf_2_0', c['csf']),
                                     ('cis_controls_v8_1', c['cis']), ('soc2_2017_tsc', c['soc']),
                                     ('mitre_attack', c['att']), ('zero_trust', c['zt']),
                                     ('owasp_asvs_4_0_3', c.get('asvs', 'N/A')),
                                     ('owasp_top_10_2021', c.get('owasp', 'N/A')),
                                     ('iso_27001_management_system', fam[fk]['iso_clause'])])),
            ('checklist_origin', c['orig']), ('source_file', c['_src'])]))
    with open(os.path.join(out, 'control-catalogue.json'), 'w', encoding='utf8') as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write('\n')

    print(f'controls   : {len(controls)}')
    print(f'families   : {len(fam)}')
    print(f'domains    : {len(meta["domains"])}')
    print(f'evidence   : {payload["counts"]["evidence_items"]}')
    print(f'written to : {out}')


if __name__ == '__main__':
    main()