#!/bin/bash
# Run the Python GI wrapper with proper environment setup

# Project root is the current directory
PROJECT_ROOT="$(pwd)"

# Set GI_TYPELIB_PATH to include the build directory
export GI_TYPELIB_PATH="$PROJECT_ROOT/build/lib/libgtkwave/src:${GI_TYPELIB_PATH}"

# Also set LD_LIBRARY_PATH (Linux) and DYLD_LIBRARY_PATH (macOS) for the library
export LD_LIBRARY_PATH="$PROJECT_ROOT/build/lib/libgtkwave/src:${LD_LIBRARY_PATH}"
export DYLD_LIBRARY_PATH="$PROJECT_ROOT/build/lib/libgtkwave/src:${DYLD_LIBRARY_PATH}"

# Add subproject libraries (libfst, etc.)
export LD_LIBRARY_PATH="$PROJECT_ROOT/build/subprojects/fst:${LD_LIBRARY_PATH}"
export DYLD_LIBRARY_PATH="$PROJECT_ROOT/build/subprojects/fst:${DYLD_LIBRARY_PATH}"
