with open('scripts/patch_campaign_events_full.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
tabs = re.findall(r"type WarRoomTab = [^;]+;", text)
print("WarRoomTab definition in patch_campaign_events_full:", tabs)

