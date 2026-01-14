import api from './request'

/**
 * 用户注册
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise} 注册响应
 */
export function register(username, password) {
  return api.post('/users/register/', {
    username,
    password
  })
}

/**
 * 用户登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise} 登录响应
 */
export function login(username, password) {
  return api.post('/users/login/', {
    username,
    password
  })
}

/**
 * 刷新Token
 * @param {string} refreshToken - refresh token
 * @returns {Promise} 刷新响应
 */
export function refreshToken(refreshToken) {
  return api.post('/users/refresh/', {
    refresh: refreshToken
  })
}

/**
 * 获取当前用户信息
 * @returns {Promise} 用户信息
 */
export function getCurrentUser() {
  return api.get('/users/current/')
}