$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$workflowDir = Join-Path $root ".github\workflows"
New-Item -ItemType Directory -Force -Path $workflowDir | Out-Null
Copy-Item (Join-Path $root "github_workflows\dart_update_and_pages.yml") (Join-Path $workflowDir "dart_update_and_pages.yml") -Force
Write-Host "Installed .github/workflows/dart_update_and_pages.yml"
