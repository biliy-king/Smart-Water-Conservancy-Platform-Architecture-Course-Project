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
  console.log('开始生成水位模拟数据')
  try {
    loading.value = true
    error.value = null

    // 生成最近7天的时间序列数据（每小时一个数据点）
    const now = new Date()
    const upstreamList = []
    const downstreamList = []

    // 上游水位基准值：175m
    // 下游水位基准值：145m
    const upstreamBase = 175
    const downstreamBase = 145

    for (let i = 168; i >= 0; i--) { // 7天 * 24小时 = 168小时
      const time = new Date(now)
      time.setHours(time.getHours() - i)

      // 生成模拟的水位数据
      // 上游水位波动：±2m
      const upstreamVariation = (Math.random() - 0.5) * 4
      const upstreamValue = upstreamBase + upstreamVariation

      // 下游水位波动：±1m
      const downstreamVariation = (Math.random() - 0.5) * 2
      const downstreamValue = downstreamBase + downstreamVariation

      upstreamList.push({
        time: time.toISOString(),
        value: parseFloat(upstreamValue.toFixed(2)),
        timestamp: time.getTime()
      })

      downstreamList.push({
        time: time.toISOString(),
        value: parseFloat(downstreamValue.toFixed(2)),
        timestamp: time.getTime()
      })
    }

    // 按时间排序
    upstreamList.sort((a, b) => a.timestamp - b.timestamp)
    downstreamList.sort((a, b) => a.timestamp - b.timestamp)

    // 只保留最近100个数据点
    upstreamData.value = upstreamList.slice(-100)
    downstreamData.value = downstreamList.slice(-100)

    console.log('生成的上游水位数据:', upstreamData.value)
    console.log('生成的下游水位数据:', downstreamData.value)

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
  const timeLabels = sortedTimes.map(time => {
    const date = new Date(time)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`
  })

  // 创建时间到值的映射
  const upstreamMap = new Map(upstreamData.value.map(item => [item.time, item.value]))
  const downstreamMap = new Map(downstreamData.value.map(item => [item.time, item.value]))

  // 为每个时间点获取对应的值
  const upstreamValues = sortedTimes.map(time => upstreamMap.get(time))
  const downstreamValues = sortedTimes.map(time => downstreamMap.get(time))

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
        const time = sortedTimes[dataIndex]
        const date = new Date(time)
        const timeStr = `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:00`
        return `
          <div style="padding: 8px;">
            <div><strong>时间:</strong> ${timeStr}</div>
            <div><strong>上游水位:</strong> ${upstreamValues[dataIndex]?.toFixed(2) || '--'} m</div>
            <div><strong>下游水位:</strong> ${downstreamValues[dataIndex]?.toFixed(2) || '--'} m</div>
          </div>
        `
      }
    },
    legend: {
      data: ['上游水位', '下游水位'],
      top: 10,
      textStyle: {
        color: '#fff'
      }
    },
    grid: {
      left: '8%',
      right: '5%',
      bottom: '15%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: {
        color: '#fff',
        fontSize: 11,
        rotate: 45
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '水位 (m)',
      nameTextStyle: {
        color: '#fff',
        fontSize: 14
      },
      axisLabel: {
        color: '#fff',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
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
        symbolSize: 4,
        lineStyle: {
          color: '#ff6b6b',
          width: 2
        },
        itemStyle: {
          color: '#ff6b6b'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(255, 107, 107, 0.4)' },
              { offset: 1, color: 'rgba(255, 107, 107, 0.1)' }
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
        symbolSize: 4,
        lineStyle: {
          color: '#4ecdc4',
          width: 2
        },
        itemStyle: {
          color: '#4ecdc4'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(78, 205, 196, 0.4)' },
              { offset: 1, color: 'rgba(78, 205, 196, 0.1)' }
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
    loadWaterLevelData()

    // 每30秒刷新一次数据
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
  background: rgba(0, 0, 0, 0.6);
  border-radius: 8px;
  padding: 16px;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.chart-header {
  margin-bottom: 12px;
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #fff;
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
}

.chart-loading,
.chart-error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #fff;
  font-size: 14px;
}

.chart-error {
  color: #ff6b6b;
}
</style>
