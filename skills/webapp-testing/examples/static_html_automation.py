from playwright.sync_api import sync_playwright
from pathlib import Path

# Example: Automating a LOCAL static HTML file with a file:// URL.
# No server needed — ideal for HTML monoliths (portales, academias, dashboards).

# Resolve a local .html to an absolute file:// URI
html_path = Path('./index.html').resolve()   # Replace with your file
url = html_path.as_uri()                      # -> file:///abs/path/index.html

console_logs = []
page_errors = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 390, 'height': 844})  # mobile-first

    page.on("console", lambda m: console_logs.append(f"[{m.type}] {m.text}"))
    page.on("pageerror", lambda e: page_errors.append(str(e)))

    page.goto(url)
    page.wait_for_load_state('networkidle')  # let inline JS run

    # Inspect what's on the page
    print(f"Title: {page.title()}")
    buttons = page.locator('button:visible').all()
    print(f"Visible buttons: {len(buttons)}")

    # Smoke test: click each visible button and watch for exceptions
    for i, btn in enumerate(buttons):
        before = len(page_errors)
        try:
            btn.click(timeout=2000)
            page.wait_for_timeout(400)
            if len(page_errors) > before:
                print(f"  ✗ button[{i}] threw: {page_errors[-1]}")
        except Exception as e:
            print(f"  ✗ button[{i}] click failed: {e}")

    page.screenshot(path='inspect.png', full_page=True)
    browser.close()

print(f"\nConsole messages: {len(console_logs)} | Uncaught exceptions: {len(page_errors)}")
for e in page_errors:
    print(f"  EXCEPTION: {e.splitlines()[0]}")
print("Screenshot: inspect.png")
