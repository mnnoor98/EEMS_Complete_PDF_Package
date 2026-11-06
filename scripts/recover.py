import json

with open('C:/Users/noor/.gemini/antigravity/brain/6444be1b-5e50-4fdb-83cf-19b9e05f089f/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if '"step_index": 9293' in line or '"step_index":9293' in line:
            obj = json.loads(line)
            tc = obj['tool_calls'][0]
            print('Found step 9293!')
            with open('scripts/recovered_team_users_code.txt', 'w', encoding='utf-8') as out:
                out.write(tc['args']['Replacement'])
            print('Saved to scripts/recovered_team_users_code.txt')
            break

