import axios from 'axios'
import { clearAuth } from '../store/auth'

// 创建axios实例
const api = axios.create({
  baseURL: '/api', // 使用代理，避免跨域问题
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：自动添加Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理401并自动刷新Token
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // 如果是401错误且未重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          throw new Error('没有refresh token')
        }

        // 尝试刷新token（使用相对路径，通过代理访问）
        const { data } = await axios.post('/api/users/refresh/', {
          refresh: refreshToken
        })

        // 更新token
        localStorage.setItem('access_token', data.tokens.access)
        localStorage.setItem('refresh_token', data.tokens.refresh)

        // 更新请求头并重新发送原请求
        originalRequest.headers['Authorization'] = `Bearer ${data.tokens.access}`
        return api(originalRequest)
      } catch (refreshError) {
        // 刷新失败，清除token并更新认证状态
        clearAuth()
        
        // 触发自定义事件，通知App.vue更新视图
        window.dispatchEvent(new CustomEvent('auth:logout'))
        
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api