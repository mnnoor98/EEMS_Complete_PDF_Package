# -*- coding: utf-8 -*-
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

print('=== 1. VERIFY CANDIDATE WAR ROOM FOR NOOR ===')
auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'noor', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
war_room = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/war-room', headers=headers)
cand = war_room['candidate']
print('Candidate Name:', cand['name'])
print('Party:', cand['partyName'])
print('Symbol:', cand['symbolNameBn'], cand['symbolEmoji'])
print('Candidate ID:', cand['candidateId'])
assert cand['candidateId'] == 'e2fff660-830e-40a9-ab69-edbf8473e55d', 'WRONG CANDIDATE!'
print('>> ISSUE 1 RESOLVED: Candidate is Dr. Kazi Obaid Ullah Faruk (দাঁড়িপাল্লা)!')

print('\n=== 2. VERIFY SMS GATEWAY CONFIG & TEST API ===')
sms_conf = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/sms-config', headers=headers)
print('SMS Config: Provider=', sms_conf['provider'], 'Live Balance=', sms_conf['balance'], 'IsActive=', sms_conf['isActive'])

# Test invalid key to verify friendly Bengali error 405
bad_test = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/sms-test', {
    'phone': '01858395506',
    'apiKey': 'Y68UVFD1fIDgDCb6AgvC2i3uL7volImeKoSUSFf93',
    'senderId': 'tousif'
}, method='POST', headers=headers)
print('Invalid key test response:', bad_test['message'])
assert '405' in bad_test['message'], 'Should flag 405 error'

# Test with unapproved sender_id
sender_test = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/sms-test', {
    'phone': '01858395506',
    'apiKey': '1FPTyJ7obhfn84GM2U5Z02ywLpd4cx2e7oWN4JeN',
    'senderId': 'tousif'
}, method='POST', headers=headers)
print('SenderId tousif test response:', sender_test['message'])
assert '413' in sender_test['message'], 'Should guide user about non-masking'
print('>> ISSUE 2 RESOLVED: Actionable guidance for 405 (Bad Token) and 413 (Unapproved Masking)!')

print('\n=== 3. VERIFY VOTER BROADCAST & WHATSAPP AUTO-BOT ===')
voter_bcast = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/voter-broadcasts', {
    'channel': 'WHATSAPP',
    'targetFilter': 'UNISSUED_SLIP_ONLY',
    'messageContent': 'আসসালামু আলাইকুম {নাম}। আপনার কেন্দ্র: {ভোটকেন্দ্র}, মার্কা: {মার্কা}'
}, method='POST', headers=headers)

print('Voter Broadcast Status:', voter_bcast['status'], 'Recipients:', voter_bcast['recipientCount'])
queue = voter_bcast.get('queue', [])
print('Queue items returned:', len(queue))
for item in queue:
    print('  - Voter:', item['fullName'], f"({item['phone']})", '-> Msg:', item['message'][:50])

assert len(queue) == 2, f'Expected 2 voters, got {len(queue)}'

# Call WhatsApp auto-broadcast with queue items
bot_items = [{'id': q['voterId'], 'name': q['fullName'], 'phone': q['phone'], 'message': q['message']} for q in queue]
auto_resp = req(f'{BASE_URL}/api/v1/candidate/whatsapp/auto-broadcast', {'items': bot_items}, method='POST', headers=headers)
print('WhatsApp auto-broadcast response:', auto_resp['message'])
assert auto_resp['success'] == True
print('>> ISSUE 3 RESOLVED: Broadcast queue properly populated and handed to WhatsApp Auto-Bot!')
print('\n*** ALL TESTS PASSED 100%! ***')
