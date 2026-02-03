# Makefile for building the read_signal example
# This demonstrates using GTKWave's libgtkwave to read waveform files

# Compiler
CC = gcc

# Program name
TARGET = read_signal

# Source files
SRCS = read_signal.c

# Object files
OBJS = $(SRCS:.c=.o)

# Get GTKWave library paths
# You'll need to adjust these paths based on your build
GTKWAVE_LIB_DIR = ../lib/libgtkwave/src
GTKWAVE_BUILD_DIR = ../build/lib/libgtkwave

# Include directories
INCLUDES = -I$(GTKWAVE_LIB_DIR) \
           -I$(GTKWAVE_BUILD_DIR)

# Libraries
LIBS = -L$(GTKWAVE_BUILD_DIR) -lgtkwave

# pkg-config for glib
GLIB_CFLAGS = $(shell pkg-config --cflags glib-2.0 gobject-2.0)
GLIB_LIBS = $(shell pkg-config --libs glib-2.0 gobject-2.0)

# Compiler flags
CFLAGS = -Wall -Wextra -g $(INCLUDES) $(GLIB_CFLAGS)

# Linker flags
LDFLAGS = $(LIBS) $(GLIB_LIBS)

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET) $(LDFLAGS)

# Compile source files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Run the program
run: $(TARGET)
	./$(TARGET)

# Clean build artifacts
clean:
	rm -f $(OBJS) $(TARGET)

# Run with valgrind for memory checking
valgrind: $(TARGET)
	valgrind --leak-check=full ./$(TARGET)

.PHONY: all run clean valgrind
