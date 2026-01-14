# 前端500错误排查指南

## 问题描述
前端资源文件（SceneView.css, DatabaseView.vue, request.js）返回500错误。

## 解决方案

### 方案1：重启Vite开发服务器（最常见）

1. **停止当前运行的开发服务器**
   - 在运行 `npm run dev` 的终端中按 `Ctrl + C`

2. **清除缓存并重新启动**
   ```bash
   cd frontend
   # Windows PowerShell
   Remove-Item -Recurse -Force node_modules\.vite -ErrorAction SilentlyContinue
   npm run dev
   ```

### 方案2：确保axios已安装

如果axios未正确安装，可能导致模块解析失败：

```bash
cd frontend
npm install axios
```

### 方案3：检查后端服务是否在运行

确保Django后端服务正在 `http://localhost:8000` 运行。如果后端未运行，代理请求会失败。

```bash
# 在backend目录下
python manage.py runserver
```

### 方案4：检查端口占用

确保端口5173没有被其他程序占用：

```bash
# Windows PowerShell
netstat -ano | findstr :5173
```

如果端口被占用，可以：
1. 关闭占用端口的程序
2. 或者修改 `vite.config.js` 中的端口号

### 方案5：检查文件是否存在

确保以下文件存在：
- `frontend/src/api/request.js`
- `frontend/src/views/SceneView.css`
- `frontend/src/components/DatabaseView.vue`

### 方案6：重新安装依赖

如果以上方法都不行，尝试重新安装所有依赖：

```bash
cd frontend
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm install
npm run dev
```

## 常见原因

1. **Vite服务器未正确启动** - 最常见
2. **axios未安装** - 导致模块解析失败
3. **端口冲突** - 5173端口被占用
4. **文件路径错误** - 导入路径不正确
5. **代理配置问题** - 代理将前端资源误转发到后端

## 如果问题仍然存在

1. 检查浏览器控制台的完整错误信息
2. 检查终端中Vite服务器的错误日志
3. 确认所有依赖都已正确安装
4. 尝试在无痕模式下打开页面，排除浏览器缓存问题
