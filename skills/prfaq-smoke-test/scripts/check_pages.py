#!/usr/bin/env python3
"""Check the smoke-test pages before launch.

  check_pages.py a.html b.html c.html

1. structure (standard library): the files are identical outside the
   `angle` JSON block, and each angle has its own variant id.
2. events (needs Playwright): each page, opened headless, fires view,
   cta_click, and signup with its own variant id after a real click and a
   test email. The email appears only in requests to product.endpoint.
   Every POST the page sends is intercepted and answered locally, so no
   test event reaches real storage.

Prints one line per check: PASS, FAIL, or UNVERIFIED.
Exit 0 only when both pass; 1 on any FAIL; 2 when events are UNVERIFIED
because Playwright is missing.

The event check relies on the template's element ids: #cta, #door,
#door-email, #door-thanks. Keep them if you restyle the template.
"""

import functools
import http.server
import json
import pathlib
import re
import sys
import threading

ANGLE = re.compile(r'(<script type="application/json" id="angle">)(.*?)(</script>)', re.S)
PRODUCT = re.compile(r'<script type="application/json" id="product">(.*?)</script>', re.S)
TEST_EMAIL = "check@example.invalid"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def structure(paths):
    """Return (ok, message, pages) where pages maps path -> variant id."""
    outside, pages = {}, {}
    for p in paths:
        text = p.read_text(encoding="utf-8")
        m = ANGLE.search(text)
        if not m:
            return False, f"{p.name}: no angle block", pages
        try:
            angle = json.loads(m.group(2))
        except json.JSONDecodeError as e:
            return False, f"{p.name}: angle block is not valid JSON ({e})", pages
        pages[p] = str(angle.get("variant", ""))
        outside[p] = text[:m.start(2)] + text[m.end(2):]

    first = paths[0]
    for p in paths[1:]:
        if outside[p] != outside[first]:
            a, b = outside[first].splitlines(), outside[p].splitlines()
            line = next((i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)) + 1)
            return False, f"{p.name} differs from {first.name} outside the angle block (near line {line} of the file without its angle block)", pages

    ids = list(pages.values())
    if any(not v for v in ids):
        return False, "an angle block has no variant id", pages
    if len(set(ids)) != len(ids):
        return False, f"variant ids repeat: {', '.join(ids)}", pages
    return True, f"{len(paths)} pages identical outside the angle block; variants {', '.join(ids)}", pages


def endpoint_of(path):
    m = PRODUCT.search(path.read_text(encoding="utf-8"))
    try:
        return json.loads(m.group(1)).get("endpoint", "") if m else ""
    except json.JSONDecodeError:
        return ""


def events(pages):
    """Return (status, message) with status True, False, or None (unverified)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, ("Playwright is not installed (pip install playwright && playwright install chromium). "
                      "Check by hand as in references/landing-pages.md and record it in test-plan.md.")

    servers = {}
    for p in pages:
        root = p.parent.resolve()
        if root not in servers:
            handler = functools.partial(QuietHandler, directory=str(root))
            srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            servers[root] = srv

    problems, summary = [], []
    try:
        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch()
            except Exception as e:
                first = str(e).strip().splitlines()[0] if str(e).strip() else type(e).__name__
                return None, (f"Playwright could not start Chromium ({first}). Run: playwright install chromium. "
                              "Or check by hand as in references/landing-pages.md and record it in test-plan.md.")
            for p, variant in pages.items():
                posts, errors = [], []
                ctx = browser.new_context()
                page = ctx.new_page()
                page.on("pageerror", lambda e: errors.append(str(e)))

                def intercept(route, request, posts=posts):
                    if request.method == "POST":
                        try:
                            posts.append(json.loads(request.post_data or "{}"))
                        except json.JSONDecodeError:
                            posts.append({"raw": request.post_data})
                        route.fulfill(status=204)
                    else:
                        route.continue_()

                page.route("**/*", intercept)
                port = servers[p.parent.resolve()].server_address[1]
                page.goto(f"http://127.0.0.1:{port}/{p.name}?utm_source=internal")
                page.click("#cta")
                door_open = page.evaluate("document.getElementById('door').open")
                page.fill("#door-email", TEST_EMAIL)
                page.click("#door button[type=submit]")
                page.wait_for_timeout(500)
                thanks = page.is_visible("#door-thanks")
                fired = page.evaluate("window.__smokeEvents || []")
                ctx.close()

                name = p.name
                seq = [e.get("event") for e in fired]
                if seq != ["view", "cta_click", "signup"]:
                    problems.append(f"{name}: events {seq}, expected view, cta_click, signup")
                if any(e.get("variant") != variant for e in fired):
                    problems.append(f"{name}: an event carries a variant other than '{variant}'")
                if not door_open:
                    problems.append(f"{name}: the CTA did not open the fake-door panel")
                if not thanks:
                    problems.append(f"{name}: no thank-you after submitting the email")
                if any(TEST_EMAIL in json.dumps(e) for e in fired):
                    problems.append(f"{name}: the email is in window.__smokeEvents (it may reach analytics)")
                if errors:
                    problems.append(f"{name}: page errors {errors}")
                if endpoint_of(p):
                    kinds = sorted(x.get("event", "?") for x in posts)
                    if kinds != ["cta_click", "signup", "view"]:
                        problems.append(f"{name}: endpoint got {kinds}, expected view, cta_click, signup")
                    leaked = [x.get("event") for x in posts if x.get("event") != "signup" and TEST_EMAIL in json.dumps(x)]
                    if leaked:
                        problems.append(f"{name}: email sent with {leaked}")
                    if not any(x.get("event") == "signup" and x.get("email") == TEST_EMAIL for x in posts):
                        problems.append(f"{name}: the signup post to the endpoint has no email")
                    summary.append(f"{variant}: {len(posts)} posts intercepted")
                else:
                    summary.append(f"{variant}: no endpoint set, nothing sent")
            browser.close()
    finally:
        for srv in servers.values():
            srv.shutdown()

    if problems:
        return False, "; ".join(problems)
    return True, "each page fired view → cta_click → signup with its own variant; " + "; ".join(summary)


def main(argv):
    if len(argv) < 2 or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv and argv[0] in ("-h", "--help") else 1
    paths = [pathlib.Path(a) for a in argv]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        print(f"error: not found: {', '.join(missing)}")
        return 1

    ok, msg, pages = structure(paths)
    print(f"structure: {'PASS' if ok else 'FAIL'} — {msg}")
    if not ok:
        print("events: SKIPPED — fix the structure first")
        return 1

    status, msg = events(pages)
    label = {True: "PASS", False: "FAIL", None: "UNVERIFIED"}[status]
    print(f"events: {label} — {msg}")
    return {True: 0, False: 1, None: 2}[status]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
