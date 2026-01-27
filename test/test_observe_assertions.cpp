#include <array>
#include <iostream>
#include <span>

struct udt {
  int _a;
};

// Test that triggers a hardening assertion with observe semantic
// This test should run on all platforms but output validation is
// platform-specific
int main() {
  std::cout << "Testing libc++ hardening with observe semantic\n";

  // Create a span and intentionally access out of bounds
  std::array<udt, 5> arr = {{{1}, {2}, {3}, {4}, {5}}};
  const std::span<udt> sp(arr);

  std::cout << "Valid access: sp[2]._a = " << sp[2]._a << "\n";

  // This should trigger an assertion in observe mode
  // In observe mode, it should log an error but continue execution
  std::cout << "Attempting out-of-bounds access...\n";

// Redirect stderr to stdout so we can capture the assertion message
#if defined(__APPLE__) && defined(__clang__)
  // On macOS with observe semantic, this should log an error
  volatile int out_of_bounds = sp[10]; // Out of bounds access
  (void)out_of_bounds;                 // Prevent optimization

  std::cout << "Continued execution after out-of-bounds access\n";
  std::cout
      << "OBSERVE_TEST_PASSED\n"; // Marker for successful observe behavior
#else
  // On other platforms, just note that the test is running
  std::cout << "Test running on non-macOS platform\n";
  std::cout << "OBSERVE_TEST_SKIPPED\n";
#endif

  return 0;
}
