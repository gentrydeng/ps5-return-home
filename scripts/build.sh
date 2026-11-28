#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
toolchain="$root/.cache/toolchain"
test -f "$toolchain/input-lock.sha256" || { echo 'Run python3 scripts/prepare.py first.' >&2; exit 1; }
export LD_LIBRARY_PATH="$toolchain/llvm-root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LLVM_CONFIG="$toolchain/llvm-root/usr/lib/llvm-19/bin/llvm-config"
export PS5_PAYLOAD_SDK="$toolchain/sdk/ps5-payload-sdk"
"$toolchain/llvm-root/usr/lib/llvm-19/bin/clang" --version
"$toolchain/llvm-root/usr/lib/llvm-19/bin/ld.lld" --version
make -C "$root" PS5_PAYLOAD_SDK="$PS5_PAYLOAD_SDK"
python3 "$root/scripts/verify.py"
