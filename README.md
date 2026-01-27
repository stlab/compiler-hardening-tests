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
2. Run: **"CMake: Select Configure Preset"** → Choose a preset (e.g., `apple-clang-arm64-debug`)
3. Run: **"CMake: Configure"**
4. Run: **"CMake: Build"**
5. Run tests using **"CMake: Run Tests"** or use the Testing sidebar

### Using CMake Presets from Command Line

The project includes presets for all compiler/architecture combinations:

```bash
# List available presets
cmake --list-presets

# Configure with a preset
cmake --preset=<preset-name>

# Build with a preset
cmake --build --preset=<preset-name>

# Run tests
ctest --preset=<preset-name> --output-on-failure
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

#### Building and Testing on Linux with GCC (x86-64)

```bash
cmake --preset=gcc-x64
cmake --build --preset=gcc-x64
ctest --test-dir build/gcc-x64 --output-on-failure
```

#### Building and Testing on macOS with Apple Clang (ARM64, Debug mode)

```bash
cmake --preset=apple-clang-arm64-debug
cmake --build --preset=apple-clang-arm64-debug
ctest --preset=apple-clang-arm64-debug --output-on-failure
```

#### Building and Testing for WebAssembly

```bash
# Make sure EMSDK is installed and activated
source $EMSDK/emsdk_env.sh

cmake --preset=emscripten-wasm
cmake --build --preset=emscripten-wasm
ctest --test-dir build/emscripten-wasm --output-on-failure
```

## Adding Hardening Options

The `CMakeLists.txt` file contains a centralized `apply_hardening_flags()` function with compiler-specific hardening options. This function is automatically applied to all test executables, ensuring consistent hardening across the project.

### Modifying the Hardening Function

To add or modify hardening flags, edit the `apply_hardening_flags()` function in `CMakeLists.txt`:

```cmake
# Example: Adding hardening options for GCC
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    message(STATUS "  Compiler: GCC")
    
    target_compile_options(${target} PRIVATE
        -Wall
        -Wextra
        -Wpedantic
        # Add your GCC hardening flags here:
        -fstack-protector-strong
        -D_FORTIFY_SOURCE=2
        -fPIE
    )

    target_link_options(${target} PRIVATE
        -pie
        -Wl,-z,relro
        -Wl,-z,now
    )
```

### Architecture-Specific Options

Each compiler section includes architecture-specific subsections:

```cmake
# Architecture-specific options for GCC
if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
    target_compile_options(${target} PRIVATE
        # x86-64 specific hardening for GCC
        -fcf-protection=full
    )
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|ARM64")
    target_compile_options(${target} PRIVATE
        # ARM64 specific hardening for GCC
        -mbranch-protection=standard
    )
endif()
```

### Adding New Tests

To add a new test, create a source file in the `test/` directory and add it to `CMakeLists.txt`:

```cmake
# New test executable
add_executable(test-my-feature test/test_my_feature.cpp)
apply_hardening_flags(test-my-feature)

# Register with CTest
add_test(NAME my_feature COMMAND test-my-feature)
set_tests_properties(my_feature PROPERTIES LABELS "my-label")
```

## Static Analysis

The project includes a dedicated clang-tidy preset that runs static analysis during compilation:

```bash
# Configure and build with clang-tidy enabled
cmake --preset=clang-tidy
cmake --build --preset=clang-tidy
```

The clang-tidy preset is based on `clang-x64` and sets `CMAKE_CXX_CLANG_TIDY` to run clang-tidy automatically on all source files during build.

## Testing

This project is test-focused. All executables are tests that verify compiler hardening features.

### Available Tests

1. **Report Test** (`test-report`): Always passes and logs compiler/platform information
2. **Observe Semantic Test** (`test-observe-assertions`): Validates libc++ `observe` assertion semantic on macOS

### Running Tests

All tests are run using CTest:

```bash
# Configure with Debug mode for macOS (includes observe semantic)
cmake --preset=apple-clang-arm64-debug

# Build
cmake --build --preset=apple-clang-arm64-debug

# Run all tests
ctest --preset=apple-clang-arm64-debug --output-on-failure

# Run specific test
ctest --preset=apple-clang-arm64-debug -R report --output-on-failure
```

### Test Presets

| Preset                     | Description                                        |
| -------------------------- | -------------------------------------------------- |
| `apple-clang-x64-debug`    | Debug build with observe semantic (macOS x86-64)   |
| `apple-clang-arm64-debug`  | Debug build with observe semantic (macOS ARM64)    |

### libc++ Observe Semantic Test

The observe semantic test validates that libc++ hardening works correctly:

1. Intentionally triggers a hardening assertion (out-of-bounds `std::span` access)
2. Verifies that with `observe` semantic, the program logs an error but continues execution
3. On macOS, validates that `OBSERVE_TEST_PASSED` appears in the output
4. On other platforms, the test runs but output validation is skipped

#### Compiler Flags

On macOS Debug builds:
- `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_DEBUG` - Debug mode hardening
- `-D_LIBCPP_ASSERTION_SEMANTIC=_LIBCPP_ASSERTION_SEMANTIC_OBSERVE` - Observe semantic

On macOS Release builds:
- `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST` - Fast mode hardening

See [test/README.md](test/README.md) for detailed test documentation.

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
├── CMakeLists.txt                    # Main CMake configuration with hardening flags
├── CMakePresets.json                 # Presets for all compiler/arch combinations
├── CMakeUserPresets.json.example     # Example user-specific default presets
├── CMakeUserPresets.json             # User-specific default presets (not committed)
├── README.md                         # This file
├── OBSERVE_SEMANTIC_TEST.md          # Implementation details for observe semantic test
├── .clang-tidy                       # clang-tidy configuration
├── .gitignore                        # Git ignore patterns
├── test/
│   ├── README.md                     # Test documentation
│   ├── report.cpp                    # Report test (logs compiler/platform info)
│   └── test_observe_assertions.cpp   # Observe semantic test
├── tools/
│   ├── diagnostic-flags/             # Diagnostic flags analysis tools
│   └── inconsistency-analysis/       # Inconsistency analysis tools
└── .github/
    └── workflows/
        └── ci.yml                    # CI configuration
```

## License

** TBD **

## Contributing

** TBD **
