@echo off
rem moodle-sync: jedna synchronizacja teraz / sync once now. Dwuklik / double-click.
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (set "PY=.venv\Scripts\python.exe") else (set "PY=python")
"%PY%" -m moodle_sync run
echo.
pause
