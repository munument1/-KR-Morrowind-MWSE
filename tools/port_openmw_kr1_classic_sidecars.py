#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def find_one(root: Path, name: str) -> Path:
    matches = [p for p in root.rglob(name) if p.is_file()]
    if not matches:
        raise SystemExit(f'missing {name} under {root}')
    return sorted(matches, key=lambda p: (len(str(p)), str(p)))[0]


def encode_cp949(text: str, label: str) -> bytes:
    try:
        return text.encode('cp949')
    except UnicodeEncodeError as e:
        raise SystemExit(f'CP949 encode failure in {label}: {e}') from e


def main() -> int:
    ap = argparse.ArgumentParser(description='Port OpenMW KR1 .cel and chargen question localization to Classic CP949.')
    ap.add_argument('--openmw-root', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()

    root = args.openmw_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    # Classic localized Morrowind uses a same-basename .cel sidecar for display-only
    # cell/region names, preserving the technical CELL ids in the plugin itself.
    src_cel = find_one(root, 'Morrowind_Korean_ReTranslation.cel')
    cel_text = src_cel.read_text(encoding='utf-8-sig')
    cel_rows = []
    for line_no, raw in enumerate(cel_text.splitlines(), 1):
        if not raw.strip():
            continue
        if '\t' not in raw:
            raise SystemExit(f'bad .cel row {line_no}: no tab')
        source, translated = raw.split('\t', 1)
        if not source or not translated:
            raise SystemExit(f'bad .cel row {line_no}: empty side')
        cel_rows.append((source, translated))
    if len(cel_rows) < 1000:
        raise SystemExit(f'unexpectedly small .cel: {len(cel_rows)} rows')
    cel_out = out / 'Morrowind_Korean_ReTranslation.cel'
    cel_rendered = '\r\n'.join(f'{a}\t{b}' for a, b in cel_rows) + '\r\n'
    cel_out.write_bytes(encode_cp949(cel_rendered, '.cel'))

    # OpenMW KR1 carries the ten character-class questionnaire texts as fallback
    # keys. Classic Morrowind reads the same data from Morrowind.ini [Question N].
    cfg = find_one(root, 'openmw.cfg')
    cfg_text = cfg.read_text(encoding='utf-8-sig')
    wanted = {}
    rx = re.compile(r'^fallback=Question_(\d+)_(Question|AnswerOne|AnswerTwo|AnswerThree),(.*)$')
    for raw in cfg_text.splitlines():
        m = rx.match(raw)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 10:
                wanted[(n, m.group(2))] = m.group(3)
    expected_keys = {(n, k) for n in range(1, 11) for k in ('Question', 'AnswerOne', 'AnswerTwo', 'AnswerThree')}
    missing = sorted(expected_keys - set(wanted))
    extra = sorted(set(wanted) - expected_keys)
    if missing or extra or len(wanted) != 40:
        raise SystemExit(f'bad chargen question set: count={len(wanted)} missing={missing} extra={extra}')

    ini_lines = []
    for n in range(1, 11):
        ini_lines.append(f'[Question {n}]')
        ini_lines.append(f'Question={wanted[(n, "Question")]}')
        ini_lines.append(f'AnswerOne={wanted[(n, "AnswerOne")]}')
        ini_lines.append(f'AnswerTwo={wanted[(n, "AnswerTwo")]}')
        ini_lines.append(f'AnswerThree={wanted[(n, "AnswerThree")]}')
        ini_lines.append(f'Sound=Vo\\Misc\\CharGen QA{n}.wav')
        ini_lines.append('')
    ini_out = out / 'Morrowind_Korean_Questions.ini'
    ini_out.write_bytes(encode_cp949('\r\n'.join(ini_lines), 'chargen ini'))

    manifest = {
        'status': 'PASS',
        'source_cel': str(src_cel),
        'source_cfg': str(cfg),
        'cel_rows': len(cel_rows),
        'question_entries': len(wanted),
        'cel_sha256': sha256(cel_out),
        'questions_ini_sha256': sha256(ini_out),
    }
    manifest_out = out / 'classic_sidecars_validation.json'
    manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
