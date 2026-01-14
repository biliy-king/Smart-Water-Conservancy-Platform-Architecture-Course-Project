/**
 * 认证状态管理
 * 使用响应式状态管理登录状态，确保token变化时UI能及时更新
 */
import { ref, computed } from 'vue'
import { isAuthenticated as checkAuth, clearAuth as clearAuthData } from '../utils/auth'

// 全局响应式状态
const isLoggedIn = ref(checkAuth())

// 更新登录状态
export function updateAuthStatus() {
  isLoggedIn.value = checkAuth()
}

// 清除认证并更新状态
export function clearAuth() {
  clearAuthData()
  isLoggedIn.value = false
}

// 设置已登录状态
export function setLoggedIn() {
  isLoggedIn.value = true
}

// 导出响应式状态
export function useAuth() {
  return {
    isLoggedIn: computed(() => isLoggedIn.value),
    updateAuthStatus,
    clearAuth,
    setLoggedIn
  }
}
