# Third-party notices

[简体中文](THIRD_PARTY.zh-CN.md)

| Component | Use | License and source |
| --- | --- | --- |
| PS5 Payload SDK v0.45 | Headers, linker support, stubs, and runtime linked into the ELF | GPL-3.0-or-later for the SDK's own runtime; bundled FreeBSD and other files retain their individual notices. [Fixed source](https://github.com/ps5-payload-dev/sdk/tree/a7685ce8e97ce1f8a4f38253a41d54241c9124f1). |
| itsPLK unified autoloader; LightningMods/etaHEN | Research reference for the system-home URI and ShellUI interface; no upstream source file is bundled | [Fixed reference](https://github.com/itsPLK/ps5-unified-autoloader/blob/abc3b82f6ef1c99ab0cc0006f90f2b3163b5229b/src/app_killer.c), which credits LightningMods/etaHEN. Its project license remains applicable to its own code. |
| LLVM/Clang/LLD 19.1.7; Debian packaging | Build tools only; not included in payload or release packages | LLVM uses Apache-2.0 with LLVM exceptions and applicable component notices. [LLVM](https://github.com/llvm/llvm-project/tree/llvmorg-19.1.7), [Debian package metadata](https://tracker.debian.org/pkg/llvm-toolchain-19). Original package copyright files remain in the build inputs. |
| GitHub Actions | CI checkout, artifact transfer, and provenance | Actions are pinned to commits in the workflow files; their licenses apply to their respective repositories. No Action code is linked into the payload. |

The project's original source uses BSD-2-Clause. The BSD notice is `LICENSE` in the repository and source ZIP, and `LICENSE-BSD-2-Clause.txt` in the binary ZIP. The ELF includes GPL-covered SDK runtime code, so the combined binary is distributed under GPL-3.0-or-later. When redistributing the ELF, include the BSD notice, the GPL version 3 text, these third-party notices, and the corresponding-source ZIP. That ZIP includes this project's build scripts and the complete SDK source archive at `third_party/ps5-payload-sdk-a7685ce8-source.tar.gz`, with upstream author, copyright, and component notices intact. [GPL version 3](licenses/GPL-3.0.txt)

The SDK binary ZIP and its source archive have separate pinned SHA-256 digests. The standard build uses the upstream prebuilt SDK runtime. The build guide also describes how to build the SDK from its corresponding source. [Build guide](https://github.com/gentrydeng/ps5-return-home/blob/main/docs/BUILD.md)

`libSceShellUIUtil.sprx` and other console system modules are loaded from the user's console. No Sony firmware, modules, SDK, keys, accounts, or game content are included. The open-source **PS5 Payload SDK** is distinct from Sony's proprietary SDK.

This project has no official affiliation, partnership, sponsorship, or endorsement from Sony, the referenced projects, their authors, or OpenAI. Technical dependencies and references are acknowledged above; trademarks remain with their respective owners.

Most project design, code, tests, documentation, and packaging were performed by OpenAI Codex at the maintainer's request. The maintainer set the project scope.
