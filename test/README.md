# Compiler Hardening Tests

This directory contains all test executables for verifying compiler hardening features.

## Test Executables

### Report Test (`report.cpp`)

A simple test that always passes and logs compiler and platform information. Useful for verifying the build environment.

### Observe Semantic Test (`test_observe_assertions.cpp`)

Validates that the libc++ `observe` assertion semantic works correctly on macOS. The `observe` semantic is designed to log errors when hardening checks fail but continue program execution instead of terminating.

#### How It Works

The test intentionally triggers a hardening assertion by performing an out-of-bounds access on a `std::span`:

```cpp
std::span<int> sp(arr, 5);
volatile int out_of_bounds = sp[10];  // Index 10 is out of bounds
```

With the `observe` semantic enabled:
- **Expected behavior on macOS**: The assertion fires, logs an error message to stderr, but the program continues execution and prints `OBSERVE_TEST_PASSED`
- **Other platforms**: The test runs but outputs `OBSERVE_TEST_SKIPPED` since the observe semantic is only configured for macOS builds

## Building and Running Tests

### On macOS (Debug mode with observe semantic):

```bash
# Configure for Apple Clang with Debug mode
cmake --preset=apple-clang-arm64-debug  # or apple-clang-x64-debug

# Build
cmake --build --preset=apple-clang-arm64-debug

# Run all tests via CTest
ctest --preset=apple-clang-arm64-debug --output-on-failure

# Run a specific test directly
./build/apple-clang-arm64-debug/test-report
./build/apple-clang-arm64-debug/test-observe-assertions
```

### On other platforms:

Tests compile and run on all platforms. The observe semantic test runs but output validation is only performed on macOS. On non-macOS platforms, the observe test reports that it was skipped.

## CTest Integration

The following tests are configured:

1. **`report`**: Always passes, logs compiler and platform information (all platforms)
2. **`observe_assertions_basic`**: Runs the observe semantic test (all platforms)
3. **`observe_assertions_output_check`**: Only runs on macOS, validates that `OBSERVE_TEST_PASSED` appears in the output

## Compiler Flags

All tests are compiled with compiler-specific hardening flags using the `apply_hardening_flags()` function in CMakeLists.txt.

On macOS, tests use:

**Debug mode:**
- `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_DEBUG`: Enables debug mode hardening
- `-D_LIBCPP_ASSERTION_SEMANTIC=_LIBCPP_ASSERTION_SEMANTIC_OBSERVE`: Uses observe semantic (log but continue)

**Release mode:**
- `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST`: Enables fast mode hardening (includes bounds checking)

## Expected Output

### Report Test

```
Hello, World!
Compiler Hardening Test Application
Compiler: Apple Clang 15.0
Architecture: ARM64
```

### Observe Semantic Test

On macOS with observe semantic, you should see output similar to:

```
Testing libc++ hardening with observe semantic
Valid access: sp[2] = 3
Attempting out-of-bounds access...
[libc++ assertion error message about out-of-bounds access]
Continued execution after out-of-bounds access
OBSERVE_TEST_PASSED
```

The key points are:
- An error message is logged when the out-of-bounds access occurs
- Execution continues after the assertion
- The test outputs `OBSERVE_TEST_PASSED`

## Debugging

If a test fails:

1. Verify you're using the correct platform and compiler
2. For observe semantic tests on macOS: Check that the Debug preset is being used
3. Examine the compiler flags: `cmake --build --preset=apple-clang-arm64-debug --verbose`
4. Run the test manually to see the full output: `./build/apple-clang-arm64-debug/test-observe-assertions 2>&1`
5. Check CTest output: `ctest --preset=apple-clang-arm64-debug -V` (verbose mode)

## References

- [libc++ Hardening Modes Documentation](https://libcxx.llvm.org/Hardening.html)
- [Assertion Semantics Documentation](https://libcxx.llvm.org/Hardening.html#assertion-semantics)
