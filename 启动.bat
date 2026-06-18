@echo off
chcp 65001 >nul
title AI小说写作助手
echo ================================
echo   📖 AI小说写作助手
echo ================================
echo.
echo 正在启动服务...
echo.

cd /d "%~dp0"

:: 检查依赖是否安装
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo 正在安装依赖...
    pip install -r requirements.txt
    echo.
)

:: 启动应用
echo 服务已启动！请在浏览器中打开：
echo http://127.0.0.1:5000
echo.
echo 按 Ctrl+C 停止服务
echo ================================
python app.py

pause
