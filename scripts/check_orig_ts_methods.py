import subprocess

p = subprocess.run(['git', 'show', ':frontend/src/app/features/candidates/candidate-war-room.page.ts'], capture_output=True, text=True, encoding='utf-8')
lines = p.stdout.splitlines()

for i in range(1200, min(1300, len(lines))):
    print(lines[i])

