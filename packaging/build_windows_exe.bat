@echo off
setlocal

rem Switch to repository root
pushd "%~dp0\.."

if "%~1"=="" (
    set "PYTHON=python"
) else (
    set "PYTHON=%~1"
)

echo Packaging Kensho using %PYTHON%
echo.
%PYTHON% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --name Kensho ^
    --windowed ^
    --collect-all win10toast ^
    src\kensho\app.py

set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
    echo.
    echo PyInstaller failed with exit code %ERR%.
)

popd
exit /b %ERR%
