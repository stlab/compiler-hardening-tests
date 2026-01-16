#include <iostream>

int main([[maybe_unused]] int argc, [[maybe_unused]] char* argv[]) {
    std::cout << "Hello, World!" << std::endl;
    std::cout << "Compiler Hardening Test Application" << std::endl;

#if defined(__clang__)
#if defined(__apple_build_version__)
    std::cout << "Compiler: Apple Clang " << __clang_major__ << "." << __clang_minor__ << std::endl;
#else
    std::cout << "Compiler: Clang " << __clang_major__ << "." << __clang_minor__ << std::endl;
#endif
#elif defined(__GNUC__)
    std::cout << "Compiler: GCC " << __GNUC__ << "." << __GNUC_MINOR__ << std::endl;
#elif defined(_MSC_VER)
    std::cout << "Compiler: MSVC " << _MSC_VER << std::endl;
#elif defined(__EMSCRIPTEN__)
    std::cout << "Compiler: Emscripten" << std::endl;
#endif

#if defined(__x86_64__) || defined(_M_X64)
    std::cout << "Architecture: x86-64" << std::endl;
#elif defined(__aarch64__) || defined(_M_ARM64)
    std::cout << "Architecture: ARM64" << std::endl;
#elif defined(__wasm__)
    std::cout << "Architecture: WebAssembly" << std::endl;
#endif

    return 0;
}
