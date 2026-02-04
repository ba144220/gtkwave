"""
Python binding for GTKWave's libgtkwave using ctypes.
Replicates the functionality of read_signal.c
"""

import sys
import ctypes
from ctypes import c_void_p, c_char_p, c_int, c_longlong, c_uint, c_uint8, c_char, POINTER, Structure
import os

# Define GwTime type
GwTime = c_longlong

# GwBit enum values
GW_BIT_0 = 0
GW_BIT_X = 1
GW_BIT_Z = 2
GW_BIT_1 = 3
GW_BIT_H = 4
GW_BIT_U = 5
GW_BIT_W = 6
GW_BIT_L = 7
GW_BIT_DASH = 8

# Define C structures
class GwHistEntValue(ctypes.Union):
    _fields_ = [
        ("h_val", c_uint8),
        ("h_vector", c_void_p),  # Use void pointer instead of char pointer
        ("h_double", ctypes.c_double),
    ]

class GwHistEnt(Structure):
    pass

GwHistEnt._fields_ = [
    ("next", POINTER(GwHistEnt)),
    ("v", GwHistEntValue),
    ("time", GwTime),
    ("flags", c_uint8),
]

class GwNode(Structure):
    _fields_ = [
        ("expansion", c_void_p),
        ("nname", c_char_p),
        ("head", GwHistEnt),
        ("curr", POINTER(GwHistEnt)),
        ("harray", c_void_p),
        ("mv", c_void_p),
        ("msi", c_int),
        ("lsi", c_int),
        ("numhist", c_int),
        # Bitfields and other fields omitted for simplicity
    ]

class GwSymbol(Structure):
    _fields_ = [
        ("sym_next", c_void_p),
        ("vec_root", c_void_p),
        ("vec_chain", c_void_p),
        ("name", c_char_p),
        ("n", POINTER(GwNode)),
        ("s_selected", c_char),
    ]

# Load the GTKWave library
lib_path = os.path.join(os.getcwd(), "build/lib/libgtkwave/src/libgtkwave.dylib")
try:
    libgtkwave = ctypes.CDLL(lib_path)
    print(f"✓ Loaded library: {lib_path}")
except OSError as e:
    print(f"✗ Failed to load library: {e}")
    sys.exit(1)

# Define C function signatures
# GwLoader* gw_vcd_loader_new(void)
libgtkwave.gw_vcd_loader_new.argtypes = []
libgtkwave.gw_vcd_loader_new.restype = c_void_p

# GwDumpFile* gw_loader_load(GwLoader *self, const gchar *filename, GError **error)
libgtkwave.gw_loader_load.argtypes = [c_void_p, c_char_p, c_void_p]
libgtkwave.gw_loader_load.restype = c_void_p

# void g_object_unref(gpointer object)
libgtkwave.g_object_unref.argtypes = [c_void_p]
libgtkwave.g_object_unref.restype = None

# gboolean gw_dump_file_import_all(GwDumpFile *self, GError **error)
libgtkwave.gw_dump_file_import_all.argtypes = [c_void_p, c_void_p]
libgtkwave.gw_dump_file_import_all.restype = c_int

# GwTimeRange* gw_dump_file_get_time_range(GwDumpFile *self)
libgtkwave.gw_dump_file_get_time_range.argtypes = [c_void_p]
libgtkwave.gw_dump_file_get_time_range.restype = c_void_p

# GwTime gw_time_range_get_start(GwTimeRange *self)
libgtkwave.gw_time_range_get_start.argtypes = [c_void_p]
libgtkwave.gw_time_range_get_start.restype = c_longlong

# GwTime gw_time_range_get_end(GwTimeRange *self)
libgtkwave.gw_time_range_get_end.argtypes = [c_void_p]
libgtkwave.gw_time_range_get_end.restype = c_longlong

# GwTime gw_dump_file_get_time_scale(GwDumpFile *self)
libgtkwave.gw_dump_file_get_time_scale.argtypes = [c_void_p]
libgtkwave.gw_dump_file_get_time_scale.restype = c_longlong

# GwFacs* gw_dump_file_get_facs(GwDumpFile *self)
libgtkwave.gw_dump_file_get_facs.argtypes = [c_void_p]
libgtkwave.gw_dump_file_get_facs.restype = c_void_p

# guint gw_facs_get_length(GwFacs *self)
libgtkwave.gw_facs_get_length.argtypes = [c_void_p]
libgtkwave.gw_facs_get_length.restype = c_uint

# GwSymbol* gw_facs_get(GwFacs *self, guint index)
libgtkwave.gw_facs_get.argtypes = [c_void_p, c_uint]
libgtkwave.gw_facs_get.restype = POINTER(GwSymbol)

# GwSymbol* gw_dump_file_lookup_symbol(GwDumpFile *self, const gchar *name)
libgtkwave.gw_dump_file_lookup_symbol.argtypes = [c_void_p, c_char_p]
libgtkwave.gw_dump_file_lookup_symbol.restype = POINTER(GwSymbol)

# char gw_bit_to_char(GwBit bit)
libgtkwave.gw_bit_to_char.argtypes = [c_uint8]
libgtkwave.gw_bit_to_char.restype = c_char

# Helper functions
def find_value_at_time(node, time):
    """Walk the linked list to find the value at or before the requested time"""
    current = ctypes.pointer(node.head)
    result = None
    
    while current and current.contents.time <= time:
        result = current
        current = current.contents.next
    
    return result

def print_scalar_value(hist):
    """Print scalar signal value"""
    if not hist:
        return "X"
    
    bit_val = hist.contents.v.h_val
    char_val = libgtkwave.gw_bit_to_char(bit_val)
    return char_val.decode('ascii') if isinstance(char_val, bytes) else chr(char_val)

def print_vector_value(node, hist):
    """Print vector signal value as decimal"""
    if not hist or hist.contents.time < 0:
        return "X"
    
    width = abs(node.msi - node.lsi) + 1
    value = 0
    
    # Check if h_vector pointer is valid
    if not hist.contents.v.h_vector:
        return "X"
    
    # Cast h_vector pointer to array of bytes
    h_vector_ptr = ctypes.cast(hist.contents.v.h_vector, POINTER(c_uint8))
    
    # Convert binary to decimal
    for i in range(width):
        bit = h_vector_ptr[i]
        if bit == GW_BIT_1:
            value |= (1 << (width - 1 - i))
    
    return str(value)

def main():
    filename = "./python/tests/basic.vcd"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    print(f"Reading waveform file: {filename}")
    print("=" * 37)
    print()
    
    # Create VCD loader
    loader = libgtkwave.gw_vcd_loader_new()
    if not loader:
        print("Error: Failed to create loader")
        return 1
    
    # Load the file
    filename_bytes = filename.encode('utf-8')
    dump_file = libgtkwave.gw_loader_load(loader, filename_bytes, None)
    libgtkwave.g_object_unref(loader)
    
    if not dump_file:
        print("Error: Failed to load file")
        return 1
    print("✓ VCD file loaded successfully")
    
    # Import traces (twice for aliases)
    libgtkwave.gw_dump_file_import_all(dump_file, None)
    libgtkwave.gw_dump_file_import_all(dump_file, None)
    print("✓ Traces imported successfully")
    
    # Get time range
    time_range = libgtkwave.gw_dump_file_get_time_range(dump_file)
    start_time = libgtkwave.gw_time_range_get_start(time_range)
    end_time = libgtkwave.gw_time_range_get_end(time_range)
    time_scale = libgtkwave.gw_dump_file_get_time_scale(dump_file)
    
    print(f"\nTime range: {start_time} to {end_time}")
    print(f"Time scale: {time_scale}")
    
    # List available signals
    print("\nAvailable signals:")
    facs = libgtkwave.gw_dump_file_get_facs(dump_file)
    num_facs = libgtkwave.gw_facs_get_length(facs)
    print(f"Total: {num_facs} signals")
    for i in range(min(num_facs, 20)):
        symbol = libgtkwave.gw_facs_get(facs, i)
        if symbol:
            print(f"  [{i}] {symbol.contents.name.decode('utf-8')}")
    
    # Look up specific signals
    print()
    clk_symbol = libgtkwave.gw_dump_file_lookup_symbol(dump_file, b"tb.clk")
    cycle_symbol = libgtkwave.gw_dump_file_lookup_symbol(dump_file, b"tb.cycle[7:0]")
    
    if not clk_symbol or not cycle_symbol:
        print("Error: Could not find signals")
        libgtkwave.g_object_unref(dump_file)
        return 1
    
    print(f"✓ Found signal: {clk_symbol.contents.name.decode('utf-8')}")
    print(f"✓ Found signal: {cycle_symbol.contents.name.decode('utf-8')}")
    
    # Get node information
    clk_node = clk_symbol.contents.n.contents
    cycle_node = cycle_symbol.contents.n.contents
    cycle_width = abs(cycle_node.msi - cycle_node.lsi) + 1
    
    print(f"\nSignal Info:")
    print(f"  clk:   {clk_node.numhist} transitions")
    print(f"  cycle: {cycle_node.numhist} transitions, width={cycle_width} bits [{cycle_node.msi}:{cycle_node.lsi}]")
    
    # Read signal values at different time points
    print("\nSignal Values:")
    print("Time | clk | cycle")
    print("-----|-----|------")
    
    for t in range(0, 31, 5):
        clk_hist = find_value_at_time(clk_node, t)
        cycle_hist = find_value_at_time(cycle_node, t)
        
        clk_val = print_scalar_value(clk_hist)
        cycle_val = print_vector_value(cycle_node, cycle_hist)
        
        print(f"{t:4d} |  {clk_val}  |  {cycle_val}")
    
    # Demonstrate reading specific values
    print("\nExample: Reading specific values")
    print("=" * 37)
    
    query_time = 7
    clk_at_7 = find_value_at_time(clk_node, query_time)
    cycle_at_7 = find_value_at_time(cycle_node, query_time)
    
    print(f"At time {query_time}:")
    print(f"  tb.clk = {print_scalar_value(clk_at_7)}")
    print(f"  tb.cycle = {print_vector_value(cycle_node, cycle_at_7)}")
    
    query_time = 20
    clk_at_20 = find_value_at_time(clk_node, query_time)
    cycle_at_20 = find_value_at_time(cycle_node, query_time)
    
    print(f"\nAt time {query_time}:")
    print(f"  tb.clk = {print_scalar_value(clk_at_20)}")
    print(f"  tb.cycle = {print_vector_value(cycle_node, cycle_at_20)}")
    
    # Clean up
    libgtkwave.g_object_unref(dump_file)
    print("\n✓ Done!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
