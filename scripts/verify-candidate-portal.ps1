param(
    [string]$BaseUrl = "http://localhost:5131",
    [string]$TenantCode = "1000000000",
    [string]$Username = "admin",
    [string]$Password = "EEMS@123456!"
)

$ErrorActionPreference = 'Stop'
Write-Host "Verifying Candidate War Room & Agent Endpoints..." -ForegroundColor Cyan

# 1. Login
$loginBody = @{
    tenantId = $TenantCode
    username = $Username
    password = $Password
} | ConvertTo-Json

$auth = Invoke-RestMethod -Uri "$BaseUrl/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$token = $auth.accessToken
$headers = @{
    "Authorization" = "Bearer $token"
    "X-Tenant-Code" = $TenantCode
}

# 2. Get Elections
$elections = Invoke-RestMethod -Uri "$BaseUrl/api/v1/elections" -Method Get -Headers $headers
$election = $elections[0]
$electionId = $election.electionId
Write-Host "Election ID: $electionId ($($election.name))" -ForegroundColor Green

# 3. Check Symbols
$symbols = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/symbols" -Method Get -Headers $headers
Write-Host "Total Election Symbols: $($symbols.Count)" -ForegroundColor Green

# 4. Check War Room
$warRoom = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/war-room" -Method Get -Headers $headers
Write-Host "Candidate: $($warRoom.candidate.name) | Symbol: $($warRoom.candidate.symbolEmoji) $($warRoom.candidate.symbolNameBn)" -ForegroundColor Green
Write-Host "EC Ceiling: $($warRoom.ecCeiling) BDT | Spent: $($warRoom.totalCommittedExpenses) BDT" -ForegroundColor Green

# 5. Check Booth Agents
$agents = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/booth-agents" -Method Get -Headers $headers
Write-Host "Assigned Booth Agents: $($agents.Count)" -ForegroundColor Green
foreach ($a in $agents) {
    Write-Host "  - $($a.agentType): $($a.fullName) | Booth: $($a.boothName) | Status: $($a.status) | NID: $($a.nidNumber)" -ForegroundColor Yellow
}

# 6. Check Results Summary
$results = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/results-summary" -Method Get -Headers $headers
Write-Host "Live Results: Total Centers: $($results.totalCenters) | Counted: $($results.countedCenters) | Lead Margin: $($results.leadMargin)" -ForegroundColor Green

# 7. Check EC Expense Schedule
$schedule = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/expenses/ec-schedule" -Method Get -Headers $headers
Write-Host "EC Expense Schedule: Categories: $($schedule.categories.Count) | Within Ceiling: $($schedule.isWithinCeiling)" -ForegroundColor Green

# 8. Check Voters Roll
$voters = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/voters" -Method Get -Headers $headers
Write-Host "Voter Roll: Total Registered Voters: $($voters.Count)" -ForegroundColor Green
foreach ($v in $voters) {
    Write-Host "  - SL $($v.serialNumber): $($v.fullName) | VoterID: $($v.voterNumber) | Category: $($v.category) | Slip: $($v.slipIssued)" -ForegroundColor Yellow
}

# 9. Check Incidents & Complaints
$incidents = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/incidents" -Method Get -Headers $headers
Write-Host "Incidents & Complaints: Total Recorded: $($incidents.Count)" -ForegroundColor Green
foreach ($inc in $incidents) {
    Write-Host "  - [$($inc.severity)] $($inc.title) | Center: $($inc.centerName) | Status: $($inc.status)" -ForegroundColor Red
}

Write-Host "`nAll Candidate War Room Endpoints Verified Successfully!" -ForegroundColor Green
