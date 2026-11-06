import urllib.request, json

# 1. Login as super admin (or noor)
login_data = json.dumps({'tenantId': '1000000000', 'username': 'noor', 'password': 'EEMS@123456!'}).encode('utf-8')
req = urllib.request.Request('http://localhost:5131/api/v1/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode())['accessToken']

headers = {'Authorization': f'Bearer {token}', 'X-Tenant-Code': '1000000000'}
req2 = urllib.request.Request('http://localhost:5131/api/v1/candidate/master-overview', headers=headers)
with urllib.request.urlopen(req2) as resp2:
    data = json.loads(resp2.read().decode())
    print('Master overview endpoint SUCCESS! Total items:', len(data))
    for it in data:
        print(f"👉 [{it['symbolEmoji']} {it['symbolName']}] {it['candidateName']} ({it['partyName']}) | User: {it['primaryUsername']} | Team: {it['teamCount']} | Agents: {it['agentCount']} | Voters: {it['voterCount']} ({it['slipPercentage']}%) | Votes: {it['totalVotes']}")

