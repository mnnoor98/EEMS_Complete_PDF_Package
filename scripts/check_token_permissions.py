import urllib.request, json, base64

def check_user(username, password):
    url = 'http://localhost:5131/api/v1/auth/login'
    body = json.dumps({'tenantId': '1000000000', 'username': username, 'password': password}).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            token = res['accessToken']
            p_b64 = token.split('.')[1] + '=='
            p_b64 = p_b64.replace('-', '+').replace('_', '/')
            payload = json.loads(base64.b64decode(p_b64).decode('utf-8', errors='ignore'))
            print(f'=== User: {username} ===')
            print('CandidateId:', payload.get('candidate_id'))
            print('IsSuperAdmin:', payload.get('is_super_admin'))
            perms = [v for k, v in payload.items() if 'permission' in k.lower()]
            # or in array
            print('Permissions in token:', payload.get('permission'))
    except Exception as e:
        print(f'User {username} error:', e)

check_user('admin', 'EEMS@123456!')
check_user('noor', 'EEMS@123456!')

