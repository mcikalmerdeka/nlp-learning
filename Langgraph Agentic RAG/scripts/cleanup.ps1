# Cleanup script for removing old files and __pycache__ folders
# Run from project root: .\scripts\cleanup.ps1

Write-Host "Cleaning up old files and folders..." -ForegroundColor Cyan

# # Remove old ingestion.py at root
# if (Test-Path "ingestion.py") {
#     Remove-Item "ingestion.py" -Force
#     Write-Host "  Removed: ingestion.py" -ForegroundColor Green
# }

# # Remove old test folder in chains
# if (Test-Path "src\chains\tests") {
#     Remove-Item "src\chains\tests" -Recurse -Force
#     Write-Host "  Removed: src\chains\tests\" -ForegroundColor Green
# }

# Remove all __pycache__ folders recursively
$pycacheFolders = Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue
foreach ($folder in $pycacheFolders) {
    Remove-Item $folder.FullName -Recurse -Force
    Write-Host "  Removed: $($folder.FullName)" -ForegroundColor Green
}

# Remove .pyc files if any remain
$pycFiles = Get-ChildItem -Path . -File -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
foreach ($file in $pycFiles) {
    Remove-Item $file.FullName -Force
    Write-Host "  Removed: $($file.FullName)" -ForegroundColor Green
}

Write-Host "`nCleanup complete!" -ForegroundColor Cyan

