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
   - **On macOS**: Uses `WILL_FAIL TRUE` + `PASS_REGULAR_EXPRESSION "Triggering hardening violation"`. Test passes when both conditions are met: (1) test prints the expected message, and (2) crashes with non-zero exit. This proves hardening is working.
   - **On other platforms**: Runs normally, should pass if hardening not available

The macOS test configuration ensures that hardening must both detect the violation (by printing the message) AND abort the program (non-zero exit).

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

The test uses `WILL_FAIL TRUE` (expects non-zero exit) combined with `PASS_REGULAR_EXPRESSION "Triggering hardening violation"` (expects specific output before crash). Both conditions must be met for the test to pass.

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
- On macOS, the test passes when: (1) it prints "Triggering hardening violation", AND (2) crashes with non-zero exit
- `WILL_FAIL TRUE` expects non-zero exit (the crash)
- `PASS_REGULAR_EXPRESSION` ensures the hardening code path was reached
- On non-macOS platforms, the test passes normally (no hardening)

## Debugging

If a test fails:

1. **On macOS**: If `hardening_assertions` fails, it means the program did NOT crash (hardening is not working)
2. Examine the compiler flags: `cmake --build --preset=apple-clang-arm64-debug --verbose`
3. Check if hardening is enabled by looking for `-D_LIBCPP_HARDENING_MODE` in the compile commands
4. Check CTest output: `ctest --preset=apple-clang-arm64-debug -V` (verbose mode)
5. Run the test directly to see raw behavior: `./build/apple-clang-arm64-debug/test-hardening-assertions`

### How the macOS Test Works

The macOS test uses CTest properties to validate the crash:

```cmake
set_tests_properties(hardening_assertions PROPERTIES
    WILL_FAIL TRUE                                    # Expect non-zero exit (crash)
    PASS_REGULAR_EXPRESSION "Triggering hardening violation"  # Must print this before crash
)
```

**How it works:**
1. `WILL_FAIL TRUE` - CTest expects the test to exit with non-zero status (which happens when killed by signal)
2. `PASS_REGULAR_EXPRESSION` - CTest requires the test output to contain "Triggering hardening violation"
3. Both conditions must be satisfied for the test to pass

**Why this works:**
- If hardening is working: Test prints the message, then crashes → both conditions met → ✓ PASS
- If hardening is NOT working: Test prints message, then prints "ERROR: Program continued..." and exits 1 → pattern matches but wrong message → ✗ FAIL  
- If test fails before the violation: Pattern not found → ✗ FAIL

**Success criteria on macOS**: The program must print "Triggering hardening violation" and then be killed by a signal (SIGABRT or SIGILL).

## References

- [libc++ Hardening Modes Documentation](https://libcxx.llvm.org/Hardening.html)
- [Assertion Semantics Documentation](https://libcxx.llvm.org/Hardening.html#assertion-semantics)
