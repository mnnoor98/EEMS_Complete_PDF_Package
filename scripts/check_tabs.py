with open('frontend/src/app/features/candidates/candidate-war-room.page.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines[:120]):
    if 'tab' in l.lower() or 'button' in l.lower() or '<nav' in l.lower():
        print(f"{i+1}: {l.rstrip()}")

