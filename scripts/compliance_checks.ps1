# DBE Expert System - Compliance Checks Script
# Validates encryption at rest, encryption in transit, and logging enablement.

$resourceGroup = "rg-dbe-ai-expert-system"
Write-Host "Starting Compliance Checks for $resourceGroup..." -ForegroundColor Cyan

# 1. Check for Encryption at Rest on Storage Accounts
$storageAccounts = Get-AzStorageAccount -ResourceGroupName $resourceGroup
foreach ($sa in $storageAccounts) {
    if ($sa.Encryption.Services.Blob.Enabled -ne $true) {
        Write-Error "Storage Account $($sa.StorageAccountName) does NOT have Blob Encryption enabled!"
    } else {
        Write-Host "Storage Account $($sa.StorageAccountName) encryption at rest: OK" -ForegroundColor Green
    }
}

# 2. Check for HTTPS only on Storage Accounts
foreach ($sa in $storageAccounts) {
    if ($sa.EnableHttpsTrafficOnly -ne $true) {
        Write-Error "Storage Account $($sa.StorageAccountName) allows non-HTTPS traffic!"
    }
}

# 3. Check for Diagnostic Settings on Key Vault
$kvs = Get-AzKeyVault -ResourceGroupName $resourceGroup
foreach ($kv in $kvs) {
    $diag = Get-AzDiagnosticSetting -ResourceId $kv.ResourceId
    if (-not $diag) {
        Write-Warning "Key Vault $($kv.VaultName) has no diagnostic settings enabled (No Audit Logs)."
    } else {
        Write-Host "Key Vault $($kv.VaultName) logging: OK" -ForegroundColor Green
    }
}

# 4. Check for Managed Identities on AKS
$aks = Get-AzKubernetesCluster -ResourceGroupName $resourceGroup
foreach ($cluster in $aks) {
    if ($cluster.Identity.Type -eq "None") {
        Write-Error "AKS Cluster $($cluster.Name) does NOT use Managed Identities!"
    }
}

Write-Host "Compliance Checks Completed." -ForegroundColor Green
