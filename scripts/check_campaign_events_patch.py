with open('scripts/patch_campaign_events_full.py', 'r', encoding='utf-8', errors='ignore') as f:
    c = f.read()

print("File size:", len(c))
print("Contains voters tab?", 'activeTab() === \'voters\'' in c or "activeTab() === 'voters'" in c)
print("Contains campaign tab?", 'activeTab() === \'campaign\'' in c or "activeTab() === 'campaign'" in c)
print("Contains incidents tab?", 'activeTab() === \'incidents\'' in c or "activeTab() === 'incidents'" in c)

# Print lines with activeTab
for line in c.splitlines():
    if 'activeTab' in line and '===' in line:
        print("  ", line.strip())

