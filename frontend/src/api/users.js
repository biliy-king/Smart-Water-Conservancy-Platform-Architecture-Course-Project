import api from './request'

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.role - 角色类型 (admin/monitor/viewer)
 * @returns {Promise} 用户列表
 */
export function getUserProfileList(params = {}) {
  return api.get('/users/user-profiles/', { params })
}

/**
 * 获取单个用户档案
 * @param {number} id - 用户档案ID
 * @returns {Promise} 用户档案详情
 */
export function getUserProfile(id) {
  return api.get(`/users/user-profiles/${id}/`)
}

/**
 * 创建用户档案
 * @param {Object} data - 用户档案数据
 * @returns {Promise} 创建的用户档案
 */
export function createUserProfile(data) {
  return api.post('/users/user-profiles/', data)
}

/**
 * 更新用户档案
 * @param {number} id - 用户档案ID
 * @param {Object} data - 用户档案数据
 * @returns {Promise} 更新后的用户档案
 */
export function updateUserProfile(id, data) {
  return api.put(`/users/user-profiles/${id}/`, data)
}

/**
 * 删除用户档案
 * @param {number} id - 用户档案ID
 * @returns {Promise}
 */
export function deleteUserProfile(id) {
  return api.delete(`/users/user-profiles/${id}/`)
}
