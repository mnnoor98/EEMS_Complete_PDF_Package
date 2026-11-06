import json

with open('C:/Users/noor/.gemini/antigravity/brain/6444be1b-5e50-4fdb-83cf-19b9e05f089f/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if 'record TestSmsRequest' in line:
            obj = json.loads(line)
            print("Step:", obj.get('step_index'))
            for tc in obj.get('tool_calls', []):
                args = tc.get('args', {})
                for k, v in args.items():
                    if 'record TestSmsRequest' in str(v):
                        print(f"Key {k}: {v[:400]}")

