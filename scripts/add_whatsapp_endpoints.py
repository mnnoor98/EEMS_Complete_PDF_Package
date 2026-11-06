with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'r', encoding='utf-8') as f:
    text = f.read()

anchor = '    // =========================================================================\n    // 11. CAMPAIGN EVENTS, RALLIES & POLICE/EC PERMITS (বিকল্প ৩)'
assert anchor in text, "anchor not found in controller"

wa_controller_code = '''    // =========================================================================
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
            var json = System.Text.Json.JsonSerializer.Serialize(request);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
            var response = await client.PostAsync("http://localhost:5140/api/whatsapp/broadcast", content, token);
            var resultStr = await response.Content.ReadAsStringAsync(token);
            return Content(resultStr, "application/json");
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = "bot_error", message = $"বট সার্ভিসের সাথে যোগাযোগ ব্যর্থ: {ex.Message}" });
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

'''

text = text.replace(anchor, wa_controller_code + anchor)

# Add records at bottom
record_anchor = 'public sealed record SendVoterBroadcastRequest('
assert record_anchor in text, "record_anchor not found"

wa_records = '''public sealed record WhatsAppAutoBroadcastRequest(
    IReadOnlyList<WhatsAppQueueItemDto> Items);

public sealed record WhatsAppQueueItemDto(
    Guid? Id,
    string? Name,
    string Phone,
    string Message);

'''

text = text.replace(record_anchor, wa_records + record_anchor)

with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated CandidatePortalController.cs with WhatsApp bot endpoints!')

# Update eems-api.service.ts
with open('frontend/src/app/core/api/eems-api.service.ts', 'r', encoding='utf-8') as f:
    api_text = f.read()

api_anchor = '  sendVoterBroadcast(electionId: string, body: SendVoterBroadcastRequest) {'
assert api_anchor in api_text, "api_anchor not found in eems-api.service.ts"

wa_api_methods = '''  getWhatsAppBotStatus() {
    return this.http.get<{ connected: boolean; phone: string | null; isConnecting: boolean; hasQR: boolean; queueStats: any; queueRemaining: number }>('/api/v1/candidate/whatsapp/status');
  }
  getWhatsAppBotQr() {
    return this.http.get<{ connected: boolean; phone: string | null; qrDataUrl: string | null }>('/api/v1/candidate/whatsapp/qr');
  }
  sendWhatsAppAutoBroadcast(body: { items: { id?: string; name?: string; phone: string; message: string }[] }) {
    return this.http.post<{ success: boolean; message: string; queueStats: any }>('/api/v1/candidate/whatsapp/auto-broadcast', body);
  }
  logoutWhatsAppBot() {
    return this.http.post<{ success: boolean; message: string }>('/api/v1/candidate/whatsapp/logout', {});
  }
'''

api_text = api_text.replace(api_anchor, wa_api_methods + api_anchor)

with open('frontend/src/app/core/api/eems-api.service.ts', 'w', encoding='utf-8') as f:
    f.write(api_text)

print('Updated eems-api.service.ts with WhatsApp bot client methods!')

