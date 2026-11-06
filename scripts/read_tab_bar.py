with open('frontend/src/app/features/candidates/candidate-war-room.page.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(75, 115):
    print(f"{i+1}: {lines[i].rstrip()}")

