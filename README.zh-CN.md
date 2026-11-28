# ps5-return-home

[English](README.md)

一个请求返回 PS5 系统主页后退出的小型 ELF 载荷，可在完成系统语言切换后用来返回主页。载荷不修改系统设置或文件，也不结束其他正在运行的应用。

## 使用

PS5 需要已有可用的 ELF 加载环境。兼容性取决于系统版本和加载器。请先保存工作并单独运行一次，确认能返回游戏或媒体主页，再考虑将载荷加入自动序列。

**当前尚无预编译下载包。** 请按下文从源码构建。解压程序包前，先用 `SHA256SUMS` 核对 ZIP，再将 `return-home-uri.elf` 加载为本地载荷。[下载页面](https://github.com/gentrydeng/ps5-return-home/releases) · [使用说明](docs/USAGE.zh-CN.md)

## 构建

使用 x86-64 Linux，准备 Python 3.11+、GNU Make、`dpkg-deb`、本机 C 编译器和构建指南列出的 LLVM 运行库。

```sh
python3 scripts/prepare.py
python3 -m unittest discover -s tests -v
sh scripts/build.sh
python3 scripts/package.py
python3 scripts/package.py --verify-only
```

准备脚本将锁定的构建依赖解压到 `.cache/`。构建过程按基准大小和 SHA-256 核对 ELF。打包在 `dist/` 中生成二进制 ZIP、对应源码 ZIP 和 `SHA256SUMS`。[构建指南](docs/BUILD.zh-CN.md) · [锁定的构建输入](scripts/toolchain.json)

## 许可与致谢

项目原创源码采用 **BSD-2-Clause**。ELF 链接了 PS5 Payload SDK 中受 GPL 约束的运行时，因此组合二进制按 **GPL-3.0-or-later** 分发。再分发 ELF 时，请一并提供 BSD 声明、GPL 全文、第三方声明和包含锁定 SDK 源码的对应源码 ZIP。[BSD-2-Clause](LICENSE) · [GPL 第 3 版](licenses/GPL-3.0.txt) · [第三方声明](THIRD_PARTY.zh-CN.md)

SDK 由 PS5 Payload SDK 贡献者维护。主页导航机制使用了 itsPLK 的 unified autoloader 所描述的接口，该项目将其来源归于 LightningMods／etaHEN。[PS5 Payload SDK](https://github.com/ps5-payload-dev/sdk) · [上游参考](https://github.com/itsPLK/ps5-unified-autoloader/blob/abc3b82f6ef1c99ab0cc0006f90f2b3163b5229b/src/app_killer.c)

本项目与 Sony、所引用项目及作者、OpenAI 无官方隶属、合作、赞助或背书关系。PlayStation 等名称归各自权利人所有。

大部分设计、代码、测试、文档和打包工作由 **OpenAI Codex** 按维护者要求完成。维护者确定项目范围。
