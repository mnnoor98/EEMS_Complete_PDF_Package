import json, urllib.request, base64

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
        content_type = resp.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return json.loads(resp.read().decode('utf-8'))
        else:
            return resp.read()

# 1. Login as user 'noor' (or admin)
auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'noor', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}

ELECTION_ID = 'eade9993-71f5-4bbc-b92c-b636333a2714'
center_id = '0f0e14b3-b1eb-4f0a-bfe0-b60454e4bdd3'
cand_id = 'e2fff660-830e-40a9-ab69-edbf8473e55d'

print("[1] Logged in successfully as user 'noor'")

# 2. Verify candidate Bangla strings
candidates = req(f'{BASE_URL}/api/v1/candidate/candidates', headers=headers)
print(f"[2] Loaded {len(candidates)} candidates. Checking for clean Bengali text:")
for c in candidates:
    print(f"  - {c['name']} | Symbol: {c.get('symbolEmoji','')} {c.get('symbolName','')} | Party: {c.get('partyName','')}")
    assert 'à¦' not in c['name'], f"Mojibake found in name: {c['name']}"

# 3. Test multi-candidate quick result submit
votes_list = [
    {'candidateId': cand_id, 'votes': 2150},
    {'candidateId': '0d1f7c32-b91c-4395-857c-cb0b784aa002', 'votes': 1720},
    {'candidateId': '0d1f7c32-b91c-4395-857c-cb0b784aa003', 'votes': 540},
    {'candidateId': '0d1f7c32-b91c-4395-857c-cb0b784aa004', 'votes': 190}
]

sub_res = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/quick-result', {
    'electionCenterId': center_id,
    'candidateVotesList': votes_list,
    'candidateId': cand_id
}, method='POST', headers=headers)
print(f"[3] Quick result submitted successfully: {sub_res}")

# 4. Upload Form-8 Presiding Officer duplicate sheet
dummy_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
b64_img = 'data:image/png;base64,' + base64.b64encode(dummy_png).decode('utf-8')

form8_req = {
    'documentData': b64_img,
    'fileName': 'form8_presiding_officer_sheet.png',
    'presidingOfficerName': 'মোঃ শফিকুল ইসলাম (প্রিজাইডিং অফিসার)',
    'presidingOfficerPhone': '01819234567',
    'cancelledVotes': 45,
    'isVerified': True,
    'verificationNote': 'ফরম-৮ কার্বন কপি প্রিজাইডিং অফিসারের স্বাক্ষরসহ যাচাইকৃত ও শতভাগ নির্ভুল।'
}

form8_res = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/centers/{center_id}/form8', form8_req, method='POST', headers=headers)
print(f"[4] Form-8 uploaded & verified: {form8_res}")

# 5. Check Form-8 file streaming
form8_bytes = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/centers/{center_id}/form8/file', headers=headers)
print(f"[5] Form-8 file streamed successfully, size: {len(form8_bytes)} bytes")
assert len(form8_bytes) > 0, "Form-8 file streaming returned empty bytes"

# 6. Verify Results Summary includes Form-8 verification and Presiding Officer metadata
summary = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/results-summary?candidateId={cand_id}', headers=headers)
print(f"[6] Result Summary: LeadMargin={summary['leadMargin']}, Winner={summary['candidateName']}")
center_item = summary['centerResults'][0]
print(f"    Center: {center_item['centerName']}")
print(f"    Form8 Document URL: {center_item.get('form8DocumentUrl')}")
print(f"    Presiding Officer: {center_item.get('presidingOfficerName')}")
print(f"    PO Phone: {center_item.get('presidingOfficerPhone')}")
print(f"    Form-8 Verified: {center_item.get('form8Verified')}")
print(f"    Cancelled Votes: {center_item.get('cancelledVotes')}")

assert center_item.get('form8Verified') == True, "Center result Form-8 should be verified"
assert 'মোঃ শফিকুল ইসলাম' in (center_item.get('presidingOfficerName') or ''), "Presiding officer name should match"

print("\n>>> ALL TESTS PASSED! Form-8 & Result Flow 100% OPERATIONAL! <<<")

