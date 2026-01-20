"""
WEB PORTAL RUNNER
=================
This is a wrapper to run the refactored web portal.
Original monolith web_dashboard.py has been split into the "web_portal" directory.
"""

import sys
import os

# Ensure the root directory is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from web_portal.app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
