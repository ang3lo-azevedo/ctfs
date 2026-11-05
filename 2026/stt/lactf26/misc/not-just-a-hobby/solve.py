import re
import matplotlib.pyplot as plt

def solve():
    print("Parsing v.v...")
    points = []
    
    try:
        with open('v.v', 'r') as f:
            content = f.read()
            
            # The file contains patterns like: (x == 7'd588 && y == 43)
            # We match 'x' and 'y' comparisons, ignoring the "7'd" prefix if present.
            # We look for both "x first" and "y first" orders just in case.
            
            # Pattern: x == value && y == value
            p1 = re.compile(r"x\s*==\s*(?:7'd)?(\d+)\s*&&\s*y\s*==\s*(?:7'd)?(\d+)")
            points.extend(p1.findall(content))
            
            # Pattern: y == value && x == value
            p2 = re.compile(r"y\s*==\s*(?:7'd)?(\d+)\s*&&\s*x\s*==\s*(?:7'd)?(\d+)")
            # Note: p2 returns (y, x), so we swap them when appending
            points.extend([(x, y) for y, x in p2.findall(content)])
            
    except FileNotFoundError:
        print("Error: Could not find 'v.v'. Make sure it is in the same directory.")
        return

    if not points:
        print("No coordinates found. Check the file content.")
        return

    print(f"Found {len(points)} pixels. Generating image...")

    # Convert strings to integers
    x_vals = [int(p[0]) for p in points]
    y_vals = [int(p[1]) for p in points]

    # Plotting
    plt.figure(figsize=(10, 6))
    # s=0.1 makes pixels small enough to see detail in high-density areas
    plt.scatter(x_vals, y_vals, c='black', s=0.1, marker='s')
    
    # Invert Y axis because screen coordinates (0,0) start at top-left
    plt.gca().invert_yaxis()
    plt.axis('equal') # Keep aspect ratio square
    plt.title("Extracted Flag")
    
    # Save to file instead of showing
    output_file = 'output.png'
    plt.savefig(output_file, dpi=100, bbox_inches='tight')
    print(f"Image saved to {output_file}")
    print("If it looks like a QR code, scan it!")
    print("If it looks inverted, try swapping the color.")

if __name__ == "__main__":
    solve()