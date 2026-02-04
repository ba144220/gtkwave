#!/bin/bash
# Wrapper script to run the Python ctypes implementation with proper environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set library path for macOS
export DYLD_LIBRARY_PATH="$PROJECT_ROOT/build/lib/libgtkwave/src:${DYLD_LIBRARY_PATH}"

# Set library path for Linux
export LD_LIBRARY_PATH="$PROJECT_ROOT/build/lib/libgtkwave/src:${LD_LIBRARY_PATH}"

# Run the Python script
exec python3 "$SCRIPT_DIR/read_signal_ctypes.py" "$@"
