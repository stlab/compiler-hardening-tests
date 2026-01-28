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
2. **`hardening_assertions`**: Runs on all platforms
   - **On macOS**: Wrapped in shell command that detects signal termination. Test passes when exit code > 128 (indicating process was killed by signal: SIGABRT=134, SIGILL=132).
   - **On other platforms**: Runs normally, should pass if hardening not available

The macOS test uses: `bash -c "$<TARGET_FILE:test-hardening-assertions>; exit $(( $? > 128 ? 0 : 1 ))"` which converts signal termination (exit code > 128) to success (exit 0).

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

**When run via CTest on non-macOS platforms**:
```
Test project /path/to/build
    Start 1: report
1/2 Test #1: report ...........................   Passed    0.01 sec
    Start 2: hardening_assertions
2/2 Test #2: hardening_assertions .............   Passed    0.01 sec

100% tests passed, 0 tests failed out of 2
```

**When run via CTest on macOS** (signal termination is expected):
```
Test project /path/to/build
    Start 1: report
1/2 Test #1: report ...........................   Passed    0.00 sec
    Start 2: hardening_assertions
2/2 Test #2: hardening_assertions .............   Passed    0.00 sec

100% tests passed, 0 tests failed out of 2
```

The shell wrapper checks the exit code: if > 128 (signal termination), it returns 0 (success); otherwise returns 1 (failure).

**When run directly** (bypassing shell wrapper):
```bash
./build/apple-clang-arm64-debug/test-hardening-assertions
```

On macOS:
```
Testing libc++ hardening assertion behavior
Valid access: sp[2]._a = 3
Attempting out-of-bounds access...
Triggering hardening violation (expecting abort)...
libc++: hardening violation: out of bounds access detected
Illegal instruction: 4 (or Abort trap: 6)
```

On other platforms:
```
Testing libc++ hardening assertion behavior
Valid access: sp[2]._a = 3
Attempting out-of-bounds access...
Test running on non-macOS platform (no hardening checks)
HARDENING_TEST_SKIPPED
```

**Key points:**
- On macOS, the program **must be killed by signal** (exit code > 128) for the test to pass
- Shell wrapper converts signal termination to test success (exit 0)
- On non-macOS platforms, the test passes normally (no hardening)

## Debugging

If a test fails:

1. **On macOS**: If `hardening_assertions` fails, it means the program did NOT crash (hardening is not working)
2. Examine the compiler flags: `cmake --build --preset=apple-clang-arm64-debug --verbose`
3. Check if hardening is enabled by looking for `-D_LIBCPP_HARDENING_MODE` in the compile commands
4. Check CTest output: `ctest --preset=apple-clang-arm64-debug -V` (verbose mode)
5. Run the test directly to see raw behavior: `./build/apple-clang-arm64-debug/test-hardening-assertions`

### How the macOS Test Works

The macOS test uses a shell wrapper to detect and validate signal termination:

```bash
bash -c "$<TARGET_FILE:test-hardening-assertions>; exit $(( $? > 128 ? 0 : 1 ))"
```

**How it works:**
1. Runs the test executable
2. Captures exit code in `$?`
3. When process is killed by signal: exit code = `128 + signal_number`
   - SIGABRT (6) → exit code 134
   - SIGILL (4) → exit code 132
4. Uses arithmetic: if exit code > 128, return 0 (success), else return 1 (failure)
5. CTest sees exit 0 → test passes ✓

**Why this works:**
- If hardening is working: Process killed by signal → exit code 134 or 132 → wrapper returns 0 → ✓ PASS
- If hardening is NOT working: Process exits normally with 0 or 1 → exit code ≤ 128 → wrapper returns 1 → ✗ FAIL

**Success criteria on macOS**: The program must be killed by a signal (SIGABRT or SIGILL) when the hardening violation occurs.

## References

- [libc++ Hardening Modes Documentation](https://libcxx.llvm.org/Hardening.html)
- [Assertion Semantics Documentation](https://libcxx.llvm.org/Hardening.html#assertion-semantics)
