#include <iostream>

int main([[maybe_unused]] int argc, [[maybe_unused]] char* argv[]) {
    std::cout << "Hello, World!\n";
    std::cout << "Compiler Hardening Test Application\n";

#ifdef __clang__
#ifdef __apple_build_version__
    std::cout << "Compiler: Apple Clang " << __clang_major__ << "." << __clang_minor__ << "\n";
#else
    std::cout << "Compiler: Clang " << __clang_major__ << "." << __clang_minor__ << "\n";
#endif
#elif defined(__GNUC__)
    std::cout << "Compiler: GCC " << __GNUC__ << "." << __GNUC_MINOR__ << "\n";
#elif defined(_MSC_VER)
    std::cout << "Compiler: MSVC " << _MSC_VER << "\n";
#elif defined(__EMSCRIPTEN__)
    std::cout << "Compiler: Emscripten\n";
#endif

#if defined(__x86_64__) || defined(_M_X64)
    std::cout << "Architecture: x86-64\n";
#elif defined(__aarch64__) || defined(_M_ARM64)
    std::cout << "Architecture: ARM64\n";
#elif defined(__wasm__)
    std::cout << "Architecture: WebAssembly\n";
#endif

    return 0;
}
