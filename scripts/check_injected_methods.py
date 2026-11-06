with open('scripts/inject_all_missing_methods.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
method_names = re.findall(r'^\s*([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{', text, re.MULTILINE)
print("Methods in inject_all_missing_methods:", method_names)

