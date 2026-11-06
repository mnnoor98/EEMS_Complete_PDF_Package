import json, urllib.request

BASE_URL = 'http://localhost:5131'
TENANT_CODE = '1000000000'
ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'

def req(url, data=None, method='GET', headers=None):
    h = headers or {}
    h['X-Tenant-Code'] = TENANT_CODE
    body = None
    if data is not None:
        h['Content-Type'] = 'application/json'
        body = json.dumps(data).encode('utf-8')
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(r) as resp:
        content_type = resp.headers.get('Content-Type', '')
        if 'json' in content_type:
            return json.loads(resp.read().decode('utf-8'))
        return resp.read()

# 1. Login as admin
auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'admin', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}

print('=== 1. FETCH INITIAL EC EXPENSE SCHEDULE ===')
sched = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/expenses/ec-schedule', headers=headers)
print(f"Ceiling: {sched['ecCeiling']}, Total Committed: {sched['totalCommitted']}, Remaining: {sched['remainingBudget']}, Utilization: {sched['utilizationPercentage']}%")
print(f"Categories count: {len(sched['categories'])}, Existing Vouchers: {len(sched['vouchers'])}")

print('\n=== 2. ADD EXPENSE VOUCHER 1 (Posters) ===')
v1 = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/expenses', {
    'category': 'প্রচারপত্র, পোস্টার, ব্যানার ও লিফলেট',
    'invoiceNumber': 'VCH-POSTER-01',
    'amount': 45000.00,
    'expenseDate': '2026-11-06',
    'vendorName': 'আল-মদিনা প্রিন্টিং প্রেস (ফেনী)',
    'description': '৫০০০ লিফলেট ও ২০০০ পোস্টার মুদ্রণ',
    'paymentMethod': 'CASH'
}, method='POST', headers=headers)
print('Created Voucher 1:', v1['id'], v1['invoiceNumber'], v1['amount'], v1['vendorName'], v1['paymentMethod'])

print('\n=== 3. ADD EXPENSE VOUCHER 2 (Sound System / Rally) ===')
v2 = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/expenses', {
    'category': 'পথসভা, জনসভা, মাইকিং ও সাউন্ড',
    'invoiceNumber': 'VCH-SOUND-01',
    'amount': 30000.00,
    'expenseDate': '2026-11-06',
    'vendorName': 'স্টার সাউন্ড অ্যান্ড লাইটিং',
    'description': 'ইয়াকুবপুর বাজারে কেন্দ্রীয় নির্বাচনী জনসভার মাইক ও সাউন্ড সিস্টেম',
    'paymentMethod': 'BANK_CHEQUE'
}, method='POST', headers=headers)
print('Created Voucher 2:', v2['id'], v2['invoiceNumber'], v2['amount'], v2['vendorName'], v2['paymentMethod'])

print('\n=== 4. ADD EXPENSE VOUCHER 3 (Polling Agent & Volunteer Refreshments) ===')
v3 = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/expenses', {
    'category': 'কর্মী ও পোলিং এজেন্ট ভাতা/আপ্যায়ন',
    'invoiceNumber': 'VCH-AGENT-01',
    'amount': 25000.00,
    'expenseDate': '2026-11-06',
    'vendorName': 'বিসমিল্লাহ হোটেল অ্যান্ড রেস্টুরেন্ট',
    'description': 'পোলিং এজেন্ট প্রশিক্ষণ কর্মশালার মধ্যাহ্নভোজ ও নাস্তা',
    'paymentMethod': 'BKASH'
}, method='POST', headers=headers)
print('Created Voucher 3:', v3['id'], v3['invoiceNumber'], v3['amount'], v3['vendorName'], v3['paymentMethod'])

print('\n=== 5. FETCH UPDATED EC EXPENSE SCHEDULE ===')
sched_after = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/expenses/ec-schedule', headers=headers)
print(f"Ceiling: {sched_after['ecCeiling']}, Total Committed: {sched_after['totalCommitted']}, Remaining: {sched_after['remainingBudget']}, Utilization: {sched_after['utilizationPercentage']}%")
print(f"Vouchers count: {len(sched_after['vouchers'])}")
for v in sched_after['vouchers']:
    print(f"  - [{v['invoiceNumber']}] {v['categoryBn']} | {v['vendorName']} | ৳{v['amount']} | {v['paymentMethod']} | {v['description']}")

print('\n=== 6. DOWNLOAD STATUTORY CSV REPORT ===')
csv_bytes = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/expenses/ec-schedule/csv', headers=headers)
print('CSV size in bytes:', len(csv_bytes))
csv_text = csv_bytes.decode('utf-8')
print('CSV Preview:\n' + '\n'.join(csv_text.splitlines()[:15]))

print('\n=== TEST SUCCESSFUL ===')

