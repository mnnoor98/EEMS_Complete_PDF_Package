with open('scripts/patch_candidate_war_room.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print("File length:", len(text))
import re
print("Variables in patch_candidate_war_room:", re.findall(r'(\w+)\s*=\s*"""', text))
print("\nFirst 1000 characters of patch_candidate_war_room:")
print(text[:1000])

