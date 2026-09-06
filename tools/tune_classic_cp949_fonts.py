#!/usr/bin/env python3
"""Tune the existing Classic CP949 bitmap fonts for larger Korean glyphs.

This tool does not need the source TTF.  It works on the already-built Classic
FNT/TEX pair used by RC6/RC7:

* keeps the single-byte/English atlas untouched;
* keeps all CP949 cell UVs and the 8x11 storage grid unchanged;
* enlarges the visible pixels inside each CP949 cell with nearest-neighbour
  resampling so strokes stay crisp;
* adjusts only glyph slot 0xFF geometry, which the CP949 code patch uses as
  the DBCS template, so Korean can be rendered slightly larger on screen.

The tuning is intentionally conservative for the regular UI fonts and a bit
stronger for century_gothic_big.  It is reversible by restoring the original
RC6 font files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

ATLAS_W = ATLAS_H = 2048
GRID_Y = 512
CELL_W, CELL_H = 8, 11
LEADS = tuple(range(0x81, 0xFE))
TRAILS = tuple(range(0x41, 0x5B)) + tuple(range(0x61, 0x7B)) + tuple(range(0x81, 0xFF))
FNT_HEADER = 12 + 284
GLYPH_SIZE = 14 * 4
EXPECTED_FNT_SIZE = FNT_HEADER + 256 * GLYPH_SIZE

# tex-scale, rendered width, rendered height, DBCS advance
# The atlas scale fattens/fills the 8x11 source cell without changing UV math.
# The geometry scale then makes Korean match the surrounding UI more closely.
PROFILES = {
    "Magic_Cards_Regular": (1.10, 9.0, 12.0, 9.0),
    "century_gothic_font_regular": (1.10, 9.0, 12.0, 9.0),
    "century_gothic_big": (1.18, 10.0, 14.0, 10.0),
    "daedric_font": (1.10, 9.0, 12.0, 9.0),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_ci(directory: Path, name: str) -> Path | None:
    exact = directory / name
    if exact.is_file():
        return exact
    folded = name.casefold()
    for p in directory.iterdir():
        if p.is_file() and p.name.casefold() == folded:
            return p
    return None


def internal_tex_name(fnt: bytes) -> str:
    if len(fnt) != EXPECTED_FNT_SIZE:
        raise ValueError(f"unexpected FNT size: {len(fnt)}")
    _, a, b = struct.unpack_from("<fii", fnt, 0)
    if (a, b) != (1, 1):
        raise ValueError(f"unexpected FNT markers: {a}, {b}")
    return fnt[12:296].split(b"\0", 1)[0].decode("ascii")


def read_tex(path: Path) -> tuple[int, int, bytearray]:
    raw = path.read_bytes()
    if len(raw) < 8:
        raise ValueError(f"TEX too small: {path}")
    w, h = struct.unpack_from("<ii", raw, 0)
    if (w, h) != (ATLAS_W, ATLAS_H):
        raise ValueError(f"expected 2048x2048 CP949 TEX, got {w}x{h}: {path.name}")
    if len(raw) != 8 + w * h * 4:
        raise ValueError(f"bad TEX size: {path}")
    return w, h, bytearray(raw[8:])


def pixel_offset(x: int, y: int) -> int:
    return (y * ATLAS_W + x) * 4


def get_cell(pixels: bytearray, x0: int, y0: int) -> list[list[tuple[int, int, int, int]]]:
    cell: list[list[tuple[int, int, int, int]]] = []
    for y in range(CELL_H):
        row = []
        for x in range(CELL_W):
            off = pixel_offset(x0 + x, y0 + y)
            row.append(tuple(pixels[off:off + 4]))
        cell.append(row)
    return cell


def set_cell(pixels: bytearray, x0: int, y0: int, cell: list[list[tuple[int, int, int, int]]]) -> None:
    for y in range(CELL_H):
        for x in range(CELL_W):
            off = pixel_offset(x0 + x, y0 + y)
            pixels[off:off + 4] = bytes(cell[y][x])


def alpha_bbox(cell: list[list[tuple[int, int, int, int]]]) -> tuple[int, int, int, int] | None:
    xs: list[int] = []
    ys: list[int] = []
    for y, row in enumerate(cell):
        for x, px in enumerate(row):
            if px[3] != 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def nearest_scale(src: list[list[tuple[int, int, int, int]]], nw: int, nh: int) -> list[list[tuple[int, int, int, int]]]:
    sh = len(src)
    sw = len(src[0])
    out: list[list[tuple[int, int, int, int]]] = []
    for y in range(nh):
        sy = min(sh - 1, int((y + 0.5) * sh / nh))
        row = []
        for x in range(nw):
            sx = min(sw - 1, int((x + 0.5) * sw / nw))
            row.append(src[sy][sx])
        out.append(row)
    return out


def tune_cell(cell: list[list[tuple[int, int, int, int]]], scale: float) -> tuple[list[list[tuple[int, int, int, int]]], bool]:
    bbox = alpha_bbox(cell)
    if bbox is None:
        return cell, False
    x0, y0, x1, y1 = bbox
    bw, bh = x1 - x0, y1 - y0
    # Grow only when at least one pixel can actually be gained.  Never crop.
    nw = min(CELL_W, max(bw, int(math.ceil(bw * scale))))
    nh = min(CELL_H, max(bh, int(math.ceil(bh * scale))))
    if nw == bw and nh == bh:
        return cell, False

    crop = [row[x0:x1] for row in cell[y0:y1]]
    grown = nearest_scale(crop, nw, nh)
    out = [[(0, 0, 0, 0) for _ in range(CELL_W)] for _ in range(CELL_H)]

    # Preserve the original baseline tendency: center horizontally, bottom-align
    # within the same 8x11 DBCS storage cell.
    dx = max(0, (CELL_W - nw) // 2)
    dy = max(0, CELL_H - nh)
    for y in range(nh):
        for x in range(nw):
            out[dy + y][dx + x] = grown[y][x]
    return out, True


def tune_fnt(path: Path, width: float, height: float, advance: float) -> dict:
    raw = bytearray(path.read_bytes())
    if len(raw) != EXPECTED_FNT_SIZE:
        raise ValueError(f"unexpected FNT size: {path.name}: {len(raw)}")
    off = FNT_HEADER + 0xFF * GLYPH_SIZE
    before = list(struct.unpack_from("<14f", raw, off))
    after = before.copy()
    # indices 1..8 are UVs and must remain exactly unchanged.
    after[9] = float(width)
    after[10] = float(height)
    after[13] = float(advance)
    struct.pack_into("<14f", raw, off, *after)
    path.write_bytes(raw)
    return {
        "before": {"width": before[9], "height": before[10], "advance": before[13]},
        "after": {"width": after[9], "height": after[10], "advance": after[13]},
        "uv_unchanged": before[1:9] == after[1:9],
    }


def tune_tex(path: Path, scale: float) -> dict:
    w, h, pixels = read_tex(path)
    before_hash = sha256(path)
    changed = 0
    nonempty = 0
    for row, _lead in enumerate(LEADS):
        y0 = GRID_Y + row * CELL_H
        if y0 + CELL_H > h:
            raise ValueError("CP949 grid exceeds atlas height")
        for col, _trail in enumerate(TRAILS):
            x0 = col * CELL_W
            cell = get_cell(pixels, x0, y0)
            if alpha_bbox(cell) is not None:
                nonempty += 1
            tuned, did_change = tune_cell(cell, scale)
            if did_change:
                set_cell(pixels, x0, y0, tuned)
                changed += 1
    path.write_bytes(struct.pack("<ii", w, h) + bytes(pixels))
    return {
        "scale": scale,
        "nonempty_cells": nonempty,
        "changed_cells": changed,
        "before_sha256": before_hash,
        "after_sha256": sha256(path),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Enlarge Korean glyphs in existing Classic CP949 FNT/TEX files.")
    ap.add_argument("fonts_dir", type=Path, help="Directory containing the eight Classic CP949 FNT/TEX files")
    ap.add_argument("--manifest", type=Path, help="Optional JSON validation manifest path")
    args = ap.parse_args()

    root = args.fonts_dir.resolve()
    if not root.is_dir():
        raise SystemExit(f"font directory not found: {root}")

    manifest = {"status": "PASS", "cell": [CELL_W, CELL_H], "profiles": {}, "files": {}}
    for stem, (tex_scale, width, height, advance) in PROFILES.items():
        fnt = find_ci(root, stem + ".fnt")
        if fnt is None:
            raise SystemExit(f"missing FNT: {stem}.fnt")
        tex_name = internal_tex_name(fnt.read_bytes()) + ".tex"
        tex = find_ci(root, tex_name)
        if tex is None:
            raise SystemExit(f"missing TEX for {stem}: {tex_name}")

        fnt_before = sha256(fnt)
        fnt_info = tune_fnt(fnt, width, height, advance)
        tex_info = tune_tex(tex, tex_scale)
        if not fnt_info["uv_unchanged"]:
            raise SystemExit(f"UV changed unexpectedly: {fnt.name}")
        if tex_info["changed_cells"] < 1000:
            raise SystemExit(f"too few CP949 cells changed in {tex.name}: {tex_info['changed_cells']}")

        manifest["profiles"][stem] = {
            "texture_scale": tex_scale,
            "render_width": width,
            "render_height": height,
            "advance": advance,
        }
        manifest["files"][fnt.name] = {
            "before_sha256": fnt_before,
            "after_sha256": sha256(fnt),
            **fnt_info,
        }
        manifest["files"][tex.name] = tex_info

    out = args.manifest or (root / "classic_cp949_font_tuning.json")
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("PASS Classic CP949 Korean font tuning")
    for stem, p in manifest["profiles"].items():
        print(f"{stem}: texture x{p['texture_scale']:.2f}, geometry {p['render_width']}x{p['render_height']}, advance {p['advance']}")
    print(f"Manifest: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
