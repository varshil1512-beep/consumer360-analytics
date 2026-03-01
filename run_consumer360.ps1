param(
    [string]$RunDate = "",
    [switch]$LaunchFrontend,
    [switch]$LaunchApi
)

$ErrorActionPreference = "Stop"

if ($RunDate -ne "") {
    python -m src.main --run-date $RunDate
} else {
    python -m src.main
}

if ($LaunchFrontend) {
    Start-Process -FilePath powershell -ArgumentList '-ExecutionPolicy Bypass -File .\run_frontend.ps1 -Port 5173' | Out-Null
}

if ($LaunchApi) {
    Start-Process -FilePath powershell -ArgumentList '-ExecutionPolicy Bypass -File .\run_api.ps1 -Port 8000' | Out-Null
}
