@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   AI PMO Agent (Windows CSV Edition)
echo ========================================

where py >nul 2>&1
if %errorlevel%==0 (
    set PY=py -3
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        set PY=python
    ) else (
        echo [錯誤] 找不到 Python，請先安裝 Python 3.9+
        pause
        exit /b 1
    )
)

if not exist ".venv\Scripts\activate.bat" (
    echo 建立虛擬環境...
    %PY% -m venv .venv
)

call .venv\Scripts\activate.bat

echo 安裝依賴...
pip install -r requirements.txt -q

if not exist "data\projects.csv" (
    echo 初始化 CSV 資料...
    python init_data.py
)

echo.
echo 啟動 Streamlit（不需 uvicorn）...
echo 瀏覽器開啟 http://localhost:8501
echo 按 Ctrl+C 停止
echo.

streamlit run app.py

pause
