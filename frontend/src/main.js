import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as echarts from 'echarts'
import App from './App.vue'
import './assets/base.css'

const app = createApp(App)
app.use(ElementPlus)
app.config.globalProperties.$echarts = echarts
app.mount('#app')
