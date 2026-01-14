<template>
  <div class="water-level-chart">
    <div class="chart-header">
      <h3 class="chart-title">水位监测</h3>
    </div>
    <div class="chart-content">
      <div v-if="loading" class="chart-loading">加载中...</div>
      <div v-else-if="error" class="chart-error">{{ error }}</div>
      <div v-else ref="chartRef" class="chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getMonitorDataList } from '@/api/monitoring'

const chartRef = ref(null)
let chartInstance = null
const loading = ref(false)
const error = ref(null)

// 存储累积的时间序列数据（最多保留100个数据点）
const upstreamData = ref([])
const downstreamData = ref([])
let refreshInterval = null

// 加载水位数据
async function loadWaterLevelData() {
  try {
    loading.value = true
    error.value = null
    
    // 获取最近7天的数据
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
    
    const response = await getMonitorDataList({
      page_size: 1000,
      start_time: sevenDaysAgo.toISOString(),
      end_time: new Date().toISOString()
    })
    
    const data = response.data.results || response.data || []
    
    // 筛选上游和下游水位数据
    const upstreamList = []
    const downstreamList = []
    
    data.forEach(item => {
      const monitorTime = item.monitor_time || item.created_at
      if (!monitorTime) return
      
      // 上游水位
      if (item.water_level_upstream !== null && item.water_level_upstream !== undefined && item.water_level_upstream !== -999.1 && item.water_level_upstream !== -999.2) {
        upstreamList.push({
          time: monitorTime,
          value: item.water_level_upstream,
          timestamp: new Date(monitorTime).getTime()
        })
      }
      
      // 下游水位
      if (item.water_level_downstream !== null && item.water_level_downstream !== undefined && item.water_level_downstream !== -999.1 && item.water_level_downstream !== -999.2) {
        downstreamList.push({
          time: monitorTime,
          value: item.water_level_downstream,
          timestamp: new Date(monitorTime).getTime()
        })
      }
    })
    
    // 按时间排序
    upstreamList.sort((a, b) => a.timestamp - b.timestamp)
    downstreamList.sort((a, b) => a.timestamp - b.timestamp)
    
    // 只保留最近100个数据点
    upstreamData.value = upstreamList.slice(-100)
    downstreamData.value = downstreamList.slice(-100)
    
    // 更新图表
    updateChart()
  } catch (err) {
    console.error('加载水位数据失败:', err)
    error.value = '加载数据失败: ' + (err.message || '未知错误')
  } finally {
    loading.value = false
  }
}

function updateChart() {
  if (!chartInstance) return
  
  // 合并所有时间点
  const allTimes = new Set()
  upstreamData.value.forEach(item => allTimes.add(item.time))
  downstreamData.value.forEach(item => allTimes.add(item.time))
  const sortedTimes = Array.from(allTimes).sort((a, b) => new Date(a) - new Date(b))
  
  // 格式化时间显示
  const formattedTimes = sortedTimes.map(time => {
    const date = new Date(time)
    return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  })
  
  // 构建上游水位数据序列
  const upstreamValues = sortedTimes.map(time => {
    const item = upstreamData.value.find(d => d.time === time)
    return item ? item.value : null
  })
  
  // 构建下游水位数据序列
  const downstreamValues = sortedTimes.map(time => {
    const item = downstreamData.value.find(d => d.time === time)
    return item ? item.value : null
  })
  
  // 计算Y轴范围
  const allValues = [...upstreamValues, ...downstreamValues].filter(v => v !== null)
  if (allValues.length === 0) {
    return
  }
  
  const minValue = Math.min(...allValues)
  const maxValue = Math.max(...allValues)
  const range = maxValue - minValue
  const padding = range * 0.2 || 1
  
  const option = {
    animation: true,
    animationDuration: 500,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        let result = `时间: ${formattedTimes[params[0].dataIndex]}<br/>`
        params.forEach(param => {
          if (param.value !== null) {
            result += `${param.seriesName}: ${param.value.toFixed(3)} m<br/>`
          }
        })
        return result
      }
    },
    legend: {
      data: ['上游水位', '下游水位'],
      top: 10,
      textStyle: {
        color: '#000'
      }
    },
    grid: {
      left: '12%',
      right: '10%',
      bottom: '15%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: formattedTimes,
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
        name: '上游水位',
        type: 'line',
        data: upstreamValues,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#5470c6',
          width: 3
        },
        itemStyle: {
          color: '#5470c6'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(84, 112, 198, 0.4)' },
              { offset: 1, color: 'rgba(84, 112, 198, 0.1)' }
            ]
          }
        }
      },
      {
        name: '下游水位',
        type: 'line',
        data: downstreamValues,
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
        }
      }
    ]
  }
  
  chartInstance.setOption(option, true)
}

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    
    // 初始化时加载一次数据
    loadWaterLevelData()
    
    // 每30秒更新一次数据
    refreshInterval = setInterval(() => {
      loadWaterLevelData()
    }, 30000)
    
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
.water-level-chart {
  width: 100%;
  height: 100%;
  background: rgba(255, 249, 189, 0.65);
  border: 1px solid rgba(158, 157, 140, 1);
  border-radius: 5px;
  padding: 10px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.chart-header {
  margin-bottom: 10px;
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #000;
  margin: 0;
  text-align: center;
}

.chart-content {
  flex: 1;
  width: 100%;
  min-height: 200px;
  position: relative;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

.chart-loading,
.chart-error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-size: 14px;
}

.chart-error {
  color: #f5222d;
}
</style>
