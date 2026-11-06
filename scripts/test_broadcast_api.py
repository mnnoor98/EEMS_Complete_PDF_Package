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
        return json.loads(resp.read().decode('utf-8'))

# 1. Login
auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'noor', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'

# 2. Get existing broadcast logs
logs = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/broadcasts', headers=headers)
print(f"Existing broadcast logs count: {len(logs)}")
for l in logs:
    print(f"  [{l['channel']}] ({l['templateType']}) -> {l['recipientCount']} agents | {l['status']} | {l['messageContent'][:60]}...")

# 3. Send test SMS broadcast
sms_req = {
    'channel': 'SMS',
    'recipientGroup': 'POLLING_AGENTS',
    'targetAgentType': 'ALL',
    'templateType': 'MORNING_CHECKIN',
    'messageContent': 'জরুরি নির্দেশ: প্রিয় পোলিং এজেন্ট, সকাল ৭:৩০ এর মধ্যে কেন্দ্রে প্রবেশ করুন ও ব্যালট বাক্স পরীক্ষা করে সিল নিশ্চিত করুন। - ডঃ কাজী উবায়েদ উল্লাহ ফারুক (দাঁড়িপাল্লা)'
}
res_sms = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/broadcasts', sms_req, method='POST', headers=headers)
print("\nSMS Broadcast Response:", res_sms)

# 4. Send test WhatsApp broadcast
wa_req = {
    'channel': 'WHATSAPP',
    'recipientGroup': 'POLLING_AGENTS',
    'targetAgentType': 'PRIMARY',
    'templateType': 'FORM8_REMINDER',
    'messageContent': 'ভোট গণনা সমাপ্ত। প্রিজাইডিং অফিসারের স্বাক্ষরিত ফরম-৮ এর ছবি অবিলম্বে হোয়াটসঅ্যাপে পাঠান। - প্রধান নির্বাচনী এজেন্ট'
}
res_wa = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/broadcasts', wa_req, method='POST', headers=headers)
print("\nWhatsApp Broadcast Response:", res_wa)

# 5. Verify updated logs
updated_logs = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/broadcasts', headers=headers)
print(f"\nUpdated broadcast logs count: {len(updated_logs)}")
assert len(updated_logs) >= len(logs) + 2, "Should have added at least 2 new logs"

print("\n>>> ALL BROADCAST BACKEND APIs 100% OPERATIONAL! <<<")

