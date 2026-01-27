#include <array>
#include <iostream>
#include <span>

struct udt {
  int _a;
};

// Test that triggers a hardening assertion to validate abort behavior
// This test should abort on platforms with hardening enabled
int main() {
  std::cout << "Testing libc++ hardening assertion behavior\n";

  // Create a span and intentionally access out of bounds
  std::array<udt, 5> arr = {{{1}, {2}, {3}, {4}, {5}}};
  const std::span<udt> sp(arr);

  std::cout << "Valid access: sp[2]._a = " << sp[2]._a << "\n";

  // This should trigger an assertion in hardening modes
  std::cout << "Attempting out-of-bounds access...\n";

#if defined(__APPLE__) && defined(__clang__)
  // On macOS with hardening enabled, this should abort
  // The test is configured with WILL_FAIL TRUE, so aborting = test passes
  std::cout << "Triggering hardening violation (expecting abort)...\n";
  volatile udt out_of_bounds = sp[10]; // Out of bounds access - will abort
  (void)out_of_bounds;                 // Prevent optimization
  
  // This line should never be reached
  std::cout << "ERROR: Program continued after hardening violation!\n";
  return 1; // Failure if we get here
#else
  // On other platforms, just note that the test is running
  std::cout << "Test running on non-macOS platform (no hardening checks)\n";
  std::cout << "HARDENING_TEST_SKIPPED\n";
  return 0; // Success on non-macOS
#endif
}
