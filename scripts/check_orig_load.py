import subprocess

p = subprocess.run(['git', 'show', ':frontend/src/app/features/candidates/candidate-war-room.page.ts'], capture_output=True, text=True, encoding='utf-8')
lines = p.stdout.splitlines()
print(f"Original file had {len(lines)} lines")

# Let's inspect the load() method of original file
start = -1
for i, l in enumerate(lines):
    if 'load()' in l:
        start = i
        break

if start != -1:
    print("\n--- Original load() ---")
    for l in lines[start:start+40]:
        print(l)

