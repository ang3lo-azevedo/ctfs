#!/usr/local/bin/python3
"""
Pickle Scanner CTF Challenge Server

Players connect and submit a pickle file. If it passes the scanner,
it gets executed.
"""

import base64
import pickle

# Import the scanner
from scanner import scan_pickle

BANNER = r"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              Yet Another Pickle Scanner (YAPS)                ║
║                                                               ║
║  Our state-of-the-art security scanner uses:                 ║
║   • Advanced taint tracking to detect obfuscation            ║
║   • Strict whitelist of safe classes only                    ║
║   • Protection against ALL known pickle exploits             ║
║                                                               ║
║  Only trivially safe types are allowed!                      ║
║                                                               ║
║  Submit your pickle for validation and execution.             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

def main():
    print(BANNER)
    print()
    print("Please submit your pickle file (base64 encoded):")
    print("> ", end="", flush=True)

    try:
        # Read the pickle data
        encoded = input().strip()

        if not encoded:
            print("❌ Error: No input provided")
            return

        # Decode from base64
        try:
            pickle_data = base64.b64decode(encoded)
        except Exception as e:
            print(f"❌ Error: Invalid base64 encoding: {e}")
            return

        print()
        print("=" * 65)
        print("🔍 SCANNING PICKLE...")
        print("=" * 65)

        # Scan the pickle
        result = scan_pickle(pickle_data)

        print()
        print("SCAN RESULTS:")
        print("-" * 65)
        print(f"  Status: {'✅ SAFE' if result.is_safe else '❌ UNSAFE'}")
        print(f"  Classes found: {len(result.static_classes)}")

        if result.static_classes:
            print()
            print("  Static class references detected:")
            for module, name in result.static_classes:
                print(f"    • {module}.{name}")

        if result.warnings:
            print()
            print("  Warnings:")
            for warning in result.warnings:
                print(f"    ⚠️  {warning}")

        print()

        if not result.is_safe:
            print("=" * 65)
            print("🚫 REJECTED!")
            print("=" * 65)
            print()
            print(f"Reason: {result.rejection_reason}")
            print()
            print("Your pickle has been flagged as malicious and will not be")
            print("executed.")
            return

        # If safe, execute it
        print("=" * 65)
        print("✅ VALIDATION PASSED!")
        print("=" * 65)
        print()
        print("Your pickle has been validated as safe.")
        print("Loading pickle...")
        print()
        print("-" * 65)

        try:
            result = pickle.loads(pickle_data)
            print()
            print("-" * 65)
            print()
            print(f"Result: {result!r}")

        except Exception as e:
            print()
            print("-" * 65)
            print()
            print(f"⚠️  Execution error: {e}")
            print()
            print("The pickle passed security validation but failed during")
            print("execution. This might be a bug in your pickle.")

    except KeyboardInterrupt:
        print()
        print()
        print("Connection closed.")
        return

    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
