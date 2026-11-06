FILE_PATH = r'G:\dotnetproject\EEMS_Complete_PDF_Package\frontend\src\app\features\candidates\candidate-war-room.page.ts'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's inspect ts_methods from patch_candidate_war_room.py
import patch_candidate_war_room

target = "  deleteCampaignEvent(ev: CandidateCampaignEventItem) {"
pos = content.rfind(target)
if pos != -1:
    # Find the end of this method (the next `  }\n\n}`) or `  }\r\n\r\n}`
    end_method = content.find("  }", pos)
    if end_method != -1:
        # End of method is after `  }`
        insert_pos = end_method + 3
        # Check if there is another `}` closing the class
        content = content[:insert_pos] + "\n\n" + patch_candidate_war_room.ts_methods + "\n" + content[insert_pos:]
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print("SUCCESSFULLY injected TypeScript methods!")
    else:
        print("end_method not found")
else:
    print("target not found")

