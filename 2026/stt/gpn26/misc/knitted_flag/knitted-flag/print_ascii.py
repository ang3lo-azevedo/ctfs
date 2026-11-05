import re

with open('pattern.k', 'r') as f:
    lines = f.readlines()

max_needle = 0
for line in lines:
    line = line.strip()
    if line.startswith('knit'):
        parts = line.split()
        if len(parts) >= 4:
            needle = parts[2]
            idx = int(needle[1:])
            if idx > max_needle:
                max_needle = idx

rows = []
current_row_f = {}
current_row_b = {}
current_dir = None

for line in lines:
    line = line.strip()
    if line.startswith('knit'):
        parts = line.split()
        if len(parts) >= 4:
            direction = parts[1]
            needle = parts[2]
            carrier = parts[3]
            
            if current_dir is None:
                current_dir = direction
            
            if direction != current_dir:
                rows.append((current_row_f, current_row_b))
                current_row_f = {}
                current_row_b = {}
                current_dir = direction
                
            idx = int(needle[1:])
            
            if needle.startswith('f'):
                current_row_f[idx] = carrier
            else:
                current_row_b[idx] = carrier

if current_row_f or current_row_b:
    rows.append((current_row_f, current_row_b))

for y, (row_f, row_b) in enumerate(rows):
    line_str = []
    for x in range(1, max_needle + 1):
        if x in row_f:
            line_str.append('#')
        else:
            line_str.append(' ')
    print(''.join(line_str))
