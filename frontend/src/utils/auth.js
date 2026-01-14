/**
 * 认证工具函数
 * 用于检查用户登录状态和管理认证信息
 */

/**
 * 检查用户是否已登录
 * @returns {boolean} 是否已登录
 */
export function isAuthenticated() {
  const token = localStorage.getItem('access_token')
  return !!token
}

/**
 * 获取当前用户的Token
 * @returns {string|null} access token
 */
export function getToken() {
  return localStorage.getItem('access_token')
}

/**
 * 获取当前用户信息
 * @returns {object|null} 用户信息
 */
export function getCurrentUser() {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch (e) {
      console.error('解析用户信息失败:', e)
      return null
    }
  }
  return null
}

/**
 * 清除所有认证信息
 */
export function clearAuth() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
}

/**
 * 保存认证信息
 * @param {string} accessToken - access token
 * @param {string} refreshToken - refresh token
 * @param {object} user - 用户信息
 */
export function saveAuth(accessToken, refreshToken, user) {
  localStorage.setItem('access_token', accessToken)
  localStorage.setItem('refresh_token', refreshToken)
  localStorage.setItem('user', JSON.stringify(user))
}
