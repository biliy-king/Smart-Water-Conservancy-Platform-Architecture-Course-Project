<template>
  <div class="chart-container">
    <div class="chart-title">下游水位监测</div>
    <div ref="chartRef" class="chart"></div>
    <div v-if="selectedData" class="chart-detail">
      <div class="detail-item">
        <span class="detail-label">时间:</span>
        <span class="detail-value">{{ selectedData.time }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">下游水位:</span>
        <span class="detail-value">{{ selectedData.value }} m</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getLatestData, getMonitorDataList } from '@/api/monitoring'

const chartRef = ref(null)
let chartInstance = null
const selectedData = ref(null)

// 存储累积的时间序列数据（最多保留100个数据点）
const timeSeriesData = ref([])
let refreshInterval = null

// 获取实时下游水位数据并更新图表
async function loadRealtimeData() {
  try {
    // 先尝试获取实时数据
    try {
      const response = await getLatestData()
      if (response.data.success && response.data.data) {
        const realtimeData = response.data.data
        
        // 筛选下游水位相关的实时数据（可能有多个测点）
        const downstreamDataList = realtimeData.filter(item => item.device_type === 'water_level_downstream')
        
        if (downstreamDataList.length > 0) {
          // 如果有多个测点，取平均值；如果只有一个，直接使用
          const avgValue = downstreamDataList.reduce((sum, item) => sum + item.value, 0) / downstreamDataList.length
          
          const now = new Date()
          const timeStr = `${now.getMonth() + 1}/${now.getDate()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
          
          // 添加新数据点
          timeSeriesData.value.push({
            time: timeStr,
            value: avgValue,
            timestamp: now.getTime()
          })
          
          // 只保留最近100个数据点
          if (timeSeriesData.value.length > 100) {
            timeSeriesData.value.shift()
          }
          
          // 更新图表
          updateChart()
          return
        }
      }
    } catch (realtimeError) {
    }
    
    // 如果实时数据失败，使用历史数据
    await loadHistoryData()
  } catch (error) {
    console.error('加载下游水位数据失败:', error)
  }
}

// 加载历史数据作为备选
async function loadHistoryData() {
  try {
    // 获取最近7天的数据
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
    
    const response = await getMonitorDataList({
      page_size: 1000,
      start_time: sevenDaysAgo.toISOString(),
      end_time: new Date().toISOString()
    })
    
    const data = response.data.results || []
    
    // 筛选下游水位数据
    const waterLevelData = data.filter(item => 
      item.water_level_downstream !== null && item.water_level_downstream !== undefined
    )
    
    if (waterLevelData.length === 0) {
      return
    }
    
    // 按时间排序
    waterLevelData.sort((a, b) => 
      new Date(a.monitor_time) - new Date(b.monitor_time)
    )
    
    // 转换为时间序列格式（只取最近的数据点）
    const recentData = waterLevelData.slice(-100).map(item => {
      const date = new Date(item.monitor_time)
      return {
        time: `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`,
        value: item.water_level_downstream,
        timestamp: date.getTime()
      }
    })
    
    // 更新数据
    timeSeriesData.value = recentData
    
    // 更新图表
    updateChart()
  } catch (error) {
    console.error('加载历史水位数据失败:', error)
  }
}

function updateChart() {
  if (!chartInstance) return
  
  const times = timeSeriesData.value.map(item => item.time)
  const values = timeSeriesData.value.map(item => item.value)
  
  // 计算Y轴范围，让数据更明显
  const minValue = Math.min(...values.filter(v => v !== null))
  const maxValue = Math.max(...values.filter(v => v !== null))
  const range = maxValue - minValue
  const padding = range * 0.2 || 1 // 20%的padding，至少1米
  
  const option = {
    animation: true,
    animationDuration: 500,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        const dataIndex = params[0].dataIndex
        const time = times[dataIndex]
        const value = values[dataIndex]
        return `时间: ${time}<br/>下游水位: ${value !== null ? value.toFixed(3) : '--'} m`
      }
    },
    grid: {
      left: '12%',
      right: '10%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: times,
      axisLabel: {
        color: '#000',
        fontSize: 12,
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '水位(m)',
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
          return value.toFixed(2)
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
        name: '下游水位',
        type: 'line',
        data: values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#91cc75',
          width: 3
        },
        itemStyle: {
          color: '#91cc75'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(145, 204, 117, 0.4)' },
              { offset: 1, color: 'rgba(145, 204, 117, 0.1)' }
            ]
          }
        },
        animationDelay: (idx) => idx * 10
      }
    ]
  }
  
  chartInstance.setOption(option, true)
  
  // 添加点击事件
  chartInstance.off('click')
  chartInstance.on('click', (params) => {
    const dataIndex = params.dataIndex
    selectedData.value = {
      time: times[dataIndex],
      value: values[dataIndex] !== null ? values[dataIndex].toFixed(3) : '--'
    }
  })
}

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    
    // 初始化时加载一次数据
    loadRealtimeData()
    
    // 每5秒更新一次数据
    refreshInterval = setInterval(() => {
      loadRealtimeData()
    }, 5000)
    
    // 响应式调整
    window.addEventListener('resize', () => {
      chartInstance?.resize()
    })
  }
})

onBeforeUnmount(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
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
