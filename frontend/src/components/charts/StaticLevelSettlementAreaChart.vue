<template>
  <div class="settlement-chart">
    <div class="chart-header"><h3 class="chart-title">{{ title || '静力水准沉降' }}</h3></div>
    <div class="chart-content"><div v-if="loading" class="chart-loading">加载中...</div><div v-else ref="chartRef" class="chart"></div></div>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
const props = defineProps({ title: String, unit: { type: String, default: 'mm' } })
const chartRef = ref(null)
let chartInstance = null
const loading = ref(false)
const data = ref([])
function getMockData() {
  const arr = []
  let base = 20
  for (let i = 0; i < 30; i++) {
    base += Math.random() * 0.5 - 0.2
    arr.push({ date: `${i + 1}日`, value: parseFloat(base.toFixed(2)) })
  }
  return arr
}
function updateChart() {
  if (!chartInstance || data.value.length === 0) return
  const baseline = data.value[0]?.value || 0
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.value.map(d => d.date), axisLabel: { color: '#faad14' } },
    yAxis: { type: 'value', name: `沉降 (${props.unit})`, axisLabel: { color: '#faad14' } },
    series: [{
      name: '沉降值', type: 'line', smooth: true, symbol: 'none',
      lineStyle: { color: '#faad14', width: 2 },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(250,173,20,0.4)' }, { offset: 1, color: 'rgba(250,173,20,0.1)' }] } },
      data: data.value.map(d => d.value),
      markLine: {
        data: [{ yAxis: baseline, name: '基准值', lineStyle: { color: '#333', type: 'dashed', width: 1 } }],
        label: { color: '#333', fontSize: 10 }
      }
    }]
  }, true)
}
onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  loading.value = false
  data.value = getMockData()
  updateChart()
  window.addEventListener('resize', () => chartInstance?.resize())
})
onBeforeUnmount(() => {
  chartInstance?.dispose()
  window.removeEventListener('resize', () => {})
})
</script>
<style scoped>
.settlement-chart { width: 100%; min-height: 350px; background: #fff; border-radius: 8px; padding: 16px; color: #faad14; }
.chart-content { min-height: 300px; }
.chart { width: 100%; height: 100%; min-height: 300px; }
.chart-loading { display: flex; align-items: center; justify-content: center; height: 100%; }
</style>