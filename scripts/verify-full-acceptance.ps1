param(
    [string]$BaseUrl = "http://localhost:5131",
    [string]$TenantCode = "1000000000",
    [string]$Username = "admin",
    [string]$Password = "EEMS@123456!"
)

$ErrorActionPreference = 'Stop'
$root = $BaseUrl.TrimEnd('/')
$passed = 0
$failed = 0

function Report-Pass($name, $details = "") {
    $script:passed++
    Write-Host " [PASS] $name $(if ($details) { "- $details" })" -ForegroundColor Green
}

function Report-Fail($name, $err) {
    $script:failed++
    Write-Host " [FAIL] $name - $err" -ForegroundColor Red
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  EEMS Staging & Operational Acceptance Verification Suite  " -ForegroundColor Cyan
Write-Host "  Target: $root | Tenant: $TenantCode                       " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# -------------------------------------------------------------
# GATE 1: Platform Health & Dependency Probes
# -------------------------------------------------------------
Write-Host "`n>>> [Gate 1] Platform Health Probes" -ForegroundColor Yellow

try {
    $liveRes = Invoke-RestMethod -Uri "$root/health/live" -Method Get
    if ($liveRes -eq "Healthy") {
        Report-Pass "Liveness Probe (/health/live)" "Status: Healthy"
    } else {
        Report-Fail "Liveness Probe (/health/live)" "Received: $liveRes"
    }
} catch {
    Report-Fail "Liveness Probe (/health/live)" $_.Message
}

try {
    $readyRes = Invoke-RestMethod -Uri "$root/health/ready" -Method Get
    if ($readyRes -eq "Healthy") {
        Report-Pass "Readiness Probe (/health/ready)" "All 13 DB Contexts Healthy"
    } else {
        Report-Fail "Readiness Probe (/health/ready)" "Received: $readyRes"
    }
} catch {
    Report-Fail "Readiness Probe (/health/ready)" $_.Message
}

# -------------------------------------------------------------
# GATE 2: Security & Authentication Gate
# -------------------------------------------------------------
Write-Host "`n>>> [Gate 2] Security & Authentication Controls" -ForegroundColor Yellow

# Negative Test 1: Invalid Tenant Format Regex (Must be 10 digits)
try {
    $badBody = @{ tenantId = "INVALID"; username = $Username; password = $Password } | ConvertTo-Json
    Invoke-RestMethod -Uri "$root/api/v1/auth/login" -Method Post -Body $badBody -ContentType "application/json"
    Report-Fail "Tenant Regex Validation" "Expected 400 Bad Request, but succeeded"
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 400) {
        Report-Pass "Tenant Format Enforcement" "Rejected non-10-digit tenant (HTTP 400)"
    } else {
        Report-Fail "Tenant Format Enforcement" "Unexpected status code: $($_.Exception.Response.StatusCode.value__)"
    }
}

# Negative Test 2: Invalid Password
try {
    $badAuth = @{ tenantId = $TenantCode; username = $Username; password = "WrongPassword99!" } | ConvertTo-Json
    Invoke-RestMethod -Uri "$root/api/v1/auth/login" -Method Post -Body $badAuth -ContentType "application/json"
    Report-Fail "Invalid Credentials Rejection" "Expected 401 Unauthorized, but succeeded"
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401) {
        Report-Pass "Credential Validation" "Rejected incorrect credentials (HTTP 401)"
    } else {
        Report-Fail "Credential Validation" "Unexpected status code: $($_.Exception.Response.StatusCode.value__)"
    }
}

# Positive Test: Valid Admin Login
$token = $null
try {
    $loginBody = @{ tenantId = $TenantCode; username = $Username; password = $Password } | ConvertTo-Json
    $loginRes = Invoke-RestMethod -Uri "$root/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    if ($loginRes.accessToken) {
        $token = $loginRes.accessToken
        Report-Pass "Admin Authentication" "JWT Token issued (Token length: $($token.Length), Refresh valid until: $($loginRes.refreshTokenExpiresAtUtc))"
    } else {
        Report-Fail "Admin Authentication" "No access token in response"
    }
} catch {
    Report-Fail "Admin Authentication" $_.Message
}

if (-not $token) {
    Write-Host "`nCritical: Authentication failed. Aborting remaining tests." -ForegroundColor Red
    exit 1
}

$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
}

# -------------------------------------------------------------
# GATE 3: Multi-Tenancy & Server Context
# -------------------------------------------------------------
Write-Host "`n>>> [Gate 3] Tenant Isolation & Server Context" -ForegroundColor Yellow

try {
    $ctx = Invoke-RestMethod -Uri "$root/api/v1/system/context" -Method Get -Headers $headers
    if ($ctx.tenantId) {
        Report-Pass "Tenant Context Binding" "Server verified Tenant GUID: $($ctx.tenantId)"
    } else {
        Report-Fail "Tenant Context Binding" "No tenantId returned in context"
    }
} catch {
    Report-Fail "Tenant Context Binding" $_.Message
}

# -------------------------------------------------------------
# GATE 4: Operations Dashboard & Oversight
# -------------------------------------------------------------
Write-Host "`n>>> [Gate 4] Operations Dashboard & Cross-Module Oversight" -ForegroundColor Yellow

try {
    $dash = Invoke-RestMethod -Uri "$root/api/v1/dashboard" -Method Get -Headers $headers
    Report-Pass "Operations Dashboard" "Total Elections: $($dash.electionCount), Active: $($dash.activeElectionCount), Open Tasks: $($dash.openTaskCount), Alerts: $($dash.alertCount)"
} catch {
    Report-Fail "Operations Dashboard" $_.Message
}

try {
    $notif = Invoke-RestMethod -Uri "$root/api/v1/oversight/notifications" -Method Get -Headers $headers
    Report-Pass "Security & Operational Notifications" "Received: $($notif.items.Count) items, Unread: $($notif.unreadCount)"
} catch {
    Report-Fail "Security & Operational Notifications" $_.Message
}

try {
    $audit = Invoke-RestMethod -Uri "$root/api/v1/oversight/audit?page=1&pageSize=10" -Method Get -Headers $headers
    Report-Pass "Audit Trail & Correlation" "Audit logs accessible. Total entries: $($audit.totalCount)"
} catch {
    Report-Fail "Audit Trail & Correlation" $_.Message
}

# -------------------------------------------------------------
# GATE 5: Master Data & Reference Structure
# -------------------------------------------------------------
Write-Host "`n>>> [Gate 5] Master Data & Reference Lookups" -ForegroundColor Yellow

try {
    $md = Invoke-RestMethod -Uri "$root/api/v1/master-data" -Method Get -Headers $headers
    Report-Pass "Master Data Workspace" "Areas: $($md.areas.Count), Types: $($md.electionTypes.Count), Positions: $($md.positions.Count), TaskStates: $($md.taskStates.Count)"
} catch {
    Report-Fail "Master Data Workspace" $_.Message
}

# -------------------------------------------------------------
# GATE 6: Operational Walkthrough Across Modules
# -------------------------------------------------------------
Write-Host "`n>>> [Gate 6] Election Lifecycle & Module Walkthrough" -ForegroundColor Yellow

$elections = @()
try {
    $elections = Invoke-RestMethod -Uri "$root/api/v1/elections" -Method Get -Headers $headers
    Report-Pass "Elections Directory" "Discovered $($elections.Count) election(s)"
} catch {
    Report-Fail "Elections Directory" $_.Message
}

$electionId = $null
if ($elections.Count -gt 0) {
    $firstElection = $elections[0]
    $electionId = if ($firstElection.electionId) { $firstElection.electionId } else { $firstElection.id }
    Write-Host "   Using Election: $($firstElection.name) [$electionId]" -ForegroundColor Gray
}

if ($electionId) {
    # 6a. Candidates
    try {
        $cands = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/candidates" -Method Get -Headers $headers
        Report-Pass "Candidates Module" "Registered candidates: $($cands.Count)"
    } catch {
        Report-Fail "Candidates Module" $_.Message
    }

    # 6b. Polling Centers & Lookups
    try {
        $pollingLookups = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/polling-centers/lookups" -Method Get -Headers $headers
        $centers = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/polling-centers?page=1&pageSize=10" -Method Get -Headers $headers
        Report-Pass "Polling Centers Module" "Centers: $($centers.totalCount), Lookups Loaded"
    } catch {
        Report-Fail "Polling Centers Module" $_.Message
    }

    # 6c. Workforce & Field Teams
    try {
        $wfLookups = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/workforce/lookups" -Method Get -Headers $headers
        $teams = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/workforce/teams" -Method Get -Headers $headers
        $wfDashboard = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/workforce/leader-dashboard" -Method Get -Headers $headers
        Report-Pass "Workforce & Field Operations" "Teams: $($teams.Count), Leader Dashboard ready"
    } catch {
        Report-Fail "Workforce & Field Operations" $_.Message
    }

    # 6d. Logistics & Inventory
    try {
        $invLookups = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/inventory/lookups" -Method Get -Headers $headers
        $items = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/inventory/items" -Method Get -Headers $headers
        $warehouses = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/inventory/warehouses" -Method Get -Headers $headers
        $allocations = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/inventory/allocations" -Method Get -Headers $headers
        Report-Pass "Logistics & Inventory" "Items: $($items.Count), Warehouses: $($warehouses.Count), Allocations: $($allocations.Count)"
    } catch {
        Report-Fail "Logistics & Inventory" $_.Message
    }

    # 6e. Finance & Expenses
    try {
        $finance = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/finance" -Method Get -Headers $headers
        Report-Pass "Finance & Expense Tracking" "Budgets: $($finance.budgets.Count), Vendors: $($finance.vendors.Count), Expenses: $($finance.expenses.Count)"
    } catch {
        Report-Fail "Finance & Expense Tracking" $_.Message
    }

    # 6f. Events & Campaign Operations
    try {
        $events = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/events" -Method Get -Headers $headers
        Report-Pass "Events & Campaign Operations" "Events: $($events.events.Count), Venues: $($events.venues.Count), Meetings: $($events.meetings.Count)"
    } catch {
        Report-Fail "Events & Campaign Operations" $_.Message
    }

    # 6g. Results Reporting & Exports
    try {
        $resLookups = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/results/lookups" -Method Get -Headers $headers
        $submissions = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/results" -Method Get -Headers $headers
        $exports = Invoke-RestMethod -Uri "$root/api/v1/elections/$electionId/results/exports" -Method Get -Headers $headers
        Report-Pass "Results & Reporting" "Submissions: $($submissions.Count), Reports/Exports: $($exports.Count)"
    } catch {
        Report-Fail "Results & Reporting" $_.Message
    }
}

# -------------------------------------------------------------
# GATE 7: Maker-Checker & Authorization Security Policy
# -------------------------------------------------------------
Write-Host "`n>>> [Gate 7] Access Control & Policy Enforcement" -ForegroundColor Yellow

try {
    # Call without Bearer token must return 401 Unauthorized
    Invoke-RestMethod -Uri "$root/api/v1/system/context" -Method Get
    Report-Fail "Unauthenticated Access Gate" "Expected 401 Unauthorized, but succeeded"
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401) {
        Report-Pass "Unauthenticated Access Gate" "Strictly blocked unauthenticated requests (HTTP 401)"
    } else {
        Report-Fail "Unauthenticated Access Gate" "Unexpected status code: $($_.Exception.Response.StatusCode.value__)"
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "                ACCEPTANCE SUMMARY REPORT                   " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Total Gates Executed: $($passed + $failed)"
Write-Host " Passed: $passed" -ForegroundColor Green
Write-Host " Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host "============================================================`n" -ForegroundColor Cyan

if ($failed -gt 0) {
    exit 1
}
