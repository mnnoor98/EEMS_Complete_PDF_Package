import glob

for p in glob.glob('scripts/patch_*.py'):
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        c = f.read()
    print(f"File: {p}, Length: {len(c)}")
    first_few = [l.strip() for l in c.splitlines()[:10] if l.strip()]
    print("  First lines:", first_few[:4])

