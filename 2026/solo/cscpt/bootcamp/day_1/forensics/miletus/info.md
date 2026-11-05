# CTF Write-up — Obfuscated PowerShell Stager (`virus_ps1.txt`)

## TL;DR

A four-layer obfuscated PowerShell **stager** that disables Windows logging/scanning
(ETW + AMSI), decrypts an embedded **second-stage loader**, and runs it via
`Invoke-Expression`. The second stage is a **HWID-gated C2 downloader** that pulls an
AES-256-CBC + HMAC-SHA256 encrypted envelope from `gloason.com`, decrypts it, and
executes the resulting **WLDR agent** in memory. The family is **WLDR C2**, a bespoke
PowerShell C2 framework (Cisco Talos, actor **UAT-11795**).

---

## Answers

**1. URL where the scripts are invoked, including the password**

The script that is `Invoke-Expression`'d is fetched from the **validation URL**:

```
https://gloason.com/white/lrau20bdzx/<HWID>
Password: 16k3g6c0pwnj
```

(The sibling URL `https://gloason.com/white/0barysbi8b07/<HWID>` is *not* invoked
directly — it is stored in `$Global:WLDR_HTTP_URI` for the agent's later C2 beaconing,
using the same password `16k3g6c0pwnj` stored in `$Global:WLDR_ENC_PASSWORD`.)

**2. The unusual hexadecimal number appended to the URL**

The **hardware ID (HWID)** — the **C:\ volume serial number**. `Get-HWID` reads the
serial via the `Scripting.FileSystemObject` COM object, formats it as **hexadecimal**
with `"{0:X}" -f $SerialNumber`, then converts it back to a 64-bit integer with
`[convert]::toint64($SerialNumber,16)`. The hex round-trip is the "unusual" bit — the
value is derived through a hex representation before being appended to the URL.

**3. Standard padding syntax used for the encrypted data**

**PKCS7** — `[System.Security.Cryptography.PaddingMode]::PKCS7` (AES-256 in CBC mode).

**4. The two manually implemented functions used by the main cryptographic function**

The main cryptographic function is `Get-ValuePlain` (the envelope decryptor). The two
custom, hand-rolled crypto routines it relies on are:

```
PBKDF2SHA256_ConstEq
```

- `PBKDF2SHA256` — a manual PBKDF2-HMAC-SHA256 key-derivation implementation (used for
  key stretching instead of `Rfc2898DeriveBytes`).
- `ConstEq` — a constant-time byte-array comparison used to verify the HMAC tag.

(By definition order in the file it is `ConstEq_PBKDF2SHA256`; by order of use inside
`Get-ValuePlain` it is `PBKDF2SHA256_ConstEq`. The two trivial helpers `B64` and `B`
are just base64/UTF-8 wrappers, not cryptographic primitives.)

**5. How many variables does the function from Q2 use (counting repeats)**

`Get-HWID` uses **8** variable references (counting repeats): `$fso`, `$SerialNumber`,
`$fso`, `$SerialNumber`, `$SerialNumber`, `$SerialNumber`, `$SerialNumber`,
`$SerialNumber`. That's **2 unique** variables (`$fso`, `$SerialNumber`) referenced
**8 times** in total.

**6. Malware family**

**WLDR C2** — a bespoke/undocumented PowerShell command-and-control framework, named
after the actor's own project designation (`WLDR_*` globals, `WSv1` envelope tag).
Publicly documented by Cisco Talos and attributed to the financially motivated actor
**UAT-11795**, delivered alongside **Starland RAT** (with **CastleStealer** and
**Remcos RAT** as follow-on payloads).

---

## Obfuscation layers

| Layer | Technique | How it was undone |
|------|-----------|-------------------|
| 1 | Control-flow flattening: a `while + switch` state machine keyed on `$z0bufDgneqr_nbW8` | Reordered the cases by their state transitions |
| 2 | String building via ~7,100 `.Remove()`, ~5,530 `.Insert()`, ~573 `.Replace()`, plus `-f`, `-join`, `[string]::Concat` | Constant-folded the pure string ops (Python) — all side-effect-free |
| 3 | base64 → repeating-key XOR → base64 (the `wKHbqsr1Ft2R` helper) | Re-implemented the exact routine statically |
| 4 | base64 → GZip | `gzip.decompress` |

The obfuscation was fully resolved **statically** — the sample was never executed and
the C2 was never contacted.

### Layer 2 folding

All identifiers/type names/method names are constructed at runtime from `.NET`
`String` operations, e.g. `'_:RMUT:'.Insert(0,'suDnb').Insert(11,'Q:A')...` These are
pure functions, so evaluating them offline collapses **205 KB → ~5 KB** of readable
code with zero execution risk.

### Layer 3: the `wKHbqsr1Ft2R` crypto routine (deobfuscated)

```
wKHbqsr1Ft2R($input, $mode, $offset, $keyStr):
    enc = [Text.Encoding]::UTF8
    key = [BitConverter]::GetBytes($offset) + enc.GetBytes($keyStr)   # 4 + 20 = 24 bytes
    data = ($mode -eq 'd') ? FromBase64String($input) : enc.GetBytes($input)
    out  = for i in 0..len-1:  data[i] XOR key[(i % key.Length) * $offset]
    return ($mode -eq 'e') ? ToBase64String(out) : enc.GetString(out)
```

Neat trick: `$offset` is `[int]$amsiInitFailed`. The payload only decrypts correctly
(offset = 1) **if the AMSI bypass succeeded**, so the sample self-gates on evasion.
XOR key = `01 00 00 00` + UTF-8 `kzWYKApomHlfUdaDPTOe` (24 bytes), index `i % 24`.

---

## Deobfuscated execution flow (outer state machine)

Start state `43597`; real order `43597 → 628100 → 694469 → 597709 → 815050 → exit`.

1. **`43597` — ETW bypass.** Loads `System.Core`, reflects into
   `System.Diagnostics.Eventing.EventProvider` on `PSEtwLogProvider.etwProvider`, and
   sets `m_enabled = 0` to blind Event Tracing for Windows.
2. **`628100`** — `Set-Alias HPUzdMbaTprFuvi = Invoke-Expression` (hides the IEX call).
3. **`694469` — AMSI bypass.** Reflectively sets
   `AmsiUtils.amsiInitFailed = $true` (classic technique, wrapped in try/catch).
4. **`597709`** — defines the `wKHbqsr1Ft2R` base64/XOR helper.
5. **`815050` — payload exec.**
   ```
   Invoke-Expression(
     [IO.StreamReader]::new(
       [IO.Compression.GZipStream]::new(
         [IO.MemoryStream]::new(
           [Convert]::FromBase64String(
             wKHbqsr1Ft2R <BLOB> 'd' [int]$amsiInitFailed 'kzWYKApomHlfUdaDPTOe'
           )
         ),
         Decompress
       )
     ).ReadToEnd()
   )
   ```

---

## Second stage (decrypted payload)

A HWID-keyed C2 fetcher/decryptor:

- **`Get-HWID`** — C:\ volume serial number → hex → Int64 (the per-victim ID).
- Builds two per-HWID URLs on `gloason.com` and pulls an encrypted JSON envelope.
- **`Get-ValuePlain`** — parses the envelope `{salt, iv, ct, tag, iter}`, then:
  - **PBKDF2-HMAC-SHA256** (`PBKDF2SHA256`, default 5000 iters, 64-byte output) →
    split into a 32-byte AES key + 32-byte MAC key.
  - **HMAC-SHA256** over `"WSv1" + salt + iv + ct`, verified with the constant-time
    `ConstEq` (encrypt-then-MAC).
  - **AES-256-CBC + PKCS7** decryption of the ciphertext.
- The decrypted plaintext is executed with `Invoke-Expression`; the beacon URL and
  password are stashed in `$Global:WLDR_HTTP_URI` / `$Global:WLDR_ENC_PASSWORD` for the
  WLDR agent.

---

## Indicators of Compromise (IOCs)

| Type | Value |
|------|-------|
| C2 host | `gloason.com` |
| Invoked-script URL | `https://gloason.com/white/lrau20bdzx/<HWID>` |
| Beacon URL (agent) | `https://gloason.com/white/0barysbi8b07/<HWID>` |
| Envelope password | `16k3g6c0pwnj` |
| XOR key | `01 00 00 00` + `kzWYKApomHlfUdaDPTOe` (offset 1, mod 24) |
| Envelope AAD/tag | `WSv1` |
| Crypto | PBKDF2-SHA256 (5000) → AES-256-CBC/PKCS7 + HMAC-SHA256 (encrypt-then-MAC) |
| Loader globals | `WLDR_HTTP_URI`, `WLDR_ENC_PASSWORD` |
| Evasion | ETW `m_enabled=0`; AMSI `amsiInitFailed=$true` |
| Family / actor | WLDR C2 / UAT-11795 (also: Starland RAT, CastleStealer, Remcos RAT) |

**Reference:** Cisco Talos — "UAT-11795 deploys novel Starland RAT and bespoke WLDR C2
implant in financially motivated campaign."

---

## Artifacts

- `deobfuscated_stager.ps1` — the fully constant-folded outer stager (readable).
- `stage2_payload.ps1` — the decrypted second-stage C2 loader.
