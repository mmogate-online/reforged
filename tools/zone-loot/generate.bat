@echo off
cd /d "%~dp0"
set /p PATCH=Enter patch number:
python generate_zone_loot.py --patch %PATCH%
pause
