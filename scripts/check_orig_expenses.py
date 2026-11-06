import subprocess

p = subprocess.run(['git', 'show', ':frontend/src/app/features/candidates/candidate-war-room.page.ts'], capture_output=True, text=True, encoding='utf-8')
lines = p.stdout.splitlines()

start = -1
for i, l in enumerate(lines):
    if 'loadExpenseSchedule' in l:
        start = i
        break

if start != -1:
    print("\n--- Original loadExpenseSchedule ---")
    for l in lines[start:start+30]:
        print(l)

