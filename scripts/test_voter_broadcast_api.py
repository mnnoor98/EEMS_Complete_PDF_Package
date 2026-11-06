import urllib.request, json

BASE_URL = 'http://localhost:5131'
TENANT_CODE = '1000000000'
ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'

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

print("=== 1. TEST GET SMS CONFIG ===")
sms_config = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/sms-config', headers=headers)
print("SMS Config:", sms_config)

print("\n=== 2. TEST SMS GATEWAY CONFIG UPDATE ===")
updated_config = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/sms-config', {
    'provider': 'SIMULATOR',
    'apiKey': 'test_sim_key_2026',
    'senderId': 'SCALE_FARUK',
    'endpointUrl': 'http://api.greenweb.com.bd/api.php',
    'isActive': True
}, method='POST', headers=headers)
print("Updated Config:", updated_config)

print("\n=== 3. TEST SEND TEST SMS ===")
test_sms = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/sms-test', {
    'phone': '01717208118',
    'message': 'টেস্ট এসএমএস: ৫ নং ইয়াকুবপুর ইউনিয়ন পরিষদ নির্বাচনে প্রার্থীর ডিজিটাল ওয়ার রুম থেকে বার্তা।'
}, method='POST', headers=headers)
print("Test SMS Result:", test_sms)

print("\n=== 4. TEST WHATSAPP VOTER BROADCAST QUEUE ===")
wa_broadcast = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/voter-broadcasts', {
    'channel': 'WHATSAPP',
    'targetFilter': 'ALL',
    'templateType': 'SLIP_NOTICE',
    'messageContent': 'আসসালামু আলাইকুম {নাম}। আপনার ভোটকেন্দ্র: {ভোটকেন্দ্র}, বুথ: {বুথ}, ক্রমিক: {ক্রমিক}। মার্কা: {মার্কা}।'
}, method='POST', headers=headers)
print("WhatsApp Queue Count:", wa_broadcast.get('recipientCount'))
if wa_broadcast.get('queue'):
    first = wa_broadcast['queue'][0]
    print("First in Queue:", first['fullName'], first['phone'])
    print("Pre-composed Message:", first['message'])
    print("WhatsApp URL:", first['waUrl'][:80] + '...')

print("\n=== 5. TEST BULK SMS VOTER BROADCAST ===")
sms_broadcast = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/voter-broadcasts', {
    'channel': 'SMS',
    'targetFilter': 'UNISSUED_SLIP',
    'templateType': 'SLIP_NOTICE',
    'messageContent': 'শ্রদ্ধেয় {নাম}, আপনার কেন্দ্র: {ভোটকেন্দ্র}, বুথ: {বুথ}, ক্রমিক: {ক্রমিক}। দাঁড়িপাল্লা মার্কায় ভোট দিন।'
}, method='POST', headers=headers)
print("SMS Broadcast Result:", sms_broadcast)

print("\nALL VOTER BROADCAST & SMS GATEWAY TESTS PASSED!")

