from pyzbar.pyzbar import decode
from PIL import Image

# Open the image you just generated
img = Image.open('final_solution.png')

# Decode it
results = decode(img)

if results:
    for result in results:
        print(f"FLAG FOUND: {result.data.decode('utf-8')}")
else:
    print("Could not decode. Try scanning the screen with your phone!")