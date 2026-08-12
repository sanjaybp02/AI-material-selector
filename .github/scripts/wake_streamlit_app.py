"""Visits the deployed app like a real browser, not a bare HTTP client.

Why this exists: a plain `curl` GET only fetches the static HTML/JS
shell of a *.streamlit.app page - it never executes JavaScript, so it
never fires the app's actual "someone opened this app" signal
(POST /api/v1/app/event/open), which is what Streamlit Community Cloud
uses to reset its inactivity/sleep timer. An earlier version of this
workflow used curl, always reported "success" (it really was reaching
a genuine 200 on the static shell), and the app kept going to sleep
anyway - proven by testing: the curl-based ping's status check passing
said nothing about whether event/open ever fired or succeeded.

Playwright actually runs the page's JavaScript in a real browser
context, so event/open fires with the same cookies/session a genuine
visitor would have. Also handles the case where the app is already
asleep when this runs, by finding and clicking the real
"Yes, get this app back up!" button instead of just loading a page
that says the app needs a human to click something.
"""

import os
import sys

from playwright.sync_api import sync_playwright

# `or` (not .get(..., default)) deliberately: an unset APP_URL secret
# still gets threaded through by the workflow as an empty string, not
# omitted entirely - .get()'s default only kicks in for a truly
# missing key, so it would silently pass "" through instead of falling
# back here.
APP_URL = os.environ.get("APP_URL") or "https://ai-material-selector-sanjaybp.streamlit.app"
WAKE_BUTTON_TEXT = "Yes, get this app back up!"


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        responses = []
        page.on("response", lambda r: responses.append((r.request.method, r.url, r.status)))

        print(f"Navigating to {APP_URL} ...")
        try:
            page.goto(APP_URL, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"FAILED: could not load the app at all: {e}")
            browser.close()
            return 1

        page.wait_for_timeout(5000)
        print(f"Page title: {page.title()}")

        wake_btn = page.get_by_text(WAKE_BUTTON_TEXT, exact=False)
        if wake_btn.count() > 0:
            print("App was asleep - clicking the wake-up button...")
            wake_btn.first.click()
            page.wait_for_timeout(20000)
            print(f"Page title after wake attempt: {page.title()}")
        else:
            print("App was already awake.")

        open_event_calls = [r for r in responses if "/event/open" in r[1]]
        browser.close()

        if not open_event_calls:
            # Not necessarily fatal - it may only fire on certain
            # navigation paths - but worth knowing if it silently stops
            # appearing in a future Streamlit Cloud frontend change.
            print("NOTE: no /event/open call observed this run.")
            return 0

        ok = True
        for method, url, status in open_event_calls:
            print(f"{method} {status} {url}")
            if status >= 400:
                ok = False

        if ok:
            print("SUCCESS: app-open event registered cleanly.")
            return 0
        else:
            print("FAILED: app-open event was rejected (see status above).")
            return 1


if __name__ == "__main__":
    sys.exit(main())
