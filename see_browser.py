#!/usr/bin/env python3
"""
Capture browser view (screenshot) so the agent can "see" what's on the page.
Saves to workspace assets for OCR/vision: read the image to see buttons, text, etc.
Usage: python3 see_browser.py [url]
  If url omitted, captures https://dashboard.render.com/login
  Output: workspace assets/browser_view.png (or path you pass)
"""
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Install: pip install playwright && playwright install chromium")
    sys.exit(1)

# Save to deploy/assets so agent can read the image (OCR/vision)
WORKSPACE_ASSETS = Path(__file__).resolve().parent / "assets"
WORKSPACE_ASSETS.mkdir(parents=True, exist_ok=True)

DEFAULT_URL = "https://dashboard.render.com/login"
OUTPUT = WORKSPACE_ASSETS / "browser_view.png"

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(3000)
        out.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(out))
        browser.close()
    print("Screenshot:", out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
