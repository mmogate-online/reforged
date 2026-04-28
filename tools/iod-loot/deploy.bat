@echo off
cd /d "%~dp0"

set /p PATCH=Enter patch number (e.g. 001):

set "SPEC=%~dp0..\..\specs\patches\%PATCH%\17-iod-loot.yaml"
set "PROJECT_ROOT=%~dp0..\..\.."
set "DATASHEET=D:\dev\mmogate\tera92\server\Datasheet"

if not exist "%SPEC%" (
    echo ERROR: Spec not found: %SPEC%
    echo Run generate.bat first.
    pause
    exit /b 1
)

cd /d "%PROJECT_ROOT%"

echo Validating...
dsl validate "%SPEC%" --path "%DATASHEET%"
if errorlevel 1 (
    echo Validation failed.
    pause
    exit /b 1
)

echo Applying...
dsl apply "%SPEC%" --path "%DATASHEET%"
if errorlevel 1 (
    echo Apply failed.
    pause
    exit /b 1
)

echo Done.
pause
