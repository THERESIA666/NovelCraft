@echo off
title AI小说写作助手
cd /d "%~dp0"

echo.
echo   ==============================
echo     AI小说写作助手
echo   ==============================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] 未检测到 Python，请先安装 Python 3.10+
    echo   https://python.org
    pause
    exit /b 1
)
echo   [OK] Python 已就绪

:: 创建虚拟环境（如不存在）
if not exist "venv\" (
    echo   [*] 正在创建虚拟环境...
    python -m venv venv
    echo   [OK] 虚拟环境已创建
)

:: 激活虚拟环境并安装依赖
call venv\Scripts\activate.bat
echo   [*] 正在检查依赖...
pip install -r requirements.txt -q 2>nul
echo   [OK] 依赖已就绪

:: 打开浏览器
echo   [*] 正在打开浏览器...
start "" http://127.0.0.1:5000

echo.
echo   ==============================
echo     服务启动中...
echo     浏览器已自动打开
echo     如未打开，手动访问：
echo     http://127.0.0.1:5000
echo     按 Ctrl+C 停止
echo   ==============================
echo.

python app.py
pause
