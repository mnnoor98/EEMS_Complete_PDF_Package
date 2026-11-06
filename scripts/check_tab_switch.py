with open('scripts/patch_war_room.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('tab_switch_replacement')
if idx != -1:
    print(text[idx:idx+1500])

