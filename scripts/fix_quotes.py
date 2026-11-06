with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for l in lines:
    if 'rText.Contains' in l and 'error' in l:
        new_lines.append('                            if (rText.Contains("\\"error\\":0") || rText.Contains("\\"error\\": 0"))\n')
    else:
        new_lines.append(l)

with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Fixed line successfully!')

