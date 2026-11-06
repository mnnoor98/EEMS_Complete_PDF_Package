import json, urllib.request

BASE_URL = 'http://localhost:5131'
TENANT_CODE = '1000000000'

def req(url, data=None, method='GET', headers=None):
    h = headers.copy() if headers else {}
    h['X-Tenant-Code'] = TENANT_CODE
    body = None
    if data is not None:
        h['Content-Type'] = 'application/json'
        body = json.dumps(data).encode('utf-8')
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(r) as resp:
        content = resp.read()
        if not content:
            return None
        return json.loads(content.decode('utf-8'))

# 1. Login
auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'noor', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
print("=== VERIFYING OPTION 2: SMS & WHATSAPP BROADCAST GATEWAY ===")
broadcasts = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/broadcasts', headers=headers)
print(f"Total Broadcasts in Outbox: {len(broadcasts)}")
for b in broadcasts[-3:]:
    print(f" - [{b['channel']}] Template: {b['templateType']} | To: {b['recipientCount']} agents | Status: {b['status']}")

print("\n=== VERIFYING OPTION 3: CAMPAIGN EVENTS, RALLIES & PERMITS ===")
venues = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/campaign-venues', headers=headers)
print(f"Available Venues in Area: {len(venues)}")
for v in venues:
    print(f" - {v['name']} | Cap: {v['capacity']} | Addr: {v['address']}")

events = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/campaign-events', headers=headers)
print(f"\nTotal Campaign Events: {len(events)}")
for e in events:
    print(f" - Title: {e['title']}")
    print(f"   Type: {e['eventTypeName']} | Venue: {e['venueName']} | Authority: {e['issuingAuthority']}")
    print(f"   Permit Status: {e['permitStatus']} (Ref: {e['permitReferenceNumber']}) | Miking Compliant: {e['isMikingHoursCompliant']}")

# Verify adding a compliant miking rally (starts 3:00 PM = 15:00 BST, ends 6:00 PM = 18:00 BST)
new_rally = {
    'title': 'দাগনভূঞা ডাকবাংলো চত্বরে প্রার্থীর নির্বাচনী শেষ প্রস্তুতি পথসমাবেশ',
    'eventTypeId': 1,
    'venueId': venues[1]['venueId'] if len(venues) > 1 else None,
    'startsAt': '2026-11-26T09:00:00Z', # 15:00 BST
    'endsAt': '2026-11-26T12:00:00Z',   # 18:00 BST
    'issuingAuthority': 'দাগনভূঞা থানা পুলিশ ও সহকারী রিটার্নিং অফিসার',
    'permitReferenceNumber': 'ডিবি-নির্বাচন/পারমিট/২০২৬/৩১০',
    'permitStateId': 2 # APPROVED
}
created_rally = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/campaign-events', new_rally, method='POST', headers=headers)
print(f"\nSuccessfully added test rally: {created_rally['title']}")
print(f"  Event ID: {created_rally['eventId']}")
print(f"  Permit: {created_rally['permitStatus']} ({created_rally['permitReferenceNumber']})")
print(f"  Is Miking Hours Compliant: {created_rally['isMikingHoursCompliant']}")
assert created_rally['isMikingHoursCompliant'] == True, "Rally from 3 PM to 6 PM must be miking compliant"

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

