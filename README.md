# Compiler Hardening Tests

[![CI](https://github.com/stlab/compiler-hardening-tests/actions/workflows/ci.yml/badge.svg)](https://github.com/stlab/compiler-hardening-tests/actions/workflows/ci.yml)

**Note: This is a work in progress. Nothing to see here yet.**

A C++20 project for testing and verifying compiler hardening options across multiple compilers and
architectures.

## Overview

This project provides a framework for systematically testing compiler-specific hardening flags and options. It supports multiple compilers and architectures with dedicated CMake configurations for each combination.

## Supported Compilers

- **Apple Clang** - Native compiler on macOS
- **Clang** - LLVM Clang compiler
- **GCC** - GNU Compiler Collection
- **MSVC** - Microsoft Visual C++ Compiler
- **Emscripten** - For WebAssembly targets

## Supported Architectures

- **x86-64** - Intel/AMD 64-bit
- **ARM64** - ARM 64-bit (AArch64)
- **WebAssembly** - Via Emscripten

## Requirements

### General

- CMake 3.25 or later
- Ninja build system (recommended)
- C++20 compatible compiler

### Platform-Specific

#### Linux

- GCC 12+ or Clang 16+
- clang-tidy (optional, for static analysis)

#### macOS

- Xcode Command Line Tools
- Apple Clang or LLVM Clang via Homebrew

#### Windows

- Visual Studio 2022 or later
- CMake and Ninja (via Visual Studio or standalone)

#### WebAssembly

- Emscripten SDK (EMSDK)

## Building

### Using VSCode/Cursor

1. Open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
2. Run: **"CMake: Select Configure Preset"** → Choose a preset (e.g., `apple-clang-x64`)
3. Run: **"CMake: Configure"**
4. Run: **"CMake: Set Launch Target"** → Select `hardening-test`
5. Press `F5` to build and run with debugging

### Using CMake Presets from Command Line

The project includes presets for all compiler/architecture combinations:

```bash
# List available presets
cmake --list-presets

# Configure with a preset
cmake --preset=<preset-name>

# Build with a preset
cmake --build --preset=<preset-name>

# Run the executable
./build/<preset-name>/hardening-test
```

### Available Presets

| Preset              | Compiler    | Architecture | Platform    |
| ------------------- | ----------- | ------------ | ----------- |
| `apple-clang-x64`   | Apple Clang | x86-64       | macOS       |
| `apple-clang-arm64` | Apple Clang | ARM64        | macOS       |
| `clang-x64`         | Clang       | x86-64       | Linux/macOS |
| `clang-arm64`       | Clang       | ARM64        | Linux/macOS |
| `gcc-x64`           | GCC         | x86-64       | Linux       |
| `gcc-arm64`         | GCC         | ARM64        | Linux       |
| `msvc-x64`          | MSVC        | x86-64       | Windows     |
| `msvc-arm64`        | MSVC        | ARM64        | Windows     |
| `emscripten-wasm`   | Emscripten  | WebAssembly  | Any         |

### Default Preset Selection

The project includes a `CMakeUserPresets.json.example` file that can be copied to `CMakeUserPresets.json` to set up default presets for your system:

```bash
cp CMakeUserPresets.json.example CMakeUserPresets.json
```

This file:

- Is user-specific and not committed to git (included in `.gitignore`)
- Helps IDEs automatically select the appropriate preset for your platform
- Can be customized for your development environment
- Provides convenient aliases like:
  - `default-macos-arm64` / `default-macos-x64` (macOS)
  - `default-linux-x64-gcc` / `default-linux-x64-clang` (Linux)
  - `default-windows-x64` (Windows)

You can edit this file to set your preferred default preset based on your system.

### Examples

#### Building on Linux with GCC (x86-64)

```bash
cmake --preset=gcc-x64
cmake --build --preset=gcc-x64
./build/gcc-x64/hardening-test
```

#### Building on macOS with Apple Clang (ARM64)

```bash
cmake --preset=apple-clang-arm64
cmake --build --preset=apple-clang-arm64
./build/apple-clang-arm64/hardening-test
```

#### Building for WebAssembly

```bash
# Make sure EMSDK is installed and activated
source $EMSDK/emsdk_env.sh

cmake --preset=emscripten-wasm
cmake --build --preset=emscripten-wasm
node ./build/emscripten-wasm/hardening-test.js
```

## Adding Hardening Options

The `CMakeLists.txt` file contains dedicated sections for each compiler with placeholders for hardening options. This structure makes it easy to add and test compiler-specific hardening flags.

### Compiler-Specific Sections

Each compiler has its own section in `CMakeLists.txt`:

```cmake
# Example: Adding hardening options for GCC
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    target_compile_options(hardening-test PRIVATE
        -Wall
        -Wextra
        -Wpedantic
        # Add your GCC hardening flags here:
        -fstack-protector-strong
        -D_FORTIFY_SOURCE=2
        -fPIE
    )

    target_link_options(hardening-test PRIVATE
        -pie
        -Wl,-z,relro
        -Wl,-z,now
    )
```

### Architecture-Specific Options

Each compiler section also includes architecture-specific subsections:

```cmake
# Architecture-specific options for GCC
if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
    target_compile_options(hardening-test PRIVATE
        # x86-64 specific hardening for GCC
        -fcf-protection=full
    )
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|ARM64")
    target_compile_options(hardening-test PRIVATE
        # ARM64 specific hardening for GCC
        -mbranch-protection=standard
    )
endif()
```

## Static Analysis

The project includes a dedicated clang-tidy preset that runs static analysis during compilation:

```bash
# Configure and build with clang-tidy enabled
cmake --preset=clang-tidy
cmake --build --preset=clang-tidy
```

The clang-tidy preset is based on `clang-x64` and sets `CMAKE_CXX_CLANG_TIDY` to run clang-tidy automatically on all source files during build.

## Continuous Integration

The project includes GitHub Actions workflows that automatically test all compiler and architecture combinations:

- **Linux**: GCC 12, GCC 13, Clang 16, Clang 17
- **macOS**: Apple Clang on x86-64 and ARM64
- **Windows**: MSVC on x86-64 and ARM64
- **WebAssembly**: Emscripten
- **Static Analysis**: clang-tidy

See `.github/workflows/ci.yml` for details.

## Project Structure

```
.
├── CMakeLists.txt                # Main CMake configuration with compiler sections
├── CMakePresets.json             # Presets for all compiler/arch combinations
├── CMakeUserPresets.json.example # Example user-specific default presets
├── CMakeUserPresets.json         # User-specific default presets (not committed)
├── main.cpp                      # Hello World test application
├── README.md                     # This file
├── .clang-tidy                  # clang-tidy configuration
├── .gitignore                   # Git ignore patterns
└── .github/
    └── workflows/
        └── ci.yml               # CI configuration
```

## License

** TBD **

## Contributing

** TBD **
