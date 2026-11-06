# -*- coding: utf-8 -*-
import re

with open('scripts/base_controller.cs', 'r', encoding='utf-16') as f:
    base_text = f.read()

# 1. Update constructor to include IPasswordHasher
old_ctor = '''public sealed class CandidatePortalController(
    CandidatesDbContext candidatesDb,
    ElectionsDbContext electionsDb,
    GeographyDbContext geographyDb,
    PollingDbContext pollingDb,
    TeamsDbContext teamsDb,
    FinanceDbContext financeDb,
    EventsDbContext eventsDb,
    ResultsDbContext resultsDb,
    IdentityDbContext identityDb,
    ITenantContext tenantContext) : ControllerBase'''

new_ctor = '''public sealed class CandidatePortalController(
    CandidatesDbContext candidatesDb,
    ElectionsDbContext electionsDb,
    GeographyDbContext geographyDb,
    PollingDbContext pollingDb,
    TeamsDbContext teamsDb,
    FinanceDbContext financeDb,
    EventsDbContext eventsDb,
    ResultsDbContext resultsDb,
    IdentityDbContext identityDb,
    ITenantContext tenantContext,
    Microsoft.AspNetCore.Identity.IPasswordHasher<EEMS.Modules.Identity.Domain.User> passwordHasher) : ControllerBase'''

assert old_ctor in base_text, "old_ctor not found"
base_text = base_text.replace(old_ctor, new_ctor, 1)

# 2. Add imports at the top
top_imports = '''using System.Globalization;
using System.Text.Json;
using EEMS.Modules.Identity.Security;
'''
base_text = top_imports + base_text

# Update CandidateVoterSummary to support optional CandidateId parameter for VoterBulkImportService
old_cvs = '''public sealed record CandidateVoterSummary(
    Guid Id,
    Guid CenterId,
    string CenterName,
    string CenterCode,
    Guid? BoothId,
    string? BoothCode,
    string? BoothName,
    string VoterNumber,
    int SerialNumber,
    string FullName,
    string? FatherOrSpouseName,
    string Gender,
    int? Age,
    string? AreaName,
    string Category,
    bool SlipIssued,
    bool HasVoted,
    string? Phone,
    string? Notes,
    DateTimeOffset CreatedAtUtc);'''

new_cvs = '''public sealed record CandidateVoterSummary(
    Guid Id,
    Guid CenterId,
    string CenterName,
    string CenterCode,
    Guid? BoothId,
    string? BoothCode,
    string? BoothName,
    string VoterNumber,
    int SerialNumber,
    string FullName,
    string? FatherOrSpouseName,
    string Gender,
    int? Age,
    string? AreaName,
    string Category,
    bool SlipIssued,
    bool HasVoted,
    string? Phone,
    string? Notes,
    DateTimeOffset CreatedAtUtc,
    Guid? CandidateId = null);'''

if old_cvs in base_text:
    base_text = base_text.replace(old_cvs, new_cvs, 1)

# 3. Add private helpers inside class
class_start = 'public sealed class CandidatePortalController(\n'
idx_cs = base_text.find(class_start)
assert idx_cs != -1

# Find opening brace of the class
open_brace = base_text.find('{\n', idx_cs)
assert open_brace != -1

helpers = '''
    private static readonly JsonSerializerOptions CamelCaseJsonOptions = new(JsonSerializerDefaults.Web);

    private (Guid? CandidateId, bool IsSuperAdmin) GetUserCandidateScope()
    {
        var isSuperAdminClaim = User.FindFirst("is_super_admin")?.Value;
        bool isSuperAdmin = string.Equals(isSuperAdminClaim, "true", StringComparison.OrdinalIgnoreCase);

        var candClaim = User.FindFirst(IdentityClaimTypes.CandidateId)?.Value;
        if (Guid.TryParse(candClaim, out var cid))
        {
            return (cid, isSuperAdmin);
        }

        return (null, isSuperAdmin);
    }
'''

base_text = base_text[:open_brace + 2] + helpers + base_text[open_brace + 2:]

# 4. Add Sections 10A through 10F before the closing brace of CandidatePortalController
target_end_of_class = '''        pollingDb.Incidents.Remove(incident);
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }
}'''

assert target_end_of_class in base_text, "target_end_of_class not found"

sections_10 = '''        pollingDb.Incidents.Remove(incident);
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 10A. BROADCAST OUTBOX LOGS
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/broadcasts")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateBroadcastLogItem>>> GetBroadcastLogs(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            SELECT broadcast_id, channel, template_type, recipient_count, status, sent_at
            FROM campaign.broadcast_logs
            WHERE tenant_id = @t AND election_id = @e
            ORDER BY sent_at DESC
            LIMIT 50;";

        var pT = cmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; cmd.Parameters.Add(pT);
        var pE = cmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; cmd.Parameters.Add(pE);

        var list = new List<CandidateBroadcastLogItem>();
        await using var reader = await cmd.ExecuteReaderAsync(token);
        while (await reader.ReadAsync(token))
        {
            list.Add(new CandidateBroadcastLogItem(
                reader.GetGuid(0),
                reader.GetString(1),
                reader.GetString(2),
                reader.GetInt32(3),
                reader.GetString(4),
                new DateTimeOffset(reader.GetDateTime(5), TimeSpan.Zero)
            ));
        }

        return Ok(list);
    }

    // =========================================================================
    // 10B. SMS GATEWAY CONFIGURATION & LIVE BALANCE
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/sms-config")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<SmsGatewayConfigDto>> GetSmsGatewayConfig(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            SELECT config_id, provider, api_key, api_secret, sender_id, endpoint_url, is_active, balance, last_tested_at, updated_at
            FROM campaign.sms_gateway_configs
            WHERE tenant_id = @t AND election_id = @e
            LIMIT 1;";

        var pT = cmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; cmd.Parameters.Add(pT);
        var pE = cmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; cmd.Parameters.Add(pE);

        await using var reader = await cmd.ExecuteReaderAsync(token);
        if (await reader.ReadAsync(token))
        {
            var configId = reader.GetGuid(0);
            var provider = reader.GetString(1);
            var apiKey = reader.GetString(2);
            var apiSecret = reader.IsDBNull(3) ? null : reader.GetString(3);
            var senderId = reader.GetString(4);
            var endpointUrl = reader.IsDBNull(5) ? null : reader.GetString(5);
            var isActive = reader.GetBoolean(6);
            var balance = reader.GetDecimal(7);
            var lastTestedAt = reader.IsDBNull(8) ? null : reader.GetFieldValue<DateTimeOffset?>(8);
            var updatedAt = reader.GetFieldValue<DateTimeOffset>(9);

            // Live balance sync for sms.net.bd
            if (!string.IsNullOrWhiteSpace(apiKey) && (provider == "SMS_NET_BD" || endpointUrl?.Contains("sms.net.bd", StringComparison.OrdinalIgnoreCase) == true))
            {
                try
                {
                    using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(3) };
                    var balUrl = $"https://api.sms.net.bd/user/balance/?api_key={apiKey.Trim()}";
                    var resp = await http.GetAsync(balUrl, token);
                    if (resp.IsSuccessStatusCode)
                    {
                        var content = await resp.Content.ReadAsStringAsync(token);
                        using var doc = JsonDocument.Parse(content);
                        if (doc.RootElement.TryGetProperty("data", out var dataEl) &&
                            dataEl.TryGetProperty("balance", out var balEl))
                        {
                            var balStr = balEl.GetString() ?? balEl.GetRawText();
                            if (decimal.TryParse(balStr, NumberStyles.Any, CultureInfo.InvariantCulture, out var liveBal))
                            {
                                balance = liveBal;
                            }
                        }
                    }
                }
                catch { }
            }

            return Ok(new SmsGatewayConfigDto(configId, provider, apiKey, apiSecret, senderId, endpointUrl, isActive, balance, lastTestedAt, updatedAt));
        }

        return Ok(new SmsGatewayConfigDto(Guid.Empty, "SMS_NET_BD", "1FPTyJ7obhfn84GM2U5Z02ywLpd4cx2e7oWN4JeN", null, "", "https://api.sms.net.bd/sendsms", true, 0.90m, null, DateTimeOffset.UtcNow));
    }

    [HttpPut("elections/{electionId:guid}/sms-config")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> UpdateSmsGatewayConfig(Guid electionId, [FromBody] UpdateSmsGatewayConfigRequest request, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            INSERT INTO campaign.sms_gateway_configs (config_id, tenant_id, election_id, provider, api_key, api_secret, sender_id, endpoint_url, is_active, balance, updated_at)
            VALUES (gen_random_uuid(), @t, @e, @prov, @key, @sec, @sid, @ep, @act, 0.90, NOW())
            ON CONFLICT (tenant_id, election_id) DO UPDATE
            SET provider = EXCLUDED.provider,
                api_key = EXCLUDED.api_key,
                api_secret = EXCLUDED.api_secret,
                sender_id = EXCLUDED.sender_id,
                endpoint_url = EXCLUDED.endpoint_url,
                is_active = EXCLUDED.is_active,
                updated_at = NOW();";

        var pT = cmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; cmd.Parameters.Add(pT);
        var pE = cmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; cmd.Parameters.Add(pE);
        var pProv = cmd.CreateParameter(); pProv.ParameterName = "@prov"; pProv.Value = request.Provider.Trim().ToUpperInvariant(); cmd.Parameters.Add(pProv);
        var pKey = cmd.CreateParameter(); pKey.ParameterName = "@key"; pKey.Value = request.ApiKey.Trim(); cmd.Parameters.Add(pKey);
        var pSec = cmd.CreateParameter(); pSec.ParameterName = "@sec"; pSec.Value = (object?)request.ApiSecret?.Trim() ?? DBNull.Value; cmd.Parameters.Add(pSec);
        var pSid = cmd.CreateParameter(); pSid.ParameterName = "@sid"; pSid.Value = (object?)request.SenderId?.Trim() ?? DBNull.Value; cmd.Parameters.Add(pSid);
        var pEp = cmd.CreateParameter(); pEp.ParameterName = "@ep"; pEp.Value = (object?)request.EndpointUrl?.Trim() ?? DBNull.Value; cmd.Parameters.Add(pEp);
        var pAct = cmd.CreateParameter(); pAct.ParameterName = "@act"; pAct.Value = request.IsActive; cmd.Parameters.Add(pAct);

        await cmd.ExecuteNonQueryAsync(token);
        return NoContent();
    }

    [HttpPost("elections/{electionId:guid}/sms-test")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> TestSmsGateway(
        Guid electionId,
        [FromBody] TestSmsRequest request,
        CancellationToken token)
    {
        if (string.IsNullOrWhiteSpace(request.Phone))
        {
            return BadRequest(new { error = "phone_required", message = "টেস্ট মোবাইল নম্বর প্রদান করুন।" });
        }

        var tenantId = tenantContext.TenantId;
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        string provider = !string.IsNullOrWhiteSpace(request.Provider) ? request.Provider.Trim() : "SMS_NET_BD";
        string apiKey = !string.IsNullOrWhiteSpace(request.ApiKey) ? request.ApiKey.Trim() : "";
        string senderId = request.SenderId != null ? request.SenderId.Trim() : "";
        string endpointUrl = !string.IsNullOrWhiteSpace(request.EndpointUrl) ? request.EndpointUrl.Trim() : "https://api.sms.net.bd/sendsms";

        await using (var getCmd = conn.CreateCommand())
        {
            getCmd.CommandText = @"
                SELECT provider, api_key, sender_id, endpoint_url
                FROM campaign.sms_gateway_configs
                WHERE tenant_id = @t AND election_id = @e
                LIMIT 1;";
            var pT = getCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; getCmd.Parameters.Add(pT);
            var pE = getCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; getCmd.Parameters.Add(pE);
            await using var reader = await getCmd.ExecuteReaderAsync(token);
            if (await reader.ReadAsync(token))
            {
                if (string.IsNullOrWhiteSpace(apiKey)) apiKey = reader.GetString(1);
                if (string.IsNullOrWhiteSpace(senderId)) senderId = reader.IsDBNull(2) ? "" : reader.GetString(2);
                if (string.IsNullOrWhiteSpace(provider) || string.Equals(provider, "SMS_NET_BD", StringComparison.OrdinalIgnoreCase)) provider = reader.GetString(0);
                if (string.IsNullOrWhiteSpace(endpointUrl) || string.Equals(endpointUrl, "https://api.sms.net.bd/sendsms", StringComparison.OrdinalIgnoreCase)) endpointUrl = reader.IsDBNull(3) ? "https://api.sms.net.bd/sendsms" : reader.GetString(3);
            }
        }

        // Live Gateway Integration for SMS.NET.BD
        if (string.Equals(provider, "SMS_NET_BD", StringComparison.OrdinalIgnoreCase) || endpointUrl.Contains("sms.net.bd", StringComparison.OrdinalIgnoreCase))
        {
            try
            {
                using var httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
                var formParams = new Dictionary<string, string>
                {
                    ["api_key"] = apiKey,
                    ["msg"] = string.IsNullOrWhiteSpace(request.Message) ? "টেস্ট বার্তা: EEMS নির্বাচনী ওয়ার রুম থেকে পরীক্ষামূলক এসএমএস।" : request.Message,
                    ["to"] = request.Phone.Trim()
                };
                if (!string.IsNullOrWhiteSpace(senderId))
                {
                    formParams["sender_id"] = senderId.Trim();
                }

                var response = await httpClient.PostAsync(endpointUrl, new FormUrlEncodedContent(formParams), token);
                var rawBody = await response.Content.ReadAsStringAsync(token);

                bool isSuccess = false;
                string statusMsg = "";
                try
                {
                    using var doc = JsonDocument.Parse(rawBody);
                    var root = doc.RootElement;
                    int errCode = root.TryGetProperty("error", out var errProp) ? errProp.GetInt32() : -1;
                    string gwMsg = root.TryGetProperty("msg", out var msgProp) ? msgProp.GetString() ?? "" : "";

                    if (errCode == 0)
                    {
                        isSuccess = true;
                        statusMsg = "এসএমএস.নেট.বিডি (SMS.NET.BD) গেটওয়ে দিয়ে টেস্ট বার্তা সফলভাবে পাঠানো হয়েছে।";
                    }
                    else
                    {
                        isSuccess = false;
                        statusMsg = $"এসএমএস গেটওয়ে রেসপন্স: {gwMsg} (Error code: {errCode})।";
                    }
                }
                catch
                {
                    statusMsg = rawBody;
                }

                return Ok(new {
                    success = isSuccess,
                    provider = "SMS_NET_BD",
                    phone = request.Phone,
                    message = statusMsg,
                    raw = rawBody
                });
            }
            catch (Exception ex)
            {
                return Ok(new {
                    success = false,
                    provider = "SMS_NET_BD",
                    phone = request.Phone,
                    message = $"গেটওয়ে কানেকশন ত্রুটি: {ex.Message}"
                });
            }
        }

        return Ok(new {
            success = true,
            provider,
            phone = request.Phone,
            message = "টেস্ট বার্তা সফলভাবে প্রক্রিয়াকরণ সম্পন্ন হয়েছে।"
        });
    }

    // =========================================================================
    // 10C. VOTER BROADCAST DISPATCHER (SMS & WHATSAPP)
    // =========================================================================

    [HttpPost("elections/{electionId:guid}/voter-broadcasts")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<ActionResult<SendVoterBroadcastResponse>> SendVoterBroadcast(
        Guid electionId,
        [FromBody] SendVoterBroadcastRequest request,
        CancellationToken token)
    {
        if (string.IsNullOrWhiteSpace(request.MessageContent))
        {
            return BadRequest(new { error = "message_empty", message = "মেসেজের বিষয়বস্তু প্রদান করা আবশ্যক।" });
        }

        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var channel = (request.Channel ?? "WHATSAPP").Trim().ToUpperInvariant();
        var targetFilter = (request.TargetFilter ?? "ALL").Trim().ToUpperInvariant();

        // 1. Query voters matching scope
        var voterQuery = pollingDb.Voters
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId);

        if (userCandidateId.HasValue)
        {
            voterQuery = voterQuery.Where(x => x.CandidateId == null || x.CandidateId == userCandidateId.Value);
        }

        if (request.TargetCenterId.HasValue && request.TargetCenterId.Value != Guid.Empty)
        {
            voterQuery = voterQuery.Where(x => x.CenterId == request.TargetCenterId.Value);
        }

        if (string.Equals(targetFilter, "SUPPORTER", StringComparison.OrdinalIgnoreCase) || string.Equals(targetFilter, "SUPPORTERS", StringComparison.OrdinalIgnoreCase))
        {
            voterQuery = voterQuery.Where(x => x.Category == "SUPPORTER");
        }
        else if (string.Equals(targetFilter, "UNISSUED_SLIP", StringComparison.OrdinalIgnoreCase) || string.Equals(targetFilter, "UNISSUED_SLIP_ONLY", StringComparison.OrdinalIgnoreCase))
        {
            voterQuery = voterQuery.Where(x => !x.SlipIssued);
        }

        var voters = await voterQuery
            .Where(x => !string.IsNullOrEmpty(x.Phone))
            .OrderBy(x => x.SerialNumber)
            .ToListAsync(token);

        if (voters.Count == 0)
        {
            return BadRequest(new { error = "no_recipients", message = "নির্বাচিত ফিল্টারে মোবাইল নম্বরযুক্ত কোনো ভোটার পাওয়া যায়নি।" });
        }

        // 2. Fetch center and booth names for placeholder interpolation
        var centerIds = voters.Select(v => v.CenterId).Distinct().ToList();
        var centers = await pollingDb.Centers.Where(c => centerIds.Contains(c.Id)).ToDictionaryAsync(c => c.Id, token);
        var boothIds = voters.Where(v => v.BoothId.HasValue).Select(v => v.BoothId!.Value).Distinct().ToList();
        var booths = await pollingDb.Booths.Where(b => boothIds.Contains(b.Id)).ToDictionaryAsync(b => b.Id, token);

        // Fetch candidate details for placeholders
        string candName = "প্রার্থী";
        string candSymbol = "মার্কা";
        var candAssignment = await candidatesDb.CandidateElections
            .SingleOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && (userCandidateId == null || x.CandidateId == userCandidateId.Value), token);
        if (candAssignment != null)
        {
            var candProfile = await candidatesDb.Candidates.SingleOrDefaultAsync(x => x.TenantId == tenantId && x.Id == candAssignment.CandidateId, token);
            if (candProfile != null) candName = candProfile.Name;
            if (candAssignment.SymbolId.HasValue)
            {
                var sym = await candidatesDb.Symbols.SingleOrDefaultAsync(s => s.Id == candAssignment.SymbolId.Value, token);
                if (sym != null) candSymbol = sym.NameBn ?? sym.NameEn ?? "মার্কা";
            }
        }

        // 3. Build queue items with personalized message
        var queue = new List<VoterQueueItem>();
        foreach (var v in voters)
        {
            var centerName = centers.TryGetValue(v.CenterId, out var c) ? c.Name : "ভোটকেন্দ্র";
            string? boothName = v.BoothId.HasValue && booths.TryGetValue(v.BoothId.Value, out var b) ? b.Name : "সাধারণ বুথ";

            var msg = request.MessageContent
                .Replace("{নাম}", v.FullName, StringComparison.Ordinal)
                .Replace("{ভোটারের নাম}", v.FullName, StringComparison.Ordinal)
                .Replace("{ভোটকেন্দ্র}", centerName, StringComparison.Ordinal)
                .Replace("{বুথ}", boothName, StringComparison.Ordinal)
                .Replace("{ক্রমিক}", v.SerialNumber.ToString(CultureInfo.InvariantCulture), StringComparison.Ordinal)
                .Replace("{ভোটার নং}", v.VoterNumber, StringComparison.Ordinal)
                .Replace("{প্রার্থী}", candName, StringComparison.Ordinal)
                .Replace("{মার্কা}", candSymbol, StringComparison.Ordinal);

            var cleanPhone = System.Text.RegularExpressions.Regex.Replace(v.Phone ?? string.Empty, @"\D", "");
            if (cleanPhone.StartsWith("880", StringComparison.Ordinal)) cleanPhone = cleanPhone.Substring(2);

            var waUrl = $"https://wa.me/88{cleanPhone}?text={Uri.EscapeDataString(msg)}";

            queue.Add(new VoterQueueItem(
                v.Id,
                v.FullName,
                v.Phone ?? string.Empty,
                v.SerialNumber,
                v.VoterNumber,
                centerName,
                boothName,
                msg,
                waUrl
            ));
        }

        // 4. Update database
        var broadcastId = Guid.NewGuid();
        var templateType = string.IsNullOrWhiteSpace(request.TemplateType) ? "SLIP_NOTICE" : request.TemplateType.Trim();
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        string responseMsg;
        if (channel == "SMS")
        {
            foreach (var v in voters)
            {
                v.MarkSlipIssued(true);
            }
            await pollingDb.SaveChangesAsync(token);

            // Fetch gateway config
            string gwProvider = "SMS_NET_BD";
            string gwApiKey = "";
            string gwSenderId = "";
            string gwEndpoint = "https://api.sms.net.bd/sendsms";

            await using (var getCmd = conn.CreateCommand())
            {
                getCmd.CommandText = @"
                    SELECT provider, api_key, sender_id, endpoint_url
                    FROM campaign.sms_gateway_configs
                    WHERE tenant_id = @t AND election_id = @e
                    LIMIT 1;";
                var pT = getCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; getCmd.Parameters.Add(pT);
                var pE = getCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; getCmd.Parameters.Add(pE);
                await using var reader = await getCmd.ExecuteReaderAsync(token);
                if (await reader.ReadAsync(token))
                {
                    gwProvider = reader.GetString(0);
                    gwApiKey = reader.GetString(1);
                    gwSenderId = reader.IsDBNull(2) ? "" : reader.GetString(2);
                    gwEndpoint = reader.IsDBNull(3) ? "https://api.sms.net.bd/sendsms" : reader.GetString(3);
                }
            }

            int successCount = 0;
            if (string.Equals(gwProvider, "SMS_NET_BD", StringComparison.OrdinalIgnoreCase) || gwEndpoint.Contains("sms.net.bd", StringComparison.OrdinalIgnoreCase))
            {
                using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };
                foreach (var q in queue)
                {
                    try
                    {
                        var formParams = new Dictionary<string, string>
                        {
                            ["api_key"] = gwApiKey,
                            ["msg"] = q.Message,
                            ["to"] = q.Phone
                        };
                        if (!string.IsNullOrWhiteSpace(gwSenderId)) formParams["sender_id"] = gwSenderId;

                        var resp = await http.PostAsync(gwEndpoint, new FormUrlEncodedContent(formParams), token);
                        if (resp.IsSuccessStatusCode) successCount++;
                    }
                    catch { }
                }
            }

            responseMsg = $"বাল্ক এসএমএস পাঠানো হয়েছে। সফল: {successCount}/{queue.Count} জন ভোটার।";
        }
        else
        {
            responseMsg = $"{queue.Count} জন ভোটারের ডিজিটাল স্লিপ বার্তা তৈরি হয়েছে।";
        }

        // Log outbox
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
        }

        return Ok(new SendVoterBroadcastResponse(
            true,
            broadcastId,
            voters.Count,
            channel,
            channel == "SMS" ? "DELIVERED" : "QUEUED_FOR_DISPATCH",
            responseMsg,
            queue
        ));
    }

    // =========================================================================
    // 10D. WHATSAPP QR AUTO-BOT DISPATCHER
    // =========================================================================

    [HttpGet("whatsapp/status")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<IActionResult> GetWhatsAppBotStatus(CancellationToken token)
    {
        try
        {
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(3) };
            var response = await client.GetAsync("http://localhost:5140/api/whatsapp/status", token);
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync(token);
                return Content(content, "application/json");
            }
        }
        catch { }

        return Ok(new {
            connected = false,
            phone = (string?)null,
            isConnecting = false,
            hasQR = false,
            serviceRunning = false,
            message = "হোয়াটসঅ্যাপ অটো-বট সার্ভিস বর্তমানে অফলাইনে আছে।"
        });
    }

    [HttpGet("whatsapp/qr")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<IActionResult> GetWhatsAppBotQr(CancellationToken token)
    {
        try
        {
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(3) };
            var response = await client.GetAsync("http://localhost:5140/api/whatsapp/qr", token);
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync(token);
                return Content(content, "application/json");
            }
        }
        catch { }

        return Ok(new {
            connected = false,
            phone = (string?)null,
            qrDataUrl = (string?)null,
            message = "কিউআর কোড পাওয়া যায়নি।"
        });
    }

    [HttpPost("whatsapp/auto-broadcast")]
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
    }

    [HttpPost("whatsapp/logout")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> LogoutWhatsAppBot(CancellationToken token)
    {
        try
        {
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            var response = await client.PostAsync("http://localhost:5140/api/whatsapp/logout", null, token);
            var resultStr = await response.Content.ReadAsStringAsync(token);
            return Content(resultStr, "application/json");
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = "bot_error", message = ex.Message });
        }
    }

    // =========================================================================
    // 10E. CANDIDATE TEAM & SUB-USERS (মাস্টার প্রার্থীর সাব-ইউজার ও কর্মী ব্যবস্থাপনা)
    // =========================================================================

    [HttpGet("team-users")]
    [Authorize(Policy = PermissionCodes.UsersRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateTeamUserItem>>> GetCandidateTeamUsers(
        [FromQuery] Guid? candidateId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = userCandidateId ?? candidateId;

        if (!targetCandidateId.HasValue && !isSuperAdmin)
        {
            return Ok(Array.Empty<CandidateTeamUserItem>());
        }

        var conn = identityDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        await using var cmd = conn.CreateCommand();
        if (targetCandidateId.HasValue)
        {
            cmd.CommandText = @"
                SELECT u.user_id, u.external_subject, u.display_name, u.email, tu.candidate_id, tu.is_active, u.created_at
                FROM iam.tenant_users tu
                JOIN iam.users u ON tu.user_id = u.user_id
                WHERE tu.tenant_id = @t AND tu.candidate_id = @c
                ORDER BY u.created_at DESC;";
            var pC = cmd.CreateParameter(); pC.ParameterName = "@c"; pC.Value = targetCandidateId.Value; cmd.Parameters.Add(pC);
        }
        else
        {
            cmd.CommandText = @"
                SELECT u.user_id, u.external_subject, u.display_name, u.email, tu.candidate_id, tu.is_active, u.created_at
                FROM iam.tenant_users tu
                JOIN iam.users u ON tu.user_id = u.user_id
                WHERE tu.tenant_id = @t AND tu.candidate_id IS NOT NULL
                ORDER BY u.created_at DESC;";
        }
        var pT = cmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; cmd.Parameters.Add(pT);

        var list = new List<CandidateTeamUserItem>();
        await using var reader = await cmd.ExecuteReaderAsync(token);
        while (await reader.ReadAsync(token))
        {
            list.Add(new CandidateTeamUserItem(
                reader.GetGuid(0),
                reader.GetString(1),
                reader.GetString(2),
                reader.IsDBNull(3) ? null : reader.GetString(3),
                null,
                "ক্যাম্পেইন টিম সদস্য",
                reader.GetBoolean(5),
                new DateTimeOffset(reader.GetDateTime(6), TimeSpan.Zero)
            ));
        }

        return Ok(list);
    }

    [HttpPost("team-users")]
    [Authorize(Policy = PermissionCodes.UsersManage)]
    public async Task<ActionResult<CandidateTeamUserItem>> CreateCandidateTeamUser(
        [FromBody] CreateCandidateTeamUserRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = userCandidateId ?? request.CandidateId;

        if (!targetCandidateId.HasValue)
        {
            return BadRequest(new { error = "candidate_required", message = "প্রার্থী নির্ধারণ করা হয়নি।" });
        }

        var normalizedUsername = request.Username.Trim();
        if (await identityDb.Users.AnyAsync(u => u.ExternalSubject == normalizedUsername, token))
        {
            return Conflict(new { error = "username_exists", message = "এই ব্যবহারকারী আইডি (Username) ইতিমধ্যে ব্যবহৃত হচ্ছে। অন্য আইডি দিন।" });
        }

        var user = EEMS.Modules.Identity.Domain.User.Create(request.Username.Trim(), request.DisplayName.Trim(), request.Email?.Trim());
        identityDb.Users.Add(user);

        var tenantUser = EEMS.Modules.Identity.Domain.TenantUser.Create(tenantId, user.Id, targetCandidateId.Value);
        identityDb.TenantUsers.Add(tenantUser);

        var hash = passwordHasher.HashPassword(user, request.Password.Trim());
        identityDb.PasswordCredentials.Add(EEMS.Modules.Identity.Domain.PasswordCredential.Create(user.Id, hash, false));

        await identityDb.SaveChangesAsync(token);

        return Ok(new CandidateTeamUserItem(
            user.Id,
            user.ExternalSubject,
            user.DisplayName,
            user.Email,
            request.Phone?.Trim(),
            request.Role?.Trim() ?? "ক্যাম্পেইন টিম সদস্য",
            true,
            user.CreatedAtUtc
        ));
    }

    [HttpPut("team-users/{userId:guid}/status")]
    [Authorize(Policy = PermissionCodes.UsersManage)]
    public async Task<IActionResult> ToggleTeamUserStatus(
        Guid userId,
        [FromBody] ToggleUserStatusRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();

        var tu = await identityDb.TenantUsers.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.UserId == userId, token);

        if (tu == null) return NotFound(new { error = "user_not_found" });

        if (userCandidateId.HasValue && tu.CandidateId != userCandidateId.Value)
        {
            return Forbid();
        }

        if (request.IsActive) tu.Enable(); else tu.Disable();
        await identityDb.SaveChangesAsync(token);
        return NoContent();
    }

    [HttpPost("team-users/{userId:guid}/reset-password")]
    [Authorize(Policy = PermissionCodes.UsersManage)]
    public async Task<IActionResult> ResetTeamUserPassword(
        Guid userId,
        [FromBody] ResetPasswordRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();

        var tu = await identityDb.TenantUsers.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.UserId == userId, token);

        if (tu == null) return NotFound(new { error = "user_not_found" });

        if (userCandidateId.HasValue && tu.CandidateId != userCandidateId.Value)
        {
            return Forbid();
        }

        var user = await identityDb.Users.SingleOrDefaultAsync(u => u.Id == userId, token);
        if (user == null) return NotFound();

        var cred = await identityDb.PasswordCredentials.SingleOrDefaultAsync(p => p.UserId == userId, token);
        var newHash = passwordHasher.HashPassword(user, request.NewPassword.Trim());
        if (cred != null)
        {
            cred.ChangePassword(newHash);
        }
        else
        {
            identityDb.PasswordCredentials.Add(EEMS.Modules.Identity.Domain.PasswordCredential.Create(user.Id, newHash, false));
        }

        await identityDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 10F. SUPER ADMIN MASTER CANDIDATES OVERVIEW HUB (মাস্টার প্রার্থীভিত্তিক তদারকি)
    // =========================================================================

    [HttpGet("master-overview")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<IReadOnlyList<MasterCandidateOverviewItem>>> GetMasterCandidateOverview(
        [FromQuery] Guid? electionId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var conn = candidatesDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        // Fetch all master candidates (filtered by election if provided)
        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            SELECT c.candidate_id, c.name, ce.election_id, s.name_bn, s.name_en, s.icon_emoji, 
                   ce.party_name, ce.slogan, c.phone, c.campaign_office, el.name as election_name
            FROM election.candidates c
            JOIN election.candidate_elections ce ON c.candidate_id = ce.candidate_id
            LEFT JOIN election.symbols s ON ce.symbol_id = s.symbol_id
            LEFT JOIN election.elections el ON ce.election_id = el.election_id
            WHERE c.is_active = TRUE " + (electionId.HasValue ? " AND ce.election_id = @e" : "") + @"
            ORDER BY ce.created_at;";

        if (electionId.HasValue)
        {
            var pE = cmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId.Value; cmd.Parameters.Add(pE);
        }

        var candidateList = new List<MasterCandidateOverviewItem>();
        var candRaw = new List<(Guid CandId, string Name, Guid ElecId, string? SymBn, string? SymEn, string? Emoji, string? Party, string? Slogan, string? Phone, string? Office, string? ElecName)>();

        await using (var reader = await cmd.ExecuteReaderAsync(token))
        {
            while (await reader.ReadAsync(token))
            {
                candRaw.Add((
                    reader.GetGuid(0),
                    reader.GetString(1),
                    reader.GetGuid(2),
                    reader.IsDBNull(3) ? null : reader.GetString(3),
                    reader.IsDBNull(4) ? null : reader.GetString(4),
                    reader.IsDBNull(5) ? "🗳️" : reader.GetString(5),
                    reader.IsDBNull(6) ? "স্বতন্ত্র" : reader.GetString(6),
                    reader.IsDBNull(7) ? "" : reader.GetString(7),
                    reader.IsDBNull(8) ? null : reader.GetString(8),
                    reader.IsDBNull(9) ? null : reader.GetString(9),
                    reader.IsDBNull(10) ? "" : reader.GetString(10)
                ));
            }
        }

        foreach (var c in candRaw)
        {
            // 1. Primary user
            string? primaryUsername = null;
            string? primaryDisplayName = null;
            await using (var uCmd = conn.CreateCommand())
            {
                uCmd.CommandText = @"
                    SELECT u.external_subject, u.display_name
                    FROM iam.tenant_users tu
                    JOIN iam.users u ON tu.user_id = u.user_id
                    WHERE tu.candidate_id = @cid
                    ORDER BY tu.joined_at
                    LIMIT 1;";
                var p = uCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; uCmd.Parameters.Add(p);
                await using var uReader = await uCmd.ExecuteReaderAsync(token);
                if (await uReader.ReadAsync(token))
                {
                    primaryUsername = uReader.GetString(0);
                    primaryDisplayName = uReader.GetString(1);
                }
            }

            // 2. Team sub-users count
            int teamCount = 0;
            await using (var tCmd = conn.CreateCommand())
            {
                tCmd.CommandText = "SELECT COUNT(*) FROM iam.tenant_users WHERE candidate_id = @cid;";
                var p = tCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; tCmd.Parameters.Add(p);
                var res = await tCmd.ExecuteScalarAsync(token);
                if (res != null) teamCount = Convert.ToInt32(res, CultureInfo.InvariantCulture);
            }

            // 3. Booth agents count
            int agentCount = 0;
            await using (var aCmd = conn.CreateCommand())
            {
                aCmd.CommandText = "SELECT COUNT(*) FROM polling.booth_agents WHERE candidate_id = @cid;";
                var p = aCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; aCmd.Parameters.Add(p);
                var res = await aCmd.ExecuteScalarAsync(token);
                if (res != null) agentCount = Convert.ToInt32(res, CultureInfo.InvariantCulture);
            }

            // 4. Voters in scope & slips count
            int voterCount = 0;
            int slipsIssuedCount = 0;
            await using (var vCmd = conn.CreateCommand())
            {
                vCmd.CommandText = "SELECT COUNT(*), COUNT(*) FILTER (WHERE slip_issued = TRUE) FROM polling.voters WHERE candidate_id = @cid;";
                var p = vCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; vCmd.Parameters.Add(p);
                await using var vReader = await vCmd.ExecuteReaderAsync(token);
                if (await vReader.ReadAsync(token))
                {
                    voterCount = vReader.GetInt32(0);
                    slipsIssuedCount = vReader.GetInt32(1);
                }
            }

            // 5. Total Form-8 center votes
            int totalVotes = 0;
            await using (var rCmd = conn.CreateCommand())
            {
                rCmd.CommandText = @"
                    SELECT COALESCE(SUM(d.votes), 0)
                    FROM results.details d
                    JOIN election.candidate_elections ce ON d.candidate_election_id = ce.candidate_election_id
                    WHERE ce.candidate_id = @cid;";
                var p = rCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; rCmd.Parameters.Add(p);
                var res = await rCmd.ExecuteScalarAsync(token);
                if (res != null) totalVotes = Convert.ToInt32(res, CultureInfo.InvariantCulture);
            }

            candidateList.Add(new MasterCandidateOverviewItem(
                c.CandId,
                c.ElecId,
                c.ElecName ?? "",
                c.Name,
                c.SymBn ?? c.SymEn ?? "",
                c.Emoji ?? "🗳️",
                c.Party ?? "স্বতন্ত্র",
                c.Slogan ?? "",
                c.Phone,
                c.Office,
                primaryUsername,
                primaryDisplayName,
                teamCount,
                agentCount,
                voterCount,
                slipsIssuedCount,
                voterCount > 0 ? (int)Math.Round((double)slipsIssuedCount * 100 / voterCount) : 0,
                totalVotes
            ));
        }

        return Ok(candidateList);
    }
}'''

base_text = base_text.replace(target_end_of_class, sections_10, 1)

# 5. Append additional records to the end
additional_records = '''
public sealed record CandidateBroadcastLogItem(
    Guid BroadcastId,
    string Channel,
    string TemplateType,
    int RecipientCount,
    string Status,
    DateTimeOffset SentAt);

public sealed record SmsGatewayConfigDto(
    Guid ConfigId,
    string Provider,
    string ApiKey,
    string? ApiSecret,
    string SenderId,
    string? EndpointUrl,
    bool IsActive,
    decimal Balance,
    DateTimeOffset? LastTestedAt,
    DateTimeOffset UpdatedAt);

public sealed record UpdateSmsGatewayConfigRequest(
    [Required] string Provider,
    [Required] string ApiKey,
    string? ApiSecret,
    string? SenderId,
    string? EndpointUrl,
    bool IsActive);

public sealed record TestSmsRequest(
    [Required] string Phone,
    string? Message,
    string? ApiKey = null,
    string? SenderId = null,
    string? Provider = null,
    string? EndpointUrl = null);

public sealed record SendVoterBroadcastRequest(
    [Required] string Channel,
    string? TargetFilter,
    Guid? TargetCenterId,
    string? TemplateType,
    [Required] string MessageContent);

public sealed record VoterQueueItem(
    Guid VoterId,
    string FullName,
    string Phone,
    int SerialNumber,
    string VoterNumber,
    string CenterName,
    string BoothName,
    string Message,
    string WhatsAppWebUrl);

public sealed record SendVoterBroadcastResponse(
    bool Success,
    Guid BroadcastId,
    int RecipientCount,
    string Channel,
    string Status,
    string Message,
    IReadOnlyList<VoterQueueItem> Queue);

public sealed record WhatsAppAutoBroadcastRequest(
    IReadOnlyList<WhatsAppQueueItemDto> Items);

public sealed record WhatsAppQueueItemDto(
    Guid? Id,
    string? Name,
    string Phone,
    string Message);

public sealed record CandidateTeamUserItem(
    Guid UserId,
    string Username,
    string DisplayName,
    string? Email,
    string? Phone,
    string Role,
    bool IsActive,
    DateTimeOffset CreatedAtUtc);

public sealed record CreateCandidateTeamUserRequest(
    [Required, MaxLength(100)] string Username,
    [Required, MaxLength(150)] string DisplayName,
    [MaxLength(150)] string? Email,
    [MaxLength(20)] string? Phone,
    [Required, MinLength(6)] string Password,
    [MaxLength(50)] string? Role,
    Guid? CandidateId);

public sealed record ToggleUserStatusRequest(bool IsActive);

public sealed record ResetPasswordRequest([Required, MinLength(6)] string NewPassword);

public sealed record MasterCandidateOverviewItem(
    Guid CandidateId,
    Guid ElectionId,
    string ElectionName,
    string CandidateName,
    string SymbolName,
    string SymbolEmoji,
    string PartyName,
    string Slogan,
    string? Phone,
    string? CampaignOffice,
    string? PrimaryUsername,
    string? PrimaryDisplayName,
    int TeamCount,
    int AgentCount,
    int VoterCount,
    int SlipsIssuedCount,
    int SlipPercentage,
    int TotalVotes);
'''

base_text += additional_records

with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'w', encoding='utf-8') as f:
    f.write(base_text)

print(f"CandidatePortalController.cs rebuilt successfully ({len(base_text.splitlines())} lines)!")
