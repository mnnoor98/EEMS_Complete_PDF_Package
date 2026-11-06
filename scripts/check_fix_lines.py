with open('scripts/fix_war_room_structure.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'tab-btn' in line or 'WarRoomTab' in line or 'voters' in line or 'campaign' in line:
        print(f"{i+1}: {line.rstrip()}")

