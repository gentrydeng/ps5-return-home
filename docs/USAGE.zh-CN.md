# ps5-return-home 0.1.0

[English](https://github.com/gentrydeng/ps5-return-home/blob/main/docs/USAGE.md)

这个 ELF 载荷请求返回 PS5 系统主页一次后退出。使用前需要已有可用的 PS5 ELF 加载环境。兼容性取决于系统版本和加载器。

## 核对下载内容

解压前，对照 `SHA256SUMS` 的对应条目核对 PS5 x86-64 ZIP。在 Linux 上执行 `sha256sum --check --ignore-missing SHA256SUMS`。在 PowerShell 中执行 `Get-FileHash -LiteralPath '.\ps5-return-home-0.1.0-ps5-x86_64.zip' -Algorithm SHA256`，并将结果与校验清单比较。[发布下载](https://github.com/gentrydeng/ps5-return-home/releases)

解压得到的 `return-home-uri.elf` 应为 110,888 字节，并匹配以下 SHA-256。

```text
51d18a54c67e63ab53a67e63484b932c6cd44af9d79fa973577066ee80340858
```

## 运行载荷

1. 保存正在进行的工作，打开系统设置页。
2. 在已有的 ELF 加载器中选择 `return-home-uri.elf` 作为本地载荷，运行一次。
3. 确认主机进入游戏或媒体主页。如果运行失败或主机出现系统错误，请先将载荷移出自动加载列表，再排查原因。

在语言切换后使用时，请等主机完成切换再运行。载荷一启动就会发出返回主页请求。停止使用时，从自动加载列表移除对应条目，并在加载器中删除本地副本。

## 源码与许可

配套的 `ps5-return-home-0.1.0-source.zip` 含构建说明，源码根目录下的 `third_party/ps5-payload-sdk-a7685ce8-source.tar.gz` 是锁定的 PS5 Payload SDK 源码归档。[源码仓库](https://github.com/gentrydeng/ps5-return-home) · [构建指南](https://github.com/gentrydeng/ps5-return-home/blob/main/docs/BUILD.zh-CN.md)

项目原创源码采用 **BSD-2-Clause**。组合 ELF 链接了受 GPL 约束的 SDK 运行时代码，按 **GPL-3.0-or-later** 分发。再分发 ELF 时，请一并提供 `LICENSE-BSD-2-Clause.txt`、`licenses/GPL-3.0.txt`、随包第三方声明和对应源码 ZIP。[第三方声明](https://github.com/gentrydeng/ps5-return-home/blob/main/THIRD_PARTY.zh-CN.md)

大部分设计、代码、测试、文档和打包工作由 OpenAI Codex 按维护者要求完成。本项目与 Sony、所引用项目及作者、OpenAI 无官方隶属、合作、赞助或背书关系。商标归各自权利人所有。
