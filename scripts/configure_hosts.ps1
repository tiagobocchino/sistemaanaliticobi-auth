param(
    [Parameter(Mandatory = $true)]
    [string]$Domain,
    [Parameter(Mandatory = $true)]
    [string]$IPAddress
)

$hostsPath = "$env:SystemRoot\\System32\\drivers\\etc\\hosts"
$entry = "$IPAddress`t$Domain"

Write-Host "Adding hosts entry: $entry"

if (-not (Test-Path $hostsPath)) {
    throw "Hosts file not found at $hostsPath"
}

$content = Get-Content -Path $hostsPath -ErrorAction Stop
if ($content -contains $entry) {
    Write-Host "Entry already exists."
    exit 0
}

Add-Content -Path $hostsPath -Value $entry -ErrorAction Stop
Write-Host "Entry added. You may need to flush DNS cache: ipconfig /flushdns"
