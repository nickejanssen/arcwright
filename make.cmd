@echo off
setlocal

set "PYTHON=%PYTHON%"
if not defined PYTHON set "PYTHON=python"

if "%~1"=="" goto help
if /I "%~1"=="lint" goto lint
if /I "%~1"=="type" goto type
if /I "%~1"=="test" goto test
if /I "%~1"=="migrate" goto migrate
if /I "%~1"=="rehearsal" goto rehearsal
if /I "%~1"=="rehearsal-stop" goto rehearsal-stop
if /I "%~1"=="rehearsal-smoke" goto rehearsal-smoke

echo Unknown target: %~1
goto help

:lint
%PYTHON% -m ruff check --config pyproject.toml engine api
exit /b %ERRORLEVEL%

:type
%PYTHON% -m mypy --config-file pyproject.toml engine api
exit /b %ERRORLEVEL%

:test
%PYTHON% -c "import sys, pytest; code = pytest.main(['-c', 'pyproject.toml', 'tests']); sys.exit(0 if code == 5 else code)"
exit /b %ERRORLEVEL%

:migrate
%PYTHON% -m alembic upgrade head
exit /b %ERRORLEVEL%

:rehearsal
%PYTHON% scripts\rehearsal.py
exit /b %ERRORLEVEL%

:rehearsal-stop
docker compose down
exit /b %ERRORLEVEL%

:rehearsal-smoke
%PYTHON% scripts\rehearsal_smoke.py
exit /b %ERRORLEVEL%

:help
echo Usage: make ^<lint^|type^|test^|migrate^|rehearsal^|rehearsal-stop^|rehearsal-smoke^>
exit /b 1
