import api from './request'

/**
 * 获取大坝列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 大坝列表
 */
export function getStructures(params = {}) {
  return api.get('/water-structures/structures/', { params })
}

/**
 * 获取单个大坝详情
 * @param {number} id - 大坝ID
 * @returns {Promise} 大坝详情
 */
export function getStructure(id) {
  return api.get(`/water-structures/structures/${id}/`)
}

/**
 * 获取监测设备列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 设备列表
 */
export function getDevices(params = {}) {
  return api.get('/water-structures/devices/', { params })
}

/**
 * 获取单个设备详情
 * @param {number} id - 设备ID
 * @returns {Promise} 设备详情
 */
export function getDevice(id) {
  return api.get(`/water-structures/devices/${id}/`)
}

/**
 * 获取监测点列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 监测点列表
 */
export function getPoints(params = {}) {
  return api.get('/water-structures/points/', { params })
}

/**
 * 获取有监测数据的测点列表
 * @returns {Promise} 有数据的测点列表
 */
export function getPointsWithData() {
  return api.get('/water-structures/points/with_data/')
}

/**
 * 获取单个监测点详情
 * @param {number} id - 监测点ID
 * @returns {Promise} 监测点详情
 */
export function getPoint(id) {
  return api.get(`/water-structures/points/${id}/`)
}

/**
 * 获取监测点阈值
 * @param {number} id - 监测点ID
 * @returns {Promise} 阈值信息
 */
export function getPointThresholds(id) {
  return api.get(`/water-structures/points/${id}/thresholds/`)
}

/**
 * 更新监测点阈值
 * @param {number} id - 监测点ID
 * @param {Object} thresholds - 阈值数据
 * @returns {Promise} 更新后的阈值信息
 */
export function updatePointThresholds(id, thresholds) {
  return api.put(`/water-structures/points/${id}/thresholds/`, thresholds)
}

/**
 * 创建大坝
 * @param {Object} data - 大坝数据
 * @returns {Promise} 创建的大坝
 */
export function createStructure(data) {
  return api.post('/water-structures/structures/', data)
}

/**
 * 更新大坝
 * @param {number} id - 大坝ID
 * @param {Object} data - 大坝数据
 * @returns {Promise} 更新后的大坝
 */
export function updateStructure(id, data) {
  return api.put(`/water-structures/structures/${id}/`, data)
}

/**
 * 删除大坝
 * @param {number} id - 大坝ID
 * @returns {Promise}
 */
export function deleteStructure(id) {
  return api.delete(`/water-structures/structures/${id}/`)
}