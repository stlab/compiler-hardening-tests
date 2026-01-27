# Compiler Hardening Tests

This directory contains all test executables for verifying compiler hardening features.

## Test Executables

### Report Test (`report.cpp`)

A simple test that always passes and logs compiler and platform information. Useful for verifying the build environment.

### Hardening Assertions Test (`test_observe_assertions.cpp`)

Validates that libc++ hardening correctly aborts when a violation is detected on macOS. This test intentionally triggers an out-of-bounds access to verify that hardening checks are working.

#### How It Works

The test intentionally triggers a hardening assertion by performing an out-of-bounds access on a `std::span`:

```cpp
std::span<udt> sp(arr);
volatile udt out_of_bounds = sp[10];  // Index 10 is out of bounds (array has 5 elements)
```

With hardening enabled:
- **Expected behavior on macOS**: The program aborts when the hardening check detects the violation (test passes via `WILL_FAIL TRUE`)
- **Other platforms**: The test runs but may not have hardening checks, so it reports `HARDENING_TEST_SKIPPED`

## Building and Running Tests

### On macOS (Debug mode with hardening):

```bash
# Configure for Apple Clang with Debug mode
cmake --preset=apple-clang-arm64-debug  # or apple-clang-x64-debug

# Build
cmake --build --preset=apple-clang-arm64-debug

# Run all tests via CTest
ctest --preset=apple-clang-arm64-debug --output-on-failure

# Run a specific test directly
./build/apple-clang-arm64-debug/test-report
# Note: test-hardening-assertions will abort when run directly (expected behavior)
```

### On other platforms:

Tests compile and run on all platforms. The hardening test may not trigger aborts on platforms without libc++ hardening support.

## CTest Integration

The following tests are configured:

1. **`report`**: Always passes, logs compiler and platform information (all platforms)
2. **`hardening_assertions_abort_check`**: Only runs on macOS, validates that the program aborts when a hardening violation is detected (test passes when program aborts)

## Compiler Flags

All tests are compiled with compiler-specific hardening flags using the `apply_hardening_flags()` function in CMakeLists.txt.

On macOS, tests use:

**Debug mode:**
- `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_DEBUG`: Enables debug mode hardening (all checks, aborts on violations)

**Release mode:**
- `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST`: Enables fast mode hardening (security-critical checks, aborts on violations)

## Expected Output

### Report Test

```
Hello, World!
Compiler Hardening Test Application
Compiler: Apple Clang 15.0
Architecture: ARM64
```

### Hardening Assertions Test

**When run via CTest on macOS** (test passes):
```
Test project /path/to/build
    Start 1: report
1/2 Test #1: report ...........................   Passed    0.01 sec
    Start 2: hardening_assertions_abort_check
2/2 Test #2: hardening_assertions_abort_check ..   Passed    0.02 sec

100% tests passed, 0 tests failed out of 2
```

**When run directly on macOS** (aborts as expected):
```
Testing libc++ hardening assertion behavior
Valid access: sp[2]._a = 3
Attempting out-of-bounds access...
Triggering hardening violation (expecting abort)...
[Program aborts with hardening error message]
```

The key points are:
- The hardening check detects the out-of-bounds access
- The program aborts (does not continue execution)
- CTest expects this abort (via `WILL_FAIL TRUE`), so the test passes

## Debugging

If a test fails:

1. Verify you're using the correct platform and compiler
2. For hardening tests on macOS: Check that Debug or Release mode is being used (both have hardening enabled)
3. Examine the compiler flags: `cmake --build --preset=apple-clang-arm64-debug --verbose`
4. Check if hardening is enabled by looking for `-D_LIBCPP_HARDENING_MODE` in the compile commands
5. Check CTest output: `ctest --preset=apple-clang-arm64-debug -V` (verbose mode)

**Note**: If `hardening_assertions_abort_check` fails (doesn't abort), it means hardening is not working correctly and violations are not being caught.

## References

- [libc++ Hardening Modes Documentation](https://libcxx.llvm.org/Hardening.html)
- [Assertion Semantics Documentation](https://libcxx.llvm.org/Hardening.html#assertion-semantics)
