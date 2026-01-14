<template>
  <div class="chart-container">
    <div class="chart-title">EX1-10 和 IP1-3 形变监测</div>
    <div ref="chartRef" class="chart"></div>
    <div v-if="selectedData" class="chart-detail">
      <div class="detail-item">
        <span class="detail-label">测点名称:</span>
        <span class="detail-value">{{ selectedData.pointName }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">形变值:</span>
        <span class="detail-value">{{ selectedData.value }} mm</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">监测时间:</span>
        <span class="detail-value">{{ selectedData.time }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getMonitorDataList } from '@/api/monitoring'

const chartRef = ref(null)
let chartInstance = null
const selectedData = ref(null)

// 生成 EX1-10 和 IP1-3 的测点名称模式
function generatePointCodePatterns() {
  const patterns = []
  
  // EX1-10
  for (let i = 1; i <= 10; i++) {
    patterns.push(new RegExp(`^EX${i}(-|$)`))
  }
  
  // IP1-3
  for (let i = 1; i <= 3; i++) {
    patterns.push(new RegExp(`^IP${i}(-|$)`))
  }
  
  return patterns
}

const pointCodePatterns = generatePointCodePatterns()

// 检查测点名称是否匹配 EX1-10 或 IP1-3
function matchesPointCode(pointCode) {
  if (!pointCode) return false
  return pointCodePatterns.some(pattern => pattern.test(pointCode))
}

// 获取设备类型对应的字段名
function getFieldNameByDeviceType(deviceType) {
  const fieldMap = {
    'inverted_plumb_left_right': 'inverted_plumb_left_right',
    'inverted_plumb_up_down': 'inverted_plumb_up_down',
    'tension_wire_up_down': 'tension_wire_up_down'
  }
  return fieldMap[deviceType] || null
}

// 加载近期数据
async function loadRecentData() {
  try {
    // 获取最近30天的数据
    const thirtyDaysAgo = new Date()
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
    
    const response = await getMonitorDataList({
      page_size: 10000,
      start_time: thirtyDaysAgo.toISOString(),
      end_time: new Date().toISOString()
    })
    
    const data = response.data.results || []
    
    // 按测点分组，获取每个测点的最新数据
    const pointDataMap = {}
    
    data.forEach(item => {
      const pointCode = item.point_info?.point_code || item.point_code
      if (!pointCode || !matchesPointCode(pointCode)) {
        return
      }
      
      // 获取设备类型对应的字段
      const deviceType = item.point_info?.device?.device_type
      if (!deviceType) return
      
      const fieldName = getFieldNameByDeviceType(deviceType)
      if (!fieldName) return
      
      const value = item[fieldName]
      if (value === null || value === undefined) return
      
      const monitorTime = new Date(item.monitor_time)
      
      // 如果该测点还没有数据，或者当前数据更新，则更新
      if (!pointDataMap[pointCode] || 
          monitorTime > new Date(pointDataMap[pointCode].time)) {
        pointDataMap[pointCode] = {
          pointName: pointCode,
          value: value,
          time: item.monitor_time
        }
      }
    })
    
    // 转换为数组并排序
    const pointData = Object.values(pointDataMap)
    
    // 按测点名称排序：先 EX1-10，再 IP1-3
    pointData.sort((a, b) => {
      const aCode = a.pointName || ''
      const bCode = b.pointName || ''
      
      // 提取数字部分
      const aMatch = aCode.match(/(EX|IP)(\d+)/)
      const bMatch = bCode.match(/(EX|IP)(\d+)/)
      
      if (!aMatch || !bMatch) return aCode.localeCompare(bCode)
      
      const aPrefix = aMatch[1]
      const bPrefix = bMatch[1]
      const aNum = parseInt(aMatch[2])
      const bNum = parseInt(bMatch[2])
      
      // EX 排在 IP 前面
      if (aPrefix !== bPrefix) {
        return aPrefix === 'EX' ? -1 : 1
      }
      
      // 同类型按数字排序
      return aNum - bNum
    })
    
    updateChart(pointData)
  } catch (error) {
    console.error('加载形变数据失败:', error)
  }
}

function updateChart(pointData) {
  if (!chartInstance) return
  
  const pointNames = pointData.map(item => item.pointName)
  const values = pointData.map(item => item.value)
  
  // 计算Y轴范围，让数据更明显
  const minValue = Math.min(...values.filter(v => v !== null))
  const maxValue = Math.max(...values.filter(v => v !== null))
  const range = maxValue - minValue
  const padding = range * 0.2 || 5 // 20%的padding，至少5mm
  
  const option = {
    animation: true,
    animationDuration: 500,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const dataIndex = params[0].dataIndex
        const pointName = pointNames[dataIndex]
        const value = values[dataIndex]
        const pointInfo = pointData[dataIndex]
        const time = pointInfo ? new Date(pointInfo.time).toLocaleString('zh-CN') : '--'
        return `测点: ${pointName}<br/>形变值: ${value !== null ? value.toFixed(2) : '--'} mm<br/>监测时间: ${time}`
      }
    },
    grid: {
      left: '15%',
      right: '10%',
      bottom: '20%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: pointNames,
      axisLabel: {
        color: '#000',
        fontSize: 12,
        rotate: 45,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '形变值(mm)',
      min: minValue - padding,
      max: maxValue + padding,
      nameTextStyle: {
        color: '#000',
        fontSize: 14
      },
      axisLabel: {
        color: '#000',
        fontSize: 12,
        formatter: function(value) {
          return value.toFixed(1)
        }
      },
      splitLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      }
    },
    series: [
      {
        name: '形变值',
        type: 'bar',
        data: values,
        itemStyle: {
          color: function(params) {
            // 根据值的大小设置不同颜色
            const value = params.value
            if (value === null || value === undefined) return '#ccc'
            
            // 正值用蓝色系，负值用红色系
            if (value >= 0) {
              return '#5470c6'
            } else {
              return '#ee6666'
            }
          }
        },
        label: {
          show: true,
          position: 'top',
          formatter: function(params) {
            return params.value !== null ? params.value.toFixed(1) : '--'
          },
          fontSize: 10,
          color: '#000'
        },
        animationDelay: (idx) => idx * 20
      }
    ]
  }
  
  chartInstance.setOption(option, true)
  
  // 添加点击事件
  chartInstance.off('click')
  chartInstance.on('click', (params) => {
    const dataIndex = params.dataIndex
    const pointInfo = pointData[dataIndex]
    if (pointInfo) {
      selectedData.value = {
        pointName: pointInfo.pointName,
        value: pointInfo.value.toFixed(2),
        time: new Date(pointInfo.time).toLocaleString('zh-CN')
      }
    }
  })
}

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    loadRecentData()
    
    // 响应式调整
    window.addEventListener('resize', () => {
      chartInstance?.resize()
    })
  }
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', () => {})
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(255, 249, 189, 0.65);
  border: 1px solid rgba(158, 157, 140, 1);
  border-radius: 5px;
  padding: 10px;
  box-sizing: border-box;
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #000;
  margin-bottom: 10px;
  text-align: center;
}

.chart {
  flex: 1;
  min-height: 200px;
  width: 100%;
}

.chart-detail {
  margin-top: 10px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  font-size: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.detail-label {
  color: #666;
  font-weight: 500;
}

.detail-value {
  color: #000;
  font-weight: 600;
}
</style>
