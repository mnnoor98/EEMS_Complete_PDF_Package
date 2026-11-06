import re

file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

tabs = re.findall(r"activeTab\(\)\s*===\s*'([^']+)'", text)
print("Tabs found:", set(tabs))

# Check imports
imports = [line for line in text.splitlines() if line.startswith('import ')]
print("Imports:", imports[:10])

# Check voter references
voter_lines = [line.strip() for line in text.splitlines() if 'voter' in line.lower()]
print(f"Total voter references: {len(voter_lines)}")
for l in voter_lines[:10]:
    print("  ", l)

