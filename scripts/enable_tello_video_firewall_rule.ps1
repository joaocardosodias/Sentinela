[CmdletBinding()]
param(
    [string]$RuleName = "G03 Tello UDP Inbound",
    [int[]]$Ports = @(11111, 8890, 8899),
    [string]$RemoteAddress = "192.168.10.1"
)

$ErrorActionPreference = "Stop"

$currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($currentIdentity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    throw "Execute este script em PowerShell como Administrador."
}

$existingRule = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue

if ($existingRule) {
    Set-NetFirewallRule -DisplayName $RuleName -Enabled True -Action Allow -Profile Any
    Set-NetFirewallPortFilter -AssociatedNetFirewallRule $existingRule -Protocol UDP -LocalPort $Ports
    Set-NetFirewallAddressFilter -AssociatedNetFirewallRule $existingRule -RemoteAddress $RemoteAddress
} else {
    New-NetFirewallRule `
        -DisplayName $RuleName `
        -Direction Inbound `
        -Action Allow `
        -Protocol UDP `
        -LocalPort $Ports `
        -RemoteAddress $RemoteAddress `
        -Profile Any `
        -Description "Permite video e telemetria UDP do DJI Tello para a CLI G03"
}

Get-NetFirewallRule -DisplayName $RuleName |
    Select-Object DisplayName, Enabled, Direction, Action, Profile

Get-NetFirewallRule -DisplayName $RuleName |
    Get-NetFirewallPortFilter |
    Select-Object Protocol, LocalPort, RemotePort

Get-NetFirewallRule -DisplayName $RuleName |
    Get-NetFirewallAddressFilter |
    Select-Object LocalAddress, RemoteAddress
