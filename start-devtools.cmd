@echo off
cd /d "%~dp0"
docker compose -f docker-compose.yml -f docker-compose.devtools.yml up -d devtools
if errorlevel 1 (
  echo Docker failed. Open Docker Desktop and try again.
  pause
  exit /b 1
)
start "" http://localhost:8766
pause
