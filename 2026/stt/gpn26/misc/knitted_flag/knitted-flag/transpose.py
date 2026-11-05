with open('ascii_output.txt', 'r') as f:
    lines = [line.rstrip() for line in f]

max_len = 20
padded_lines = [line.ljust(max_len) for line in lines]

for new_y in range(19, -1, -1):
    row_chars = []
    for new_x in range(len(padded_lines)):
        row_chars.append(padded_lines[new_x][new_y])
    print(''.join(row_chars))
