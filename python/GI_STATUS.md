# GTKWave Python GObject Introspection - Status Report

## Summary

GTKWave **already has GObject Introspection support built-in**. The minimal first step to wrap the C program with Python GI is partially working, but there's a critical segfault issue preventing object creation.

## What Works ✓

1. **Build with Introspection**: GTKWave builds with GObject Introspection enabled

   ```bash
   meson configure build | grep introspection
   # Output: introspection = true
   ```

2. **GIR and TypeLib files generated**: `Gw-1.gir` and `Gw-1.typelib` exist in `build/lib/libgtkwave/src/`

3. **Module imports successfully** in Python:

   ```python
   import gi
   gi.require_version('Gw', '1')
   from gi.repository import Gw
   # SUCCESS: <IntrospectionModule 'Gw' from '.../Gw-1.typelib'>
   ```

4. **Namespace inspection** works:
   - Can list all classes: `VcdLoader`, `FstLoader`, `GhwLoader`, `DumpFile`, etc.
   - Can access enums: `Gw.Bit`
   - Can list functions: `bit_from_char`, `bit_to_char`, etc.

## What Doesn't Work ✗

**Creating any GObject instance causes a segmentation fault:**

```python
loader = Gw.VcdLoader.new()  # SEGFAULT (exit code 139)
```

This affects ALL loader types:

- `Gw.VcdLoader.new()` → segfault
- `Gw.FstLoader.new()` → segfault
- `Gw.GhwLoader.new()` → segfault

## Investigation Done

1. ✓ Verified C program works with `DYLD_LIBRARY_PATH` set
2. ✓ Confirmed symbols are exported (`gw_vcd_loader_new`, `gw_vcd_loader_get_type`)
3. ✓ Checked GIR file - constructor definitions look correct
4. ✓ Tested with GLib/GObject initialization - still segfaults
5. ✓ Verified Python 3.11.14 and PyGObject 3.54.5 (both current)

## Hypothesis

The segfault likely occurs during:

- GObject type registration when first accessed from Python GI
- Symbol resolution or linking issue specific to dynamic loading via GI
- Possible ABI mismatch or missing initialization in the library

## Minimal Working Example

**File**: `python/test_minimal.py`

```python
#!/usr/bin/env python3
import sys
import gi

gi.require_version('Gw', '1')
from gi.repository import Gw

print(f"SUCCESS: {Gw}")
print(f"Available loaders: {[a for a in dir(Gw) if 'Loader' in a]}")
```

**Run with**:

```bash
mamba activate gtkwave
./python/run_gi.sh python/test_minimal.py
```

**Expected Output**:

```
SUCCESS: <IntrospectionModule 'Gw' from '.../Gw-1.typelib'>
Available loaders: ['FstLoader', 'GhwLoader', 'Loader', 'VcdLoader']
```

## Files Created

1. `python/run_gi.sh` - Wrapper script that sets `GI_TYPELIB_PATH` and `DYLD_LIBRARY_PATH`
2. `python/test_minimal.py` - Minimal import test (works)
3. `python/test_loader.py` - Loader creation test (segfaults)
4. `python/read_signal.py` - Full Python implementation (incomplete due to segfault)

## Next Steps to Fix

1. **Debug the segfault** with lldb/gdb to get a stack trace
2. **Check if library needs proper installation** instead of running from build dir
3. **Verify rpath settings** - library currently uses `@rpath/libgtkwave.dylib`
4. **Check for missing global initialization** in libgtkwave
5. **Test on Linux** - may be macOS-specific DYLD issue
6. **Review GTKWave build options** - check if special flags needed for GI

## Alternative Approach

If GI continues to fail, consider using **ctypes** or **cffi** instead:

- Direct C function calls without GObject overhead
- More manual but potentially more reliable
- Would require writing Python wrapper classes manually

## Usage (Once Fixed)

The intended Python API would be:

```python
import gi
gi.require_version('Gw', '1')
from gi.repository import Gw

# Load waveform file
loader = Gw.VcdLoader.new()  # Currently segfaults here
dump_file = loader.load("test.vcd")

# Import traces
dump_file.import_all()
dump_file.import_all()  # Twice for aliases

# Get time range
time_range = dump_file.get_time_range()
start = time_range.get_start()
end = time_range.get_end()

# Look up signals
symbol = dump_file.lookup_symbol("tb.clk")
node = symbol.n

# Access signal data...
```

This matches the C API almost 1:1 thanks to GObject Introspection.
