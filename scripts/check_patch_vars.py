with open('scripts/patch_war_room.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
matches = re.findall(r'(\w+)\s*=\s*"""', text)
print("Variables in patch_war_room:", matches)

