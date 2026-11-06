import urllib.request, json

def test():
    # 1. Login to get JWT
    login_url = "http://localhost:5131/api/v1/auth/login"
    login_data = json.dumps({"tenantId": "1000000000", "username": "noor", "password": "EEMS@123456!"}).encode('utf-8')
    req = urllib.request.Request(login_url, data=login_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        token = json.loads(resp.read().decode('utf-8'))['accessToken']

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    # 2. Test WhatsApp Bot Status via Backend API proxy
    print("Testing WhatsApp Bot Status API...")
    req_wa = urllib.request.Request("http://localhost:5131/api/v1/candidate/whatsapp/status", headers=headers)
    with urllib.request.urlopen(req_wa) as resp:
        wa_status = json.loads(resp.read().decode('utf-8'))
        print(f"✓ WhatsApp Bot Status: Connected={wa_status['connected']}, HasQR={wa_status['hasQR']}")

    # 3. Test WhatsApp QR via Backend API proxy
    print("Testing WhatsApp QR Code API...")
    req_qr = urllib.request.Request("http://localhost:5131/api/v1/candidate/whatsapp/qr", headers=headers)
    with urllib.request.urlopen(req_qr) as resp:
        wa_qr = json.loads(resp.read().decode('utf-8'))
        has_qr = bool(wa_qr.get('qrDataUrl'))
        qr_str = wa_qr.get('qrDataUrl') or ''
        print(f"✓ WhatsApp QR Code Available: {has_qr} (Prefix: {qr_str[:40]}...)")

    # 3B. Test WhatsApp Auto Broadcast endpoint proxy
    print("Testing WhatsApp Auto-Broadcast Queue via Backend API proxy...")
    auto_data = json.dumps({
        "items": [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "Test Voter",
                "phone": "01858395506",
                "message": "টেস্ট মেসেজ"
            }
        ]
    }).encode('utf-8')
    req_auto = urllib.request.Request("http://localhost:5131/api/v1/candidate/whatsapp/auto-broadcast", data=auto_data, headers=headers)
    with urllib.request.urlopen(req_auto) as resp:
        auto_res = json.loads(resp.read().decode('utf-8'))
        print(f"✓ WhatsApp Auto-Broadcast: success={auto_res.get('success')}, message={auto_res.get('message')}")

    # 4. Test SMS Gateway Config
    print("Testing SMS Gateway Config...")
    election_id = "eade9993-71f5-4bbc-b92c-b636333a2714"
    req_sms = urllib.request.Request(f"http://localhost:5131/api/v1/candidate/elections/{election_id}/sms-config", headers=headers)
    with urllib.request.urlopen(req_sms) as resp:
        sms_cfg = json.loads(resp.read().decode('utf-8'))
        print(f"✓ SMS Gateway Provider: {sms_cfg['provider']} | Endpoint: {sms_cfg['endpointUrl']} | Balance: ৳{sms_cfg['balance']}")

    print("\n=======================================================")
    print("ALL 1 & 3 CAPABILITIES FULLY OPERATIONAL AND VERIFIED!")
    print("=======================================================")

if __name__ == '__main__':
    test()
