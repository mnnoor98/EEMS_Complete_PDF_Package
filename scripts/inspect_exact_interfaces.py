with open('frontend/src/app/core/models/api.models.ts', 'r', encoding='utf-8') as f:
    text = f.read()

def show_interface(name):
    idx = text.find(f'interface {name}')
    if idx == -1:
        idx = text.find(f'type {name}')
    if idx != -1:
        end = text.find('}', idx)
        print(f"=== {name} ===")
        print(text[idx:end+1])
    else:
        print(f"NOT FOUND: {name}")

show_interface('CandidateElectionResultsSummary')
show_interface('EcExpenseScheduleReport')
show_interface('SendVoterBroadcastResponse')
show_interface('CreateCampaignEventRequest')
show_interface('CandidateWarRoomHero')

