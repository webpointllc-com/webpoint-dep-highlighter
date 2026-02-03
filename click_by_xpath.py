#!/usr/bin/env python3
"""
Click an element by XPath. Use when snapshot refs are missing or for reliable targeting.
Usage: python3 click_by_xpath.py <url> <xpath>
  e.g. python3 click_by_xpath.py "https://dashboard.render.com/login" "//button[contains(., 'GitHub')]"
"""
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Install: pip install playwright && playwright install chromium")
    sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 click_by_xpath.py <url> <xpath>")
        print('  e.g. python3 click_by_xpath.py "https://dashboard.render.com/login" "//button[contains(., \\'GitHub\\')]"')
        sys.exit(1)
    url, xpath = sys.argv[1], sys.argv[2]
    if not xpath.startswith("xpath=") and not xpath.startswith("//"):
        xpath = "xpath=" + xpath
    elif xpath.startswith("//"):
        xpath = "xpath=" + xpath
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        try:
            loc = page.locator(xpath).first
            if loc.count():
                loc.click(timeout=5000)
                print("Clicked element at XPath.")
            else:
                print("No element found for XPath.")
            page.wait_for_timeout(5000)
        except Exception as e:
            print("Error:", e)
        browser.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
