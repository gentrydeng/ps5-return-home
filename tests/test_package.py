# SPDX-License-Identifier: BSD-2-Clause
import hashlib
from pathlib import Path
import stat
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import package


class ArchiveTests(unittest.TestCase):
    def test_required_licensing_files(self):
        required_binary_docs = {
            "LICENSE-BSD-2-Clause.txt": "LICENSE",
            "README.md": "docs/USAGE.md",
            "README.zh-CN.md": "docs/USAGE.zh-CN.md",
            "THIRD_PARTY.md": "THIRD_PARTY.md",
            "THIRD_PARTY.zh-CN.md": "THIRD_PARTY.zh-CN.md",
            "licenses/GPL-3.0.txt": "licenses/GPL-3.0.txt",
        }
        self.assertEqual(package.BINARY_DOCS, required_binary_docs)
        required_sources = {"LICENSE", "licenses/GPL-3.0.txt", "THIRD_PARTY.md", "THIRD_PARTY.zh-CN.md",
                            "Makefile", "src/main.c", "scripts/prepare.py", "scripts/build.sh", "scripts/package.py",
                            "scripts/verify.py", "scripts/source-files.txt", "scripts/toolchain.json"}
        actual_sources = {path.relative_to(ROOT).as_posix() for path in package.source_files()}
        self.assertLessEqual(required_sources, actual_sources)

    def test_archive_contents(self):
        expected = {"LICENSE.txt": b"expected text"}
        locked_name = "sdk-source.tar.gz"
        locked_bytes = b"locked bytes"
        locked = {"bytes": len(locked_bytes), "sha256": hashlib.sha256(locked_bytes).hexdigest()}
        valid = [*expected.items(), (locked_name, locked_bytes)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            good = root / "valid.zip"
            package.write_zip(good, valid)
            package.verify_zip(good, expected, locked_name, locked)

            for label, entries, error in [
                ("missing-license", valid[1:], "invalid member list"),
                ("extra-member", valid + [("extra.txt", b"extra")], "invalid member list"),
                ("unsafe-path", valid + [("../extra.txt", b"extra")], "unsafe ZIP member path"),
                ("wrong-license", [("LICENSE.txt", b"changed  text"), valid[1]], "wrong contents"),
                ("wrong-length", [valid[0], (locked_name, b"short")], "wrong size"),
                ("wrong-locked-hash", [valid[0], (locked_name, b"altered data")], "wrong contents"),
            ]:
                with self.subTest(label=label):
                    archive = root / f"{label}.zip"
                    package.write_zip(archive, entries)
                    with self.assertRaisesRegex(ValueError, error):
                        package.verify_zip(archive, expected, locked_name, locked)

            unsafe_name = "../LICENSE.txt"
            unsafe_archive = root / "unsafe-expected-path.zip"
            package.write_zip(unsafe_archive, [(unsafe_name, expected["LICENSE.txt"]), valid[1]])
            with self.assertRaisesRegex(ValueError, "unsafe ZIP member path"):
                package.verify_zip(unsafe_archive, {unsafe_name: expected["LICENSE.txt"]}, locked_name, locked)

            duplicate = root / "duplicate.zip"
            with self.assertWarns(UserWarning):
                package.write_zip(duplicate, [*valid, valid[0]])
            with self.assertRaisesRegex(ValueError, "invalid member list"):
                package.verify_zip(duplicate, expected, locked_name, locked)

            linked = root / "symlink.zip"
            package.write_zip(linked, valid[1:])
            link = zipfile.ZipInfo(valid[0][0])
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(linked, "a") as archive:
                archive.writestr(link, valid[0][1])
            with self.assertRaisesRegex(ValueError, "invalid ZIP member"):
                package.verify_zip(linked, expected, locked_name, locked)

            for label, mode in [("executable", 0o100755), ("setuid", 0o104644)]:
                noncanonical = root / f"{label}-mode.zip"
                with zipfile.ZipFile(noncanonical, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                    for name, data in valid:
                        member = zipfile.ZipInfo(name, package.STAMP)
                        member.create_system = 3
                        member.external_attr = mode << 16
                        member.compress_type = zipfile.ZIP_DEFLATED
                        archive.writestr(member, data)
                with self.subTest(label=label), self.assertRaisesRegex(ValueError, "invalid ZIP member"):
                    package.verify_zip(noncanonical, expected, locked_name, locked)

    def test_release_checksum_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "return-home.zip"
            source = root / "source.zip"
            checksum = root / "SHA256SUMS"
            binary.write_bytes(b"binary")
            source.write_bytes(b"source")
            checksum.write_text("".join(
                f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
                for path in [binary, source]), encoding="utf-8")
            package.verify_checksums(binary, source, checksum)
            checksum.write_text(checksum.read_text(encoding="utf-8").replace("source", "other"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "manifest"):
                package.verify_checksums(binary, source, checksum)
