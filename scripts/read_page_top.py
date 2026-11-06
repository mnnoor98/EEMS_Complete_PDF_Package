with open('frontend/src/app/features/candidates/candidate-war-room.page.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(min(40, len(lines))):
    print(lines[i].rstrip())

