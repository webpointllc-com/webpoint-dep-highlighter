#!/usr/bin/env python3
"""
Visible browser test for DEP Highlighter.
Launches Chrome in headed mode so you see the window; drives dropzone, file, Process, success.
"""
import asyncio
from pathlib import Path

from playwright.sync_api import sync_playwright

DEPLOY_DIR = Path(__file__).resolve().parent
TEST_FILE = DEPLOY_DIR / "test_NY_NewYorkCity.xlsx"
if not TEST_FILE.exists():
    TEST_FILE = DEPLOY_DIR / "test_dep_input.xlsx"
URL = "https://webpoint-dep-highlighter.onrender.com"

def main():
    if not TEST_FILE.exists():
        print("Missing test file:", TEST_FILE)
        return 1
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        page.locator("#fileInput").set_input_files(str(TEST_FILE))
        page.wait_for_timeout(800)
        page.locator("#processBtn").click()
        try:
            page.locator("#successOverlay.active").wait_for(state="visible", timeout=45000)
            page.wait_for_timeout(2000)
            page.locator("#downloadBtn").click()
            page.wait_for_timeout(1500)
            print("SUCCESS. Check Downloads for the processed file.")
            result = 0
        except Exception as e:
            err_el = page.locator("#errorMessage.active")
            if err_el.count() > 0:
                err_text = err_el.text_content()
                print("FAILED - Error shown on page:", err_text)
            else:
                print("FAILED -", str(e))
            result = 1
        browser.close()
    return result

if __name__ == "__main__":
    exit(main())
