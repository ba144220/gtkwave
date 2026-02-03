"""
Doing the same thing as read_signal.c, but in Python.
"""

import sys
import gi

gi.require_version('Gw', '1')
from gi.repository import Gw # pylint: disable=all

def main():
  print(Gw)
  return 0

if __name__ == '__main__':
  sys.exit(main())