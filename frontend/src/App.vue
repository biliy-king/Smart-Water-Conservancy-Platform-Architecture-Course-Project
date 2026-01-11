<template>
  <div class="tech-screen-root screen-bg">
    <!-- 顶部导航栏 -->
    <header class="tech-header screen-header">
      <div class="tech-title screen-title">数字孪生可视化系统</div>
      <div class="tech-switch screen-switch">
        <el-button :type="activeTab==='scene'?'primary':'default'" class="screen-btn" @click="activeTab='scene'">全球总览</el-button>
        <el-button :type="activeTab==='database'?'primary':'default'" class="screen-btn" @click="activeTab='database'">城市数据</el-button>
      </div>
      <div class="tech-info screen-info">
        <span>{{ currentTime }}</span>
        <span class="tech-user screen-user">管理员</span>
      </div>
    </header>

    <div v-if="activeTab==='scene'" class="tech-body screen-body screen-monitor-layout">
      <!-- 左侧菜单区（缩窄，仅一栏） -->
      <aside class="screen-side screen-side-left screen-menu-narrow">
        <el-card class="screen-card" shadow="hover">
          <div class="screen-card-title">三维场景模型</div>
          <el-menu default-active="1" class="screen-menu-list" background-color="#0a2a4a" text-color="#fff" active-text-color="#00eaff">
            <el-menu-item index="1">开关状态</el-menu-item>
            <el-menu-item index="2">开关监测</el-menu-item>
            <el-menu-item index="3">开关分析</el-menu-item>
          </el-menu>
        </el-card>
      </aside>

      <!-- 中间Cesium三维场景铺满 -->
      <main class="screen-main screen-cesium-full">
        <CesiumScene />
      </main>

      <!-- 右侧测点数据表（缩窄，仅一栏） -->
      <aside class="screen-side screen-side-right screen-status-narrow">
        <el-card class="screen-card" shadow="hover">
          <div class="screen-card-title">测点数据</div>
          <el-table :data="tableData" style="width:100%" height="320">
            <el-table-column prop="name" label="测点" width="80" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="value" label="测值(mm)" width="80" />
          </el-table>
        </el-card>
      </aside>

      <!-- 底部区：状态信息和多图表分析区 -->
      <section class="screen-bottom-charts-narrow">
        <el-card class="screen-card" shadow="hover">
          <div class="screen-card-title">状态信息</div>
          <div>最新测点：{{ tableData[0]?.name || '-' }}</div>
          <div>最新测值：{{ tableData[0]?.value || '-' }} mm</div>
          <div>状态：<span style="color:#00eaff">正常</span></div>
        </el-card>
        <el-card class="screen-card" shadow="hover">
          <div class="screen-card-title">趋势分析</div>
          <div style="height:120px;"><LineChart /></div>
        </el-card>
        <el-card class="screen-card" shadow="hover">
          <div class="screen-card-title">测值变化</div>
          <div style="height:120px;"><BarChart /></div>
        </el-card>
      </section>
    </div>

    <div v-else class="tech-body screen-body">
      <DatabaseView />
    </div>

    <!-- 底部发光状态栏 -->
    <footer class="tech-footer screen-footer">
      <div class="tech-footer-timeline">2024/1/1 ~ 2024/1/29</div>
      <div class="tech-footer-status">系统状态：正常</div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CesiumScene from './components/CesiumScene.vue'
import LineChart from './components/LineChart.vue'
import BarChart from './components/BarChart.vue'
import DatabaseView from './components/DatabaseView.vue'

const currentTime = ref('2026/1/11 17:04:37')
const activeTab = ref('scene')
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
/* 缩窄边栏，Cesium铺满，底部多栏 */
.screen-menu-narrow {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 160px;
  width: 120px;
  z-index: 2;
  height: auto;
}
.screen-status-narrow {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 160px;
  width: 180px;
  z-index: 2;
  height: auto;
}
.screen-cesium-full {
  position: absolute;
  left: 120px;
  right: 180px;
  top: 0;
  bottom: 160px;
  z-index: 1;
  height: auto;
  background: #000c;
  border-radius: 12px;
  box-shadow: 0 2px 16px #1e4c7a44 inset;
  overflow: hidden;
}
.screen-bottom-charts-narrow {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 160px;
  display: flex;
  gap: 24px;
  padding: 0 120px 0 180px;
  z-index: 3;
}
/* 监控大屏参考图功能分区布局 */
.screen-monitor-layout {
  flex-direction: column;
  height: calc(100vh - 70px - 40px);
  min-height: 0;
  padding: 0;
  gap: 0;
  position: relative;
}
.screen-menu {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 160px;
  width: 220px;
  z-index: 2;
  height: auto;
}
.screen-menu-list {
  border-radius: 8px;
  box-shadow: 0 0 12px #00eaff44;
  margin-top: 12px;
}
.screen-cesium {
  position: absolute;
  left: 220px;
  right: 340px;
  top: 0;
  bottom: 160px;
  z-index: 1;
  height: auto;
  background: #000c;
  border-radius: 12px;
  box-shadow: 0 2px 16px #1e4c7a44 inset;
  overflow: hidden;
}
.screen-status {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 160px;
  width: 340px;
  z-index: 2;
  height: auto;
}
.screen-bottom-charts {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 160px;
  display: flex;
  gap: 24px;
  padding: 0 240px;
  z-index: 3;
}
/* 数字孪生大屏科技感主样式 */
.screen-bg {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: radial-gradient(ellipse at 50% 50%, #0a2a4a 60%, #1e4c7a 100%) fixed;
  box-shadow: 0 0 80px 10px #1e4c7a88 inset;
  position: relative;
}
.screen-header {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 48px;
  background: linear-gradient(90deg, #0a2a4a 80%, #1e4c7a 100%);
  border-bottom: 2px solid #00eaff;
  box-shadow: 0 4px 24px #00eaff44, 0 0 32px #1e4c7a88 inset;
}
.screen-title {
  font-size: 32px;
  font-weight: bold;
  color: #fff;
  letter-spacing: 4px;
  text-shadow: 0 0 16px #00eaff, 0 2px 8px #1e4c7a88;
}
.screen-switch {
  display: flex;
  gap: 24px;
}
.screen-btn {
  font-size: 18px;
  font-weight: bold;
  border-radius: 24px;
  background: linear-gradient(90deg, #00eaff 40%, #1e4c7a 100%);
  color: #fff;
  box-shadow: 0 0 12px #00eaff88, 0 2px 8px #1e4c7a88;
  border: none;
  padding: 8px 32px;
}
.screen-btn:hover {
  background: linear-gradient(90deg, #1e4c7a 40%, #00eaff 100%);
  color: #fff;
}
.screen-info {
  font-size: 18px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 24px;
}
.screen-user {
  background: #00eaff44;
  border-radius: 16px;
  padding: 4px 16px;
  box-shadow: 0 0 8px #00eaff88;
}
.screen-body {
  display: flex;
  flex-direction: row;
  height: calc(100vh - 70px - 40px);
  min-height: 0;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 0 24px;
  box-sizing: border-box;
  overflow: hidden;
}
.screen-side {
  width: 340px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background: none;
  z-index: 2;
}
.screen-card {
  background: linear-gradient(120deg, #0a2a4a 80%, #00eaff44 100%);
  color: #fff;
  border-radius: 18px;
  box-shadow: 0 0 24px #00eaff88, 0 2px 12px #1e4c7a88;
  border: 2px solid #00eaff;
  padding: 18px 24px;
  font-size: 18px;
  position: relative;
}
.screen-card-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 12px;
  text-shadow: 0 0 8px #00eaff, 0 2px 8px #1e4c7a88;
}
.screen-card-content {
  margin-bottom: 8px;
  font-size: 18px;
}
.screen-num {
  color: #00eaff;
  font-weight: bold;
  font-size: 22px;
  text-shadow: 0 0 8px #00eaff;
}
.screen-indicators {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.screen-indicator {
  background: #1e4c7a88;
  border-radius: 8px;
  padding: 8px 0;
  text-align: center;
  color: #fff;
  font-size: 16px;
  box-shadow: 0 0 8px #00eaff44;
}
.screen-main {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}
/* 移除圆形地球背景，直接展示Cesium底图 */
.screen-model {
  font-size: 18px;
  margin-bottom: 8px;
  color: #fff;
}
.screen-rank {
  font-size: 16px;
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.screen-footer {
  height: 40px;
  background: linear-gradient(90deg, #0a2a4a 80%, #00eaff 100%);
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  padding: 0 48px;
  border-top: 2px solid #00eaff;
  box-shadow: 0 -4px 24px #00eaff44, 0 0 32px #1e4c7a88 inset;
}
</style>
