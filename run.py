import sys
import os

# Force UTF-8 encoding on standard output and error streams for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add the parent directory to the Python path so the backend package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import main

if __name__ == '__main__':
    main()
