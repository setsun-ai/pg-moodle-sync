@echo off
rem moodle-sync - instalacja na Windows / installation on Windows.
rem Dwuklik / double-click. Tworzy .venv, instaluje biblioteki, uruchamia kreator.
setlocal
cd /d "%~dp0"

set "PY="
py -3 -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>nul && set "PY=py -3"
if not defined PY python -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>nul && set "PY=python"
if not defined PY (
    echo [PL] Nie znaleziono Pythona 3.10+. Zainstaluj go:  winget install Python.Python.3.12
    echo      albo z https://www.python.org/downloads/ ^(zaznacz "Add python.exe to PATH"^), potem uruchom ten plik ponownie.
    echo [EN] Python 3.10+ not found. Install it:  winget install Python.Python.3.12
    echo      or from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^), then run this file again.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Tworze srodowisko / creating environment .venv ...
    %PY% -m venv .venv || goto :error
)
echo Instaluje biblioteki / installing libraries ...
".venv\Scripts\python.exe" -m pip install --upgrade pip -q || goto :error
".venv\Scripts\python.exe" -m pip install -r requirements.txt -q || goto :error

".venv\Scripts\python.exe" -m moodle_sync setup
pause
exit /b 0

:error
echo [PL] Cos poszlo nie tak - przeczytaj komunikat powyzej. / [EN] Something went wrong - see the message above.
pause
exit /b 1
