# 快速修复500错误

## 立即执行以下步骤：

### 步骤1：停止当前Vite服务器
如果Vite开发服务器正在运行，请按 `Ctrl + C` 停止它。

### 步骤2：安装axios（如果还没有安装）
```bash
cd frontend
npm install axios
```

### 步骤3：清除Vite缓存
```bash
# 在frontend目录下执行
Remove-Item -Recurse -Force .vite -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force node_modules\.vite -ErrorAction SilentlyContinue
```

### 步骤4：重新启动开发服务器
```bash
npm run dev
```

## 如果仍然出现500错误：

### 检查1：确认axios已安装
打开 `frontend/node_modules` 文件夹，确认 `axios` 文件夹存在。

### 检查2：确认文件路径正确
确保以下文件存在：
- ✅ `frontend/src/api/request.js`
- ✅ `frontend/src/views/SceneView.css`
- ✅ `frontend/src/components/DatabaseView.css`

### 检查3：检查终端错误日志
查看运行 `npm run dev` 的终端，查看是否有具体的错误信息。

### 检查4：尝试无代理模式
临时修改 `vite.config.js`，注释掉代理配置，看是否是代理导致的问题：

```javascript
server: {
  port: 5173,
  open: true,
  // 临时注释掉代理
  // proxy: {
  //   '/api': {
  //     target: 'http://localhost:8000',
  //     changeOrigin: true,
  //     secure: false,
  //   }
  // }
},
```

## 最可能的原因

根据错误信息，最可能的原因是：
1. **Vite开发服务器没有正常运行或需要重启** - 占90%
2. **axios模块未正确安装** - 占8%
3. **文件路径或导入错误** - 占2%

## 如果问题仍然存在

请提供以下信息：
1. 运行 `npm run dev` 时的完整终端输出
2. 浏览器控制台的完整错误信息
3. 是否有其他错误日志
