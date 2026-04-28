@echo off
chcp 65001 > nul
echo ================================================
echo  Car Price Predictor 2026 - Windows Setup
echo ================================================
echo.

echo [1/3] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: pip install failed. Make sure Python 3.12 is installed.
    pause
    exit /b 1
)

echo.
echo [2/3] Generating model files for your Python version...
set PYTHONIOENCODING=utf-8
python retrain_model.py
if %errorlevel% neq 0 (
    echo ERROR: retrain_model.py failed. See error above.
    pause
    exit /b 1
)

echo.
echo [3/3] Launching the app...
echo  Open your browser at: http://localhost:8501
echo.
set PYTHONIOENCODING=utf-8
streamlit run app.py

pause
