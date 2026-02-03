#!/usr/bin/env python3
"""
Find and click the GitHub button on Render login using:
- Logo image (img src/alt containing github)
- Logo color hex (#000000, #232925 - scan DOM for fill/color)
- Logo/button size (button ~110x36, icon ~20-24px)
"""
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Install: pip install playwright && playwright install chromium")
    sys.exit(1)

RENDER_LOGIN = "https://dashboard.render.com/login"

# GitHub logo colors (hex) - for DOM fill/color or image scan
GITHUB_LOGO_HEX = ("#000000", "#232925", "#101411", "#000", "rgb(0,0,0)", "rgb(35,41,37)")

def find_and_click_github(page, headless=True):
    page.goto(RENDER_LOGIN, wait_until="domcontentloaded", timeout=15000)
    page.wait_for_timeout(3000)

    # 1) By image: button containing img with github in src or alt
    sel_img = 'button:has(img[src*="github"]), button:has(img[alt*="GitHub"]), button:has(img[alt*="github"])'
    btn = page.locator(sel_img).first
    if btn.count():
        btn.click(timeout=5000)
        return "image (src/alt)"

    # 2) XPath: button containing img[src or alt contains github]
    xpath_img = '//button[.//img[contains(@src,"github") or contains(@alt,"GitHub") or contains(@alt,"github")]]'
    btn = page.locator(f"xpath={xpath_img}").first
    if btn.count():
        btn.click(timeout=5000)
        return "xpath image"

    # 3) By size: buttons ~80-150px wide, 30-50px tall; first one is usually GitHub
    buttons = page.locator("button").all()
    for b in buttons:
        try:
            box = b.bounding_box()
            if not box:
                continue
            w, h = box.get("width", 0), box.get("height", 0)
            if 80 <= w <= 150 and 30 <= h <= 50:
                # Check if it contains an image (logo)
                img = b.locator("img, svg").first
                if img.count():
                    b.click(timeout=5000)
                    return "size+logo"
                # First social-sized button with text "GitHub"
                text = b.text_content() or ""
                if "GitHub" in text:
                    b.click(timeout=5000)
                    return "size+text"
        except Exception:
            continue

    # 4) SVG with fill matching GitHub logo color (black/dark)
    xpath_svg = '//button[.//svg//*[contains(@fill,"000") or contains(@fill,"232925") or contains(@fill,"101411")]]'
    btn = page.locator(f"xpath={xpath_svg}").first
    if btn.count():
        btn.click(timeout=5000)
        return "svg fill"

    # 5) Fallback: first button with text "GitHub"
    btn = page.locator('button:has-text("GitHub")').first
    if btn.count():
        btn.click(timeout=5000)
        return "text"

    return None

def main():
    headless = "--headless" in sys.argv or "-q" in sys.argv
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, channel="chrome")
        page = browser.new_page()
        try:
            method = find_and_click_github(page, headless=headless)
            if method:
                print(f"Clicked GitHub button (method: {method}). URL after: {page.url[:70]}...")
            else:
                print("GitHub button not found.")
            page.wait_for_timeout(5000)
        except Exception as e:
            print("Error:", e)
        browser.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
