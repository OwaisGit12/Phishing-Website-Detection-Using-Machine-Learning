@echo off
title Starting Flask App + Admin Page
echo Starting Phishing Detector (Admin)...

REM Move to script folder
cd /d "%~dp0"

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install required packages (only if missing)
echo Checking required packages...
pip show flask >nul 2>&1 || pip install flask
pip show joblib >nul 2>&1 || pip install joblib
pip show pandas >nul 2>&1 || pip install pandas
pip show xgboost >nul 2>&1 || pip install xgboost

echo.
echo Launching App...

REM Open browser directly to admin login
start "" http://127.0.0.1:5000/admin/login

REM Run Flask app
python app.py

pause