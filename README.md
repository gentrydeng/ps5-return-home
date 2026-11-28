# ps5-return-home

[简体中文](README.zh-CN.md)

A small PS5 ELF payload that requests the system Home screen once and exits. It can return you to Home after you finish changing the system language. The payload leaves system settings and files alone and keeps running applications open.

## Use

You need a PS5 with an existing environment that can load ELF payloads. Compatibility depends on the firmware and loader. Save your work and confirm that a standalone run returns to the games or media Home screen before adding the payload to an automatic sequence.

**No prebuilt downloads are available.** Build from source below. Before extracting a package, check its ZIP against `SHA256SUMS`. Load the extracted `return-home-uri.elf` as a local payload. [Downloads](https://github.com/gentrydeng/ps5-return-home/releases) · [Usage guide](docs/USAGE.md)

## Build

Use x86-64 Linux with Python 3.11+, GNU Make, `dpkg-deb`, a host C compiler, and the LLVM runtime libraries listed in the build guide.

```sh
python3 scripts/prepare.py
python3 -m unittest discover -s tests -v
sh scripts/build.sh
python3 scripts/package.py
python3 scripts/package.py --verify-only
```

The preparation script unpacks pinned build dependencies into `.cache/`. The build checks the ELF against its reference size and SHA-256. Packaging produces the binary ZIP, the corresponding-source ZIP, and `SHA256SUMS` in `dist/`. [Build guide](docs/BUILD.md) · [Pinned inputs](scripts/toolchain.json)

## Licenses and credits

Original project source uses **BSD-2-Clause**. The ELF links the GPL-covered runtime of the PS5 Payload SDK, so the combined binary is distributed under **GPL-3.0-or-later**. Include the BSD notice, GPL text, third-party notices, and corresponding-source ZIP with the pinned SDK source when redistributing the ELF. [BSD-2-Clause](LICENSE) · [GPL version 3](licenses/GPL-3.0.txt) · [Third-party notices](THIRD_PARTY.md)

PS5 Payload SDK contributors maintain the SDK. The home-navigation mechanism draws on an interface described by itsPLK's unified autoloader, which credits LightningMods/etaHEN. [PS5 Payload SDK](https://github.com/ps5-payload-dev/sdk) · [Upstream reference](https://github.com/itsPLK/ps5-unified-autoloader/blob/abc3b82f6ef1c99ab0cc0006f90f2b3163b5229b/src/app_killer.c)

This project has no official affiliation, partnership, sponsorship, or endorsement from Sony, the referenced projects and their authors, or OpenAI. PlayStation and other names belong to their respective owners.

**OpenAI Codex** performed most of the design, code, testing, documentation, and packaging work at the maintainer's request. The maintainer set the project scope.
