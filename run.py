import sys
import os

# Add src to path so we can import kensho package
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from kensho.app import main

if __name__ == '__main__':
    main()
