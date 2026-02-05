#!/usr/bin/env python3
"""
Main app entry (dep_tool pattern): check Python, pip install -r requirements.txt, run main app.
"""
from dep_highlighter_server import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
