# DBE Expert System - Security Audit Script
# This script checks for common misconfigurations in the Azure environment.

$resourceGroup = "rg-dbe-ai-expert-system"

Write-Host "Starting Security Audit for $resourceGroup..." -ForegroundColor Cyan

# 1. Check if Key Vault is publicly accessible
$kv = Get-AzKeyVault -ResourceGroupName $resourceGroup
foreach ($v in $kv) {
    if ($v.NetworkAcls.DefaultAction -eq "Allow") {
        Write-Warning "Key Vault $($v.VaultName) has default network action 'Allow'. Consider restricting access."
    }
}

# 2. Check for Public IP Addresses
$publicIps = Get-AzPublicIpAddress -ResourceGroupName $resourceGroup
if ($publicIps) {
    Write-Warning "Found $($publicIps.Count) Public IP Addresses. Ensure these are necessary (e.g., Load Balancer/APIM)."
}

# 3. Check for open NSG rules (e.g., SSH/RDP)
$nsgs = Get-AzNetworkSecurityGroup -ResourceGroupName $resourceGroup
foreach ($nsg in $nsgs) {
    $riskyRules = $nsg.SecurityRules | Where-Object { $_.Access -eq "Allow" -and ($_.DestinationPortRange -eq "22" -or $_.DestinationPortRange -eq "3389") -and $_.SourceAddressPrefix -eq "*" }
    if ($riskyRules) {
        Write-Error "NSG $($nsg.Name) has rules allowing SSH/RDP from ANY source!"
    }
}

# 4. Check for Storage Account public access
$storageAccounts = Get-AzStorageAccount -ResourceGroupName $resourceGroup
foreach ($sa in $storageAccounts) {
    if ($sa.AllowBlobPublicAccess -eq $true) {
        Write-Warning "Storage Account $($sa.StorageAccountName) allows public blob access."
    }
}

Write-Host "Security Audit Completed." -ForegroundColor Green
