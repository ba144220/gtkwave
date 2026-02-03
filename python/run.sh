#!/bin/bash
# Helper script to run read_signal with the correct library path

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    export DYLD_LIBRARY_PATH="../build/lib/libgtkwave/src:$DYLD_LIBRARY_PATH"
else
    # Linux
    export LD_LIBRARY_PATH="../build/lib/libgtkwave/src:$LD_LIBRARY_PATH"
fi

# Run the program
./read_signal "$@"
