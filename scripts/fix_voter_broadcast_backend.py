# -*- coding: utf-8 -*-
with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update SendVoterBroadcastRequest to add Guid? CandidateId = null
old_req_def = '''public sealed record SendVoterBroadcastRequest(
    [Required] string Channel,
    string? TargetFilter,
    Guid? TargetCenterId,
    string? TemplateType,
    [Required] string MessageContent);'''

new_req_def = '''public sealed record SendVoterBroadcastRequest(
    [Required] string Channel,
    string? TargetFilter,
    Guid? TargetCenterId,
    string? TemplateType,
    [Required] string MessageContent,
    Guid? CandidateId = null);'''

assert old_req_def in text, 'old_req_def not found'
text = text.replace(old_req_def, new_req_def, 1)
print('1. SendVoterBroadcastRequest updated!')

# 2. Update SendVoterBroadcast targetCandidateId and scoping
old_scope_calc = '''        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var channel = (request.Channel ?? "WHATSAPP").Trim().ToUpperInvariant();
        var targetFilter = (request.TargetFilter ?? "ALL").Trim().ToUpperInvariant();

        // 1. Query voters matching scope
        var voterQuery = pollingDb.Voters
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId);

        if (userCandidateId.HasValue)
        {
            voterQuery = voterQuery.Where(x => x.CandidateId == null || x.CandidateId == userCandidateId.Value);
        }'''

new_scope_calc = '''        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = request.CandidateId ?? userCandidateId;
        var channel = (request.Channel ?? "WHATSAPP").Trim().ToUpperInvariant();
        var targetFilter = (request.TargetFilter ?? "ALL").Trim().ToUpperInvariant();

        // 1. Query voters matching scope
        var voterQuery = pollingDb.Voters
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId);

        if (targetCandidateId.HasValue)
        {
            voterQuery = voterQuery.Where(x => x.CandidateId == null || x.CandidateId == targetCandidateId.Value);
        }'''

assert old_scope_calc in text, 'old_scope_calc not found'
text = text.replace(old_scope_calc, new_scope_calc, 1)
print('2. SendVoterBroadcast scope updated!')

# 3. Update candidate profile lookup in SendVoterBroadcast
old_cand_assign = '''        var candAssignment = await candidatesDb.CandidateElections
            .SingleOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && (userCandidateId == null || x.CandidateId == userCandidateId.Value), token);'''

new_cand_assign = '''        var candAssignment = await candidatesDb.CandidateElections
            .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && (targetCandidateId == null || x.CandidateId == targetCandidateId.Value), token);
        if (candAssignment == null)
        {
            candAssignment = await candidatesDb.CandidateElections
                .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.IsActive, token);
        }'''

assert old_cand_assign in text, 'old_cand_assign not found'
text = text.replace(old_cand_assign, new_cand_assign, 1)
print('3. Candidate assignment lookup in broadcast updated!')

# 4. Update SendVoterBroadcast broadcast_logs insert SQL
old_insert = '''        // Log outbox
        await using (var insCmd = conn.CreateCommand())
        {
            insCmd.CommandText = @"
                INSERT INTO campaign.broadcast_logs (broadcast_id, tenant_id, election_id, channel, template_type, recipient_count, status, sent_at)
                VALUES (@id, @t, @e, @ch, @tpl, @rc, @st, NOW());";
            var pId = insCmd.CreateParameter(); pId.ParameterName = "@id"; pId.Value = broadcastId; insCmd.Parameters.Add(pId);
            var pT = insCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; insCmd.Parameters.Add(pT);
            var pE = insCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; insCmd.Parameters.Add(pE);
            var pCh = insCmd.CreateParameter(); pCh.ParameterName = "@ch"; pCh.Value = channel; insCmd.Parameters.Add(pCh);
            var pTpl = insCmd.CreateParameter(); pTpl.ParameterName = "@tpl"; pTpl.Value = templateType; insCmd.Parameters.Add(pTpl);
            var pRc = insCmd.CreateParameter(); pRc.ParameterName = "@rc"; pRc.Value = voters.Count; insCmd.Parameters.Add(pRc);
            var pSt = insCmd.CreateParameter(); pSt.ParameterName = "@st"; pSt.Value = channel == "SMS" ? "DELIVERED" : "QUEUED"; insCmd.Parameters.Add(pSt);
            await insCmd.ExecuteNonQueryAsync(token);
        }'''

new_insert = '''        // Log outbox
        await using (var insCmd = conn.CreateCommand())
        {
            insCmd.CommandText = @"
                INSERT INTO campaign.broadcast_logs (broadcast_id, tenant_id, election_id, channel, recipient_group, recipient_count, message_content, template_type, status, sent_at)
                VALUES (@id, @t, @e, @ch, 'VOTERS', @rc, @msg, @tpl, @st, NOW());";
            var pId = insCmd.CreateParameter(); pId.ParameterName = "@id"; pId.Value = broadcastId; insCmd.Parameters.Add(pId);
            var pT = insCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; insCmd.Parameters.Add(pT);
            var pE = insCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; insCmd.Parameters.Add(pE);
            var pCh = insCmd.CreateParameter(); pCh.ParameterName = "@ch"; pCh.Value = channel; insCmd.Parameters.Add(pCh);
            var pRc = insCmd.CreateParameter(); pRc.ParameterName = "@rc"; pRc.Value = voters.Count; insCmd.Parameters.Add(pRc);
            var pMsg = insCmd.CreateParameter(); pMsg.ParameterName = "@msg"; pMsg.Value = request.MessageContent; insCmd.Parameters.Add(pMsg);
            var pTpl = insCmd.CreateParameter(); pTpl.ParameterName = "@tpl"; pTpl.Value = (object?)templateType ?? DBNull.Value; insCmd.Parameters.Add(pTpl);
            var pSt = insCmd.CreateParameter(); pSt.ParameterName = "@st"; pSt.Value = channel == "SMS" ? "DELIVERED" : "QUEUED"; insCmd.Parameters.Add(pSt);
            await insCmd.ExecuteNonQueryAsync(token);
        }'''

assert old_insert in text, 'old_insert not found'
text = text.replace(old_insert, new_insert, 1)
print('4. broadcast_logs insert SQL updated!')

# 5. Update SendWhatsAppAutoBroadcast to return proper HTTP status code and validate items
old_wa_broadcast = '''    [HttpPost("whatsapp/auto-broadcast")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> SendWhatsAppAutoBroadcast(
        [FromBody] WhatsAppAutoBroadcastRequest request,
        CancellationToken token)
    {
        try
        {
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            var json = JsonSerializer.Serialize(request, CamelCaseJsonOptions);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
            var response = await client.PostAsync("http://localhost:5140/api/whatsapp/broadcast", content, token);
            var resultStr = await response.Content.ReadAsStringAsync(token);
            return Content(resultStr, "application/json");
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = "bot_error", message = ex.Message });
        }
    }'''

new_wa_broadcast = '''    [HttpPost("whatsapp/auto-broadcast")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> SendWhatsAppAutoBroadcast(
        [FromBody] WhatsAppAutoBroadcastRequest request,
        CancellationToken token)
    {
        try
        {
            if (request == null || request.Items == null || request.Items.Count == 0)
            {
                return BadRequest(new { error = "empty_items", message = "কোনো প্রাপক ভোটার তালিকা প্রদান করা হয়নি।" });
            }

            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
            var json = JsonSerializer.Serialize(request, CamelCaseJsonOptions);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
            var response = await client.PostAsync("http://localhost:5140/api/whatsapp/broadcast", content, token);
            var resultStr = await response.Content.ReadAsStringAsync(token);
            return new ContentResult
            {
                StatusCode = (int)response.StatusCode,
                Content = resultStr,
                ContentType = "application/json"
            };
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = "bot_error", message = ex.Message });
        }
    }'''

assert old_wa_broadcast in text, 'old_wa_broadcast not found'
text = text.replace(old_wa_broadcast, new_wa_broadcast, 1)
print('5. SendWhatsAppAutoBroadcast method updated!')

# 6. Update TestSmsGateway with informative error messages
old_sms_err = '''                    if (errCode == 0)
                    {
                        isSuccess = true;
                        statusMsg = "এসএমএস.নেট.বিডি (SMS.NET.BD) গেটওয়ে দিয়ে টেস্ট বার্তা সফলভাবে পাঠানো হয়েছে।";
                    }
                    else
                    {
                        isSuccess = false;
                        statusMsg = $"এসএমএস গেটওয়ে রেসপন্স: {gwMsg} (Error code: {errCode})।";
                    }'''

new_sms_err = '''                    if (errCode == 0)
                    {
                        isSuccess = true;
                        statusMsg = "এসএমএস.নেট.বিডি (SMS.NET.BD) গেটওয়ে দিয়ে টেস্ট বার্তা সফলভাবে পাঠানো হয়েছে।";
                    }
                    else if (errCode == 405)
                    {
                        isSuccess = false;
                        statusMsg = $"এসএমএস গেটওয়ে রেসপন্স: এপিআই টোকেন অনুমোদিত নয় বা ভুল (Error 405)। আপনার sms.net.bd ড্যাশবোর্ড থেকে সঠিক API Key কপি করে সংরক্ষণ করুন।";
                    }
                    else if (errCode == 413)
                    {
                        isSuccess = false;
                        statusMsg = $"এসএমএস গেটওয়ে রেসপন্স: অননুমোদিত সেন্ডার আইডি '{senderId}' (Error 413)। নন-মাস্কিং এসএমএস পাঠাতে 'সেন্ডার আইডি' ঘরটি খালি রাখুন।";
                    }
                    else
                    {
                        isSuccess = false;
                        statusMsg = $"এসএমএস গেটওয়ে রেসপন্স: {gwMsg} (Error code: {errCode})।";
                    }'''

assert old_sms_err in text, 'old_sms_err not found'
text = text.replace(old_sms_err, new_sms_err, 1)
print('6. TestSmsGateway error handling updated!')

with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'w', encoding='utf-8') as f:
    f.write(text)

print('All backend updates successfully written!')

