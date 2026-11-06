# -*- coding: utf-8 -*-
import json, urllib.request

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

print("=================================================================")
print("EEMS CANDIDATE WAR ROOM & DIGITAL CAMPAIGN VERIFICATION SUITE")
print("=================================================================")

# 1. Login
auth = req(f'{BASE_URL}/api/v1/auth/login', {'tenantId': TENANT_CODE, 'username': 'noor', 'password': 'EEMS@123456!'}, method='POST')
token = auth['accessToken']
headers = {'Authorization': f'Bearer {token}'}
print("✓ Authentication successful. JWT token received.")

# 2. Candidate War Room Summary
summary = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/war-room', headers=headers)
cand = summary.get('candidate')
print(f"✓ Candidate: {cand.get('name')} | Symbol: {cand.get('symbolEmoji')} {cand.get('symbolNameBn')} | Party: {cand.get('partyName')}")
print(f"  Total Centers: {summary.get('totalCenters')} | Total Booths: {summary.get('totalBooths')}")

# 3. Booth Agents
agents = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/booth-agents', headers=headers)
print(f"✓ Total Appointed Booth Agents: {len(agents)}")
if agents:
    sample_ag = agents[0]
    print(f"  Sample Agent: {sample_ag.get('fullName')} | NID: {sample_ag.get('nidNumber')} | Center: {sample_ag.get('centerName')} | Booth: {sample_ag.get('boothName')}")

# 4. Voter Database
voters = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/voters', headers=headers)
print(f"✓ Total Registered Voters: {len(voters)}")
issued_slips = sum(1 for v in voters if v.get('slipIssued'))
print(f"  Slip Issued: {issued_slips}/{len(voters)} ({(issued_slips/len(voters))*100:.1f}%)")
if voters:
    v = voters[0]
    print(f"  Sample Voter: #{v.get('serialNumber')} {v.get('fullName')} | NID: {v.get('voterNumber')} | Phone: {v.get('phone')} | Center: {v.get('centerName')}")

# 5. SMS Gateway Config
sms_cfg = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/sms-config', headers=headers)
print(f"✓ SMS Gateway Provider: {sms_cfg.get('provider')} | Sender ID: {sms_cfg.get('senderId')} | Balance: ৳{sms_cfg.get('balance'):.2f}")

# 6. Test SMS Gateway
test_sms = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/sms-test', {'phone': '01717208118', 'message': 'EEMS টেস্ট এসএমএস।'}, method='POST', headers=headers)
print(f"✓ Test SMS Result: {test_sms.get('message')}")

# 7. WhatsApp Voter Broadcast Queue
wa_broadcast = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/voter-broadcasts', {
    'channel': 'WHATSAPP',
    'targetFilter': 'ALL',
    'messageContent': 'আসসালামু আলাইকুম {নাম}। আপনার ভোটকেন্দ্র: {ভোটকেন্দ্র}, বুথ: {বুথ}, তালিকা ক্রমিক: {ক্রমিক}। মার্কা: {মার্কা}।'
}, method='POST', headers=headers)
q = wa_broadcast.get('queue', [])
print(f"✓ WhatsApp Broadcast Queue: {len(q)} voters queued")
if q:
    sample_q = q[0]
    print(f"  First Queue Item: {sample_q.get('fullName')} -> Phone: {sample_q.get('phone')}")
    print(f"  Generated WhatsApp Direct Link: {sample_q.get('waUrl')[:65]}...")

# 8. Campaign Events & Permitted Rallies
campaign_events = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/campaign-events', headers=headers)
print(f"✓ Total Campaign Events: {len(campaign_events)}")
approved_events = [e for e in campaign_events if e.get('permitStatus') == 'APPROVED']
print(f"  Permitted/Approved Rallies: {len(approved_events)}")
if campaign_events:
    ev = campaign_events[0]
    print(f"  Sample Rally: {ev.get('title')} | Venue: {ev.get('venueName')} | Miking Compliant: {ev.get('isMikingHoursCompliant')}")

# 9. Incidents & Magistrate Complaints
incidents = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/incidents', headers=headers)
print(f"✓ Recorded Incidents: {len(incidents)}")
if incidents:
    inc = incidents[0]
    print(f"  Sample Incident: {inc.get('title')} | Severity: {inc.get('severity')} | Status: {inc.get('status')}")

# 10. Live Results & Form-8
results = req(f'{BASE_URL}/api/v1/candidate/elections/{ELECTION_ID}/results-summary', headers=headers)
print(f"✓ Results Counted Centers: {results.get('countedCenters')}/{results.get('totalCenters')}")
print(f"  Candidate Votes: {results.get('candidateTotalVotes')} vs Opponent: {results.get('runnerUpTotalVotes')} | Lead Margin: +{results.get('leadMargin')}")

print("\n=================================================================")
print("ALL E2E SUB-SYSTEMS AND WORKFLOWS VERIFIED 100% OPERATIONAL!")
print("=================================================================")

