@echo off
cd /d "%~dp0"
set /p PATCH=Enter patch number:
python generate_evolutions.py --patch %PATCH%
pause
