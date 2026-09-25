@echo off
rem Dwuklik = wlacz automatyczna synchronizacje co 30 min. / Double-click = enable automatic sync every 30 min.
rem Wylaczenie / remove:  schedule.bat -Remove
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0schedule.ps1" %*
pause
