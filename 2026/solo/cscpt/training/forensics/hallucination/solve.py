import base64

b64 = "XMTMzNzY5NDIwA==" 

def shift_31(data):
    # Shifts each byte by 31 (the difference between '\' and '{')
    return bytes((x + 31) % 256 for x in data)

def main():
    data = base64.b64decode(b64)
    print(data)
    data = shift_31(data)
    print(data)

if __name__ == "__main__":
    main()