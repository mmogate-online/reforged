@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo === Zone Loot Deploy ===
echo.

set /p PATCH=Enter patch number:
echo.

set "LOOT_DIR=%~dp0..\..\specs\patches\%PATCH%\loot"
set "PROJECT_ROOT=%~dp0..\..\.."
set "DATASHEET=D:\dev\mmogate\tera92\server\Datasheet"

if not exist "%LOOT_DIR%" (
    echo ERROR: Loot directory not found: %LOOT_DIR%
    echo Run generate.bat first to generate zone specs.
    pause
    exit /b 1
)

set TOTAL=0
set FAILED=0

echo [1/2] Applying cCompensation specs...
echo.

set C_DIR=%LOOT_DIR%\c-compensation
if exist "%C_DIR%" (
    set C_TOTAL=0
    for %%f in ("%C_DIR%\zone-*.yaml") do set /a C_TOTAL+=1

    set C_CURRENT=0
    for %%f in ("%C_DIR%\zone-*.yaml") do (
        set /a C_CURRENT+=1
        set /a TOTAL+=1
        echo   [!C_CURRENT!/!C_TOTAL!] %%~nxf
        cd /d "%PROJECT_ROOT%"
        dsl apply "%%f" --path "%DATASHEET%"
        if errorlevel 1 (
            echo     FAILED: %%~nxf
            set /a FAILED+=1
        )
    )
) else (
    echo   No cCompensation specs found.
)
echo.

echo [2/2] Applying eCompensation specs...
echo.

set E_DIR=%LOOT_DIR%\e-compensation
if exist "%E_DIR%" (
    set E_TOTAL=0
    for %%f in ("%E_DIR%\zone-*.yaml") do set /a E_TOTAL+=1

    set E_CURRENT=0
    for %%f in ("%E_DIR%\zone-*.yaml") do (
        set /a E_CURRENT+=1
        set /a TOTAL+=1
        echo   [!E_CURRENT!/!E_TOTAL!] %%~nxf
        cd /d "%PROJECT_ROOT%"
        dsl apply "%%f" --path "%DATASHEET%"
        if errorlevel 1 (
            echo     FAILED: %%~nxf
            set /a FAILED+=1
        )
    )
) else (
    echo   No eCompensation specs found.
)
echo.

if %FAILED% gtr 0 (
    echo WARNING: %FAILED% of %TOTAL% specs failed to apply.
) else (
    echo All %TOTAL% zone specs applied successfully.
)
echo.

echo === Deploy complete ===
pause
