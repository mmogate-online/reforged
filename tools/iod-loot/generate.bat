@echo off
cd /d "%~dp0"
set /p PATCH=Enter patch number (e.g. 001):
python generate_iod_loot.py --patch %PATCH%
pause
