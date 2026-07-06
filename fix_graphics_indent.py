"""
Fix indentation in graphics.py for growth indicator code.
All lines from "# Calculate center of tile" through the end of the growth
indicator section need to be indented 4 more spaces.
"""

# Read the file
with open('graphics.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "# Calculate center of tile" that's in the growth indicator section
# and indent everything from there until we hit a line that's back at the original indentation
in_section = False
start_line = None
end_line = None
base_indent = None

for i, line in enumerate(lines):
    # Find start
    if '# Calculate center of tile' in line and 'tile_center_x = sx + tile_size // 2' in lines[i+1]:
        in_section = True
        start_line = i
        # Calculate current indentation (should be 32 spaces)
        base_indent = len(line) - len(line.lstrip())
        print(f"Found start at line {i+1}, base indent: {base_indent}")
        continue
    
    # Find end - when we hit a line at or less than base_indent that's not blank/comment
    if in_section and line.strip() and not line.strip().startswith('#'):
        current_indent = len(line) - len(line.lstrip())  
        if current_indent <= base_indent:
            end_line = i
            print(f"Found end at line {i+1}")
            break

if start_line is None:
    print("ERROR: Could not find growth indicator section!")
    exit(1)

if end_line is None:
    # Go to end of nearby block
    for i in range(start_line, min(start_line + 200, len(lines))):
        if 'self.current_tile = None' in lines[i]:
            end_line = i
            print(f"Using 'self.current_tile = None' as end marker at line {i+1}")
            break

print(f"Indenting lines {start_line+1} to {end_line}")

# Indent the section by adding 4 spaces to each line
for i in range(start_line, end_line):
    if lines[i].strip():  # Only indent non-empty lines
        lines[i] = '    ' + lines[i]

# Write back
with open('graphics.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done! Fixed indentation.")
