@echo off
setlocal
cd /d "%~dp0"
python auto_coexist.py
if errorlevel 1 (
    echo.
    echo Auto coexist failed.
) else (
    echo.
    echo Auto coexist finished successfully.
)
pause
