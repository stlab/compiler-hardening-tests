cmake_minimum_required(VERSION 3.25)

project(compiler-hardening-tests
    VERSION 1.0.0
    DESCRIPTION "Testing and verification of compiler hardening options"
    LANGUAGES CXX
)

# Set C++20 as the required standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Export compile commands for clang-tidy
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Enable testing
enable_testing()

# ============================================================================
# Compiler-Specific Hardening Options Function
# ============================================================================

# Function to apply compiler-specific hardening flags to a target
function(apply_hardening_flags target)
    message(STATUS "Applying hardening flags to ${target}")
    
    # ----------------------------------------------------------------------------
    # Apple Clang Hardening Options
    # ----------------------------------------------------------------------------
    if(CMAKE_CXX_COMPILER_ID MATCHES "AppleClang")
        message(STATUS "  Compiler: Apple Clang")
        
        target_compile_options(${target} PRIVATE
            -Wall
            -Warray-bounds-pointer-arithmetic
            -Wconversion
            -Werror=format-security
            -Wextra
            -Wformat
            -Wformat=2
            -Wimplicit-fallthrough
            -Wshadow
            -Wsign-conversion
            -fPIE
            -fstack-protector-strong
            -pedantic-errors
        )
        
        # Debug-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Debug>:
                -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST
                -D_LIBCPP_ASSERTION_SEMANTIC=_LIBCPP_ASSERTION_SEMANTIC_OBSERVE
            >
        )
        
        # Release-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Release>:
                -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST
                -fno-delete-null-pointer-checks
                -fno-strict-aliasing
                -fno-strict-overflow
                -ftrivial-auto-var-init=zero
            >
        )
        
        # Architecture-specific options
        if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64")
            target_compile_options(${target} PRIVATE
                # x86-64 specific hardening for Apple Clang
            )
        elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64")
            target_compile_options(${target} PRIVATE
                # ARM64 specific hardening for Apple Clang
            )
        endif()

    # ----------------------------------------------------------------------------
    # Clang Hardening Options
    # ----------------------------------------------------------------------------
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang" AND NOT CMAKE_CXX_COMPILER_ID MATCHES "AppleClang")
        message(STATUS "  Compiler: Clang")
        
        target_compile_options(${target} PRIVATE
            -Wall
            -Wextra
            -Wpedantic
        )
        
        # Debug-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Debug>:
                # Debug-specific options for Clang
            >
        )
        
        # Release-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Release>:
                # Release-specific options for Clang
            >
        )
        
        # Architecture-specific options
        if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
            target_compile_options(${target} PRIVATE
                # x86-64 specific hardening for Clang
            )
        elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|ARM64")
            target_compile_options(${target} PRIVATE
                # ARM64 specific hardening for Clang
            )
        endif()

    # ----------------------------------------------------------------------------
    # GCC Hardening Options
    # ----------------------------------------------------------------------------
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
        message(STATUS "  Compiler: GCC")
        
        target_compile_options(${target} PRIVATE
            -Wall
            -Wextra
            -Wpedantic
        )
        
        # Debug-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Debug>:
                # Debug-specific options for GCC
            >
        )
        
        # Release-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Release>:
                # Release-specific options for GCC
            >
        )
        
        # Architecture-specific options
        if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
            target_compile_options(${target} PRIVATE
                # x86-64 specific hardening for GCC
            )
        elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|ARM64")
            target_compile_options(${target} PRIVATE
                # ARM64 specific hardening for GCC
            )
        endif()

    # ----------------------------------------------------------------------------
    # MSVC Hardening Options
    # ----------------------------------------------------------------------------
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
        message(STATUS "  Compiler: MSVC")
        
        target_compile_options(${target} PRIVATE
            /W4
        )
        
        # Debug-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Debug>:
                # Debug-specific options for MSVC
            >
        )
        
        # Release-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Release>:
                # Release-specific options for MSVC
            >
        )
        
        # Architecture-specific options
        if(CMAKE_SYSTEM_PROCESSOR MATCHES "AMD64|x64")
            target_compile_options(${target} PRIVATE
                # x86-64 specific hardening for MSVC
            )
        elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "ARM64")
            target_compile_options(${target} PRIVATE
                # ARM64 specific hardening for MSVC
            )
        endif()

    # ----------------------------------------------------------------------------
    # Emscripten Hardening Options
    # ----------------------------------------------------------------------------
    elseif(EMSCRIPTEN)
        message(STATUS "  Compiler: Emscripten")
        
        target_compile_options(${target} PRIVATE
            -Wall
            -Wextra
            -Wpedantic
        )
        
        # Debug-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Debug>:
                # Debug-specific options for Emscripten
            >
        )
        
        # Release-specific flags
        target_compile_options(${target} PRIVATE
            $<$<CONFIG:Release>:
                # Release-specific options for Emscripten
            >
        )
        
        # Set output file extension to .js (which will also generate .wasm)
        set_target_properties(${target} PROPERTIES SUFFIX ".js")
        
        target_link_options(${target} PRIVATE
            # Target Node.js environment specifically
            -sENVIRONMENT=node
            # Embed wasm as base64 in JS to avoid fetch() URL issues with Node.js
            -sSINGLE_FILE=1
            -sNODEJS_CATCH_EXIT=0
            -sNODEJS_CATCH_REJECTION=0
        )
    endif()
endfunction()

# ============================================================================
# Test Executables
# ============================================================================

# Report test - logs compiler and platform information
add_executable(test-report test/report.cpp)
apply_hardening_flags(test-report)
add_test(
    NAME report
    COMMAND test-report
)
set_tests_properties(report PROPERTIES
    LABELS "info;always-pass"
)

# Observe assertions test - validates libc++ observe semantic
add_executable(test-observe-assertions test/test_observe_assertions.cpp)
apply_hardening_flags(test-observe-assertions)

# Basic test that runs on all platforms
add_test(
    NAME observe_assertions_basic
    COMMAND test-observe-assertions
)
set_tests_properties(observe_assertions_basic PROPERTIES
    LABELS "hardening;observe"
)

# macOS-specific test that validates the observe semantic output
if(APPLE)
    add_test(
        NAME observe_assertions_output_check
        COMMAND ${CMAKE_COMMAND} -E env
            bash -c "$<TARGET_FILE:test-observe-assertions> 2>&1 | tee /tmp/test_output.txt && grep -q 'OBSERVE_TEST_PASSED' /tmp/test_output.txt"
    )
    
    set_tests_properties(observe_assertions_output_check PROPERTIES
        LABELS "macOS;hardening;observe"
        PASS_REGULAR_EXPRESSION "OBSERVE_TEST_PASSED"
    )
endif()

# ============================================================================
# Installation
# ============================================================================
install(TARGETS test-report test-observe-assertions
    RUNTIME DESTINATION bin
)
