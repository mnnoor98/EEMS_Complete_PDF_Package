param(
    [string]$BaseUrl = "http://localhost:5131",
    [string]$TenantCode = "1000000000",
    [string]$Username = "admin",
    [string]$Password = "EEMS@123456!"
)

$ErrorActionPreference = 'Stop'

# 1. Login
$auth = Invoke-RestMethod -Uri "$BaseUrl/api/v1/auth/login" -Method Post -Body (@{
    tenantId = $TenantCode
    username = $Username
    password = $Password
} | ConvertTo-Json) -ContentType "application/json"

$headers = @{
    "Authorization" = "Bearer $($auth.accessToken)"
    "X-Tenant-Code" = $TenantCode
}

# 2. Get Election & Candidate
$elections = Invoke-RestMethod -Uri "$BaseUrl/api/v1/elections" -Method Get -Headers $headers
$electionId = $elections[0].electionId
$warRoom = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/war-room" -Method Get -Headers $headers
$candidateId = $warRoom.candidate.candidateId

Write-Host "Updating Candidate Symbol to Pineapple (আনারস 🍍)..." -ForegroundColor Cyan
$updateBody = @{
    symbolId = 14 # Pineapple
    partyName = "স্বতন্ত্র প্রার্থী"
    slogan = "জনগণের সেবায় সততা ও অঙ্গীকার"
    phone = "01711223344"
    campaignOffice = "বাড়ি #১২, ধানমন্ডি, ঢাকা"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/candidates/$candidateId/campaign" -Method Put -Body $updateBody -Headers $headers -ContentType "application/json"

# 3. Check updated War Room Hero
$updatedWarRoom = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/war-room" -Method Get -Headers $headers
Write-Host "Updated Hero: $($updatedWarRoom.candidate.name) | Symbol: $($updatedWarRoom.candidate.symbolEmoji) $($updatedWarRoom.candidate.symbolNameBn) ($($updatedWarRoom.candidate.symbolNameEn))" -ForegroundColor Green
Write-Host "Party: $($updatedWarRoom.candidate.partyName) | Slogan: $($updatedWarRoom.candidate.slogan)" -ForegroundColor Green

# 4. Submit Quick Center Result (Form-8 live entry)
$centers = Invoke-RestMethod -Uri "$BaseUrl/api/v1/elections/$electionId/polling-centers" -Method Get -Headers $headers
$centerLink = $centers.items[0]
Write-Host "`nSubmitting Live Count for Center: $($centerLink.name)..." -ForegroundColor Cyan
$quickResult = @{
    electionCenterId = $centerLink.electionCenterId
    candidateVotes = 1450
    runnerUpVotes = 820
    notes = "ফরম-৮ এর ফলাফল অনুমোদিত"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/quick-result" -Method Post -Body $quickResult -Headers $headers -ContentType "application/json"

# 5. Check Live Lead Margin
$results = Invoke-RestMethod -Uri "$BaseUrl/api/v1/candidate/elections/$electionId/results-summary" -Method Get -Headers $headers
Write-Host "Live Scoreboard:" -ForegroundColor Yellow
Write-Host "  Candidate Votes: $($results.candidateTotalVotes) ($($results.candidateSymbolEmoji) $($results.candidateSymbol))" -ForegroundColor Green
Write-Host "  Runner-up Votes: $($results.runnerUpTotalVotes) ($($results.runnerUpSymbolEmoji) $($results.runnerUpSymbol))" -ForegroundColor Red
Write-Host "  Lead Margin: +$($results.leadMargin) votes (Leading: $($results.isLeading))" -ForegroundColor Cyan
Write-Host "  Counted Centers: $($results.countedCenters)/$($results.totalCenters)" -ForegroundColor Green

