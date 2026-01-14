<template>
  <div class="page flex-col">
    <!-- 顶部导航栏 -->
    <div class="box_1 flex-row">
      <span class="text_1">{{ currentTime }}</span>
      <img
        class="image_1"
        src="/images/FigmaDDSSlicePNG440bb7ea1afcaab61d12ba4fe112e4af.png"
        alt="Logo"
      />
      <span class="text_2">数字化大坝监测可视化系统</span>
      <img
        class="image_2"
        src="/images/FigmaDDSSlicePNG8b836aa3a170ae20cb243c3ae0b91c60.png"
        alt="Decoration"
      />
      <img
        class="image_3"
        src="/images/FigmaDDSSlicePNGe5d552036766d5152518ed0eb573dfa2.png"
        alt="Avatar"
      />
      <div class="text-wrapper_1 flex-col" @click="$emit('show-login')">
        <span class="text_3">登录/注册</span>
      </div>
    </div>

    <div class="box_2 flex-col">
      <!-- Cesium三维场景 - 占据整个区域，显示大坝模型 -->
      <main class="screen-main screen-cesium-full">
        <CesiumScene ref="cesiumSceneRef" />
      </main>
      
      <!-- 左侧菜单 - 浮在 Cesium 场景之上 -->
      <div class="section_2 flex-col justify-between">
        <div class="text-wrapper_2 flex-col">
          <span class="paragraph_1">数字监控大屏</span>
        </div>
        <div class="text-wrapper_3 flex-col" @click="$emit('switch-to-database')">
          <span class="paragraph_2">数据库界面</span>
        </div>
      </div>
      
      <!-- 左侧概述框 -->
      <div class="section_3 flex-col">
        <div class="text-wrapper_7 flex-row"><span class="text_7">{{ damInfo.name || '加载中...' }}</span></div>
        <div class="text-wrapper_8 flex-row"><span class="text_8">概述：</span></div>
        <div class="overview-content">
          <div v-if="damInfo.id" class="overview-item">
            <span class="overview-label">工程等级：</span>
            <span class="overview-value">{{ damInfo.level || '-' }}</span>
          </div>
          <div v-if="damInfo.completion_time" class="overview-item">
            <span class="overview-label">建成时间：</span>
            <span class="overview-value">{{ damInfo.completion_time }}</span>
          </div>
          <div v-if="damInfo.create_time" class="overview-item">
            <span class="overview-label">录入时间：</span>
            <span class="overview-value">{{ formatDateTime(damInfo.create_time) }}</span>
          </div>
        </div>
      </div>
      <!-- 底部控制按钮 -->
      <div class="section_4 flex-row">
        <div class="text-wrapper_4 flex-col" @click="showEffectPanel = !showEffectPanel">
          <span class="text_4">效果设置</span>
        </div>
        <div class="text-wrapper_5 flex-col" @click="showViewPanel = !showViewPanel">
          <span class="text_5">视角切换</span>
        </div>
        <div class="box_3 flex-col" @click="showPopupImage = !showPopupImage">
          <img
            class="label_1"
            referrerpolicy="no-referrer"
            src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNG3b086c1c5325ce6f851400e353ee79e6.png"
            alt="Label"
          />
        </div>
        <div class="text-wrapper_6 flex-col" @click="showSensorPanel = !showSensorPanel">
          <span class="text_6">测点切换</span>
        </div>
      </div>
      <!-- 底部控制面板（效果设置、视角切换、测点切换） -->
      <div class="bottom-panels">
        <!-- 效果设置面板 -->
        <div class="bottom-panel effect-panel-container" v-if="showEffectPanel">
          <EffectPanel />
        </div>
        <!-- 视角切换面板 -->
        <div class="bottom-panel view-panel-container" v-if="showViewPanel">
          <ViewSwitchPanel @switch-view="handleViewSwitch" />
        </div>
        <!-- 测点切换面板 -->
        <div class="bottom-panel sensor-panel-container" v-if="showSensorPanel">
          <SensorPanel @select-sensor="handleSensorSelect" />
        </div>
      </div>
      <!-- 弹出的图片 -->
      <transition name="bounce-popup">
        <div class="popup-image-container" v-if="showPopupImage" @click="showPopupImage = false">
          <img
            class="popup-image"
            referrerpolicy="no-referrer"
            src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNG390c4140626680b672c1c1eef8944edf.png"
            alt="Popup"
          />
        </div>
      </transition>
      
      <!-- 右下角兔子组件 -->
      <div class="rabbit-container" :class="{ active: showVisualizationPanel }" @click="toggleVisualizationPanel">
        <div class="text-wrapper_9 flex-col">
          <span class="text_9">可视化</span>
        </div>
        <img
          class="rabbit-image"
          referrerpolicy="no-referrer"
          src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNG802be2cc7db6899de194f09e5d4e2669.png"
          alt="Rabbit"
        />
      </div>
      
      <!-- 可视化栏目（从下方滑出，跟随兔子） -->
      <transition name="slide-up-smooth">
        <div class="visualization-panel" v-if="showVisualizationPanel">
          <div class="visualization-content">
            <div class="image-container" v-for="i in 4" :key="i">
              <div class="image-placeholder">
                <!-- 图片占位区域 -->
              </div>
            </div>
          </div>
        </div>
      </transition>
      
      <!-- 传感器详情弹窗 -->
      <SensorDetailModal 
        v-if="showSensorModal"
        :sensor-name="selectedSensorName"
        :status="selectedSensorStatus"
        @close="showSensorModal = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import CesiumScene from '@/components/CesiumScene.vue'
import ViewSwitchPanel from '@/components/ViewSwitchPanel.vue'
import EffectPanel from '@/components/EffectPanel.vue'
import SensorPanel from '@/components/SensorPanel.vue'
import SensorDetailModal from '@/components/SensorDetailModal.vue'
import { getStructures } from '@/api/waterStructures'
import { isAuthenticated } from '@/utils/auth'

const emit = defineEmits(['show-login', 'switch-to-database'])

const currentTime = ref('2026/1/15 10:00:00 星期四')
const showViewPanel = ref(false)
const showEffectPanel = ref(false)
const showSensorPanel = ref(false)
const showPopupImage = ref(false)
const showVisualizationPanel = ref(false)
const showSensorModal = ref(false)
const selectedSensorName = ref('传感器EX1')
const selectedSensorStatus = ref('normal')
const cesiumSceneRef = ref(null)

// 大坝信息
const damInfo = ref({})

let timeInterval = null

// 加载大坝信息
async function loadDamInfo() {
  try {
    const response = await getStructures({ page_size: 1 })
    if (response.data.results && response.data.results.length > 0) {
      damInfo.value = response.data.results[0]
      console.log('加载大坝信息成功:', damInfo.value)
      
      // TODO: 可以根据大坝的cesium坐标调整Cesium场景的视角
      // if (damInfo.value.cesium_center_x && damInfo.value.cesium_center_y && cesiumSceneRef.value) {
      //   // 调整相机位置
      // }
    } else {
      console.warn('没有找到大坝信息')
    }
  } catch (error) {
    console.error('加载大坝信息失败:', error)
  }
}

// 格式化日期时间
function formatDateTime(dateTimeStr) {
  if (!dateTimeStr) return '-'
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  // 检查登录状态，如果未登录则触发登录事件
  if (!isAuthenticated()) {
    console.warn('未登录，无法访问大屏')
    emit('show-login')
    return
  }
  
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  loadDamInfo()
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

function handleViewSwitch(viewName) {
  // 通过 ref 调用 CesiumScene 的视角切换方法
  if (cesiumSceneRef.value && cesiumSceneRef.value.switchView) {
    cesiumSceneRef.value.switchView(viewName)
  }
}

function handleSensorSelect(sensor) {
  console.log('选择传感器:', sensor)
  // 当点击传感器1时显示弹窗
  if (sensor.id === 1) {
    selectedSensorName.value = sensor.name
    selectedSensorStatus.value = sensor.status
    showSensorModal.value = true
  }
}

function toggleVisualizationPanel() {
  showVisualizationPanel.value = !showVisualizationPanel.value
}
</script>

<style scoped src="./SceneView.css"></style>
