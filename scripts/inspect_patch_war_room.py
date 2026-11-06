with open('scripts/patch_war_room.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Length of patch_war_room.py:", len(text))
tabs = re.findall(r"activeTab\(\)\s*===\s*'([^']+)'", text)
print("Tabs in patch_war_room:", set(tabs))

