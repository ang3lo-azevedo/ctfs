# To run: uv run checker.py

import json
import sys


from holpy import logic, kernel, server
from holpy.logic import basic
from holpy.kernel import theory
from holpy.server import items, monitor


def win():
    with open("./flag.txt", "r") as f:
        flag = f.read().strip()
        print(f"Congratulations! You've found the flag: {flag}")


def theorem_proves_false_unconditioned(thm):
    """Check if theorem proves 'false' with no assumptions or hypotheses.

    Args:
        thm: A Thm object to check

    Returns:
        True if theorem conclusion is false and has no assumptions/hypotheses
    """
    try:
        # Check if conclusion is the false constant OR a variable named False/false
        concl_str = str(thm.concl).strip().lower()
        is_false = (
            thm.concl.is_const("false") or concl_str == "false" or concl_str == "?false"
        )

        # Check if there are no assumptions (assumptions are premises to the theorem)
        no_assumptions = len(thm.assums) == 0

        # Check if there are no hypotheses (hyps are implicit assumptions)
        no_hypotheses = len(thm.hyps) == 0

        return is_false and no_assumptions and no_hypotheses
    except Exception as e:
        print(f"Warning: error checking theorem: {e}")
        return False


if __name__ == "__main__":

    hex_proof = input("give me your hex proof")
    proof = bytes.fromhex(hex_proof).decode("utf-8")

    # Load JSON file directly
    try:
        data = json.loads(proof)
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        sys.exit(1)

    # Load imports from the JSON file
    with theory.fresh_theory():
        imports = data.get("imports", [])
        for imp in imports:
            try:
                # Import names don't have .json extension in the JSON
                basic.load_theory(imp)
            except Exception as e:
                print(f"Warning: failed to load import '{imp}': {e}")

        content = data.get("content", [])
        for idx in range(len(content)):

            raw_item = content[idx]
            item = items.parse_item(raw_item)
            if item.error:
                print(f"Warning: parse error for item {idx}: {item.error}")
                continue
            # HELP WTF IS THIS IG
            if item.ty == "thm":
                result = monitor.check_proof(item, rewrite=False)

                if result["status"] in ["OK", "ProofOK"]:
                    print("✓ Proof check passed")

                    exts = item.get_extension()

                    report =theory.thy.checked_extend(exts)
                    if (len(report.get_axioms())) > 1:
                        print("✗ Too many axioms introduced")
                        sys.exit(1)
                    elif report.get_axioms() == 1 and item.ty != "thm":
                        sys.exit(1)
                    try:
                        thm = theory.thy.get_theorem(item.name)

                        if theorem_proves_false_unconditioned(thm):
                            win()
                            sys.exit(2)
                    except Exception as e:
                        print(f"Error getting theorem: {e}")

                    sys.exit(0)
                else:
                    print("✗ Proof check failed")
                    sys.exit(1)
            # ig we addd it ??
            else:
                exts = item.get_extension()

                report =theory.thy.checked_extend(exts)
            if (len(report.get_axioms())) > 1:
                print("✗ Too many axioms introduced")
                sys.exit(1)
            elif report.get_axioms() == 1 and item.ty != "thm":
                sys.exit(1)
