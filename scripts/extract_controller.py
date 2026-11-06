import json

with open('C:/Users/noor/.gemini/antigravity/brain/6444be1b-5e50-4fdb-83cf-19b9e05f089f/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if '"step_index": 9034' in line or '"step_index":9034' in line:
            obj = json.loads(line)
            tc = obj['tool_calls'][0]
            print(tc['name'], tc['args'].get('Path'))
            if 'CandidatePortalController.cs' in str(tc['args'].get('Path')):
                print('Content len:', len(tc['args']['Content']))
                with open('scripts/controller_at_9034.cs', 'w', encoding='utf-8') as out:
                    out.write(tc['args']['Content'])
                print('Saved controller_at_9034.cs!')
            break

