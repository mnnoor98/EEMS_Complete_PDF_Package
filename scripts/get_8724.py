import json

with open('C:/Users/noor/.gemini/antigravity/brain/6444be1b-5e50-4fdb-83cf-19b9e05f089f/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if '"step_index": 8724' in line or '"step_index":8724' in line:
            obj = json.loads(line)
            tc = obj['tool_calls'][0]
            with open('scripts/step_8724_patch.py', 'w', encoding='utf-8') as out:
                out.write(tc['args']['Content'])
            print('Saved step 8724 patch!')
            break

