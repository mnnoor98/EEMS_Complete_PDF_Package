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
            return {'status_code': resp.status}
        return json.loads(content.decode('utf-8'))

# 1. Login
auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'noor', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
cand_id = 'e2fff660-830e-40a9-ab69-edbf8473e55d'
center_id = '27a07512-2dec-4c89-b0e3-df026e534577'

# 2. Create emergency incident
incident_req = {
    'centerId': center_id,
    'incidentType': 'BOOTH_AGENT_EXPELLED',
    'severity': 'CRITICAL',
    'title': '১ নং ভোটকক্ষ হইতে পোলিং এজেন্টকে বলপ্রয়োগে বহিষ্কার ও কেন্দ্র দখলের অপচেষ্টা',
    'description': 'অদ্য সকাল ১০:১৫ ঘটিকায় কতিপয় বহিরাগত সশস্ত্র সন্ত্রাসী ভোটকক্ষে প্রবেশ করিয়া আমাদের পোলিং এজেন্ট মোঃ শফিকুল ইসলামকে মারধর করিয়া মোবাইল কাড়িয়া নেয় এবং জোরপূর্বক ভোটকেন্দ্র হইতে বাহির করিয়া দেয়। তারা প্রিজাইডিং অফিসারকে জিম্মি করিয়া ব্যালট ছিনতাইয়ের চেষ্টা করিতেছে।',
    'reportedBy': 'মোঃ শফিকুল ইসলাম (পোলিং এজেন্ট)',
    'reportedByPhone': '01717208118',
    'candidateId': cand_id
}

created = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/incidents', incident_req, method='POST', headers=headers)
print("[1] Incident created successfully:")
inc_id = created['id']
print(f"  ID: {inc_id}")
print(f"  Title: {created['title']}")
print(f"  Center: {created['centerName']}")
print(f"  Severity: {created['severity']}")
print(f"  Status: {created['status']}")

# 3. Update status to SUBMITTED_TO_EC
status_url = f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/incidents/{inc_id}/status'
updated = req(status_url, {
    'status': 'SUBMITTED_TO_EC',
    'actionTaken': 'সহকারী রিটার্নিং অফিসার (ARO) ও বিজ্ঞ জুডিশিয়াল ম্যাজিস্ট্রেট বরাবরে আনুষ্ঠানিক লিখিত অভিযোগপত্র দাখিল করা হইয়াছে। স্ট্রাইকিং ফোর্স কেন্দ্রে পৌঁছাইয়া পরিস্থিতি নিয়ন্ত্রণে আনিয়াছে।',
    'magistrateName': 'আহমেদ মোরশেদ (বিজ্ঞ জুডিশিয়াল ম্যাজিস্ট্রেট)'
}, method='PUT', headers=headers)
print(f"\n[2] Status escalated to SUBMITTED_TO_EC (HTTP {updated.get('status_code', 200)})")

# 4. Fetch all incidents and verify update
incidents = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/incidents', headers=headers)
found = next((i for i in incidents if i['id'] == inc_id), None)
assert found is not None, "Created incident should exist in list"
print(f"\n[3] Verified incident in database:")
print(f"  Status: {found['status']}")
print(f"  Action Taken: {found['actionTaken']}")
print(f"  Magistrate: {found['magistrateName']}")
assert found['status'] == 'SUBMITTED_TO_EC', "Status should be SUBMITTED_TO_EC"

print("\n>>> ALL INCIDENT & MAGISTRATE NOTICE FLOWS 100% OPERATIONAL! <<<")
