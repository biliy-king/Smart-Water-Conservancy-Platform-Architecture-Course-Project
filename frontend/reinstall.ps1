# PowerShell 脚本：重新安装依赖
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "重新安装前端依赖" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 检查 package.json
if (-not (Test-Path "package.json")) {
    Write-Host "错误: 未找到 package.json，请确保在 frontend 目录下运行此脚本" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}

# 步骤1: 清理旧的依赖
Write-Host "[1/4] 清理旧的依赖（如果存在）..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "删除 node_modules 文件夹..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
}

# 步骤2: 清理缓存
Write-Host "[2/4] 清理 npm 缓存..." -ForegroundColor Yellow
npm cache clean --force

# 步骤3: 安装依赖
Write-Host "[3/4] 安装依赖..." -ForegroundColor Yellow
npm install

# 检查安装结果
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "安装完成！" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "现在可以运行: npm run dev" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Red
    Write-Host "安装失败，请检查错误信息" -ForegroundColor Red
    Write-Host "====================================" -ForegroundColor Red
}

Write-Host ""
Read-Host "按 Enter 键退出"
