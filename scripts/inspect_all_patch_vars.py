import re

def check_file(path, name):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()
        print(f"=== {name} ({len(c)} bytes) ===")
        # find variables defined in script
        var_names = re.findall(r'(\w+)\s*=\s*"""', c)
        print("Multiline vars:", var_names)
    except Exception as e:
        print(f"Error {name}: {e}")

check_file('scripts/patch_batch_id_card.py', 'Batch ID Card')
check_file('scripts/patch_form8_and_lead_chart.py', 'Form-8 & Lead Chart')
check_file('scripts/patch_magistrate_complaint.py', 'Magistrate Complaint')
check_file('scripts/patch_campaign_events_full.py', 'Campaign Events')
check_file('scripts/patch_candidate_war_room.py', 'Smart Voter Slip & Broadcast')

