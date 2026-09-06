#!/usr/bin/env python3
import argparse
import hashlib
from pathlib import Path

SUPPORTED = {
    "8fe33fb11b6a682721e7456af78eefd228e8b60dc7c9f4253f89a361f8a4dfc5",
    "c3585b91741689057c18ff86a1c3381d47278cd1d81443d38ed3b179c2fa1cd8",
    "a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c",
}

OFFSET = 0x3457C0

# MCP Japanese localization compatibility routine, captured from the validated
# project reference executable before applying the CP949 replacement.
SOURCE_PATTERN = bytes.fromhex(
    "558bec8b4d080fb70186c49080fc810f82bb00000080fc9f761780fce00f82ad"
    "00000080fcef0f87a400000080ecc1eb0380ec81d0e43c400f82920000003cfc"
    "770e3ca07206fec42c"
)

PATCH = bytes.fromhex(
    "5589e58b4d080fb70186c480fc81723480fcfd772f80ec813c4172283c5a7614"
    "3c6172203c7a76103c8172183cfe77142c4deb062c41eb022c47503e8b4d0ce9"
    "15000000e987000000"
)

REFERENCE_MCP_JP_INPUT_SHA256 = (
    "a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c"
)
REFERENCE_MCP_JP_OUTPUT_SHA256 = (
    "bff9c8381d59657e5dfbfc66058745996327b20f4516f63e54ce9c7f726b45fc"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pattern_at(data: bytes, pattern: bytes) -> bool:
    return data[OFFSET : OFFSET + len(pattern)] == pattern


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Patch MCP Morrowind.exe for CP949 Korean text rendering. "
            "Unknown whole-file hashes are accepted only when the validated "
            "Japanese-localization code pattern is present at 0x3457C0."
        )
    )
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "output", nargs="?", type=Path, default=Path("Morrowind.MCP-Korean.exe")
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    data = bytearray(args.input.read_bytes())
    needed = OFFSET + max(len(SOURCE_PATTERN), len(PATCH))
    if len(data) < needed:
        raise SystemExit("Morrowind.exe is unexpectedly small")

    input_hash = digest(data)
    already = pattern_at(data, PATCH)
    source_match = pattern_at(data, SOURCE_PATTERN)
    known_hash = input_hash in SUPPORTED

    if args.check:
        if already:
            print("Already CP949-patched:", input_hash)
            return 0
        if source_match:
            print("Japanese-localization code pattern verified:", input_hash)
            if not known_hash:
                print("Whole-file hash is an unpinned MCP option combination; pattern is safe.")
            return 0
        if known_hash:
            print("Supported pinned input:", input_hash)
            return 0
        raise SystemExit(
            "Unsupported input: whole-file SHA-256 is unknown and the validated "
            "Japanese-localization code pattern is absent"
        )

    if already:
        args.output.write_bytes(data)
        print("Input is already CP949-patched")
        print("Output:", args.output)
        print("SHA-256:", digest(data))
        return 0

    if not source_match and not known_hash:
        actual = bytes(data[OFFSET : OFFSET + min(len(SOURCE_PATTERN), 32)]).hex()
        raise SystemExit(
            f"Unsupported input SHA-256: {input_hash}; code bytes at 0x3457C0: {actual}"
        )

    if source_match and not known_hash:
        print("Unpinned MCP option-combination SHA-256:", input_hash)
        print("Japanese-localization code pattern verified; continuing safely.")

    data[OFFSET : OFFSET + len(PATCH)] = PATCH
    if not pattern_at(data, PATCH):
        raise SystemExit("CP949 code-pattern verification failed after write")

    args.output.write_bytes(data)
    output_hash = digest(data)
    print("Output:", args.output)
    print("SHA-256:", output_hash)

    if input_hash == REFERENCE_MCP_JP_INPUT_SHA256:
        if output_hash != REFERENCE_MCP_JP_OUTPUT_SHA256:
            raise SystemExit("Reference MCP Japanese-localization output hash mismatch")
        print("Validated MCP Japanese-localization CP949 output")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
