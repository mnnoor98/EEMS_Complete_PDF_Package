with open('scripts/patch_war_room.py', 'r', encoding='utf-8', errors='ignore') as f:
    c = f.read()

print("File size:", len(c))
print("Keywords:")
for kw in ['voters', 'incidents', 'campaign', 'TAB 3', 'TAB 4', 'TAB 5', 'TAB 6']:
    print(f"  {kw}: {'in file' if kw in c else 'NOT in file'}")

