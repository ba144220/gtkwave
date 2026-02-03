#!/bin/bash
# Simple build script for read_signal example

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Building read_signal example..."

# Check if GTKWave is built
if [ ! -d "../build" ]; then
    echo -e "${RED}Error: GTKWave build directory not found${NC}"
    echo "Please build GTKWave first:"
    echo "  cd .."
    echo "  meson setup build"
    echo "  ninja -C build"
    exit 1
fi

# Get the necessary flags from pkg-config
GLIB_CFLAGS=$(pkg-config --cflags glib-2.0 gobject-2.0)
GLIB_LIBS=$(pkg-config --libs glib-2.0 gobject-2.0)

# Compiler and flags
CC=${CC:-gcc}
CFLAGS="-Wall -Wextra -g"
INCLUDES="-I../lib/libgtkwave/src -I../build -I../build/lib/libgtkwave/src"
LDFLAGS="-L../build/lib/libgtkwave/src -lgtkwave"

# Build command
echo "Compiling read_signal.c..."
$CC $CFLAGS $INCLUDES $GLIB_CFLAGS read_signal.c -o read_signal $LDFLAGS $GLIB_LIBS

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo ""
    echo "Run with:"
    echo "  ./read_signal"
    echo ""
    echo "Or with a custom VCD file:"
    echo "  ./read_signal path/to/your/file.vcd"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
