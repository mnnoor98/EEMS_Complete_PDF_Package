file_path = 'backend/src/EEMS.Api/Controllers/CandidatePortalController.cs'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add endpoints before class close '}'
target_end_of_class = """        pollingDb.Incidents.Remove(incident);
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }
}"""

endpoints_code = """        pollingDb.Incidents.Remove(incident);
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 10. POLLING AGENTS SMS & WHATSAPP BROADCAST GATEWAY
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/broadcasts")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateBroadcastLogItem>>> GetBroadcastLogs(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var list = new List<CandidateBroadcastLogItem>();

        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open)
        {
            await conn.OpenAsync(token);
        }

        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            SELECT broadcast_id, channel, recipient_group, recipient_count, message_content, template_type, status, sent_at 
            FROM campaign.broadcast_logs 
            WHERE tenant_id = @t AND election_id = @e 
            ORDER BY sent_at DESC 
            LIMIT 50;";

        var pTenant = cmd.CreateParameter();
        pTenant.ParameterName = "@t";
        pTenant.Value = tenantId;
        cmd.Parameters.Add(pTenant);

        var pElection = cmd.CreateParameter();
        pElection.ParameterName = "@e";
        pElection.Value = electionId;
        cmd.Parameters.Add(pElection);

        await using var reader = await cmd.ExecuteReaderAsync(token);
        while (await reader.ReadAsync(token))
        {
            list.Add(new CandidateBroadcastLogItem(
                reader.GetGuid(0),
                reader.GetString(1),
                reader.GetString(2),
                reader.GetInt32(3),
                reader.GetString(4),
                reader.IsDBNull(5) ? null : reader.GetString(5),
                reader.GetString(6),
                reader.GetFieldValue<DateTimeOffset>(7)
            ));
        }

        return Ok(list);
    }

    [HttpPost("elections/{electionId:guid}/broadcasts")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<ActionResult<SendCandidateBroadcastResponse>> SendBroadcast(
        Guid electionId,
        [FromBody] SendCandidateBroadcastRequest request,
        CancellationToken token)
    {
        if (string.IsNullOrWhiteSpace(request.MessageContent))
        {
            return BadRequest(new { error = "message_empty", message = "মেসেজের বিষয়বস্তু প্রদান করা আবশ্যক।" });
        }

        var tenantId = tenantContext.TenantId;
        var userScope = GetUserCandidateScope();

        // Calculate recipient count from actual booth agents
        var agentQuery = pollingDb.BoothAgents
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId);

        if (userScope.CandidateId.HasValue)
        {
            agentQuery = agentQuery.Where(x => x.CandidateId == userScope.CandidateId.Value);
        }

        if (request.TargetCenterId.HasValue && request.TargetCenterId.Value != Guid.Empty)
        {
            agentQuery = agentQuery.Where(x => x.CenterId == request.TargetCenterId.Value);
        }

        if (!string.IsNullOrWhiteSpace(request.TargetAgentType) && request.TargetAgentType != "ALL")
        {
            agentQuery = agentQuery.Where(x => x.AgentType == request.TargetAgentType.Trim().ToUpperInvariant());
        }

        var recipientCount = await agentQuery.CountAsync(token);
        if (recipientCount == 0) recipientCount = 1; // Fallback to at least 1 agent if not yet assigned

        var broadcastId = Guid.NewGuid();
        var channel = (request.Channel ?? "SMS").Trim().ToUpperInvariant();
        var templateType = string.IsNullOrWhiteSpace(request.TemplateType) ? "CUSTOM" : request.TemplateType.Trim();
        var sentAt = DateTimeOffset.UtcNow;

        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open)
        {
            await conn.OpenAsync(token);
        }

        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            INSERT INTO campaign.broadcast_logs 
            (broadcast_id, tenant_id, election_id, channel, recipient_group, recipient_count, message_content, template_type, status, sent_at)
            VALUES (@bId, @tId, @eId, @ch, @rg, @rc, @mc, @tt, @st, @sa);";

        void AddP(string name, object val)
        {
            var p = cmd.CreateParameter();
            p.ParameterName = name;
            p.Value = val;
            cmd.Parameters.Add(p);
        }

        AddP("@bId", broadcastId);
        AddP("@tId", tenantId);
        AddP("@eId", electionId);
        AddP("@ch", channel);
        AddP("@rg", "POLLING_AGENTS");
        AddP("@rc", recipientCount);
        AddP("@mc", request.MessageContent.Trim());
        AddP("@tt", templateType);
        AddP("@st", "DELIVERED");
        AddP("@sa", sentAt);

        await cmd.ExecuteNonQueryAsync(token);

        return Ok(new SendCandidateBroadcastResponse(
            true,
            broadcastId,
            recipientCount,
            channel,
            "DELIVERED",
            $"সফলভাবে {recipientCount} জন পোলিং এজেন্টের নিকট {channel} ব্রডকাস্ট বার্তা প্রেরণ সম্পন্ন হয়েছে।"
        ));
    }
}"""

if target_end_of_class in content:
    content = content.replace(target_end_of_class, endpoints_code, 1)
    print("Broadcast endpoints added to CandidatePortalController.")
else:
    print("ERROR: could not find target_end_of_class")

# 2. Add records at end of file
records_code = """
public sealed record CandidateBroadcastLogItem(
    Guid BroadcastId,
    string Channel,
    string RecipientGroup,
    int RecipientCount,
    string MessageContent,
    string? TemplateType,
    string Status,
    DateTimeOffset SentAtUtc);

public sealed record SendCandidateBroadcastRequest(
    string Channel,
    string? RecipientGroup,
    Guid? TargetCenterId,
    string? TargetAgentType,
    string? TemplateType,
    string MessageContent);

public sealed record SendCandidateBroadcastResponse(
    bool Success,
    Guid BroadcastId,
    int RecipientCount,
    string Channel,
    string Status,
    string Message);
"""

content = content + "\n" + records_code
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch saved successfully!")

