# 重新安装依赖说明

## 当前项目需要的依赖

根据 `package.json`，项目需要以下依赖：

### 生产依赖 (dependencies)
- `vue`: ^3.4.0 - Vue框架
- `element-plus`: ^2.4.0 - UI组件库
- `echarts`: ^5.4.0 - 图表库
- `cesium`: ^1.136.0 - 3D地球/地图库
- `axios`: ^1.6.0 - HTTP请求库（我们新添加的）

### 开发依赖 (devDependencies)
- `@vitejs/plugin-vue`: ^4.4.0 - Vite的Vue插件
- `vite`: ^4.4.0 - 构建工具

## 重新安装步骤

### 方法1：直接重新安装（推荐）

在 `frontend` 目录下打开终端（PowerShell 或 CMD），执行：

```bash
npm install
```

### 方法2：清理后重新安装（如果方法1不行）

```bash
# 1. 删除 node_modules 文件夹（如果存在）
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue

# 2. 删除 package-lock.json（可选）
Remove-Item package-lock.json -ErrorAction SilentlyContinue

# 3. 清除 npm 缓存（可选）
npm cache clean --force

# 4. 重新安装
npm install
```

### 方法3：使用国内镜像（如果下载慢）

```bash
# 使用淘宝镜像
npm install --registry=https://registry.npmmirror.com
```

## 验证安装

安装完成后，检查依赖是否正确安装：

```bash
npm list --depth=0
```

应该看到所有依赖都列出来了。

## 如果遇到权限错误

如果遇到权限错误，可以：

1. **以管理员身份运行 PowerShell**
   - 右键点击 PowerShell
   - 选择"以管理员身份运行"
   - 然后执行安装命令

2. **或者使用 npm 的 --force 参数**
   ```bash
   npm install --force
   ```

## 安装完成后

安装完成后，启动开发服务器：

```bash
npm run dev
```

如果一切正常，应该能看到 Vite 开发服务器启动，并自动打开浏览器。
