<template>
  <div class="main-dashboard">
    <!-- 顶部导航栏 -->
    <header class="dashboard-header">
      <div class="dashboard-title">青山水电站防汛安全在线监控系统</div>
      <div class="dashboard-info">
        <span>{{ currentTime }}</span>
        <span class="dashboard-user">管理员</span>
      </div>
    </header>

    <div class="dashboard-body">
      <!-- 左侧菜单 -->
      <aside class="dashboard-sidebar">
        <el-menu default-active="1" class="el-menu-vertical">
          <el-sub-menu index="1">
            <template #title>三维场景模型</template>
            <el-menu-item index="1-1">开闸状态</el-menu-item>
            <el-menu-item index="1-2">开闸模型</el-menu-item>
            <el-menu-item index="1-3">开闸参数</el-menu-item>
            <el-menu-item index="1-4">压力监测</el-menu-item>
            <el-menu-item index="1-5">流量监测</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="2">
            <template #title>功能角度</template>
            <el-menu-item index="2-1">常视角</el-menu-item>
            <el-menu-item index="2-2">功能角</el-menu-item>
            <el-menu-item index="2-3">场景角</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </aside>

      <!-- 中间Cesium场景 -->
      <main class="dashboard-main">
        <CesiumScene />
      </main>

      <!-- 右侧数据面板 -->
      <aside class="dashboard-panel">
        <el-card class="panel-card" shadow="hover">
          <div class="panel-title">实时数据</div>
          <el-table :data="tableData" style="width: 100%">
            <el-table-column prop="name" label="测点" width="80" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="value" label="测值(mm)" width="80" />
          </el-table>
        </el-card>
        <el-card class="panel-card" shadow="hover">
          <div class="panel-title">实时数据
            <el-button type="primary" size="small" style="float:right" @click="dialogVisible = true">添加测点</el-button>
          </div>
          <el-table :data="tableData" style="width: 100%">
            <el-table-column prop="name" label="测点" width="80" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="value" label="测值(mm)" width="80" />
          </el-table>
        </el-card>
        <el-dialog v-model="dialogVisible" title="添加测点" width="360px">
          <el-form :model="newPoint" label-width="60px">
            <el-form-item label="测点">
              <el-input v-model="newPoint.name" placeholder="如EX1" />
            </el-form-item>
            <el-form-item label="日期">
              <el-date-picker v-model="newPoint.date" type="date" placeholder="选择日期" style="width:100%" />
            </el-form-item>
            <el-form-item label="测值">
              <el-input v-model="newPoint.value" type="number" placeholder="如0.21" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="addPoint">确定</el-button>
          </template>
        </el-dialog>
        <el-card class="panel-card" shadow="hover">
          <div class="panel-title">数据分析</div>
          <div style="height:180px;"><LineChart /></div>
          <div style="height:180px;"><BarChart /></div>
        </el-card>
      </aside>
    </div>

    <!-- 底部时间轴和状态栏 -->
    <footer class="dashboard-footer">
      <div class="footer-timeline">2024/1/1 ~ 2024/1/29</div>
      <div class="footer-status">系统状态：正常</div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CesiumScene from './components/CesiumScene.vue'
import LineChart from './components/LineChart.vue'
import BarChart from './components/BarChart.vue'

const currentTime = ref('2026/1/11 17:04:37')
const tableData = ref([
  { name: 'EX1', date: '2025-01-15', value: 0.21 },
  { name: 'EX2', date: '2025-01-15', value: 0.18 }
])
const dialogVisible = ref(false)
const newPoint = ref({ name: '', date: '', value: '' })

function addPoint() {
  if (!newPoint.value.name || !newPoint.value.date || !newPoint.value.value) return
  tableData.value.push({
    name: newPoint.value.name,
    date: typeof newPoint.value.date === 'string' ? newPoint.value.date : newPoint.value.date.toISOString().slice(0, 10),
    value: Number(newPoint.value.value)
  })
  dialogVisible.value = false
  newPoint.value = { name: '', date: '', value: '' }
}

onMounted(() => {
  // 可加定时更新时间
})
</script>

<style scoped>
.main-dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0a2a4a;
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 56px;
  background: linear-gradient(90deg, #0a2a4a 80%, #1e4c7a 100%);
  color: #fff;
  padding: 0 32px;
  font-size: 22px;
}
.dashboard-title {
  font-weight: bold;
  letter-spacing: 2px;
}
.dashboard-info {
  font-size: 16px;
}
.dashboard-user {
  margin-left: 24px;
  background: #1e4c7a;
  border-radius: 12px;
  padding: 4px 12px;
}
.dashboard-body {
  display: flex;
  flex: 1;
  min-height: 0;
}
.dashboard-sidebar {
  width: 220px;
  background: #183c5a;
  color: #fff;
  padding-top: 12px;
  box-shadow: 2px 0 8px #0002;
}
.dashboard-main {
  flex: 1;
  position: relative;
  background: #000;
  min-width: 0;
}
.dashboard-panel {
  width: 340px;
  background: #183c5a;
  color: #fff;
  padding: 12px 8px;
  box-shadow: -2px 0 8px #0002;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.panel-card {
  background: #204c7a;
  color: #fff;
  margin-bottom: 8px;
}
.panel-title {
  font-weight: bold;
  margin-bottom: 8px;
}
.dashboard-footer {
  height: 32px;
  background: #0a2a4a;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  padding: 0 32px;
}
</style>
