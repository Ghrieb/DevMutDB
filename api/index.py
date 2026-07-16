import os
import sys
from pathlib import Path

# Explicitly find the absolute backend path relative to this file
base_dir = Path(__file__).resolve().parent.parent
backend_path = os.path.join(base_dir, "backend")

# Insert both paths at the top of Python's lookup registry
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from app.main import app
