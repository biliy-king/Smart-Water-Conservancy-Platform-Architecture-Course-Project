<template>
  <div class="main-container">
    <!-- 登录/注册页面 -->
    <div v-if="showLogin" class="login-container">
      <LoginPage @close="showLogin = false" @switch-to-register="showRegister = true; showLogin = false" />
    </div>
    <div v-else-if="showRegister" class="login-container">
      <RegisterPage @close="showRegister = false" @switch-to-login="showLogin = true; showRegister = false" />
    </div>
    
    <!-- 主监控大屏 -->
    <div v-else class="tech-screen-root screen-bg">
      <!-- 顶部导航栏 -->
      <header class="tech-header screen-header">
        <div class="header-left">
          <div class="tech-title screen-title">数字化大坝监测可视化系统</div>
        </div>
        <div class="header-right">
          <div class="tech-info screen-info">
            <span class="current-time">{{ currentTime }}</span>
            <div class="user-avatar">
              <div class="avatar-circle"></div>
            </div>
            <span class="login-register-btn" @click="showLogin = true">登录/注册</span>
          </div>
        </div>
      </header>

      <div v-if="activeTab==='scene'" class="tech-body screen-body screen-monitor-layout">
        <!-- 左侧垂直菜单 -->
        <aside class="screen-side screen-side-left screen-menu-narrow">
          <div class="menu-item" :class="{ active: activeTab === 'scene' }" @click="activeTab = 'scene'">
            <div class="menu-rectangle"></div>
            <div class="menu-text">数<br/>字<br/>监<br/>控<br/>大<br/>屏</div>
          </div>
          <div class="menu-item" :class="{ active: activeTab === 'database' }" @click="activeTab = 'database'">
            <div class="menu-rectangle"></div>
            <div class="menu-text">数<br/>据<br/>库<br/>界<br/>面</div>
          </div>
        </aside>

        <!-- 中间Cesium三维场景 -->
        <main class="screen-main screen-cesium-full">
          <CesiumScene />
          <!-- 底部控制按钮 -->
          <div class="bottom-controls">
            <div class="control-btn" @click="showEffectPanel = !showEffectPanel">
              <div class="btn-rectangle">效果设置</div>
            </div>
            <div class="control-btn" @click="showViewPanel = !showViewPanel">
              <div class="btn-rectangle">视角切换</div>
            </div>
            <div class="control-btn" @click="showSensorPanel = !showSensorPanel">
              <div class="btn-rectangle">测点切换</div>
            </div>
          </div>
        </main>

        <!-- 右侧控制面板 -->
        <aside class="screen-side screen-side-right screen-control-panel">
          <ViewSwitchPanel v-if="showViewPanel" />
          <EffectPanel v-if="showEffectPanel" />
          <SensorPanel v-if="showSensorPanel" />
        </aside>

        <!-- 底部传感器信息卡片 -->
        <section class="screen-bottom-info">
          <div class="sensor-info-card">
            <div class="sensor-title">乌拉呀哈大坝</div>
            <div class="sensor-overview">概述：</div>
            <div class="visualization-card">
              <div class="vis-card-header">可视化</div>
              <div class="vis-card-image"></div>
            </div>
          </div>
        </section>
      </div>

      <div v-else class="tech-body screen-body">
        <DatabaseView @switch-to-scene="activeTab = 'scene'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import CesiumScene from './components/CesiumScene.vue'
import DatabaseView from './components/DatabaseView.vue'
import ViewSwitchPanel from './components/ViewSwitchPanel.vue'
import EffectPanel from './components/EffectPanel.vue'
import SensorPanel from './components/SensorPanel.vue'
import LoginPage from './components/LoginPage.vue'
import RegisterPage from './components/RegisterPage.vue'

const currentTime = ref('2026/1/15 10:00:00 星期四')
const activeTab = ref('scene')
const showLogin = ref(false)
const showRegister = ref(false)
const showViewPanel = ref(true)
const showEffectPanel = ref(false)
const showSensorPanel = ref(false)

let timeInterval = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

function updateTime() {
  const now = new Date()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  const weekday = weekdays[now.getDay()]
  currentTime.value = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}${weekday}`
}
</script>

<style scoped>
.main-container {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 主监控大屏样式 */
.screen-bg {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #FFFFFF;
  position: relative;
}

/* 顶部标题栏 */
.screen-header {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  background: #FFFAC1;
  position: relative;
}

.header-left {
  display: flex;
  align-items: center;
  padding-left: 475px;
}

.header-logo {
  width: 181px;
  height: 188px;
  margin-right: 20px;
}

.screen-title {
  font-family: 'Inter', sans-serif;
  font-weight: 900;
  font-size: 96px;
  color: #000000;
  letter-spacing: 0;
  line-height: 1.21;
}

.header-right {
  display: flex;
  align-items: center;
  padding-right: 23px;
}

.current-time {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 36px;
  color: #000000;
  margin-right: 20px;
}

.user-avatar {
  width: 72px;
  height: 72px;
  margin-right: 16px;
}

.avatar-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNzIiIGhlaWdodD0iNzIiIHZpZXdCb3g9IjAgMCA3MiA3MiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMzYiIGN5PSIzNiIgcj0iMzYiIGZpbGw9IiNGRkY5QjkiLz4KPC9zdmc+') no-repeat center;
  background-size: cover;
}

.login-register-btn {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: rgba(0, 0, 0, 0.64);
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: background 0.3s;
}

.login-register-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

/* 主体布局 */
.screen-body {
  height: calc(100vh - 200px);
  position: relative;
  background: #FFFFFF;
}

.screen-monitor-layout {
  height: 100%;
  position: relative;
}

/* 左侧垂直菜单 */
.screen-menu-narrow {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 48px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.menu-item {
  position: relative;
  width: 48px;
  height: 271px;
  cursor: pointer;
  transition: all 0.3s;
}

.menu-item.active .menu-rectangle {
  background: #D9D9D9;
}

.menu-item:not(.active) .menu-rectangle {
  background: #FFFAB9;
}

.menu-rectangle {
  width: 48px;
  height: 271px;
  transition: background 0.3s;
}

.menu-text {
  position: absolute;
  left: 8px;
  top: 27px;
  width: 32px;
  height: 234px;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 32px;
  color: #000000;
  line-height: 1.21;
  writing-mode: vertical-lr;
  text-align: center;
}

/* 中间Cesium场景 */
.screen-cesium-full {
  position: absolute;
  left: 48px;
  right: 512px;
  top: 0;
  bottom: 0;
  z-index: 1;
  background: #000;
  overflow: hidden;
}

.bottom-controls {
  position: absolute;
  bottom: 0;
  left: 504px;
  height: 57px;
  display: flex;
  gap: 0;
  z-index: 100;
}

.control-btn {
  width: 240px;
  height: 57px;
  cursor: pointer;
  position: relative;
}

.btn-rectangle {
  width: 240px;
  height: 57px;
  background: #FFFAC1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 32px;
  color: #000000;
  border: 1px solid #000000;
  transition: background 0.3s;
}

.control-btn:hover .btn-rectangle {
  background: #D9D9D9;
}

/* 右侧控制面板 */
.screen-control-panel {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 512px;
  z-index: 5;
  background: rgba(255, 249, 189, 0.65);
  padding: 20px;
  overflow-y: auto;
}

/* 底部传感器信息 */
.screen-bottom-info {
  position: absolute;
  left: 60px;
  bottom: 60px;
  z-index: 6;
}

.sensor-info-card {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 20px;
  min-width: 300px;
}

.sensor-title {
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  font-size: 40px;
  color: #000000;
  margin-bottom: 10px;
}

.sensor-overview {
  font-family: 'Baloo Bhai 2', sans-serif;
  font-weight: 400;
  font-size: 40px;
  color: #000000;
  margin-bottom: 20px;
}

.visualization-card {
  width: 162px;
  height: 215px;
  background: #FFFAC1;
  border: 1px solid #626262;
  border-radius: 10px;
  padding: 10px;
}

.vis-card-header {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 30px;
  color: #0F1419;
  text-align: center;
  margin-bottom: 10px;
}

.vis-card-image {
  width: 100%;
  height: 177px;
  background: #D9D9D9;
  border-radius: 5px;
}

/* 响应式调整 */
@media (max-width: 1920px) {
  .screen-title {
    font-size: 64px;
  }
  .header-left {
    padding-left: 200px;
  }
}
</style>
