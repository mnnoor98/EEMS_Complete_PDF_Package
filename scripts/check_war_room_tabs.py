with open('scripts/patch_war_room.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

for line in text.splitlines():
    if 'tab-btn' in line or 'activeTab' in line:
        print(line.strip())

