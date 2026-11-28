# 第三方声明

[English](THIRD_PARTY.md)

| 组件 | 用途 | 许可与来源 |
| --- | --- | --- |
| PS5 Payload SDK v0.45 | ELF 使用的头文件、链接支持、桩库和运行时 | SDK 自有运行时采用 GPL-3.0-or-later；所含 FreeBSD 等文件保留各自声明。[固定源码](https://github.com/ps5-payload-dev/sdk/tree/a7685ce8e97ce1f8a4f38253a41d54241c9124f1)。 |
| itsPLK unified autoloader；LightningMods／etaHEN | 系统主页 URI 和 ShellUI 接口的研究参考；没有打包上游源码文件 | [固定参考](https://github.com/itsPLK/ps5-unified-autoloader/blob/abc3b82f6ef1c99ab0cc0006f90f2b3163b5229b/src/app_killer.c)，其中注明 LightningMods／etaHEN 来源。上游代码仍遵循其自身项目许可。 |
| LLVM／Clang／LLD 19.1.7；Debian 打包 | 仅用于构建，不进入载荷或发布包 | LLVM 采用 Apache-2.0 with LLVM exceptions 及适用组件声明。[LLVM](https://github.com/llvm/llvm-project/tree/llvmorg-19.1.7)、[Debian 包资料](https://tracker.debian.org/pkg/llvm-toolchain-19)。构建输入保留原包中的 copyright 文件。 |
| GitHub Actions | CI 检出、制品传递与来源证明 | 工作流中固定 Action 提交；各自遵循其仓库许可。Action 代码不链接进载荷。 |

项目原创源码采用 BSD-2-Clause。BSD 声明在仓库和源码 ZIP 中名为 `LICENSE`，在二进制 ZIP 中名为 `LICENSE-BSD-2-Clause.txt`。ELF 包含受 GPL 约束的 SDK 运行时代码，因此组合二进制按 GPL-3.0-or-later 分发。再分发 ELF 时，请一并提供 BSD 声明、GPL 第 3 版全文、本第三方声明及对应源码 ZIP。对应源码 ZIP 包含本项目构建脚本及完整的 SDK 源码归档 `third_party/ps5-payload-sdk-a7685ce8-source.tar.gz`，保留上游作者、版权及组件声明。[GPL 第 3 版全文](licenses/GPL-3.0.txt)

SDK 二进制 ZIP 与源码归档分别固定 SHA-256。标准构建使用上游预编译 SDK 运行时。构建指南也说明了如何从对应源码构建 SDK。[构建指南](https://github.com/gentrydeng/ps5-return-home/blob/main/docs/BUILD.zh-CN.md)

`libSceShellUIUtil.sprx` 等系统模块从用户自己的主机加载。本项目不包含 Sony 固件、模块、专有 SDK、密钥、账号或游戏内容。开源 **PS5 Payload SDK** 与 Sony 的专有 SDK 是不同项目。

本项目与 Sony、所引用项目及其作者、OpenAI 没有官方隶属、合作、赞助或背书关系。技术依赖与参考已在上文注明；商标归各自权利人所有。

大部分项目设计、代码、测试、文档及打包工作由 OpenAI Codex 按维护者要求完成。维护者确定项目范围。
