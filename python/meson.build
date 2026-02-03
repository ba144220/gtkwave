# Meson build file for the waveform reader example
# This integrates with GTKWave's main build system

project('gtkwave-reader-example', 'c',
  version : '1.0.0',
  default_options : ['warning_level=2']
)

# Dependencies
glib_dep = dependency('glib-2.0')
gobject_dep = dependency('gobject-2.0')

# Include directories
libgtkwave_inc = include_directories('../lib/libgtkwave/src')

# Link to the built libgtkwave
libgtkwave_dep = dependency('libgtkwave', 
  fallback : ['libgtkwave', 'libgtkwave_dep'],
  required : true
)

# Build the example executable
read_signal_exe = executable('read_signal',
  'read_signal.c',
  dependencies : [glib_dep, gobject_dep, libgtkwave_dep],
  include_directories : libgtkwave_inc,
  install : false
)

# Add a test that runs the example
test('read_signal_test', read_signal_exe,
  workdir : meson.current_source_dir()
)
