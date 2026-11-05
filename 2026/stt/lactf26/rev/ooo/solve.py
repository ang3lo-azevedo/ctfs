# The target array from the challenge
targets = [
    205, 196, 215, 218, 225, 226, 1189, 2045, 2372, 9300, 8304, 660, 
    8243, 16057, 16113, 16057, 16004, 16007, 16006, 8561, 805, 346, 
    195, 201, 154, 146, 223
]

# Start with known first character
flag_chars = [ord('l')]

# Reverse the logic: next_char = target - current_char
for t in targets:
    next_val = t - flag_chars[-1]
    flag_chars.append(next_val)

# Build the string
final_flag = "".join(chr(c) for c in flag_chars)

print("--- COPY THE LINE BELOW ---")
print(final_flag)
print("---------------------------")

# Optional: Print the hex values to verify correctness against the challenge logic
# The critical sequence in the middle is: ... 1F40, 1F79, 1F78 ...
print("Debug (Critical Middle Section):")
for c in final_flag[13:17]:
    print(f"{c}: {hex(ord(c))}")