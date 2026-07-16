import sys
import os

# Get the root task path dynamically provided by Vercel
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Force target directories straight into the core registry loop
backend_path = os.path.join(root_dir, "backend")
app_parent_path = os.path.join(root_dir, "backend", "app")

for path in [backend_path, app_parent_path, root_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import directly from the verified module paths
from backend.app.main import app

