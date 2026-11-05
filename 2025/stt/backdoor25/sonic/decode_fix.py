from pyzbar.pyzbar import decode
from PIL import Image, ImageOps

def solve_final():
    # 1. Open the barcode image
    try:
        img = Image.open('final_solution.png')
    except FileNotFoundError:
        print("Error: final_solution.png not found!")
        return

    # 2. Add a 'Quiet Zone' (White Border)
    # We add 50 pixels of whitespace on all sides.
    # This is required for the scanner to recognize the start/stop bits.
    img_padded = ImageOps.expand(img, border=50, fill='white')
    
    # Optional: Save it so you can see the difference
    img_padded.save('final_decoded.png')

    # 3. Decode
    results = decode(img_padded)

    if results:
        print("\n" + "="*40)
        for result in results:
            # The .data attribute is a byte-string, so we decode to utf-8
            print(f"SUCCESS! The flag is: {result.data.decode('utf-8')}")
        print("="*40 + "\n")
    else:
        print("Still failing... try uploading 'final_decoded.png' to zxing.org")

if __name__ == "__main__":
    solve_final()