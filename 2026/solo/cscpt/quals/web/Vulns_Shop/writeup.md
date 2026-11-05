---
title: Vulns Shop
date: '2026-06-20'
draft: false
authors: ['ang3l0']
tags: ['Web', 'SQL Injection', 'CTF']
summary: 'SQL injection in a webshop selling vulnerabilities'
canonical: ''
---

## Vulns Shop — CSCPT Quals 2026

**Category:** Web  
**Points:** 500  

### Source

No source provided. The application is a simple PHP webshop with MySQL backend:

- `products.php` — product listing + detail view
- `buy.php` — purchase endpoint  
- `dashboard.php` — user purchases
- `login.php` / `register.php` — authentication
- `config/auth.php` — session handling (includes)

The shop sells vulnerabilities: XSS (€25), SQL injection (€70), SSTI (€120), CSRF to RCE (€1,337), Uknown 0day (€1,337). Starting balance: €500.

### Solution

#### 1. Reconnaissance

The "View product detail" button sends:
```
GET /products.php?product_id_detail=1&product_column=name
```

Testing the `product_column` parameter reveals SQL errors with column names and file paths:
```
Unknown column 'test' in 'field list' in /var/www/html/products.php:68
```

The query template is:
```sql
SELECT `{input}` FROM products WHERE id = ?
```

Columns in `products` table: `id`, `name`, `description`, `price`, `stock`.

Product 5 (Uknown 0day) has description `------------`.

#### 2. SQL Injection Analysis

The input is backtick-quoted and escaped with backslashes (prevents backtick breakout). However, input containing `--` triggers a **different code path:**

| Input | Behavior |
|---|---|
| `name` | Normal: `SELECT \`name\` FROM products WHERE id = ?` → works |
| `` id` FROM products `` | Escaped: treated as literal column name → Unknown column |
| `` id` FROM products-- `` | Security path: WHERE clause removed → **Parameter mismatch** |
| `` id` FROM products WHERE id=?-- `` | Security path + `?`: param count matches → **MySQL syntax error near '?'** |

The security path:
1. Detects `--` in input
2. Removes `--` from the input  
3. Removes/disables backtick escaping (backtick now closes the identifier)
4. Removes the `WHERE` clause → 0 `?` placeholders
5. Still calls `execute([$id])` with 1 parameter → **mismatch**

Adding a `?` to the injection balances the parameter count (1 `?` total, 1 param), but **MySQL rejects `?` in every position tested** (SELECT list, WHERE clause, function arguments, subqueries).

#### 3. Security Path Triggers

The security path is triggered by BOTH `--` and `/*` in the input. Other sequences (`#`, `;`, single `-`, `*/`) do NOT trigger it:

| Input | Triggers Security Path? |
|---|---|
| `` id`-- `` | ✅ Yes |
| `` id`/* `` | ✅ Yes |
| `` id`# `` | ❌ No |
| `` id`; `` | ❌ No |
| `` id` - `` | ❌ No |

#### 4. Key Constraint

When the security path triggers:
- Backtick escaping is disabled → `` ` `` can close the identifier
- The `WHERE` clause is removed → 0 `?` placeholders  
- Code still calls `execute([$id])` with 1 parameter

This creates a catch-22:
- **Without `--`/`/*`**: cannot break out of backtick quoting → limited to reading existing columns
- **With `--`/`/*`**: can break out, but WHERE clause removed → 0 `?`s vs 1 param → **mismatch**
- **With `--`/`/*` + `?`**: param count matches (1 `?`, 1 param), but MySQL returns **"syntax error near '?'"** at execute time

The `?` rejection occurs in ALL positions tested (SELECT list, WHERE clause, function arguments, subqueries). Even simple `SELECT ?, ...` is rejected. The root cause appears to be that PDO is in emulated mode, replaces the `?` with the parameter value, and the resulting SQL has a structural issue that MySQL rejects.

#### 5. Current Blocker

The `?` placeholder in the security-path query is recognized by PDO (parameter count matches) but the query fails at MySQL level. This is the last piece needed — once resolved, UNION/subquery/`LOAD_FILE` all become available to extract the flag.

#### 4. Exploitation Strategy

The intended exploit chain likely involves:

1. **Break out of backtick quoting** using `` `-- `` to trigger the security path
2. **Inject a `?` placeholder** that MySQL accepts in the query context
3. **Extract data** via UNION, subqueries, or `LOAD_FILE()`
4. **Read flag** from other tables (`users`, `flags`, etc.) or filesystem

Once the `?` acceptance issue is resolved, the following payload structure should work:

```
id`,(SELECT password FROM users WHERE id=?)`name--
```

Which would produce:
```sql
SELECT `id`, (SELECT password FROM users WHERE id=?), `name` FROM products
```

#### 5. Notes

- No SSTI, LFI, or XSS vectors identified
- No race condition in buy functionality
- Registration/login use parameterized queries (no injection)
- `--` detection is the only way to break backtick escaping
- `#` comments do NOT trigger the security path
- PDO is used for database queries (PHP 8.3, MySQL via PDO)
