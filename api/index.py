import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from app.main import app
except ImportError:
    from backend.app.main import app as fallback_app
    app = fallback_app
