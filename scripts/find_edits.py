import json

with open('C:/Users/noor/.gemini/antigravity/brain/6444be1b-5e50-4fdb-83cf-19b9e05f089f/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if 'CandidatePortalController.cs' in line and '"edit_file"' in line:
            obj = json.loads(line)
            idx = obj.get('step_index')
            for tc in obj.get('tool_calls', []):
                if 'CandidatePortalController.cs' in str(tc.get('args')):
                    print(f"Step {idx}: Target len={len(tc['args'].get('Target', ''))}, Replacement len={len(tc['args'].get('Replacement', ''))}")

