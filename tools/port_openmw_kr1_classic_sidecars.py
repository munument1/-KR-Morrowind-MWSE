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
    ap = argparse.ArgumentParser(
        description='Port OpenMW KR1 .cel and Classic Morrowind.ini display localization to CP949.'
    )
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

    # OpenMW fallback keys mirror values historically stored in Morrowind.ini.
    # Only display strings are ported. Technical keys (fonts, blood model/texture
    # paths, questionnaire Sound= lines, etc.) remain untouched in the user's INI.
    cfg = find_one(root, 'openmw.cfg')
    cfg_text = cfg.read_text(encoding='utf-8-sig')

    questions: dict[tuple[int, str], str] = {}
    qrx = re.compile(r'^fallback=Question_(\d+)_(Question|AnswerOne|AnswerTwo|AnswerThree),(.*)$')

    level_up: dict[str, str] = {}
    lrx = re.compile(r'^fallback=Level_Up_(Level(?:[2-9]|1\d|20)|Default),(.*)$')

    blood: dict[str, str] = {}
    brx = re.compile(r'^fallback=Blood_Texture_Name_([0-2]),(.*)$')

    for raw in cfg_text.splitlines():
        m = qrx.match(raw)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 10:
                questions[(n, m.group(2))] = m.group(3)
            continue
        m = lrx.match(raw)
        if m:
            level_up[m.group(1)] = m.group(2)
            continue
        m = brx.match(raw)
        if m:
            blood[m.group(1)] = m.group(2)

    expected_questions = {
        (n, k)
        for n in range(1, 11)
        for k in ('Question', 'AnswerOne', 'AnswerTwo', 'AnswerThree')
    }
    missing_questions = sorted(expected_questions - set(questions))
    if missing_questions or len(questions) != 40:
        raise SystemExit(
            f'bad chargen question set: count={len(questions)} missing={missing_questions}'
        )

    expected_levels = {f'Level{n}' for n in range(2, 21)} | {'Default'}
    missing_levels = sorted(expected_levels - set(level_up))
    extra_levels = sorted(set(level_up) - expected_levels)
    if missing_levels or extra_levels or len(level_up) != 20:
        raise SystemExit(
            f'bad level-up set: count={len(level_up)} missing={missing_levels} extra={extra_levels}'
        )

    expected_blood = {'0', '1', '2'}
    missing_blood = sorted(expected_blood - set(blood))
    extra_blood = sorted(set(blood) - expected_blood)
    if missing_blood or extra_blood or len(blood) != 3:
        raise SystemExit(
            f'bad blood-name set: count={len(blood)} missing={missing_blood} extra={extra_blood}'
        )

    # Overlay format intentionally contains only localized display keys. The BAT
    # merges each key into the existing section rather than replacing sections.
    ini_lines: list[str] = []

    ini_lines.append('[Level Up]')
    for n in range(2, 21):
        key = f'Level{n}'
        ini_lines.append(f'{key}={level_up[key]}')
    ini_lines.append(f'Default={level_up["Default"]}')
    ini_lines.append('')

    ini_lines.append('[Blood]')
    for n in range(3):
        ini_lines.append(f'Texture Name {n}={blood[str(n)]}')
    ini_lines.append('')

    for n in range(1, 11):
        ini_lines.append(f'[Question {n}]')
        ini_lines.append(f'Question={questions[(n, "Question")]}')
        ini_lines.append(f'AnswerOne={questions[(n, "AnswerOne")]}')
        ini_lines.append(f'AnswerTwo={questions[(n, "AnswerTwo")]}')
        ini_lines.append(f'AnswerThree={questions[(n, "AnswerThree")]}')
        ini_lines.append('')

    ini_out = out / 'Morrowind_Korean_INI.ini'
    ini_out.write_bytes(encode_cp949('\r\n'.join(ini_lines), 'Classic INI overlay'))

    ini_entry_count = len(questions) + len(level_up) + len(blood)
    if ini_entry_count != 63:
        raise SystemExit(f'unexpected INI display entry count: {ini_entry_count}')

    manifest = {
        'status': 'PASS',
        'source_cel': str(src_cel),
        'source_cfg': str(cfg),
        'cel_rows': len(cel_rows),
        'question_entries': len(questions),
        'level_up_entries': len(level_up),
        'blood_name_entries': len(blood),
        'ini_display_entries': ini_entry_count,
        'cel_sha256': sha256(cel_out),
        'ini_overlay_sha256': sha256(ini_out),
    }
    manifest_out = out / 'classic_sidecars_validation.json'
    manifest_out.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
