import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: true,  // 允许外部访问
    open: true,  // 自动打开浏览器
    cors: true,  // 允许跨域
    // 重要：允许服务静态资源
    fs: {
      allow: ['..']
    }
  },
  // 配置根目录
  root: '.',
  // 静态资源处理
  publicDir: 'public',
  // 配置别名
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  // 构建配置
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  },
  // 优化依赖
  optimizeDeps: {
    exclude: ['cesium']
  }
})