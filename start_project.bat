@echo off
cd /d %~dp0

start cmd /k "C:\Redis\redis-server.exe"
start cmd /k "venv\Scripts\activate && python manage.py runserver"
start cmd /k "venv\Scripts\activate && python manage.py run_cue_engine"