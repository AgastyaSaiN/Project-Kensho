import sys
import os

# Ensure we have the absolute path to the directory containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Insert at the beginning of sys.path to prioritize local modules
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from kensho.app import main

if __name__ == '__main__':
    main()
