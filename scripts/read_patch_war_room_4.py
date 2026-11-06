with open('scripts/patch_war_room.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i in range(380, len(lines)):
    print(lines[i].rstrip())

