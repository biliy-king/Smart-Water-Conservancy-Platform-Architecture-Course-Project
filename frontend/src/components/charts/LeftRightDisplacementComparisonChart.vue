<template>
  <div class="comparison-chart">
    <div class="chart-header"><h3 class="chart-title">{{ title || '倒垂线-左右岸位移' }}</h3></div>
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
  for (let i = 0; i < 7; i++) {
    arr.push({
      date: `${i + 1}日`,
      max: 10 + Math.random() * 2,
      avg: 8 + Math.random() * 2,
      min: 6 + Math.random() * 2
    })
  }
  return arr
}
function updateChart() {
  if (!chartInstance || data.value.length === 0) return
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['最大值', '平均值', '最小值'], top: 10, textStyle: { color: '#333' } },
    xAxis: { type: 'category', data: data.value.map(d => d.date), axisLabel: { color: '#333' } },
    yAxis: { type: 'value', name: `位移 (${props.unit})`, axisLabel: { color: '#333' } },
    series: [
      { name: '最大值', type: 'bar', stack: 'displacement', data: data.value.map(d => d.max), itemStyle: { color: '#ff7875' }, barWidth: '30%' },
      { name: '平均值', type: 'bar', stack: 'displacement', data: data.value.map(d => d.avg), itemStyle: { color: '#52c41a' }, barWidth: '30%' },
      { name: '最小值', type: 'bar', stack: 'displacement', data: data.value.map(d => d.min), itemStyle: { color: '#1890ff' }, barWidth: '30%' }
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
.comparison-chart { width: 100%; min-height: 350px; background: #fff; border-radius: 8px; padding: 16px; color: #333; }
.chart-content { min-height: 300px; }
.chart { width: 100%; height: 100%; min-height: 300px; }
.chart-loading { display: flex; align-items: center; justify-content: center; height: 100%; }
</style>