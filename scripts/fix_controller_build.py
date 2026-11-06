with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix Task.Run CA2016
old_tr = '_ = Task.Run(async () =>'
new_tr = '_ = Task.Run(async () =>'
if old_tr in text:
    text = text.replace(
        '_ = Task.Run(async () =>',
        '_ = Task.Run(async () =>',
    ) # wait, Task.Run takes (Func<Task>, CancellationToken): Task.Run(async () => { ... }, CancellationToken.None);

old_task_run = '''                            _ = Task.Run(async () =>
                            {
                                try
                                {
                                    await using var syncConn = pollingDb.Database.GetDbConnection();
                                    if (syncConn.State != System.Data.ConnectionState.Open) await syncConn.OpenAsync();
                                    await using var syncCmd = syncConn.CreateCommand();
                                    syncCmd.CommandText = "UPDATE campaign.sms_gateway_configs SET balance = @b WHERE config_id = @id;";
                                    var pB = syncCmd.CreateParameter(); pB.ParameterName = "@b"; pB.Value = liveBal; syncCmd.Parameters.Add(pB);
                                    var pId = syncCmd.CreateParameter(); pId.ParameterName = "@id"; pId.Value = configId; syncCmd.Parameters.Add(pId);
                                    await syncCmd.ExecuteNonQueryAsync();
                                }
                                catch { }
                            });'''

new_task_run = '''                            _ = Task.Run(async () =>
                            {
                                try
                                {
                                    await using var syncConn = pollingDb.Database.GetDbConnection();
                                    if (syncConn.State != System.Data.ConnectionState.Open) await syncConn.OpenAsync(CancellationToken.None);
                                    await using var syncCmd = syncConn.CreateCommand();
                                    syncCmd.CommandText = "UPDATE campaign.sms_gateway_configs SET balance = @b WHERE config_id = @id;";
                                    var pB = syncCmd.CreateParameter(); pB.ParameterName = "@b"; pB.Value = liveBal; syncCmd.Parameters.Add(pB);
                                    var pId = syncCmd.CreateParameter(); pId.ParameterName = "@id"; pId.Value = configId; syncCmd.Parameters.Add(pId);
                                    await syncCmd.ExecuteNonQueryAsync(CancellationToken.None);
                                }
                                catch { }
                            }, CancellationToken.None);'''

assert old_task_run in text, "old_task_run not found"
text = text.replace(old_task_run, new_task_run)

# Fix SendVoterBroadcastResponse call
old_resp = '''        return Ok(new SendVoterBroadcastResponse(
            broadcastId,
            voters.Count,
            channel,
            channel == "SMS" ? "DELIVERED" : "QUEUED_FOR_DISPATCH",
            responseMsg,
            queue
        ));'''

new_resp = '''        return Ok(new SendVoterBroadcastResponse(
            true,
            broadcastId,
            voters.Count,
            channel,
            channel == "SMS" ? "DELIVERED" : "QUEUED_FOR_DISPATCH",
            responseMsg,
            queue
        ));'''

assert old_resp in text, "old_resp not found"
text = text.replace(old_resp, new_resp)

with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated Task.Run and SendVoterBroadcastResponse successfully!')

