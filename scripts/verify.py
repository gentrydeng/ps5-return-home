#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Validate the ELF against the build lock and check the source packaging manifest."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct

ROOT = Path(__file__).resolve().parents[1]


def source_files():
    names = (ROOT / "scripts/source-files.txt").read_text().splitlines()
    if len(names) != len(set(names)):
        raise ValueError("Duplicate source manifest entry")
    paths = []
    for name in names:
        path = PurePosixPath(name)
        if (not name or path.as_posix() != name or path.is_absolute()
                or ".." in path.parts or "\\" in name or ":" in name or "\0" in name):
            raise ValueError(f"Unsafe source manifest entry: {name!r}")
        file = ROOT / name
        if not file.is_file() or any(p.is_symlink() for p in [file, *file.parents]):
            raise ValueError(f"Missing or linked source file: {name}")
        paths.append(file)
    return paths


def verify_elf(path):
    expected = json.loads((ROOT / "scripts/toolchain.json").read_text())["payload"]
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if len(data) != expected["bytes"] or sha != expected["sha256"]:
        raise ValueError("ELF size or SHA-256 differs from the build lock")
    if data[:7] != b"\x7fELF\x02\x01\x01":
        raise ValueError("Expected little-endian ELF64")
    header = struct.unpack_from("<HHIQQQIHHHHHH", data, 16)
    if header[0] != 3 or header[1] != 62:
        raise ValueError("Expected x86-64 ET_DYN payload")
    entry, phoff, phsize, phcount = header[3], header[4], header[8], header[9]
    if phsize != 56 or phoff + phsize * phcount > len(data):
        raise ValueError("Invalid program header table")
    executable_entry = False
    for index in range(phcount):
        kind, flags, offset, address, _, filesz, memsz, _ = struct.unpack_from("<IIQQQQQQ", data, phoff + index * phsize)
        if offset + filesz > len(data) or (kind == 1 and filesz > memsz):
            raise ValueError("Segment outside ELF file or memory bounds")
        if kind == 1 and flags & 1 and address <= entry < address + memsz:
            executable_entry = True
    if not executable_entry:
        raise ValueError("ELF entry is not inside an executable load segment")
    print(f"ELF: {len(data)} bytes, SHA-256 {sha}")
    return sha


if __name__ == "__main__":
    print(f"Source manifest: {len(source_files())} files")
    verify_elf(ROOT / "build/return-home-uri.elf")
