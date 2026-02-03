# GTKWave Waveform Reader Example

This is a simple C program that demonstrates how to use GTKWave's `libgtkwave` library to read waveform files programmatically (without the UI).

## What it does

The `read_signal.c` program:
- **Loads multiple waveform formats**: VCD, FST, GHW (auto-detected by file extension)
- Looks up signals by hierarchical name (e.g., "tb.clk", "tb.cycle")
- Reads signal values at specific time points
- Demonstrates both scalar (1-bit) and vector (multi-bit) signals

## Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| **VCD** | `.vcd`, `.vcd.gz` | Value Change Dump (text-based, widely supported) |
| **FST** | `.fst` | Fast Signal Trace (binary, compressed, very fast) |
| **GHW** | `.ghw` | GHDL Waveform (VHDL simulator output) |

## Building

### Option 1: Using Meson (Recommended)

First, build GTKWave's libgtkwave:

```bash
# From the root GTKWave directory
meson setup build
ninja -C build
```

Then build this example:

```bash
cd python
./build.sh
```

### Option 2: Using Makefile

If you have GTKWave already built:

```bash
cd python
make
```

**Note:** You may need to adjust the paths in the Makefile to point to your GTKWave build directory.

## Running

On macOS:
```bash
DYLD_LIBRARY_PATH=../build/lib/libgtkwave/src:$DYLD_LIBRARY_PATH ./read_signal
```

On Linux:
```bash
LD_LIBRARY_PATH=../build/lib/libgtkwave/src:$LD_LIBRARY_PATH ./read_signal
```

Or specify a different waveform file (any supported format):

```bash
DYLD_LIBRARY_PATH=../build/lib/libgtkwave/src:$DYLD_LIBRARY_PATH ./read_signal path/to/your/waveform.fst
```

Or use the helper script:

```bash
./run.sh                          # Uses default VCD file
./run.sh tests/basic.fst          # Use FST file
./run.sh path/to/your/wave.vcd    # Use any file
```

**Tip:** You can also install libgtkwave to a system location to avoid setting the library path.

## Example Output

### VCD File
```
Reading waveform file: ./tests/basic.vcd
=====================================

Detected format: VCD
✓ VCD file loaded successfully
✓ Traces imported successfully

Time range: 0 to 30
Time scale: 1

Available signals:
Total: 2 signals
  [0] tb.clk
  [1] tb.cycle[7:0]

✓ Found signal: tb.clk
✓ Found signal: tb.cycle[7:0]

Signal Info:
  clk:   31 transitions
  cycle: 31 transitions, width=8 bits [7:0]

Signal Values:
Time | clk | cycle
-----|-----|------
   0 |  1  |  0
   5 |  0  |  2
  10 |  1  |  5
  15 |  0  |  7
  20 |  1  |  10
  25 |  0  |  12
  30 |  1  |  15

Example: Reading specific values
=====================================
At time 7:
  tb.clk = 0
  tb.cycle = 3

At time 20:
  tb.clk = 1
  tb.cycle = 10

✓ Done!
```

### FST File
```
Reading waveform file: tests/basic.fst
=====================================

Detected format: FST
✓ FST file loaded successfully
✓ Traces imported successfully

Time range: 0 to 30
Time scale: 1
...
```

## API Usage

The key steps for reading waveform data:

```c
// 1. Create a loader based on file type (auto-detect by extension)
GwLoader *loader = NULL;
if (g_str_has_suffix(filename, ".fst")) {
    loader = gw_fst_loader_new();
} else if (g_str_has_suffix(filename, ".vcd") || g_str_has_suffix(filename, ".vcd.gz")) {
    loader = gw_vcd_loader_new();
} else if (g_str_has_suffix(filename, ".ghw")) {
    loader = gw_ghw_loader_new();
}

// 2. Load the file
GwDumpFile *dump_file = gw_loader_load(loader, filename, &error);

// 3. Import traces (twice for aliases)
gw_dump_file_import_all(dump_file, &error);
gw_dump_file_import_all(dump_file, &error);

// 4. Look up a signal by name
GwSymbol *symbol = gw_dump_file_lookup_symbol(dump_file, "tb.clk");
GwNode *node = symbol->n;

// 5. Find value at a specific time
// Method 1: Walk the linked list (simple, works for all cases)
GwHistEnt *current = &node->head;
GwHistEnt *result = NULL;
while (current != NULL && current->time <= time) {
    result = current;
    current = current->next;
}

// Method 2: Use binary search (faster, but requires harray to be built)
// See src/bsearch.c bsearch_node() function for the full implementation
// This is what GTKWave uses internally for better performance

// 6. Extract the value
if (node->msi == node->lsi) {
    // Scalar signal (1-bit)
    char value = gw_bit_to_char(hist->v.h_val);
} else {
    // Vector signal (multi-bit)
    char *vector = hist->v.h_vector;  // array of GwBit values
    int width = abs(node->msi - node->lsi) + 1;
}
```

### Performance Notes

- **Linked List Traversal**: O(n) where n is the number of transitions. Simple and always works.
- **Binary Search** (using `harray`): O(log n). Much faster for signals with many transitions, but requires the sorted array to be built first.

For production code, you'd want to use the binary search approach from `src/bsearch.c:bsearch_node()` or build the `harray` yourself.

## For Python Bindings

This C code can serve as a reference for creating Python bindings. The Python API you want:

```python
wv = GTKWave("waves.fst")
t = 100
value = wv.read_signal_value("dut.input", t)
```

Can be implemented by wrapping the C functions shown here using:
- [ctypes](https://docs.python.org/3/library/ctypes.html) - pure Python, no compilation
- [pybind11](https://pybind11.readthedocs.io/) - C++ wrapper, clean API
- [Cython](https://cython.org/) - Python/C hybrid
- [CFFI](https://cffi.readthedocs.io/) - C Foreign Function Interface

## Test VCD File

The `tests/basic.vcd` file contains:
- `tb.clk`: 1-bit clock signal that toggles every time unit
- `tb.cycle`: 8-bit counter that increments every 2 time units

See `tests/README.md` for more details.
