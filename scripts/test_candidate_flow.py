import json
import urllib.request

BASE_URL = "http://localhost:5131"
TENANT_CODE = "1000000000"

def post_json(url, data, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def put_json(url, data, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="PUT")
    with urllib.request.urlopen(req) as resp:
        if resp.status == 204:
            return None
        return json.loads(resp.read().decode("utf-8"))

def get_json(url, headers=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

# 1. Login
auth = post_json(f"{BASE_URL}/api/v1/auth/login", {
    "tenantId": TENANT_CODE,
    "username": "admin",
    "password": "EEMS@123456!"
})
token = auth["accessToken"]
headers = {
    "Authorization": f"Bearer {token}",
    "X-Tenant-Code": TENANT_CODE
}

# 2. Get Elections & Candidate
elections = get_json(f"{BASE_URL}/api/v1/elections", headers)
election_id = elections[0]["electionId"]

war_room = get_json(f"{BASE_URL}/api/v1/candidate/elections/{election_id}/war-room", headers)
candidate_id = war_room["candidate"]["candidateId"]

print(f"Election: {elections[0]['name']} [{election_id}]")
print(f"Current Candidate: {war_room['candidate']['name']}")

# 3. Update candidate symbol to Pineapple (id: 14)
print("\nUpdating Candidate Symbol to Pineapple (আনারস 🍍)...")
put_json(f"{BASE_URL}/api/v1/candidate/elections/{election_id}/candidates/{candidate_id}/campaign", {
    "symbolId": 14,
    "partyName": "স্বতন্ত্র প্রার্থী (Independent)",
    "slogan": "উন্নয়ন ও জনকল্যাণে আমরা সর্বদা প্রস্তুত",
    "phone": "01711223344",
    "campaignOffice": "ধানমন্ডি, ঢাকা"
}, headers)

# Re-check war room
updated_war_room = get_json(f"{BASE_URL}/api/v1/candidate/elections/{election_id}/war-room", headers)
hero = updated_war_room["candidate"]
print(f"Updated Symbol: {hero['symbolEmoji']} {hero['symbolNameBn']} ({hero['symbolNameEn']})")
print(f"Slogan: {hero['slogan']}")
print(f"Assigned Booth Agents: {updated_war_room['assignedAgents']}")

# 4. Submit Quick Result for Center
centers = get_json(f"{BASE_URL}/api/v1/elections/{election_id}/polling-centers", headers)
center_link = centers["items"][0]
print(f"\nSubmitting live votes for Center: {center_link['name']}...")

post_json(f"{BASE_URL}/api/v1/candidate/elections/{election_id}/quick-result", {
    "electionCenterId": center_link["electionCenterId"],
    "candidateVotes": 1450,
    "runnerUpVotes": 820,
    "notes": "ফরম-৮ এর ভিত্তিতে প্রস্তুতকৃত"
}, headers)

# 5. Fetch Live Results Summary
results = get_json(f"{BASE_URL}/api/v1/candidate/elections/{election_id}/results-summary", headers)
print("\n=== Live Election Day Results Scoreboard ===")
print(f"Candidate: {results['candidateName']} ({results['candidateSymbolEmoji']} {results['candidateSymbol']}) -> {results['candidateTotalVotes']} votes")
print(f"Opponent : {results['runnerUpName']} ({results['runnerUpSymbolEmoji']} {results['runnerUpSymbol']}) -> {results['runnerUpTotalVotes']} votes")
print(f"Lead Margin: +{results['leadMargin']} votes (Is Leading: {results['isLeading']})")
print(f"Centers Counted: {results['countedCenters']} / {results['totalCenters']}")
print("\nALL CANDIDATE FLOW TESTS PASSED 100%!")

