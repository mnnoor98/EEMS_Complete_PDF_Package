param(
    [Parameter(Mandatory = $true)][ValidatePattern('^https?://')][string]$BaseUrl
)

$ErrorActionPreference = 'Stop'
$root = $BaseUrl.TrimEnd('/')
$checks = @(
    @{ Name = 'Web application'; Uri = "$root/"; Expected = 200 },
    @{ Name = 'Liveness'; Uri = "$root/health/live"; Expected = 200 },
    @{ Name = 'Readiness'; Uri = "$root/health/ready"; Expected = 200 }
)

foreach ($check in $checks) {
    $response = Invoke-WebRequest -Uri $check.Uri -Method Get -MaximumRedirection 5
    if ([int]$response.StatusCode -ne $check.Expected) {
        throw "$($check.Name) failed: expected $($check.Expected), received $($response.StatusCode)."
    }
    Write-Host "PASS $($check.Name) $($check.Uri)"
}

Write-Host 'Staging public endpoint smoke checks passed.'
