import glob
for p in glob.glob('scripts/*.py'):
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        c = f.read()
    if "activeTab() === 'voters'" in c or 'activeTab() === "voters"' in c:
        print('Found in:', p)

