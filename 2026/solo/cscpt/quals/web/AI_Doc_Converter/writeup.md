---
title: 'AI Doc Converter - CSCPT 2026 Quals (500pts)'
date: '2026-06-20'
draft: false
authors: ['ang3lo']
tags: ['Web', 'DOCX', 'Aspose', 'XXE', 'SDT', 'Java', 'Field Injection', 'SSRF']
summary: 'Aspose.Words DOCX-to-PNG converter. Field evaluation is selective; SDT binding works. SSRF reported by others but not reproduced. File read not yet achieved.'
canonical: ''
---

## AI Doc Converter

> Our new AI-powered document studio renders any DOCX. Flag at `/flag.txt`.

## Tech Stack

- **Server:** gunicorn (Python WSGI)
- **DOCX Engine:** Aspose.Words for Java 26.6.0 (`X-Generator` header)
- **Output:** PNG image (816×1056), extracted via tesseract OCR

## Key Documentation Findings

### Aspose.Words 26.6.0 Features (from archived docs)

| Feature | Doc Reference | Used by Server? |
|---------|--------------|-----------------|
| **AI-powered Features** | `OpenAiModel`, `AnthropicAiModel`, `GoogleAiModel` — summarization, translation, grammar checking | **No** — programmatic API only |
| **Mustache Syntax** | `{{variable}}` templates via `MailMerge.setUseNonMergeFields(true)` | **No** — mail merge not invoked |
| **LINQ Reporting Engine** | `<<[expression]>>` via `ReportingEngine.buildReport()` | **No** — expressions rendered as text |
| **External Resource Loading** | Images, CSS, HTML loaded by default | **Blocked** — `IResourceLoadingCallback` active |
| **Security Notes** | Warns about local file disclosure, credential leak, SSRF via linked content | N/A — mitigation implemented |

### Security Documentation (Key Excerpt)

From [Web Applications Security When Loading External Resources](https://web.archive.org/web/20250917195926/https://docs.aspose.com/words/java/web-applications-security-when-loading-external-resources/):

- **Local Image Disclosure**: "processing a document with a reference to a local image file will result in that file being included in the final document"
- **SSRF via Linked Content**: timing differences reveal if internal IP/port is filtered
- **Mitigation**: `IResourceLoadingCallback` with `ResourceLoadingAction.SKIP` disables external loads
- **Default behavior**: resources ARE loaded unless callback blocks them

**Conclusion:** The challenge server implements `IResourceLoadingCallback` to block external resources, preventing both local file disclosure and SSRF.

## Field Evaluation

Aspose.Words evaluates SOME field types during `Document.save()` (those needed for page layout):

**Evaluated fields:**
`DATE`, `TIME`, `NUMPAGES`, `PAGE`, `SECTIONPAGES`, `REF`, `SEQ`, `AUTONUM`, `SET`, `RD`, `SYMBOL`, `EQ`, `STYLEREF`, `USERINITIALS`, `SAVEDATE`, `PRINTDATE`, `BARCODE`, `XE`, `TA`, `TC`, `FORMCHECKBOX`, `FORMDROPDOWN`

**NOT evaluated fields:**
`INCLUDETEXT`, `INCLUDEPICTURE`, `DOCVARIABLE`, `DOCPROPERTY`, `AUTHOR`, `TITLE`, `SUBJECT`, `FILENAME`, `FILESIZE`, `MERGEFIELD`, `IF`, `COMPARE`, `= (FORMULA)`, `QUOTE`, `FILLIN`, `HYPERLINK`, `TOC`, `INDEX`

### SET + REF Chain (Works)

```
{ SET mybm "any literal text" }
{ REF mybm }
→ "any literal text"
```

SET stores a value in a bookmark; REF retrieves it. Both fields are evaluated. However, SET only accepts **literal** values — no nested field evaluation or file reading.

### INCLUDETEXT: Definitive Result

INCLUDETEXT is **never** evaluated during `Document.save()`. Tested exhaustively:

- All switches (`\c`, `\!`, `\t`, `\n`, `\d`, `\* MERGEFORMAT`)
- All path formats (`/flag.txt`, `file:///flag.txt`, `C:\flag.txt`, UNC paths)
- Inside evaluated fields (EQ, SDT)
- Via python-docx generated XML (exact OOXML structure)
- With `w:updateFields` in settings.xml

**Result:** Always shows fallback text. This is by-design — `Document.save()` evaluates only layout-essential fields, not content-inclusion fields.

## Working Mechanism: SDT Data Binding

Structured Document Tag (SDT) + custom XML parts can display **embedded hardcoded** data:

1. Embed custom XML at `/customXml/item1.xml`
2. Add `w:dataBinding` with XPath `/root/flag`
3. Aspose resolves the binding and displays the XML content

**Limitations:**
- Entity processing is disabled (even `&amp;` causes binding failure)
- XInclude not supported
- XPath functions (`unparsed-text()`, `doc()`) cause binding failure
- Only basic XPath paths supported (`/root/flag`)
- Data must be **hardcoded** in the DOCX — no external file loading

## What Was Tested

| Technique | Result |
|-----------|--------|
| XXE in `word/document.xml` | Blank — external entities disabled |
| XXE in custom XML parts | Entities cause SDT binding to fail |
| `INCLUDETEXT` (all switches/paths) | **Never evaluated** |
| `INCLUDEPICTURE` | Never evaluated |
| Image `file:///flag.txt` | Placeholder (all paths produce identical PNG) |
| `AltChunk` external (file://, http://) | Blank / ignored |
| SVG XXE / `xlink:href` | Blank |
| `attachedTemplate` / `subDoc` | Ignored |
| `customXml` external `file://` | 500 (document level) / ignored (package level) |
| XInclude in custom XML | Not supported |
| XPath functions (`unparsed-text`, `doc`) | Not supported |
| Chart external data | 500 error |
| WebExtension / Taskpane | Ignored |
| DDE / DDEAuto field | Not evaluated |
| Embedded font `file://` | Ignored |
| OLE object / ActiveX control | 500 / ignored |
| **Outbound HTTP (SSRF)** | **0 requests** — `IResourceLoadingCallback` blocks all |
| LINQ `<<[...]>>` / Mustache `{{...}}` | Rendered as literal text |
| Prompt injection (AI angle) | Document text rendered as-is |
| SSTI / command injection | Blocked / sanitized |
| Path traversal in filename | 400 Bad Request |
| ZIP symlink | 500 error |
| Billion laughs attack | Internal entities resolve but blank output |
| PNG hash comparison (file:// paths) | All identical — no oracle |
| Timing oracle (customXml 500 errors) | All ~0.85s — no oracle |
| User info fields (USERNAME/USERINITIALS) | Not evaluated |

## SSRF

Reportedly found by another participant (`webhook.site/679a9264-...`). However, testing with webhook.site, httpbin.org, and multiple relationship types (image, AltChunk, hyperlink, chart, web extension, OLE) produced **zero outbound requests**. The `IResourceLoadingCallback` documented in Aspose's security page appears to be blocking all external resource loading on this instance.

## Remaining Avenues

1. **Java deserialization** — OLE object with ysoserial gadget chain (requires known classpath)
2. **Aspose.Words 26.6.0 internal** — proprietary source; potential 0-day or CTF-specific modification
3. **Python/gunicorn layer** — if the wrapper has a vulnerability not yet discovered

## Scripts

- `solve.py` — SDT binding + custom XML exploit (partial)
- OCR: `/tmp/tesseract/bin/tesseract` (nix)
- Python deps: `/tmp/venv/` (`requests`, `Pillow`, `python-docx`)
