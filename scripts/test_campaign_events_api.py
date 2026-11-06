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

# 2. Get venues
venues = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/campaign-venues', headers=headers)
print(f"Venues count: {len(venues)}")
for v in venues:
    print(f" - [{v['venueId']}] {v['name']} ({v['address']}) [Cap: {v['capacity']}]")

# 3. Get existing campaign events
events = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/campaign-events', headers=headers)
print(f"\nExisting campaign events count: {len(events)}")
for e in events:
    print(f" - [{e['eventId']}] {e['title']}")
    print(f"   Type: {e['eventTypeName']} | Venue: {e['venueName']} | Authority: {e['issuingAuthority']} | Permit: {e['permitStatus']} ({e['permitReferenceNumber']}) | Miking Compliant: {e['isMikingHoursCompliant']}")

# 4. Create new campaign event with sound hours check (e.g. 15:00 - 18:00 BST = UTC 09:00 - 12:00)
new_event_req = {
    'title': 'মৌলভীবাজার সরকারি প্রাথমিক বিদ্যালয় মাঠে ওয়ার্ড সমাবেশ ও ভোটার মতবিনিময়',
    'eventTypeId': 1,
    'venueId': venues[0]['venueId'] if venues else None,
    'startsAt': '2026-11-25T09:00:00Z', # 15:00 BST (+06:00)
    'endsAt': '2026-11-25T12:00:00Z',   # 18:00 BST (+06:00)
    'issuingAuthority': 'দাগনভূঞা থানা পুলিশ ও সহকারী রিটার্নিং অফিসার',
    'permitReferenceNumber': 'ডিবি-নির্বাচন/পারমিট-আবেদন/২০২৬/৮৮',
    'permitStateId': 2 # APPROVED
}
created_event = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/campaign-events', new_event_req, method='POST', headers=headers)
print(f"\nCreated Event: {created_event['title']}")
print(f"  Event ID: {created_event['eventId']}, Permit: {created_event['permitStatus']}, Miking Compliant: {created_event['isMikingHoursCompliant']}")

# 5. Test permit patch
patch_req = {
    'permitStateId': 2,
    'issuingAuthority': 'সহকারী রিটার্নিং অফিসার ও উপজেলা নির্বাহী অফিসার (ইউএনও)',
    'permitReferenceNumber': 'ইউএনও/দাগন/অনুমোদন-২০২৬/৩৪৭'
}
req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/campaign-events/{created_event['eventId']}/permit', patch_req, method='PATCH', headers=headers)
print("\nPermit updated successfully via PATCH.")

print("\nALL BACKEND CAMPAIGN EVENT TESTS PASSED!")

