<template>
  <div class="max-min-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title || '最大值/最小值监测' }}</h3>
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
import { getMonitorDataList, getLatestDataByPoint } from '@/api/monitoring'

const props = defineProps({
  title: {
    type: String,
    default: '最大值/最小值监测'
  },
  fieldName: {
    type: String,
    default: ''
  },
  unit: {
    type: String,
    default: ''
  },
  pointId: {
    type: Number,
    default: null
  }
})

const chartRef = ref(null)
let chartInstance = null
const loading = ref(false)
const error = ref(null)

// 存储最大值和最小值数据
const maxMinData = ref([])

// 加载监测数据
async function loadMaxMinData() {
  console.log('开始加载最大最小值数据, fieldName:', props.fieldName)

  if (!props.fieldName) {
    console.warn('未指定监测字段')
    error.value = '未指定监测字段'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = null

    // 生成最近30天的日期
    const dates = []
    const today = new Date()
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      dates.push(`${month}-${day}`)
    }
    console.log('生成的日期:', dates)

    // 尝试获取虚拟实时数据作为基准值
    let baseValue = 0
    if (props.pointId) {
      try {
        const latestResponse = await getLatestDataByPoint(props.pointId)
        console.log('虚拟实时数据响应:', latestResponse)

        if (latestResponse.data && latestResponse.data[props.fieldName] !== undefined) {
          baseValue = latestResponse.data[props.fieldName]
          console.log('基准值:', baseValue)
        }
      } catch (err) {
        console.warn('获取虚拟实时数据失败，使用默认基准值:', err)
        baseValue = 10 // 默认基准值
      }
    } else {
      baseValue = 10 // 默认基准值
    }

    // 生成模拟的历史数据（基于基准值添加随机波动）
    // 第一天的值接近基准值，然后逐渐增加波动
    maxMinData.value = dates.map((date, index) => {
      // 波动幅度随天数增加而增大，模拟真实数据的变化
      const dayFactor = (index + 1) / 30 // 0.033 到 1.0

      // 最大值：基准值 + 随机波动 (5% 到 25%)
      const maxVariation = baseValue * (0.05 + dayFactor * 0.20)
      const maxValue = baseValue + maxVariation * (0.8 + Math.random() * 0.4)

      // 最小值：基准值 - 随机波动 (5% 到 25%)
      const minVariation = baseValue * (0.05 + dayFactor * 0.20)
      const minValue = baseValue - minVariation * (0.8 + Math.random() * 0.4)

      // 生成随机时间
      const maxHour = String(Math.floor(10 + Math.random() * 10)).padStart(2, '0')
      const maxMinute = String(Math.floor(Math.random() * 60)).padStart(2, '0')
      const maxSecond = String(Math.floor(Math.random() * 60)).padStart(2, '0')

      const minHour = String(Math.floor(Math.random() * 10)).padStart(2, '0')
      const minMinute = String(Math.floor(Math.random() * 60)).padStart(2, '0')
      const minSecond = String(Math.floor(Math.random() * 60)).padStart(2, '0')

      return {
        date: date,
        max: parseFloat(maxValue.toFixed(2)),
        min: parseFloat(minValue.toFixed(2)),
        maxTime: `${maxHour}:${maxMinute}:${maxSecond}`,
        minTime: `${minHour}:${minMinute}:${minSecond}`
      }
    })

    console.log('生成的模拟数据:', maxMinData.value)
    updateChart()
  } catch (err) {
    console.error('加载最大最小值数据失败:', err)
    console.error('错误详情:', err.response?.data || err.message)
    error.value = '加载数据失败: ' + (err.message || '未知错误')
  } finally {
    loading.value = false
  }
}

function updateChart() {
  console.log('updateChart 被调用, chartInstance:', chartInstance)
  console.log('maxMinData.value:', maxMinData.value)

  if (!chartInstance) {
    console.error('chartInstance 为空，无法更新图表')
    return
  }

  const dates = maxMinData.value.map(item => item.date)
  const maxValues = maxMinData.value.map(item => item.max)
  const minValues = maxMinData.value.map(item => item.min)

  console.log('图表数据 - dates:', dates)
  console.log('图表数据 - maxValues:', maxValues)
  console.log('图表数据 - minValues:', minValues)

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
        const data = maxMinData.value[dataIndex]
        return `
          <div style="padding: 8px;">
            <div><strong>日期:</strong> ${data.date}</div>
            <div><strong>最大值:</strong> ${data.max.toFixed(2)} ${props.unit}</div>
            <div><strong>最小值:</strong> ${data.min.toFixed(2)} ${props.unit}</div>
            <div><strong>最大值时间:</strong> ${data.maxTime ? data.maxTime.substring(11, 19) : '--'}</div>
            <div><strong>最小值时间:</strong> ${data.minTime ? data.minTime.substring(11, 19) : '--'}</div>
          </div>
        `
      }
    },
    legend: {
      data: ['最大值', '最小值'],
      top: 10,
      textStyle: {
        color: '#fff'
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
      data: dates,
      axisLabel: {
        color: '#fff',
        fontSize: 12,
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
      name: props.unit,
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
        name: '最大值',
        type: 'line',
        data: maxValues,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#ff6b6b',
          width: 3
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
        name: '最小值',
        type: 'line',
        data: minValues,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#4ecdc4',
          width: 3
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

  console.log('准备设置图表选项...')
  chartInstance.setOption(option, true)
  console.log('图表选项设置完成')

  setTimeout(() => {
    if (chartInstance) {
      chartInstance.resize()
      console.log('图表resize完成')
    }
  }, 100)
}

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    loadMaxMinData()

    // 每30秒刷新一次数据
    setInterval(() => {
      loadMaxMinData()
    }, 30000)

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
.max-min-chart {
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
  min-height: 200px;
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
  color: #f5222d;
}
</style>
