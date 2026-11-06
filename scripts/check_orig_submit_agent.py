import subprocess

p = subprocess.run(['git', 'show', ':frontend/src/app/features/candidates/candidate-war-room.page.ts'], capture_output=True, text=True, encoding='utf-8')
lines = p.stdout.splitlines()

start = -1
for i, l in enumerate(lines):
    if 'submitNewBoothAgent()' in l:
        start = i
        break

if start != -1:
    print("\n--- Original submitNewBoothAgent() ---")
    for l in lines[start-5:start+60]:
        print(l)

