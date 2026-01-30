@echo off
setlocal
cd /d "%~dp0"

echo === Enchant Materials Deploy ===
echo.

set /p PATCH=Enter patch number:
echo.

echo [1/4] Generating specs from enchant.xlsx...
python generate_enchant_materials.py --patch %PATCH%
if errorlevel 1 (
    echo ERROR: Generation failed.
    pause
    exit /b 1
)
echo.

echo [2/4] Applying enchant-materials.yaml...
cd /d "%~dp0..\..\..\"
dsl apply "reforged\specs\patches\%PATCH%\enchant-materials.yaml" --path "D:\dev\mmogate\tera92\server\Datasheet"
if errorlevel 1 (
    echo ERROR: Apply enchant-materials failed.
    pause
    exit /b 1
)
echo.

echo [3/4] Applying enchant-item-links.yaml...
dsl apply "reforged\specs\patches\%PATCH%\enchant-item-links.yaml" --path "D:\dev\mmogate\tera92\server\Datasheet"
if errorlevel 1 (
    echo ERROR: Apply enchant-item-links failed.
    pause
    exit /b 1
)
echo.

echo [4/4] Syncing to client DataCenter...
dsl sync --config reforged\config\sync-config.yaml -e MaterialEnchantData -e ItemData
if errorlevel 1 (
    echo ERROR: Client sync failed.
    pause
    exit /b 1
)
echo.

echo === Deploy complete ===
pause
