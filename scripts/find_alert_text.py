import os

matches = []
for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['node_modules', '.git', 'bin', 'obj', '.angular', 'dist']):
        continue
    for file in files:
        path = os.path.join(root, file)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'submit center result' in content.lower():
                    matches.append((path, 'submit center result'))
                if 'could not submit' in content.lower():
                    matches.append((path, 'could not submit'))
        except Exception:
            pass

print('Matches:', matches)

