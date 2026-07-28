---
layout: page
title: Deferred WSL2 and Linux Setup
permalink: /setup-wsl/
---

# Deferred WSL2 and Linux setup

Status: **documented, not yet executed**

Use this chapter when ready to begin implementation. Do not mark Phase 0
complete merely because these commands are written down; record the real
outputs and versions when they are run.

## Why WSL2

Spike and the RISC-V GNU toolchain are Linux-first projects. WSL2 gives this
Windows project a normal Linux build environment while keeping GitHub Pages and
editor workflows accessible from Windows.

Use a real Ubuntu distribution. The existing `docker-desktop` WSL distribution
is an implementation detail of Docker Desktop and should not be used as the
development distribution.

## Stage W0 — Inspect before changing anything

Open a non-administrator PowerShell terminal and run:

```powershell
wsl --status
wsl --version
wsl --list --verbose
wsl --list --online
```

Record the output in the Phase 0 progress article. The desired end state is a
normal Ubuntu distribution with version `2`.

If Ubuntu is already present, do not reinstall it. Launch it and continue at
Stage W2.

## Stage W1 — Install Ubuntu

Installation changes Windows features and may require a restart, so perform it
from an administrator PowerShell terminal when you choose to proceed.

If `Ubuntu-24.04` appears in `wsl --list --online`:

```powershell
wsl --install --distribution Ubuntu-24.04
```

Otherwise install the listed Ubuntu distribution:

```powershell
wsl --install --distribution Ubuntu
```

Restart if requested. At first launch, create a Linux user and password. Do not
use `root` as the normal development account.

Verify from PowerShell:

```powershell
wsl --list --verbose
```

If the distribution is not using WSL2:

```powershell
wsl --set-version Ubuntu-24.04 2
```

Replace `Ubuntu-24.04` with the exact name shown by `wsl --list --verbose`.

Expected shape, not exact version text:

```text
NAME            STATE           VERSION
Ubuntu-24.04    Stopped         2
```

## Stage W2 — Choose one canonical checkout

Linux builds perform many small file operations. Keep the implementation
checkout in the Linux filesystem:

```bash
mkdir -p ~/src
cd ~/src
read -r -p "Paste the HTTPS clone URL from the GitHub Code menu: " repository_url
git clone "$repository_url"
cd NPU_sw_stack
```

Do not make both the Windows checkout and WSL checkout independently editable.
The recommended workflow is:

```text
edit/build/test in ~/src/NPU_sw_stack under WSL
-> commit and push
-> use GitHub as the synchronization boundary
```

Windows can browse this checkout through:

```text
\\wsl.localhost\Ubuntu-24.04\home\LINUX_USER\src\NPU_sw_stack
```

Avoid building the Windows checkout through `/mnt/c/...`; Microsoft documents
that Linux builds and Git operations are faster in the Linux filesystem.

## Stage W3 — Record the base environment

Inside Ubuntu:

```bash
uname -a
cat /etc/os-release
git --version
python3 --version
```

Save these values in the progress post. They are observations, not assumed
versions.

## Stage W4 — Install common project packages

First update package metadata:

```bash
sudo apt-get update
```

Install the native project tools:

```bash
sudo apt-get install -y \
  build-essential \
  ca-certificates \
  cmake \
  git \
  ninja-build \
  pkg-config \
  python3 \
  python3-pip \
  python3-venv
```

Verify:

```bash
cmake --version
ninja --version
g++ --version
python3 --version
```

Record installed package versions:

```bash
dpkg-query -W \
  build-essential cmake git ninja-build \
  python3 python3-pip python3-venv
```

## Stage W5 — Create the Python environment

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip freeze
```

The prompt should indicate the active environment. Verify imports:

```bash
python -c "import numpy; print(numpy.__version__)"
```

If `python3 -m venv` reports that `ensurepip` is unavailable, confirm that
`python3-venv` is installed.

## Stage W6 — Build the native project

The Linux-native build should become the primary path once WSL exists:

```bash
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DNPU_ENABLE_SANITIZERS=ON
cmake --build build
ctest --test-dir build --output-on-failure
```

Also run:

```bash
python -m pytest -q
powershell.exe -NoProfile -File scripts/check_docs.ps1
```

If PowerShell interoperability is unavailable, add a Linux documentation-check
script before declaring WSL the canonical environment.

## Stage W7 — Install the packaged RV64 bare-metal compiler

For the first hello-world gate, use Ubuntu's packaged compiler:

```bash
sudo apt-get install -y \
  binutils-riscv64-unknown-elf \
  gcc-riscv64-unknown-elf
```

Verify and record:

```bash
riscv64-unknown-elf-gcc --version
riscv64-unknown-elf-ld --version
```

This is a bootstrap choice, not a forever pin. If its Newlib/header packaging
is insufficient for the freestanding runtime, either keep the firmware
strictly freestanding or build the pinned upstream Newlib toolchain described
below.

## Stage W8 — Optional pinned upstream RISC-V toolchain

Building the complete upstream toolchain consumes several gigabytes and time.
Do it only if the packaged compiler cannot satisfy the runtime gate or exact
compiler revision is part of an experiment.

The official toolchain README lists the Ubuntu prerequisites and supports a
Newlib build:

```bash
git clone https://github.com/riscv-collab/riscv-gnu-toolchain.git
cd riscv-gnu-toolchain
git checkout PINNED_COMMIT
./configure --prefix="$HOME/opt/riscv"
make -j"$(nproc)"
```

Before running it:

1. Replace `PINNED_COMMIT` with a reviewed full commit hash.
2. Record that hash in the repository dependency manifest.
3. Ensure sufficient disk space.
4. Do not install into a system directory.
5. Add `$HOME/opt/riscv/bin` to the project shell environment.

## Stage W9 — Install Spike build dependencies

The Spike README names Device Tree Compiler and Boost system/regex
dependencies. Install those plus the standard build tools:

```bash
sudo apt-get install -y \
  autoconf \
  automake \
  device-tree-compiler \
  libboost-regex-dev \
  libboost-system-dev \
  libtool
```

Then clone and pin Spike:

```bash
mkdir -p ~/src/third_party
cd ~/src/third_party
git clone https://github.com/riscv-software-src/riscv-isa-sim.git
cd riscv-isa-sim
git checkout PINNED_SPIKE_COMMIT
git rev-parse HEAD
```

Build into a user-owned prefix:

```bash
mkdir -p build
cd build
../configure --prefix="$HOME/opt/riscv"
make -j"$(nproc)"
make install
```

Verify:

```bash
"$HOME/opt/riscv/bin/spike" --help
```

Do not select `PINNED_SPIKE_COMMIT` by copying the moving `master` branch into
the documentation. Record the reviewed full hash in a dependency manifest.

## Stage W10 — First Spike proof

The first proof contains no NPU:

1. Compile a minimal RV64 freestanding ELF.
2. Inspect it with `readelf` and `objdump`.
3. Run it under the pinned Spike.
4. Capture exit status and console output.
5. Repeat from a clean build.

Suggested inspection commands:

```bash
riscv64-unknown-elf-readelf -h -S firmware.elf
riscv64-unknown-elf-objdump -d firmware.elf > firmware.dis
spike --isa=rv64imac firmware.elf
```

The exact Spike launch depends on whether the project uses HTIF, semihosting,
`riscv-pk`, or its own reset/exit mechanism. Freeze that choice in the firmware
lesson instead of silently changing the command.

## WSL setup exit gate

The setup is complete only when all statements are true:

- A named Ubuntu distribution runs under WSL2.
- The repository lives in the Linux filesystem.
- Native C++ and Python tests run from a clean checkout.
- Compiler, CMake, Ninja, Python, and package versions are recorded.
- A pinned Spike build runs.
- A non-NPU RV64 program exits deterministically.
- The progress article contains actual outputs and any deviations from this
  guide.

## Troubleshooting decision tree

```text
No Ubuntu distribution?
  -> inspect wsl --list --online
  -> install one named distribution

Build is unexpectedly slow?
  -> check pwd
  -> move checkout from /mnt/c to ~/src

No riscv64-unknown-elf-gcc?
  -> verify Ubuntu package installation
  -> only then consider upstream toolchain build

Spike configure cannot find a dependency?
  -> compare with the pinned Spike README
  -> record the missing package
  -> do not add arbitrary packages without documenting why

RV64 ELF traps immediately?
  -> inspect ELF entry point, ISA string, linker map, and reset address
  -> prove hello-world before loading the NPU plug-in
```

## Primary references

- [Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Basic WSL commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)
- [WSL file storage and performance](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
- [Spike repository and official build steps](https://github.com/riscv-software-src/riscv-isa-sim)
- [RISC-V GNU toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain)
- [Ubuntu RV64 bare-metal binutils package](https://packages.ubuntu.com/noble/binutils-riscv64-unknown-elf)
- [Ubuntu RV64 bare-metal GCC package](https://packages.ubuntu.com/noble/gcc-riscv64-unknown-elf)
