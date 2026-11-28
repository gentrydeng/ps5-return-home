# ps5-return-home 0.1.0

[简体中文](https://github.com/gentrydeng/ps5-return-home/blob/main/docs/USAGE.zh-CN.md)

This ELF payload requests the PS5 system Home screen once and exits. It requires an existing PS5 ELF-loading environment. Compatibility depends on your firmware and loader.

## Check the download

Compare the PS5 x86-64 ZIP with the matching entry in `SHA256SUMS` before extracting. Run `sha256sum --check --ignore-missing SHA256SUMS` on Linux. On PowerShell, run `Get-FileHash -LiteralPath '.\ps5-return-home-0.1.0-ps5-x86_64.zip' -Algorithm SHA256` and compare the result with the manifest. [Releases](https://github.com/gentrydeng/ps5-return-home/releases)

The extracted `return-home-uri.elf` should be 110,888 bytes and match the following SHA-256 hash.

```text
51d18a54c67e63ab53a67e63484b932c6cd44af9d79fa973577066ee80340858
```

## Run the payload

1. Save your work and open a system settings page.
2. In your existing ELF loader, select `return-home-uri.elf` as a local payload and run it once.
3. Confirm that the games or media Home screen appears. If the payload fails or the console reports a system error, remove it from automatic loading before investigating.

If using the payload after a language change, wait for the console to finish switching languages before launching it. The payload sends the Home request as soon as it starts. To stop using it, remove its automatic entry and delete the local copy from your loader.

## Source and licenses

The matching `ps5-return-home-0.1.0-source.zip` contains the build instructions and the pinned PS5 Payload SDK source at `third_party/ps5-payload-sdk-a7685ce8-source.tar.gz` under its source root. [Source repository](https://github.com/gentrydeng/ps5-return-home) · [Build guide](https://github.com/gentrydeng/ps5-return-home/blob/main/docs/BUILD.md)

Original project source uses **BSD-2-Clause**. The combined ELF links GPL-covered SDK runtime code and is distributed under **GPL-3.0-or-later**. When redistributing the ELF, include `LICENSE-BSD-2-Clause.txt`, `licenses/GPL-3.0.txt`, the bundled third-party notices, and the corresponding-source ZIP. [Third-party notices](https://github.com/gentrydeng/ps5-return-home/blob/main/THIRD_PARTY.md)

OpenAI Codex performed most of the design, code, testing, documentation, and packaging work at the maintainer's request. This project has no official affiliation, partnership, sponsorship, or endorsement from Sony, the referenced projects and their authors, or OpenAI. Trademarks belong to their respective owners.
