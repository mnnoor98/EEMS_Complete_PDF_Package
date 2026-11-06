with open('scripts/patch_war_room.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('TAB 3: VOTERS')
if idx != -1:
    print(text[idx:idx+1500])
else:
    print("TAB 3: VOTERS not found")

