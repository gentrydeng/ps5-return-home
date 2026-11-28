#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Package verified bytes and the exact corresponding SDK sources."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

from verify import ROOT, source_files, verify_elf

STAMP = (2026, 1, 1, 0, 0, 0)
BINARY_DOCS = {
    "LICENSE-BSD-2-Clause.txt": "LICENSE",
    "README.md": "docs/USAGE.md",
    "README.zh-CN.md": "docs/USAGE.zh-CN.md",
    "THIRD_PARTY.md": "THIRD_PARTY.md",
    "THIRD_PARTY.zh-CN.md": "THIRD_PARTY.zh-CN.md",
    "licenses/GPL-3.0.txt": "licenses/GPL-3.0.txt",
}


def write_zip(target, entries):
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, data in sorted(entries):
            info = zipfile.ZipInfo(name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            output.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def verify_zip(path, files, locked_member, locked):
    """Check whitelist, file type, CRC, and contents without extracting."""
    expected_names = set(files) | {locked_member}
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        for member in members:
            name = member.filename
            member_path = PurePosixPath(name)
            if (not name or member_path.as_posix() != name or member_path.is_absolute()
                    or ".." in member_path.parts or "\\" in name or ":" in name
                    or "\0" in member.orig_filename):
                raise ValueError(f"{path.name}: unsafe ZIP member path {name!r}")
        names = {member.filename for member in members}
        if len(members) != len(names) or names != expected_names:
            raise ValueError(f"{path.name}: invalid member list (missing {sorted(expected_names - names)}, "
                             f"extra {sorted(names - expected_names)} or duplicate members)")
        for member in members:
            name = member.filename
            if (member.orig_filename != name or member.create_system != 3
                    or member.external_attr >> 16 != 0o100644):
                raise ValueError(f"{path.name}: invalid ZIP member {name!r}")
            size = locked["bytes"] if name == locked_member else len(files[name])
            if member.file_size != size:
                raise ValueError(f"{path.name}: wrong size for {name}")
            data = archive.read(member)  # ZipFile also checks the member CRC.
            if name == locked_member:
                matches = len(data) == size and hashlib.sha256(data).hexdigest() == locked["sha256"]
            else:
                matches = data == files[name]
            if not matches:
                raise ValueError(f"{path.name}: wrong contents for {name}")
    print(f"Verified {path.name}: {len(members)} members")


def verify_checksums(binary, source, checksum):
    expected = {binary.name: hashlib.sha256(binary.read_bytes()).hexdigest(),
                source.name: hashlib.sha256(source.read_bytes()).hexdigest()}
    observed = {}
    for line in checksum.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9._-]+)", line)
        if not match or match[2] in observed:
            raise ValueError("Invalid release checksum manifest")
        observed[match[2]] = match[1]
    if observed != expected:
        raise ValueError("Release checksum manifest does not match both ZIPs")
    print(f"Verified {checksum.name}: {len(observed)} assets")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", nargs="?", const=ROOT / "dist", metavar="DIRECTORY", type=Path,
                        help="check existing ZIPs without writing (default directory: dist)")
    args = parser.parse_args()
    version = (ROOT / "VERSION").read_text().strip()
    if version != "0.1.0":
        raise ValueError("Package layout is defined for version 0.1.0")
    lock = json.loads((ROOT / "scripts/toolchain.json").read_text())
    payload = lock["payload"]
    sdk = lock["sdk_source"]
    dist = args.verify_only if args.verify_only is not None else ROOT / "dist"
    binary = dist / f"ps5-return-home-{version}-ps5-x86_64.zip"
    source = dist / f"ps5-return-home-{version}-source.zip"
    checksum = dist / "SHA256SUMS"
    binary_docs = {name: (ROOT / file).read_bytes() for name, file in BINARY_DOCS.items()}
    prefix = f"ps5-return-home-{version}/"
    project_sources = {prefix + path.relative_to(ROOT).as_posix(): path.read_bytes() for path in source_files()}
    sdk_member = prefix + "third_party/" + sdk["file"]

    if args.verify_only is not None:
        verify_zip(binary, binary_docs, payload["file"], payload)
        verify_zip(source, project_sources, sdk_member, sdk)
        verify_checksums(binary, source, checksum)
        return

    if any(path.exists() or path.is_symlink() for path in [binary, source, checksum]):
        raise FileExistsError("Inspect existing dist outputs; no release file is overwritten")
    elf = ROOT / "build" / payload["file"]
    verify_elf(elf)
    raw = (ROOT / ".cache/downloads" / sdk["file"]).read_bytes()
    if len(raw) != sdk["bytes"] or hashlib.sha256(raw).hexdigest() != sdk["sha256"]:
        raise ValueError("SDK corresponding-source archive does not match lock")
    dist.mkdir(exist_ok=True)
    write_zip(binary, [*binary_docs.items(), (payload["file"], elf.read_bytes())])
    write_zip(source, [*project_sources.items(), (sdk_member, raw)])
    with checksum.open("x", encoding="utf-8", newline="\n") as manifest:
        for path in [binary, source]:
            manifest.write(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n")
    print(f"Prepared {binary.name}, {source.name}, SHA256SUMS")


if __name__ == "__main__":
    main()
