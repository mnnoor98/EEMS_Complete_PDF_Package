with open('frontend/src/app/features/candidates/candidate-war-room.page.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("File total lines:", len(lines))

sections = []
for i, l in enumerate(lines):
    if l.strip().startswith('<!-- =================') or l.strip().startswith('<!-- TAB') or l.strip().startswith('// ================='):
        sections.append((i+1, l.strip()))

for s in sections:
    print(f"Line {s[0]}: {s[1]}")

