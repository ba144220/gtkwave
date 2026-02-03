/*
    This is a simple C program that reads signals from waveform files.
    
    It demonstrates:
    - Loading waveform files using GTKWave's libgtkwave
      * Supports VCD, FST, and GHW formats (auto-detected)
    - Looking up signals by hierarchical name
    - Reading signal values at specific times
    - Working with both scalar (1-bit) and vector (multi-bit) signals
    
    Usage:
      ./read_signal [filename]
    
    Examples:
      ./read_signal                    # Uses default VCD file
      ./read_signal waves.fst          # Read FST file
      ./read_signal dump.vcd.gz        # Read compressed VCD
*/

#include <stdio.h>
#include <stdlib.h>
#include <gtkwave.h>

// Helper function to find the history entry at or before the given time
static GwHistEnt *find_value_at_time(GwNode *node, GwTime time)
{
    // Walk the linked list to find the value at or before the requested time
    GwHistEnt *current = &node->head;
    GwHistEnt *result = NULL;
    
    // Find the last entry where entry->time <= time
    while (current != NULL && current->time <= time) {
        result = current;
        current = current->next;
    }
    
    return result;
}

// Helper function to print scalar signal value
static void print_scalar_value(GwHistEnt *hist)
{
    if (hist == NULL) {
        printf("X");
        return;
    }
    
    printf("%c", gw_bit_to_char(hist->v.h_val));
}

// Helper function to print vector signal value
static void print_vector_value(GwNode *node, GwHistEnt *hist)
{
    if (hist == NULL || hist->time < 0) {
        printf("X");
        return;
    }
    
    int width = abs(node->msi - node->lsi) + 1;
    
    // Convert binary to decimal for easier reading
    unsigned long long value = 0;
    for (int i = 0; i < width; i++) {
        if (hist->v.h_vector[i] == GW_BIT_1) {
            value |= (1ULL << (width - 1 - i));
        }
    }
    
    printf("%llu", value);
}

int main(int argc, char **argv)
{
    const char *filename = "./tests/basic.vcd";
    
    if (argc > 1) {
        filename = argv[1];
    }
    
    printf("Reading waveform file: %s\n", filename);
    printf("=====================================\n\n");
    
    // Determine file type based on extension and create appropriate loader
    GwLoader *loader = NULL;
    const char *file_type = NULL;
    
    if (g_str_has_suffix(filename, ".fst")) {
        loader = gw_fst_loader_new();
        file_type = "FST";
    } else if (g_str_has_suffix(filename, ".vcd") || g_str_has_suffix(filename, ".vcd.gz")) {
        loader = gw_vcd_loader_new();
        file_type = "VCD";
    } else if (g_str_has_suffix(filename, ".ghw")) {
        loader = gw_ghw_loader_new();
        file_type = "GHW";
    } else {
        fprintf(stderr, "Error: Unsupported file format\n");
        fprintf(stderr, "Supported formats: .fst, .vcd, .vcd.gz, .ghw\n");
        return 1;
    }
    
    if (loader == NULL) {
        fprintf(stderr, "Error: Failed to create %s loader\n", file_type);
        return 1;
    }
    
    printf("Detected format: %s\n", file_type);
    
    // Load the waveform file
    GError *error = NULL;
    GwDumpFile *dump_file = gw_loader_load(loader, filename, &error);
    g_object_unref(loader);
    
    if (dump_file == NULL) {
        fprintf(stderr, "Error: Failed to load %s file: %s\n", 
                file_type,
                error ? error->message : "unknown error");
        if (error) g_error_free(error);
        return 1;
    }
    
    printf("✓ %s file loaded successfully\n", file_type);
    
    // Import all traces (need to import twice for aliases as mentioned in dump.c)
    if (!gw_dump_file_import_all(dump_file, &error)) {
        fprintf(stderr, "Error: Failed to import traces: %s\n", 
                error ? error->message : "unknown error");
        if (error) g_error_free(error);
        g_object_unref(dump_file);
        return 1;
    }
    
    if (!gw_dump_file_import_all(dump_file, &error)) {
        fprintf(stderr, "Error: Failed to import traces (2nd pass): %s\n", 
                error ? error->message : "unknown error");
        if (error) g_error_free(error);
        g_object_unref(dump_file);
        return 1;
    }
    
    printf("✓ Traces imported successfully\n\n");
    
    // Get time range
    GwTimeRange *time_range = gw_dump_file_get_time_range(dump_file);
    GwTime start_time = gw_time_range_get_start(time_range);
    GwTime end_time = gw_time_range_get_end(time_range);
    
    printf("Time range: %lld to %lld\n", (long long)start_time, (long long)end_time);
    printf("Time scale: %lld\n", (long long)gw_dump_file_get_time_scale(dump_file));
    printf("\n");
    
    // List all available signals
    printf("Available signals:\n");
    GwFacs *facs = gw_dump_file_get_facs(dump_file);
    guint num_facs = gw_facs_get_length(facs);
    printf("Total: %u signals\n", num_facs);
    for (guint i = 0; i < num_facs && i < 20; i++) {
        GwSymbol *symbol = gw_facs_get(facs, i);
        printf("  [%u] %s\n", i, symbol->name);
    }
    printf("\n");
    
    // Look up signals
    GwSymbol *clk_symbol = gw_dump_file_lookup_symbol(dump_file, "tb.clk");
    GwSymbol *cycle_symbol = gw_dump_file_lookup_symbol(dump_file, "tb.cycle[7:0]");
    
    if (clk_symbol == NULL) {
        fprintf(stderr, "Error: Could not find signal 'tb.clk'\n");
        g_object_unref(dump_file);
        return 1;
    }
    
    if (cycle_symbol == NULL) {
        fprintf(stderr, "Error: Could not find signal 'tb.cycle'\n");
        g_object_unref(dump_file);
        return 1;
    }
    
    printf("✓ Found signal: %s\n", clk_symbol->name);
    printf("✓ Found signal: %s\n", cycle_symbol->name);
    printf("\n");
    
    // Get the nodes
    GwNode *clk_node = clk_symbol->n;
    GwNode *cycle_node = cycle_symbol->n;
    
    printf("Signal Info:\n");
    printf("  clk:   %d transitions\n", clk_node->numhist);
    printf("  cycle: %d transitions, width=%d bits [%d:%d]\n", 
           cycle_node->numhist, 
           abs(cycle_node->msi - cycle_node->lsi) + 1,
           cycle_node->msi, cycle_node->lsi);
    printf("\n");
    
    // Read and print signal values at different time points
    printf("Signal Values:\n");
    printf("Time | clk | cycle\n");
    printf("-----|-----|------\n");
    
    for (GwTime t = 0; t <= 30; t += 5) {
        GwHistEnt *clk_hist = find_value_at_time(clk_node, t);
        GwHistEnt *cycle_hist = find_value_at_time(cycle_node, t);
        
        printf("%4lld |  ", (long long)t);
        print_scalar_value(clk_hist);
        printf("  |  ");
        print_vector_value(cycle_node, cycle_hist);
        printf("\n");
    }
    
    printf("\n");
    
    // Demonstrate reading specific values (like the Python API you want)
    printf("Example: Reading specific values\n");
    printf("=====================================\n");
    
    GwTime query_time = 7;
    GwHistEnt *clk_at_7 = find_value_at_time(clk_node, query_time);
    GwHistEnt *cycle_at_7 = find_value_at_time(cycle_node, query_time);
    
    printf("At time %lld:\n", (long long)query_time);
    printf("  tb.clk = ");
    print_scalar_value(clk_at_7);
    printf("\n");
    printf("  tb.cycle = ");
    print_vector_value(cycle_node, cycle_at_7);
    printf("\n\n");
    
    // Another example
    query_time = 20;
    GwHistEnt *clk_at_20 = find_value_at_time(clk_node, query_time);
    GwHistEnt *cycle_at_20 = find_value_at_time(cycle_node, query_time);
    
    printf("At time %lld:\n", (long long)query_time);
    printf("  tb.clk = ");
    print_scalar_value(clk_at_20);
    printf("\n");
    printf("  tb.cycle = ");
    print_vector_value(cycle_node, cycle_at_20);
    printf("\n");
    
    // Clean up
    g_object_unref(dump_file);
    
    printf("\n✓ Done!\n");
    return 0;
}
