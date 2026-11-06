with open('frontend/src/app/features/candidates/candidate-war-room.page.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line_no in [586, 664, 709, 800]:
    print(f"--- Around line {line_no} ---")
    for l in lines[line_no-1:line_no+15]:
        print(l.rstrip())

