import sys

LEN_BLOCK=8
LEN_FLAG=64


def box(i):
    S = [5, 6, 4, 3, 1, 2, 0, 7]
    return S[(3*i) % len(S):] + S[:(3*i) % len(S)]


def mixer(msg, r):
    out = [0 for _ in range(LEN_FLAG)]
    for block in range(LEN_FLAG // LEN_BLOCK):
        s = box(r + block)
        for j in range(LEN_BLOCK):
            out[s[j] + block * LEN_BLOCK] = msg[j + block * LEN_BLOCK] ^ j
    return out


def main():
    if len(sys.argv) != 2:
        print ("Usage: python3 {} <flag>".format(sys.argv[0]))
        return 1
    elif len(sys.argv[1]) != LEN_FLAG:
        print ("Tamanho da flag incorrecto")
        return 1
    else:
        msg = list(map(ord, sys.argv[1]))
        for i in range(8):
            msg = mixer(msg, i)

    print(msg)
    return 0

main()

# python3 mixer.py <FLAG> = [87, 120, 87, 107, 64, 80, 64, 83, 110, 127, 98, 117, 110, 116, 88, 106, 109, 108, 119, 92, 92, 106, 112, 92, 110, 101, 107, 98, 119, 104, 116, 116, 113, 102, 117, 102, 92, 119, 108, 92, 114, 105, 107, 98, 117, 116, 98, 88, 108, 118, 92, 113, 112, 112, 92, 122, 119, 117, 104, 122, 98, 88, 102, 88]
