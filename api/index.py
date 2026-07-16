import sys
import os
from fastapi import FastAPI

# Locate the strict root environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_path = os.path.join(project_root, "backend")

# Inject paths into the system registry
for path in [backend_path, project_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import your underlying main application setup cleanly 
try:
    from app.main import app
except ImportError:
    # Fail-safe fall back to direct import if Vercel moves paths
    from backend.app.main import app as fallback_app
    app = fallback_app
