# -*- coding: utf-8 -*-
with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update TestSmsRequest record
old_record = '''public sealed record TestSmsRequest(
    [Required] string Phone,
    string? Message);'''

new_record = '''public sealed record TestSmsRequest(
    [Required] string Phone,
    string? Message,
    string? ApiKey = null,
    string? SenderId = null,
    string? Provider = null,
    string? EndpointUrl = null);'''

if old_record in text:
    text = text.replace(old_record, new_record, 1)
    print("Updated TestSmsRequest record in CandidatePortalController.cs!")
else:
    print("old_record not found!")

# 2. Update TestSmsGateway implementation to prioritize request params and auto-save
old_impl_start = '        string provider = "SMS_NET_BD";\n        string apiKey = "";\n        string senderId = "";\n        string endpointUrl = "https://api.sms.net.bd/sendsms";'

new_impl_start = '''        string provider = !string.IsNullOrWhiteSpace(request.Provider) ? request.Provider.Trim() : "SMS_NET_BD";
        string apiKey = !string.IsNullOrWhiteSpace(request.ApiKey) ? request.ApiKey.Trim() : "";
        string senderId = request.SenderId != null ? request.SenderId.Trim() : "";
        string endpointUrl = !string.IsNullOrWhiteSpace(request.EndpointUrl) ? request.EndpointUrl.Trim() : "https://api.sms.net.bd/sendsms";'''

if old_impl_start in text:
    text = text.replace(old_impl_start, new_impl_start, 1)
    print("Updated variable initialization in TestSmsGateway!")

# When reading DB config, only fallback if apiKey was not passed in request
old_db_read = '''            if (await reader.ReadAsync(token))
            {
                provider = reader.GetString(0);
                apiKey = reader.GetString(1);
                senderId = reader.IsDBNull(2) ? "" : reader.GetString(2);
                endpointUrl = reader.IsDBNull(3) ? "https://api.sms.net.bd/sendsms" : reader.GetString(3);
            }'''

new_db_read = '''            if (await reader.ReadAsync(token))
            {
                if (string.IsNullOrWhiteSpace(apiKey)) apiKey = reader.GetString(1);
                if (string.IsNullOrWhiteSpace(senderId)) senderId = reader.IsDBNull(2) ? "" : reader.GetString(2);
                if (string.IsNullOrWhiteSpace(provider) || provider == "SMS_NET_BD") provider = reader.GetString(0);
                if (string.IsNullOrWhiteSpace(endpointUrl) || endpointUrl == "https://api.sms.net.bd/sendsms") endpointUrl = reader.IsDBNull(3) ? "https://api.sms.net.bd/sendsms" : reader.GetString(3);
            }'''

if old_db_read in text:
    text = text.replace(old_db_read, new_db_read, 1)
    print("Updated DB read fallback in TestSmsGateway!")

# Update DB save to persist latest key and senderId tested
old_upd = '''        await using (var updCmd = conn.CreateCommand())
        {
            updCmd.CommandText = @"
                UPDATE campaign.sms_gateway_configs
                SET last_tested_at = NOW()
                WHERE tenant_id = @t AND election_id = @e;";
            var pT = updCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; updCmd.Parameters.Add(pT);
            var pE = updCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; updCmd.Parameters.Add(pE);
            await updCmd.ExecuteNonQueryAsync(token);
        }'''

new_upd = '''        await using (var updCmd = conn.CreateCommand())
        {
            updCmd.CommandText = @"
                UPDATE campaign.sms_gateway_configs
                SET api_key = @key, sender_id = @sid, provider = @prov, endpoint_url = @ep, last_tested_at = NOW()
                WHERE tenant_id = @t AND election_id = @e;";
            var pT = updCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; updCmd.Parameters.Add(pT);
            var pE = updCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; updCmd.Parameters.Add(pE);
            var pK = updCmd.CreateParameter(); pK.ParameterName = "@key"; pK.Value = apiKey; updCmd.Parameters.Add(pK);
            var pS = updCmd.CreateParameter(); pS.ParameterName = "@sid"; pS.Value = senderId; updCmd.Parameters.Add(pS);
            var pP = updCmd.CreateParameter(); pP.ParameterName = "@prov"; pP.Value = provider; updCmd.Parameters.Add(pP);
            var pEp = updCmd.CreateParameter(); pEp.ParameterName = "@ep"; pEp.Value = endpointUrl; updCmd.Parameters.Add(pEp);
            await updCmd.ExecuteNonQueryAsync(token);
        }'''

if old_upd in text:
    text = text.replace(old_upd, new_upd, 1)
    print("Updated DB save in TestSmsGateway!")

with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved CandidatePortalController.cs successfully!")
