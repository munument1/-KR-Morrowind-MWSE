#!/usr/bin/env python3
"""Port only OpenMW KR1 dialogue-link fixes onto the Classic CP949 RC6 payload.

The Classic ESP is the base and stays authoritative for compiled scripts and
Classic-only record fixes.  An INFO response is changed only when the current
CP949 text is byte-for-text identical to the KR1 text after removing explicit
@topic# markup.  General translation edits are therefore deliberately excluded.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import struct
import unicodedata
import zipfile
from pathlib import Path

OPENMW_ESP_SHA256 = "e19f85d66d980ed5716682c711b0beaa1c7fe9decbdc06f2f95f0cb9a07ee78d"
OPENMW_TOP_SHA256 = "b87c1501a1402f34b77681631eed5f743815d34d9a50652a2fb856a52094e853"
OPENMW_MRK_SHA256 = "733f8398e9f2db2b8f1608a3f4a02e2d5f717b0d933f05432790b5652eccc91f"
CP949_RC6_ESP_SHA256 = "d876e2fd60b84380a3bca4750033ac6a36f776e173f5f2476433c66e519a9762"
EXPECTED_DIALS = 4955
EXPECTED_INFOS = 31716
EXPECTED_SCRIPTS = 236
EXPECTED_MARKER_ONLY = 7692
EXPECTED_CONTENT_CHANGES_SKIPPED = 177
EXPECTED_TOP_ROWS = 5843
EXPECTED_MRK_ROWS = 376

PUNCT_FALLBACK = {
    "\u2018": "'", "\u2019": "'", "\u201a": ",", "\u201c": '"', "\u201d": '"',
    "\u201e": '"', "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a0": " ",
}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def decode_openmw(data: bytes) -> str:
    data = data.rstrip(b"\x00")
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("latin1", errors="replace")


def decode_cp949(data: bytes) -> str:
    data = data.rstrip(b"\x00")
    for enc in ("cp949", "utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("latin1", errors="replace")


def encode_cp949(text: str, fallback_counter: collections.Counter | None = None) -> bytes:
    out = bytearray()
    for ch in text:
        try:
            out += ch.encode("cp949")
        except UnicodeEncodeError:
            repl = PUNCT_FALLBACK.get(ch)
            if repl is None:
                decomp = unicodedata.normalize("NFKD", ch)
                repl = "".join(c for c in decomp if ord(c) < 128 and not unicodedata.combining(c)) or "?"
            out += repl.encode("ascii")
            if fallback_counter is not None:
                fallback_counter[(ch, repl)] += 1
    return bytes(out)


def strip_markers(text: str) -> str:
    return re.sub(r"@([^#]*)#", r"\1", text)


def marker_phrases(text: str) -> list[str]:
    return re.findall(r"@([^#]+)#", text)


def iter_records(blob: bytes):
    pos = 0
    rec_index = 0
    while pos < len(blob):
        if pos + 16 > len(blob):
            raise ValueError(f"record header overrun at {pos}")
        rtype = blob[pos:pos+4]
        size = struct.unpack_from("<I", blob, pos + 4)[0]
        rest = blob[pos+8:pos+16]
        end = pos + 16 + size
        if end > len(blob):
            raise ValueError(f"record overrun at {pos}")
        q = pos + 16
        subs = []
        while q < end:
            if q + 8 > end:
                raise ValueError(f"subrecord header overrun at {q}")
            stype = blob[q:q+4]
            ssize = struct.unpack_from("<I", blob, q + 4)[0]
            p0, p1 = q + 8, q + 8 + ssize
            if p1 > end:
                raise ValueError(f"subrecord overrun at {q}")
            subs.append((stype, blob[p0:p1]))
            q = p1
        yield rec_index, rtype, rest, subs, blob[pos:end]
        pos = end
        rec_index += 1


def build_record(rtype: bytes, rest: bytes, subs) -> bytes:
    body = bytearray()
    for stype, payload in subs:
        body += stype + struct.pack("<I", len(payload)) + payload
    return rtype + struct.pack("<I", len(body)) + rest + body


def get_sub(subs, key: bytes):
    for stype, payload in subs:
        if stype == key:
            return payload
    return None


def replace_first_sub(subs, key: bytes, new_payload: bytes):
    out = []
    done = False
    for stype, payload in subs:
        if stype == key and not done:
            payload = new_payload
            done = True
        out.append((stype, payload))
    if not done:
        raise KeyError(f"missing subrecord {key!r}")
    return out


def find_file(root: Path, suffix: str, prefer: str | None = None) -> Path | None:
    matches = [p for p in root.rglob(f"*{suffix}") if p.is_file()]
    if prefer:
        preferred = [p for p in matches if prefer.lower() in p.name.lower()]
        if preferred:
            matches = preferred
    if not matches:
        return None
    matches.sort(key=lambda p: (len(str(p)), str(p)))
    return matches[0]


def parse_dialogue(blob: bytes, decoder):
    dials = []
    infos = []
    scripts = []
    current_dial = -1
    info_ord = collections.defaultdict(int)
    for rec_index, rtype, rest, subs, raw in iter_records(blob):
        if rtype == b"DIAL":
            current_dial += 1
            name = decoder(get_sub(subs, b"NAME") or b"")
            data = get_sub(subs, b"DATA") or b""
            dials.append({"index": current_dial, "name": name, "data": data.hex(), "record_index": rec_index})
        elif rtype == b"INFO":
            ordinal = info_ord[current_dial]
            info_ord[current_dial] += 1
            infos.append({
                "dial_index": current_dial,
                "ordinal": ordinal,
                "record_index": rec_index,
                "inam": decoder(get_sub(subs, b"INAM") or b""),
                "response": decoder(get_sub(subs, b"NAME") or b""),
            })
        elif rtype == b"SCPT":
            scripts.append(raw)
    return dials, infos, scripts


def info_key(info):
    return (info["dial_index"], info["inam"], info["ordinal"])


def read_sidecar(path: Path) -> tuple[bytes, list[tuple[str, str]]]:
    raw = path.read_bytes()
    text = decode_openmw(raw)
    rows = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line:
            continue
        if "\t" not in line:
            raise ValueError(f"{path.name}:{line_no}: missing tab")
        key, value = line.split("\t", 1)
        rows.append((key, value))
    return raw, rows


def write_sidecar_cp949(path: Path, rows, fallback_counter):
    encoded = []
    for key, value in rows:
        encoded.append(encode_cp949(key, fallback_counter) + b"\t" + encode_cp949(value, fallback_counter))
    path.write_bytes(b"\r\n".join(encoded) + b"\r\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--openmw-root", required=True, type=Path)
    ap.add_argument("--cp949-root", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()

    openmw_esp = find_file(args.openmw_root, ".esp", "ReTranslation") or find_file(args.openmw_root, ".esp")
    openmw_top = find_file(args.openmw_root, ".top", "ReTranslation") or find_file(args.openmw_root, ".top")
    openmw_mrk = find_file(args.openmw_root, ".mrk", "ReTranslation") or find_file(args.openmw_root, ".mrk")
    cp949_esp = find_file(args.cp949_root, ".esp", "ReTranslation") or find_file(args.cp949_root, ".esp")
    if not all((openmw_esp, openmw_top, openmw_mrk, cp949_esp)):
        raise SystemExit("required ESP/TOP/MRK input not found")

    checks = {
        "openmw_esp_hash": digest_file(openmw_esp) == OPENMW_ESP_SHA256,
        "openmw_top_hash": digest_file(openmw_top) == OPENMW_TOP_SHA256,
        "openmw_mrk_hash": digest_file(openmw_mrk) == OPENMW_MRK_SHA256,
        "cp949_rc6_esp_hash": digest_file(cp949_esp) == CP949_RC6_ESP_SHA256,
    }

    omw_blob = openmw_esp.read_bytes()
    cp_blob = cp949_esp.read_bytes()
    omw_dials, omw_infos, _ = parse_dialogue(omw_blob, decode_openmw)
    cp_dials, cp_infos, cp_scripts = parse_dialogue(cp_blob, decode_cp949)
    checks.update({
        "dial_count": len(omw_dials) == len(cp_dials) == EXPECTED_DIALS,
        "info_count": len(omw_infos) == len(cp_infos) == EXPECTED_INFOS,
        "script_count": len(cp_scripts) == EXPECTED_SCRIPTS,
        "dial_names_identical": [(d["name"], d["data"]) for d in omw_dials] == [(d["name"], d["data"]) for d in cp_dials],
    })

    omw_info = {info_key(i): i for i in omw_infos}
    cp_info = {info_key(i): i for i in cp_infos}
    checks["info_keys_identical"] = set(omw_info) == set(cp_info)

    marker_candidates = {}
    content_changes = []
    for key in sorted(set(omw_info) & set(cp_info)):
        a, b = omw_info[key], cp_info[key]
        if a["response"] == b["response"]:
            continue
        markers = marker_phrases(a["response"])
        if markers and strip_markers(a["response"]) == b["response"]:
            marker_candidates[b["record_index"]] = {"key": key, "text": a["response"], "markers": markers}
        else:
            content_changes.append({"key": key, "openmw": a["response"], "cp949": b["response"]})

    checks["marker_only_count"] = len(marker_candidates) == EXPECTED_MARKER_ONLY
    checks["content_changes_skipped"] = len(content_changes) == EXPECTED_CONTENT_CHANGES_SKIPPED

    fallback_counter = collections.Counter()
    out_blob = bytearray()
    patched = []
    for rec_index, rtype, rest, subs, raw in iter_records(cp_blob):
        candidate = marker_candidates.get(rec_index)
        if not candidate:
            out_blob += raw
            continue
        old = get_sub(subs, b"NAME")
        if old is None:
            raise RuntimeError(f"INFO record {rec_index}: missing NAME")
        terminated = old.endswith(b"\x00")
        encoded = encode_cp949(candidate["text"], fallback_counter) + (b"\x00" if terminated else b"")
        ns = replace_first_sub(subs, b"NAME", encoded)
        out_blob += build_record(rtype, rest, ns)
        patched.append({"record_index": rec_index, "key": candidate["key"], "markers": candidate["markers"]})

    out_dir = args.output_dir.resolve()
    dist = out_dir / "MO2"
    dist.mkdir(parents=True, exist_ok=True)
    out_esp = dist / "Morrowind_Korean_ReTranslation.esp"
    out_top = dist / "Morrowind_Korean_ReTranslation.top"
    out_mrk = dist / "Morrowind_Korean_ReTranslation.mrk"
    out_readme = dist / "README.txt"
    out_validation = out_dir / "Morrowind_Korean_ReTranslation_KR1_TopicFix_Classic_CP949_validation.json"
    out_zip = out_dir / "Morrowind_Korean_ReTranslation_KR1_TopicFix_Classic_CP949.zip"
    out_esp.write_bytes(bytes(out_blob))

    top_raw, top_rows = read_sidecar(openmw_top)
    mrk_raw, mrk_rows = read_sidecar(openmw_mrk)
    checks["top_rows"] = len(top_rows) == EXPECTED_TOP_ROWS
    checks["mrk_rows"] = len(mrk_rows) == EXPECTED_MRK_ROWS
    write_sidecar_cp949(out_top, top_rows, fallback_counter)
    write_sidecar_cp949(out_mrk, mrk_rows, fallback_counter)

    out_dials, out_infos, out_scripts = parse_dialogue(out_esp.read_bytes(), decode_cp949)
    out_info = {info_key(i): i for i in out_infos}
    checks["output_dial_count"] = len(out_dials) == EXPECTED_DIALS
    checks["output_info_count"] = len(out_infos) == EXPECTED_INFOS
    checks["output_script_count"] = len(out_scripts) == EXPECTED_SCRIPTS
    checks["compiled_scripts_byte_identical"] = cp_scripts == out_scripts
    checks["classic_dials_byte_semantics_preserved"] = [(d["name"], d["data"]) for d in cp_dials] == [(d["name"], d["data"]) for d in out_dials]

    changed_keys = []
    unexpected = []
    marker_occurrences = 0
    marker_phrases_counter = collections.Counter()
    for key, before in cp_info.items():
        after = out_info[key]
        if before["response"] != after["response"]:
            changed_keys.append(key)
            if after["record_index"] not in marker_candidates:
                unexpected.append(key)
        phrases = marker_phrases(after["response"])
        marker_occurrences += len(phrases)
        marker_phrases_counter.update(phrases)
    checks["only_expected_info_names_changed"] = len(changed_keys) == EXPECTED_MARKER_ONLY and not unexpected

    top_map = dict(top_rows)
    dial_names = {d["name"] for d in out_dials}
    unresolved = []
    resolution = collections.Counter()
    for phrase in marker_phrases_counter:
        if phrase in top_map:
            resolution["top"] += 1
        elif phrase in dial_names:
            resolution["direct_dial"] += 1
        else:
            unresolved.append(phrase)
    checks["all_output_markers_resolve"] = not unresolved

    # Classic RC6 deliberately removes this bad Voice condition; it must remain removed.
    current_dial_type = None
    wilderness = 0
    for _, rtype, _, subs, _ in iter_records(out_esp.read_bytes()):
        if rtype == b"DIAL":
            d = get_sub(subs, b"DATA")
            current_dial_type = d[0] if d else None
        elif rtype == b"INFO" and current_dial_type == 1:
            for stype, payload in subs:
                if stype == b"ANAM" and payload.rstrip(b"\x00") == b"Wilderness":
                    wilderness += 1
    checks["classic_voice_wilderness_fix_preserved"] = wilderness == 0

    status = "PASS" if all(checks.values()) else "FAIL"
    validation = {
        "status": status,
        "strategy": "RC6 Classic base + marker-only INFO NAME changes + KR1 TOP/MRK; 177 general translation changes deliberately skipped",
        "inputs": {
            "openmw_esp": str(openmw_esp), "openmw_esp_sha256": digest_file(openmw_esp),
            "openmw_top_sha256": digest_file(openmw_top), "openmw_mrk_sha256": digest_file(openmw_mrk),
            "cp949_rc6_esp": str(cp949_esp), "cp949_rc6_esp_sha256": digest_file(cp949_esp),
        },
        "output": {
            "esp_sha256": digest_file(out_esp), "esp_size": out_esp.stat().st_size,
            "top_sha256": digest_file(out_top), "top_rows": len(top_rows),
            "mrk_sha256": digest_file(out_mrk), "mrk_rows": len(mrk_rows),
            "marker_only_info_changed": len(changed_keys),
            "content_changes_skipped": len(content_changes),
            "marker_occurrences": marker_occurrences,
            "unique_marker_phrases": len(marker_phrases_counter),
            "marker_resolution": dict(resolution),
            "unresolved_markers": unresolved,
        },
        "cp949_fallbacks": {f"{a!r}->{b!r}": n for (a, b), n in fallback_counter.items()},
        "checks": checks,
        "patched_info_sample": patched[:50],
        "skipped_content_change_sample": content_changes[:20],
    }
    out_validation.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    if status != "PASS":
        raise RuntimeError(json.dumps(validation, ensure_ascii=False, indent=2))

    out_readme.write_text(
        "Morrowind Korean ReTranslation - Classic CP949 KR1 Topic Fix\r\n"
        "=============================================================\r\n\r\n"
        "Base: Classic CP949 RC6\r\n"
        "Reference: OpenMW Korean Support KR1 final translation payload\r\n\r\n"
        "Applied only dialogue-link compatibility changes:\r\n"
        f"- explicit @topic# marker-only INFO responses: {len(changed_keys)}\r\n"
        f"- TOP mappings: {len(top_rows)}\r\n"
        f"- MRK mappings: {len(mrk_rows)}\r\n"
        f"- general translation response changes skipped: {len(content_changes)}\r\n"
        "- Classic RC6 compiled scripts and Classic-only fixes preserved\r\n\r\n"
        "Priority runtime regression tests:\r\n"
        "- Hasphat Antabolis / favor and information path\r\n"
        "- Ranis Athrys / Mages Guild join and duties\r\n"
        "- Ajira / Galbedir bet quest\r\n"
        "- Tribunal and Bloodmoon dialogue topic links\r\n",
        encoding="cp949",
        errors="replace",
    )

    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(dist.iterdir()):
            if p.is_file():
                zi = zipfile.ZipInfo(p.name, date_time=(1980, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = 0o100644 << 16
                zi.create_system = 3
                zf.writestr(zi, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        zi = zipfile.ZipInfo(out_validation.name, date_time=(1980, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o100644 << 16
        zi.create_system = 3
        zf.writestr(zi, out_validation.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print("ZIP:", out_zip)
    print("ZIP SHA-256:", digest_file(out_zip))


if __name__ == "__main__":
    main()
