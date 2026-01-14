import api from './request'

/**
 * 获取监测数据列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {number} params.point - 监测点ID
 * @param {string} params.start_time - 开始时间
 * @param {string} params.end_time - 结束时间
 * @param {string} params.status - 状态 (normal/warning/alarm)
 * @returns {Promise} 监测数据列表
 */
export function getMonitorDataList(params = {}) {
  // 后端路由为 /api/monitoring/data/
  return api.get('/monitoring/data/', { params })
}

/**
 * 获取单条监测数据
 * @param {number} id - 监测数据ID
 * @returns {Promise} 监测数据详情
 */
export function getMonitorData(id) {
  return api.get(`/monitoring/data/${id}/`)
}

/**
 * 新增监测数据
 * @param {Object} data - 监测数据
 * @returns {Promise} 创建的监测数据
 */
export function createMonitorData(data) {
  return api.post('/monitoring/data/', data)
}

/**
 * 批量新增监测数据
 * @param {Array} dataList - 监测数据数组
 * @returns {Promise} 批量创建结果
 */
export function batchCreateMonitorData(dataList) {
  // 后端暂未提供批量接口，如需批量请实现 /api/monitoring/data/batch/
  return api.post('/monitoring/data/batch/', dataList)
}

/**
 * 获取数据统计
 * @returns {Promise} 统计数据
 */
export function getStatistics() {
  return api.get('/monitoring/statistics/')
}

/**
 * 获取指定测点的最新监测数据（虚拟实时数据）
 * @param {number} pointId - 测点ID
 * @returns {Promise} 最新监测数据
 */
export function getLatestDataByPoint(pointId) {
  return api.get(`/monitoring/latest/${pointId}/`)
}

/**
 * 获取指定测点的历史数据
 * @param {number} pointId - 测点ID
 * @param {Object} params - 查询参数
 * @param {number} params.days - 查询天数，默认7天
 * @param {number} params.page - 页码，默认1
 * @param {number} params.size - 每页数量，默认100
 * @returns {Promise} 历史数据
 */
export function getHistoryDataByPoint(pointId, params = {}) {
  return api.get(`/monitoring/history/${pointId}/`, { params })
}

/**
 * 更新监测数据
 * @param {number} id - 监测数据ID
 * @param {Object} data - 监测数据
 * @returns {Promise} 更新后的监测数据
 */
export function updateMonitorData(id, data) {
  return api.put(`/monitoring/data/${id}/`, data)
}

/**
 * 删除监测数据
 * @param {number} id - 监测数据ID
 * @returns {Promise}
 */
export function deleteMonitorData(id) {
  return api.delete(`/monitoring/data/${id}/`)
}

/**
 * 批量删除监测数据
 * @param {Array} ids - 监测数据ID数组
 * @returns {Promise}
 */
export function batchDeleteMonitorData(ids) {
  return api.post('/monitoring/data/batch-delete/', { ids })
}