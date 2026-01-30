@echo off
cd /d "%~dp0"
set /p PATCH=Enter patch number:
python generate_enchant_materials.py --patch %PATCH%
pause
