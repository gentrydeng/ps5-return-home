# SPDX-License-Identifier: BSD-2-Clause
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PayloadTests(unittest.TestCase):
    def test_navigation_and_failure_boundaries(self):
        with tempfile.TemporaryDirectory(prefix="return-home-tests-") as directory:
            root = Path(directory)
            cc = os.environ.get("CC", "cc")
            subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(ROOT / "tests/include"),
                            "-Dmain=payload_main", "-c", str(ROOT / "src/main.c"), "-o", str(root / "payload.o")], check=True)
            subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", str(ROOT / "tests/payload_harness.c"),
                            str(root / "payload.o"), "-o", str(root / "harness")], check=True)
            for scenario in ["success", "already-initialized", "user-error", "no-user", "zero-user", "module-error",
                             "missing-initialize", "missing-launch", "launch-error"]:
                with self.subTest(scenario=scenario):
                    subprocess.run([str(root / "harness"), scenario], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
