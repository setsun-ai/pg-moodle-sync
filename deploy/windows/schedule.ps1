<#
moodle-sync: automatic sync on Windows (Task Scheduler) while you're logged in.

Runs hidden (pythonw.exe, no window popping up) every N minutes, plus once
after logon; a run missed while the PC was off/asleep starts as soon as possible.
Output goes to logs\sync.log.

    powershell -ExecutionPolicy Bypass -File deploy\windows\schedule.ps1              # every 30 min
    powershell -ExecutionPolicy Bypass -File deploy\windows\schedule.ps1 -Minutes 60
    powershell -ExecutionPolicy Bypass -File deploy\windows\schedule.ps1 -Remove      # turn off
(or double-click schedule.bat next to this file)
#>
param(
    [ValidateRange(15, 1440)][int]$Minutes = 30,
    [switch]$Remove
)
$ErrorActionPreference = "Stop"
$TaskName = "moodle-sync"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "[PL] Wylaczono automatyczna synchronizacje. / [EN] Automatic sync turned off."
    exit 0
}

$Pythonw = Join-Path $Root ".venv\Scripts\pythonw.exe"
if (-not (Test-Path $Pythonw)) {
    throw "[PL] Brak .venv - najpierw uruchom install.bat. / [EN] No .venv - run install.bat first."
}
New-Item -ItemType Directory -Force (Join-Path $Root "logs") | Out-Null
$Log = Join-Path $Root "logs\sync.log"

$Action = New-ScheduledTaskAction -Execute $Pythonw `
    -Argument "-m moodle_sync run --log-file `"$Log`"" -WorkingDirectory $Root
# Every N minutes, indefinitely (no RepetitionDuration = forever on Windows 10/11) + after logon.
$Every = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) `
    -RepetitionInterval (New-TimeSpan -Minutes $Minutes)
$AtLogon = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)
# Interactive = only while you're logged in, no password needed, normal user rights.
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger @($Every, $AtLogon) `
    -Settings $Settings -Principal $Principal -Force `
    -Description "moodle-sync: Moodle -> cloud, calendar, notifications (every $Minutes min)" | Out-Null

Write-Host "[PL] Gotowe: synchronizacja co $Minutes min, gdy jestes zalogowany. Log: $Log"
Write-Host "[EN] Done: sync every $Minutes min while you're logged in. Log: $Log"
Write-Host "     Harmonogram zadan / Task Scheduler -> '$TaskName'. Wylaczenie / remove: schedule.ps1 -Remove"
