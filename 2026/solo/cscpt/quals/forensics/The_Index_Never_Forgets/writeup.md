---
title: "The Index Never Forgets - CSCPT 2026 Qualifiers"
date: '2026-06-20'
draft: false
authors: ['ang3lo']
tags: ['Forensics', 'NTFS', 'MFT', 'LogFile', 'Windows Search Index', 'Thumbcache']
summary: 'Recover a shredded PDF and ZIP to compute the flag hash'
canonical: ''
---

## The Index Never Forgets

## Table of Contents

1. [Challenge](#challenge)
2. [Evidence Overview](#evidence-overview)
3. [Solution](#solution)
   1. [Step 1: Identify the Files](#step-1-identify-the-files)
   2. [Step 2: Windows Search Index Metadata](#step-2-windows-search-index-metadata)
   3. [Step 3: Extract the Text Content from the Index](#step-3-extract-the-text-content-from-the-index)
   4. [Step 4: Decode the Flag](#step-4-decode-the-flag)
4. [Flag](#flag)
5. [Tools Used](#tools-used)

---

## Challenge

> A workstation was triaged after an incident. The suspect opened a PDF document, shredded it, and rebooted. Recover the secret flag.

**Category**: Forensics
**Points**: 500

## Evidence Overview

The triage collection (performed with KAPE) includes:

| Artifact | Purpose |
|----------|---------|
| `$MFT` (328 MB) | Master File Table |
| `$LogFile` (64 MB) | NTFS transaction journal |
| `$Extend/$J` (35 MB) | USN Change Journal |
| `Windows.edb` (16 MB) | Windows Search Index (ESE database) |
| `NTUSER.DAT` | User registry hive |
| `Recent/` folder | LNK shortcut files |
| `Thumbcache/` | Explorer thumbnail cache |

## Solution

### Step 1: Identify the Files

Two LNK shortcut files in `C:\Users\cscpt\AppData\Roaming\Microsoft\Windows\Recent\` reveal the attack timeline:

| LNK File | Target | MFT Record |
|----------|--------|------------|
| `cscpt.lnk` | `C:\Users\cscpt\Downloads\cscpt.zip` | #302265 (resident, 570 bytes) |
| `cscpt (2).lnk` | `C:\Users\cscpt\Documents\cscpt.pdf` | #68726 (resident, 582 bytes) |

`sdelete.lnk` confirms the suspect used Sysinternals SDelete to shred files.

The suspect downloaded `cscpt.zip`, extracted `cscpt.pdf`, opened the PDF, then shredded both files.

### Step 2: Windows Search Index Metadata

Open the Windows Search Index database using NirSoft ESEDatabaseView.

The `SystemIndex_PropertyStore` table (record WorkId 1109) yields PDF metadata:

| Property | Value |
|----------|-------|
| Filename | `cscpt.pdf` |
| Size | 4,770 bytes |
| Type | `application/pdf` |
| Author | `CSCPT Research Group` |
| PDF Creator | `ReportLab PDF Library - (opensource)` |
| Subject | `You WON a SECRET!` |
| Tags | `Cybersecurity Challenge PT 2026` |

### Step 3: Extract the Text Content from the Index

The Windows Search Index not only stores metadata but also the indexed text. Looking at the `SystemIndex_Gthr` table, we see the indexed text for the PDF:

> Cybersecurity Challenge PT 2026 Cybersecurity Challenge PT 2026 CONFIDENTIAL Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. INJUGUCUPMYWCZJRGJRGEZLCGJRWMNLBMQ2GCYTFGAYGMNRZHFSDCZRYMJQTQMZRMQ2WEZBZGJQWIM3EG AYTKYZZGBQTONJQGY3DOYTFGYZWINLEPU======

### Step 4: Decode the Flag

At the end of the text, there is a Base32 encoded string. We can decode it to get the flag:

```bash
echo "INJUGUCUPMYWCZJRGJRGEZLCGJRWMNLBMQ2GCYTFGAYGMNRZHFSDCZRYMJQTQMZRMQ2WEZBZGJQWIM3EGAYTKYZZGBQTONJQGY3DOYTFGYZWINLEPU======" | base32 -d
```

## Flag

```
CSCPT{1ae12bbeb2cf5ad4abe00f699d1f8ba831d5bd92ad3d015c90a750667be63d5d}
```

## Tools Used

- **NirSoft ESEDatabaseView** - ESE database viewer
