#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Fetch hash-pinned public build inputs and unpack them locally."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def valid(path, item):
    return (path.is_file() and not path.is_symlink()
            and path.stat().st_size == item["bytes"]
            and digest(path) == item["sha256"])


def obtain(item, cache, offline=False):
    target = cache / item["file"]
    if target.exists():
        if not valid(target, item):
            raise ValueError(f"Cached input does not match lock: {target.name}")
        return target
    if offline:
        raise FileNotFoundError(f"Offline cache is missing {target.name}")
    partial = target.with_name(target.name + ".partial")
    if partial.exists():
        raise FileExistsError(f"Inspect existing partial input: {partial.name}")
    failures = []
    for url in item["urls"]:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "ps5-return-home-build/0.1.0"})
            with urllib.request.urlopen(request, timeout=30) as response, partial.open("xb") as output:
                remaining = item["bytes"] + 1
                while remaining:
                    data = response.read(min(1024 * 1024, remaining))
                    if not data:
                        break
                    output.write(data)
                    remaining -= len(data)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            failures.append(f"{url}: {type(error).__name__}")
            # Only this invocation's incomplete transfer is removed for fallback.
            partial.unlink(missing_ok=True)
            continue
        if not valid(partial, item):
            raise ValueError(f"Downloaded input mismatch; inspect {partial.name}")
        partial.rename(target)
        return target
    raise RuntimeError("No download source succeeded: " + "; ".join(failures))


def unpack_sdk(archive, destination):
    with zipfile.ZipFile(archive) as source:
        for item in source.infolist():
            path = PurePosixPath(item.filename)
            mode = item.external_attr >> 16
            if (path.is_absolute() or ".." in path.parts or "\\" in item.filename
                    or (mode & 0o170000) == 0o120000
                    or not path.parts or path.parts[0] != "ps5-payload-sdk"):
                raise ValueError(f"Unexpected SDK archive member: {item.filename}")
        source.extractall(destination)
    for path in (destination / "ps5-payload-sdk" / "bin").iterdir():
        if path.is_file():
            path.chmod(0o755)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Use only verified .cache/downloads inputs")
    args = parser.parse_args()
    if sys.platform != "linux" or os.uname().machine != "x86_64":
        parser.error("Use x86-64 Linux, including x86-64 WSL")
    lock = json.loads((ROOT / "scripts/toolchain.json").read_text())
    cache = ROOT / ".cache/downloads"
    cache.mkdir(parents=True, exist_ok=True)
    inputs = [lock["sdk"], lock["sdk_source"], *lock["packages"]]
    for item in inputs:
        obtain(item, cache, args.offline)
    destination = ROOT / ".cache/toolchain"
    marker = destination / "input-lock.sha256"
    lock_digest = digest(ROOT / "scripts/toolchain.json")
    if destination.exists():
        if marker.is_file() and marker.read_text().strip() == lock_digest:
            print("Verified input cache; existing toolchain matches lock marker.")
            return
        raise FileExistsError("Existing toolchain has no matching completion marker; inspect it before retrying")
    destination.mkdir()
    unpack_sdk(cache / lock["sdk"]["file"], destination / "sdk")
    llvm = destination / "llvm-root"
    llvm.mkdir()
    for item in lock["packages"]:
        subprocess.run(["dpkg-deb", "-x", str(cache / item["file"]), str(llvm)], check=True)
    marker.write_text(lock_digest + "\n")
    print("Prepared pinned SDK and LLVM under .cache/toolchain; no system packages installed.")


if __name__ == "__main__":
    main()
