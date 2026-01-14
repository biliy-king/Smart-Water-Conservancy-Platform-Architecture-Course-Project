<template>
  <div class="water-level-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title || '水位监测' }}</h3>
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
const props = defineProps({
  title: String,
  unit: { type: String, default: 'm' }
})
const chartRef = ref(null)
let chartInstance = null
const loading = ref(false)
const error = ref(null)
const data = ref([])
function getMockData() {
  const arr = []
  for (let i = 0; i < 14; i++) {
    arr.push({
      date: `${i + 1}日`,
      upstream: 50 + Math.sin(i / 2) * 2 + Math.random(),
      downstream: 48 + Math.cos(i / 2) * 2 + Math.random()
    })
  }
  return arr
}
function updateChart() {
  if (!chartInstance || data.value.length === 0) return
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['上游水位', '下游水位'], top: 10, textStyle: { color: '#4a90e2' } },
    xAxis: { type: 'category', data: data.value.map(d => d.date), axisLabel: { color: '#4a90e2' } },
    yAxis: { type: 'value', name: `水位 (${props.unit})`, axisLabel: { color: '#4a90e2' } },
    series: [
      { name: '上游水位', type: 'line', data: data.value.map(d => d.upstream), smooth: true, lineStyle: { color: '#4a90e2' } },
      { name: '下游水位', type: 'line', data: data.value.map(d => d.downstream), smooth: true, lineStyle: { color: '#faad14' } }
    ]
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
.water-level-chart { width: 100%; min-height: 350px; background: #fff; border-radius: 8px; padding: 16px; color: #4a90e2; }
.chart-content { min-height: 300px; }
.chart { width: 100%; height: 100%; min-height: 300px; }
.chart-loading, .chart-error { display: flex; align-items: center; justify-content: center; height: 100%; }
.chart-error { color: #ff6b6b; }
</style>