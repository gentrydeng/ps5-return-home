# 从源码构建

[English](BUILD.md)

## 环境与输入

在 x86-64 Linux 上以普通用户构建。需要 Python 3.11+、GNU Make、`dpkg-deb`、`readelf`、本机 C 编译器及 LLVM 运行依赖。

若缺少前提工具，管理员可在 Debian 13 或 Ubuntu 24.04 上通过发行版签名仓库安装：

```sh
sudo apt-get update
sudo apt-get install --no-install-recommends make python3 gcc binutils dpkg-dev \
  libffi8 libedit2 libz3-4 libxml2 libzstd1 ca-certificates
```

项目脚本不执行这些管理命令，只在本地解压编译器和 SDK。固定输入为 SDK **v0.45**、提交 `a7685ce8e97ce1f8a4f38253a41d54241c9124f1`，以及 LLVM／Clang／LLD **19.1.7**、Debian **1:19.1.7-3+b1**。八个下载输入的完整 URL、大小及 SHA-256 见 [toolchain.json](../scripts/toolchain.json)。Debian 包使用 TUNA HTTPS，SDK 二进制和源码来自上游 GitHub。下载或散列失败立即停止，不关闭 TLS 或静默换版本。

## 标准构建

如有对应源码 ZIP，可解压后使用，也可克隆仓库。在源码根目录执行以下命令。

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

预期 ELF 为 x86-64 ELF64／ET_DYN，**110,888 字节**，SHA-256 为 `51d18a54c67e63ab53a67e63484b932c6cd44af9d79fa973577066ee80340858`。打包在 `dist/` 中生成二进制 ZIP、对应源码 ZIP 和 `SHA256SUMS`。任一步失败均应停止。打包前须确保输出目录中没有同名文件。

最后一条命令检查从当前检出内容生成的两份 ZIP，核对归档成员清单，将随附的许可声明及其他项目文件与当前检出内容比对，按锁定散列核对归档内的 ELF 和 SDK 源码，并用 `SHA256SUMS` 核对两份 ZIP。

离线准备时，将八个锁定文件放入 `.cache/downloads/`，使用 `python3 scripts/prepare.py --offline`。如使用对应源码 ZIP，可从解压后的源码目录将 `third_party/ps5-payload-sdk-a7685ce8-source.tar.gz` 复制到该缓存。

## 完整手动等价过程

先按锁定表将八个文件下载到根目录下的 `.cache/downloads/`，再执行下列完整命令，无须准备／构建封装：

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

目录检查避免合并中断的准备结果。失败后保留输入，先核查部分目录再处理。路径映射移除本项目翻译单元中的构建路径。命令禁用链接器的 build ID，并按锁定的 ELF 散列核对输出。

## SDK 对应源码

完成上述手动准备后，可将所附 SDK 源码编译到另一个本地目录：

```sh
set -eu
test ! -e .cache/sdk-source
mkdir -p .cache/sdk-source
tar --no-same-owner -xzf .cache/downloads/ps5-payload-sdk-a7685ce8-source.tar.gz -C .cache/sdk-source
sdk_source="$PWD/.cache/sdk-source/sdk-a7685ce8e97ce1f8a4f38253a41d54241c9124f1"
make -C "$sdk_source" DESTDIR="$PWD/.cache/sdk-rebuilt" install
"$PWD/.cache/sdk-rebuilt/bin/prospero-clang" -Os -Wall -Wextra -Werror -fno-ident -ffile-prefix-map="$PWD"=. -Wl,--build-id=none -o build/return-home-uri-rebuilt-sdk.elf src/main.c -lSceUserService
```

锁定的 ELF 散列对应使用上游预编译 SDK 的标准构建。本地重建 SDK 运行时可能生成散列不同的 ELF。
