import urllib.request
import json
import uuid

try:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Voters'
    ws.append(['ক্রমিক', 'ভোটার আইডি', 'ভোটারের নাম', 'পিতা বা স্বামীর নাম', 'লিঙ্গ', 'বয়স', 'গ্রাম বা এলাকা', 'ক্যাটাগরি', 'মোবাইল'])
    ws.append([1, '1995111222333', 'কাজী জামিল উদ্দিন', 'মরহুম কাজী ফারুক', 'পুরুষ', 30, 'দক্ষিণ পাড়া', 'সমর্থক', '01700112233'])
    ws.append([2, '1997222333444', 'মোসাঃ আসমা আক্তার', 'কাজী জামিল উদ্দিন', 'মহিলা', 28, 'দক্ষিণ পাড়া', 'সমর্থক', '01800112233'])
    excel_path = 'scripts/test_voters.xlsx'
    wb.save(excel_path)
    with open(excel_path, 'rb') as f:
        excel_bytes = f.read()

    auth_data = json.dumps({'tenantId': '1000000000', 'username': 'admin', 'password': 'EEMS@123456!'}).encode('utf-8')
    req = urllib.request.Request('http://localhost:5131/api/v1/auth/login', data=auth_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        token = json.loads(resp.read().decode('utf-8'))['accessToken']

    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
    lines = [
        f'--{boundary}',
        'Content-Disposition: form-data; name="centerId"',
        '',
        '0f0e14b3-b1eb-4f0a-bfe0-b60454e4bdd3',
        f'--{boundary}',
        'Content-Disposition: form-data; name="file"; filename="test_voters.xlsx"',
        'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '',
        ''
    ]
    body = '\r\n'.join(lines).encode('utf-8') + excel_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')
    req2 = urllib.request.Request('http://localhost:5131/api/v1/candidate/elections/eade9993-71f5-4bbc-b92c-b636333a2714/voters/bulk-import-file', data=body, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    }, method='POST')

    with urllib.request.urlopen(req2) as resp:
        print('EXCEL IMPORT RESULT:', resp.status, resp.read().decode('utf-8'))
except Exception as e:
    print('Excel test error:', e)

