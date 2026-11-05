import base64

with open("ciphertexts.txt") as f:
    lines = f.read().splitlines()

cts = [base64.b64decode(line) for line in lines]

flag_prefix = "CSCPT{"
ks = []

for i in range(len(flag_prefix)):
    ks.append(cts[4][101 + i] ^ ord(flag_prefix[i]))

common_chars = set(b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \n\r\t.,!?:;-")
vowels = set(b"aeiouAEIOU ")
common_letters = set(b"srtdnmlcSRTDNMLC")

def score_k(pos, k):
    score = 0
    valid = True
    for ct_idx in [0, 1, 2, 3, 5, 6, 7, 8]:
        if pos < len(cts[ct_idx]):
            c = cts[ct_idx][pos] ^ k
            if c not in common_chars:
                if c >= 128: # Allow accents but with neutral score
                    pass
                else:
                    valid = False
            else:
                score += 1
                if c in vowels:
                    score += 2
                if c in common_letters:
                    score += 1
    
    if pos < len(cts[4]):
        p = cts[4][pos] ^ k
        if chr(p) not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_}":
            valid = False
            
    if not valid:
        return -1
    return score

print("Recovering flag using heuristic analysis on Many-Time Pad...")
for pos in range(101 + 6, 149):
    best_score = -1
    best_k = []
    for k in range(256):
        s = score_k(pos, k)
        if s > best_score:
            best_score = s
            best_k = [k]
        elif s == best_score and s != -1:
            best_k.append(k)
    
    if best_k:
        # Just pick the first best
        ks.append(best_k[0])
    else:
        ks.append(0)

heuristic_flag = ""
for i in range(101, 149):
    heuristic_flag += chr(cts[4][i] ^ ks[i - 101])

print(f"Heuristically recovered string: {heuristic_flag}")

# The heuristic gets extremely close. We manually correct the typos and context (AES CTR mode)
corrections = {
    13: 'u', # 'U' -> 'u'
    26: 's', # 'S' -> 's'
    29: 'n', # 'z' -> 'n'
    # 'kirxxoC0k' -> 'CTR_mode}'
    39: 'C',
    40: 'T',
    41: 'R',
    42: '_',
    43: 'm',
    44: 'o',
    45: 'd',
    46: 'e',
    47: '}'
}

final_flag = list(heuristic_flag)
for idx, char in corrections.items():
    final_flag[idx] = char

final_flag = "".join(final_flag)
print(f"Final corrected flag: {final_flag}")
