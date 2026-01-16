<template>
  <div class="trend-chart">
    <div class="chart-header"><h3 class="chart-title">{{ title || '倒垂线-上下游位移' }}</h3></div>
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
  for (let i = 0; i < 30; i++) {
    arr.push({ date: `${i + 1}日`, value: 10 + Math.sin(i / 5) * 3 + Math.random() * 2 })
  }
  return arr
}
function updateChart() {
  if (!chartInstance || data.value.length === 0) return
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.value.map(d => d.date), axisLabel: { color: '#4a90e2' } },
    yAxis: { type: 'value', name: `位移 (${props.unit})`, axisLabel: { color: '#4a90e2' } },
    series: [{
      name: '位移值', type: 'line', smooth: true, symbol: 'circle', symbolSize: 4,
      lineStyle: { color: '#4a90e2', width: 2 },
      itemStyle: { color: '#4a90e2' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(74,144,226,0.4)' }, { offset: 1, color: 'rgba(74,144,226,0.1)' }] } },
      data: data.value.map(d => d.value)
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
.trend-chart { width: 100%; min-height: 350px; background: #fff; border-radius: 8px; padding: 16px; color: #4a90e2; }
.chart-content { min-height: 300px; }
.chart { width: 100%; height: 100%; min-height: 300px; }
.chart-loading { display: flex; align-items: center; justify-content: center; height: 100%; }
</style>