with open('scripts/patch_war_room.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
voter_matches = [m.start() for m in re.finditer(r'voters', text, re.IGNORECASE)]
print("Total occurrences of voters in patch_war_room:", len(voter_matches))
for pos in voter_matches[:5]:
    snippet = text[max(0, pos-40):pos+80].replace('\n', ' ')
    print(f"  At {pos}: {snippet}")

