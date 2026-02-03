#!/usr/bin/env python3
"""
Scan screenshot for GitHub logo color (hex #000000, #232925).
Find regions with that color, map pixel coords to DOM element via elementFromPoint.
Requires: pip install pillow
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Install: pip install pillow")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Install: pip install playwright && playwright install chromium")
    sys.exit(1)

RENDER_LOGIN = "https://dashboard.render.com/login"
# GitHub logo on light bg: black #000000; brand dark gray #232925
TARGET_HEX = [
    (0, 0, 0),           # #000000
    (35, 41, 37),        # #232925
    (16, 20, 17),        # #101411
]
# Allow small tolerance (logo may be anti-aliased)
TOLERANCE = 25

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

def pixel_matches(rgb, target, tol):
    return all(abs(rgb[i] - target[i]) <= tol for i in range(3))

def find_dark_region_center(im, target_rgbs, tolerance, min_area=30):
    """Find a dark region (logo) in upper half; return center (x,y). Prefer leftmost (GitHub first)."""
    w, h = im.size
    if im.mode != "RGB":
        im = im.convert("RGB")
    pixels = im.load()
    best_center = None
    best_count = 0
    # Only scan upper half (login buttons); coarser step for speed
    step = 8
    patch = 16
    for y in range(0, min(h // 2, h - patch), step):
        for x in range(0, w - patch, step):
            count = 0
            for dy in range(patch):
                for dx in range(patch):
                    px = pixels[x + dx, y + dy]
                    for trgb in target_rgbs:
                        if pixel_matches(px, trgb, tolerance):
                            count += 1
                            break
            if count >= min_area and (best_center is None or x < best_center[0]):
                best_count = count
                best_center = (x + patch // 2, y + patch // 2)
                break
        if best_center is not None:
            break
    return best_center

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        page = browser.new_page()
        page.goto(RENDER_LOGIN, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(3000)

        out = Path(__file__).resolve().parent / "assets" / "scan_screenshot.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(out))
        im = Image.open(out)
        center = find_dark_region_center(im, TARGET_HEX, TOLERANCE, min_area=30)
        if center:
            x, y = center
            # Get element at that point (viewport coords)
            el_selector = page.evaluate(f"""() => {{
                const el = document.elementFromPoint({x}, {y});
                if (!el) return null;
                const btn = el.closest('button');
                return btn ? btn.tagName + (btn.textContent || '').trim().slice(0,20) : el.tagName;
            }}""")
            print(f"Color scan: dark region center ({x},{y}) -> element: {el_selector}")
            # Click at that point (often the logo is inside a button)
            page.mouse.click(x, y)
            page.wait_for_timeout(2000)
            if "github" in page.url.lower():
                print("Clicked; navigated to GitHub.")
            else:
                # Try clicking the button that contains this point
                page.evaluate(f"""() => {{
                    const el = document.elementFromPoint({x}, {y});
                    const btn = el ? el.closest('button') : null;
                    if (btn) btn.click();
                }}""")
                page.wait_for_timeout(2000)
                print("URL after:", page.url[:70])
        else:
            print("No dark region found; falling back to text/XPath.")
            btn = page.locator('button:has-text("GitHub")').first
            if btn.count():
                btn.click(timeout=5000)
                print("Clicked GitHub (text fallback).")
        browser.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
