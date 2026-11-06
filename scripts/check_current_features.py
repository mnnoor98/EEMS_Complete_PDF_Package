with open('frontend/src/app/features/candidates/candidate-war-room.page.ts', 'r', encoding='utf-8') as f:
    text = f.read()

features = [
    'Batch ID Card',
    'openBatchIdCardsModal',
    'Form-8',
    'openForm8Modal',
    'Magistrate',
    'openComplaintLetter',
    'Voters',
    'loadVoters',
    'Campaign',
    'loadCampaignEvents',
    'openSmartSlip',
    'openVoterBroadcastModal',
    'openSmsConfigModal'
]

for ft in features:
    print(f"{ft}: {'YES' if ft in text else 'NO'}")

