#!/usr/bin/env python3
import argparse, hashlib
from pathlib import Path

SUPPORTED = {
    "8fe33fb11b6a682721e7456af78eefd228e8b60dc7c9f4253f89a361f8a4dfc5",
    "c3585b91741689057c18ff86a1c3381d47278cd1d81443d38ed3b179c2fa1cd8",
    # MCP Japanese localization enabled + additional MCP option combination
    # validated from the current Korean project reference executable.
    "a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c",
}
OFFSET = 0x3457C0
PATCH = bytes.fromhex(
    "5589e58b4d080fb70186c480fc81723480fcfd772f80ec813c4172283c5a7614"
    "3c6172203c7a76103c8172183cfe77142c4deb062c41eb022c47503e8b4d0ce9"
    "15000000e987000000"
)
PILOT_SHA256 = "710196b98d1a4efa174aebb5539e14b36cff20d008dc1f0c0610ce099d06cf72"
REFERENCE_MCP_JP_INPUT_SHA256 = "a87ee7f9239023469d4c031e6dab87648a316ab8c1354e96c2478aca3376167c"
REFERENCE_MCP_JP_OUTPUT_SHA256 = "bff9c8381d59657e5dfbfc66058745996327b20f4516f63e54ce9c7f726b45fc"

def digest(b): return hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser(description="Patch a supported MCP Morrowind.exe for CP949 Korean text rendering.")
    p.add_argument("input",type=Path)
    p.add_argument("output",nargs="?",type=Path,default=Path("Morrowind.MCP-Korean.exe"))
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    data=bytearray(a.input.read_bytes())
    h=digest(data)
    if h not in SUPPORTED:
        raise SystemExit(f"Unsupported input SHA-256: {h}")
    if a.check:
        print("Supported input:",h)
        return
    data[OFFSET:OFFSET+len(PATCH)] = PATCH
    a.output.write_bytes(data)
    out=digest(data)
    print("Output:",a.output)
    print("SHA-256:",out)
    if h == REFERENCE_MCP_JP_INPUT_SHA256:
        if out != REFERENCE_MCP_JP_OUTPUT_SHA256:
            raise SystemExit("Reference MCP Japanese-localization output hash mismatch")
        print("Validated MCP Japanese-localization CP949 output")
    elif out != PILOT_SHA256:
        print("NOTE: output differs from the originally validated pilot hash.")

if __name__=="__main__":
    main()
