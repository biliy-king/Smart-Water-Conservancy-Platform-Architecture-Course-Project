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
import { getPoints, getPoint } from '@/api/waterStructures'

const emit = defineEmits(['select-sensor'])

const sensors = ref([])
const loading = ref(false)
const selectedSensor = ref(null)

// 加载监测点列表
async function loadSensors() {
  loading.value = true
  
  try {
    // 获取所有监测点（不限制分页，或者设置较大的page_size）
    const response = await getPoints({ page_size: 100 })
    
    // 转换数据格式并获取每个监测点的状态
    const points = response.data.results || []
    
    // 为每个监测点获取详细信息（包含实时状态）
    const sensorsWithStatus = await Promise.all(
      points.map(async (point) => {
        try {
          // 获取监测点详情（包含current_status等P0增强字段）
          const detailResponse = await getPoint(point.id)
          const detail = detailResponse.data
          
          // 状态映射
          let status = 'normal'
          let statusText = '正常'
          if (detail.current_status === 'warning') {
            status = 'warning'
            statusText = '预警'
          } else if (detail.current_status === 'alarm') {
            status = 'abnormal'
            statusText = '告警'
          }
          
          return {
            id: point.id,
            name: point.point_code || `监测点${point.id}`,
            status: status,
            statusText: statusText,
            rawData: point,
            detail: detail
          }
        } catch (error) {
          console.error(`获取监测点${point.id}详情失败:`, error)
          // 如果获取详情失败，使用默认状态
          return {
            id: point.id,
            name: point.point_code || `监测点${point.id}`,
            status: 'normal',
            statusText: '正常',
            rawData: point
          }
        }
      })
    )
    
    sensors.value = sensorsWithStatus
    console.log('加载监测点成功，共', sensors.value.length, '个')
  } catch (error) {
    console.error('加载监测点失败:', error)
    sensors.value = []
  } finally {
    loading.value = false
  }
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
