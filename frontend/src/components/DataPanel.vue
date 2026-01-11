<template>
  <div class="data-panel">
    <el-card shadow="never" class="panel-card">
      <div class="panel-title">监测数据</div>
      <el-table :data="tableData" style="width: 100%; margin-bottom: 16px;">
        <el-table-column prop="name" label="测点" width="80" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="value" label="测值(mm)" width="100" />
      </el-table>
      <div class="charts-row">
        <div class="chart-box" ref="lineChartRef"></div>
        <div class="chart-box" ref="barChartRef"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const tableData = ref([
  { name: 'EX1', date: '2025-01-15', value: 0.21 },
  { name: 'EX2', date: '2025-01-15', value: 0.18 },
])
const lineChartRef = ref(null)
const barChartRef = ref(null)

onMounted(() => {
  // 这里可用 echarts.init(lineChartRef.value) 初始化图表
})
</script>

<style scoped>
.data-panel {
  width: 340px;
  height: 100vh;
  background: #223044;
  padding: 8px 0 0 0;
  box-sizing: border-box;
}
.panel-card {
  background: #223044;
  color: #fff;
  border: none;
  height: 100%;
}
.panel-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}
.charts-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.chart-box {
  flex: 1;
  height: 160px;
  background: #181f2a;
  border-radius: 6px;
}
</style>
