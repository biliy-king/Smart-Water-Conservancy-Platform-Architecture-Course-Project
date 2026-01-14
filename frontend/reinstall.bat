@echo off
chcp 65001 >nul
echo ====================================
echo 重新安装前端依赖
echo ====================================
echo.

cd /d "%~dp0"

echo [1/4] 检查当前目录...
if not exist "package.json" (
    echo 错误: 未找到 package.json，请确保在 frontend 目录下运行此脚本
    pause
    exit /b 1
)

echo [2/4] 清理旧的依赖（如果存在）...
if exist "node_modules" (
    echo 删除 node_modules 文件夹...
    rmdir /s /q node_modules
)

echo [3/4] 清理缓存...
call npm cache clean --force

echo [4/4] 安装依赖...
call npm install

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================
    echo 安装完成！
    echo ====================================
    echo.
    echo 现在可以运行: npm run dev
) else (
    echo.
    echo ====================================
    echo 安装失败，请检查错误信息
    echo ====================================
)

echo.
pause
