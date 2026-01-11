
# Cesium Earth Viewer

本项目为基于 CesiumJS 的三维地球可视化前端，使用 Vue3 + Vite 构建。

## 主要功能
- 加载 Cesium 地球并进行三维可视化展示
- 支持自定义地球场景和数据扩展

## 快速开始
1. 安装依赖：
   ```sh
   npm install
   ```
2. 启动开发环境：
   ```sh
   npm run dev
   ```

## 目录结构说明
- `public/Cesium-1.136/`：CesiumJS 主库及资源文件
- `src/components/CesiumViewer.vue`：地球核心组件
- `src/App.vue`、`src/main.js`：应用入口
- `index.html`：主页面
- `vite.config.js`、`package.json`：配置与依赖

## 其他说明
如需扩展地球功能，请在 `CesiumViewer.vue` 中进行开发。

```sh
npm run lint
```
