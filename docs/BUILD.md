# Building from source

[简体中文](BUILD.zh-CN.md)

## Environment and inputs

Build as an ordinary user on x86-64 Linux with Python 3.11+, GNU Make, `dpkg-deb`, `readelf`, a host C compiler, and LLVM runtime dependencies.

If prerequisites are missing, an administrator can install them from the distribution's signed repositories on Debian 13 or Ubuntu 24.04:

```sh
sudo apt-get update
sudo apt-get install --no-install-recommends make python3 gcc binutils dpkg-dev \
  libffi8 libedit2 libz3-4 libxml2 libzstd1 ca-certificates
```

Project scripts do not execute these administrative commands. They unpack the compiler and SDK locally. Fixed inputs are SDK **v0.45**, commit `a7685ce8e97ce1f8a4f38253a41d54241c9124f1`, and LLVM/Clang/LLD **19.1.7**, Debian **1:19.1.7-3+b1**. All eight download URLs, sizes, and SHA-256 values are in [toolchain.json](../scripts/toolchain.json). Debian packages use TUNA HTTPS; the SDK binary and source use upstream GitHub. A download or hash failure is a stop condition. Do not disable TLS or change versions silently.

## Standard build

Extract the corresponding-source ZIP when available, or clone the repository. Run the following commands from the source tree root.

```sh
python3 scripts/prepare.py
python3 -m unittest discover -s tests -v
sh scripts/build.sh
readelf -h build/return-home-uri.elf
readelf -d build/return-home-uri.elf
sha256sum build/return-home-uri.elf
python3 scripts/package.py
python3 scripts/package.py --verify-only
```

The expected ELF is x86-64 ELF64/ET_DYN, **110,888 bytes**, with SHA-256 `51d18a54c67e63ab53a67e63484b932c6cd44af9d79fa973577066ee80340858`. Packaging writes the binary ZIP, corresponding-source ZIP, and `SHA256SUMS` to `dist/`. Stop after any failed command. Packaging requires an empty output location for those files.

The final command checks the ZIPs generated from the current checkout. It verifies the member lists, compares bundled notices and other project files with the checkout, checks the archived ELF and SDK source against their pinned hashes, and verifies `SHA256SUMS` against both ZIPs.

For offline preparation, place the eight locked files in `.cache/downloads/` and use `python3 scripts/prepare.py --offline`. If you started from the corresponding-source ZIP, copy `third_party/ps5-payload-sdk-a7685ce8-source.tar.gz` from the extracted source tree into that cache.

## Manual equivalent

From the root, first download the eight files listed in the lock into `.cache/downloads/`. The following complete commands verify, unpack, and compile without the preparation/build wrappers:

```sh
set -eu
python3 - <<'PY'
import hashlib, json
from pathlib import Path
lock = json.loads(Path('scripts/toolchain.json').read_text())
for item in [lock['sdk'], lock['sdk_source'], *lock['packages']]:
    path = Path('.cache/downloads') / item['file']
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if path.stat().st_size != item['bytes'] or actual != item['sha256']:
        raise SystemExit('Input mismatch: ' + item['file'])
    print('OK', item['file'])
PY
test ! -e .cache/manual-toolchain
mkdir -p .cache/manual-toolchain/sdk .cache/manual-toolchain/llvm-root
python3 -m zipfile -e .cache/downloads/ps5-payload-sdk-v0.45.zip .cache/manual-toolchain/sdk
chmod +x .cache/manual-toolchain/sdk/ps5-payload-sdk/bin/*
for package in clang-19 libclang-cpp19 libllvm19 libclang-common-19-dev lld-19 llvm-19; do
  dpkg-deb -x ".cache/downloads/${package}_19.1.7-3+b1_amd64.deb" .cache/manual-toolchain/llvm-root
done
export LD_LIBRARY_PATH="$PWD/.cache/manual-toolchain/llvm-root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LLVM_CONFIG="$PWD/.cache/manual-toolchain/llvm-root/usr/lib/llvm-19/bin/llvm-config"
export PS5_PAYLOAD_SDK="$PWD/.cache/manual-toolchain/sdk/ps5-payload-sdk"
mkdir -p build
"$PS5_PAYLOAD_SDK/bin/prospero-clang" -Os -Wall -Wextra -Werror -fno-ident \
  -ffile-prefix-map="$PWD"=. -Wl,--build-id=none \
  -o build/return-home-uri.elf src/main.c -lSceUserService
python3 scripts/verify.py
```

The directory check avoids merging interrupted preparation. On failure, preserve inputs and inspect partial directories before retrying. Path mapping removes this project's translation-unit build path. The command disables the linker build ID and checks the output against the pinned ELF digest.

## SDK corresponding sources

After the manual preparation above, rebuild the supplied SDK sources into another local destination:

```sh
set -eu
test ! -e .cache/sdk-source
mkdir -p .cache/sdk-source
tar --no-same-owner -xzf .cache/downloads/ps5-payload-sdk-a7685ce8-source.tar.gz -C .cache/sdk-source
sdk_source="$PWD/.cache/sdk-source/sdk-a7685ce8e97ce1f8a4f38253a41d54241c9124f1"
make -C "$sdk_source" DESTDIR="$PWD/.cache/sdk-rebuilt" install
"$PWD/.cache/sdk-rebuilt/bin/prospero-clang" -Os -Wall -Wextra -Werror -fno-ident -ffile-prefix-map="$PWD"=. -Wl,--build-id=none -o build/return-home-uri-rebuilt-sdk.elf src/main.c -lSceUserService
```

The pinned ELF digest is for the standard build with the upstream prebuilt SDK. A locally rebuilt SDK runtime can produce an ELF with a different digest.
