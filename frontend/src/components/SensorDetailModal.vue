<template>
  <div class="sensor-modal-overlay" @click.self="closeModal">
    <div class="page flex-col">
      <div class="section_1 flex-col justify-end">
        <!-- 关闭按钮 -->
        <button class="close-btn" @click="closeModal">×</button>
        
        <!-- 标题 -->
        <span class="text_1">{{ pointInfo.device_info?.device_name || '设备详情' }}</span>
        
        <!-- 测点名称 -->
        <span class="text_2">测点：{{ pointInfo.point_code || sensorName || '--' }}</span>
        
        <!-- 设备类型 -->
        <span class="text_3">设备类型：{{ getDeviceTypeName(pointInfo.device_info?.device_type) || '--' }}</span>
        
        <!-- 安装位置 -->
        <span class="text_5">安装位置：{{ pointInfo.device_info?.install_position || '--' }}</span>
        
        <!-- 状态 -->
        <div class="box_1 flex-row">
          <span class="text_6">状态：</span>
          <div class="section_2 flex-col justify-between">
            <div class="box_2" :class="{ active: currentStatus === 'normal' }"></div>
            <div class="box_3" :class="{ active: currentStatus === 'alarm' || currentStatus === 'abnormal' || currentStatus === 'warning' }"></div>
          </div>
          <div class="text-group_1 flex-col justify-between">
            <span class="text_7">正常</span>
            <span class="text_8">异常</span>
          </div>
        </div>
        
        <!-- 虚拟实时数据表格 -->
        <div class="table-container">
          <div class="table-title">实时监测数据</div>
          <div v-if="tableLoading" class="table-loading">加载中...</div>
          <div v-else-if="tableError" class="table-error">{{ tableError }}</div>
          <el-table 
            v-else
            :data="realtimeTableData" 
            style="width: 100%"
            :max-height="400"
            stripe
            border
          >
            <el-table-column prop="time" label="时间" width="180" />
            <!-- 根据设备类型动态显示对应的监测字段 -->
            <el-table-column 
              v-if="shouldShowColumn('water_level_upstream')"
              prop="value" 
              label="上游水位(m)" 
              width="140"
            >
              <template #default="scope">
                <span v-if="scope.row.value !== null && scope.row.value !== undefined">
                  {{ scope.row.value.toFixed(3) }}
                </span>
                <span v-else>--</span>
              </template>
            </el-table-column>
            <el-table-column 
              v-if="shouldShowColumn('water_level_downstream')"
              prop="value" 
              label="下游水位(m)" 
              width="140"
            >
              <template #default="scope">
                <span v-if="scope.row.value !== null && scope.row.value !== undefined">
                  {{ scope.row.value.toFixed(3) }}
                </span>
                <span v-else>--</span>
              </template>
            </el-table-column>
            <el-table-column 
              v-if="shouldShowColumn('inverted_plumb_up_down')"
              prop="value" 
              label="倒垂线-上下游位移(mm)" 
              width="200"
            >
              <template #default="scope">
                <span v-if="scope.row.value !== null && scope.row.value !== undefined">
                  {{ scope.row.value.toFixed(2) }}
                </span>
                <span v-else>--</span>
              </template>
            </el-table-column>
            <el-table-column 
              v-if="shouldShowColumn('inverted_plumb_left_right')"
              prop="value" 
              label="倒垂线-左右岸位移(mm)" 
              width="200"
            >
              <template #default="scope">
                <span v-if="scope.row.value !== null && scope.row.value !== undefined">
                  {{ scope.row.value.toFixed(2) }}
                </span>
                <span v-else>--</span>
              </template>
            </el-table-column>
            <el-table-column 
              v-if="shouldShowColumn('hydrostatic_leveling')"
              prop="value" 
              label="静力水准沉降(mm)" 
              width="180"
            >
              <template #default="scope">
                <span v-if="scope.row.value !== null && scope.row.value !== undefined">
                  {{ scope.row.value.toFixed(2) }}
                </span>
                <span v-else>--</span>
              </template>
            </el-table-column>
            <el-table-column 
              v-if="shouldShowColumn('tension_wire_up_down')"
              prop="value" 
              label="引张线-上下游位移(mm)" 
              width="200"
            >
              <template #default="scope">
                <span v-if="scope.row.value !== null && scope.row.value !== undefined">
                  {{ scope.row.value.toFixed(2) }}
                </span>
                <span v-else>--</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag 
                  :type="getStatusTagType(scope.row.status)"
                  size="small"
                >
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { getPoint } from '@/api/waterStructures'
import { getLatestDataByPoint } from '@/api/monitoring'

const props = defineProps({
  sensorName: {
    type: String,
    default: '传感器EX1'
  },
  status: {
    type: String,
    default: 'normal'
  },
  pointId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['close'])

const pointInfo = ref({})
const loading = ref(false)
const error = ref(null)
const currentStatus = ref(props.status)

// 实时数据表格相关
const realtimeTableData = ref([])
const tableLoading = ref(false)
const tableError = ref(null)
let refreshTimer = null // 定时刷新器

// 状态文本映射
const statusTextMap = {
  normal: '正常',
  warning: '预警',
  alarm: '告警',
  abnormal: '异常'
}

// 获取状态文本
function getStatusText(status) {
  return statusTextMap[status] || '未知'
}

// 获取状态标签类型
function getStatusTagType(status) {
  const typeMap = {
    normal: 'success',
    warning: 'warning',
    alarm: 'danger',
    abnormal: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取设备类型中文名称
function getDeviceTypeName(deviceType) {
  const typeMap = {
    'water_level_upstream': '水位传感器-上游',
    'water_level_downstream': '水位传感器-下游',
    'inverted_plumb_up_down': '倒垂线-上下游位移',
    'inverted_plumb_left_right': '倒垂线-左右岸位移',
    'hydrostatic_leveling': '静力水准-沉降',
    'tension_wire_up_down': '引张线-上下游位移'
  }
  return typeMap[deviceType] || deviceType || '--'
}

// 判断是否应该显示该列
function shouldShowColumn(fieldName) {
  const deviceType = pointInfo.value.device_info?.device_type
  if (!deviceType) return false
  
  // 设备类型到字段名的映射
  const deviceTypeToField = {
    'water_level_upstream': 'water_level_upstream',
    'water_level_downstream': 'water_level_downstream',
    'inverted_plumb_up_down': 'inverted_plumb_up_down',
    'inverted_plumb_left_right': 'inverted_plumb_left_right',
    'hydrostatic_leveling': 'hydrostatic_leveling',
    'tension_wire_up_down': 'tension_wire_up_down'
  }
  
  return deviceTypeToField[deviceType] === fieldName
}

// 格式化时间
function formatTime(timeStr) {
  if (!timeStr) return '--'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 加载测点基本信息
async function loadPointInfo() {
  const pointId = typeof props.pointId === 'number' ? props.pointId : parseInt(props.pointId)
  
  if (!pointId || isNaN(pointId)) {
    console.warn('未提供有效的测点ID（数字），无法加载详细信息', props.pointId)
    error.value = '未找到测点ID，无法加载详细信息'
    return
  }

  try {
    loading.value = true
    error.value = null
    
    console.log('正在加载测点信息，ID:', pointId)
    const response = await getPoint(pointId)
    pointInfo.value = response.data
    
    // 更新状态
    if (pointInfo.value.current_status) {
      currentStatus.value = pointInfo.value.current_status
    }
    
    console.log('测点信息加载成功:', pointInfo.value)
  } catch (err) {
    console.error('加载测点信息失败:', err)
    if (err.response?.status === 404) {
      error.value = `测点ID ${pointId} 不存在，请检查测点是否已正确配置`
    } else {
      error.value = '加载测点信息失败: ' + (err.message || '未知错误')
    }
  } finally {
    loading.value = false
  }
}

// 获取虚拟实时数据
async function fetchRealtimeData() {
  const pointId = typeof props.pointId === 'number' ? props.pointId : parseInt(props.pointId)
  
  if (!pointId || isNaN(pointId)) {
    console.warn('未提供有效的测点ID，无法加载实时数据', props.pointId)
    realtimeTableData.value = []
    return
  }

  try {
    tableLoading.value = true
    tableError.value = null
    
    console.log('正在获取实时数据，测点ID:', pointId)
    const response = await getLatestDataByPoint(pointId)
    
    console.log('实时数据接口响应:', response.data)
    
    // 处理实时数据
    let data = null
    if (response.data && response.data.success && response.data.data) {
      data = response.data.data
    } else if (response.data && response.data.data) {
      data = response.data.data
    } else {
      data = response.data
    }
    
    // 转换为表格数据格式
    // 虚拟实时数据接口返回格式：{ success: true, data: { value, timestamp, status, field_name, unit } }
    if (data) {
      let tableRow = null
      
      // 如果返回的是单个对象（虚拟实时数据格式）
      if (typeof data === 'object' && !Array.isArray(data)) {
        if (data.value !== undefined) {
          // 这是 generate_baseline_value 返回的虚拟实时数据格式
          tableRow = {
            time: formatTime(data.timestamp || data.last_update_time || new Date().toISOString()),
            value: data.value,
            status: data.status || 'normal',
            unit: data.unit || ''
          }
        } else if (data.point_id || data.point || data.point_info) {
          // 这是完整的监测数据对象，需要根据设备类型提取对应字段
          const deviceType = pointInfo.value.device_info?.device_type
          let value = null
          
          // 根据设备类型提取对应的监测值
          if (deviceType === 'water_level_upstream') {
            value = data.water_level_upstream
          } else if (deviceType === 'water_level_downstream') {
            value = data.water_level_downstream
          } else if (deviceType === 'inverted_plumb_up_down') {
            value = data.inverted_plumb_up_down
          } else if (deviceType === 'inverted_plumb_left_right') {
            value = data.inverted_plumb_left_right
          } else if (deviceType === 'hydrostatic_leveling') {
            value = data.hydrostatic_leveling_settlement
          } else if (deviceType === 'tension_wire_up_down') {
            value = data.tension_wire_up_down
          }
          
          tableRow = {
            time: formatTime(data.monitor_time || data.created_at || data.timestamp),
            value: value,
            status: data.status || 'normal',
            unit: ''
          }
        }
      } else if (Array.isArray(data)) {
        // 如果是数组，处理每个元素
        const newRows = data.map(item => {
          const deviceType = pointInfo.value.device_info?.device_type
          let value = null
          
          if (deviceType === 'water_level_upstream') {
            value = item.water_level_upstream
          } else if (deviceType === 'water_level_downstream') {
            value = item.water_level_downstream
          } else if (deviceType === 'inverted_plumb_up_down') {
            value = item.inverted_plumb_up_down
          } else if (deviceType === 'inverted_plumb_left_right') {
            value = item.inverted_plumb_left_right
          } else if (deviceType === 'hydrostatic_leveling') {
            value = item.hydrostatic_leveling_settlement
          } else if (deviceType === 'tension_wire_up_down') {
            value = item.tension_wire_up_down
          }
          
          return {
            time: formatTime(item.monitor_time || item.created_at || item.timestamp),
            value: value,
            status: item.status || 'normal',
            unit: ''
          }
        })
        
        realtimeTableData.value = [...newRows, ...realtimeTableData.value].slice(0, 20)
        return
      }
      
      // 添加新数据到表格顶部（最新数据在前）
      if (tableRow && tableRow.value !== null && tableRow.value !== undefined) {
        realtimeTableData.value.unshift(tableRow)
        
        // 只保留最近20条数据
        if (realtimeTableData.value.length > 20) {
          realtimeTableData.value = realtimeTableData.value.slice(0, 20)
        }
        
        // 更新状态
        if (tableRow.status) {
          currentStatus.value = tableRow.status
        }
      }
    }
    
    console.log('实时数据加载成功，表格数据:', realtimeTableData.value)
  } catch (err) {
    console.error('加载实时数据失败:', err)
    tableError.value = '加载实时数据失败: ' + (err.message || '未知错误')
  } finally {
    tableLoading.value = false
  }
}

// 启动定时刷新
function startAutoRefresh() {
  // 清除之前的定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 如果有 pointId，每 5 秒刷新一次实时数据
  const pointId = typeof props.pointId === 'number' ? props.pointId : parseInt(props.pointId)
  if (pointId && !isNaN(pointId)) {
    refreshTimer = setInterval(() => {
      console.log('定时刷新实时数据...')
      fetchRealtimeData()
    }, 5000) // 5秒刷新一次
  }
}

// 停止定时刷新
function stopAutoRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  realtimeTableData.value = []
}

function closeModal() {
  stopAutoRefresh() // 关闭弹窗时停止定时刷新
  emit('close')
}

// 监听 pointId 变化
watch(() => props.pointId, (newId) => {
  // 停止之前的定时器
  stopAutoRefresh()
  
  if (newId) {
    loadPointInfo()
    // 立即加载一次实时数据
    fetchRealtimeData().then(() => {
      // 数据加载完成后启动定时刷新
      startAutoRefresh()
    })
  } else {
    // 如果 pointId 为 null（前端写死模式），至少显示测点名称
    pointInfo.value = {
      point_code: props.sensorName || '传感器EX1',
      device: {
        model: '--',
        measurement_object: '--',
        range: '--'
      },
      location: '--'
    }
    realtimeTableData.value = []
  }
}, { immediate: true })

// 组件挂载时加载数据
onMounted(() => {
  if (props.pointId) {
    loadPointInfo()
    // 立即加载一次实时数据
    fetchRealtimeData().then(() => {
      // 数据加载完成后启动定时刷新
      startAutoRefresh()
    })
  } else {
    // 如果 pointId 为 null（前端写死模式），至少显示测点名称
    pointInfo.value = {
      point_code: props.sensorName || '传感器EX1',
      device: {
        model: '--',
        measurement_object: '--',
        range: '--'
      },
      location: '--'
    }
    realtimeTableData.value = []
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.sensor-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.page {
  position: relative;
  width: 819px;
  height: 1161px;
  overflow: hidden;
}

.section_1 {
  background-color: rgba(255, 252, 214, 1);
  border-radius: 30px;
  width: 819px;
  height: 1161px;
  border: 5px solid rgba(247, 226, 88, 1);
  padding: 53px 83px 40px 83px;
  position: relative;
  box-sizing: border-box;
  overflow-y: auto;
}

.text_1 {
  width: 288px;
  height: 104px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 64px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 64px;
  margin: 0 0 0 183px;
}

.text_2 {
  width: 120px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin: 64px 0 0 0;
}

.text_3 {
  width: 200px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin: 27px 0 0 0;
}

.text_4 {
  width: 120px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin: 27px 0 0 0;
}

.text_5 {
  width: 200px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin: 27px 0 0 0;
}

.box_1 {
  width: 303px;
  height: 136px;
  margin: 27px 0 0 0;
}

.text_6 {
  width: 120px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
}

.section_2 {
  width: 33px;
  height: 104px;
  margin: 10px 0 0 39px;
}

.box_2 {
  background-color: rgba(217, 217, 217, 1);
  border-radius: 50%;
  width: 33px;
  height: 33px;
  transition: background-color 0.3s;
}

.box_2.active {
  background-color: rgba(109, 236, 97, 1);
}

.box_3 {
  background-color: rgba(217, 217, 217, 1);
  border-radius: 50%;
  width: 33px;
  height: 33px;
  margin-top: 38px;
  transition: background-color 0.3s;
}

.box_3.active {
  background-color: rgba(255, 82, 39, 1);
}

.text-group_1 {
  width: 80px;
  height: 136px;
  margin-left: 31px;
}

.text_7 {
  width: 80px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
}

.text_8 {
  width: 80px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin-top: 6px;
}

/* 实时数据表格样式 */
.table-container {
  margin-top: 40px;
  width: 100%;
}

.table-title {
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  color: rgba(0, 0, 0, 1);
  margin-bottom: 20px;
  text-align: left;
}

.table-loading,
.table-error {
  text-align: center;
  padding: 30px;
  color: rgba(0, 0, 0, 0.6);
  font-size: 32px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
}

.table-error {
  color: rgba(255, 82, 39, 1);
}

/* Flexbox utility classes */
.flex-col {
  display: flex;
  flex-direction: column;
}

.flex-row {
  display: flex;
  flex-direction: row;
}

.justify-between {
  justify-content: space-between;
}

.justify-end {
  justify-content: flex-end;
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: 20px;
  right: 30px;
  background: none;
  border: none;
  font-size: 60px;
  color: rgba(0, 0, 0, 0.5);
  cursor: pointer;
  line-height: 1;
  z-index: 10;
  transition: color 0.3s;
  padding: 0;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: rgba(0, 0, 0, 1);
}

/* Element Plus 表格样式覆盖 */
:deep(.el-table) {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: rgba(247, 226, 88, 0.5);
  color: rgba(0, 0, 0, 1);
  font-weight: 600;
  font-size: 16px;
}

:deep(.el-table td) {
  color: rgba(0, 0, 0, 0.8);
  font-size: 14px;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: rgba(247, 226, 88, 0.1);
}
</style>
