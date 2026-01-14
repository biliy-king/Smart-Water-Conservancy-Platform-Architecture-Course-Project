<template>
  <div class="sensor-panel">
    <div class="panel-title">测点切换</div>
    <div v-if="loading" class="loading-text">加载中...</div>
    <div v-else-if="sensors.length === 0" class="empty-text">暂无监测点数据</div>
    <div v-else class="sensor-list">
      <div 
        v-for="sensor in sensors" 
        :key="sensor.id" 
        class="sensor-item"
        :class="{ active: selectedSensor === sensor.id }"
        @click="selectSensor(sensor)"
      >
        <div class="sensor-rectangle" :class="sensor.status"></div>
        <div class="sensor-text">{{ sensor.name }}</div>
        <div class="sensor-status" :class="sensor.status">{{ sensor.statusText }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPoints } from '@/api/waterStructures'

const emit = defineEmits(['select-sensor'])

const sensors = ref([])
const loading = ref(false)
const selectedSensor = ref(null)

// 定义10个测点（EX1-10）
const SENSOR_LIST = [
  'EX1', 'EX2', 'EX3', 'EX4', 'EX5', 'EX6', 'EX7', 'EX8', 'EX9', 'EX10'
]

// 加载监测点列表（从后端获取 pointId）
async function loadSensors() {
  loading.value = true
  
  try {
    // 从后端获取所有测点
    const response = await getPoints({ page_size: 1000 })
    const allPoints = response.data?.results || response.data || []
    

    
    // 建立映射：EX1对应EX1-2-位移mm，EX2对应EX1-3-位移mm，以此类推
    const pointMap = {}
    allPoints.forEach(point => {
      // 使用多种可能的字段名来获取测点名称
      const sensorName = point.point_code || 
                       point.name || 
                       point.device_info?.device_name ||
                       point.device_name

      if (sensorName) {
        const code = sensorName.toUpperCase().trim()
        // 直接使用测点名称作为key
        pointMap[code] = point

        // 建立EX映射：EX1-2-位移mm → EX1, EX1-3-位移mm → EX2, EX1-4-位移mm → EX3, ...
        const match = code.match(/^EX1-(\d+)-位移MM$/i)
        if (match) {
          const deviceNum = parseInt(match[1])
          // EX1-2-位移mm → EX1, EX1-3-位移mm → EX2, EX1-4-位移mm → EX3, ...
          // deviceNum从2开始，对应EX1；deviceNum=3对应EX2，所以公式是：EX(deviceNum-1)
          if (deviceNum >= 2 && deviceNum <= 11) {
            const exName = `EX${deviceNum - 1}`
            pointMap[exName] = point
          }
        }
      }
    })
    

    
    // 创建测点数据，优先使用后端数据
    sensors.value = SENSOR_LIST.map((sensorName) => {
      const upperName = sensorName.toUpperCase()
      const matchedPoint = pointMap[upperName] || pointMap[sensorName]
      
      if (matchedPoint) {
        // 使用后端返回的完整测点信息
        return {
          id: sensorName, // 使用EX1-EX10作为ID（用于UI显示和Cesium飞行定位）
          name: sensorName, // 直接使用EX1-EX10作为名称（用于UI显示和Cesium飞行定位）
          pointId: matchedPoint.id, // 从后端获取的数字ID（用于加载详情）
          status: matchedPoint.current_status || 'normal', // 使用后端的状态
          statusText: getStatusText(matchedPoint.current_status || 'normal'),
          rawData: matchedPoint, // 保存完整的测点数据
          detail: matchedPoint // 保存完整的测点详情
        }
      } else {
        // 如果后端没有匹配的测点，使用默认值
        return {
          id: sensorName,
          name: sensorName,
          pointId: null,
          status: 'normal',
          statusText: '正常',
          rawData: null,
          detail: null
        }
      }
    })
    

  } catch (error) {
    console.error('加载测点失败:', error)
    // 如果失败，至少显示测点名称
    sensors.value = SENSOR_LIST.map(name => ({
      id: name,
      name: name,
      pointId: null,
      status: 'normal',
      statusText: '正常',
      rawData: null,
      detail: null
    }))
  } finally {
    loading.value = false
  }
}

// 获取状态文本
function getStatusText(status) {
  const statusMap = {
    normal: '正常',
    warning: '预警',
    alarm: '告警',
    abnormal: '异常'
  }
  return statusMap[status] || '正常'
}

function selectSensor(sensor) {
  if (selectedSensor.value === sensor.id) {
    selectedSensor.value = null
  } else {
    selectedSensor.value = sensor.id
  }
  emit('select-sensor', sensor)
  console.log('选择监测点:', sensor)
}

// 组件挂载时加载数据
onMounted(() => {
  loadSensors()
})
</script>

<style scoped>
.sensor-panel {
  padding: 20px;
  background: rgba(255, 249, 189, 0.65);
}

.panel-title {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #000000;
  margin-bottom: 20px;
}

.sensor-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.sensor-item {
  position: relative;
  width: 240px;
  height: 57px;
  margin-bottom: 0;
  cursor: pointer;
  transition: all 0.3s;
}

.sensor-item:not(:last-child) {
  border-bottom: 3px solid #9E9D8C;
}

.sensor-rectangle {
  position: absolute;
  width: 240px;
  height: 57px;
  background: #FFFCD5;
  border: 3px solid #9E9D8C;
  transition: background 0.3s;
}

.sensor-item.active .sensor-rectangle {
  background: #D9D9D9;
}

.sensor-text {
  position: absolute;
  left: 52px;
  top: 50%;
  transform: translateY(-50%);
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 28px;
  color: #000000;
  line-height: 1.21;
  z-index: 2;
}

.sensor-status {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 24px;
  z-index: 2;
}

.sensor-status.normal {
  color: #52c41a;
}

.sensor-status.warning {
  color: #faad14;
}

.sensor-status.abnormal {
  color: #f5222d;
}

.sensor-rectangle.normal {
  border-color: #52c41a;
}

.sensor-rectangle.warning {
  border-color: #faad14;
  background: #fff7e6;
}

.sensor-rectangle.abnormal {
  border-color: #f5222d;
  background: #fff1f0;
}

.loading-text,
.empty-text {
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 24px;
}
</style>
