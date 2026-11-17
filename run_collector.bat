
@echo off
cd /d "%~dp0"

if not exist "data" mkdir "data"

echo. >> "data\collector.log"
echo [%date% %time%] Collector started >> "data\collector.log"

".venv\Scripts\python.exe" -u "etl\collect_live.py" >> "data\collector.log" 2>&1

set "EXIT_CODE=%ERRORLEVEL%"

echo [%date% %time%] Finished with exit code %EXIT_CODE% >> "data\collector.log"

exit /b %EXIT_CODE%
