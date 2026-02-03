#!/usr/bin/env python3
"""
Programmatically click 'Log in with GitHub' on Render login page.
Run this so the browser opens Render login and clicks the GitHub button; you complete auth in the window.
"""
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Install: pip install playwright && playwright install chromium")
    exit(1)

RENDER_LOGIN = "https://dashboard.render.com/login"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()
        page.goto(RENDER_LOGIN, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(1500)
        # Click "Log in with GitHub" using XPath (reliable across DOM changes)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
            page.wait_for_timeout(2000)
            # XPath: button containing "GitHub" text, or link with github in href
            xpaths = [
                "xpath=//button[contains(., 'GitHub')]",
                "xpath=//button[contains(normalize-space(), 'GitHub')]",
                "xpath=//a[contains(@href, 'github')]",
                "xpath=//*[contains(text(), 'GitHub') and (self::a or self::button)]",
            ]
            clicked = False
            for xp in xpaths:
                btn = page.locator(xp).first
                if btn.count():
                    btn.click(timeout=5000)
                    print("Clicked Log in with GitHub (XPath). Complete auth in the browser.")
                    clicked = True
                    break
            if not clicked:
                print("GitHub button not found by XPath. Manually click it in the open window.")
            page.wait_for_timeout(5000)
        except Exception as e:
            print("Click failed:", e)
            print("Manually click 'Log in with GitHub' in the open window.")
            page.wait_for_timeout(10000)
        browser.close()
    return 0

if __name__ == "__main__":
    exit(main())
