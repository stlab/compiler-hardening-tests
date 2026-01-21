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

# Create the executable
add_executable(hardening-test main.cpp)

# ============================================================================
# Compiler-Specific Hardening Options
# ============================================================================

# Helper function to add architecture-specific flags
function(add_arch_specific_flags target)
    # Determine target architecture
    set(TARGET_ARCH "")
    if(APPLE AND CMAKE_OSX_ARCHITECTURES)
        set(TARGET_ARCH ${CMAKE_OSX_ARCHITECTURES})
    else()
        set(TARGET_ARCH ${CMAKE_SYSTEM_PROCESSOR})
    endif()
    
    if(TARGET_ARCH MATCHES "x86_64|AMD64")
        # x86-64 specific flags will go here
        message(STATUS "Configuring for x86-64 architecture")
    elseif(TARGET_ARCH MATCHES "aarch64|ARM64|arm64")
        # ARM64 specific flags will go here
        message(STATUS "Configuring for ARM64 architecture")
    elseif(EMSCRIPTEN)
        # WebAssembly specific flags will go here
        message(STATUS "Configuring for WebAssembly architecture")
    endif()
endfunction()

# ----------------------------------------------------------------------------
# Apple Clang Hardening Options
# ----------------------------------------------------------------------------
if(CMAKE_CXX_COMPILER_ID MATCHES "AppleClang")
    message(STATUS "Configuring hardening options for Apple Clang")
    
    target_compile_options(hardening-test PRIVATE
        # Placeholder for Apple Clang hardening options
        -O2 -Wall -Wformat -Wformat=2 -Wconversion -Wimplicit-fallthrough
        -Werror=format-security
        -pedantic-errors
        -fstack-protector-strong

        -Wextra
        -Wsign-conversion

        -fPIE -pie

        -fno-delete-null-pointer-checks -fno-strict-overflow -fno-strict-aliasing -ftrivial-auto-var-init=zero
    )
    
    # Architecture-specific options for Apple Clang
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64")
        target_compile_options(hardening-test PRIVATE
            # x86-64 specific hardening for Apple Clang
            -fcf-protection=full
        )
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64")
        target_compile_options(hardening-test PRIVATE
            # ARM64 specific hardening for Apple Clang
            -mbranch-protection=standard
        )
    endif()

# ----------------------------------------------------------------------------
# Clang Hardening Options
# ----------------------------------------------------------------------------
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang" AND NOT CMAKE_CXX_COMPILER_ID MATCHES "AppleClang")
    message(STATUS "Configuring hardening options for Clang")
    
    target_compile_options(hardening-test PRIVATE
        # Placeholder for Clang hardening options
        -Wall
        -Wextra
        -Wpedantic
    )
    
    # Architecture-specific options for Clang
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
        target_compile_options(hardening-test PRIVATE
            # x86-64 specific hardening for Clang
        )
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|ARM64")
        target_compile_options(hardening-test PRIVATE
            # ARM64 specific hardening for Clang
        )
    endif()

# ----------------------------------------------------------------------------
# GCC Hardening Options
# ----------------------------------------------------------------------------
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    message(STATUS "Configuring hardening options for GCC")
    
    target_compile_options(hardening-test PRIVATE
        # Placeholder for GCC hardening options
        -Wall
        -Wextra
        -Wpedantic
    )
    
    # Architecture-specific options for GCC
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
        target_compile_options(hardening-test PRIVATE
            # x86-64 specific hardening for GCC
        )
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|ARM64")
        target_compile_options(hardening-test PRIVATE
            # ARM64 specific hardening for GCC
        )
    endif()

# ----------------------------------------------------------------------------
# MSVC Hardening Options
# ----------------------------------------------------------------------------
elseif(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    message(STATUS "Configuring hardening options for MSVC")
    
    target_compile_options(hardening-test PRIVATE
        # Placeholder for MSVC hardening options
        /W4
    )
    
    # Architecture-specific options for MSVC
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "AMD64|x64")
        target_compile_options(hardening-test PRIVATE
            # x86-64 specific hardening for MSVC
        )
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "ARM64")
        target_compile_options(hardening-test PRIVATE
            # ARM64 specific hardening for MSVC
        )
    endif()

# ----------------------------------------------------------------------------
# Emscripten Hardening Options
# ----------------------------------------------------------------------------
elseif(EMSCRIPTEN)
    message(STATUS "Configuring hardening options for Emscripten")
    
    target_compile_options(hardening-test PRIVATE
        # Placeholder for Emscripten hardening options
        -Wall
        -Wextra
        -Wpedantic
    )
    
    # Set output file extension to .js (which will also generate .wasm)
    set_target_properties(hardening-test PROPERTIES SUFFIX ".js")
    
    target_link_options(hardening-test PRIVATE
        # Emscripten-specific link options
        # Target Node.js environment specifically
        -sENVIRONMENT=node
        # Embed wasm as base64 in JS to avoid fetch() URL issues with Node.js
        -sSINGLE_FILE=1
        -sNODEJS_CATCH_EXIT=0
        -sNODEJS_CATCH_REJECTION=0
    )
endif()

# Apply architecture-specific flags
add_arch_specific_flags(hardening-test)

# ============================================================================
# Installation
# ============================================================================
install(TARGETS hardening-test
    RUNTIME DESTINATION bin
)
