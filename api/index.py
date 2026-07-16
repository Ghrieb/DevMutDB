import os
import sys

# Locate the precise runtime server folder tree provided by Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, "backend")

# Bind all structural root lookups into the absolute top tier
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

# Import the direct sub-module explicitly
import backend.app.main as main_module
app = main_module.app
