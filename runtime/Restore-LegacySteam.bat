@echo off
cd /d "%~dp0"
set "LEGACY_PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe" set "LEGACY_PS=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"
"%LEGACY_PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0LegacySteam-Patch.ps1" -Mode Restore
echo.
pause
