#!/usr/bin/env python3
"""
The Index Never Forgets - CSCPT 2026 Qualifiers Forensics

Recovers a shredded PDF's flag from the Windows Search Index (Windows.edb).
The suspect opened cscpt.pdf, shredded it with sdelete, and rebooted.
"The Index Never Forgets" — Windows Search retains indexed metadata.
"""

import os
import sys
import subprocess
import shutil
import glob
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EDB_PATH = SCRIPT_DIR / "C/ProgramData/Microsoft/search/data/applications/windows/Windows.edb"
EXPORT_DIR = SCRIPT_DIR / "edb_export.export"


def check_docker() -> bool:
    """Check if Docker is available."""
    return shutil.which("docker") is not None


def check_esedbexport() -> bool:
    """Check if esedbexport is available natively."""
    return shutil.which("esedbexport") is not None


def export_edb_tables() -> bool:
    """
    Export all tables from the Windows.edb ESE database.
    Uses esedbexport (native or via Docker).
    Returns True on success.
    """
    if not EDB_PATH.exists():
        print(f"[!] Windows.edb not found at: {EDB_PATH}")
        return False

    # Remove previous export
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)

    print(f"[*] Exporting tables from: {EDB_PATH}")

    if check_esedbexport():
        # Native esedbexport
        cmd = [
            "esedbexport",
            "-t", str(EXPORT_DIR.with_suffix("")),  # Strips .export suffix
            "-m", "tables",
            str(EDB_PATH),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[!] esedbexport failed: {result.stderr}")
            return False
    elif check_docker():
        # Docker-based esedbexport
        print("[*] Using Docker for esedbexport...")
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{SCRIPT_DIR}:/data",
            "-w", "/data",
            "ubuntu:latest",
            "bash", "-c",
            "apt-get update -qq && "
            "apt-get install -y -qq libesedb-utils && "
            f"esedbexport -t all -m tables 'C/ProgramData/Microsoft/search/data/applications/windows/Windows.edb'",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and "Export completed" not in result.stdout:
            print(f"[!] Docker esedbexport failed: {result.stderr}")
            return False
    else:
        print("[!] Neither esedbexport nor Docker is available.")
        print("[!] Install libesedb-utils or Docker and try again.")
        return False

    # Verify export
    pstore = EXPORT_DIR / "SystemIndex_PropertyStore.11"
    if not pstore.exists():
        print(f"[!] Export incomplete — PropertyStore not found.")
        return False

    print(f"[+] Export complete. {len(list(EXPORT_DIR.iterdir()))} tables exported.")
    return True


def find_flag() -> str | None:
    """
    Parse the exported PropertyStore table to find cscpt.pdf metadata.
    The flag is derived from the System.Keywords property.
    """
    pstore_path = EXPORT_DIR / "SystemIndex_PropertyStore.11"
    if not pstore_path.exists():
        print(f"[!] PropertyStore not found. Run export first.")
        return None

    print(f"[*] Searching for cscpt.pdf in PropertyStore...")

    # First, find WorkId for cscpt.pdf from the gather log
    gthr_path = EXPORT_DIR / "SystemIndex_Gthr.6"
    work_id = None
    if gthr_path.exists():
        with open(gthr_path) as f:
            for line in f:
                if "cscpt.pdf" in line:
                    work_id = line.split("\t")[1]
                    print(f"[*] Found cscpt.pdf with WorkId = {work_id}")
                    break

    # Extract properties from PropertyStore
    with open(pstore_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            # Search for the cscpt.pdf record
            if "\tcscpt.pdf\t" in line or "\tcscpt.pdf" in line:
                fields = line.strip().split("\t")

                print("\n[*] Recovered PDF metadata from Windows Search Index:\n")

                # Decode and display metadata
                metadata = {}

                # Helper: decode hex field if applicable
                def decode_field(val: str) -> str:
                    if all(c in "0123456789abcdefABCDEF" for c in val) and len(val) >= 4 and len(val) % 2 == 0:
                        try:
                            decoded = bytes.fromhex(val).decode("ascii")
                            if decoded.isprintable():
                                return decoded
                        except:
                            pass
                    return val

                # Field indices based on the PropertyStore schema
                field_map = {
                    36: "Parent Directory",
                    39: "Full Path",
                    426: "Document Type",
                    430: "Subject",
                    433: "Tags / Keywords",
                    438: "Filename",
                    462: "Perceived Type",
                }

                for idx, label in field_map.items():
                    if idx < len(fields) and fields[idx]:
                        value = decode_field(fields[idx])
                        metadata[label] = value
                        print(f"  {label:20s}: {value}")

                # Decode hex-encoded author fields
                for idx in [53, 300, 435]:
                    if idx < len(fields) and fields[idx]:
                        decoded = decode_field(fields[idx])
                        if decoded != fields[idx]:
                            metadata["Author" if idx == 53 else "Company"] = decoded
                            print(f"  {'Author' if idx == 53 else 'Company':20s}: {decoded}")

                # Decode hex-encoded PDF creator
                if 230 < len(fields) and fields[230]:
                    decoded = decode_field(fields[230])
                    if decoded != fields[230]:
                        metadata["PDF Creator"] = decoded
                        print(f"  {'PDF Creator':20s}: {decoded}")

                # The flag is the System.Title property from the PDF metadata
                subject = fields[430] if 430 < len(fields) else ""
                flag = f"CSCPT{{{subject.replace(' ', '_')}}}"

                print(f"\n[+] FLAG: {flag}")

                return flag

    print("[!] cscpt.pdf not found in PropertyStore.")
    return None


def main():
    print("=" * 60)
    print("  The Index Never Forgets — CSCPT 2026 Forensics")
    print("=" * 60)

    # Check if pre-exported tables exist
    if not (EXPORT_DIR / "SystemIndex_PropertyStore.11").exists():
        print("[*] No exported tables found. Running export...")
        if not export_edb_tables():
            return 1
    else:
        print(f"[*] Using existing export at: {EXPORT_DIR}")

    flag = find_flag()
    if not flag:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
