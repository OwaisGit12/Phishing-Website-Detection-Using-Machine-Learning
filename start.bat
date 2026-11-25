@echo off
title Starting Flask App
echo Starting Phishing Detector...

REM Move to this folder
cd /d "%~dp0"

REM Activate venv
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

REM Auto-open browser
start "" http://127.0.0.1:5000

REM Run your flask app
python app.py

pause