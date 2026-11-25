@echo off
cd /d "%~dp0"
start "Patient Portal - 5000" cmd /k python patient_app.py
start "Medical Shop Portal - 5001" cmd /k python shop_app.py
