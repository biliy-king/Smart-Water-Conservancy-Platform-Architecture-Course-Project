/**
 * 测点映射关系
 * EX1对应EX1-2-位移mm，EX2对应EX1-3-位移mm，以此类推
 */
export const SENSOR_TO_CODE_MAP = {
  'EX1': 'EX1-2-位移mm',
  'EX2': 'EX1-3-位移mm',
  'EX3': 'EX1-4-位移mm',
  'EX4': 'EX1-5-位移mm',
  'EX5': 'EX1-6-位移mm',
  'EX6': 'EX1-7-位移mm',
  'EX7': 'EX1-8-位移mm',
  'EX8': 'EX1-9-位移mm',
  'EX9': 'EX1-10-位移mm',
  'EX10': 'EX1-11-位移mm'
}

/**
 * 根据测点名称获取对应的测点代码
 * @param {string} sensorName - 测点名称（如EX1）
 * @returns {string|null} 测点代码（如EX1-2-位移mm）
 */
export function getSensorCode(sensorName) {
  return SENSOR_TO_CODE_MAP[sensorName] || null
}
